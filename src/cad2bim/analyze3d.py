"""Điều phối cad2bim 3D (TASK-018): một DXF 3D -> Model3D (lưới mặt + khung dây) kèm thống kê.

    from src.cad2bim.analyze3d import analyze3d
    m = analyze3d("model.dxf"); m.meshes, m.wires, m.stats

Chưa phân loại ngữ nghĩa BIM: mỗi phần tử chỉ mang `layer` và `kind` suy từ tên layer (có thể "unknown").
Đơn vị: dùng lại `read.resolve_units` (kiểm kích thước bản vẽ); khi $INSUNITS có vẻ sai mà kích thước vẫn "hợp lý"
(ví dụ sân vận động 200 đơn vị khai báo inch = 5 m) thì KHÔNG phát hiện được — luôn ghi cảnh báo nếu đơn vị không chắc chắn.
"""
from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..ingest.dxf import load_dxf
from .analyze import load_cfg
from .classify import Classifier
from .read import _UNIT_FACTOR, resolve_units, robust_span
from .read3d import Mesh3D, Wire3D, iter_geometry3d


@dataclass
class Model3D:
    meshes: list[Mesh3D] = field(default_factory=list)
    wires: list[Wire3D] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def layers(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for m in self.meshes:
            out.setdefault(m.layer, {"faces": 0, "wires": 0})["faces"] += len(m.faces)
        for w in self.wires:
            out.setdefault(w.layer, {"faces": 0, "wires": 0})["wires"] += 1
        return out


def _probe_span(msp: Any, max_depth: int, n: int = 4000) -> float:
    pts = []
    for g in iter_geometry3d(msp, 1.0, lambda _l: "probe", max_depth=max_depth, flatten_m=1.0, max_items=n):
        pts.extend(g.vertices if isinstance(g, Mesh3D) else g.pts)
    return robust_span([(p[0], p[1]) for p in pts])


def analyze3d(path: str | Path, cfg: dict[str, Any] | None = None, *, fallback_unit: str | None = None) -> Model3D:
    t0 = time.time()
    cfg = cfg or load_cfg()
    cls = Classifier(cfg)
    lim, tol = cfg["limits"], cfg["tolerances"]
    p = Path(path)
    model = Model3D()
    src = load_dxf(p, "m")
    for w in src.warnings:
        if "recover" in w:
            model.warnings.append(w)
    doc = src.doc
    msp = doc.modelspace()
    depth = lim.get("max_block_depth_3d", 8)
    span = _probe_span(msp, depth)
    factor, unit_name, how = resolve_units(doc, cfg.get("units", {}), lambda u: span * _UNIT_FACTOR[u], fallback_unit)
    if how == "insunits_conflict":
        model.warnings.append(f"{p.name}: $INSUNITS={doc.header.get('$INSUNITS')} nhưng kích thước ({span:g} đơn vị) vô lý; "
                              f"dùng '{unit_name}' — GIẢ ĐỊNH, cần xác nhận")
    elif how != "insunits":
        model.warnings.append(f"{p.name}: đơn vị không khai báo; dùng '{unit_name}' ({how}) — GIẢ ĐỊNH, cần xác nhận")
    st: Counter = Counter()
    for g in iter_geometry3d(msp, factor, cls.layer_kind, max_depth=depth, flatten_m=tol["flatten_m"] * 10,
                             max_items=lim.get("max_items_3d"), stats=st):
        (model.meshes if isinstance(g, Mesh3D) else model.wires).append(g)
    zs = [v[2] for m in model.meshes for v in m.vertices] + [q[2] for w in model.wires for q in w.pts]
    xs = [v[0] for m in model.meshes for v in m.vertices] + [q[0] for w in model.wires for q in w.pts]
    ys = [v[1] for m in model.meshes for v in m.vertices] + [q[1] for w in model.wires for q in w.pts]
    model.stats = {
        "file": p.name, "bytes": p.stat().st_size, "sha256": src.sha256, "units": unit_name, "units_how": how, "factor": factor,
        "declared_insunits": doc.header.get("$INSUNITS"),
        **{k: st[k] for k in ("entities", "meshes", "wires", "faces", "errors", "insert_too_deep", "truncated")},
        "vertices": sum(len(m.vertices) for m in model.meshes), "wire_points": sum(len(w.pts) for w in model.wires),
        "sources": {k[5:]: v for k, v in st.items() if k.startswith("mesh:")},
        "wire_types": {k[5:]: v for k, v in st.items() if k.startswith("wire:")},
        "unsupported": {k[12:]: v for k, v in st.items() if k.startswith("unsupported:")},
        "other_types": {k[6:]: v for k, v in st.items() if k.startswith("other:")},
        "bbox_m": [[min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]] if zs else None,
        "n_layers": len(model.layers()), "seconds": round(time.time() - t0, 2),
    }
    if model.stats["bbox_m"]:
        lo, hi = model.stats["bbox_m"]
        ext = max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        if ext < 10.0:
            model.warnings.append(f"{p.name}: kích thước lớn nhất chỉ {ext:.2f} m với đơn vị '{unit_name}' ({how}) — nhỏ bất thường "
                                  f"cho công trình; kiểm tra lại đơn vị (ngưỡng 10 m chỉ là heuristic)")
    return model
