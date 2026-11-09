"""POC (TASK-017): thử bước NỐI GÓC tường trên đường tim lấy từ DXF.

Dùng:  python -I wall_corner_join_trial.py <in.dxf> [thickness_m] [layer] [gap_m] [tol_m]
Chỉ in số liệu; không ghi file, không sửa src/.

Các bước (ý tưởng: FreeCAD offsetWire/connect, Cloud2BIM space_generator, roomgraph):
  0. Đường tim = LINE + cạnh LWPOLYLINE của layer A-WALL (giả định đơn vị mét, độ dày tham số).
  1. BASELINE (POC cũ): mỗi đoạn là một hộp riêng, đầu phẳng.
  2. extend_free_ends: đầu mút rời được kéo dài tới đường tim gần nhất trong dung sai (kiểu Cloud2BIM).
  3. Noding: unary_union các đoạn để tách tại mọi giao điểm (kể cả chữ T), linemerge ghép chuỗi qua nút bậc 2.
  4. buffer(mitre, cap phẳng) từng chuỗi rồi unary_union.
Giả định/giới hạn: chỉ đoạn thẳng; polyline có bulge bị coi là dây cung; chưa xử lý góc nhọn,
tường cong, tường nhiều độ dày. Dung sai là tham số, chưa hiệu chỉnh với bản vẽ thật."""
import math
import sys

import ezdxf
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, unary_union

EPS = 1e-6


def read_segments(path, layer="A-WALL"):
    segs = []
    for e in ezdxf.readfile(path).modelspace():
        if e.dxf.layer.upper() != layer.upper():
            continue
        if e.dxftype() == "LINE":
            segs.append(((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)))
        elif e.dxftype() == "LWPOLYLINE":
            pts = [(float(p[0]), float(p[1])) for p in e.get_points("xy")]
            if e.closed:
                pts.append(pts[0])
            segs += list(zip(pts, pts[1:]))
    return [(tuple(map(float, a)), tuple(map(float, b))) for a, b in segs]


def baseline_boxes(segs, thick):
    """POC cũ: mỗi đoạn một hộp, đầu phẳng, không nối."""
    return [LineString(s).buffer(thick / 2, cap_style="flat") for s in segs]


def _touches(pt, lines, skip, tol):
    """Điểm có chạm đường tim nào khác (kể cả phần giữa đoạn) trong dung sai tol không."""
    p = Point(pt)
    return any(i != skip and ln.distance(p) <= tol for i, ln in enumerate(lines))


def extend_free_ends(segs, tol):
    """Đầu mút không chạm đoạn nào khác: bắn tia theo hướng đoạn, kéo dài tới giao điểm
    gần nhất nếu cách <= tol. Trả về (danh sách mới, số đầu đã kéo dài)."""
    lines = [LineString(s) for s in segs]
    out, n_ext = [], 0
    for i, (a, b) in enumerate(segs):
        new = [a, b]
        for end in (0, 1):
            p = new[end]
            if _touches(p, lines, i, EPS * 10):
                continue
            q = new[1 - end]
            d = (p[0] - q[0], p[1] - q[1])
            L = math.hypot(*d)
            if L < EPS:
                continue
            d = (d[0] / L, d[1] / L)
            ray = LineString([p, (p[0] + d[0] * tol, p[1] + d[1] * tol)])
            best = None
            for j, ln in enumerate(lines):
                if j == i:
                    continue
                hit = ray.intersection(ln)
                if hit.is_empty:
                    continue
                pts = [hit] if hit.geom_type == "Point" else list(getattr(hit, "geoms", []))
                for h in pts:
                    if h.geom_type != "Point":
                        continue
                    dist = math.hypot(h.x - p[0], h.y - p[1])
                    if best is None or dist < best[0]:
                        best = (dist, (h.x, h.y))
            if best:
                new[end] = best[1]
                n_ext += 1
        out.append((new[0], new[1]))
    return out, n_ext


def join_walls(segs, thick):
    """Noding + ghép chuỗi + buffer mitre. Trả về (hình hợp nhất, danh sách chuỗi tim)."""
    noded = unary_union([LineString(s) for s in segs])
    merged = linemerge(noded)
    chains = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]
    walls = [c.buffer(thick / 2, cap_style="flat", join_style="mitre", mitre_limit=5.0) for c in chains]
    return unary_union(walls), chains


def report(tag, geom, n_parts):
    comps = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    holes = sum(len(c.interiors) for c in comps)
    print(f"  {tag:<34} phần tử={n_parts:>3}  diện tích={geom.area:8.4f} m²  thành phần={len(comps)}  lỗ(phòng)={holes}  valid={geom.is_valid}")
    return geom.area


def main():
    path = sys.argv[1]
    thick = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
    layer = sys.argv[3] if len(sys.argv) > 3 else "A-WALL"
    gap = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15
    tol = float(sys.argv[5]) if len(sys.argv) > 5 else 0.3
    segs = read_segments(path, layer)
    print(f"{path}: {len(segs)} đoạn tim, độ dày {thick} m")

    print("\n[A] Mẫu gốc (sạch)")
    boxes = baseline_boxes(segs, thick)
    u_base = unary_union(boxes)
    a_sum = sum(b.area for b in boxes)
    report("BASELINE (hộp riêng, hợp nhất)", u_base, len(boxes))
    print(f"  (cộng diện tích từng hộp = {a_sum:.4f}; trùng nhau = {a_sum - u_base.area:.4f})")
    joined, chains = join_walls(segs, thick)
    report("NỐI GÓC (noding+mitre)", joined, len(chains))
    print(f"  khác biệt hợp nhất: +{joined.area - u_base.area:.4f} m² (kỳ vọng 4 góc ngoài × {(thick/2)**2:.4f} = {4*(thick/2)**2:.4f}); "
          f"chiều dài tim = {sum(c.length for c in chains):.3f} m")
    print(f"  chuỗi tim: {[round(c.length, 2) for c in chains]}")

    print(f"\n[B] Ca lỗi cố ý: rút ngắn {gap} m đầu mút vách ngăn (nửa độ dày = {thick/2} m), dung sai kéo dài = {tol} m")
    def pull_back(p, q, d=None):
        d = gap if d is None else d
        """Rút điểm p về phía q một đoạn d."""
        L = math.hypot(p[0] - q[0], p[1] - q[1])
        return (p[0] + (q[0] - p[0]) / L * d, p[1] + (q[1] - p[1]) / L * d)

    broken = []
    for (a, b) in segs:
        vertical = abs(a[0] - b[0]) < EPS
        if vertical and a[0] not in (0.0, 24.0) and abs(a[1] - b[1]) > 3.0:  # vách ngăn dọc
            # chỉ rút đầu nằm trên tim tường hành lang (y=5 hoặc y=7)
            if a[1] in (5.0, 7.0):
                a = pull_back(a, b)
            elif b[1] in (5.0, 7.0):
                b = pull_back(b, a)
        broken.append((a, b))
    n_changed = sum(1 for s, t in zip(segs, broken) if s != t)
    print(f"  đã làm hở {n_changed} vách ngăn")
    jb, cb = join_walls(broken, thick)
    report(f"KHÔNG kéo dài (hở {gap} m)", jb, len(cb))
    ext, n = extend_free_ends(broken, tol=tol)
    je, ce = join_walls(ext, thick)
    report(f"CÓ kéo dài đầu rời (tol {tol}; {n} đầu)", je, len(ce))
    print(f"  so với mẫu gốc đã nối: |Δ diện tích| = {abs(je.area - joined.area):.6f} m²;  "
          f"symmetric_difference = {je.symmetric_difference(joined).area:.6f} m²")
    print(f"  không kéo dài: symmetric_difference với mẫu gốc = {jb.symmetric_difference(joined).area:.6f} m²")


if __name__ == "__main__":
    main()
