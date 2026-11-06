"""Georeference: toạ độ cục bộ (mét) -> EPSG:4326.

Thứ tự ưu tiên: IfcMapConversion (IFC4+), `georeference` trong project.yaml (gốc + góc quay + tỉ lệ, hoặc
control points), IfcSite (dự phòng, kèm cảnh báo); không có nguồn nào thì lỗi, trừ khi dùng `--allow-unreferenced`.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

import numpy as np
import shapely
from pyproj import Transformer
from shapely.affinity import affine_transform
from shapely.geometry.base import BaseGeometry

from ..config import DataError
from ..model import Model


@dataclass
class Georef:
    source: str                         # ifc_map_conversion | project | ifc_site | none
    crs: str | None = None              # None = chưa georeference
    e0: float = 0.0
    n0: float = 0.0
    rotation_deg: float = 0.0           # góc quay CCW so với trục Đông (a' = cosθ, b' = sinθ)
    scale: float = 1.0
    residual_m: float | None = None     # control points: sai số lớn nhất của phép khớp (m)

    @property
    def referenced(self) -> bool:
        return self.crs is not None

    def to_projected(self, geom: BaseGeometry) -> BaseGeometry:
        a = self.scale * math.cos(math.radians(self.rotation_deg))
        b = self.scale * math.sin(math.radians(self.rotation_deg))
        # E = a·x − b·y + E0 ; N = b·x + a·y + N0
        return affine_transform(geom, [a, -b, b, a, self.e0, self.n0])

    def to_wgs84(self, geom: BaseGeometry) -> BaseGeometry:
        if not self.referenced:
            return geom
        proj = self.to_projected(geom)
        tr = Transformer.from_crs(self.crs, "EPSG:4326", always_xy=True)
        return shapely.transform(proj, lambda c: np.column_stack(tr.transform(c[:, 0], c[:, 1])))

    def describe(self) -> dict[str, Any]:
        return {"source": self.source, "crs": self.crs, "e0": self.e0, "n0": self.n0,
                "rotation_deg": self.rotation_deg, "scale": self.scale, "residual_m": self.residual_m}


NONE = Georef("none")


def from_control_points(cfg: dict[str, Any]) -> Georef:
    """Phép đồng dạng (tịnh tiến + quay + tỉ lệ) khớp bình phương tối thiểu từ >= 2 cặp điểm local <-> thế giới.

    Dùng số phức: world = a·local + b, với a = scale·e^{iθ}. `control_points: [{local: [x, y], world: [E, N]}, ...]`.
    """
    if "crs" not in cfg:
        raise DataError("georeference trong project.yaml thiếu `crs`")
    pts = cfg["control_points"]
    if not isinstance(pts, list) or len(pts) < 2:
        raise DataError("control_points cần ít nhất 2 cặp điểm")
    try:
        z = np.array([complex(float(p["local"][0]), float(p["local"][1])) for p in pts])
        w = np.array([complex(float(p["world"][0]), float(p["world"][1])) for p in pts])
    except (KeyError, TypeError, ValueError, IndexError) as e:
        raise DataError(f"control_points không hợp lệ (cần local: [x, y] và world: [E, N]): {e}") from e
    dz = z - z.mean()
    denom = float((np.abs(dz) ** 2).sum())
    if denom < 1e-12:
        raise DataError("control_points: các điểm local trùng nhau")
    a = (np.conj(dz) * (w - w.mean())).sum() / denom
    b = w.mean() - a * z.mean()
    if abs(a) < 1e-12:
        raise DataError("control_points: các điểm world trùng nhau")
    residual = float(np.abs(a * z + b - w).max())
    return Georef("control_points", str(cfg["crs"]), float(b.real), float(b.imag),
                  float(np.degrees(np.angle(a))), float(abs(a)), residual)


def from_project(cfg: dict[str, Any]) -> Georef:
    if cfg.get("control_points"):
        return from_control_points(cfg)
    for k in ("crs", "origin"):
        if k not in cfg:
            raise DataError(f"georeference trong project.yaml thiếu `{k}`")
    try:
        origin = cfg["origin"]
        return Georef("project", str(cfg["crs"]), float(origin[0]), float(origin[1]),
                      float(cfg.get("rotation_deg", 0.0)), float(cfg.get("scale", 1.0)))
    except (TypeError, ValueError, IndexError) as e:
        raise DataError(f"georeference trong project.yaml không hợp lệ: {e}") from e


_MAP_UNIT = {None: 1.0, "": 1.0, "MILLI": 1e-3, "CENTI": 1e-2, "KILO": 1e3}


def from_ifc_map_conversion(ifc_file, unit_scale: float, model: Model, fname: str) -> Georef | None:
    """IfcMapConversion + IfcProjectedCRS (IFC4+). (a', b') là XAxisAbscissa/Ordinate đã CHUẨN HOÁ (đã xác minh)."""
    mcs = ifc_file.by_type("IfcMapConversion") if ifc_file.schema != "IFC2X3" else []
    if not mcs:
        return None
    mc = mcs[0]
    crs_el = mc.TargetCRS
    name = getattr(crs_el, "Name", None) or ""
    m = re.search(r"EPSG:(\d+)", name, re.I)
    if not m:
        model.warn(f"{fname}: IfcProjectedCRS.Name '{name}' không có dạng EPSG:xxxx; bỏ qua IfcMapConversion")
        return None
    a = mc.XAxisAbscissa if mc.XAxisAbscissa is not None else 1.0
    b = mc.XAxisOrdinate if mc.XAxisOrdinate is not None else 0.0
    n = math.hypot(a, b) or 1.0
    rot = math.degrees(math.atan2(b / n, a / n))
    map_unit = getattr(crs_el, "MapUnit", None)
    mu = 1.0
    if map_unit is not None:
        if map_unit.is_a("IfcSIUnit") and map_unit.Name == "METRE":
            mu = _MAP_UNIT.get(map_unit.Prefix, 1.0)
        else:
            model.warn(f"{fname}: MapUnit không phải mét SI; giả định mét")
    return Georef("ifc_map_conversion", f"EPSG:{m.group(1)}", float(mc.Eastings) * mu, float(mc.Northings) * mu,
                  rot, float(mc.Scale) if mc.Scale is not None else 1.0)


def from_ifc_site(ifc_file, model: Model, fname: str) -> Georef | None:
    sites = ifc_file.by_type("IfcSite")
    if not sites or sites[0].RefLatitude is None or sites[0].RefLongitude is None:
        return None

    def dms(v):
        d, m, s = (list(v) + [0, 0, 0])[:3]
        mic = v[3] if len(v) > 3 else 0
        sign = -1 if d < 0 or m < 0 or s < 0 else 1
        return sign * (abs(d) + abs(m) / 60 + (abs(s) + abs(mic) / 1e6) / 3600)

    lat, lon = dms(sites[0].RefLatitude), dms(sites[0].RefLongitude)
    zone = int((lon + 180) // 6) + 1
    epsg = (32600 if lat >= 0 else 32700) + zone
    e0, n0 = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True).transform(lon, lat)
    model.warn(f"{fname}: georeference dự phòng từ IfcSite.RefLatitude/RefLongitude (độ chính xác thấp, không có hướng)")
    return Georef("ifc_site", f"EPSG:{epsg}", e0, n0, 0.0, 1.0)


def resolve(project_cfg: dict[str, Any] | None, ifc_georef: Georef | None, ifc_site: Georef | None,
            allow_unreferenced: bool, model: Model) -> Georef:
    if ifc_georef is not None:
        return ifc_georef
    if project_cfg:
        g = from_project(project_cfg)
        if g.residual_m is not None and g.residual_m > 0.1:
            model.warn(f"control points: sai số khớp lớn nhất {g.residual_m:.3f} m (> 0,1 m); kiểm tra lại các điểm")
        return g
    if ifc_site is not None:
        return ifc_site
    if allow_unreferenced:
        model.warn("không có georeference: ghi toạ độ cục bộ (--allow-unreferenced); crs_source='none'")
        return NONE
    raise DataError(
        "không có nguồn georeference (IfcMapConversion, `georeference` trong project.yaml, IfcSite); "
        "thêm cấu hình hoặc dùng --allow-unreferenced"
    )
