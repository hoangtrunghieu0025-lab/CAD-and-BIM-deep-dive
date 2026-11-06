"""Ghi .gpkg, mỗi IMDF feature type một bảng.

Bảng không geometry (`address`, `building`, `_meta`) phải ghi từ DataFrame thường để thành `attributes`;
GeoDataFrame có `geometry=[None]` sẽ thành bảng `features`.
"""
from __future__ import annotations

import json
import sqlite3
import struct
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio

ATTR_TABLES = ("address", "building")
ORDER = ["venue", "address", "building", "footprint", "level", "unit", "opening", "fixture", "detail"]
REQUIRED = {"venue", "address"}


def _uniform_geom_type(g: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, str]:
    types = set(g.geometry.geom_type)
    if types <= {"Polygon"}:
        return g, "Polygon"
    if types <= {"Polygon", "MultiPolygon"}:
        g = g.copy()
        g["geometry"] = [_to_multi(x) for x in g.geometry]
        return g, "MultiPolygon"
    if types <= {"LineString"}:
        return g, "LineString"
    return g, "Unknown"


def _to_multi(p):
    from shapely.geometry import MultiPolygon

    return MultiPolygon([p]) if p.geom_type == "Polygon" else p


def _set_local_srs(path: Path, tables: list[str]) -> None:
    """Không georeference: GDAL ghi SRS tuỳ chỉnh 99999, nhưng cần srs_id = -1 (undefined Cartesian).

    Vá metadata và header GeoPackageBinary của từng geometry (byte 4..8 là srs_id, thứ tự byte theo bit 0 của
    flags). Chỉ làm được khi không có RTree, vì trigger của RTree chặn việc cập nhật cột geometry.
    """
    con = sqlite3.connect(path)
    try:
        for t in tables:
            (gcol,) = con.execute("select column_name from gpkg_geometry_columns where table_name=?", (t,)).fetchone()
            rows = con.execute(f'select rowid, "{gcol}" from "{t}"').fetchall()
            for rid, blob in rows:
                b = bytearray(blob)
                struct.pack_into("<i" if b[3] & 1 else ">i", b, 4, -1)
                con.execute(f'update "{t}" set "{gcol}"=? where rowid=?', (bytes(b), rid))
            con.execute("update gpkg_geometry_columns set srs_id=-1 where table_name=?", (t,))
            con.execute("update gpkg_contents set srs_id=-1 where table_name=?", (t,))
        con.execute("delete from gpkg_spatial_ref_sys where srs_id not in (-1, 0, 4326)")
        con.commit()
    finally:
        con.close()


def write_gpkg(features: dict[str, pd.DataFrame], path: str | Path, meta: dict) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.unlink()
    wrote: list[str] = []
    geo_written: list[str] = []
    unref = meta.get("crs_source") == "none"
    lopts = {"SPATIAL_INDEX": "NO"} if unref else None     # không RTree để còn vá srs_id
    for name in ORDER:
        df = features.get(name)
        if df is None or (len(df) == 0 and name not in REQUIRED):
            continue
        append = p.exists()
        if name in ATTR_TABLES:
            pyogrio.write_dataframe(pd.DataFrame(df), str(p), layer=name, driver="GPKG", append=append)
        else:
            g, gtype = _uniform_geom_type(df)
            pyogrio.write_dataframe(g, str(p), layer=name, driver="GPKG", append=append, geometry_type=gtype,
                                    layer_options=lopts)
            geo_written.append(name)
        wrote.append(name)
    meta_row = {
        "pipeline_version": meta["pipeline_version"], "created": meta["created"],
        "source_files": json.dumps(meta["source_files"], ensure_ascii=False),
        "crs_source": meta["crs_source"],
        "georeference": json.dumps(meta.get("georeference"), ensure_ascii=False),
        "warnings": json.dumps(meta["warnings"], ensure_ascii=False),
    }
    pyogrio.write_dataframe(pd.DataFrame([meta_row]), str(p), layer="_meta", driver="GPKG", append=True)
    if unref:
        _set_local_srs(p, geo_written)
    con = sqlite3.connect(p)
    try:
        for name in wrote:
            con.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS ux_{name}_id ON "{name}"(id)')
        con.commit()
    finally:
        con.close()
    return p
