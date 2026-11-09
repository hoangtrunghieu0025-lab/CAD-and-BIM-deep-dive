"""Cầu nối thử (TASK-018, chưa phải M3): kết quả cad2bim v2 `analyze()` -> IfcWall + IfcDoor + IfcSpace.
Cửa: v2 chỉ cho điểm + bề rộng (swing_arc, không có tường chủ/hướng) -> ở đây gán tường gần nhất, lấy hướng của nó, đặt cửa
vào khoảng hở (chọn phía có đầu kia chạm tường). Phòng: v2 không sinh `space` cho bản vẽ không có layer phòng -> ở đây suy
ra: hợp các tường (đệm theo độ dày) + đoạn bịt khoảng hở cửa, lấy các lỗ kín làm phòng (derived, thô).
Dùng: .venv/bin/python -I research/06-cad-to-bim/poc/v2_walls_to_ifc.py <in.dxf> <out.ifc>
Lấy từ v2: đường tim, độ dày (derived từ cặp nét song song), chiều cao (assumed 3,0 m). Mỗi phần tử ghi nguồn/khẳng định
vào Pset_Cad2Bim_Provenance. Toạ độ được tịnh tiến về gốc cục bộ (bản vẽ thật thường ở xa gốc); độ dịch ghi vào
IfcProject.Description. Không ghi cửa, phòng, lỗ mở. Chưa xác minh hình học bằng mắt."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import math
import ifcopenshell, ifcopenshell.api as api
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from src.cad2bim.analyze import analyze

src, dst = sys.argv[1], sys.argv[2]
m = analyze(src)
walls = m.of("wall")
if not walls:
    sys.exit("không có tường nào")
ox = min(min(c[0] for c in w.geometry.coords) for w in walls)
oy = min(min(c[1] for c in w.geometry.coords) for w in walls)

f = api.run("project.create_file", version="IFC4")
proj = api.run("root.create_entity", f, ifc_class="IfcProject", name=os.path.basename(src))
proj.Description = f"cad2bim v2; đơn vị mét; đã tịnh tiến gốc: x0={ox:.3f}, y0={oy:.3f} (mét, trong toạ độ bản vẽ)"
api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METRE"})
ctx = api.run("context.add_context", f, context_type="Model")
body = api.run("context.add_context", f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)
site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Building")
st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name=m.storey or "Level 1")
api.run("aggregate.assign_object", f, products=[site], relating_object=proj)
api.run("aggregate.assign_object", f, products=[bld], relating_object=site)
api.run("aggregate.assign_object", f, products=[st], relating_object=bld)
n = 0; n_door = 0
for k, w in enumerate(walls):
    pts = [(x - ox, y - oy) for x, y in w.geometry.coords]
    for a, b in zip(pts, pts[1:]):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) < 1e-6:
            continue
        el = api.run("root.create_entity", f, ifc_class="IfcWall", name=f"Wall-{k}-{n}")
        api.run("geometry.edit_object_placement", f, product=el)
        rep = api.run("geometry.create_2pt_wall", f, element=el, context=body, p1=a, p2=b, elevation=0.0,
                      height=float(w.params.get("height", 3.0)), thickness=float(w.params.get("thickness", 0.2)))
        api.run("geometry.assign_representation", f, product=el, representation=rep)
        api.run("spatial.assign_container", f, products=[el], relating_structure=st)
        ps = api.run("pset.add_pset", f, product=el, name="Pset_Cad2Bim_Provenance")
        api.run("pset.edit_pset", f, pset=ps, properties={
            "SourceRefs": "; ".join(w.prov.source_refs)[:200], "Claims": str(w.prov.claims),
            "Confidence": w.prov.confidence, "ThicknessSource": str(w.params.get("source", ""))})
        n += 1

# ---- cửa
tw = [(w, LineString([(x - ox, y - oy) for x, y in w.geometry.coords])) for w in walls]
def seg_dir(ls):
    (x1, y1), (x2, y2) = ls.coords[0], ls.coords[-1]
    L = math.hypot(x2 - x1, y2 - y1) or 1.0
    return (x2 - x1) / L, (y2 - y1) / L
wall_geoms = [g for _, g in tw]
openings, plugs = [], []
for k, d in enumerate(m.of("door")):
    pt = Point(d.geometry.x - ox, d.geometry.y - oy)
    w, g = min(tw, key=lambda t: t[1].distance(pt))
    if g.distance(pt) > 0.6:
        continue
    u = seg_dir(g)
    q = g.interpolate(g.project(pt))
    wd = float(d.params.get("width", 0.9))
    cands = [((q.x + s_ * u[0] * wd, q.y + s_ * u[1] * wd)) for s_ in (1, -1)]
    end = min(cands, key=lambda c: min(x.distance(Point(c)) for x in wall_geoms if x is not g))
    a, b = (q.x, q.y), end
    th = float(w.params.get("thickness", 0.2))
    el = api.run("root.create_entity", f, ifc_class="IfcDoor", name=f"Door-{k}")
    el.OverallWidth, el.OverallHeight = wd, float(d.params.get("height", 2.1))
    api.run("geometry.edit_object_placement", f, product=el)
    rep = api.run("geometry.create_2pt_wall", f, element=el, context=body, p1=a, p2=b, elevation=0.0,
                  height=el.OverallHeight, thickness=th)
    api.run("geometry.assign_representation", f, product=el, representation=rep)
    api.run("spatial.assign_container", f, products=[el], relating_structure=st)
    ps = api.run("pset.add_pset", f, product=el, name="Pset_Cad2Bim_Provenance")
    api.run("pset.edit_pset", f, pset=ps, properties={"SourceRefs": "; ".join(d.prov.source_refs)[:200], "Claims": str(d.prov.claims),
            "Note": "vị trí/hướng suy ra từ tường gần nhất (cầu nối), không phải từ v2"})
    plugs.append(LineString([a, b]).buffer(th / 2, cap_style=2))
    n_door = k + 1

# ---- phòng: lỗ kín của (tường đệm + đoạn bịt cửa)
foot = unary_union([g.buffer(float(w.params.get("thickness", 0.2)) / 2, cap_style=3) for w, g in tw] + plugs)
CLOSE = 0.5   # m: đóng khe hở <= 1 m (tường v2 vỡ vụn; khe cửa + khe khác) -> nguy cơ gộp/bỏ sót phòng, chưa kiểm
foot = foot.buffer(CLOSE, cap_style=3, join_style=2).buffer(-CLOSE, join_style=2)
rooms, seen = [], set()
for poly in (foot.geoms if foot.geom_type == "MultiPolygon" else [foot]):
    for ring in poly.interiors:
        pg = type(poly)(ring)
        key = (round(pg.centroid.x, 1), round(pg.centroid.y, 1), round(pg.area, 1))
        if pg.area >= 1.5 and key not in seen:
            seen.add(key); rooms.append(pg)
n_room = 0
for i, r in enumerate(sorted(rooms, key=lambda p: (p.centroid.y, p.centroid.x))):
    if r.area > 200:
        continue
    r = r.simplify(0.01)
    sp = api.run("root.create_entity", f, ifc_class="IfcSpace", name=f"Room-{i + 1}")
    api.run("geometry.edit_object_placement", f, product=sp)
    rep = api.run("geometry.add_slab_representation", f, context=body, depth=2.7, polyline=list(r.exterior.coords))
    api.run("geometry.assign_representation", f, product=sp, representation=rep)
    api.run("aggregate.assign_object", f, products=[sp], relating_object=st)
    ps = api.run("pset.add_pset", f, product=sp, name="Pset_Cad2Bim_Provenance")
    api.run("pset.edit_pset", f, pset=ps, properties={"Claims": "{'boundary': 'derived', 'height': 'assumed'}",
            "NetAreaM2": round(r.area, 2), "Note": "phòng suy ra từ lỗ kín của tường + đoạn bịt cửa; chưa có tên/loại phòng"})
    n_room += 1
f.write(dst)
print(f"{len(walls)} tường v2 -> {n} IfcWall, {n_door} IfcDoor, {n_room} IfcSpace -> {dst}")
