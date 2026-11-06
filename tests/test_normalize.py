"""T7, T8, T17, T18, T20."""
import json
import re
import unicodedata

import pytest

from src import pipeline
from src.config import Project
from src.model import Obj
from src.normalize.features import first_rule
from src.normalize.ids import UUID_V4_RE, short_from_name, stable_v4


@pytest.mark.parametrize("kind", ["dxf", "ifc"])
def test_t7_osm_tags_and_imdf_categories(built, kind):
    f = built[kind][0].features
    unit, op = f["unit"], f["opening"]
    corridor = unit[unit["osm_indoor"] == "corridor"]
    assert len(corridor) == 2 and set(corridor["category"]) == {"walkway"}
    rooms = unit[unit["osm_indoor"] == "room"]
    assert len(rooms) == 24 and set(rooms["category"]) == {"room"}
    assert set(op["osm_indoor"]) == {"door"} and set(op["osm_door"]) == {"yes"} and set(op["category"]) == {"pedestrian"}
    assert unit["osm_level"].isin(["0", "1"]).all() and unit["osm_level_ref"].isin(["1", "2"]).all()


def test_t8_ids_stable_between_runs(root, built):
    second = pipeline.run(Project(root / "samples" / "project-dxf.yaml"))
    for table in ("venue", "level", "unit", "opening", "footprint", "building", "address"):
        assert list(built["dxf"][0].features[table]["id"]) == list(second.features[table]["id"])


def test_ids_change_with_namespace(root):
    p = Project(root / "samples" / "project-dxf.yaml")
    ns = p.tags["defaults"]["ids"]["namespace"]
    assert stable_v4(ns, "x") == stable_v4(ns, "x") != stable_v4("00000000-0000-0000-0000-000000000000", "x")


@pytest.mark.parametrize("kind", ["dxf", "ifc"])
def test_t17_level_labels(built, kind):
    lv = built[kind][0].features["level"].sort_values("ordinal")
    names = [json.loads(v) for v in lv["name"]]
    shorts = [json.loads(v) for v in lv["short_name"]]
    assert names == [{"vi": "TẦNG 1"}, {"vi": "TẦNG 2"}]
    assert shorts == [{"vi": "1"}, {"vi": "2"}]
    for d in names + shorts:
        t = d["vi"]
        assert t == unicodedata.normalize("NFC", t) and t == t.upper()
    assert list(lv["ordinal"]) == [0, 1]


@pytest.mark.parametrize("kind", ["dxf", "ifc"])
def test_t18_all_ids_are_uuid_v4(built, kind):
    for table, df in built[kind][0].features.items():
        for v in df["id"]:
            assert UUID_V4_RE.match(v), (table, v)
    # sanity: không phải uuid5
    assert not UUID_V4_RE.match("6ba7b810-9dad-51d1-80b4-00c04fd430c8")


def _space(name=None, long_name=None, object_type=None):
    return Obj("space", "ifc", "r", "IfcSpace", "k", None,
               {"name": name, "long_name": long_name, "object_type": object_type, "label": name})


@pytest.fixture(scope="module")
def space_rules(root):
    return Project(root / "samples" / "project-dxf.yaml").tags["object_types"]["space"]["rules"]


def test_t20_nfd_corridor_matches_after_nfc(space_rules):
    nfd = unicodedata.normalize("NFD", "Hành lang")
    assert nfd != "Hành lang"
    assert first_rule(space_rules, _space(long_name=nfd))["id"] == "corridor"


def test_t20_keyword_in_middle_is_not_corridor(space_rules):
    assert first_rule(space_rules, _space(long_name="Tuyến hành lang kỹ thuật"))["id"] == "default-room"
    assert first_rule(space_rules, _space(long_name="Hành lang tầng 2"))["id"] == "corridor"
    assert first_rule(space_rules, _space(name="HL100", object_type="Corridor"))["id"] == "corridor"
    assert first_rule(space_rules, _space(long_name="WC nam"))["id"] == "restroom"
    assert first_rule(space_rules, _space(long_name="Phòng họp"))["id"] == "default-room"


@pytest.mark.parametrize("kind", ["dxf", "ifc"])
def test_t20_corridor_has_no_ref(built, kind):
    unit = built[kind][0].features["unit"]
    assert unit[unit["osm_indoor"] == "corridor"]["osm_ref"].isna().all()
    assert unit[unit["osm_indoor"] == "room"]["osm_ref"].notna().all()


def test_short_from_name():
    assert short_from_name("Tầng 1") == "1" and short_from_name("B1") == "B1" and short_from_name("Basement -2") == "-2"
    assert short_from_name("Mái") == "Mái"


def test_storey_short_name_override_from_project(root):
    p = Project(root / "samples" / "project-dxf.yaml")
    p.inputs[0]["storey"]["short_name"] = "G"
    res = pipeline.run(p)
    lv = res.features["level"].sort_values("ordinal")
    assert json.loads(lv["short_name"].iloc[0]) == {"vi": "G"} and lv["osm_level_ref"].iloc[0] == "G"
    assert json.loads(lv["short_name"].iloc[1]) == {"vi": "2"}          # tầng không ghi đè giữ nguyên


def test_manifest_language_default_is_vi_and_matches_labels(built, tmp_path):
    import zipfile
    from src.export.imdf import export_imdf

    z = export_imdf(built["dxf"][1], tmp_path / "m.zip")
    with zipfile.ZipFile(z) as zf:
        lang = json.loads(zf.read("manifest.json"))["language"]
        level = json.loads(zf.read("level.geojson"))["features"][0]["properties"]["name"]
    assert lang == "vi" and lang in level          # LABELS có mục cho ngôn ngữ mặc định của manifest
