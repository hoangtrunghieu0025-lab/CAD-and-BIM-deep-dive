"""Đọc cấu hình mapping và project.yaml (spec mục 3).

Lỗi cấu hình ném `ConfigError` -> CLI trả mã thoát 2.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


class ConfigError(Exception):
    """Cấu hình thiếu/sai (mã thoát 2)."""


class DataError(Exception):
    """Dữ liệu đầu vào không dùng được (mã thoát 1)."""


def load_yaml(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise ConfigError(f"không thấy file cấu hình: {p}")
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ConfigError(f"YAML sai cú pháp trong {p}: {e}") from e
    if not isinstance(data, dict):
        raise ConfigError(f"{p}: nội dung gốc phải là mapping")
    return data


class Project:
    """project.yaml + hai file mapping đã nạp. Đường dẫn tương đối tính từ thư mục chứa project.yaml
    (rồi tới thư mục làm việc hiện tại nếu không thấy)."""

    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        self.base = self.path.parent
        self.raw = load_yaml(self.path)
        for key in ("name", "mapping", "inputs"):
            if key not in self.raw:
                raise ConfigError(f"project.yaml thiếu khoá bắt buộc `{key}`")
        m = self.raw["mapping"]
        if not isinstance(m, dict) or "layers" not in m or "tags" not in m:
            raise ConfigError("project.yaml: `mapping` cần `layers` và `tags`")
        self.name: str = str(self.raw["name"])
        self.layers = load_yaml(self._resolve(m["layers"]))
        self.tags = load_yaml(self._resolve(m["tags"]))
        self.inputs: list[dict[str, Any]] = list(self.raw["inputs"])
        if not self.inputs:
            raise ConfigError("project.yaml: `inputs` rỗng")
        for i, inp in enumerate(self.inputs):
            if inp.get("kind") not in ("dxf", "ifc"):
                raise ConfigError(f"inputs[{i}].kind phải là dxf hoặc ifc")
            if "file" not in inp:
                raise ConfigError(f"inputs[{i}] thiếu `file`")
            if inp["kind"] == "dxf" and "storey" not in inp:
                raise ConfigError(f"inputs[{i}] (dxf) thiếu `storey` (name, long_name, elevation_m)")
        self.georeference: dict[str, Any] | None = self.raw.get("georeference")
        self.venue: dict[str, Any] = self.raw.get("venue") or {}
        self.address: dict[str, Any] = self.raw.get("address") or {}

    def _resolve(self, p: str | Path) -> Path:
        q = Path(p)
        if q.is_absolute():
            return q
        for root in (self.base, Path.cwd(), self.base.parent):
            if (root / q).exists():
                return root / q
        return self.base / q

    def input_path(self, inp: dict[str, Any]) -> Path:
        return self._resolve(inp["file"])

    # --- truy cập tiện lợi -------------------------------------------------
    @property
    def namespace(self) -> str:
        ns = self.tags.get("defaults", {}).get("ids", {}).get("namespace")
        if not ns:
            raise ConfigError("tag_mapping.yaml: defaults.ids.namespace chưa đặt")
        return str(ns)

    @property
    def language(self) -> str:
        return str(self.tags.get("defaults", {}).get("language", "vi"))

    @property
    def manifest_language(self) -> str:
        return str(self.tags.get("imdf_package", {}).get("manifest", {}).get("language", "vi"))

    def validate_required(self) -> None:
        """Các trường bắt buộc để sinh venue/address (IMDF)."""
        miss = []
        if not self.venue.get("name"):
            miss.append("venue.name")
        if not self.venue.get("category"):
            miss.append("venue.category")
        for k in ("address", "locality", "country"):
            if not self.address.get(k):
                miss.append(f"address.{k}")
        if miss:
            raise ConfigError("project.yaml thiếu: " + ", ".join(miss))
        from .export.imdf_vocab import VENUE

        if self.venue["category"] not in VENUE:
            raise ConfigError(
                f"venue.category '{self.venue['category']}' không thuộc 22 giá trị IMDF: {sorted(VENUE)}"
            )


def compile_re(pattern: str) -> re.Pattern[str]:
    try:
        return re.compile(pattern)
    except re.error as e:
        raise ConfigError(f"regex không hợp lệ `{pattern}`: {e}") from e
