"""Điều phối ingest -> cad2bim/extract -> georeference -> normalize (spec mục 2)."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

import pandas as pd

from . import cad2bim
from .config import DataError, Project
from .extract import georef as gr
from .extract import ifc as ifc_extract
from .ingest.dxf import load_dxf
from .ingest.ifc import load_ifc
from .model import Model, Storey
from .normalize.features import to_features

PIPELINE_VERSION = "0.1.0"


@dataclass
class BuildResult:
    features: dict[str, pd.DataFrame]
    model: Model
    georef: gr.Georef
    meta: dict[str, Any]


def run(project: Project, allow_unreferenced: bool = False) -> BuildResult:
    project.validate_required()
    model = Model()
    ifc_georef: gr.Georef | None = None
    ifc_site: gr.Georef | None = None
    fallback_unit = project.layers.get("units", {}).get("fallback_unit", "m")
    door_cfg = project.tags["object_types"]["door"]["geometry_source"]

    for order, inp in enumerate(project.inputs):
        path = project.input_path(inp)
        if inp["kind"] == "dxf":
            src = load_dxf(path, fallback_unit)
            for w in src.warnings:
                model.warn(w)
            s = inp["storey"]
            if "name" not in s or "elevation_m" not in s:
                raise DataError(f"inputs[{order}].storey cần `name` và `elevation_m`")
            storey = Storey(
                key=f"dxf:{path.name}", name=str(s["name"]), long_name=str(s.get("long_name") or s["name"]),
                elevation_m=float(s["elevation_m"]), source_kind="dxf", source_ref=f"dxf-storey|{path.name}",
                ordinal=s.get("ordinal"), file_order=order * 1000,
            )
            model.storeys.append(storey)
            cad2bim.build(src, storey, project.layers, project.tags, model)
            model.source_files.append({"file": path.name, "kind": "dxf", "sha256": src.sha256})
        else:
            src = load_ifc(path)
            ifc_extract.extract(src, model, door_cfg, order)
            model.source_files.append({"file": path.name, "kind": "ifc", "schema": src.schema, "sha256": src.sha256})
            if ifc_georef is None:
                ifc_georef = gr.from_ifc_map_conversion(src.file, src.unit_scale, model, path.name)
            if ifc_site is None:
                ifc_site = gr.from_ifc_site(src.file, model, path.name)

    geo = gr.resolve(project.georeference, ifc_georef, ifc_site, allow_unreferenced, model)
    features = to_features(model, project, geo)
    meta = {
        "pipeline_version": PIPELINE_VERSION,
        "created": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "source_files": model.source_files,
        "crs_source": geo.source if geo.referenced else "none",
        "georeference": geo.describe(),
        "warnings": model.warnings,
    }
    return BuildResult(features, model, geo, meta)
