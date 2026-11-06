"""Obj -> các bảng IMDF kèm cột tag OSM (`osm_*`), theo tag_mapping.yaml."""
from __future__ import annotations

import json
import re
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely import set_precision
from shapely.affinity import translate
from shapely.geometry import Polygon, mapping
from shapely.ops import nearest_points, unary_union

from ..config import ConfigError, Project, compile_re
from ..extract.georef import Georef
from ..model import Model, Obj, Storey
from .door import door_json
from .ids import labels, level_case, nfc, short_from_name, stable_v4

OSM_COLS = ["osm_indoor", "osm_level", "osm_level_ref", "osm_name", "osm_ref", "osm_door", "osm_entrance",
            "osm_highway", "osm_stairs"]


def jdump(v: Any) -> str | None:
    return None if v is None else json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def assign_storey_indices(model: Model, tcfg: dict[str, Any]) -> list[Storey]:
    """Sắp tầng theo cao độ; tầng có |cao độ| nhỏ nhất là 0 (ghi đè bằng `ground_storey`)."""
    rule = tcfg["object_types"]["storey"].get("index_rule", {})
    known = sorted([s for s in model.storeys if s.elevation_m is not None], key=lambda s: (s.elevation_m, s.file_order))
    unknown = sorted([s for s in model.storeys if s.elevation_m is None], key=lambda s: s.file_order)
    ordered = known + unknown
    if not ordered:
        return []
    gname = rule.get("ground_storey")
    ground = None
    if gname:
        ground = next((i for i, s in enumerate(ordered) if gname in (s.name, s.long_name)), None)
        if ground is None:
            model.warn(f"ground_storey '{gname}' không khớp tầng nào; dùng quy tắc min_abs_elevation")
    if ground is None:
        ground = min(range(len(known)), key=lambda i: abs(known[i].elevation_m)) if known else 0
    for i, s in enumerate(ordered):
        s.index = i - ground
    if unknown:
        model.warn("có tầng không có cao độ: xếp cuối theo thứ tự file")
    return ordered


def _texts(obj: Obj) -> list[str]:
    out = []
    for k in ("name", "long_name", "label"):
        v = obj.props.get(k)
        if v:
            out.append(nfc(str(v)))
    return out


def match_when(when: dict[str, Any], obj: Obj) -> bool:
    if when.get("any") is True:
        return True
    if "any_of" in when:
        return any(match_when(w, obj) for w in when["any_of"])
    ok = False
    for key, val in when.items():
        if key == "name_regex":
            rx = compile_re(val)
            ok = any(rx.search(t) for t in _texts(obj))
        elif key == "ifc_object_type_regex":
            ot = obj.props.get("object_type")
            ok = bool(ot) and bool(compile_re(val).search(nfc(str(ot))))
        elif key == "pset":
            ok = True
            for path, want in val.items():
                pset, prop = path.split(".", 1)
                ok = ok and (obj.props.get("psets", {}).get(pset, {}).get(prop) == want)
        else:
            raise ConfigError(f"điều kiện rule không hỗ trợ: `{key}`")
        if not ok:
            return False
    return ok


def first_rule(rules: list[dict[str, Any]], obj: Obj) -> dict[str, Any] | None:
    for r in rules:
        if match_when(r["when"], obj):
            return r
    return None


def _split_osm(osm: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """Tag có cột riêng -> `osm_<tag>`; phần còn lại -> `osm_tags` (JSON)."""
    cols: dict[str, Any] = {c: None for c in OSM_COLS}
    rest: dict[str, Any] = {}
    for k, v in {**osm, **extra}.items():
        col = "osm_" + k.replace(":", "_")
        if col in cols:
            cols[col] = None if v is None else str(v)
        elif v is not None:
            rest[k] = v
    cols["osm_tags"] = jdump(rest) if rest else None
    return cols


GRID = 1e-6          # m: lưới làm tròn sau khi trừ vùng đè, để các cạnh chung khớp nhau tuyệt đối
SNAP_MAX = 0.5       # m: khoảng cách tối đa dịch cửa vào ranh giới unit
GAP_TOL = 1e-3       # m²: khe nhỏ hơn mức này bỏ qua
# thứ tự ưu tiên khi hai unit chồng nhau: số nhỏ giữ nguyên, số lớn bị trừ phần đè
PRIORITY = {"column": 0, "elevator": 1, "stair": 1, "wall": 2, "space": 3}


def _polygonal(g):
    """Chỉ giữ phần Polygon của kết quả phép toán hình học."""
    parts = [x for x in getattr(g, "geoms", [g]) if x.geom_type == "Polygon" and not x.is_empty]
    if not parts:
        return None
    return parts[0] if len(parts) == 1 else unary_union(parts)


def _unit_drafts(model: Model, project: Project, storey_by_key, level_id) -> list[dict[str, Any]]:
    """Mọi thứ sẽ thành `unit`: phòng, cầu thang, thang máy, cột và (mode structure) mạng tường."""
    tcfg, ns, lang = project.tags, project.namespace, project.language
    space_cfg = tcfg["object_types"]["space"]
    ref_re = compile_re(space_cfg["osm_common"].get("ref_pattern", r"^[A-Za-z]{1,3}\d{1,4}$"))
    drafts: list[dict[str, Any]] = []

    def add(o: Obj | None, st: Storey, ref: str, klass: str, kind: str, geom, category: str, osm: dict, name, prio: int):
        drafts.append({"storey": st.key, "source_ref": ref, "source_class": klass, "source_kind": kind,
                       "geom": geom, "category": category, "osm": osm, "name": name, "prio": prio})

    for o in model.objs:
        if o.storey_key not in storey_by_key or o.geometry is None:
            continue
        st = storey_by_key[o.storey_key]
        if o.type == "space":
            rule = first_rule(space_cfg["rules"], o)
            if rule is None:
                model.warn(f"không có rule cho space '{o.props.get('label')}'")
                continue
            text_name, long_name, code = o.props.get("name"), o.props.get("long_name"), o.props.get("ref")
            if code is None and o.source_kind == "ifc" and o.props.get("name") and ref_re.fullmatch(nfc(o.props["name"])):
                code = nfc(o.props["name"])                  # IFC: IfcSpace.Name dạng mã phòng -> ref
            display_name = nfc(long_name or (None if code and text_name == code else text_name))
            osm = dict(rule.get("osm", {}))
            osm.update({"level": st.index, "level:ref": st.name, "name": display_name, "ref": code})
            for k in rule.get("osm_omit", []):
                osm[k] = None
            add(o, st, o.source_ref, o.source_class, o.source_kind, o.geometry, rule["imdf"]["category"], osm,
                display_name, PRIORITY["space"])
        elif o.type in ("stair", "elevator", "column"):
            cfg = tcfg["object_types"].get(o.type) or {}
            if not cfg.get("imdf"):
                continue
            name = nfc(o.props.get("name"))
            osm = dict(cfg.get("osm") or {})
            if osm:
                osm.update({"level": st.index, "level:ref": st.name, "name": name})
            add(o, st, o.source_ref, o.source_class, o.source_kind, o.geometry, cfg["imdf"]["category"], osm, name,
                PRIORITY[o.type])

    if project.wall_mode == "structure":
        wcfg = tcfg["object_types"]["wall"]
        cat = wcfg["imdf"]["structure"]["category"]
        for key, st in storey_by_key.items():
            walls = [o for o in model.objs if o.type == "wall" and o.storey_key == key and o.geometry is not None]
            if not walls:
                continue
            osm = dict(wcfg.get("osm") or {})
            osm.update({"level": st.index, "level:ref": st.name, "area": "yes"})    # tường dạng vùng: indoor=wall + area=yes
            add(None, st, f"walls|{key}", walls[0].source_class, walls[0].source_kind,
                unary_union([o.geometry for o in walls]), cat, osm, None, PRIORITY["wall"])
    return drafts


def _carve(drafts: list[dict[str, Any]], model: Model) -> list[dict[str, Any]]:
    """Unit không được chồng nhau (IMDF): phần đè của cột/cầu thang/thang máy/tường bị trừ khỏi unit ưu tiên thấp hơn."""
    out = []
    by_storey: dict[str, list[dict[str, Any]]] = {}
    for d in drafts:
        by_storey.setdefault(d["storey"], []).append(d)
    for items in by_storey.values():
        for d in items:
            higher = [x["geom"] for x in items if x["prio"] < d["prio"]]
            if higher:
                cover = unary_union(higher)
                if d["geom"].intersection(cover).area > 1e-9:          # chạm cạnh không tính là chồng
                    g = _polygonal(set_precision(d["geom"].difference(cover), GRID))
                    if g is None or g.area < 1e-6:
                        model.warn(f"unit '{d['source_ref']}' nằm trọn trong vùng của đối tượng ưu tiên cao hơn; bỏ")
                        continue
                    d = {**d, "geom": g}
                    model.count("units_carved")
            out.append(d)
    return out


def _snap_door(line, boundary, model: Model, ref: str):
    """Đưa đoạn cửa lên ranh giới unit gần nhất (tường dày: tâm cửa nằm giữa tường, không nằm trên ranh giới)."""
    if boundary is None or boundary.is_empty or (line.distance(boundary) < 1e-6 and boundary.buffer(1e-6).covers(line)):
        return line
    c = line.centroid
    p = nearest_points(boundary, c)[0]
    if c.distance(p) > SNAP_MAX:
        model.warn(f"cửa '{ref}' cách ranh giới unit gần nhất {c.distance(p):.2f} m (> {SNAP_MAX} m); không dịch")
        return line
    moved = translate(line, p.x - c.x, p.y - c.y)
    model.count("openings_snapped")
    if not boundary.buffer(1e-6).covers(moved):
        model.warn(f"cửa '{ref}' đã dịch lên ranh giới nhưng chưa nằm trọn trên một cạnh")
    return moved


def _outline(model: Model, key: str):
    """Đường bao tầng độc lập với unit: polygon lớn trên layer tường (DXF), hoặc vành ngoài của hợp các thân tường."""
    outs = [o.geometry for o in model.objs if o.type == "outline" and o.storey_key == key]
    if outs:
        return max(outs, key=lambda g: g.area)
    walls = [o.geometry for o in model.objs if o.type == "wall" and o.storey_key == key and o.geometry is not None]
    if not walls:
        return None
    u = unary_union(walls)
    ring = max(getattr(u, "geoms", [u]), key=lambda g: g.area)
    return Polygon(ring.exterior)


def to_features(model: Model, project: Project, georef: Georef) -> dict[str, pd.DataFrame]:
    tcfg = project.tags
    ns = project.namespace
    lang = project.language
    case_mode = tcfg["defaults"].get("labels", {}).get("level_case", "upper")
    storeys = assign_storey_indices(model, tcfg)
    storey_by_key = {s.key: s for s in storeys}
    door_cfg = tcfg["object_types"]["door"]

    building_id = stable_v4(ns, f"building|{project.name}")
    address_id = stable_v4(ns, f"address|{project.name}")
    level_id = {s.key: stable_v4(ns, f"level|{s.source_ref}") for s in storeys}

    rows: dict[str, list[dict[str, Any]]] = {k: [] for k in ("unit", "opening", "level", "footprint", "fixture", "detail")}
    geoms: dict[str, list[Any]] = {k: [] for k in rows}

    drafts = _carve(_unit_drafts(model, project, storey_by_key, level_id), model)
    unit_by_storey: dict[str, list[Any]] = {}
    for d in drafts:
        extra = {"area": "yes"} if d["osm"].get("area") == "yes" else {}
        row = {
            "id": stable_v4(ns, d["source_ref"]), "feature_type": "unit", "source_kind": d["source_kind"],
            "source_ref": d["source_ref"], "source_class": d["source_class"],
            "category": d["category"], "level_id": level_id[d["storey"]],
            "name": jdump(labels(d["name"], lang)), "restriction": None, "accessibility": None,
            "display_point": None, **_split_osm({k: v for k, v in d["osm"].items() if k != "area"}, extra),
        }
        rows["unit"].append(row)
        geoms["unit"].append(d["geom"])
        unit_by_storey.setdefault(d["storey"], []).append(d["geom"])

    # đường bao độc lập -> cảnh báo khe giữa các unit
    for st in storeys:
        outline = _outline(model, st.key)
        if outline is None or st.key not in unit_by_storey:
            continue
        gap = outline.difference(unary_union(unit_by_storey[st.key])).area
        model.gaps[st.key] = round(gap, 4)
        if gap > GAP_TOL:
            model.warn(f"tầng '{st.long_name}': khe {gap:.2f} m² giữa các unit trong đường bao tường "
                       f"(đặt options.wall_mode: structure để lấp bằng unit `structure`)")

    # opening: dịch lên ranh giới unit (không tính unit structure) rồi dựng object `door`
    boundary_by_storey = {}
    for d in drafts:
        if d["category"] != "structure":
            boundary_by_storey.setdefault(d["storey"], []).append(d["geom"].boundary)
    boundary_by_storey = {k: unary_union(v) for k, v in boundary_by_storey.items()}
    for o in model.objs:
        if o.type != "door" or o.storey_key not in storey_by_key:
            continue
        st = storey_by_key[o.storey_key]
        rule = first_rule(door_cfg["rules"], o)
        if rule is None:
            continue
        osm = dict(rule.get("osm", {}))
        osm.update({"level": st.index})
        door = door_json(o.props, lambda m, ref=o.source_ref: model.warn(f"cửa '{ref}': {m}"))
        row = {
            "id": stable_v4(ns, o.source_ref), "feature_type": "opening", "source_kind": o.source_kind,
            "source_ref": o.source_ref, "source_class": o.source_class,
            "category": rule["imdf"]["category"], "level_id": level_id[o.storey_key],
            "door": jdump(door), "access_control": None, "accessibility": None, "name": None, **_split_osm(osm, {}),
        }
        rows["opening"].append(row)
        geoms["opening"].append(_snap_door(o.geometry, boundary_by_storey.get(o.storey_key), model, o.source_ref))

    # fixture và detail
    for o in model.objs:
        if o.type not in ("fixture", "detail") or o.storey_key not in storey_by_key or o.geometry is None:
            continue
        imdf = (tcfg["object_types"].get(o.type) or {}).get("imdf")
        if not imdf:
            continue
        row = {"id": stable_v4(ns, o.source_ref), "feature_type": o.type, "source_kind": o.source_kind,
               "source_ref": o.source_ref, "source_class": o.source_class, "level_id": level_id[o.storey_key]}
        if o.type == "fixture":
            row.update({"category": imdf["category"], "name": jdump(labels(nfc(o.props.get("name")), lang)),
                        "display_point": None})
        rows[o.type].append(row)
        geoms[o.type].append(o.geometry)

    lvl_polys: dict[str, Any] = {}
    for st in storeys:
        polys = unit_by_storey.get(st.key)
        if not polys:
            model.warn(f"tầng '{st.long_name}' không có unit nào; bỏ level")
            continue
        poly = unary_union(polys)
        lvl_polys[st.key] = poly
        ordinal = st.ordinal if st.ordinal is not None else st.index
        osm = {"indoor": "level", "level": st.index, "level:ref": st.name}
        rows["level"].append({
            "id": level_id[st.key], "feature_type": "level", "source_kind": st.source_kind,
            "source_ref": st.source_ref, "source_class": "IfcBuildingStorey" if st.source_kind == "ifc" else "dxf",
            "category": tcfg["object_types"]["storey"]["imdf"]["properties"]["category"],
            "outdoor": 0, "ordinal": int(ordinal),
            "name": jdump(labels(level_case(st.long_name or st.name, case_mode), lang)),
            "short_name": jdump(labels(level_case(st.name, case_mode), lang)),
            "building_ids": jdump([building_id]), "restriction": None, "display_point": None,
            **_split_osm(osm, {}),
        })
        geoms["level"].append(poly)
    if not lvl_polys:
        raise ConfigError("không dựng được level/unit nào; không có gì để xuất")
    ground = min((s for s in storeys if s.key in lvl_polys), key=lambda s: abs(s.index))
    foot = lvl_polys[ground.key]
    rows["footprint"].append({
        "id": stable_v4(ns, f"footprint|{project.name}"), "feature_type": "footprint", "source_kind": "derived",
        "source_ref": f"footprint|{project.name}", "source_class": "union(unit) tầng mặt đất",
        "category": "ground", "building_ids": jdump([building_id]),
    })
    geoms["footprint"].append(foot)

    buffer_m = float(project.venue.get("buffer_m", tcfg.get("imdf_package", {}).get("venue", {}).get("buffer_m", 1.0)))
    venue_geom_local = unary_union([foot] + list(lvl_polys.values())).buffer(buffer_m, join_style=2)
    mins = [s.index for s in storeys if s.key in lvl_polys]
    b_osm = {"building": "yes", "min_level": min(mins), "max_level": max(mins)}
    building_name = project.venue.get("building_name") or model.building.name
    building_row = {
        "id": building_id, "feature_type": "building", "source_kind": "ifc" if model.building.ifc_ref else "derived",
        "source_ref": model.building.ifc_ref or f"building|{project.name}",
        "source_class": "IfcBuilding" if model.building.ifc_ref else "derived",
        "category": "unspecified", "name": jdump(labels(building_name, lang)), "address_id": None,
        "osm_tags": jdump(b_osm),
    }
    address_row = {
        "id": address_id, "feature_type": "address", "source_kind": "project", "source_ref": f"address|{project.name}",
        "source_class": "project.yaml", "address": project.address["address"], "locality": project.address["locality"],
        "country": project.address["country"], "unit": project.address.get("unit"),
        "province": project.address.get("province"), "postal_code": project.address.get("postal_code"),
        "postal_code_ext": None, "postal_code_vanity": None,
    }

    def gdf(table: str) -> gpd.GeoDataFrame:
        g = [georef.to_wgs84(x) for x in geoms[table]]
        if table in ("unit", "level", "fixture"):               # display_point: điểm nằm trong vùng, dùng để đặt nhãn
            for r, geom in zip(rows[table], g):
                r["display_point"] = jdump(mapping(geom.representative_point()))
        return gpd.GeoDataFrame(pd.DataFrame(rows[table]), geometry=g, crs="EPSG:4326" if georef.referenced else None)

    venue_geom = georef.to_wgs84(venue_geom_local)
    dp = venue_geom.representative_point()
    venue_row = {
        "id": stable_v4(ns, f"venue|{project.name}"), "feature_type": "venue", "source_kind": "derived",
        "source_ref": f"venue|{project.name}", "source_class": "buffer(footprint)",
        "category": project.venue["category"], "restriction": None,
        "name": jdump(labels(project.venue["name"], lang)), "alt_name": None, "hours": None, "phone": None,
        "website": None, "display_point": jdump(mapping(dp)), "address_id": address_id,
    }
    out: dict[str, pd.DataFrame] = {
        "venue": gpd.GeoDataFrame(pd.DataFrame([venue_row]), geometry=[venue_geom],
                                  crs="EPSG:4326" if georef.referenced else None),
        "address": pd.DataFrame([address_row]),
        "building": pd.DataFrame([building_row]),
        "footprint": gdf("footprint"),
        "level": gdf("level"),
        "unit": gdf("unit"),
        "opening": gdf("opening"),
    }
    for t in ("fixture", "detail"):
        if rows[t]:
            out[t] = gdf(t)
    return out
