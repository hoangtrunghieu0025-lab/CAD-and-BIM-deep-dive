"""TASK-018 M1: classify.py + read.py + analyze.py trên DXF tổng hợp dựng bằng ezdxf (có đáp án)."""
import math

import ezdxf
import pytest

from src.cad2bim.analyze import analyze, load_cfg
from src.cad2bim.classify import Classifier, UNKNOWN, ANNOTATION
from src.cad2bim.read import Prim, iter_prims, resolve_units, guess_extent_m


@pytest.fixture(scope="module")
def cls():
    return Classifier(load_cfg())


@pytest.mark.parametrize("layer, kind", [
    ("A-WALL", "wall"), ("A-WALL-FULL", "wall"), ("WALL", "wall"), ("Walls", "wall"), ("MURO", "wall"),
    ("A-DOOR", "door"), ("DOORS", "door"), ("PUERTA", "door"),
    ("WIN", "window"), ("A-GLAZ", "window"), ("CECO.NET SMITH HOUSE GLASSES", "window"),
    ("COLUMN", "column"), ("COL", "column"), ("A-COLS", "column"),
    ("AREA", "space"), ("A-AREA", "space"), ("ROOM", "space"),
    ("BEAM CONCRETE", "beam"), ("FUR", "furniture"),
    ("04-AC_F.A.DUCT", "mep_duct"), ("15-AC-CH.WT PIPING (S)", "mep_pipe"), ("M-EQBMNT", "mep_equipment"),
    ("A-WALL-TEXT", ANNOTATION), ("AC-TEXT", ANNOTATION), ("COLHATCH", ANNOTATION), ("A-AREA-IDEN", ANNOTATION),
    ("DEFPOINTS", ANNOTATION), ("00-1-FRAME", ANNOTATION), ("DIM", ANNOTATION),
    ("COLOR", UNKNOWN), ("COLLECTION", UNKNOWN), ("0", UNKNOWN), ("XYZ", UNKNOWN),
])
def test_layer_kind(cls, layer, kind):
    assert cls.layer_kind(layer) == kind


def test_token_match_not_substring(cls):
    # lỗi của ifcbim: "col" khớp "color", "floor" -> slab. Ở đây chỉ khớp token nguyên
    assert cls.layer_kind("COLOR") == UNKNOWN and cls.layer_kind("FLOORING") == UNKNOWN


def test_block_kind(cls):
    assert cls.block_kind("DOOR_900") == "door" and cls.block_kind("Window-2") == "window"
    assert cls.block_kind("*U12") is None and cls.block_kind("CHAIR") is None


def _doc(units=6):
    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = units
    return doc, doc.modelspace()


def _prims(msp, factor, cls, **kw):
    return list(iter_prims(msp, factor, cls.layer_kind, **kw))


def test_bulge_is_kept(cls):
    doc, msp = _doc()
    msp.add_lwpolyline([(0, 0, 1), (4, 0, 0), (4, 3, 0)], format="xyb", dxfattribs={"layer": "WALL"})
    pr = _prims(msp, 1.0, cls, flatten_m=0.001)[0]
    length = sum(math.dist(a, b) for a, b in zip(pr.pts, pr.pts[1:]))
    assert length == pytest.approx(2 * math.pi + 3, rel=1e-3)         # nửa đường tròn R=2 + đoạn 3 m


def test_insert_explosion_and_layer_inheritance(cls):
    doc, msp = _doc()
    blk = doc.blocks.new("DOOR")
    blk.add_line((0, 0), (0.9, 0), dxfattribs={"layer": "0"})
    blk.add_arc((0, 0), 0.9, 0, 90, dxfattribs={"layer": "0"})
    msp.add_blockref("DOOR", (5, 1), dxfattribs={"layer": "A-DOOR", "rotation": 90})
    prims = _prims(msp, 1.0, cls)
    assert [p.etype for p in prims] == ["INSERT", "LINE", "ARC"]
    assert all(p.layer == "A-DOOR" and p.kind == "door" for p in prims)       # layer "0" kế thừa từ INSERT
    line = prims[1]
    assert line.pts[0] == pytest.approx((5.0, 1.0)) and line.pts[1] == pytest.approx((5.0, 1.9))   # xoay 90°


def test_mirrored_insert_arc_center_in_wcs(cls):
    doc, msp = _doc()
    blk = doc.blocks.new("DOOR")
    blk.add_arc((0, 0), 0.9, 0, 90, dxfattribs={"layer": "0"})
    msp.add_blockref("DOOR", (2, 1), dxfattribs={"layer": "A-DOOR", "rotation": 90, "xscale": -1})
    arc = [p for p in _prims(msp, 1.0, cls, flatten_m=0.001) if p.etype == "ARC"][0]
    xs, ys = [q[0] for q in arc.pts], [q[1] for q in arc.pts]
    # cung bán kính 0,9 có một đầu mút tại (2±0.9...) quanh tâm (2,1): mọi điểm cách (2,1) đúng 0,9
    assert all(math.dist(q, (2.0, 1.0)) == pytest.approx(0.9, abs=1e-3) for q in arc.pts)
    assert arc.radius == pytest.approx(0.9)


def test_units_from_insunits_and_guess(cls):
    doc, msp = _doc(units=4)
    f, name, how = resolve_units(doc, {}, None, None)
    assert (f, name, how) == (0.001, "mm", "insunits")
    doc0, msp0 = _doc(units=0)
    msp0.add_line((0, 0), (24000, 0))
    msp0.add_line((0, 0), (0, 12000))
    ext = lambda u: guess_extent_m(msp0, u)
    cfg_u = {"guess_order": ["m", "mm", "cm", "in"], "plausible_extent_m": [3.0, 600.0]}
    f2, name2, how2 = resolve_units(doc0, cfg_u, ext, None)
    assert (name2, how2) == ("mm", "guess")                      # 24 000 đơn vị = 24 m nếu là mm


def test_analyze_synthetic_plan(tmp_path):
    doc, msp = _doc(units=6)
    for layer in ("WALL", "DOOR", "AREA", "WIN", "COLUMN", "A-WALL-TEXT"):
        doc.layers.add(layer)
    # phòng 6x4 vẽ nét đôi, dày 0,2
    def rect(x0, y0, x1, y1):
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    msp.add_lwpolyline(rect(-.1, -.1, 6.1, 4.1), close=True, dxfattribs={"layer": "WALL"})
    msp.add_lwpolyline(rect(.1, .1, 5.9, 3.9), close=True, dxfattribs={"layer": "WALL"})
    msp.add_lwpolyline(rect(.1, .1, 5.9, 3.9), close=True, dxfattribs={"layer": "AREA"})
    msp.add_text("PHONG KHACH", dxfattribs={"layer": "A-WALL-TEXT", "insert": (3, 2), "height": .2})
    msp.add_lwpolyline(rect(2.9, 3.9, 3.1, 4.1), close=True, dxfattribs={"layer": "COLUMN"})
    blk = doc.blocks.new("DOOR_90")
    blk.add_line((0, 0), (0.9, 0)); blk.add_arc((0, 0), 0.9, 0, 90)
    msp.add_blockref("DOOR_90", (1.0, 0.0), dxfattribs={"layer": "DOOR"})
    f = tmp_path / "plan.dxf"
    doc.saveas(f)
    m = analyze(f)
    assert m.stats["units_how"] == "insunits" and m.stats["units"] == "m"
    assert len(m.of("space")) == 1 and m.of("space")[0].props["name"] == "PHONG KHACH"
    assert len(m.of("door")) == 1 and m.of("door")[0].params["width"] == pytest.approx(0.9, abs=0.02)
    assert len(m.of("column")) == 1
    walls = m.of("wall")
    assert m.stats["n_walls_pair"] == 4 and all(w.params["thickness"] == pytest.approx(0.2, abs=1e-6) for w in walls)
    assert all(w.prov.claims["thickness"] == "derived" and w.prov.claims["height"] == "assumed" for w in walls)
    assert m.stats["wall_footprint_m2"] == pytest.approx(6.2 * 4.2 - 5.8 * 3.8, abs=0.01)


def test_elements_have_stable_ids(tmp_path):
    doc, msp = _doc()
    doc.layers.add("WALL")
    msp.add_line((0, 0), (5, 0), dxfattribs={"layer": "WALL"})
    msp.add_line((0, 0.2), (5, 0.2), dxfattribs={"layer": "WALL"})
    f = tmp_path / "w.dxf"
    doc.saveas(f)
    a, b = analyze(f), analyze(f)
    assert [e.id for e in a.elements] == [e.id for e in b.elements] and a.elements


def test_declared_unit_that_is_implausible_gets_overridden():
    """Ca tái hiện từ bản vẽ thật: $INSUNITS=4 (mm) nhưng kích thước 27,8 x 14 đơn vị => căn hộ vẽ theo mét."""
    doc, msp = _doc(units=4)
    msp.add_line((0, 0), (27.8, 0)); msp.add_line((0, 0), (0, 14.0))
    cfg_u = {"guess_order": ["m", "mm", "cm", "in"], "plausible_extent_m": [3.0, 300.0]}
    f, name, how = resolve_units(doc, cfg_u, lambda u: guess_extent_m(msp, u), None)
    assert (name, how) == ("m", "insunits_conflict")


def test_declared_unit_that_is_plausible_is_kept():
    doc, msp = _doc(units=4)
    msp.add_line((0, 0), (27800, 0)); msp.add_line((0, 0), (0, 14000))
    cfg_u = {"guess_order": ["m", "mm", "cm", "in"], "plausible_extent_m": [3.0, 300.0]}
    assert resolve_units(doc, cfg_u, lambda u: guess_extent_m(msp, u), None) == (0.001, "mm", "insunits")


def test_empty_drawing_keeps_declared_unit():
    doc, msp = _doc(units=4)
    cfg_u = {"guess_order": ["m", "mm", "cm", "in"], "plausible_extent_m": [3.0, 300.0]}
    assert resolve_units(doc, cfg_u, lambda u: guess_extent_m(msp, u), None)[2] == "insunits"


def test_unit_check_sees_geometry_inside_blocks_inserted_at_origin(tmp_path):
    """Ca tái hiện từ bản vẽ thật (Apto, Small-apto): mọi INSERT cấp cao nhất đặt tại (0,0) và chứa hình học ở toạ độ
    thật (xa gốc); $INSUNITS=4 nhưng bản vẽ rộng ~28 đơn vị => phải nhận ra là mét, không được bỏ qua kiểm tra."""
    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = 4
    doc.layers.add("WALL")
    blk = doc.blocks.new("PLAN")
    for y in (2150.0, 2150.3):                                    # hai nét tường song song cách nhau 0,3 đơn vị
        blk.add_line((2840.0, y), (2868.0, y), dxfattribs={"layer": "WALL"})
    blk.add_line((2840.0, 2150.0), (2840.0, 2164.0), dxfattribs={"layer": "WALL"})
    doc.modelspace().add_blockref("PLAN", (0, 0), dxfattribs={"layer": "0"})
    f = tmp_path / "origin_block.dxf"
    doc.saveas(f)
    m = analyze(f)
    assert m.stats["units"] == "m" and m.stats["units_how"] == "insunits_conflict"
    assert m.stats["wall_input_len_m"] > 40.0                      # 28 + 28 + 14 m, không phải 0,07 m
