"""Trích tầng, footprint phòng, cầu thang/thang máy/cột/tường/nội thất và đoạn cửa từ IFC."""
from __future__ import annotations

from typing import Any

import numpy as np
from shapely import make_valid
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

import ifcopenshell.geom
import ifcopenshell.util.element as E
import ifcopenshell.util.placement as P
import ifcopenshell.util.representation as R

from ..ingest.ifc import IfcSource
from ..model import Model, Obj, Storey


def _settings():
    s = ifcopenshell.geom.settings()
    s.set(s.USE_WORLD_COORDS, True)
    return s


def _shape_xy(settings, element_or_rep) -> tuple[np.ndarray, np.ndarray] | None:
    try:
        sh = ifcopenshell.geom.create_shape(settings, element_or_rep)
    except Exception:
        return None
    v = np.array(sh.geometry.verts).reshape(-1, 3)
    f = np.array(sh.geometry.faces).reshape(-1, 3)
    return (v, f) if len(v) and len(f) else None


def _union_xy(v: np.ndarray, f: np.ndarray) -> tuple[Polygon | None, int]:
    """Hợp các tam giác chiếu xuống XY. Trả (polygon, số mảnh rời bị bỏ)."""
    tris = [Polygon(v[i][:, :2]) for i in f]
    tris = [t for t in tris if t.area > 1e-9]
    if not tris:
        return None, 0
    u = unary_union(tris).simplify(1e-9)
    dropped = 0
    if u.geom_type == "MultiPolygon":
        dropped = len(u.geoms) - 1
        u = max(u.geoms, key=lambda g: g.area)       # chỉ giữ mảnh lớn nhất; nơi gọi sẽ cảnh báo
    return (u, dropped) if u.geom_type == "Polygon" and not u.is_empty else (None, 0)


def _footprint(settings, el) -> tuple[Polygon | None, int]:
    """Footprint XY của phần tử; nếu chính nó không có hình học thì hợp footprint các phần tử con (vd IfcStairFlight)."""
    xy = _shape_xy(settings, el)
    if xy:
        return _union_xy(*xy)
    polys, dropped = [], 0
    for part in E.get_parts(el):
        xy = _shape_xy(settings, part)
        if xy:
            p, d = _union_xy(*xy)
            if p is not None:
                polys.append(p)
                dropped += d
    if not polys:
        return None, 0
    u = unary_union(polys)
    if u.geom_type == "MultiPolygon":
        dropped += len(u.geoms) - 1
        u = max(u.geoms, key=lambda g: g.area)
    return u, dropped


# class IFC dựng thành vùng (Polygon) và loại đối tượng tương ứng trong tag_mapping.yaml
AREA_CLASSES = (("IfcStair", "stair"), ("IfcColumn", "column"), ("IfcWall", "wall"), ("IfcFurnishingElement", "fixture"))   # IfcFurnishingElement có ở cả IFC2X3 và IFC4


def storey_of(el) -> Any:
    """Tầng chứa phần tử: IfcSpace thường qua aggregate, IfcDoor/IfcWall qua containment; thử cả hai."""
    st = E.get_aggregate(el)
    while st is not None and not st.is_a("IfcBuildingStorey"):
        st = E.get_aggregate(st)
    if st is None:
        st = E.get_container(el)
        while st is not None and not st.is_a("IfcBuildingStorey"):
            st = E.get_container(st) or E.get_aggregate(st)
    return st


def extract(src: IfcSource, model: Model, door_cfg: dict[str, Any], file_order: int = 0) -> None:
    f, sc = src.file, src.unit_scale
    fname = src.path.name
    settings = _settings()

    b = f.by_type("IfcBuilding")
    if b:
        model.building.name = model.building.name or b[0].LongName or b[0].Name
        model.building.ifc_ref = b[0].GlobalId
    else:
        model.warn(f"{fname}: không có IfcBuilding")

    storey_by_id: dict[int, Storey] = {}
    for k, s in enumerate(f.by_type("IfcBuildingStorey")):
        elev = s.Elevation * sc if s.Elevation is not None else None
        if elev is None:
            try:
                elev = float(P.get_local_placement(s.ObjectPlacement)[2][3]) * 1.0
                model.warn(f"{fname}: tầng '{s.Name}' thiếu Elevation, dùng Z của placement")
            except Exception:
                elev = None
                model.warn(f"{fname}: tầng '{s.Name}' thiếu Elevation và placement; xếp theo thứ tự file")
        from ..normalize.ids import short_from_name

        name = s.Name or f"Tang {k}"
        st = Storey(
            key=s.GlobalId, name=short_from_name(name), long_name=s.LongName or name,
            elevation_m=elev, source_kind="ifc", source_ref=s.GlobalId, file_order=file_order * 1000 + k,
        )
        storey_by_id[s.id()] = st
        model.storeys.append(st)
    if not storey_by_id:
        model.warn(f"{fname}: không có IfcBuildingStorey")

    n_sp = 0
    for sp in f.by_type("IfcSpace"):
        st_el = storey_of(sp)
        if st_el is None or st_el.id() not in storey_by_id:
            model.warn(f"{fname}: IfcSpace '{sp.Name}' không thuộc tầng nào; bỏ qua")
            continue
        poly, dropped = None, 0
        rep = R.get_representation(sp, "Plan", "FootPrint", "GRAPH_VIEW")
        if rep is not None:
            xy = _shape_xy(settings, rep)
            if xy:
                poly, dropped = _union_xy(*xy)
        if poly is None:                                       # không có FootPrint: chiếu Body xuống XY
            xy = _shape_xy(settings, sp)
            if xy:
                poly, dropped = _union_xy(*xy)
        if poly is None:
            model.warn(f"{fname}: IfcSpace '{sp.Name}' không dựng được footprint; bỏ qua")
            continue
        if dropped:
            model.warn(f"{fname}: IfcSpace '{sp.Name}' gồm {dropped + 1} mảnh rời; chỉ giữ mảnh lớn nhất")
        if not poly.is_valid:
            poly = make_valid(poly)
            if poly.geom_type != "Polygon":
                poly = max((g for g in poly.geoms if g.geom_type == "Polygon"), key=lambda g: g.area)
        psets = E.get_psets(sp)
        model.objs.append(Obj(
            "space", "ifc", sp.GlobalId, "IfcSpace", storey_by_id[st_el.id()].key, poly,
            {"name": sp.Name, "long_name": sp.LongName, "object_type": sp.ObjectType, "psets": psets,
             "ref": None, "label": sp.Name},
        ))
        n_sp += 1
    model.count("ifc:IfcSpace", n_sp)

    ifc_cfg = door_cfg.get("ifc", {})
    anchor = ifc_cfg.get("placement_anchor", "start")
    fallback_w = float(door_cfg.get("width_fallback_m", 0.9))
    n_door = 0
    for d in f.by_type("IfcDoor"):
        st_el = storey_of(d)
        if st_el is None or st_el.id() not in storey_by_id:
            model.warn(f"{fname}: IfcDoor '{d.Name}' không thuộc tầng nào; bỏ qua")
            continue
        n_door += 1
        line, center_src = door_line(src, d, anchor, fallback_w, settings)
        if center_src == "placement_with_anchor":
            model.warn(f"{fname}: tâm cửa lấy từ placement + anchor '{anchor}' (không có hình học); kiểm lại bằng file thật")
        model.objs.append(Obj(
            "door", "ifc", d.GlobalId, "IfcDoor", storey_by_id[st_el.id()].key, line,
            {"name": d.Name, "psets": E.get_psets(d), "center_source": center_src,
             "width_m": line.length, "attribs": {}, "op_type": getattr(d, "OperationType", None)},
        ))
    model.count("ifc:IfcDoor", n_door)

    candidates = [(el.is_a(), typ, el) for cls, typ in AREA_CLASSES for el in f.by_type(cls)]
    for el in f.by_type("IfcTransportElement"):
        kind = getattr(el, "PredefinedType", None) or getattr(el, "OperationType", None)   # IFC2X3 dùng OperationType
        if kind == "ELEVATOR":
            candidates.append(("IfcTransportElement", "elevator", el))
        else:
            model.count(f"ifc:skipped:IfcTransportElement.{kind}")
            model.warn(f"{fname}: IfcTransportElement '{el.Name}' ({kind}) chưa được ánh xạ; bỏ qua")
    for cls, typ, el in candidates:
        st_el = storey_of(el)
        if st_el is None or st_el.id() not in storey_by_id:
            model.warn(f"{fname}: {cls} '{el.Name}' không thuộc tầng nào; bỏ qua")
            continue
        poly, dropped = _footprint(settings, el)
        if poly is None:
            model.warn(f"{fname}: {cls} '{el.Name}' không dựng được footprint; bỏ qua")
            continue
        if dropped:
            model.warn(f"{fname}: {cls} '{el.Name}' gồm {dropped + 1} mảnh rời; chỉ giữ mảnh lớn nhất")
        model.objs.append(Obj(typ, "ifc", el.GlobalId, cls, storey_by_id[st_el.id()].key, poly,
                              {"name": el.Name, "psets": E.get_psets(el)}))
        model.count(f"ifc:{cls}")
    model.count("ifc:IfcWindow", len(f.by_type("IfcWindow")))      # cửa sổ: IMDF không có feature tương ứng, chỉ đếm


def door_line(src: IfcSource, door_el, anchor: str, fallback_w: float, settings=None) -> tuple[LineString, str]:
    """Đoạn cửa và nguồn tâm. Tâm lấy theo thứ tự: hình học IfcOpeningElement, bbox thân cửa, placement + anchor.

    Hướng là trục X của placement; bề rộng là OverallWidth, nếu thiếu thì bề rộng hình học, rồi giá trị dự phòng.
    """
    sc = src.unit_scale
    settings = settings or _settings()
    M = P.get_local_placement(door_el.ObjectPlacement)
    ox, oy = float(M[0][3]), float(M[1][3])
    ux, uy = float(M[0][0]), float(M[1][0])
    n = (ux * ux + uy * uy) ** 0.5 or 1.0
    ux, uy = ux / n, uy / n
    width = door_el.OverallWidth * sc if door_el.OverallWidth else None

    for rel in getattr(door_el, "FillsVoids", None) or []:
        opening = rel.RelatingOpeningElement
        if opening is not None and opening.Representation is not None:
            xy = _shape_xy(settings, opening)
            if xy:
                c, w = _bbox_center_width(xy[0], ux, uy)
                return _line(c, ux, uy, width or w), "opening_element_geometry"
    if door_el.Representation is not None:
        xy = _shape_xy(settings, door_el)
        if xy:
            c, w = _bbox_center_width(xy[0], ux, uy)
            return _line(c, ux, uy, width or w), "door_body_bbox"
    w = width or fallback_w
    if anchor == "start":
        c = (ox + ux * w / 2, oy + uy * w / 2)
    else:
        c = (ox, oy)
    return _line(c, ux, uy, w), "placement_with_anchor"


def _bbox_center_width(verts: np.ndarray, ux: float, uy: float) -> tuple[tuple[float, float], float]:
    xs, ys = verts[:, 0], verts[:, 1]
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    proj = verts[:, 0] * ux + verts[:, 1] * uy
    return (cx, cy), float(proj.max() - proj.min())


def _line(c: tuple[float, float], ux: float, uy: float, w: float) -> LineString:
    return LineString([(c[0] - ux * w / 2, c[1] - uy * w / 2), (c[0] + ux * w / 2, c[1] + uy * w / 2)])
