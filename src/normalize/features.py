"""normalize (spec 4.4): Obj -> các bảng IMDF (kèm cột tag OSM `osm_*`) theo tag_mapping.yaml."""
from __future__ import annotations

import json
import re
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping
from shapely.ops import unary_union

from ..config import ConfigError, Project, compile_re
from ..extract.georef import Georef
from ..model import Model, Obj, Storey
from .ids import labels, level_case, nfc, short_from_name, stable_v4

OSM_COLS = ["osm_indoor", "osm_level", "osm_level_ref", "osm_name", "osm_ref", "osm_door", "osm_entrance",
            "osm_highway", "osm_stairs"]


def jdump(v: Any) -> str | None:
    return None if v is None else json.dumps(v, ensure_ascii=False, separators=(",", ":"))


# --------------------------------------------------------------------------- tầng
def assign_storey_indices(model: Model, tcfg: dict[str, Any]) -> list[Storey]:
    """spec 4.2.5: sắp theo cao độ; tầng có |cao độ| nhỏ nhất = 0 (ghi đè bằng `ground_storey`)."""
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


# --------------------------------------------------------------------------- luật
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


# --------------------------------------------------------------------------- chính
def to_features(model: Model, project: Project, georef: Georef) -> dict[str, pd.DataFrame]:
    tcfg = project.tags
    ns = project.namespace
    lang = project.language
    case_mode = tcfg["defaults"].get("labels", {}).get("level_case", "upper")
    storeys = assign_storey_indices(model, tcfg)
    storey_by_key = {s.key: s for s in storeys}
    space_cfg = tcfg["object_types"]["space"]
    door_cfg = tcfg["object_types"]["door"]
    ref_re = compile_re(space_cfg["osm_common"].get("ref_pattern", r"^[A-Za-z]{1,3}\d{1,4}$"))

    building_id = stable_v4(ns, f"building|{project.name}")
    address_id = stable_v4(ns, f"address|{project.name}")
    level_id = {s.key: stable_v4(ns, f"level|{s.source_ref}") for s in storeys}

    rows: dict[str, list[dict[str, Any]]] = {k: [] for k in ("unit", "opening", "level", "footprint")}
    geoms: dict[str, list[Any]] = {k: [] for k in rows}

    # --- unit
    unit_by_storey: dict[str, list[Any]] = {}
    for o in model.objs:
        if o.type != "space" or o.storey_key not in storey_by_key:
            continue
        st = storey_by_key[o.storey_key]
        rule = first_rule(space_cfg["rules"], o)
        if rule is None:
            model.warn(f"không có rule cho space '{o.props.get('label')}'")
            continue
        text_name = o.props.get("name")
        long_name = o.props.get("long_name")
        code = o.props.get("ref")
        if code is None and o.source_kind == "ifc" and o.props.get("name") and ref_re.fullmatch(nfc(o.props["name"])):
            code = nfc(o.props["name"])                  # IFC: IfcSpace.Name dạng mã phòng -> ref
        display_name = nfc(long_name or (None if code and text_name == code else text_name))
        osm = dict(rule.get("osm", {}))
        osm.update({"level": st.index, "level:ref": st.name, "name": display_name, "ref": code})
        for k in rule.get("osm_omit", []):
            osm[k] = None
        imdf = rule["imdf"]
        row = {
            "id": stable_v4(ns, o.source_ref), "feature_type": "unit", "source_kind": o.source_kind,
            "source_ref": o.source_ref, "source_class": o.source_class,
            "category": imdf["category"], "level_id": level_id[o.storey_key],
            "name": jdump(labels(display_name, lang)), "restriction": None, "accessibility": None,
            "display_point": None, **_split_osm(osm, {}),
        }
        rows["unit"].append(row)
        geoms["unit"].append(o.geometry)
        unit_by_storey.setdefault(o.storey_key, []).append(o.geometry)

    # --- opening
    for o in model.objs:
        if o.type != "door" or o.storey_key not in storey_by_key:
            continue
        st = storey_by_key[o.storey_key]
        rule = first_rule(door_cfg["rules"], o)
        if rule is None:
            continue
        osm = dict(rule.get("osm", {}))
        osm.update({"level": st.index})
        row = {
            "id": stable_v4(ns, o.source_ref), "feature_type": "opening", "source_kind": o.source_kind,
            "source_ref": o.source_ref, "source_class": o.source_class,
            "category": rule["imdf"]["category"], "level_id": level_id[o.storey_key],
            "door": None, "access_control": None, "accessibility": None, "name": None, **_split_osm(osm, {}),
        }
        rows["opening"].append(row)
        geoms["opening"].append(o.geometry)

    # --- level + footprint
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

    # --- venue / address / building
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
    return out
