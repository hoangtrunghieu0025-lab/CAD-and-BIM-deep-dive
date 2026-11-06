"""Dựng object `door` của IMDF opening (type, automatic, material) từ IFC hoặc ATTRIB của block DXF."""
from __future__ import annotations

from typing import Any

from ..export.imdf_vocab import DOOR_MATERIAL, DOOR_TYPE

# IfcDoor.OperationType (IFC4) -> door.type của IMDF. Dạng gập (FOLDING) chưa có ánh xạ chắc chắn nên để null.
_IFC_TYPE = {"REVOLVING": "revolving", "ROLLINGUP": "shutter"}
_TRUE = {"YES", "TRUE", "1", "Y"}
_FALSE = {"NO", "FALSE", "0", "N"}


def _ifc_type(op: str | None) -> str | None:
    if not op:
        return None
    if op in _IFC_TYPE:
        return _IFC_TYPE[op]
    if "SWING" in op:
        return "swinging"
    if "SLIDING" in op:
        return "sliding"
    return None


def door_json(props: dict[str, Any], warn) -> dict[str, Any] | None:
    """Trả {type, automatic, material} (member nào không biết thì null), hoặc None nếu không biết gì."""
    attrs = {str(k).upper(): str(v).strip() for k, v in (props.get("attribs") or {}).items()}
    typ = None
    if "TYPE" in attrs:
        typ = attrs["TYPE"].lower()
        if typ not in DOOR_TYPE:
            warn(f"ATTRIB TYPE '{attrs['TYPE']}' không thuộc các giá trị door.type của IMDF; bỏ qua")
            typ = None
    else:
        typ = _ifc_type(props.get("op_type"))

    auto = None
    if "AUTOMATIC" in attrs:
        v = attrs["AUTOMATIC"].upper()
        auto = True if v in _TRUE else False if v in _FALSE else None
        if auto is None:
            warn(f"ATTRIB AUTOMATIC '{attrs['AUTOMATIC']}' không hiểu được; bỏ qua")
    else:
        drive = (props.get("psets") or {}).get("Pset_DoorCommon", {}).get("HasDrive")
        auto = drive if isinstance(drive, bool) else None

    mat = None
    if "MATERIAL" in attrs:
        mat = attrs["MATERIAL"].lower()
        if mat not in DOOR_MATERIAL:
            warn(f"ATTRIB MATERIAL '{attrs['MATERIAL']}' không thuộc door.material của IMDF; bỏ qua")
            mat = None

    if typ is None and auto is None and mat is None:
        return None
    return {"type": typ, "automatic": auto, "material": mat}
