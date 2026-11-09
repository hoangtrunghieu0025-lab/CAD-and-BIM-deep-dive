"""Mô hình BIM trung gian có truy vết (TASK-018). Chưa ghi IFC ở đây: ifc_writer (task sau) chỉ biên dịch mô hình này.

Ý tưởng: alvin528/CAD2BIM (Apache-2.0) — mỗi phần tử mang nguồn, trạng thái khẳng định (observed/derived/assumed),
giả định và độ tin cậy; không đoán im lặng.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from shapely.geometry.base import BaseGeometry

CLAIMS = ("observed", "derived", "assumed")


def stable_id(*parts: object) -> str:
    """Id ổn định từ các thành phần nguồn; cùng đầu vào -> cùng id (tái lập)."""
    return hashlib.sha1("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:22]


@dataclass
class Provenance:
    source_refs: list[str] = field(default_factory=list)       # "tệp|layer|handle"
    claims: dict[str, str] = field(default_factory=dict)       # trường -> observed | derived | assumed
    assumptions: list[str] = field(default_factory=list)
    confidence: str = "medium"                                 # high | medium | low

    def claim(self, name: str, state: str, why: str | None = None) -> None:
        if state not in CLAIMS:
            raise ValueError(f"claim_state không hợp lệ: {state}")
        self.claims[name] = state
        if state == "assumed" and why:
            self.assumptions.append(f"{name}: {why}")


@dataclass
class BimElement:
    id: str
    kind: str                       # wall | column | door | window | space | duct | pipe | equipment | ...
    ifc_class: str
    storey: str
    geometry: BaseGeometry | None   # mét: tường = đường tim; vùng = Polygon; điểm = Point
    params: dict[str, Any] = field(default_factory=dict)       # thickness, height, width, rotation...
    props: dict[str, Any] = field(default_factory=dict)
    psets: dict[str, dict[str, Any]] = field(default_factory=dict)
    prov: Provenance = field(default_factory=Provenance)
    host_id: str | None = None


@dataclass
class BimModel:
    storey: str
    elements: list[BimElement] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def of(self, kind: str) -> list[BimElement]:
        return [e for e in self.elements if e.kind == kind]

    def warn(self, msg: str) -> None:
        if msg not in self.warnings:
            self.warnings.append(msg)
