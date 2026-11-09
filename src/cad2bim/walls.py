"""Tầng 3 — dựng tường: ghép hai nét song song thành (đường tim, độ dày) và nối góc.

Ý tưởng (TASK-018; đã viết lại, không chép mã):
  * roomgraph (MIT) `walls.py`: tường CAD vẽ bằng HAI NÉT SONG SONG; gom đoạn lên đường thẳng vô hạn rồi ghép
    cặp qua khoảng độ dày hợp lý; khoảng hở của cặp là ứng viên lỗ mở.
  * FreeCAD `DraftGeomUtils.connect`/Cloud2BIM: nối góc bằng giao điểm của hai đường tim.
Mọi độ dày suy ra từ cặp nét là `derived`; tường chỉ có một nét thì độ dày lấy từ cấu hình và là `assumed`.
Thuần hình học, đơn vị mét.
"""
from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field

from shapely import STRtree, set_precision
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from .segments import Pt, Seg, node_and_chain

Interval = tuple[float, float]


@dataclass
class WallPiece:
    axis: LineString              # đường tim (mét)
    thickness: float
    source: str                   # "pair" (độ dày suy ra từ hai nét) | "single" (độ dày theo cấu hình)
    theta: float = 0.0            # góc hướng (rad), chỉ có với "pair"
    d: float = 0.0                # độ lệch vuông góc của đường tim so với gốc, chỉ có với "pair"
    t0: float = 0.0               # đoạn dọc đường tim [t0, t1]
    t1: float = 0.0
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------- khoảng (interval)
def _merge(iv: list[Interval], gap: float = 1e-6) -> list[Interval]:
    out: list[Interval] = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1] + gap:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def _intersect(x: list[Interval], y: list[Interval]) -> list[Interval]:
    out: list[Interval] = []
    i = j = 0
    while i < len(x) and j < len(y):
        a, b = max(x[i][0], y[j][0]), min(x[i][1], y[j][1])
        if b > a:
            out.append((a, b))
        if x[i][1] < y[j][1]:
            i += 1
        else:
            j += 1
    return out


def _subtract(x: list[Interval], cut: list[Interval]) -> list[Interval]:
    out: list[Interval] = []
    for a, b in x:
        cur = a
        for c, d in cut:
            if d <= cur or c >= b:
                continue
            if c > cur:
                out.append((cur, c))
            cur = max(cur, d)
        if cur < b:
            out.append((cur, b))
    return out


# ---------------------------------------------------------------- gom đoạn lên đường thẳng vô hạn
@dataclass
class _Line:
    d: float
    cover: list[Interval]


@dataclass
class _Group:
    theta: float
    lines: list[_Line]


def _group_lines(segs: Sequence[Seg], ang_tol: float, off_tol: float) -> list[_Group]:
    items = []
    for (p, q) in segs:
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy)
        if length < 1e-9:
            continue
        ux, uy = dx / length, dy / length
        if ux < -1e-12 or (abs(ux) <= 1e-12 and uy < 0):
            ux, uy, p, q = -ux, -uy, q, p
        items.append((math.atan2(uy, ux), p, q, length))
    if not items:
        return []
    items.sort(key=lambda it: it[0])
    clusters: list[list[tuple]] = [[items[0]]]
    for it in items[1:]:
        if it[0] - clusters[-1][-1][0] <= ang_tol:
            clusters[-1].append(it)
        else:
            clusters.append([it])
    # vòng góc: các đoạn gần thẳng đứng có θ ≈ -π/2 và ≈ +π/2 là cùng hướng
    if len(clusters) > 1 and clusters[0][0][0] + math.pi - clusters[-1][-1][0] <= ang_tol:
        last = clusters.pop()
        clusters[0] = clusters[0] + last
        wrapped = True
    else:
        wrapped = False
    groups: list[_Group] = []
    for ci, cl in enumerate(clusters):
        # góc trung bình có trọng số độ dài; với cụm vòng, đưa các θ gần -π/2 về +π/2
        ths = []
        for th, *_rest in cl:
            ths.append(th + math.pi if (wrapped and ci == 0 and th < 0) else th)
        w = [it[3] for it in cl]
        theta = sum(t * wi for t, wi in zip(ths, w)) / sum(w)
        ux, uy = math.cos(theta), math.sin(theta)
        nx, ny = -uy, ux
        recs = []
        for (th, p, q, _l) in cl:
            t0, t1 = ux * p[0] + uy * p[1], ux * q[0] + uy * q[1]
            d = nx * (p[0] + q[0]) / 2 + ny * (p[1] + q[1]) / 2
            recs.append((d, (min(t0, t1), max(t0, t1))))
        recs.sort()
        lines: list[_Line] = []
        cur = [recs[0]]
        for r in recs[1:]:
            if r[0] - cur[-1][0] <= off_tol:
                cur.append(r)
            else:
                lines.append(_Line(sum(x[0] for x in cur) / len(cur), _merge([x[1] for x in cur])))
                cur = [r]
        lines.append(_Line(sum(x[0] for x in cur) / len(cur), _merge([x[1] for x in cur])))
        groups.append(_Group(theta, lines))
    return groups


def _point(theta: float, t: float, d: float) -> Pt:
    ux, uy = math.cos(theta), math.sin(theta)
    return (ux * t - uy * d, uy * t + ux * d)


def pair_walls(
    segs: Sequence[Seg],
    thick_min: float = 0.05,
    thick_max: float = 0.45,
    min_len: float = 0.30,
    ang_tol_deg: float = 1.0,
    off_tol: float = 0.01,
    leftover_min: float = 0.05,
) -> tuple[list[WallPiece], list[Seg]]:
    """Ghép hai nét song song cách nhau trong [thick_min, thick_max] thành tường.

    Trả về (các mảnh tường có độ dày suy ra, các đoạn thừa chưa ghép). Mỗi phần của một nét chỉ dùng một lần;
    ưu tiên cặp có phần chồng dài nhất. `min_len` là độ dài chồng tối thiểu để thành tường.
    """
    pieces: list[WallPiece] = []
    leftovers: list[Seg] = []
    for g in _group_lines(segs, math.radians(ang_tol_deg), off_tol):
        avail = [list(ln.cover) for ln in g.lines]
        cands: list[tuple[float, float, int, int]] = []
        for i in range(len(g.lines)):
            for j in range(i + 1, len(g.lines)):
                delta = g.lines[j].d - g.lines[i].d
                if delta > thick_max:
                    break
                if delta < thick_min:
                    continue
                ov = _intersect(g.lines[i].cover, g.lines[j].cover)
                tot = sum(b - a for a, b in ov if b - a >= min_len)
                if tot > 0:
                    cands.append((tot, delta, i, j))
        cands.sort(key=lambda c: (-c[0], c[1]))
        for _tot, delta, i, j in cands:
            ov = [(a, b) for a, b in _intersect(avail[i], avail[j]) if b - a >= min_len]
            if not ov:
                continue
            dmid = (g.lines[i].d + g.lines[j].d) / 2
            for a, b in ov:
                axis = LineString([_point(g.theta, a, dmid), _point(g.theta, b, dmid)])
                pieces.append(WallPiece(axis, delta, "pair", g.theta, dmid, a, b))
            avail[i] = _subtract(avail[i], ov)
            avail[j] = _subtract(avail[j], ov)
        for ln, av in zip(g.lines, avail):
            for a, b in av:
                if b - a >= leftover_min:
                    leftovers.append((_point(g.theta, a, ln.d), _point(g.theta, b, ln.d)))
    # "gốc góc": phần nét thừa ngắn (<= thick_max) nằm sát một tường đã ghép là mặt ngoài của góc, không phải tường riêng
    if pieces and leftovers:
        rects = [p.axis.buffer(p.thickness / 2, cap_style="flat") for p in pieces]
        tree = STRtree(rects)
        kept: list[Seg] = []
        for (a, b) in leftovers:
            length = math.dist(a, b)
            mid = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            is_stub = False
            if length <= thick_max:
                for k in tree.query(mid.buffer(length)):
                    if rects[int(k)].distance(mid) <= length / 2 + 2 * off_tol:
                        is_stub = True
                        break
            if not is_stub:
                kept.append((a, b))
        leftovers = kept
    return pieces, leftovers


def opening_candidates(pieces: Sequence[WallPiece], min_gap: float = 0.5, max_gap: float = 4.0,
                       off_tol: float = 0.02) -> list[dict]:
    """Khoảng hở giữa hai mảnh tường cùng đường tim, cùng độ dày -> ứng viên lỗ mở (cửa/cửa sổ)."""
    buckets: dict[tuple, list[WallPiece]] = defaultdict(list)
    for p in pieces:
        if p.source != "pair":
            continue
        buckets[(round(p.theta, 2), round(p.d / off_tol), round(p.thickness, 2))].append(p)
    out: list[dict] = []
    for ps in buckets.values():
        ps.sort(key=lambda p: p.t0)
        for a, b in zip(ps, ps[1:]):
            gap = b.t0 - a.t1
            if min_gap <= gap <= max_gap:
                c = _point(a.theta, (a.t1 + b.t0) / 2, a.d)
                out.append({"center": c, "width": gap, "theta": a.theta, "thickness": a.thickness})
    return out


# ---------------------------------------------------------------- dựng hình tường
def _strip(centre: Pt, theta: float, thickness: float, reach: float) -> Polygon:
    u = (math.cos(theta), math.sin(theta))
    a = (centre[0] - u[0] * reach, centre[1] - u[1] * reach)
    b = (centre[0] + u[0] * reach, centre[1] + u[1] * reach)
    return LineString([a, b]).buffer(thickness / 2, cap_style="flat")


def _theta(line: LineString) -> float:
    (x0, y0), (x1, y1) = line.coords[0], line.coords[-1]
    return math.atan2(y1 - y0, x1 - x0)


def footprint(pieces: Sequence[WallPiece], mitre_limit: float = 5.0, corner_tol: float = 0.02) -> BaseGeometry:
    """Hợp hình các tường. Tường "pair" là hình chữ nhật đầu phẳng + mảnh vá ở các góc/chữ T; tường "single"
    (chuỗi tim nhiều đoạn) dùng buffer mitre. Mảnh vá = giao hai dải vô hạn của hai tường gần nhau không song song."""
    if not pieces:
        return Polygon()
    rects: list[BaseGeometry] = []
    pair_idx: list[int] = []
    for k, p in enumerate(pieces):
        if p.source == "pair":
            rects.append(p.axis.buffer(p.thickness / 2, cap_style="flat"))
            pair_idx.append(k)
        else:
            rects.append(p.axis.buffer(p.thickness / 2, cap_style="flat", join_style="mitre", mitre_limit=mitre_limit))
    patches: list[BaseGeometry] = []
    if len(pair_idx) > 1:
        tree = STRtree([rects[k] for k in pair_idx])
        for a_i, ka in enumerate(pair_idx):
            pa = pieces[ka]
            for b_i in tree.query(rects[ka].buffer(pa.thickness)):
                b_i = int(b_i)
                if b_i <= a_i:
                    continue
                pb = pieces[pair_idx[b_i]]
                if abs(math.sin(_theta(pa.axis) - _theta(pb.axis))) < 0.1:
                    continue
                inter = _axis_intersection(pa.axis, pb.axis)
                if inter is None:
                    continue
                reach = pa.thickness + pb.thickness
                if (pa.axis.distance(Point(inter)) <= pb.thickness / 2 + corner_tol
                        and pb.axis.distance(Point(inter)) <= pa.thickness / 2 + corner_tol):
                    patch = _strip(inter, _theta(pa.axis), pa.thickness, reach).intersection(
                        _strip(inter, _theta(pb.axis), pb.thickness, reach))
                    if not patch.is_empty:
                        patches.append(patch)
    geom = set_precision(unary_union(rects + patches), 1e-6)
    if geom.geom_type == "MultiPolygon" and len(geom.geoms) == 1:   # bỏ lớp bọc một phần tử
        geom = geom.geoms[0]
    return geom


def _axis_intersection(a: LineString, b: LineString) -> Pt | None:
    (x1, y1), (x2, y2) = a.coords[0], a.coords[-1]
    (x3, y3), (x4, y4) = b.coords[0], b.coords[-1]
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-12:
        return None
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return (px, py)


def single_walls(segs: Sequence[Seg], thickness: float) -> list[WallPiece]:
    """Tường chỉ có một nét: noding + ghép chuỗi; độ dày là giá trị cấu hình (assumed)."""
    return [WallPiece(ch, thickness, "single") for ch in node_and_chain(segs)]
