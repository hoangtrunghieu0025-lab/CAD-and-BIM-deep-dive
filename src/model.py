"""Mô hình trung gian (spec mục 2): mọi bước sau `ingest` chỉ làm việc với `Obj` / `Storey`."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shapely.geometry.base import BaseGeometry


@dataclass
class Storey:
    key: str                      # khoá nội bộ (ổn định): "dxf:<file>" hoặc GlobalId của IfcBuildingStorey
    name: str                     # nhãn ngắn trên toà nhà (level:ref), vd "1"
    long_name: str                # tên dài, vd "Tầng 1"
    elevation_m: float | None
    source_kind: str              # dxf | ifc
    source_ref: str               # để sinh id
    index: int = 0                # storey_index (OSM level, IMDF ordinal mặc định)
    ordinal: int | None = None    # ghi đè nếu cấu hình
    file_order: int = 0


@dataclass
class Obj:
    type: str                     # space | door | wall | ...
    source_kind: str              # dxf | ifc
    source_ref: str               # IfcGloballyUniqueId hoặc "file|layer|handle"
    source_class: str             # IFC class hoặc layer CAD
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
    georef_hint: Any = None       # georeference đọc từ IFC (nếu có)

    def warn(self, msg: str) -> None:
        if msg not in self.warnings:
            self.warnings.append(msg)

    def count(self, key: str, n: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + n
