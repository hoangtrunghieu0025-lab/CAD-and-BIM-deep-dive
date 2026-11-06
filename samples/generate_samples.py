"""Sinh file mẫu DXF + IFC cho dự án (tự dựng, không dùng dữ liệu bên thứ ba).

Chạy:  .venv/bin/python samples/generate_samples.py

Toà nhà giả định 2 tầng, mặt bằng 24 m x 12 m, hệ toạ độ cục bộ (mét), gốc (0,0)
ở góc tây-nam. Mỗi tầng: 6 phòng phía nam + 6 phòng phía bắc (mỗi phòng 4 x 5 m),
hành lang rộng 2 m ở giữa => 12 phòng/tầng, 24 phòng tổng.
"""
from pathlib import Path

import ezdxf
import ifcopenshell
import ifcopenshell.api
import numpy as np

OUT = Path(__file__).resolve().parent

COLS, ROOM_W, ROOM_D, CORR_D = 6, 4.0, 5.0, 2.0
BLD_W = COLS * ROOM_W                      # 24
BLD_D = 2 * ROOM_D + CORR_D                # 12
FLOOR_H, WALL_T, DOOR_W, DOOR_H = 3.0, 0.2, 0.9, 2.1
LEVELS = [("Tầng 1", 0.0, 100), ("Tầng 2", FLOOR_H, 200)]


def rooms(base):
    """Trả về [(tên, (x0,y0,x1,y1))]; số phòng = base + 1.. base + 12."""
    out = []
    for i in range(COLS):
        x0 = i * ROOM_W
        out.append((f"P{base + 1 + i}", (x0, 0.0, x0 + ROOM_W, ROOM_D)))                 # nam
        out.append((f"P{base + 7 + i}", (x0, ROOM_D + CORR_D, x0 + ROOM_W, BLD_D)))      # bắc
    return out


def door_pos(box):
    """Cửa mở ra hành lang: giữa cạnh hướng hành lang. Trả về (x, y, hướng y)."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    return (cx, y1, +1) if y0 == 0.0 else (cx, y0, -1)


# ----------------------------------------------------------------- DXF
def make_dxf(name, base):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.M          # $INSUNITS = 6 (mét)
    for layer, color in [("A-WALL", 7), ("A-DOOR", 3), ("A-AREA", 5), ("A-AREA-IDEN", 2)]:
        doc.layers.add(layer, color=color)
    blk = doc.blocks.new("DOOR")
    blk.add_line((-DOOR_W / 2, 0), (DOOR_W / 2, 0))
    blk.add_arc((-DOOR_W / 2, 0), DOOR_W, 0, 90)
    msp = doc.modelspace()
    # tường ngoài (polyline kín) + tường ngăn phòng/hành lang
    msp.add_lwpolyline([(0, 0), (BLD_W, 0), (BLD_W, BLD_D), (0, BLD_D)], close=True,
                       dxfattribs={"layer": "A-WALL"})
    for y in (ROOM_D, ROOM_D + CORR_D):
        msp.add_line((0, y), (BLD_W, y), dxfattribs={"layer": "A-WALL"})
    for i in range(1, COLS):
        for ya, yb in ((0, ROOM_D), (ROOM_D + CORR_D, BLD_D)):
            msp.add_line((i * ROOM_W, ya), (i * ROOM_W, yb), dxfattribs={"layer": "A-WALL"})
    for room, box in rooms(base):
        x0, y0, x1, y1 = box
        msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True,
                           dxfattribs={"layer": "A-AREA"})
        msp.add_text(room, height=0.4, dxfattribs={"layer": "A-AREA-IDEN"}).set_placement(
            ((x0 + x1) / 2, (y0 + y1) / 2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        dx, dy, sgn = door_pos(box)
        msp.add_blockref("DOOR", (dx, dy), dxfattribs={"layer": "A-DOOR",
                                                        "rotation": 0 if sgn > 0 else 180})
    corr = [(0, ROOM_D), (BLD_W, ROOM_D), (BLD_W, ROOM_D + CORR_D), (0, ROOM_D + CORR_D)]
    msp.add_lwpolyline(corr, close=True, dxfattribs={"layer": "A-AREA"})
    msp.add_text("HANH LANG", height=0.4, dxfattribs={"layer": "A-AREA-IDEN"}).set_placement(
        (BLD_W / 2, ROOM_D + CORR_D / 2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    doc.saveas(OUT / name)


# ----------------------------------------------------------------- IFC
def make_ifc(name):
    f = ifcopenshell.api.run("project.create_file", version="IFC4")
    api = ifcopenshell.api
    project = api.run("root.create_entity", f, ifc_class="IfcProject", name="Sample Building")
    api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METERS"})  # mét (mặc định của api là mm)
    ctx = api.run("context.add_context", f, context_type="Model")
    body = api.run("context.add_context", f, context_type="Model", context_identifier="Body",
                   target_view="MODEL_VIEW", parent=ctx)
    site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
    bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Sample Building")
    api.run("aggregate.assign_object", f, products=[site], relating_object=project)
    api.run("aggregate.assign_object", f, products=[bld], relating_object=site)

    def place(prod, x, y, z, rot_deg=0.0):
        c, s = np.cos(np.radians(rot_deg)), np.sin(np.radians(rot_deg))
        m = np.array([[c, -s, 0, x], [s, c, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])
        api.run("geometry.edit_object_placement", f, product=prod, matrix=m)

    for lname, elev, base in LEVELS:
        st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name=lname)
        st.Elevation = elev
        api.run("aggregate.assign_object", f, products=[st], relating_object=bld)
        place(st, 0, 0, elev)

        def add_wall(x, y, length, rot, nm):
            w = api.run("root.create_entity", f, ifc_class="IfcWall", name=nm)
            rep = api.run("geometry.add_wall_representation", f, context=body,
                          length=length, height=FLOOR_H, thickness=WALL_T)
            api.run("geometry.assign_representation", f, product=w, representation=rep)
            place(w, x, y, elev, rot)
            api.run("spatial.assign_container", f, products=[w], relating_structure=st)

        add_wall(0, 0, BLD_W, 0, f"{lname} - tuong ngoai nam")
        add_wall(BLD_W, 0, BLD_D, 90, f"{lname} - tuong ngoai dong")
        add_wall(BLD_W, BLD_D, BLD_W, 180, f"{lname} - tuong ngoai bac")
        add_wall(0, BLD_D, BLD_D, 270, f"{lname} - tuong ngoai tay")

        def add_space(nm, long_name, box):
            x0, y0, x1, y1 = box
            sp = api.run("root.create_entity", f, ifc_class="IfcSpace", name=nm)
            sp.LongName = long_name
            poly = [(0.0, 0.0), (x1 - x0, 0.0), (x1 - x0, y1 - y0), (0.0, y1 - y0), (0.0, 0.0)]
            rep = api.run("geometry.add_slab_representation", f, context=body,
                          depth=FLOOR_H, polyline=poly)
            api.run("geometry.assign_representation", f, product=sp, representation=rep)
            place(sp, x0, y0, elev)
            api.run("aggregate.assign_object", f, products=[sp], relating_object=st)
            pset = api.run("pset.add_pset", f, product=sp, name="Pset_SpaceCommon")
            api.run("pset.edit_pset", f, pset=pset, properties={"Reference": nm, "IsExternal": False})
            return sp

        for room, box in rooms(base):
            add_space(room, f"Phong {room}", box)
            dx, dy, sgn = door_pos(box)
            d = api.run("root.create_entity", f, ifc_class="IfcDoor", name=f"Cua {room}")
            d.OverallWidth, d.OverallHeight = DOOR_W, DOOR_H
            place(d, dx - DOOR_W / 2, dy, elev)
            api.run("spatial.assign_container", f, products=[d], relating_structure=st)
        add_space(f"HL{base}", "Hanh lang", (0.0, ROOM_D, BLD_W, ROOM_D + CORR_D))
    f.write(str(OUT / name))


if __name__ == "__main__":
    make_dxf("sample-floor-1.dxf", 100)
    make_dxf("sample-floor-2.dxf", 200)
    make_ifc("sample-building.ifc")
    print("OK")
