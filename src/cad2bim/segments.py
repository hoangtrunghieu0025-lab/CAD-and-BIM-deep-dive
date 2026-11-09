"""Tầng 2 — làm sạch đoạn thẳng: gộp đầu mút, kéo dài đầu rời, tách tại giao điểm, ghép chuỗi.

Thuần hình học (shapely), đơn vị mét, không biết gì về layer hay IFC; kiểm riêng được.
Nguồn ý tưởng (TASK-018): kéo dài đầu rời tới đường tim gần nhất và tách chữ T theo Cloud2BIM
(`space_generator.py`, MIT); nối góc mitre theo FreeCAD `DraftGeomUtils.connect` (chỉ nguyên lý).
Đã kiểm nguyên lý bằng research/06-cad-to-bim/poc/wall_corner_join_trial.py.
"""
from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

from shapely import STRtree, set_precision
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, unary_union

Pt = tuple[float, float]
Seg = tuple[Pt, Pt]

EPS = 1e-9


def explode(paths: Iterable[Sequence[Pt]], min_len: float = 1e-6) -> list[Seg]:
    """Đường gấp khúc -> các đoạn thẳng liên tiếp; bỏ đoạn dài < min_len."""
    out: list[Seg] = []
    for pts in paths:
        for a, b in zip(pts, pts[1:]):
            if math.dist(a, b) >= min_len:
                out.append(((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))))
    return out


def snap_endpoints(segs: Sequence[Seg], tol: float) -> list[Seg]:
    """Gộp các đầu mút cách nhau <= tol về cùng một toạ độ (trung bình cụm). Bỏ đoạn suy biến sau khi gộp."""
    if tol <= 0 or not segs:
        return list(segs)
    pts: list[Pt] = [p for s in segs for p in s]
    parent = list(range(len(pts)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    cell = tol
    grid: dict[tuple[int, int], list[int]] = {}
    for i, (x, y) in enumerate(pts):
        grid.setdefault((math.floor(x / cell), math.floor(y / cell)), []).append(i)
    for (cx, cy), idx in grid.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in grid.get((cx + dx, cy + dy), ()):
                    for i in idx:
                        if i < j and math.dist(pts[i], pts[j]) <= tol:
                            ri, rj = find(i), find(j)
                            if ri != rj:
                                parent[rj] = ri
    sums: dict[int, list[float]] = {}
    for i, (x, y) in enumerate(pts):
        r = find(i)
        s = sums.setdefault(r, [0.0, 0.0, 0.0])
        s[0] += x
        s[1] += y
        s[2] += 1
    centre = {r: (s[0] / s[2], s[1] / s[2]) for r, s in sums.items()}
    out: list[Seg] = []
    for k in range(0, len(pts), 2):
        a, b = centre[find(k)], centre[find(k + 1)]
        if math.dist(a, b) > EPS:
            out.append((a, b))
    return out


def _touches(p: Pt, tree: STRtree, lines: list[LineString], skip: int, eps: float) -> bool:
    pt = Point(p)
    for j in tree.query(pt.buffer(eps)):
        if int(j) != skip and lines[int(j)].distance(pt) <= eps:
            return True
    return False


def extend_free_ends(segs: Sequence[Seg], tol: float, eps: float = 1e-6) -> tuple[list[Seg], int]:
    """Đầu mút không chạm đoạn nào khác: bắn tia theo hướng đoạn, kéo dài tới giao điểm gần nhất nếu <= tol.

    Trả về (danh sách mới, số đầu đã kéo dài). Kéo dài bao gồm cả biên (khoảng cách == tol vẫn tính);
    nên chọn tol lớn hơn khe hở dự kiến rõ rệt.
    """
    if tol <= 0 or not segs:
        return list(segs), 0
    lines = [LineString(s) for s in segs]
    tree = STRtree(lines)
    out: list[Seg] = []
    n_ext = 0
    for i, (a, b) in enumerate(segs):
        new = [a, b]
        for end in (0, 1):
            p, q = new[end], new[1 - end]
            if _touches(p, tree, lines, i, max(eps * 10, 1e-9)):
                continue
            d = (p[0] - q[0], p[1] - q[1])
            length = math.hypot(*d)
            if length < EPS:
                continue
            d = (d[0] / length, d[1] / length)
            ray = LineString([p, (p[0] + d[0] * tol, p[1] + d[1] * tol)])
            best: tuple[float, Pt] | None = None
            for j in tree.query(ray):
                j = int(j)
                if j == i:
                    continue
                hit = ray.intersection(lines[j])
                if hit.is_empty:
                    continue
                geoms = [hit] if hit.geom_type == "Point" else list(getattr(hit, "geoms", []))
                for h in geoms:
                    if h.geom_type != "Point":
                        continue
                    dist = math.hypot(h.x - p[0], h.y - p[1])
                    if best is None or dist < best[0]:
                        best = (dist, (h.x, h.y))
            if best is not None:
                new[end] = best[1]
                n_ext += 1
        out.append((new[0], new[1]))
    return out, n_ext


def node_and_chain(segs: Sequence[Seg]) -> list[LineString]:
    """Tách mọi giao điểm (kể cả chữ T), gộp phần chồng/trùng, rồi ghép chuỗi qua nút bậc 2."""
    if not segs:
        return []
    # làm tròn lưới 1e-6 để hai đầu mút lệch sai số số học (~1e-15) được coi là cùng một nút
    noded = unary_union([set_precision(LineString(s), 1e-6) for s in segs])
    if noded.geom_type == "LineString":              # đầu vào chỉ một đoạn (hoặc các đoạn trùng nhau): không có gì để ghép
        return [noded] if noded.length > EPS else []
    merged = linemerge(noded)
    geoms = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]
    return [g for g in geoms if g.geom_type == "LineString" and g.length > EPS]


def total_length(segs: Sequence[Seg]) -> float:
    """Tổng chiều dài sau khi gộp phần chồng/trùng (độ dài của hợp), dùng kiểm bảo toàn."""
    if not segs:
        return 0.0
    return float(unary_union([LineString(s) for s in segs]).length)


def free_end_count(segs: Sequence[Seg], eps: float = 1e-6) -> int:
    """Số đầu mút không chạm đoạn nào khác (đầu rời)."""
    if not segs:
        return 0
    lines = [LineString(s) for s in segs]
    tree = STRtree(lines)
    n = 0
    for i, s in enumerate(segs):
        for p in s:
            if not _touches(p, tree, lines, i, max(eps * 10, 1e-9)):
                n += 1
    return n
