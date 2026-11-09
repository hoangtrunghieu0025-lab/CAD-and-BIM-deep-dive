"""Điều phối cad2bim v2: một DXF -> BimModel (tầng 0..5 + MEP), kèm thống kê để đánh giá.

    from src.cad2bim.analyze import analyze
    model = analyze("ban_ve.dxf")                # dùng config/classify.yaml
    model.of("wall"), model.stats

Chưa ghi IFC và chưa nối vào pipeline GPKG cũ (xem TASK-018, mốc M3+). Mọi giá trị suy đoán có claim_state.
"""
from __future__ import annotations

import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from shapely.geometry import LineString, Point, Polygon

from ..config import load_yaml
from ..ingest.dxf import load_dxf
from . import segments as sg
from . import walls as wl
from .classify import ANNOTATION, UNKNOWN, Classifier
from .elements import BimElement, BimModel, Provenance, stable_id
from .read import _UNIT_FACTOR, Prim, iter_prims, raw_span, resolve_units

ROOT = Path(__file__).resolve().parents[2]
_PATH_ETYPES = {"LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE", "ELLIPSE", "SPLINE"}


def load_cfg(path: str | Path | None = None) -> dict[str, Any]:
    return load_yaml(path or ROOT / "config" / "classify.yaml")


def _poly(pts: list[tuple[float, float]]) -> Polygon | None:
    if len(pts) < 3:
        return None
    p = Polygon(pts)
    if not p.is_valid:
        p = p.buffer(0)
    return p if p.geom_type == "Polygon" and not p.is_empty else None


def analyze(path: str | Path, cfg: dict[str, Any] | None = None, *, storey: str = "L1",
            fallback_unit: str | None = None) -> BimModel:
    t0 = time.time()
    cfg = cfg or load_cfg()
    cls = Classifier(cfg)
    tol, dflt, lim = cfg["tolerances"], cfg["defaults"], cfg["limits"]
    p = Path(path)
    name = p.name
    model = BimModel(storey=storey)
    src = load_dxf(p, "m")
    for w in src.warnings:
        if "recover" in w:
            model.warn(w)
    doc = src.doc
    msp = doc.modelspace()
    span = raw_span(msp)                                      # tính một lần, nhân với hệ số của từng đơn vị thử
    factor, unit_name, how = resolve_units(doc, cfg.get("units", {}), lambda u: span * _UNIT_FACTOR[u], fallback_unit)
    if how == "insunits_conflict":
        model.warn(f"{name}: $INSUNITS={doc.header.get('$INSUNITS')} nhưng kích thước bản vẽ ({span:g} đơn vị) vô lý; "
                   f"dùng '{unit_name}' — GIẢ ĐỊNH, cần xác nhận")
    elif how != "insunits":
        model.warn(f"{name}: đơn vị không khai báo ($INSUNITS=0); dùng '{unit_name}' ({how}) — GIẢ ĐỊNH, cần xác nhận")

    rstats: Counter = Counter()
    prims = list(iter_prims(msp, factor, cls.layer_kind, max_depth=lim["max_block_depth"], flatten_m=tol["flatten_m"],
                            max_prims=lim["max_prims"], stats=rstats))
    by_kind: dict[str, list[Prim]] = defaultdict(list)
    for pr in prims:
        by_kind[pr.kind].append(pr)
    top_prim = {pr.handle: pr for pr in prims if pr.etype == "INSERT"}

    def prov(layer: str, handle: str, state: dict[str, str] | None = None, why: dict[str, str] | None = None,
             conf: str = "medium") -> Provenance:
        pv = Provenance([f"{name}|{layer}|{handle}"], confidence=conf)
        for k, v in (state or {}).items():
            pv.claim(k, v, (why or {}).get(k))
        return pv

    # ------------------------------------------------------------------ tường
    wall_paths = [pr.pts for pr in by_kind["wall"] if pr.etype in _PATH_ETYPES]
    segs = sg.snap_endpoints(sg.explode(wall_paths, 1e-3), tol["snap_m"])
    pieces, left = wl.pair_walls(segs, tol["pair_min_m"], tol["pair_max_m"], tol["min_wall_len_m"],
                                 tol["angle_tol_deg"], tol["offset_tol_m"])
    left = sg.snap_endpoints(left, tol["snap_m"])       # đầu mút dựng lại sau ghép nét có sai số số học
    left, n_ext = sg.extend_free_ends(left, tol["extend_m"])
    singles = [w for w in wl.single_walls(left, dflt["wall"]["thickness_m"]) if w.axis.length >= tol["min_wall_len_m"]]
    layers_w = sorted({pr.layer for pr in by_kind["wall"]})
    for piece in pieces + singles:
        derived = piece.source == "pair"
        pv = Provenance([f"{name}|{'/'.join(layers_w)[:80]}|{'pair' if derived else 'single'}"],
                        confidence="medium" if derived else "low")
        pv.claim("axis", "derived" if derived else "observed")
        pv.claim("thickness", "derived" if derived else "assumed",
                 None if derived else f"{piece.thickness} m theo cấu hình (không ghép được hai nét)")
        pv.claim("height", "assumed", f"{dflt['wall']['height_m']} m theo cấu hình")
        coords = tuple(round(c, 3) for xy in piece.axis.coords for c in xy)
        model.elements.append(BimElement(
            stable_id(name, "wall", coords), "wall", cls.ifc_class("wall"), storey, piece.axis,
            {"thickness": piece.thickness, "height": dflt["wall"]["height_m"], "source": piece.source}, prov=pv))
    fp = wl.footprint(pieces + singles, tol["mitre_limit"])
    model.stats["wall_footprint_m2"] = round(fp.area, 3)
    model.stats["wall_axis_len_m"] = round(sum(w.axis.length for w in pieces + singles), 3)
    model.stats["wall_paired_len_m"] = round(sum(w.axis.length for w in pieces), 3)
    model.stats["wall_input_len_m"] = round(sg.total_length(segs), 3)
    model.stats["wall_free_ends_before"] = sg.free_end_count(segs) if len(segs) < 20000 else None
    model.stats["wall_ends_extended"] = n_ext
    model.stats["opening_candidates"] = len(wl.opening_candidates(pieces))

    # ------------------------------------------------------------------ cột (hợp nhất hình trùng tâm)
    cols: dict[tuple[int, int], tuple[Polygon, Prim]] = {}
    for pr in by_kind["column"]:
        if pr.etype == "INSERT" or not pr.closed:
            continue
        pg = _poly(pr.pts)
        if pg is None or pg.area > 4.0 or pg.area < 0.005:
            continue
        c = pg.centroid
        key = (round(c.x / 0.1), round(c.y / 0.1))
        if key not in cols or pg.area > cols[key][0].area:
            cols[key] = (pg, pr)
    for pg, pr in cols.values():
        pv = prov(pr.layer, pr.handle, {"footprint": "observed", "height": "assumed"},
                  {"height": f"{dflt['column']['height_m']} m theo cấu hình"})
        model.elements.append(BimElement(stable_id(name, "column", round(pg.centroid.x, 2), round(pg.centroid.y, 2)),
                                         "column", cls.ifc_class("column"), storey, pg,
                                         {"height": dflt["column"]["height_m"]}, prov=pv))

    # ------------------------------------------------------------------ cửa / cửa sổ
    bbox_of: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for pr in prims:
        if pr.top != pr.handle and pr.pts:
            bbox_of[pr.top].extend(pr.pts)
    seen_door: set[str] = set()
    for pr in prims:
        if pr.etype != "INSERT":
            continue
        kind = pr.kind if pr.kind in ("door", "window") else cls.block_kind(pr.block)
        if kind not in ("door", "window"):
            continue
        parent = top_prim.get(pr.top)
        if pr.depth > 0 and parent is not None and (parent.kind in ("door", "window") or cls.block_kind(parent.block) in ("door", "window")):
            continue
        pts = bbox_of.get(pr.handle) or bbox_of.get(pr.top, [])
        width = None
        if pts:
            xs, ys = [q[0] for q in pts], [q[1] for q in pts]
            width = max(max(xs) - min(xs), max(ys) - min(ys))
        d = dflt[kind]
        ok = width is not None and 0.4 <= width <= 4.0
        pv = prov(pr.layer, pr.handle, {"position": "observed", "width": "derived" if ok else "assumed",
                                        "height": "assumed"},
                  {"width": f"{d['width_m']} m theo cấu hình (không suy được từ khối)",
                   "height": f"{d['height_m']} m theo cấu hình"}, conf="medium" if ok else "low")
        model.elements.append(BimElement(
            stable_id(name, kind, pr.handle), kind, cls.ifc_class(kind), storey, Point(pr.pts[0]),
            {"width": round(width, 3) if ok else d["width_m"], "height": d["height_m"],
             "rotation_deg": pr.ins[2] if pr.ins else 0.0, "block": pr.block, "mirrored": bool(pr.ins and (pr.ins[3] < 0) != (pr.ins[4] < 0))},
            props={"attribs": pr.attribs} if pr.attribs else {}, prov=pv))
        seen_door.add(pr.handle)
    for pr in by_kind["door"]:                                    # cửa vẽ rời bằng cung quét (không có khối)
        if pr.etype == "ARC" and pr.depth == 0 and pr.radius and 0.4 <= pr.radius <= 3.0:
            pv = prov(pr.layer, pr.handle, {"position": "derived", "width": "derived", "height": "assumed"},
                      {"height": f"{dflt['door']['height_m']} m theo cấu hình"}, conf="low")
            model.elements.append(BimElement(stable_id(name, "door", pr.handle), "door", cls.ifc_class("door"), storey,
                                             Point(pr.pts[0]), {"width": round(pr.radius, 3), "height": dflt["door"]["height_m"],
                                                                "source": "swing_arc"}, prov=pv))

    # ------------------------------------------------------------------ phòng (vùng kín trên layer phòng)
    spaces: dict[tuple, tuple[Polygon, Prim]] = {}
    for pr in by_kind["space"]:
        if pr.etype == "INSERT" or not pr.closed:
            continue
        pg = _poly(pr.pts)
        if pg is None or not (tol["space_min_area_m2"] <= pg.area <= tol["space_max_area_m2"]):
            continue
        spaces.setdefault((round(pg.centroid.x, 1), round(pg.centroid.y, 1), round(pg.area, 1)), (pg, pr))
    texts = [pr for pr in prims if pr.etype in ("TEXT", "MTEXT") and pr.text]
    for pg, pr in spaces.values():
        label = next((t.text for t in texts if pg.contains(Point(t.pts[0]))), None)
        pv = prov(pr.layer, pr.handle, {"footprint": "observed", "name": "derived" if label else "assumed"},
                  {"name": "không có nhãn nằm trong vùng"}, conf="medium")
        model.elements.append(BimElement(stable_id(name, "space", round(pg.centroid.x, 2), round(pg.centroid.y, 2)),
                                         "space", cls.ifc_class("space"), storey, pg, {"area_m2": round(pg.area, 3)},
                                         props={"name": label}, prov=pv))

    # ------------------------------------------------------------------ MEP: tuyến (ống gió, ống nước) và điểm (thiết bị)
    for kind in ("mep_duct", "mep_pipe"):
        paths = [pr.pts for pr in by_kind[kind] if pr.etype in _PATH_ETYPES]
        msegs = sg.snap_endpoints(sg.explode(paths, 1e-3), tol["snap_m"])
        for ch in sg.node_and_chain(msegs):
            if ch.length < tol["min_wall_len_m"]:
                continue
            pv = Provenance([f"{name}|{kind}|chain"], confidence="low")
            pv.claim("route", "observed")
            pv.claim("size", "assumed", "chưa suy được tiết diện/đường kính từ bản vẽ")
            coords = tuple(round(c, 3) for xy in ch.coords for c in xy)
            model.elements.append(BimElement(stable_id(name, kind, coords), kind.removeprefix("mep_"), cls.ifc_class(kind),
                                             storey, ch, {"length_m": round(ch.length, 3)}, prov=pv))
    for kind in ("mep_equipment", "mep_fire"):
        for pr in by_kind[kind]:
            if pr.etype != "INSERT":
                continue
            parent = top_prim.get(pr.top)
            if pr.depth > 0 and parent is not None and parent.kind == kind:
                continue
            model.elements.append(BimElement(stable_id(name, kind, pr.handle), "equipment" if kind == "mep_equipment" else "fire_device",
                                             cls.ifc_class(kind), storey, Point(pr.pts[0]),
                                             {"block": pr.block, "rotation_deg": pr.ins[2] if pr.ins else 0.0},
                                             props={"attribs": pr.attribs} if pr.attribs else {},
                                             prov=prov(pr.layer, pr.handle, {"position": "observed", "type": "assumed"},
                                                       {"type": "chưa suy được loại thiết bị"}, conf="low")))

    # ------------------------------------------------------------------ thống kê
    kinds = Counter(e.kind for e in model.elements)
    claims = Counter(f"{k}:{v}" for e in model.elements for k, v in e.prov.claims.items())
    unknown_layers = {k.split(":", 2)[2]: v for k, v in rstats.most_common() if k.startswith(f"layer:{UNKNOWN}:")}
    model.stats.update({
        "file": name, "bytes": p.stat().st_size, "sha256": src.sha256, "units": unit_name, "units_how": how, "factor": factor,
        "entities": rstats["entities"], "prims": len(prims), "truncated": bool(rstats["truncated"]),
        "read_errors": rstats["errors"], "elements": dict(kinds),
        "layer_kinds": dict(Counter(pr.kind for pr in prims if pr.etype != "INSERT")),
        "skipped_annotation": rstats[f"skipped:{ANNOTATION}"], "skipped_unknown": rstats[f"skipped:{UNKNOWN}"],
        "claims": dict(claims), "n_walls_pair": len(pieces), "n_walls_single": len(singles),
        "unknown_layers_top": dict(list(unknown_layers.items())[:8]), "n_unknown_layers": len(unknown_layers),
        "other_types": {k.removeprefix("other:"): v for k, v in rstats.items() if k.startswith("other:")},
        "seconds": round(time.time() - t0, 2),
    })
    return model
