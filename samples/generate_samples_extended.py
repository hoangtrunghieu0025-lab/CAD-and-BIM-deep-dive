"""Sinh mẫu bổ sung cho TASK-015 (tự dựng, không dùng dữ liệu bên thứ ba).

Chạy:  .venv/bin/python samples/generate_samples_extended.py

Mặt bằng 1 tầng, 24 x 12 m, TƯỜNG DÀY 0,2 m đặt trên các trục lưới (nên giữa các phòng có khe 0,2 m):
  - 6 phòng phía nam P101-P106 (4 x 5 m), hành lang 2 m, 4 phòng phía bắc P107-P110, ô cầu thang (x 16-20) và ô thang máy (x 20-24).
  - Mỗi cột trục lưới x = 4, 8, ..., 20 có vách ngăn; hai tường dọc hành lang ở y = 5 và y = 7; tường ngoài ở chu vi.
  - 1 cột 0,4 x 0,4 m giữa hành lang, 2 cửa sổ, 3 món nội thất.
Các đối tượng: tường/cột/cầu thang/thang máy/nội thất có hình học; cửa có Pset_DoorCommon, OperationType; một cửa
lấp IfcOpeningElement (nguồn tâm 1), một cửa có thân (nguồn tâm 2), một cửa chỉ có placement (nguồn tâm 3).
"""
from pathlib import Path

import ezdxf
import ifcopenshell
import ifcopenshell.api
import numpy as np

OUT = Path(__file__).resolve().parent
T = 0.2
H = T / 2
HEIGHT = 3.0
XS = [0, 4, 8, 12, 16, 20, 24]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


def plan():
    """Hình học dùng chung cho IFC và DXF (mét)."""
    rooms = {}
    for i in range(6):
        rooms[f"P{101 + i}"] = (XS[i] + H, H, XS[i + 1] - H, 5 - H)
    for i in range(4):
        rooms[f"P{107 + i}"] = (XS[i] + H, 7 + H, XS[i + 1] - H, 12 - H)
    corridor = (H, 5 + H, 24 - H, 7 - H)
    stair = (XS[4] + H, 7 + H, XS[5] - H, 12 - H)
    elevator = (XS[5] + H, 7 + H, XS[6] - H, 12 - H)
    walls = [rect(-H, -H, 24 + H, H), rect(-H, 12 - H, 24 + H, 12 + H),
             rect(-H, -H, H, 12 + H), rect(24 - H, -H, 24 + H, 12 + H),
             rect(H, 5 - H, 24 - H, 5 + H), rect(H, 7 - H, 24 - H, 7 + H)]
    for x in XS[1:-1]:
        walls.append(rect(x - H, H, x + H, 5 - H))
        walls.append(rect(x - H, 7 + H, x + H, 12 - H))
    column = (12 - 0.2, 6 - 0.2, 12 + 0.2, 6 + 0.2)
    # cửa: (mã phòng, tâm x, tâm y)
    doors = [(f"P{101 + i}", XS[i] + 2, 5.0) for i in range(6)] + [(f"P{107 + i}", XS[i] + 2, 7.0) for i in range(4)]
    windows = [(6.0, 0.0), (18.0, 12.0)]
    furniture = [("P101", (1.0, 1.0, 2.0, 1.6)), ("P102", (5.0, 1.0, 6.2, 1.6)), ("P107", (1.0, 10.0, 2.4, 11.0))]
    return rooms, corridor, stair, elevator, walls, column, doors, windows, furniture


# --------------------------------------------------------------------- IFC4 mở rộng
def make_ifc_extended(name="sample-building-extended.ifc"):
    rooms, corridor, stair, elevator, walls, column, doors, windows, furniture = plan()
    f = ifcopenshell.api.run("project.create_file", version="IFC4")
    api = ifcopenshell.api
    project = api.run("root.create_entity", f, ifc_class="IfcProject", name="Extended Sample")
    api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METERS"})
    ctx = api.run("context.add_context", f, context_type="Model")
    body = api.run("context.add_context", f, context_type="Model", context_identifier="Body",
                   target_view="MODEL_VIEW", parent=ctx)
    site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
    bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Extended Building")
    st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="Tầng 1")
    st.Elevation = 0.0
    api.run("aggregate.assign_object", f, products=[site], relating_object=project)
    api.run("aggregate.assign_object", f, products=[bld], relating_object=site)
    api.run("aggregate.assign_object", f, products=[st], relating_object=bld)

    def place(prod, x=0.0, y=0.0, z=0.0):
        m = np.eye(4)
        m[:3, 3] = [x, y, z]
        api.run("geometry.edit_object_placement", f, product=prod, matrix=m)

    def solid(el, polyline, depth=HEIGHT):
        rep = api.run("geometry.add_slab_representation", f, context=body, depth=depth, polyline=polyline)
        api.run("geometry.assign_representation", f, product=el, representation=rep)
        place(el)

    def contain(*els):
        api.run("spatial.assign_container", f, products=list(els), relating_structure=st)

    # phòng (IfcSpace, gắn tầng bằng aggregate)
    def space(nm, long_name, box):
        sp = api.run("root.create_entity", f, ifc_class="IfcSpace", name=nm)
        sp.LongName = long_name
        x0, y0, x1, y1 = box
        solid(sp, rect(0, 0, x1 - x0, y1 - y0))
        place(sp, x0, y0)
        api.run("aggregate.assign_object", f, products=[sp], relating_object=st)

    for nm, box in rooms.items():
        space(nm, f"Phong {nm}", box)
    space("HL100", "Hanh lang", corridor)

    for k, poly in enumerate(walls):
        w = api.run("root.create_entity", f, ifc_class="IfcWall", name=f"Tuong {k + 1}")
        solid(w, poly)
        contain(w)
    s = api.run("root.create_entity", f, ifc_class="IfcStair", name="Cau thang 1")
    solid(s, rect(0, 0, stair[2] - stair[0], stair[3] - stair[1])); place(s, stair[0], stair[1]); contain(s)
    e = api.run("root.create_entity", f, ifc_class="IfcTransportElement", name="Thang may 1", predefined_type="ELEVATOR")
    solid(e, rect(0, 0, elevator[2] - elevator[0], elevator[3] - elevator[1])); place(e, elevator[0], elevator[1]); contain(e)
    c = api.run("root.create_entity", f, ifc_class="IfcColumn", name="Cot 1")
    solid(c, rect(0, 0, column[2] - column[0], column[3] - column[1])); place(c, column[0], column[1]); contain(c)
    for k, (_, box) in enumerate(furniture):
        fu = api.run("root.create_entity", f, ifc_class="IfcFurniture", name=f"Noi that {k + 1}")
        solid(fu, rect(0, 0, box[2] - box[0], box[3] - box[1]), depth=0.8); place(fu, box[0], box[1]); contain(fu)
    for k, (wx, wy) in enumerate(windows):
        wd = api.run("root.create_entity", f, ifc_class="IfcWindow", name=f"Cua so {k + 1}")
        wd.OverallWidth, wd.OverallHeight = 1.2, 1.2
        place(wd, wx - 0.6, wy - H, 1.0); contain(wd)

    # cửa
    op_types = {"P101": "SINGLE_SWING_LEFT", "P102": "SINGLE_SWING_LEFT", "P103": "SLIDING_TO_LEFT",
                "P104": "REVOLVING", "P105": "SINGLE_SWING_RIGHT", "P106": "SINGLE_SWING_LEFT"}
    for room, cx, cy in doors:
        d = api.run("root.create_entity", f, ifc_class="IfcDoor", name=f"Cua {room}")
        d.OverallWidth, d.OverallHeight = 0.9, 2.1
        d.OperationType = op_types.get(room, "SINGLE_SWING_LEFT")
        contain(d)
        if room == "P105":                       # nguồn tâm 1: IfcOpeningElement mà cửa lấp (cửa không có thân)
            op = api.run("root.create_entity", f, ifc_class="IfcOpeningElement", name=f"Lo {room}")
            solid(op, rect(cx - 0.45, cy - H, cx + 0.45, cy + H), depth=2.1)
            api.run("feature.add_feature", f, feature=op, element=[w for w in f.by_type("IfcWall")][4])
            api.run("feature.add_filling", f, opening=op, element=d)
            place(d, cx - 0.45, cy - 0.3)        # placement cố ý lệch: nguồn tâm phải là opening, không phải placement
        elif room == "P110":                     # nguồn tâm 3: chỉ có placement (đầu cửa)
            place(d, cx - 0.45, cy)
        else:                                    # nguồn tâm 2: thân cửa (bbox)
            solid(d, rect(0, 0, 0.9, T), depth=2.1)
            place(d, cx - 0.45, cy - H)
        if room == "P101":
            ps = api.run("pset.add_pset", f, product=d, name="Pset_DoorCommon")
            api.run("pset.edit_pset", f, pset=ps, properties={"IsExternal": True})
        if room == "P102":
            ps = api.run("pset.add_pset", f, product=d, name="Pset_DoorCommon")
            api.run("pset.edit_pset", f, pset=ps, properties={"FireExit": True})
        if room in ("P103", "P104"):
            ps = api.run("pset.add_pset", f, product=d, name="Pset_DoorCommon")
            api.run("pset.edit_pset", f, pset=ps, properties={"HasDrive": True})
        if room == "P106":
            ps = api.run("pset.add_pset", f, product=d, name="Pset_DoorCommon")
            api.run("pset.edit_pset", f, pset=ps, properties={"HasDrive": False})
    f.write(str(OUT / name))


# --------------------------------------------------------------------- IFC2X3 tối thiểu
def make_ifc2x3(name="sample-building-ifc2x3.ifc"):
    f = ifcopenshell.api.run("project.create_file", version="IFC2X3")
    api = ifcopenshell.api
    # IFC2X3 bắt buộc có OwnerHistory: khai báo người dùng/ứng dụng cho ifcopenshell.api
    import ifcopenshell.api.owner.settings as owner_settings

    org = f.createIfcOrganization(Name="Sample")
    user = f.createIfcPersonAndOrganization(f.createIfcPerson(FamilyName="Sample"), org)
    application = f.createIfcApplication(org, "1.0", "generate_samples_extended", "GSE")
    owner_settings.get_user = lambda ifc: user
    owner_settings.get_application = lambda ifc: application
    project = api.run("root.create_entity", f, ifc_class="IfcProject", name="IFC2X3 Sample")
    api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METERS"})
    ctx = api.run("context.add_context", f, context_type="Model")
    body = api.run("context.add_context", f, context_type="Model", context_identifier="Body",
                   target_view="MODEL_VIEW", parent=ctx)
    site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
    bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="IFC2X3 Building")
    st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="Tầng 1")
    st.Elevation = 0.0
    api.run("aggregate.assign_object", f, products=[site], relating_object=project)
    api.run("aggregate.assign_object", f, products=[bld], relating_object=site)
    api.run("aggregate.assign_object", f, products=[st], relating_object=bld)

    def place(prod, x=0.0, y=0.0):
        m = np.eye(4)
        m[:3, 3] = [x, y, 0.0]
        api.run("geometry.edit_object_placement", f, product=prod, matrix=m)

    cells = {"P101": (0, 0, 4, 5), "P102": (4, 0, 8, 5), "HL100": (0, 5, 8, 7)}
    for nm, (x0, y0, x1, y1) in cells.items():
        sp = api.run("root.create_entity", f, ifc_class="IfcSpace", name=nm)
        sp.LongName = "Hanh lang" if nm == "HL100" else f"Phong {nm}"
        rep = api.run("geometry.add_slab_representation", f, context=body, depth=3.0, polyline=rect(0, 0, x1 - x0, y1 - y0))
        api.run("geometry.assign_representation", f, product=sp, representation=rep)
        place(sp, x0, y0)
        api.run("aggregate.assign_object", f, products=[sp], relating_object=st)
    for nm, cx in (("P101", 2.0), ("P102", 6.0)):
        d = api.run("root.create_entity", f, ifc_class="IfcDoor", name=f"Cua {nm}")
        d.OverallWidth, d.OverallHeight = 0.9, 2.1
        place(d, cx - 0.45, 5.0)
        api.run("spatial.assign_container", f, products=[d], relating_structure=st)
    f.write(str(OUT / name))


# --------------------------------------------------------------------- DXF mở rộng
def make_dxf_extended(name="sample-floor-extended.dxf"):
    rooms, corridor, stair, elevator, walls, column, doors, windows, furniture = plan()
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.M
    for layer, color in [("A-WALL", 7), ("A-DOOR", 3), ("A-AREA", 5), ("A-AREA-IDEN", 2), ("A-STRS", 6),
                         ("A-COLS", 1), ("A-GLAZ", 4), ("A-FURN", 30), ("A-DETL", 8)]:
        doc.layers.add(layer, color=color)
    blk = doc.blocks.new("DOOR")
    blk.add_line((-0.45, 0), (0.45, 0))
    blk.add_arc((-0.45, 0), 0.9, 0, 90)
    for tag in ("TYPE", "AUTOMATIC", "MATERIAL"):
        blk.add_attdef(tag, (0, 0.1), dxfattribs={"height": 0.1, "invisible": True})
    msp = doc.modelspace()
    attribs = {"P101": {"TYPE": "swinging", "AUTOMATIC": "NO", "MATERIAL": "wood"},
               "P103": {"TYPE": "sliding", "AUTOMATIC": "YES", "MATERIAL": "glass"},
               "P104": {"TYPE": "revolving", "AUTOMATIC": "YES", "MATERIAL": "glass"},
               "P106": {"TYPE": "turnstile.fullheight", "AUTOMATIC": "NO", "MATERIAL": "metal"}}

    def poly(points, layer):
        msp.add_lwpolyline(points[:-1], close=True, dxfattribs={"layer": layer})

    for w in walls:
        poly(w, "A-WALL")
    for nm, box in list(rooms.items()) + [("HANH LANG", corridor), ("THANG MAY", elevator)]:
        poly(rect(*box), "A-AREA")
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        msp.add_text(nm, height=0.4, dxfattribs={"layer": "A-AREA-IDEN"}).set_placement(
            (cx, cy), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    poly(rect(*stair), "A-STRS")
    poly(rect(*column), "A-COLS")
    for room, cx, cy in doors:
        ins = msp.add_blockref("DOOR", (cx, cy), dxfattribs={"layer": "A-DOOR"})
        if room in attribs:
            ins.add_auto_attribs(attribs[room])
    for wx, wy in windows:
        msp.add_line((wx - 0.6, wy), (wx + 0.6, wy), dxfattribs={"layer": "A-GLAZ"})
    for _, box in furniture:
        poly(rect(*box), "A-FURN")
    for x in (3.0, 9.0, 15.0):
        msp.add_line((x, 5.6), (x + 1.0, 5.6), dxfattribs={"layer": "A-DETL"})
    doc.saveas(OUT / name)


if __name__ == "__main__":
    make_ifc_extended()
    make_ifc2x3()
    make_dxf_extended()
    print("OK")
