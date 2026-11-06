"""T2, T3, T4 và các ca biên của cad2bim."""
import ezdxf
import pytest

from src import cad2bim
from src.config import Project
from src.ingest.dxf import load_dxf
from src.model import Model, Storey


def _build(root, name="sample-floor-1.dxf"):
    project = Project(root / "samples" / "project-dxf.yaml")
    src = load_dxf(root / "samples" / name)
    model = Model()
    st = Storey("k", "1", "Tầng 1", 0.0, "dxf", "ref")
    cad2bim.build(src, st, project.layers, project.tags, model)
    return model


def test_t2_layer_mapping_counts_and_no_unmatched(root):
    m = _build(root)
    assert m.counts["dxf:space-boundary"] == 13
    assert m.counts["dxf:space-label"] == 13
    assert m.counts["dxf:door"] == 12
    assert m.counts["dxf:wall"] == 13              # 12 LINE + 1 LWPOLYLINE
    assert m.unmatched == {}


def test_t3_room_polygons_and_areas(root):
    spaces = [o for o in _build(root).objs if o.type == "space"]
    assert len(spaces) == 13
    areas = sorted(round(o.geometry.area, 6) for o in spaces)
    assert areas.count(20.0) == 12 and areas.count(48.0) == 1


def test_t4_labels_attached_to_right_polygon(root):
    spaces = [o for o in _build(root).objs if o.type == "space"]
    refs = {o.props["ref"] for o in spaces if o.props["ref"]}
    assert refs == {f"P1{n:02d}" for n in range(1, 13)}
    corridor = [o for o in spaces if o.props["name"] == "HANH LANG"]
    assert len(corridor) == 1 and corridor[0].props["ref"] is None
    for o in spaces:
        if o.props["ref"] and o.props["ref"] != "P1":
            assert o.geometry.contains(o.geometry.representative_point())


def test_door_opening_width_from_block_and_rotation(root):
    doors = [o for o in _build(root).objs if o.type == "door"]
    assert len(doors) == 12
    for d in doors:
        assert d.geometry.length == pytest.approx(0.9)


def test_unclosed_polyline_is_polygonized_with_warning(tmp_path, root):
    doc = ezdxf.new("R2010"); doc.units = 6
    doc.layers.add("A-AREA")
    doc.modelspace().add_lwpolyline([(0, 0), (4, 0), (4, 5), (0, 5), (0, 0)], dxfattribs={"layer": "A-AREA"})  # không close=True
    doc.saveas(tmp_path / "open.dxf")
    project = Project(root / "samples" / "project-dxf.yaml")
    model = Model()
    cad2bim.build(load_dxf(tmp_path / "open.dxf"), Storey("k", "1", "T1", 0.0, "dxf", "r"), project.layers, project.tags, model)
    spaces = [o for o in model.objs if o.type == "space"]
    assert len(spaces) == 1 and spaces[0].geometry.area == pytest.approx(20.0)
    assert any("polygonize" in w for w in model.warnings)


def test_unmatched_layer_reported_not_raised(tmp_path, root):
    doc = ezdxf.new("R2010"); doc.units = 6
    doc.layers.add("XYZ-LAYER")
    doc.modelspace().add_line((0, 0), (1, 1), dxfattribs={"layer": "XYZ-LAYER"})
    doc.saveas(tmp_path / "u.dxf")
    project = Project(root / "samples" / "project-dxf.yaml")
    model = Model()
    cad2bim.build(load_dxf(tmp_path / "u.dxf"), Storey("k", "1", "T1", 0.0, "dxf", "r"), project.layers, project.tags, model)
    assert model.unmatched == {("XYZ-LAYER", "LINE"): 1}


def test_layer_normalisation_strips_xref_prefix(root):
    project = Project(root / "samples" / "project-dxf.yaml")
    assert cad2bim.norm_layer("XREF|a-wall", project.layers) == "A-WALL"
    kind, rule = cad2bim.match_rule("xref|A-DOOR", "INSERT", "DOOR", project.layers)
    assert kind == "rule" and rule["id"] == "door"
    assert cad2bim.match_rule("Defpoints", "POINT", None, project.layers)[0] == "ignore"
