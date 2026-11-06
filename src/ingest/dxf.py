"""Ingest DXF (spec 4.1): ezdxf.readfile, thất bại -> ezdxf.recover.readfile; chuẩn hoá đơn vị về mét."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import ezdxf
from ezdxf import recover, units as ezunits

from ..config import DataError

_UNIT_TO_M = {
    ezunits.M: 1.0,
    ezunits.MM: 1e-3,
    ezunits.CM: 1e-2,
    ezunits.KM: 1e3,
}


@dataclass
class DxfSource:
    path: Path
    doc: "ezdxf.document.Drawing"
    factor: float                      # nhân toạ độ DXF -> mét
    sha256: str
    warnings: list[str] = field(default_factory=list)

    @property
    def msp(self):
        return self.doc.modelspace()


def to_metres(value: float, unit_code: int, fallback_unit: str = "m") -> float:
    """Đổi độ dài sang mét. Mã đơn vị không hỗ trợ (0 unitless, 8, 9, 21-24, ...) -> dùng fallback_unit."""
    f = unit_factor(unit_code, fallback_unit)[0]
    return value * f


def unit_factor(unit_code: int, fallback_unit: str = "m") -> tuple[float, str | None]:
    """Trả (hệ số -> mét, cảnh báo|None)."""
    if unit_code in _UNIT_TO_M:
        return _UNIT_TO_M[unit_code], None
    try:  # inch, foot, ... mà ezdxf biết quy đổi
        return float(ezunits.conversion_factor(unit_code, ezunits.M)), None
    except (TypeError, ValueError, KeyError):
        pass
    fb = {"m": 1.0, "mm": 1e-3, "cm": 1e-2, "km": 1e3}.get(fallback_unit)
    if fb is None:
        raise DataError(f"units.fallback_unit '{fallback_unit}' không hỗ trợ")
    return fb, (
        f"$INSUNITS={unit_code} không quy đổi được (unitless/không hỗ trợ): dùng fallback_unit='{fallback_unit}'"
    )


def load_dxf(path: str | Path, fallback_unit: str = "m") -> DxfSource:
    p = Path(path)
    if not p.is_file():
        raise DataError(f"không thấy file DXF: {p}")
    warnings: list[str] = []
    try:
        doc = ezdxf.readfile(str(p))
    except (IOError, ezdxf.DXFStructureError, UnicodeDecodeError):
        try:
            doc, auditor = recover.readfile(str(p))
        except Exception as e:  # noqa: BLE001
            raise DataError(f"không đọc được DXF {p.name}: {e}") from e
        warnings.append(f"{p.name}: đọc bằng ezdxf.recover ({len(auditor.errors)} lỗi, {len(auditor.fixes)} sửa)")
    factor, w = unit_factor(doc.units, fallback_unit)
    if w:
        warnings.append(f"{p.name}: {w}")
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    return DxfSource(path=p, doc=doc, factor=factor, sha256=sha, warnings=warnings)
