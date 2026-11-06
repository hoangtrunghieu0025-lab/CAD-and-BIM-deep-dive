"""TASK-015: cầu thang/thang máy/cột, tường structure, object door, display_point, fixture/detail, khe, IFC2X3."""
import json
import shutil

import geopandas as gpd
import ifcopenshell
import pytest
from shapely.geometry import shape

from src import pipeline
from src.config import Project
from src.export.imdf import export_imdf
from src.export.validate import check_gpkg

EXT = ["ext-ifc", "ext-dxf"]


def _metric(g):
    return g.to_crs(g.estimate_utm_crs())


def _project(root, name, **opts):
    p = Project(root / "samples" / f"project-{name}.yaml")
    p.raw.setdefault("options", {}).update(opts)
    return p


# ------------------------------------------------------------------ (a) cầu thang, thang máy, cột
@pytest.mark.parametrize("kind", EXT)
def test_a_stairs_column_become_units_and_check_passes(built_ext, kind):
    res, gpkg, _ = built_ext[kind]
    u = res.features["unit"]
    assert (u["category"] == "stairs").sum() == 1 and (u["category"] == "column").sum() == 1
    stair = u[u["category"] == "stairs"].iloc[0]
    assert stair["osm_stairs"] == "yes" and stair["osm_indoor"] == "room"
    assert _metric(gpd.GeoSeries([stair.geometry], crs=4326)).area.iloc[0] == pytest.approx(3.8 * 4.8, abs=1e-3)
    assert check_gpkg(gpkg).ok


def test_a_elevator_from_ifc_transport_element(built_ext):
    u = built_ext["ext-ifc"][0].features["unit"]
    e = u[u["category"] == "elevator"].iloc[0]
    assert e["osm_highway"] == "elevator" and e["osm_indoor"] == "room"
    assert json.loads(e["osm_tags"]) == {"area": "yes"}               # area=yes nằm trong osm_tags


def test_a_column_is_carved_out_of_corridor(built_ext):
    u = _metric(built_ext["ext-ifc"][0].features["unit"])
    corridor = u[u["category"] == "walkway"].iloc[0].geometry
    assert corridor.area == pytest.approx(23.8 * 1.8 - 0.4 * 0.4, abs=1e-3)       # cột 0,4 x 0,4 bị trừ khỏi hành lang
    assert len(corridor.interiors) == 1
    assert built_ext["ext-ifc"][0].model.counts["units_carved"] == 1


def test_a_non_elevator_transport_element_is_skipped_with_warning(root, tmp_path):
    f = ifcopenshell.open(str(root / "samples" / "sample-building-extended.ifc"))
    f.by_type("IfcTransportElement")[0].PredefinedType = "ESCALATOR"
    ifc = tmp_path / "esc.ifc"
    f.write(str(ifc))
    p = _project(root, "ext-ifc")
    p.inputs[0]["file"] = str(ifc)
    res = pipeline.run(p)
    assert (res.features["unit"]["category"] == "elevator").sum() == 0
    assert any("ESCALATOR" in w for w in res.model.warnings)


# ------------------------------------------------------------------ (b) tường structure và (f) khe
@pytest.mark.parametrize("kind", EXT)
def test_b_structure_walls_are_one_unit_with_osm_wall_area(built_ext, kind):
    u = built_ext[kind][0].features["unit"]
    s = u[u["category"] == "structure"]
    assert len(s) == 1 and s.iloc[0]["osm_indoor"] == "wall" and json.loads(s.iloc[0]["osm_tags"]) == {"area": "yes"}
    assert _metric(s).area.iloc[0] == pytest.approx(33.52, abs=0.05)


@pytest.mark.parametrize("kind", ["ext-ifc", "ext-dxf"])
def test_f_gap_is_warned_in_simplified_and_closed_in_structure(root, built_ext, kind):
    simple = pipeline.run(_project(root, kind, wall_mode="simplified"))
    gap = next(iter(simple.model.gaps.values()))
    assert gap == pytest.approx(33.52, abs=0.05)
    assert any("khe" in w for w in simple.model.warnings)
    assert (simple.features["unit"]["category"] == "structure").sum() == 0
    full = built_ext[kind][0]
    assert next(iter(full.model.gaps.values())) == pytest.approx(0.0, abs=1e-3)
    assert not any("khe" in w for w in full.model.warnings)


def test_f_legacy_samples_have_no_gap_warning(built):
    for kind in ("dxf", "ifc"):
        res = built[kind][0]
        assert not any("khe" in w for w in res.model.warnings)
        assert all(g == pytest.approx(0.0, abs=1e-3) for g in res.model.gaps.values())


def test_invalid_wall_mode_is_config_error(root):
    from src.config import ConfigError

    with pytest.raises(ConfigError):
        _ = _project(root, "ext-ifc", wall_mode="nonsense").wall_mode


# ------------------------------------------------------------------ mở: cửa chuyển lên ranh giới unit
@pytest.mark.parametrize("kind", EXT)
def test_doors_are_snapped_onto_unit_boundaries(built_ext, kind):
    res, gpkg, _ = built_ext[kind]
    assert res.model.counts["openings_snapped"] == 10
    assert check_gpkg(gpkg).ok            # B-open: mọi opening nằm trên ranh giới unit cùng tầng


def test_ifc_door_centre_sources_cover_all_three_paths(built_ext):
    src = [o.props["center_source"] for o in built_ext["ext-ifc"][0].model.objs if o.type == "door"]
    assert sorted(set(src)) == ["door_body_bbox", "opening_element_geometry", "placement_with_anchor"]
    assert src.count("opening_element_geometry") == 1 and src.count("placement_with_anchor") == 1


def test_ifc_and_dxf_openings_have_same_centres(built_ext):
    def centres(kind):
        g = built_ext[kind][0].features["opening"].geometry
        return sorted((round(x.centroid.x, 8), round(x.centroid.y, 8)) for x in g)
    import numpy as np

    assert np.allclose(centres("ext-ifc"), centres("ext-dxf"), atol=1e-8)


# ------------------------------------------------------------------ (c) object door và display_point
def test_c_door_object_from_ifc_operation_type_and_pset(built_ext):
    o = built_ext["ext-ifc"][0].features["opening"].set_index("source_ref")
    by_name = {}
    res = built_ext["ext-ifc"][0]
    for obj in res.model.objs:
        if obj.type == "door":
            by_name[obj.props["name"]] = json.loads(o.loc[obj.source_ref, "door"])
    assert by_name["Cua P103"] == {"type": "sliding", "automatic": True, "material": None}
    assert by_name["Cua P104"] == {"type": "revolving", "automatic": True, "material": None}
    assert by_name["Cua P106"] == {"type": "swinging", "automatic": False, "material": None}
    assert by_name["Cua P101"]["type"] == "swinging" and by_name["Cua P101"]["automatic"] is None


def test_c_door_object_from_dxf_attributes(built_ext):
    doors = [json.loads(v) for v in built_ext["ext-dxf"][0].features["opening"]["door"].dropna()]
    assert {"type": "sliding", "automatic": True, "material": "glass"} in doors
    assert {"type": "turnstile.fullheight", "automatic": False, "material": "metal"} in doors
    assert len(doors) == 4 and built_ext["ext-dxf"][0].features["opening"]["door"].isna().sum() == 6


def test_c_invalid_door_attributes_are_warned_and_ignored(root, tmp_path):
    import ezdxf

    doc = ezdxf.readfile(str(root / "samples" / "sample-floor-extended.dxf"))
    ins = next(e for e in doc.modelspace().query("INSERT") if e.attribs)
    for a in ins.attribs:
        if a.dxf.tag == "TYPE":
            a.dxf.text = "hinged"                         # không thuộc 9 giá trị door.type
        if a.dxf.tag == "MATERIAL":
            a.dxf.text = "plastic"                        # không thuộc 4 giá trị door.material
    path = tmp_path / "bad.dxf"
    doc.saveas(path)
    p = _project(root, "ext-dxf")
    p.inputs[0]["file"] = str(path)
    res = pipeline.run(p)
    assert any("hinged" in w for w in res.model.warnings) and any("plastic" in w for w in res.model.warnings)
    assert all(json.loads(v)["type"] != "hinged" for v in res.features["opening"]["door"].dropna())


def test_c_pset_door_common_selects_opening_rules(built_ext):
    o = built_ext["ext-ifc"][0].features["opening"]
    assert (o["osm_entrance"] == "yes").sum() == 1 and (o["category"] == "emergencyexit").sum() == 1
    entrance = o[o["osm_entrance"] == "yes"].iloc[0]
    import pandas as pd

    assert entrance["osm_door"] == "yes" and pd.isna(entrance["osm_indoor"])


@pytest.mark.parametrize("kind", EXT)
def test_c_display_point_lies_inside_the_feature(built_ext, kind):
    f = built_ext[kind][0].features
    for table in ("unit", "level"):
        for _, row in f[table].iterrows():
            assert shape(json.loads(row["display_point"])).within(row.geometry) or \
                shape(json.loads(row["display_point"])).intersects(row.geometry)


# ------------------------------------------------------------------ (d) fixture và detail
@pytest.mark.parametrize("kind", EXT)
def test_d_fixture_table(built_ext, kind):
    res, gpkg, _ = built_ext[kind]
    fx = res.features["fixture"]
    assert len(fx) == 3 and set(fx["category"]) == {"furniture"}
    assert set(fx["level_id"]) <= set(res.features["level"]["id"])
    assert fx.geometry.geom_type.eq("Polygon").all()
    assert check_gpkg(gpkg).ok


def test_d_detail_table_from_dxf_only(built_ext):
    d = built_ext["ext-dxf"][0].features["detail"]
    assert len(d) == 3 and d.geometry.geom_type.eq("LineString").all() and set(d.columns) >= {"id", "level_id"}
    assert "detail" not in built_ext["ext-ifc"][0].features


def test_d_fixture_and_detail_are_exported_in_imdf_package(built_ext, tmp_path):
    import zipfile

    z = export_imdf(built_ext["ext-dxf"][1], tmp_path / "e.zip")
    with zipfile.ZipFile(z) as zf:
        assert {"fixture.geojson", "detail.geojson"} <= set(zf.namelist())
        fx = json.loads(zf.read("fixture.geojson"))["features"]
        assert len(fx) == 3 and all(f["feature_type"] == "fixture" for f in fx)
        assert all(f["geometry"]["type"] == "LineString" for f in json.loads(zf.read("detail.geojson"))["features"])
        door = [f["properties"]["door"] for f in json.loads(zf.read("opening.geojson"))["features"] if f["properties"]["door"]]
        assert {"type": "sliding", "automatic": True, "material": "glass"} in door


def test_ifc_windows_are_counted_but_not_exported(built_ext):
    res = built_ext["ext-ifc"][0]
    assert res.model.counts["ifc:IfcWindow"] == 2
    assert not any("window" in str(v).lower() for v in res.features["unit"]["source_class"])


# ------------------------------------------------------------------ IFC2X3
def test_ifc2x3_builds_with_project_georeference(built_ext):
    res, gpkg, _ = built_ext["ifc2x3"]
    assert res.georef.source == "project" and res.model.storeys[0].source_kind == "ifc"
    assert len(res.features["unit"]) == 3 and len(res.features["opening"]) == 2
    assert check_gpkg(gpkg).ok


def test_ifc2x3_without_georeference_is_an_error(root):
    from src.config import DataError

    p = _project(root, "ifc2x3")
    p.georeference = None
    with pytest.raises(DataError, match="georeference"):
        pipeline.run(p)


# ------------------------------------------------------------------ check phải bắt lỗi mới
def _rebuild(built_ext, tmp_path, mutate, kind="ext-dxf"):
    from src.export.gpkg import write_gpkg

    res = built_ext[kind][0]
    feats = {k: v.copy() for k, v in res.features.items()}
    mutate(feats)
    p = tmp_path / "mut.gpkg"
    write_gpkg(feats, p, res.meta)
    return check_gpkg(p)


def test_check_detects_invalid_door_object(built_ext, tmp_path):
    def m(f):
        f["opening"].loc[f["opening"].index[0], "door"] = json.dumps({"type": "hinged", "automatic": "yes", "material": "x"})
    assert "B-door" in _rebuild(built_ext, tmp_path, m).codes()


def test_check_detects_fixture_outside_venue(built_ext, tmp_path):
    from shapely.affinity import translate

    def m(f):
        g = f["fixture"]
        g.loc[g.index[0], "geometry"] = translate(g.geometry.iloc[0], xoff=0.01)       # ~1 km ra ngoài venue
    assert "B-venue" in _rebuild(built_ext, tmp_path, m).codes()
