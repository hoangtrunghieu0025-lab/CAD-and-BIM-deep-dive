"""THỬ NGHIỆM (TASK-018, ngoài pipeline v2): tường vẽ bằng nét TÔ ĐẶC (SOLID) -> IfcWall.
Bản vẽ vector hoá từ PDF (layer 'PDF_Solid Fills') vẽ tường là các SOLID đen, đường trục là các SOLID rất mảnh.
Cách làm: hợp các SOLID trong từng khung mặt bằng, bỏ mảnh mỏng (rộng < 2*min_half), mỗi mảnh còn lại -> IfcWall đùn 3,0 m.
Dùng: .venv/bin/python -I research/06-cad-to-bim/poc/solid_fill_walls_to_ifc.py <in.dxf> <out.ifc> <layer> "x0,x1,y0,y1;x0,x1,y0,y1;..." [min_half=0.04]
Mỗi khung = một tầng (Plan-1, Plan-2…), cao độ 0, 3, 6…; xy tịnh tiến sao cho góc dưới-trái của tường mỗi khung về (0,0) (GIẢ ĐỊNH: các tầng cùng vị trí góc đó).
CHƯA kiểm với đáp án. Không có cửa, phòng, lỗ mở; ô cửa chỉ là chỗ hở trong tường."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np, ezdxf, ifcopenshell, ifcopenshell.api as api
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

src, dst, layer, regions = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
half = float(sys.argv[5]) if len(sys.argv) > 5 else 0.04
boxes = [tuple(float(v) for v in r.split(",")) for r in regions.split(";")]
doc = ezdxf.readfile(src)
assert doc.header.get("$INSUNITS") == 6, "chỉ nhận $INSUNITS=6 (mét)"
polys = []
for e in doc.modelspace():
    if e.dxftype() == "SOLID" and e.dxf.layer == layer:
        v = [e.dxf.vtx0, e.dxf.vtx1, e.dxf.vtx3, e.dxf.vtx2]          # thứ tự DXF của SOLID là 0,1,3,2
        p = Polygon([(q.x, q.y) for q in v])
        p = p if p.is_valid else p.buffer(0)
        if not p.is_empty and p.area > 0:
            polys.append(p)
f = api.run("project.create_file", version="IFC4")
proj = api.run("root.create_entity", f, ifc_class="IfcProject", name=os.path.basename(src))
api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METRE"})
ctx = api.run("context.add_context", f, context_type="Model")
body = api.run("context.add_context", f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)
site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Building")
api.run("aggregate.assign_object", f, products=[site], relating_object=proj)
api.run("aggregate.assign_object", f, products=[bld], relating_object=site)
ref = boxes[0]
summary = []
dump = []
for k, (x0, x1, y0, y1) in enumerate(boxes):
    region = box(x0, y0, x1, y1)
    u = unary_union([p for p in polys if p.intersects(region) and region.contains(p.representative_point())])
    parts = list(u.geoms) if u.geom_type == "MultiPolygon" else [u]
    def marker(p):          # ô vuông đặc ~0,5 x 0,5 m đứng lẻ (dấu tỷ lệ/định vị của tờ vẽ), không phải tường
        bx = p.bounds; w, h = bx[2] - bx[0], bx[3] - bx[1]
        return 0.4 <= w <= 0.6 and 0.4 <= h <= 0.6 and p.area / (w * h) > 0.9
    keep = [p for p in parts if p.area >= 0.05 and not p.buffer(-half).is_empty and not marker(p)]
    ox, oy = (min(p.bounds[0] for p in keep), min(p.bounds[1] for p in keep)) if keep else (x0, y0)   # gốc = góc dưới-trái của các tường
    st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name=f"Plan-{k + 1}")
    st.Elevation = 3.0 * k
    api.run("aggregate.assign_object", f, products=[st], relating_object=bld)
    for i, p in enumerate(keep):
        p = p.simplify(0.005)
        pts = [(x - ox, y - oy) for x, y in p.exterior.coords]
        el = api.run("root.create_entity", f, ifc_class="IfcWall", name=f"Plan-{k + 1}-W{i}")
        m = np.eye(4); m[2, 3] = 3.0 * k
        api.run("geometry.edit_object_placement", f, product=el, matrix=m)
        rep = api.run("geometry.add_slab_representation", f, context=body, depth=3.0, polyline=pts)
        api.run("geometry.assign_representation", f, product=el, representation=rep)
        api.run("spatial.assign_container", f, products=[el], relating_structure=st)
    dump.append([list(p.exterior.coords) for p in keep])
    summary.append((len(parts), len(keep), round(sum(p.area for p in keep), 2)))
f.write(dst)
if len(sys.argv) > 6:
    import json; json.dump(dump, open(sys.argv[6], "w"))
print("mỗi khung (mảnh sau hợp, giữ lại làm tường, tổng diện tích m2):", summary, "->", dst)
