"""T10–T13 và kiểm tra âm tính (bộ check phải bắt được lỗi)."""
import sqlite3
import subprocess

import geopandas as gpd
import pytest

from src.export.validate import check_gpkg

LAYERS = {"venue", "address", "building", "footprint", "level", "unit", "opening", "_meta"}


@pytest.mark.parametrize("kind", ["dxf", "ifc"])
def test_t10_structure_checks_pass_and_ogrinfo_reads(built, kind):
    gpkg = built[kind][1]
    rep = check_gpkg(gpkg)
    assert rep.ok, [f.message for f in rep.errors]
    out = subprocess.run(["ogrinfo", "-al", "-so", str(gpkg)], capture_output=True, text=True)
    assert out.returncode == 0
    for layer in LAYERS - {"_meta"}:
        assert f"Layer name: {layer}" in out.stdout
    assert 'ID["EPSG",4326]' in out.stdout


@pytest.mark.parametrize("kind", ["dxf", "ifc"])
def test_t11_data_checks_pass(built, kind):
    rep = check_gpkg(built[kind][1])
    assert rep.ok and not rep.codes("warn")
    assert {"B2", "B3", "B4", "B5", "B6", "B-geo", "B-open", "B-venue", "B-lab"} <= set(rep.checked)


def _rebuild(built, tmp_path, mutate, kind="dxf"):
    """Sao chép đối tượng features, áp `mutate(features)` rồi ghi lại bằng write_gpkg và kiểm tra."""
    from src.export.gpkg import write_gpkg

    res = built[kind][0]
    feats = {k: v.copy() for k, v in res.features.items()}
    mutate(feats)
    p = tmp_path / "mut.gpkg"
    write_gpkg(feats, p, res.meta)
    return check_gpkg(p)


def test_t11_broken_foreign_key_is_detected(built, tmp_path):
    def m(f):
        f["unit"].loc[f["unit"].index[0], "level_id"] = "00000000-0000-4000-8000-000000000000"
    assert "B4" in _rebuild(built, tmp_path, m).codes()


def test_overlapping_units_are_detected(built, tmp_path):
    def m(f):
        g = f["unit"]
        g.loc[g.index[0], "geometry"] = g.geometry.iloc[0].buffer(5e-6)      # ~0,5 m: chồng lên unit kề + vượt level
    codes = _rebuild(built, tmp_path, m).codes()
    assert "B-geo" in codes


def test_opening_off_boundary_is_detected(built, tmp_path):
    from shapely.affinity import translate

    def m(f):
        g = f["opening"]
        g.loc[g.index[0], "geometry"] = translate(g.geometry.iloc[0], yoff=2e-5)   # ~2 m khỏi ranh giới
    assert "B-open" in _rebuild(built, tmp_path, m).codes()


def test_missing_venue_is_detected(built, tmp_path):
    def m(f):
        del f["venue"]
    rep = _rebuild(built, tmp_path, m)
    assert "B-pkg" in rep.codes()


def test_bad_category_label_and_id_are_detected(built, tmp_path):
    import json

    def m(f):
        f["unit"].loc[f["unit"].index[0], "category"] = "wall"                         # không có trong từ vựng unit
        f["level"].loc[f["level"].index[0], "name"] = json.dumps({"vi": "Tầng 1"}, ensure_ascii=False)   # lẫn hoa/thường
        f["opening"].loc[f["opening"].index[0], "id"] = "6ba7b810-9dad-51d1-80b4-00c04fd430c8"             # uuid v5
    codes = _rebuild(built, tmp_path, m).codes()
    assert {"B6", "B-lab", "B3"} <= codes


def test_null_required_column_is_detected(built, tmp_path):
    def m(f):
        f["level"].loc[f["level"].index[0], "short_name"] = None
    assert "B5" in _rebuild(built, tmp_path, m).codes()


def test_t12_attribute_tables_have_no_geometry(built):
    con = sqlite3.connect(built["dxf"][1])
    try:
        for t in ("building", "address", "_meta"):
            assert con.execute("select data_type, srs_id from gpkg_contents where table_name=?", (t,)).fetchone() == ("attributes", 0)
            assert con.execute("select count(*) from gpkg_geometry_columns where table_name=?", (t,)).fetchone()[0] == 0
        assert con.execute("select count(*) from gpkg_contents where data_type='features'").fetchone()[0] == 5
    finally:
        con.close()


def test_unique_index_on_id(built):
    con = sqlite3.connect(built["dxf"][1])
    try:
        rows = {r[1] for r in con.execute("select * from sqlite_master where type='index'")}
        assert {"ux_unit_id", "ux_level_id", "ux_venue_id"} <= rows
    finally:
        con.close()


@pytest.mark.parametrize("kind", ["dxf", "ifc"])
def test_t13_geopandas_roundtrip(built, kind):
    gpkg = built[kind][1]
    expect = {"venue": 1, "footprint": 1, "level": 2, "unit": 26, "opening": 24}
    for layer, n in expect.items():
        g = gpd.read_file(gpkg, layer=layer)
        assert len(g) == n and g.crs.to_epsg() == 4326
    import pandas as pd
    import pyogrio
    for layer in ("address", "building"):
        df = pyogrio.read_dataframe(gpkg, layer=layer)
        assert isinstance(df, pd.DataFrame) and not isinstance(df, gpd.GeoDataFrame) and len(df) == 1
