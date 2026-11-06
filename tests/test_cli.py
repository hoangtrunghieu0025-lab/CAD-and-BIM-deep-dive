"""Giao diện dòng lệnh và mã thoát (spec mục 3)."""
import csv
import json
import subprocess
import sys

import pytest


def run(root, *args):
    return subprocess.run([sys.executable, "-m", "src.cli", *args], cwd=root, capture_output=True, text=True)


def test_build_check_imdf_exit_zero_and_reports(root, tmp_path):
    gpkg = tmp_path / "o" / "b.gpkg"
    r = run(root, "build", "--project", "samples/project-dxf.yaml", "--out", str(gpkg))
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "o" / "unmatched_layers.csv").exists()
    rep = json.loads((tmp_path / "o" / "build_report.json").read_text(encoding="utf-8"))
    assert rep["tables"]["unit"] == 26 and rep["counts"]["spaces"] == 26 and rep["unmatched"] == []
    rows = list(csv.reader((tmp_path / "o" / "unmatched_layers.csv").open(encoding="utf-8")))
    assert rows == [["layer", "entity_type", "count"]]
    assert run(root, "check", str(gpkg)).returncode == 0
    z = tmp_path / "o" / "b.imdf.zip"
    assert run(root, "imdf", str(gpkg), "--out", str(z)).returncode == 0 and z.exists()


def test_exit_code_2_on_config_errors(root, tmp_path):
    assert run(root, "build", "--project", str(tmp_path / "none.yaml"), "--out", str(tmp_path / "x.gpkg")).returncode == 2
    bad = tmp_path / "p.yaml"
    bad.write_text("name: x\n", encoding="utf-8")
    assert run(root, "build", "--project", str(bad), "--out", str(tmp_path / "x.gpkg")).returncode == 2


def test_exit_code_1_on_data_errors(root, tmp_path):
    src = (root / "samples" / "project-dxf.yaml").read_text(encoding="utf-8")
    no_geo = tmp_path / "nogeo.yaml"
    # bỏ khối georeference, giữ đường dẫn tuyệt đối tới mapping và mẫu
    lines, skip = [], False
    for ln in src.splitlines():
        if ln.startswith("georeference:"):
            skip = True
            continue
        if skip and ln.startswith(" "):
            continue
        skip = False
        lines.append(ln)
    text = "\n".join(lines).replace("../config", str(root / "config")).replace("file: sample-", f"file: {root}/samples/sample-")
    no_geo.write_text(text, encoding="utf-8")
    r = run(root, "build", "--project", str(no_geo), "--out", str(tmp_path / "x.gpkg"))
    assert r.returncode == 1 and "georeference" in r.stderr
    ok = run(root, "build", "--project", str(no_geo), "--out", str(tmp_path / "y.gpkg"), "--allow-unreferenced")
    assert ok.returncode == 0
    assert run(root, "imdf", str(tmp_path / "y.gpkg"), "--out", str(tmp_path / "y.zip")).returncode == 1   # từ chối


def test_check_fails_with_exit_1_on_missing_file(root, tmp_path):
    assert run(root, "check", str(tmp_path / "nope.gpkg")).returncode == 1


def test_missing_venue_category_is_config_error(root, tmp_path):
    src = (root / "samples" / "project-dxf.yaml").read_text(encoding="utf-8").replace("category: businesscampus", "category: nonsense")
    p = tmp_path / "v.yaml"
    p.write_text(src.replace("../config", str(root / "config")).replace("file: sample-", f"file: {root}/samples/sample-"), encoding="utf-8")
    r = run(root, "build", "--project", str(p), "--out", str(tmp_path / "x.gpkg"))
    assert r.returncode == 2 and "venue.category" in r.stderr
