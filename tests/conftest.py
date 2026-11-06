"""Fixture dùng chung: dựng hai dự án mẫu (DXF, IFC) một lần cho cả phiên test."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import pipeline  # noqa: E402
from src.config import Project  # noqa: E402
from src.export.gpkg import write_gpkg  # noqa: E402

SAMPLES = ROOT / "samples"


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    """{'dxf'|'ifc': (BuildResult, Path gpkg)}"""
    out = {}
    base = tmp_path_factory.mktemp("built")
    for kind in ("dxf", "ifc"):
        project = Project(SAMPLES / f"project-{kind}.yaml")
        res = pipeline.run(project)
        gpkg = base / f"{kind}.gpkg"
        write_gpkg(res.features, gpkg, res.meta)
        out[kind] = (res, gpkg, project)
    return out
