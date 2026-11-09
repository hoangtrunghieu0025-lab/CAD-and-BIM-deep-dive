"""Tầng 1 — phân loại layer/khối thành loại đối tượng theo luật khai báo (config/classify.yaml).

Khớp theo TOKEN (không khớp chuỗi con) nên "COL" không khớp "COLOR". Một layer có thể chứa nhiều token; loại
được chọn theo thứ tự `priority` (annotation đứng đầu: "A-WALL-TEXT" là chú thích, không phải tường).
Ý tưởng luật khai báo theo hồ sơ: Mcrauli/dwg2ifc (MIT); tránh lỗi regex không neo của ifcbim.
"""
from __future__ import annotations

import re
from typing import Any

_TOKEN = re.compile(r"[A-Z0-9]+")
UNKNOWN = "unknown"
ANNOTATION = "annotation"


def tokens(name: str) -> list[str]:
    return _TOKEN.findall(name.upper())


class Classifier:
    def __init__(self, cfg: dict[str, Any]):
        self.priority: list[str] = list(cfg.get("priority", []))
        ann = cfg.get("annotation", {})
        self._ann_tokens = {t.upper() for t in ann.get("tokens", [])}
        self._ann_suffix = tuple(s.upper() for s in ann.get("suffixes", []))
        self._token_kind: dict[str, str] = {}
        self._block_kind: dict[str, str] = {}
        self.ifc: dict[str, str] = {}
        for kind, spec in cfg.get("kinds", {}).items():
            self.ifc[kind] = spec.get("ifc", "IfcBuildingElementProxy")
            for t in spec.get("tokens", []):
                self._token_kind.setdefault(t.upper(), kind)
            for t in spec.get("block_tokens", []):
                self._block_kind.setdefault(t.upper(), kind)
        self._rank = {k: i for i, k in enumerate(self.priority)}
        self._prefix = sorted((t for t in self._token_kind if len(t) >= 4), key=len, reverse=True)

    def _kind_of_token(self, tok: str) -> str | None:
        if tok in self._ann_tokens or (len(tok) > 4 and tok.endswith(self._ann_suffix)):
            return ANNOTATION
        k = self._token_kind.get(tok)
        if k:
            return k
        for pre in self._prefix:                    # "WALLS2" -> wall; chỉ cho từ khoá >= 4 ký tự
            if tok.startswith(pre) and not tok[len(pre):].isalpha():
                return self._token_kind[pre]
        return None

    def layer_kind(self, layer: str) -> str:
        """Loại của layer: một khoá trong `kinds`, "annotation" hoặc "unknown"."""
        kinds = {k for k in (self._kind_of_token(t) for t in tokens(layer)) if k}
        if not kinds:
            return UNKNOWN
        return min(kinds, key=lambda k: self._rank.get(k, 10**6))

    def block_kind(self, block: str | None) -> str | None:
        """Loại suy ra từ tên khối (cửa, cửa sổ); None nếu tên khối không gợi ý gì."""
        if not block or block.startswith("*"):
            return None
        for t in tokens(block):
            k = self._block_kind.get(t)
            if k:
                return k
        return None

    def ifc_class(self, kind: str) -> str:
        return self.ifc.get(kind, "IfcBuildingElementProxy")
