"""T14, T15."""
import json
import zipfile

import pytest

from src.export.gpkg import write_gpkg
from src.export.imdf import ImdfExportError, export_imdf
from src.normalize.ids import UUID_V4_RE
from src import pipeline

REQUIRED = {"manifest.json", "address.geojson", "venue.geojson"}


@pytest.mark.parametrize("kind", ["dxf", "ifc"])
def test_t14_package_structure(built, tmp_path, kind):
    z = export_imdf(built[kind][1], tmp_path / "b.imdf.zip")
    with zipfile.ZipFile(z) as zf:
        names = set(zf.namelist())
        assert REQUIRED <= names
        assert names == REQUIRED | {"building.geojson", "footprint.geojson", "level.geojson", "unit.geojson", "opening.geojson"}
        manifest = json.loads(zf.read("manifest.json"))
        assert manifest["version"] == "1.0.0" and manifest["language"] == "vi"
        assert len(manifest["created"]) == 19 and "+" not in manifest["created"] and not manifest["created"].endswith("Z")
        for n in names - {"manifest.json"}:
            fc = json.loads(zf.read(n))
            assert fc["type"] == "FeatureCollection" and fc["features"]
            ft = n.removesuffix(".geojson")
            for f in fc["features"]:
                assert f["type"] == "Feature" and f["feature_type"] == ft and UUID_V4_RE.match(f["id"])
                assert not any(k.startswith(("osm_", "source_")) for k in f["properties"])
                assert "fid" not in f["properties"]
        venue = json.loads(zf.read("venue.geojson"))
        assert len(venue["features"]) == 1
        vp = venue["features"][0]["properties"]
        assert vp["name"] == {"vi": "Toà nhà mẫu"} and vp["display_point"]["type"] == "Point"
        # feature không geometry
        assert json.loads(zf.read("building.geojson"))["features"][0]["geometry"] is None
        assert json.loads(zf.read("address.geojson"))["features"][0]["geometry"] is None
        lv = json.loads(zf.read("level.geojson"))["features"]
        assert {f["properties"]["ordinal"] for f in lv} == {0, 1} and all(f["properties"]["outdoor"] is False for f in lv)
        assert all(isinstance(f["properties"]["building_ids"], list) for f in lv)
        op = json.loads(zf.read("opening.geojson"))["features"]
        assert all(f["geometry"]["type"] == "LineString" for f in op)


def test_t15_refuses_without_georeference(root, tmp_path):
    from src.config import Project

    p = Project(root / "samples" / "project-dxf.yaml")
    p.georeference = None
    res = pipeline.run(p, allow_unreferenced=True)
    gpkg = tmp_path / "u.gpkg"
    write_gpkg(res.features, gpkg, res.meta)
    with pytest.raises(ImdfExportError, match="georeference"):
        export_imdf(gpkg, tmp_path / "u.zip")
    assert not (tmp_path / "u.zip").exists()


def test_t15_refuses_without_venue(built, tmp_path):
    res = built["dxf"][0]
    feats = {k: v for k, v in res.features.items() if k != "venue"}
    gpkg = tmp_path / "nv.gpkg"
    write_gpkg(feats, gpkg, res.meta)
    with pytest.raises(ImdfExportError, match="venue"):
        export_imdf(gpkg, tmp_path / "nv.zip")


def test_refuses_invalid_gpkg(built, tmp_path):
    res = built["dxf"][0]
    feats = {k: v.copy() for k, v in res.features.items()}
    feats["unit"].loc[feats["unit"].index[0], "level_id"] = "00000000-0000-4000-8000-000000000000"
    gpkg = tmp_path / "bad.gpkg"
    write_gpkg(feats, gpkg, res.meta)
    with pytest.raises(ImdfExportError, match="kiểm tra"):
        export_imdf(gpkg, tmp_path / "bad.zip")


def test_unreferenced_gpkg_uses_srs_minus_one_and_is_readable(root, tmp_path):
    import sqlite3
    import geopandas as gpd
    from src.config import Project

    p = Project(root / "samples" / "project-dxf.yaml")
    p.georeference = None
    res = pipeline.run(p, allow_unreferenced=True)
    gpkg = tmp_path / "local.gpkg"
    write_gpkg(res.features, gpkg, res.meta)
    con = sqlite3.connect(gpkg)
    try:
        assert {r[0] for r in con.execute("select srs_id from gpkg_geometry_columns")} == {-1}
        assert {r[0] for r in con.execute("select srs_id from gpkg_contents where data_type='features'")} == {-1}
        assert con.execute("select count(*) from gpkg_spatial_ref_sys where srs_id not in (-1,0,4326)").fetchone()[0] == 0
    finally:
        con.close()
    g = gpd.read_file(gpkg, layer="unit")
    assert len(g) == 26 and tuple(g.total_bounds) == __import__("pytest").approx((0.0, 0.0, 24.0, 12.0))
    from src.export.validate import check_gpkg
    assert check_gpkg(gpkg).ok          # srs_id -1 được chấp nhận khi crs_source='none'
