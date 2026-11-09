"""THỬ NGHIỆM (TASK-018, ngoài pipeline v2): DXF 3D -> IFC giữ cả LƯỚI MẶT và KHUNG DÂY.
 - polyface -> IfcBuildingElementProxy '<layer>' (lưới mặt gộp theo layer, như mesh3d_to_ifc.py)
 - LINE, ARC, CIRCLE, ELLIPSE, SPLINE, polyline 3D -> IfcBuildingElementProxy '<layer> (wire)', biểu diễn 'Curve3D' gồm các IfcPolyline
   (cung/tròn/ê-líp được làm phẳng thành đoạn thẳng, sai số `delta`, nên KHÔNG còn là cung chính xác)
 - INSERT mở đệ quy tối đa 8 tầng (có chặn vòng). Không phân loại ngữ nghĩa.
Dùng: .venv/bin/python -I mesh3d_full_to_ifc.py <in.dxf> <out.ifc> [delta=0.05]"""
import sys, os, math, collections
import ezdxf, ifcopenshell, ifcopenshell.api as api
from ezdxf import path as ezpath
from ezdxf.render import MeshBuilder

src, dst = sys.argv[1], sys.argv[2]
delta = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
MAXD = 8
doc = ezdxf.readfile(src)
meshes = collections.defaultdict(lambda: ([], []))
curves = collections.defaultdict(list)           # layer -> [list[(x,y,z)]]
stat = collections.Counter(); lost = collections.Counter()

def walk(ents, pl, depth):
    for e in ents:
        layer = e.dxf.layer if not (e.dxf.layer == "0" and pl) else pl
        t = e.dxftype()
        if t == "POLYLINE" and e.is_poly_face_mesh:
            mb = MeshBuilder.from_polyface(e); v, f = meshes[layer]; b = len(v)
            v.extend((float(p.x), float(p.y), float(p.z)) for p in mb.vertices)
            f.extend([tuple(b + i for i in fc) for fc in mb.faces if len(fc) >= 3]); stat["polyface"] += 1
        elif t == "INSERT":
            if depth < MAXD:
                try: walk(list(e.virtual_entities()), layer, depth + 1)
                except Exception: lost["INSERT lỗi mở"] += 1
            else: lost["INSERT quá sâu"] += 1
        elif t == "LINE":
            curves[layer].append([tuple(e.dxf.start), tuple(e.dxf.end)]); stat["LINE"] += 1
        elif t == "POLYLINE" and (e.is_3d_polyline or e.is_2d_polyline):
            pts = [tuple(p) for p in e.points()]
            if e.is_closed and pts: pts.append(pts[0])
            if len(pts) >= 2: curves[layer].append(pts); stat["POLYLINE3D"] += 1
        elif t in ("ARC", "CIRCLE", "ELLIPSE", "SPLINE", "LWPOLYLINE"):
            try:
                pts = [tuple(v) for v in ezpath.make_path(e).flattening(delta)]
                if len(pts) >= 2: curves[layer].append(pts); stat[t] += 1
            except Exception: lost[t + " lỗi"] += 1
        else:
            lost[t] += 1

walk(doc.modelspace(), None, 0)
f = api.run("project.create_file", version="IFC4")
proj = api.run("root.create_entity", f, ifc_class="IfcProject", name=os.path.basename(src))
proj.Description = f"THỬ NGHIỆM; đơn vị GIẢ ĐỊNH mét ($INSUNITS={doc.header.get('$INSUNITS')} trong file); lưới mặt + khung dây (cung làm phẳng, sai số {delta}); chưa phân loại"
api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METRE"})
ctx = api.run("context.add_context", f, context_type="Model")
body = api.run("context.add_context", f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)
site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Building")
st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="All")
api.run("aggregate.assign_object", f, products=[site], relating_object=proj)
api.run("aggregate.assign_object", f, products=[bld], relating_object=site)
api.run("aggregate.assign_object", f, products=[st], relating_object=bld)
n_mesh = n_curve = n_pts = 0
for layer, (v, fc) in meshes.items():
    if not fc: continue
    el = api.run("root.create_entity", f, ifc_class="IfcBuildingElementProxy", name=layer)
    api.run("geometry.edit_object_placement", f, product=el)
    api.run("geometry.assign_representation", f, product=el, representation=api.run("geometry.add_mesh_representation", f, context=body, vertices=[v], faces=[fc]))
    api.run("spatial.assign_container", f, products=[el], relating_structure=st); n_mesh += len(fc)
for layer, cs in curves.items():
    el = api.run("root.create_entity", f, ifc_class="IfcBuildingElementProxy", name=f"{layer} (wire)")
    api.run("geometry.edit_object_placement", f, product=el)
    items = []
    for pts in cs:
        items.append(f.createIfcPolyline([f.createIfcCartesianPoint([float(c) for c in p]) for p in pts])); n_pts += len(pts)
    rep = f.createIfcShapeRepresentation(body, "Body", "Curve3D", items)
    api.run("geometry.assign_representation", f, product=el, representation=rep)
    api.run("spatial.assign_container", f, products=[el], relating_structure=st); n_curve += len(cs)
f.write(dst)
print("đã giữ:", dict(stat), "| mặt:", n_mesh, "| đường (IfcPolyline):", n_curve, "| điểm:", n_pts)
print("bỏ qua:", dict(lost), "->", dst)
