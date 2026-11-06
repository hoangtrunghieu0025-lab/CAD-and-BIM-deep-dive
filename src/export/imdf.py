"""Xuất .gpkg thành gói IMDF (`manifest.json` + `*.geojson`, nén zip).

Bắt buộc có `manifest.json`, `address.geojson` và `venue.geojson` (đúng một Venue).
"""
from __future__ import annotations

import datetime as dt
import json
import sqlite3
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd
import pyogrio
from shapely.geometry import mapping

from ..config import DataError
from .validate import GEOM_TABLES, check_gpkg

JSON_COLS = {"name", "alt_name", "short_name", "building_ids", "level_ids", "parents", "accessibility",
             "access_control", "door", "display_point"}
BOOL_COLS = {"outdoor"}
INT_COLS = {"ordinal"}
DROP_PREFIX = ("osm_", "source_")
DROP_COLS = {"fid", "id", "feature_type", "geometry"}
FEATURE_FILES = ["address", "venue", "building", "footprint", "level", "unit", "opening", "fixture", "detail"]


class ImdfExportError(DataError):
    """Từ chối xuất gói IMDF (thiếu venue/address, không georeference, hoặc dữ liệu vi phạm ràng buộc)."""


def _clean(v: Any) -> Any:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if hasattr(v, "item"):
        v = v.item()
    return v


def _props(row: pd.Series, cols: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for c in cols:
        v = _clean(row[c])
        if v is None:
            out[c] = None
        elif c in JSON_COLS and isinstance(v, str):
            out[c] = json.loads(v)
        elif c in BOOL_COLS:
            out[c] = bool(v)
        elif c in INT_COLS:
            out[c] = int(v)
        else:
            out[c] = v
    return out


def _feature_collection(df: pd.DataFrame, table: str) -> dict[str, Any]:
    cols = [c for c in df.columns if c not in DROP_COLS and not c.startswith(DROP_PREFIX)]
    feats = []
    has_geom = table in GEOM_TABLES
    for _, row in df.iterrows():
        geom = None
        if has_geom:
            g = row["geometry"]
            geom = None if g is None or g.is_empty else mapping(g)
        feats.append({"id": row["id"], "type": "Feature", "feature_type": table, "geometry": geom,
                      "properties": _props(row, cols)})
    return {"type": "FeatureCollection", "features": feats}


def export_imdf(gpkg: str | Path, zip_path: str | Path, language: str = "vi",
                generated_by: str = "cad-and-BIM-deep-dive") -> Path:
    p = Path(gpkg)
    con = sqlite3.connect(p)
    try:
        tables = {r[0] for r in con.execute("select table_name from gpkg_contents")}
        meta = con.execute("select crs_source from _meta").fetchone() if "_meta" in tables else None
    finally:
        con.close()
    for must in ("venue", "address"):
        if must not in tables:
            raise ImdfExportError(f"thiếu bảng bắt buộc `{must}`")
    if meta and meta[0] == "none":
        raise ImdfExportError("GPKG không có georeference (crs_source='none'): không xuất gói IMDF")
    rep = check_gpkg(p, language=language.split("-")[0])
    if not rep.ok:
        raise ImdfExportError("GPKG không đạt kiểm tra hợp lệ: " + "; ".join(f.message for f in rep.errors[:5]))

    zp = Path(zip_path)
    zp.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"version": "1.0.0", "created": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                "language": language, "generated_by": generated_by, "extensions": None}
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for t in FEATURE_FILES:
            if t not in tables:
                continue
            df = pyogrio.read_dataframe(str(p), layer=t)
            if len(df) == 0 and t not in ("venue", "address"):
                continue
            if t == "venue" and len(df) != 1:
                raise ImdfExportError("venue.geojson phải chứa đúng một Venue")
            z.writestr(f"{t}.geojson", json.dumps(_feature_collection(df, t), ensure_ascii=False))
    return zp
