"""TASK-018 (3D): read3d.py, analyze3d.py, ifc3d.py trên DXF tổng hợp dựng bằng ezdxf (có đáp án)."""
import math

import ezdxf
import ifcopenshell
import ifcopenshell.util.unit as iunit
import pytest

from src.cad2bim.analyze3d import analyze3d
from src.cad2bim.ifc3d import write_ifc3d
from src.cad2bim.read3d import Mesh3D, Wire3D


def _save(doc, tmp_path, name="m.dxf"):
    p = tmp_path / name
    doc.saveas(p)
    return p


def _doc(units=6):
    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = units
    return doc


def test_polyface_3dface_mesh_polygonmesh(tmp_path):
    doc = _doc()
    msp = doc.modelspace()
    pf = msp.add_polyface(dxfattribs={"layer": "ROOF"})
    pf.append_faces([[(0, 0, 3), (10, 0, 3), (10, 10, 3)], [(0, 0, 3), (10, 10, 3), (0, 10, 3)]])
    msp.add_3dface([(0, 0, 0), (4, 0, 0), (4, 4, 0), (0, 4, 0)], dxfattribs={"layer": "FLOOR"})
    msp.add_3dface([(0, 0, 0), (4, 0, 0), (4, 4, 0), (4, 4, 0)], dxfattribs={"layer": "TRI"})        # tam giác (đỉnh 3 = đỉnh 2)
    msh = msp.add_mesh(dxfattribs={"layer": "M"})
    with msh.edit_data() as md:
        md.vertices = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
        md.faces = [[0, 1, 2, 3]]
    pm = msp.add_polymesh((2, 3), dxfattribs={"layer": "PM"})
    for i in range(2):
        for j in range(3):
            pm.set_mesh_vertex((i, j), (i, j, 0.5))
    m = analyze3d(_save(doc, tmp_path))
    src = {x.source: x for x in m.meshes}
    assert set(src) == {"polyface", "3dface", "mesh", "polygon_mesh"}
    assert len(src["polyface"].faces) == 2
    assert sorted(len(x.faces[0]) for x in m.meshes if x.source == "3dface") == [3, 4]     # tam giác và tứ giác
    assert len(src["polygon_mesh"].faces) == 2                                               # lưới 2x3 -> 1x2 ô
    assert m.stats["bbox_m"][1][2] == pytest.approx(3.0)


def test_arc_and_circle_are_exact_three_and_four_points(tmp_path):
    doc = _doc()
    msp = doc.modelspace()
    msp.add_arc((0, 0, 0), 2.0, 0, 90)
    msp.add_circle((10, 0, 0), 1.0)
    m = analyze3d(_save(doc, tmp_path))
    arc = next(w for w in m.wires if w.shape == "arc3")
    assert [round(c, 6) for c in arc.pts[0]] == [2.0, 0.0, 0.0]
    assert [round(c, 6) for c in arc.pts[2]] == [0.0, 2.0, 0.0]
    mid = arc.pts[1]
    assert mid[0] == pytest.approx(math.sqrt(2)) and mid[1] == pytest.approx(math.sqrt(2))   # điểm giữa cung ở 45°
    circ = next(w for w in m.wires if w.shape == "circle4")
    assert len(circ.pts) == 4 and circ.pts[2][0] == pytest.approx(9.0)


def test_arc_wraps_through_zero_degrees(tmp_path):
    doc = _doc()
    doc.modelspace().add_arc((0, 0, 0), 1.0, 270, 90)         # đi qua 0°: giữa phải ở 0°
    arc = analyze3d(_save(doc, tmp_path)).wires[0]
    assert arc.pts[1][0] == pytest.approx(1.0) and arc.pts[1][1] == pytest.approx(0.0, abs=1e-9)


def test_thickness_makes_prism_and_keeps_wire(tmp_path):
    doc = _doc()
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (4, 0), (4, 3), (0, 3)], close=True, dxfattribs={"thickness": 2.5, "layer": "WALL"})
    m = analyze3d(_save(doc, tmp_path))
    prism = [x for x in m.meshes if x.source == "extrusion"]
    assert len(prism) == 1 and len(prism[0].faces) == 6                 # 4 mặt bên + 2 nắp
    assert max(v[2] for v in prism[0].vertices) == pytest.approx(2.5)
    assert any(isinstance(w, Wire3D) for w in m.wires)


def test_open_line_with_thickness_gives_single_quad(tmp_path):
    doc = _doc()
    doc.modelspace().add_line((0, 0, 0), (5, 0, 0), dxfattribs={"thickness": 3.0})
    prism = [x for x in analyze3d(_save(doc, tmp_path)).meshes if x.source == "extrusion"]
    assert len(prism) == 1 and len(prism[0].faces) == 1


def test_nested_inserts_deeper_than_old_limit_are_read(tmp_path):
    doc = _doc()
    depth = 6                                                         # sâu hơn giới hạn 3 của bộ đọc 2D
    blocks = [doc.blocks.new(f"B{i}") for i in range(depth)]
    pf = blocks[-1].add_polyface(dxfattribs={"layer": "DEEP"})
    pf.append_face([(0, 0, 0), (1, 0, 0), (1, 1, 0)])
    for i in range(depth - 1):
        blocks[i].add_blockref(f"B{i + 1}", (0, 0, 0))
    doc.modelspace().add_blockref("B0", (100, 0, 0))
    m = analyze3d(_save(doc, tmp_path))
    assert len(m.meshes) == 1 and m.stats["insert_too_deep"] == 0
    assert m.meshes[0].vertices[0][0] == pytest.approx(100.0)          # phép dời của INSERT đã áp dụng


def test_layer_zero_inherits_insert_layer(tmp_path):
    doc = _doc()
    blk = doc.blocks.new("DOORB")
    blk.add_line((0, 0), (1, 0), dxfattribs={"layer": "0"})
    doc.layers.add("A-DOOR")
    doc.modelspace().add_blockref("DOORB", (0, 0), dxfattribs={"layer": "A-DOOR"})
    m = analyze3d(_save(doc, tmp_path))
    assert m.wires[0].layer == "A-DOOR" and m.wires[0].kind == "door"


def test_unknown_layers_are_kept_not_dropped(tmp_path):
    doc = _doc()
    doc.modelspace().add_line((0, 0, 0), (1, 1, 1), dxfattribs={"layer": "XYZ-123"})
    m = analyze3d(_save(doc, tmp_path))
    assert len(m.wires) == 1 and m.wires[0].kind == "unknown"          # khác read.py 2D: 3D không bỏ layer lạ


def test_acis_solid_is_counted_as_unsupported_not_silently_lost(tmp_path):
    doc = ezdxf.new("R2007")                                         # R2007: ACIS dạng văn bản SAT (R2013+ dùng nhị phân, ezdxf không ghi được)
    doc.header["$INSUNITS"] = 6
    e = doc.modelspace().new_entity("3DSOLID", {"layer": "S"})
    e.sat = ["400 1 1 0 ", "1 0 1 0"]                                  # dữ liệu giả: chỉ để thực thể tồn tại
    m = analyze3d(_save(doc, tmp_path))
    assert m.stats["unsupported"] == {"3DSOLID": 1} and not m.meshes


def test_units_conflict_is_resolved_and_warned(tmp_path):
    doc = _doc(units=4)                                                 # khai báo mm nhưng bản vẽ rộng 28 đơn vị -> mét
    doc.modelspace().add_line((0, 0, 0), (28, 0, 0))
    m = analyze3d(_save(doc, tmp_path))
    assert m.stats["units"] == "m" and m.stats["units_how"] == "insunits_conflict" and m.warnings


def test_ifc_roundtrip_exact_arcs_and_unit(tmp_path):
    doc = _doc()
    msp = doc.modelspace()
    pf = msp.add_polyface(dxfattribs={"layer": "ROOF"})
    pf.append_face([(0, 0, 3), (10, 0, 3), (10, 10, 3)])
    msp.add_line((0, 0, 0), (5, 0, 0), dxfattribs={"layer": "ROOF"})
    msp.add_arc((0, 0, 0), 2.0, 0, 90, dxfattribs={"layer": "ROOF"})
    msp.add_circle((10, 0, 0), 1.0, dxfattribs={"layer": "ROOF"})
    m = analyze3d(_save(doc, tmp_path))
    out = tmp_path / "o.ifc"
    info = write_ifc3d(m, out)
    assert info["exact_arcs"] == 2 and info["faces"] == 1
    f = ifcopenshell.open(str(out))
    assert iunit.calculate_unit_scale(f) == 1.0                         # đơn vị dài là mét (lỗi cũ: .MILLI.)
    assert {p.Name for p in f.by_type("IfcBuildingElementProxy")} == {"ROOF", "ROOF (wire)"}
    curves = f.by_type("IfcIndexedPolyCurve")
    assert len(curves) == 2 and sum(len(c.Segments) for c in curves) == 3   # cung 1 đoạn + tròn 2 đoạn (IfcArcIndex)
    assert len(f.by_type("IfcPolyline")) == 1
