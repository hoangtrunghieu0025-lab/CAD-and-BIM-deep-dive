"""Tầng 0 (3D) — đọc hình học 3D của DXF: lưới mặt, khung dây (giữ cung chính xác), nét có độ dày (thickness).

Khác `read.py` (2D, chỉ lấy x,y, bỏ hình trên layer lạ): ở đây **không bỏ layer nào** (3D thường không có tên layer
có nghĩa), giữ cả toạ độ Z, và mở khối INSERT sâu hơn (mặc định 8 tầng; kho thật có khối lồng > 3 tầng chứa ~16% mặt).

Đọc được:
  * lưới mặt: POLYLINE polyface, POLYLINE polygon mesh (M×N), 3DFACE, MESH;
  * khung dây: LINE, ARC (giữ chính xác: đầu-giữa-cuối), CIRCLE (4 điểm), POLYLINE/LWPOLYLINE/ELLIPSE/SPLINE (làm phẳng);
  * "2,5D": thực thể 2D có `thickness` (mã 39) → thêm lăng trụ (`Mesh3D.source == "extrusion"`).
KHÔNG đọc được: 3DSOLID, BODY, REGION, SURFACE… (dữ liệu ACIS nhúng; cần bộ đọc ACIS) → chỉ đếm `unsupported:<loại>`.
Toạ độ trả về ở WCS, đã nhân `factor` (mét). Điểm là bộ ba (x, y, z).
"""
from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

from ezdxf import path as ezpath
from ezdxf.math import Vec3
from ezdxf.render import MeshBuilder

P3 = tuple[float, float, float]

ACIS_TYPES = {"3DSOLID", "BODY", "REGION", "SURFACE", "EXTRUDEDSURFACE", "LOFTEDSURFACE", "REVOLVEDSURFACE", "SWEPTSURFACE",
              "PLANESURFACE", "NURBSURFACE"}
_PATH_TYPES = {"LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE", "ELLIPSE", "SPLINE"}


@dataclass
class Mesh3D:
    layer: str
    kind: str                       # loại theo Classifier.layer_kind (có thể "unknown")
    handle: str
    top: str                        # handle INSERT cấp cao nhất chứa nó
    depth: int
    source: str                     # polyface | polygon_mesh | 3dface | mesh | extrusion
    vertices: list[P3] = field(default_factory=list)
    faces: list[tuple[int, ...]] = field(default_factory=list)


@dataclass
class Wire3D:
    layer: str
    kind: str
    handle: str
    top: str
    depth: int
    shape: str                      # polyline | arc3 (đầu, giữa, cuối) | circle4 (bốn điểm cách 90°)
    pts: list[P3] = field(default_factory=list)
    etype: str = ""


def _p(v: Any, f: float) -> P3:
    return (float(v[0]) * f, float(v[1]) * f, float(v[2]) * f)


def _arc_points(e: Any, f: float) -> list[P3]:
    """ARC -> [đầu, giữa, cuối] ở WCS."""
    c, r = e.dxf.center, float(e.dxf.radius)
    a0, a1 = float(e.dxf.start_angle), float(e.dxf.end_angle)
    if a1 <= a0:
        a1 += 360.0
    out = []
    for a in (a0, (a0 + a1) / 2.0, a1):
        t = math.radians(a)
        out.append(_p(e.ocs().to_wcs(Vec3(c.x + r * math.cos(t), c.y + r * math.sin(t), c.z)), f))
    return out


def _circle_points(e: Any, f: float) -> list[P3]:
    c, r = e.dxf.center, float(e.dxf.radius)
    return [_p(e.ocs().to_wcs(Vec3(c.x + r * math.cos(t), c.y + r * math.sin(t), c.z)), f)
            for t in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)]


def _extrude(pts: list[P3], closed: bool, vec: P3) -> tuple[list[P3], list[tuple[int, ...]]]:
    """Lăng trụ từ đường `pts` kéo theo vector `vec`: mặt bên là tứ giác, đường kín thì thêm hai nắp."""
    if closed and len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    n = len(pts)
    if n < 2:
        return [], []
    verts = pts + [(x + vec[0], y + vec[1], z + vec[2]) for x, y, z in pts]
    segs = n if closed else n - 1
    faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(segs)]
    if closed and n >= 3:
        faces += [tuple(range(n)), tuple(range(n, 2 * n))]
    return verts, faces


def iter_geometry3d(
    msp: Any,
    factor: float,
    layer_kind: Callable[[str], str],
    *,
    max_depth: int = 8,
    flatten_m: float = 0.05,
    max_items: int | None = None,
    stats: Counter | None = None,
) -> Iterator[Mesh3D | Wire3D]:
    """Duyệt modelspace, mở khối INSERT tới `max_depth`. `stats` đếm: entities, meshes, wires, faces, unsupported:<loại>,
    other:<loại>, insert_too_deep, errors, truncated."""
    st = stats if stats is not None else Counter()
    produced = 0
    delta = flatten_m / factor if factor else flatten_m

    def walk(e: Any, depth: int, parent_layer: str | None, top: str | None) -> Iterator[Mesh3D | Wire3D]:
        nonlocal produced
        if max_items is not None and produced >= max_items:
            st["truncated"] = 1
            return
        et = e.dxftype()
        layer = e.dxf.layer
        if layer == "0" and parent_layer:
            layer = parent_layer
        kind = layer_kind(layer)
        handle = e.dxf.handle
        top_h = top or handle
        st["entities"] += 1

        def mesh(source: str, v: list[P3], fc: list[tuple[int, ...]]) -> Mesh3D:
            nonlocal produced
            produced += 1
            st["meshes"] += 1
            st["faces"] += len(fc)
            st[f"mesh:{source}"] += 1
            return Mesh3D(layer, kind, handle, top_h, depth, source, v, fc)

        def wire(shape: str, pts: list[P3]) -> Wire3D:
            nonlocal produced
            produced += 1
            st["wires"] += 1
            st[f"wire:{et}"] += 1
            return Wire3D(layer, kind, handle, top_h, depth, shape, pts, et)

        if et == "INSERT":
            if depth < max_depth:
                try:
                    for child in e.virtual_entities():
                        yield from walk(child, depth + 1, layer, top_h)
                except Exception:           # khối hỏng/thiếu định nghĩa
                    st["errors"] += 1
            else:
                st["insert_too_deep"] += 1
            return
        try:
            if et == "POLYLINE" and e.is_poly_face_mesh:
                mb = MeshBuilder.from_polyface(e)
                fc = [tuple(int(i) for i in f) for f in mb.faces if len(f) >= 3]
                if fc:
                    yield mesh("polyface", [_p(v, factor) for v in mb.vertices], fc)
            elif et == "POLYLINE" and e.is_polygon_mesh:
                m, n = int(e.dxf.m_count), int(e.dxf.n_count)
                vs = [_p(v.dxf.location, factor) for v in e.vertices]
                if m * n == len(vs) and m > 1 and n > 1:
                    mi = m if e.is_m_closed else m - 1
                    nj = n if e.is_n_closed else n - 1
                    fc = [(i * n + j, ((i + 1) % m) * n + j, ((i + 1) % m) * n + (j + 1) % n, i * n + (j + 1) % n)
                          for i in range(mi) for j in range(nj)]
                    yield mesh("polygon_mesh", vs, fc)
            elif et == "3DFACE":
                vs = [_p(e.dxf.get(k), factor) for k in ("vtx0", "vtx1", "vtx2", "vtx3")]
                ring = vs[:3] if vs[3] == vs[2] else vs
                yield mesh("3dface", ring, [tuple(range(len(ring)))])
            elif et == "MESH":
                vs = [_p(v, factor) for v in e.vertices]
                fc = [tuple(int(i) for i in f) for f in e.faces if len(f) >= 3]
                if fc:
                    yield mesh("mesh", vs, fc)
            elif et in _PATH_TYPES:
                if et == "LINE":
                    pts = [_p(e.dxf.start, factor), _p(e.dxf.end, factor)]
                    yield wire("polyline", pts)
                elif et == "ARC":
                    pts = _arc_points(e, factor)
                    yield wire("arc3", pts)
                elif et == "CIRCLE":
                    pts = _circle_points(e, factor)
                    yield wire("circle4", pts)
                else:
                    pts = [_p(v, factor) for v in ezpath.make_path(e).flattening(delta)]
                    if len(pts) >= 2:
                        yield wire("polyline", pts)
                    else:
                        pts = []
                th = float(e.dxf.get("thickness", 0.0)) if et != "POLYLINE" or not e.is_3d_polyline else 0.0
                if th and pts:                                    # "2,5D": nét có độ dày -> lăng trụ
                    ext = Vec3(e.dxf.get("extrusion", (0, 0, 1))).normalize() * (th * factor)
                    if et in ("ARC", "CIRCLE"):                   # cần điểm làm phẳng để dựng mặt bên
                        pts = [_p(v, factor) for v in ezpath.make_path(e).flattening(delta)]
                    closed = et == "CIRCLE" or bool(getattr(e, "is_closed", False) or getattr(e, "closed", False))
                    v, fc = _extrude(pts, closed, (ext.x, ext.y, ext.z))
                    if fc:
                        yield mesh("extrusion", v, fc)
            elif et in ACIS_TYPES:
                st[f"unsupported:{et}"] += 1
            else:
                st[f"other:{et}"] += 1
        except Exception:
            st["errors"] += 1

    for e in msp:
        yield from walk(e, 0, None, None)
