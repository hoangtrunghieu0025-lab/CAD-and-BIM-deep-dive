"""cad2bim (spec 4.2): áp layer_mapping.yaml lên DXF -> Obj (space, door, wall) có tầng và nhãn."""
from __future__ import annotations

import math
import re
from typing import Any

from ezdxf.math import OCS, Vec3
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, unary_union

from ..config import compile_re
from ..ingest.dxf import DxfSource
from ..model import Model, Obj, Storey


def norm_layer(name: str, cfg: dict[str, Any]) -> str:
    n = cfg.get("normalize", {})
    out = name.upper() if n.get("uppercase", True) else name
    if n.get("strip_whitespace", True):
        out = re.sub(r"\s+", "", out)
    if n.get("strip_xref_prefix", True) and "|" in out:
        out = out.split("|")[-1]
    return out


def match_rule(layer: str, etype: str, block: str | None, cfg: dict[str, Any]):
    """('ignore'|'rule'|'unmatched', rule|None). Khớp đầu tiên thắng; rule khớp cả pattern lẫn entity_types."""
    n = norm_layer(layer, cfg)
    for pat in cfg.get("ignore", []):
        if compile_re(pat).search(n):
            return "ignore", None
    for r in cfg.get("rules", []):
        if compile_re(r["pattern"]).search(n) and etype in r.get("entity_types", []):
            bp = r.get("block_pattern")
            if bp and block is not None and not compile_re(bp).search(block):
                continue
            return "rule", r
    return "unmatched", None


def _wcs_xy(e, factor: float) -> list[tuple[float, float]]:
    """Điểm 2D của polyline sang WCS (xử lý OCS khi extrusion != (0,0,1))."""
    ext = Vec3(e.dxf.get("extrusion", (0, 0, 1)))
    if e.dxftype() == "LWPOLYLINE":
        elev = float(e.dxf.get("elevation", 0.0))
        pts = [(p[0], p[1]) for p in e.get_points("xy")]
        if not ext.isclose(Vec3(0, 0, 1)):
            ocs = OCS(ext)
            return [(v.x * factor, v.y * factor) for v in ocs.points_to_wcs(Vec3(x, y, elev) for x, y in pts)]
        return [(x * factor, y * factor) for x, y in pts]
    # POLYLINE 2D/3D
    return [(v.x * factor, v.y * factor) for v in e.points()] if hasattr(e, "points") else []


def _is_closed(e) -> bool:
    return bool(getattr(e, "is_closed", False) or getattr(e, "closed", False))


def _hatch_polygons(e, factor: float) -> list[Polygon]:
    from ezdxf import path as ezpath

    polys: list[Polygon] = []
    try:
        for sub in ezpath.from_hatch(e).sub_paths():
            pts = [(v.x * factor, v.y * factor) for v in sub.flattening(0.01 / max(factor, 1e-9))]
            if len(pts) >= 3:
                polys.append(Polygon(pts))
    except Exception:  # noqa: BLE001
        return []
    return polys


def build(src: DxfSource, storey: Storey, cfg: dict[str, Any], tcfg: dict[str, Any], model: Model) -> None:
    """Phân loại entity theo layer_mapping, dựng phòng/nhãn/cửa và thêm Obj vào model."""
    fname = src.path.name
    spaces: list[tuple[Polygon, str, str]] = []        # (polygon, handle, layer)
    unclosed: dict[str, list[LineString]] = {}
    labels: list[tuple[str, Point, str]] = []
    ref_re = compile_re(tcfg["object_types"]["space"]["osm_common"].get("ref_pattern", r"^[A-Za-z]{1,3}\d{1,4}$"))
    door_cfg = tcfg["object_types"]["door"]["geometry_source"]
    fallback_w = float(door_cfg.get("width_fallback_m", 0.9))

    for e in src.msp:
        et = e.dxftype()
        block = e.dxf.name if et == "INSERT" else None
        kind, rule = match_rule(e.dxf.layer, et, block, cfg)
        if kind == "ignore":
            continue
        if kind == "unmatched":
            model.unmatched[(e.dxf.layer, et)] = model.unmatched.get((e.dxf.layer, et), 0) + 1
            continue
        rid = rule["id"]
        model.count(f"dxf:{rid}")
        handle = e.dxf.handle
        if rid == "space-boundary":
            if et == "HATCH":
                for k, poly in enumerate(_hatch_polygons(e, src.factor)):
                    spaces.append((poly, f"{handle}.{k}", e.dxf.layer))
                continue
            pts = _wcs_xy(e, src.factor)
            if len(pts) >= 3 and _is_closed(e):
                spaces.append((Polygon(pts), handle, e.dxf.layer))
            elif len(pts) >= 2:
                unclosed.setdefault(e.dxf.layer, []).append(LineString(pts))
        elif rid == "space-label":
            text = e.plain_text() if et == "MTEXT" else e.dxf.text
            ins = e.dxf.insert
            labels.append((" ".join(str(text).split()), Point(ins.x * src.factor, ins.y * src.factor), handle))
        elif rid == "door":
            blk = src.doc.blocks.get(e.dxf.name)
            lens = [l.dxf.start.distance(l.dxf.end) for l in blk if l.dxftype() == "LINE"] if blk is not None else []
            sx = abs(e.dxf.get("xscale", 1.0)) or 1.0
            width = (max(lens) * sx * src.factor) if lens else fallback_w
            if not lens:
                model.warn(f"{fname}: block '{e.dxf.name}' không có LINE để suy bề rộng cửa; dùng {fallback_w} m")
            ins = e.dxf.insert
            ang = math.radians(float(e.dxf.get("rotation", 0.0)))
            c = (ins.x * src.factor, ins.y * src.factor)
            d = (math.cos(ang) * width / 2, math.sin(ang) * width / 2)
            line = LineString([(c[0] - d[0], c[1] - d[1]), (c[0] + d[0], c[1] + d[1])])
            attribs = {a.dxf.tag: a.dxf.text for a in e.attribs}
            model.objs.append(Obj("door", "dxf", f"{fname}|{e.dxf.layer}|{handle}", e.dxf.layer, storey.key,
                                  line, {"width_m": width, "center": c, "attribs": attribs, "psets": {}}))
        elif rid == "wall":
            model.count("wall_entities")
            # tường: mode `simplified` (không xuất hình học); chỉ đếm để báo cáo

    # polyline hở -> thử polygonize (spec 4.2.2)
    for layer, lines in unclosed.items():
        polys = list(polygonize(unary_union(lines)))
        if not polys:
            model.warn(f"{fname}: {len(lines)} polyline hở trên layer '{layer}' không khép được; bỏ qua")
        for k, p in enumerate(polys):
            spaces.append((p, f"polygonize.{layer}.{k}", layer))
            model.warn(f"{fname}: dựng phòng từ polyline hở bằng polygonize (layer '{layer}')")

    # gán nhãn vào polygon chứa điểm chèn (chọn polygon nhỏ nhất nếu lồng nhau)
    label_of: dict[int, str] = {}
    for text, pt, _h in labels:
        inside = [i for i, (poly, _, _) in enumerate(spaces) if poly.contains(pt)]
        if not inside:
            model.warn(f"{fname}: nhãn '{text}' nằm ngoài mọi phòng")
            continue
        i = min(inside, key=lambda k: spaces[k][0].area)
        if i in label_of:
            model.warn(f"{fname}: phòng có nhiều nhãn ('{label_of[i]}', '{text}'); giữ nhãn đầu")
            continue
        label_of[i] = text

    for i, (poly, handle, layer) in enumerate(spaces):
        if not poly.is_valid:
            from shapely import make_valid

            poly = make_valid(poly)
            if poly.geom_type != "Polygon":
                parts = [g for g in getattr(poly, "geoms", []) if g.geom_type == "Polygon"]
                if not parts:
                    model.warn(f"{fname}: bỏ phòng hình học không hợp lệ ({handle})")
                    continue
                poly = max(parts, key=lambda g: g.area)
        text = label_of.get(i)
        props: dict[str, Any] = {"label": text, "ref": None, "name": None}
        if text:
            if ref_re.fullmatch(text):
                props["ref"] = text                      # spec 4.2.6: khớp ref_pattern -> ref
            else:
                props["name"] = text                     # ngược lại -> name
        model.objs.append(Obj("space", "dxf", f"{fname}|{layer}|{handle}", layer, storey.key, poly, props))
        model.count("spaces")
