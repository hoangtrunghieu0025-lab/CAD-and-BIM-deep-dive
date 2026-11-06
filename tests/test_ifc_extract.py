"""T5, T6, T19."""
import numpy as np
import pytest

from src import cad2bim
from src.config import Project
from src.ingest.dxf import load_dxf
from src.model import Model, Storey


def test_t5_ifc_counts_and_storey_via_aggregate(built):
    res, _, _ = built["ifc"]
    m = res.model
    assert len(m.storeys) == 2
    assert m.counts["ifc:IfcSpace"] == 26 and m.counts["ifc:IfcDoor"] == 24 and m.counts["ifc:IfcWall"] == 8
    keys = {s.key for s in m.storeys}
    spaces = [o for o in m.objs if o.type == "space"]
    assert len(spaces) == 26 and all(o.storey_key in keys for o in spaces)   # get_aggregate trả tầng cho mọi IfcSpace
    assert {s.elevation_m for s in m.storeys} == {0.0, 3.0}                  # đơn vị mét đã đúng (lỗi đơn vị mm cũ)


def test_t6_ifc_footprint_equals_dxf_area(root, built):
    res, _, _ = built["ifc"]
    st1 = next(s for s in res.model.storeys if s.elevation_m == 0.0)
    ifc_areas = sorted(round(o.geometry.area, 6) for o in res.model.objs if o.type == "space" and o.storey_key == st1.key)
    project = Project(root / "samples" / "project-dxf.yaml")
    model = Model()
    cad2bim.build(load_dxf(root / "samples" / "sample-floor-1.dxf"), Storey("k", "1", "T", 0.0, "dxf", "r"),
                  project.layers, project.tags, model)
    dxf_areas = sorted(round(o.geometry.area, 6) for o in model.objs if o.type == "space")
    assert len(ifc_areas) == len(dxf_areas) == 13
    assert np.allclose(ifc_areas, dxf_areas, atol=1e-6)


def test_t19_door_centres_match_between_ifc_and_dxf(built):
    """Phép kiểm 'nằm trên ranh giới' không thấy lệch dọc tường; so thẳng tâm opening IFC với DXF."""
    def centres(kind):
        g = built[kind][0].features["opening"]
        pts = sorted((round(c.x, 9), round(c.y, 9)) for c in (x.centroid for x in g.geometry))
        return np.array(pts)
    a, b = centres("ifc"), centres("dxf")
    assert a.shape == b.shape == (24, 2)
    assert np.allclose(a, b, atol=1e-8)            # ~1 mm


def test_ifc_door_center_source_is_flagged_when_only_placement(built):
    res, _, _ = built["ifc"]
    assert all(o.props["center_source"] == "placement_with_anchor" for o in res.model.objs if o.type == "door")
    assert any("placement" in w for w in res.model.warnings)


def test_union_xy_reports_dropped_pieces():
    from src.extract.ifc import _union_xy

    # hai hình vuông rời nhau (mỗi hình 2 tam giác): giữ hình lớn hơn, báo bỏ 1 mảnh
    big = [(0, 0, 0), (4, 0, 0), (4, 4, 0), (0, 4, 0)]
    small = [(10, 0, 0), (11, 0, 0), (11, 1, 0), (10, 1, 0)]
    v = np.array(big + small, dtype=float)
    f = np.array([[0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7]])
    poly, dropped = _union_xy(v, f)
    assert dropped == 1 and poly.area == pytest.approx(16.0)
    single, none = _union_xy(v[:4], f[:2])
    assert none == 0 and single.area == pytest.approx(16.0)
