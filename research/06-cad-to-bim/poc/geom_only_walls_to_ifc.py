"""THỬ NGHIỆM (TASK-018, ngoài pipeline v2): DXF mà layer không có nghĩa (vd DWG vector hoá từ PDF: layer PDF_Geometry) ->
IfcWall bằng cách ghép cặp nét song song CHỈ theo hình học, bỏ qua tên layer. Dùng lại segments.snap_endpoints/explode và
walls.pair_walls của v2. Mỗi layer hình học -> một IfcBuildingStorey (cao độ 0, chưa biết tầng nào là tầng nào).
Dùng: .venv/bin/python -I research/06-cad-to-bim/poc/geom_only_walls_to_ifc.py <in.dxf> <out.ifc> <layer1,layer2> [dày_min=0.08] [dày_max=0.40]
CHƯA kiểm: không có đáp án; nét đồ đạc/chữ vector hoá có thể bị ghép thành tường giả. Không có cửa, phòng, lỗ mở."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import ezdxf, ifcopenshell, ifcopenshell.api as api
from src.cad2bim import segments as sg, walls as wl

src, dst, layers = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
tmin = float(sys.argv[4]) if len(sys.argv) > 4 else 0.08
tmax = float(sys.argv[5]) if len(sys.argv) > 5 else 0.40
doc = ezdxf.readfile(src)
assert doc.header.get("$INSUNITS") == 6, "script này chỉ nhận $INSUNITS=6 (mét)"
paths = {l: [] for l in layers}
for e in doc.modelspace():
    if e.dxf.layer in paths and e.dxftype() in ("LWPOLYLINE", "LINE"):
        if e.dxftype() == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        else:
            pts = [(x, y) for x, y in e.get_points("xy")]
            if e.closed:
                pts.append(pts[0])
        paths[e.dxf.layer].append(pts)
res = {}
for l, ps in paths.items():
    segs = sg.snap_endpoints(sg.explode(ps, 1e-3), 0.01)
    pieces, _ = wl.pair_walls(segs, tmin, tmax, 0.5, 1.0, 0.01)
    res[l] = pieces
allp = [p for v in res.values() for p in v]
if not allp:
    sys.exit("không ghép được tường nào")
ox = min(min(c[0] for c in p.axis.coords) for p in allp)
oy = min(min(c[1] for c in p.axis.coords) for p in allp)
f = api.run("project.create_file", version="IFC4")
proj = api.run("root.create_entity", f, ifc_class="IfcProject", name=os.path.basename(src))
proj.Description = f"THỬ NGHIỆM ghép cặp theo hình học; đơn vị mét; đã tịnh tiến gốc x0={ox:.3f}, y0={oy:.3f}"
api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METRE"})
ctx = api.run("context.add_context", f, context_type="Model")
body = api.run("context.add_context", f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)
site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Building")
api.run("aggregate.assign_object", f, products=[site], relating_object=proj)
api.run("aggregate.assign_object", f, products=[bld], relating_object=site)
for l, pieces in res.items():
    st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name=l)
    api.run("aggregate.assign_object", f, products=[st], relating_object=bld)
    for i, p in enumerate(pieces):
        (x1, y1), (x2, y2) = p.axis.coords[0], p.axis.coords[-1]
        el = api.run("root.create_entity", f, ifc_class="IfcWall", name=f"{l}-W{i}")
        api.run("geometry.edit_object_placement", f, product=el)
        rep = api.run("geometry.create_2pt_wall", f, element=el, context=body, p1=(x1 - ox, y1 - oy), p2=(x2 - ox, y2 - oy),
                      elevation=0.0, height=3.0, thickness=p.thickness)
        api.run("geometry.assign_representation", f, product=el, representation=rep)
        api.run("spatial.assign_container", f, products=[el], relating_structure=st)
f.write(dst)
print({l: len(v) for l, v in res.items()}, "->", dst)
