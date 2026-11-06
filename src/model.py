"""Mô hình trung gian: mọi bước sau `ingest` chỉ làm việc với `Obj` và `Storey`."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shapely.geometry.base import BaseGeometry


@dataclass
class Storey:
    key: str
    name: str                     # nhãn ngắn trên toà nhà (level:ref), vd "1"
    long_name: str
    elevation_m: float | None
    source_kind: str              # dxf | ifc
    source_ref: str
    index: int = 0                # số tầng: 0 = mặt đất; dùng cho OSM `level` và IMDF `ordinal` mặc định
    ordinal: int | None = None
    file_order: int = 0


@dataclass
class Obj:
    type: str                     # space | door | ...
    source_kind: str
    source_ref: str               # IfcGloballyUniqueId, hoặc "file|layer|handle" với DXF; dùng để sinh id ổn định
    source_class: str
    storey_key: str
    geometry: BaseGeometry | None = None   # mét, toạ độ cục bộ
    props: dict[str, Any] = field(default_factory=dict)


@dataclass
class Building:
    name: str | None = None
    ifc_ref: str | None = None


@dataclass
class Model:
    storeys: list[Storey] = field(default_factory=list)
    objs: list[Obj] = field(default_factory=list)
    building: Building = field(default_factory=Building)
    warnings: list[str] = field(default_factory=list)
    unmatched: dict[tuple[str, str], int] = field(default_factory=dict)   # (layer, entity_type) -> số lượng
    counts: dict[str, int] = field(default_factory=dict)
    source_files: list[dict[str, str]] = field(default_factory=list)

    def warn(self, msg: str) -> None:
        if msg not in self.warnings:
            self.warnings.append(msg)

    def count(self, key: str, n: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + n
