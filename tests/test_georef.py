"""T9 và các nguồn georeference."""
import math

import pytest
from pyproj import Transformer
from shapely.geometry import Point

from src import pipeline
from src.config import DataError, Project
from src.extract import georef as gr
from src.model import Model


def test_t9_origin_maps_to_expected_lonlat():
    g = gr.Georef("project", "EPSG:3405", 588000.0, 2325000.0, 0.0, 1.0)
    p = g.to_wgs84(Point(0, 0))
    lon, lat = Transformer.from_crs("EPSG:3405", "EPSG:4326", always_xy=True).transform(588000.0, 2325000.0)
    assert (p.x, p.y) == pytest.approx((lon, lat), abs=1e-12)
    assert 105.8 < p.x < 105.9 and 21.0 < p.y < 21.1       # khoảng Hà Nội (toạ độ minh hoạ)


def test_rotation_and_scale_follow_spec_formula():
    g = gr.Georef("project", "EPSG:3405", 100.0, 200.0, 90.0, 2.0)
    e = g.to_projected(Point(10, 0))                      # xoay 90° CCW, scale 2: E=100+2*(10*0)=100, N=200+2*10=220
    assert (e.x, e.y) == pytest.approx((100.0, 220.0))
    h = gr.Georef("project", "EPSG:3405", 0.0, 0.0, 30.0, 1.0).to_projected(Point(10, 5))
    a, b = math.cos(math.radians(30)), math.sin(math.radians(30))
    assert (h.x, h.y) == pytest.approx((10 * a - 5 * b, 10 * b + 5 * a))


def test_missing_georeference_is_data_error(root):
    p = Project(root / "samples" / "project-dxf.yaml")
    p.georeference = None
    with pytest.raises(DataError, match="georeference"):
        pipeline.run(p)


def test_allow_unreferenced_keeps_local_coordinates(root):
    p = Project(root / "samples" / "project-dxf.yaml")
    p.georeference = None
    res = pipeline.run(p, allow_unreferenced=True)
    assert res.meta["crs_source"] == "none"
    assert res.features["unit"].crs is None
    xs = res.features["unit"].total_bounds
    assert tuple(xs) == pytest.approx((0.0, 0.0, 24.0, 12.0))     # mét cục bộ, đúng bao 24×12


def test_ifc_map_conversion_is_read_and_normalised(root, tmp_path):
    import ifcopenshell
    import ifcopenshell.api
    import ifcopenshell.api.georeference

    f = ifcopenshell.open(str(root / "samples" / "sample-building.ifc"))
    ifcopenshell.api.georeference.add_georeferencing(f)
    ifcopenshell.api.georeference.edit_georeferencing(
        f, projected_crs={"Name": "EPSG:3405"},
        coordinate_operation={"Eastings": 588000.0, "Northings": 2325000.0, "OrthogonalHeight": 0.0,
                              "XAxisAbscissa": 3.0, "XAxisOrdinate": 4.0, "Scale": 1.0})
    g = gr.from_ifc_map_conversion(f, 1.0, Model(), "t.ifc")
    assert g.crs == "EPSG:3405" and g.e0 == 588000.0 and g.n0 == 2325000.0
    assert g.rotation_deg == pytest.approx(math.degrees(math.atan2(4, 3)))   # (3,4) chuẩn hoá thành (0.6, 0.8)
    pt = g.to_projected(Point(10, 0))
    assert (pt.x, pt.y) == pytest.approx((588000.0 + 6.0, 2325000.0 + 8.0))


def test_ifc_georef_takes_priority_over_project(root):
    ifc = gr.Georef("ifc_map_conversion", "EPSG:3406", 1.0, 2.0)
    out = gr.resolve({"crs": "EPSG:3405", "origin": [0, 0]}, ifc, None, False, Model())
    assert out.source == "ifc_map_conversion"
