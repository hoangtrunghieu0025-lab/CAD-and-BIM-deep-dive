"""Tầng 0 — đọc DXF thành các nguyên thủy phẳng ở hệ toạ độ thế giới (WCS), đơn vị mét.

Khác `build` cũ: mở khối INSERT (virtual_entities, đệ quy có giới hạn), giữ cung của LWPOLYLINE (`ezdxf.path.make_path`
thay vì `get_points("xy")` vốn bỏ bulge), đổi OCS->WCS cho cung/tròn nằm trong khối lật gương, đoán đơn vị khi
$INSUNITS = 0 (kết quả luôn là giả định). Bỏ qua hình học của layer chú thích/không rõ để tiết kiệm thời gian.
"""
from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

from ezdxf import path as ezpath
from ezdxf import units as ezunits

Pt = tuple[float, float]

_PATH_TYPES = {"LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE", "ELLIPSE", "SPLINE"}
_UNIT_FACTOR = {"m": 1.0, "mm": 1e-3, "cm": 1e-2, "in": 0.0254, "ft": 0.3048}


@dataclass
class Prim:
    etype: str                       # loại DXF gốc
    layer: str                       # layer sau khi kế thừa từ INSERT (layer "0" lấy layer của khối chứa)
    kind: str                        # loại theo Classifier.layer_kind(layer)
    handle: str
    top: str                         # handle của INSERT cấp cao nhất chứa nó (== handle nếu ở cấp cao nhất)
    depth: int = 0
    pts: list[Pt] = field(default_factory=list)   # đường/vùng (mét)
    closed: bool = False
    text: str | None = None
    block: str | None = None         # tên khối (với INSERT)
    ins: tuple[float, float, float, float, float] | None = None   # x, y, xoay(độ), sx, sy
    attribs: dict[str, str] = field(default_factory=dict)
    radius: float | None = None      # với ARC/CIRCLE (mét)


def resolve_units(doc: Any, cfg_units: dict, extents_m_by_unit: Callable[[str], float] | None = None,
                  fallback: str | None = None) -> tuple[float, str, str]:
    """-> (hệ số nhân sang mét, tên đơn vị, cách xác định).

    Cách xác định: "insunits" (khai báo, đã qua kiểm hợp lý) | "insunits_conflict" (khai báo nhưng kích thước bản vẽ
    vô lý nên đổi sang đơn vị hợp lý đầu tiên) | "guess" (không khai báo, đoán theo kích thước) | "fallback".
    $INSUNITS hay sai trong thực tế (mẫu mặc định là mm dù vẽ theo mét), nên luôn đối chiếu với kích thước bản vẽ."""
    code = doc.header.get("$INSUNITS", 0)
    declared = {ezunits.M: "m", ezunits.MM: "mm", ezunits.CM: "cm", ezunits.IN: "in", ezunits.FT: "ft"}.get(code)
    lo, hi = cfg_units.get("plausible_extent_m", [3.0, 300.0])
    order = cfg_units.get("guess_order", ["m", "mm", "cm", "in"])
    if declared:
        if extents_m_by_unit is not None:
            size = extents_m_by_unit(declared)
            if size > 0 and not (lo <= size <= hi):                   # bản vẽ rỗng (size == 0) thì giữ khai báo
                for cand in order:
                    if lo <= extents_m_by_unit(cand) <= hi:
                        return _UNIT_FACTOR[cand], cand, "insunits_conflict"
        return _UNIT_FACTOR[declared], declared, "insunits"
    if extents_m_by_unit is not None:
        for cand in order:
            if lo <= extents_m_by_unit(cand) <= hi:
                return _UNIT_FACTOR[cand], cand, "guess"
    fb = fallback or "m"
    return _UNIT_FACTOR[fb], fb, "fallback"


def _path_points(e: Any, factor: float, delta_m: float) -> tuple[list[Pt], bool, float | None]:
    if e.dxftype() == "LINE":
        s, t = e.dxf.start, e.dxf.end
        return [(s.x * factor, s.y * factor), (t.x * factor, t.y * factor)], False, None
    p = ezpath.make_path(e)
    pts = [(v.x * factor, v.y * factor) for v in p.flattening(delta_m / factor)]
    closed = bool(getattr(e, "closed", False) or getattr(e, "is_closed", False) or p.is_closed)
    radius = float(e.dxf.radius) * factor if e.dxftype() in ("ARC", "CIRCLE") else None
    return pts, closed, radius


def iter_prims(
    msp: Any,
    factor: float,
    layer_kind: Callable[[str], str],
    *,
    max_depth: int = 3,
    flatten_m: float = 0.005,
    max_prims: int | None = None,
    stats: Counter | None = None,
    skip_kinds: tuple[str, ...] = ("annotation", "unknown"),
) -> Iterator[Prim]:
    """Duyệt modelspace, mở khối INSERT. `stats` đếm: entities, skipped:<kind>, errors, truncated."""
    st = stats if stats is not None else Counter()
    produced = 0

    def walk(e: Any, depth: int, parent_layer: str | None, top: str | None) -> Iterator[Prim]:
        nonlocal produced
        if max_prims is not None and produced >= max_prims:
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
        if et == "INSERT":
            ins = e.dxf.insert
            attribs = {a.dxf.tag: a.dxf.text for a in getattr(e, "attribs", [])}
            produced += 1
            yield Prim(et, layer, kind, handle, top_h, depth, block=e.dxf.name,
                       pts=[(ins.x * factor, ins.y * factor)],
                       ins=(ins.x * factor, ins.y * factor, float(e.dxf.get("rotation", 0.0)),
                            float(e.dxf.get("xscale", 1.0)), float(e.dxf.get("yscale", 1.0))), attribs=attribs)
            if depth < max_depth:
                try:
                    for child in e.virtual_entities():
                        yield from walk(child, depth + 1, layer, top_h)
                except Exception:       # khối hỏng/thiếu định nghĩa
                    st["errors"] += 1
            return
        if kind in skip_kinds and et not in ("TEXT", "MTEXT"):
            st[f"skipped:{kind}"] += 1
            st[f"layer:{kind}:{layer}"] += 1
            return
        try:
            if et in _PATH_TYPES:
                pts, closed, radius = _path_points(e, factor, flatten_m)
                if len(pts) >= 2:
                    produced += 1
                    yield Prim(et, layer, kind, handle, top_h, depth, pts=pts, closed=closed, radius=radius)
            elif et == "HATCH":
                for sub in ezpath.from_hatch(e).sub_paths():
                    pts = [(v.x * factor, v.y * factor) for v in sub.flattening(flatten_m / factor)]
                    if len(pts) >= 3:
                        produced += 1
                        yield Prim(et, layer, kind, handle, top_h, depth, pts=pts, closed=True)
            elif et in ("TEXT", "MTEXT"):
                text = e.plain_text() if et == "MTEXT" else e.dxf.text
                ins = e.dxf.insert
                produced += 1
                yield Prim(et, layer, kind, handle, top_h, depth, text=" ".join(str(text).split()),
                           pts=[(ins.x * factor, ins.y * factor)])
            else:
                st[f"other:{et}"] += 1
        except Exception:
            st["errors"] += 1

    for e in msp:
        yield from walk(e, 0, None, None)


def robust_span(points: list[Pt]) -> float:
    """Cạnh lớn nhất của đám điểm (đơn vị bản vẽ); ít điểm dùng toàn dải, nhiều điểm bỏ 1% hai đầu để tránh điểm rác."""
    if len(points) < 2:
        return 0.0

    def span(v: list[float]) -> float:
        v = sorted(v)
        if len(v) < 200:
            return v[-1] - v[0]
        return v[int(0.99 * (len(v) - 1))] - v[int(0.01 * (len(v) - 1))]

    return max(span([p[0] for p in points]), span([p[1] for p in points]))


def probe_span(msp: Any, max_depth: int = 3, probe_prims: int = 4000) -> float:
    """Kích thước bản vẽ theo đơn vị bản vẽ, đo trên HÌNH HỌC ĐÃ MỞ KHỐI của vài nghìn nguyên thủy đầu tiên
    (mọi loại layer). Tránh sai khi mọi INSERT cấp cao nhất đặt tại gốc và chứa toạ độ thật."""
    pts: list[Pt] = []
    for pr in iter_prims(msp, 1.0, lambda _l: "probe", max_depth=max_depth, flatten_m=0.01, max_prims=probe_prims,
                         skip_kinds=()):
        if pr.etype == "INSERT" or pr.etype in ("TEXT", "MTEXT"):
            continue                                   # điểm chèn không đại diện cho kích thước
        pts.extend(pr.pts)
    return robust_span(pts)


def guess_extent_m(msp: Any, unit: str, sample: int = 20000) -> float:
    """Cạnh lớn nhất (mét) của phần lớn bản vẽ nếu coi đơn vị là `unit`; dùng phân vị 1–99% để bỏ điểm rác."""
    return raw_span(msp, sample) * _UNIT_FACTOR[unit]


def raw_span(msp: Any, sample: int = 20000) -> float:
    """Cạnh lớn nhất của bản vẽ theo ĐƠN VỊ BẢN VẼ (chưa đổi sang mét); tính một lần rồi nhân với hệ số."""
    xs: list[float] = []
    ys: list[float] = []
    for i, e in enumerate(msp):
        if i >= sample:
            break
        try:
            if e.dxftype() == "LINE":
                xs += [e.dxf.start.x, e.dxf.end.x]
                ys += [e.dxf.start.y, e.dxf.end.y]
            elif e.dxftype() in ("CIRCLE", "ARC", "INSERT", "TEXT", "MTEXT"):
                p = e.dxf.center if e.dxftype() in ("CIRCLE", "ARC") else e.dxf.insert
                xs.append(p.x)
                ys.append(p.y)
            elif e.dxftype() == "LWPOLYLINE":
                for x, y in e.get_points("xy"):
                    xs.append(x)
                    ys.append(y)
        except Exception:
            continue
    if len(xs) < 2:
        return 0.0
    def span(v: list[float]) -> float:
        v = sorted(v)
        if len(v) < 200:                      # ít điểm: dùng toàn dải; nhiều điểm: bỏ 1% hai đầu để tránh điểm rác
            return v[-1] - v[0]
        return v[int(0.99 * (len(v) - 1))] - v[int(0.01 * (len(v) - 1))]
    return max(span(xs), span(ys))
