"""THỬ NGHIỆM (TASK-018, ngoài pipeline v2): DXF 3D dạng lưới mặt (POLYLINE polyface) -> IFC, mỗi layer một
IfcBuildingElementProxy mang lưới mặt gộp. Mở khối INSERT (đệ quy <= 3 tầng) bằng virtual_entities().
Dùng: .venv/bin/python -I research/06-cad-to-bim/poc/mesh3d_to_ifc.py <in.dxf> <out.ifc> [đơn_vị_giả_định=m]
KHÔNG phân loại ngữ nghĩa (không biết tường/dầm/mái): lớp IFC luôn là IfcBuildingElementProxy, tên = tên layer.
Bỏ qua LINE/ARC/CIRCLE (khung dây), 3D polyline, MESH/3DFACE/3DSOLID (kho này chỉ gặp polyface)."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import numpy as np, ezdxf, ifcopenshell, ifcopenshell.api as api
from ezdxf.render import MeshBuilder

src, dst = sys.argv[1], sys.argv[2]
unit = sys.argv[3] if len(sys.argv) > 3 else "m"
doc = ezdxf.readfile(src)
meshes = collections.defaultdict(lambda: ([], []))        # layer -> (đỉnh, mặt)
n_poly = n_skip = 0

def add(e, layer):
    global n_poly
    mb = MeshBuilder.from_polyface(e)
    v, f = meshes[layer]
    base = len(v)
    v.extend((float(p.x), float(p.y), float(p.z)) for p in mb.vertices)
    f.extend([tuple(base + int(i) for i in face) for face in mb.faces if len(face) >= 3])
    n_poly += 1

def walk(ents, parent_layer, depth):
    global n_skip
    for e in ents:
        t = e.dxftype()
        layer = e.dxf.layer
        if layer == "0" and parent_layer:
            layer = parent_layer
        if t == "POLYLINE" and e.is_poly_face_mesh:
            add(e, layer)
        elif t == "INSERT":
            if depth < 3:
                try:
                    walk(list(e.virtual_entities()), layer, depth + 1)
                except Exception:
                    n_skip += 1
        else:
            n_skip += 1

walk(doc.modelspace(), None, 0)
f = api.run("project.create_file", version="IFC4")
proj = api.run("root.create_entity", f, ifc_class="IfcProject", name=os.path.basename(src))
proj.Description = f"THỬ NGHIỆM; đơn vị GIẢ ĐỊNH '{unit}' ($INSUNITS={doc.header.get('$INSUNITS')} trong file); chỉ lưới polyface, chưa phân loại"
api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METRE"})
ctx = api.run("context.add_context", f, context_type="Model")
body = api.run("context.add_context", f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)
site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Building")
st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="All")
api.run("aggregate.assign_object", f, products=[site], relating_object=proj)
api.run("aggregate.assign_object", f, products=[bld], relating_object=site)
api.run("aggregate.assign_object", f, products=[st], relating_object=bld)
tv = tf = 0
for layer, (v, fc) in meshes.items():
    if not fc:
        continue
    el = api.run("root.create_entity", f, ifc_class="IfcBuildingElementProxy", name=layer)
    api.run("geometry.edit_object_placement", f, product=el)
    rep = api.run("geometry.add_mesh_representation", f, context=body, vertices=[v], faces=[fc])
    api.run("geometry.assign_representation", f, product=el, representation=rep)
    api.run("spatial.assign_container", f, products=[el], relating_structure=st)
    tv += len(v); tf += len(fc)
f.write(dst)
print({l: (len(v), len(fc)) for l, (v, fc) in meshes.items()})
print(f"polyface đã dùng {n_poly}, thực thể bỏ qua {n_skip}, tổng đỉnh {tv}, tổng mặt {tf} -> {dst}")
