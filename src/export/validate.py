"""Kiểm .gpkg: cấu trúc GeoPackage (A) và ràng buộc dữ liệu IMDF (B). Kết quả là `Report`."""
from __future__ import annotations

import json
import sqlite3
import unicodedata
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import pyogrio
from shapely.ops import unary_union

from ..normalize.ids import UUID_V4_RE
from . import imdf_vocab as V

TOL_M = 1e-3          # mét
TOL_AREA = 1e-3       # m²

GEOM_TABLES = ("venue", "footprint", "level", "unit", "opening", "fixture", "detail")
ATTR_TABLES = ("address", "building", "_meta")
EXPECT_GEOM_TYPE = {"venue": {"Polygon", "MultiPolygon"}, "footprint": {"Polygon", "MultiPolygon"},
                    "level": {"Polygon", "MultiPolygon"}, "unit": {"Polygon", "MultiPolygon"},
                    "fixture": {"Polygon", "MultiPolygon"}, "opening": {"LineString"},
                    "detail": {"LineString", "MultiLineString"}}
REQUIRED_COLS = {
    "venue": ["category", "name", "display_point", "address_id"],
    "address": ["address", "locality", "country"],
    "building": ["category"],
    "footprint": ["category", "building_ids"],
    "level": ["category", "outdoor", "ordinal", "name", "short_name"],
    "unit": ["category", "level_id"],
    "opening": ["category", "level_id"],
    "fixture": ["category", "level_id"],
    "detail": ["level_id"],
}
CATEGORY_VOCAB = {"unit": V.UNIT, "opening": V.OPENING, "level": V.LEVEL, "building": V.BUILDING,
                  "footprint": V.FOOTPRINT, "venue": V.VENUE, "fixture": V.FIXTURE}


@dataclass
class Finding:
    level: str
    code: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)

    def error(self, code: str, msg: str) -> None:
        self.findings.append(Finding("error", code, msg))

    def warn(self, code: str, msg: str) -> None:
        self.findings.append(Finding("warn", code, msg))

    def passed(self, code: str) -> None:
        self.checked.append(code)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def codes(self, level: str = "error") -> set[str]:
        return {f.code for f in self.findings if f.level == level}


def _jload(v: Any) -> Any:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    return json.loads(v) if isinstance(v, str) else v


def _null(v: Any) -> bool:
    return v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and v == "")


def check_structure(path: Path, rep: Report) -> dict[str, str]:
    """Trả {bảng: data_type}."""
    con = sqlite3.connect(path)

    def q(sql: str):
        return con.execute(sql).fetchall()

    try:
        if q("PRAGMA application_id")[0][0] != 0x47504B47:
            rep.error("A1", "application_id khác 0x47504B47")
        else:
            rep.passed("A1")
        if q("PRAGMA user_version")[0][0] < 10200:
            rep.error("A2", "user_version < 10200")
        else:
            rep.passed("A2")
        srs = {r[0] for r in q("select srs_id from gpkg_spatial_ref_sys")}
        if not {-1, 0, 4326} <= srs:
            rep.error("A3", f"gpkg_spatial_ref_sys thiếu dòng bắt buộc (có {sorted(srs)})")
        else:
            rep.passed("A3")
        contents = {r[0]: (r[1], r[2]) for r in q("select table_name, data_type, srs_id from gpkg_contents")}
        gcols = {r[0]: (r[1], r[2], r[3]) for r in q(
            "select table_name, column_name, geometry_type_name, srs_id from gpkg_geometry_columns")}
        bad = False
        for t, (dt_, srs_id) in contents.items():
            want = "attributes" if t in ATTR_TABLES else "features"
            if dt_ != want:
                rep.error("A4", f"bảng {t}: data_type={dt_}, cần {want}")
                bad = True
            if want == "attributes" and t in gcols:
                rep.error("A5", f"bảng attributes {t} lại có dòng trong gpkg_geometry_columns")
                bad = True
            if want == "features" and t not in gcols:
                rep.error("A5", f"bảng features {t} thiếu dòng trong gpkg_geometry_columns")
                bad = True
        if not bad:
            rep.passed("A4"); rep.passed("A5")
        if q("PRAGMA integrity_check")[0][0] != "ok":
            rep.error("A6", "PRAGMA integrity_check không ok")
        else:
            rep.passed("A6")
        if q("PRAGMA foreign_key_check"):
            rep.error("A7", "PRAGMA foreign_key_check không rỗng")
        else:
            rep.passed("A7")
        crs_none = False
        if "_meta" in contents:
            r = q("select crs_source from _meta")
            crs_none = bool(r) and r[0][0] == "none"
        for t, (_, _, srs_id) in gcols.items():
            if srs_id != 4326 and not crs_none:
                rep.error("B1", f"bảng {t}: srs_id={srs_id}, cần 4326")
        return {t: v[0] for t, v in contents.items()}
    finally:
        con.close()


def check_data(path: Path, tables: dict[str, str], rep: Report, language: str = "vi") -> dict[str, pd.DataFrame]:
    dfs: dict[str, pd.DataFrame] = {}
    for t in tables:
        if t == "_meta":
            continue
        dfs[t] = pyogrio.read_dataframe(str(path), layer=t)
    for must in ("venue", "address"):
        if must not in dfs or len(dfs[must]) == 0:
            rep.error("B-pkg", f"thiếu bảng/dòng bắt buộc `{must}`")
    if "venue" in dfs and len(dfs["venue"]) != 1:
        rep.error("B-pkg", f"venue phải có đúng 1 dòng (có {len(dfs['venue'])})")

    all_ids: dict[str, str] = {}
    for t, df in dfs.items():
        if "id" not in df:
            rep.error("B3", f"{t}: thiếu cột id")
            continue
        for _id in df["id"]:
            if not isinstance(_id, str) or not UUID_V4_RE.match(_id):
                rep.error("B3", f"{t}: id không phải UUID v4: {_id!r}")
            elif _id in all_ids:
                rep.error("B3", f"id trùng giữa {t} và {all_ids[_id]}: {_id}")
            else:
                all_ids[_id] = t
        if "feature_type" in df and not (df["feature_type"] == t).all():
            rep.error("B3", f"{t}: feature_type không khớp tên bảng")
    rep.passed("B3")

    for t in GEOM_TABLES:
        if t not in dfs:
            continue
        g = dfs[t]
        for i, geom in enumerate(g.geometry):
            if geom is None or geom.is_empty:
                rep.error("B2", f"{t}[{i}]: hình học rỗng")
            elif not geom.is_valid:
                rep.error("B2", f"{t}[{i}]: hình học không hợp lệ")
            elif geom.geom_type not in EXPECT_GEOM_TYPE[t]:
                rep.error("B2", f"{t}[{i}]: kiểu {geom.geom_type}, cần {sorted(EXPECT_GEOM_TYPE[t])}")
    rep.passed("B2")

    for t, cols in REQUIRED_COLS.items():
        if t not in dfs:
            continue
        for c in cols:
            if c not in dfs[t]:
                rep.error("B5", f"{t}: thiếu cột bắt buộc {c}")
            elif any(_null(v) for v in dfs[t][c]):
                rep.error("B5", f"{t}.{c}: có giá trị null (bắt buộc)")
    rep.passed("B5")

    for t, vocab in CATEGORY_VOCAB.items():
        if t in dfs and "category" in dfs[t]:
            for v in dfs[t]["category"].dropna().unique():
                if v not in vocab:
                    rep.error("B6", f"{t}.category='{v}' không thuộc từ vựng IMDF")
    rep.passed("B6")

    for t, cols in {"venue": ["name"], "level": ["name", "short_name"], "unit": ["name"], "building": ["name"]}.items():
        if t not in dfs:
            continue
        for c in cols:
            for v in dfs[t][c].dropna():
                try:
                    lab = _jload(v)
                except json.JSONDecodeError:
                    rep.error("B-lab", f"{t}.{c}: không phải JSON")
                    continue
                if not isinstance(lab, dict) or language not in lab or not all(isinstance(x, str) for x in lab.values()):
                    rep.error("B-lab", f"{t}.{c}: LABELS phải là object có khoá '{language}': {v}")
                elif t == "level":
                    txt = lab[language]
                    if txt != unicodedata.normalize("NFC", txt) or txt != txt.upper():
                        rep.error("B-lab", f"level.{c} không phải chữ hoa NFC: {txt!r}")
    rep.passed("B-lab")

    if "opening" in dfs and "door" in dfs["opening"]:
        for v in dfs["opening"]["door"].dropna():
            d = json.loads(v)
            if (d.get("type") not in (None, *V.DOOR_TYPE) or d.get("material") not in (None, *V.DOOR_MATERIAL)
                    or d.get("automatic") not in (None, True, False)):
                rep.error("B-door", f"opening.door không hợp lệ theo IMDF: {v}")
    rep.passed("B-door")

    ids = {t: set(df["id"]) for t, df in dfs.items() if "id" in df}
    def fk(table: str, col: str, target: str, is_list: bool = False) -> None:
        if table not in dfs or col not in dfs[table]:
            return
        for v in dfs[table][col]:
            if _null(v):
                continue
            refs = _jload(v) if is_list else [v]
            for r in refs:
                if r not in ids.get(target, set()):
                    rep.error("B4", f"{table}.{col} → {target}: id không tồn tại ({r})")
    fk("unit", "level_id", "level"); fk("opening", "level_id", "level")
    fk("fixture", "level_id", "level"); fk("detail", "level_id", "level")
    fk("level", "building_ids", "building", True); fk("footprint", "building_ids", "building", True)
    fk("venue", "address_id", "address"); fk("building", "address_id", "address")
    rep.passed("B4")

    geoms = {t: dfs[t] for t in ("venue", "footprint", "level", "unit", "opening", "fixture", "detail")
             if t in dfs and len(dfs[t])}
    if {"venue", "level", "unit"} <= set(geoms):
        _spatial(geoms, rep)
    return dfs


def _to_metric(g: gpd.GeoDataFrame, crs) -> gpd.GeoDataFrame:
    """4326 -> UTM để đo khoảng cách và diện tích theo mét."""
    if g.crs is not None and g.crs.is_geographic:
        return g.to_crs(crs)
    return g


def _spatial(geoms: dict[str, gpd.GeoDataFrame], rep: Report) -> None:
    ref = geoms["venue"]
    metric = ref.estimate_utm_crs() if ref.crs is not None and ref.crs.is_geographic else None
    m = {t: (_to_metric(g, metric) if metric is not None else g) for t, g in geoms.items()}
    level, unit = m["level"], m["unit"]
    level_geom = dict(zip(level["id"], level.geometry))
    for lid, lg in level_geom.items():
        us = unit[unit["level_id"] == lid]
        if len(us) == 0:
            rep.error("B-geo", f"level {lid} không có unit")
            continue
        ug = list(us.geometry)
        if not all(u.within(lg.buffer(TOL_M)) for u in ug):
            rep.error("B-geo", f"level {lid}: có unit nằm ngoài level")
        ov = sum(a.intersection(b).area for a, b in combinations(ug, 2))
        if ov > TOL_AREA:
            rep.error("B-geo", f"level {lid}: các unit chồng lấn {ov:.4f} m²")
        sd = unary_union(ug).symmetric_difference(lg).area
        if sd > TOL_AREA:
            rep.error("B-geo", f"level {lid}: hợp unit khác level (symmetric difference {sd:.4f} m²)")
        holes = sum(len(p.interiors) for p in getattr(lg, "geoms", [lg]))
        if holes:
            rep.warn("B-geo", f"level {lid}: có {holes} lỗ/khe bên trong (kiểm tra khe giữa các unit)")
    rep.passed("B-geo")
    if "opening" in m:
        for _, row in m["opening"].iterrows():
            g = row.geometry
            if g.geom_type != "LineString" or len(g.coords) < 2:
                rep.error("B-open", f"opening {row['id']}: không phải LineString một phần")
                continue
            us = unit[unit["level_id"] == row["level_id"]]
            bnd = unary_union([u.boundary for u in us.geometry]) if len(us) else None
            if bnd is None or not bnd.buffer(TOL_M).covers(g):
                rep.error("B-open", f"opening {row['id']}: không nằm trên ranh giới unit cùng tầng")
    rep.passed("B-open")
    vg = m["venue"].geometry.iloc[0].buffer(TOL_M)
    for t in ("footprint", "level", "unit", "opening", "fixture", "detail"):
        if t in m and not all(vg.covers(g) for g in m[t].geometry):
            rep.error("B-venue", f"có feature `{t}` nằm ngoài venue")
    rep.passed("B-venue")


def check_gpkg(path: str | Path, language: str = "vi") -> Report:
    p = Path(path)
    rep = Report()
    if not p.is_file():
        rep.error("A0", f"không thấy file {p}")
        return rep
    tables = check_structure(p, rep)
    check_data(p, tables, rep, language)
    return rep
