"""Đọc IFC và hệ số đơn vị chiều dài."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import ifcopenshell
import ifcopenshell.util.unit

from ..config import DataError


@dataclass
class IfcSource:
    path: Path
    file: "ifcopenshell.file"
    unit_scale: float          # nhân giá trị độ dài thô -> mét (mọi giá trị đọc thủ công phải nhân hệ số này)
    sha256: str

    @property
    def schema(self) -> str:
        return self.file.schema


def load_ifc(path: str | Path) -> IfcSource:
    p = Path(path)
    if not p.is_file():
        raise DataError(f"không thấy file IFC: {p}")
    try:
        f = ifcopenshell.open(str(p))
    except Exception as e:
        raise DataError(f"không đọc được IFC {p.name}: {e}") from e
    try:
        scale = float(ifcopenshell.util.unit.calculate_unit_scale(f))
    except Exception as e:
        raise DataError(f"không xác định được đơn vị chiều dài của {p.name}: {e}") from e
    return IfcSource(p, f, scale, hashlib.sha256(p.read_bytes()).hexdigest())
