"""POC (TASK-017): layer A-WALL của DXF -> IfcWall bằng ezdxf + ifcopenshell.
Dùng: python -I dxf_walls_to_ifc.py <in.dxf> <out.ifc> [height_m] [thickness_m]
Giả định (chưa xác minh với bản vẽ thật): đơn vị DXF là mét; cao độ/độ dày là tham số nhập tay."""
import sys, ezdxf, ifcopenshell, ifcopenshell.api as api

src, dst = sys.argv[1], sys.argv[2]
height = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
thick = float(sys.argv[4]) if len(sys.argv) > 4 else 0.2

segs = []
for e in ezdxf.readfile(src).modelspace():
    if e.dxf.layer.upper() != "A-WALL":
        continue
    if e.dxftype() == "LINE":
        segs.append(((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)))
    elif e.dxftype() == "LWPOLYLINE":
        pts = [(p[0], p[1]) for p in e.get_points("xy")]
        if e.closed:
            pts.append(pts[0])
        segs += list(zip(pts, pts[1:]))

f = api.run("project.create_file", version="IFC4")
proj = api.run("root.create_entity", f, ifc_class="IfcProject", name="POC")
api.run("unit.assign_unit", f)
ctx = api.run("context.add_context", f, context_type="Model")
body = api.run("context.add_context", f, context_type="Model", context_identifier="Body",
               target_view="MODEL_VIEW", parent=ctx)
site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Building")
st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="Level 1")
api.run("aggregate.assign_object", f, products=[site], relating_object=proj)
api.run("aggregate.assign_object", f, products=[bld], relating_object=site)
api.run("aggregate.assign_object", f, products=[st], relating_object=bld)
for i, (p1, p2) in enumerate(segs):
    w = api.run("root.create_entity", f, ifc_class="IfcWall", name=f"Wall-{i}")
    api.run("geometry.edit_object_placement", f, product=w)
    rep = api.run("geometry.create_2pt_wall", f, element=w, context=body, p1=p1, p2=p2,
                  elevation=0.0, height=height, thickness=thick)
    api.run("geometry.assign_representation", f, product=w, representation=rep)
    api.run("spatial.assign_container", f, products=[w], relating_structure=st)
f.write(dst)
print(f"{len(segs)} wall segments -> {dst}")
