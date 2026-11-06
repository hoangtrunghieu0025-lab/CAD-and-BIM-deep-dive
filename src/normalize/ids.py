"""id IMDF và nhãn (LABELS).

IMDF: id phải là "RFC 4122 section 4.4 compliant version 4 UUID" (reference/type_designators, đã xác minh);
`uuid5` có version = 5 nên không dùng. `stable_v4` sinh UUID dạng v4 xác định: 16 byte đầu của
sha256(namespace + source_ref), đặt version = 4 và variant = 10xx.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
import uuid

UUID_V4_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def stable_v4(namespace: str, source_ref: str) -> str:
    digest = bytearray(hashlib.sha256((namespace + source_ref).encode("utf-8")).digest()[:16])
    digest[6] = (digest[6] & 0x0F) | 0x40
    digest[8] = (digest[8] & 0x3F) | 0x80
    return str(uuid.UUID(bytes=bytes(digest)))


def nfc(text: str | None) -> str | None:
    return None if text is None else unicodedata.normalize("NFC", text)


def level_case(text: str, mode: str = "upper") -> str:
    t = unicodedata.normalize("NFC", text).strip()
    return t.upper() if mode == "upper" else t.lower() if mode == "lower" else t


_SHORT_RE = re.compile(r"([A-Za-z]{0,2}-?\d+)\s*$")


def short_from_name(name: str) -> str:
    """'Tầng 1' -> '1', 'B1' -> 'B1', 'Basement -2' -> '-2'; không có số thì giữ nguyên."""
    m = _SHORT_RE.search(unicodedata.normalize("NFC", name).strip())
    return m.group(1) if m else name.strip()


def labels(text: str | None, lang: str) -> dict[str, str] | None:
    """LABELS = {LANGUAGE-TAG: chuỗi}; None nếu rỗng."""
    t = nfc(text)
    if t is None or not t.strip():
        return None
    return {lang: t.strip()}
