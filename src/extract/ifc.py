"""extract — IFC (spec 4.3): tầng, footprint phòng, đoạn cửa, thuộc tính."""
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
    """(verts Nx3 mét, faces Mx3) của một element/representation; None nếu không dựng được."""
    try:
        sh = ifcopenshell.geom.create_shape(settings, element_or_rep)
    except Exception:  # noqa: BLE001
        return None
    v = np.array(sh.geometry.verts).reshape(-1, 3)
    f = np.array(sh.geometry.faces).reshape(-1, 3)
    return (v, f) if len(v) and len(f) else None


def _union_xy(v: np.ndarray, f: np.ndarray) -> Polygon | None:
    tris = [Polygon(v[i][:, :2]) for i in f]
    tris = [t for t in tris if t.area > 1e-9]
    if not tris:
        return None
    u = unary_union(tris).simplify(1e-9)
    if u.geom_type == "MultiPolygon":
        u = max(u.geoms, key=lambda g: g.area)       # phòng gồm nhiều mảnh rời: lấy mảnh lớn nhất (+ cảnh báo ở nơi gọi)
    return u if u.geom_type == "Polygon" and not u.is_empty else None


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

    # --- toà nhà
    b = f.by_type("IfcBuilding")
    if b:
        model.building.name = model.building.name or b[0].LongName or b[0].Name
        model.building.ifc_ref = b[0].GlobalId
    else:
        model.warn(f"{fname}: không có IfcBuilding")

    # --- tầng (Elevation là OPTIONAL: placement Z, rồi thứ tự file)
    storey_by_id: dict[int, Storey] = {}
    for k, s in enumerate(f.by_type("IfcBuildingStorey")):
        elev = s.Elevation * sc if s.Elevation is not None else None
        if elev is None:
            try:
                elev = float(P.get_local_placement(s.ObjectPlacement)[2][3]) * 1.0
                model.warn(f"{fname}: tầng '{s.Name}' thiếu Elevation, dùng Z của placement")
            except Exception:  # noqa: BLE001
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

    # --- phòng
    n_sp = 0
    for sp in f.by_type("IfcSpace"):
        st_el = storey_of(sp)
        if st_el is None or st_el.id() not in storey_by_id:
            model.warn(f"{fname}: IfcSpace '{sp.Name}' không thuộc tầng nào; bỏ qua")
            continue
        poly = None
        rep = R.get_representation(sp, "Plan", "FootPrint", "GRAPH_VIEW")
        if rep is not None:
            xy = _shape_xy(settings, rep)
            if xy:
                poly = _union_xy(*xy)
        if poly is None:                                       # dự phòng: chiếu Body xuống XY
            xy = _shape_xy(settings, sp)
            if xy:
                poly = _union_xy(*xy)
        if poly is None:
            model.warn(f"{fname}: IfcSpace '{sp.Name}' không dựng được footprint; bỏ qua")
            continue
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

    # --- cửa
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
             "width_m": line.length, "attribs": {}},
        ))
    model.count("ifc:IfcDoor", n_door)
    model.count("ifc:IfcWall", len(f.by_type("IfcWall")))


def door_line(src: IfcSource, door_el, anchor: str, fallback_w: float, settings=None) -> tuple[LineString, str]:
    """Đoạn cửa (spec 4.3): tâm theo thứ tự opening_element_geometry -> door_body_bbox -> placement_with_anchor.

    Trả (LineString, nguồn_tâm). Hướng = trục X cục bộ của placement; bề rộng = OverallWidth -> bề rộng hình học -> dự phòng.
    """
    sc = src.unit_scale
    settings = settings or _settings()
    M = P.get_local_placement(door_el.ObjectPlacement)
    ox, oy = float(M[0][3]), float(M[1][3])
    ux, uy = float(M[0][0]), float(M[1][0])
    n = (ux * ux + uy * uy) ** 0.5 or 1.0
    ux, uy = ux / n, uy / n
    width = door_el.OverallWidth * sc if door_el.OverallWidth else None

    # 1) hình học IfcOpeningElement mà cửa lấp
    for rel in getattr(door_el, "FillsVoids", None) or []:
        opening = rel.RelatingOpeningElement
        if opening is not None and opening.Representation is not None:
            xy = _shape_xy(settings, opening)
            if xy:
                c, w = _bbox_center_width(xy[0], ux, uy)
                return _line(c, ux, uy, width or w), "opening_element_geometry"
    # 2) bbox thân cửa
    if door_el.Representation is not None:
        xy = _shape_xy(settings, door_el)
        if xy:
            c, w = _bbox_center_width(xy[0], ux, uy)
            return _line(c, ux, uy, width or w), "door_body_bbox"
    # 3) placement + anchor
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
