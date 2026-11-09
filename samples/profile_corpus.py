"""Lập hồ sơ từng DXF trong samples/corpus/<nguồn>/ để đánh giá độ phức tạp và độ phủ của bộ kiểm thử.

Dùng:  python -I samples/profile_corpus.py [thư_mục_corpus]   (mặc định samples/corpus)
Ghi:   <thư_mục>/PROFILE.csv và in tóm tắt. Chỉ ĐỌC file bằng ezdxf (dữ liệu không tin cậy, không thực thi gì).

Cột chính: phiên bản DXF, đơn vị ($INSUNITS), số layer/block/INSERT, số thực thể theo loại,
số LWPOLYLINE có bulge (cung), số thực thể nằm trong khối bị lật gương, kích thước bao (m nếu đơn vị biết),
tên layer, và điểm phức tạp thô (không phải chuẩn nào, chỉ để xếp hạng nội bộ)."""
import csv, math, os, sys
from collections import Counter

import ezdxf
from ezdxf import recover

MAIN_TYPES = ["LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE", "ELLIPSE", "SPLINE", "HATCH", "INSERT",
              "TEXT", "MTEXT", "DIMENSION", "SOLID", "3DFACE", "MESH", "LEADER", "MLINE", "WIPEOUT", "IMAGE", "XLINE"]


def flatten_count(msp, max_depth=4, cap=200000):
    """Đếm thực thể sau khi mở khối INSERT (đệ quy, giới hạn độ sâu và tổng) -> (Counter, độ sâu lớn nhất, bị cắt?)."""
    cnt, deepest, truncated = Counter(), 0, False
    stack = [(e, 0) for e in msp]
    while stack:
        e, d = stack.pop()
        deepest = max(deepest, d)
        if sum(cnt.values()) > cap:
            truncated = True
            break
        if e.dxftype() == "INSERT" and d < max_depth:
            try:
                stack.extend((v, d + 1) for v in e.virtual_entities())
            except Exception:  # noqa: BLE001
                cnt["INSERT_ERR"] += 1
            continue
        cnt[e.dxftype()] += 1
    return cnt, deepest, truncated


def profile(path):
    row = {"file": os.path.basename(path), "bytes": os.path.getsize(path)}
    try:
        doc = ezdxf.readfile(path)
        row["read"] = "ok"
    except Exception:
        try:
            doc, auditor = recover.readfile(path)
            row["read"] = f"recovered({len(auditor.errors)} lỗi)"
        except Exception as e:  # noqa: BLE001
            row["read"] = f"FAIL: {type(e).__name__}"
            return row
    row["dxfversion"] = doc.dxfversion
    u = doc.header.get("$INSUNITS", 0)
    row["insunits"] = u
    msp = doc.modelspace()
    c = Counter(e.dxftype() for e in msp)
    row["entities"] = sum(c.values())
    for t in MAIN_TYPES:
        row[t] = c.get(t, 0)
    row["other_types"] = sum(v for k, v in c.items() if k not in MAIN_TYPES)
    row["layers_used"] = len({e.dxf.layer for e in msp})
    row["layers_defined"] = len(doc.layers)
    row["blocks"] = sum(1 for b in doc.blocks if not b.name.startswith("*"))
    row["paperspace_ents"] = sum(len(l) for l in doc.layouts if l.name != "Model")
    bulge = 0
    mirrored = 0
    for e in msp:
        t = e.dxftype()
        if t == "LWPOLYLINE" and e.has_arc:
            bulge += 1
        if t == "INSERT" and (e.dxf.get("xscale", 1) < 0 or e.dxf.get("yscale", 1) < 0):
            mirrored += 1
    fc, deepest, trunc = flatten_count(msp)
    row["entities_flat"] = sum(fc.values())
    row["block_depth"] = deepest
    row["flat_types"] = ";".join(f"{k}:{v}" for k, v in fc.most_common(6))
    row["lwpoly_with_bulge"] = bulge
    row["mirrored_inserts"] = mirrored
    try:
        from ezdxf import bbox
        ext = bbox.extents(msp, fast=True)
        if ext.has_data:
            row["bbox_w"] = round(ext.size.x, 3)
            row["bbox_h"] = round(ext.size.y, 3)
    except Exception:  # noqa: BLE001
        pass
    names = sorted({e.dxf.layer for e in msp})
    row["layer_names"] = "|".join(names)[:400]
    # điểm phức tạp thô: nhiều loại thực thể, nhiều layer, có cung/khối/ghi chú
    kinds = sum(1 for t in MAIN_TYPES if fc.get(t, 0) > 0)
    row["complexity"] = round(math.log10(max(row["entities_flat"], 1)) * 2 + kinds * 0.5 + math.log2(row["layers_used"] + 1)
                              + (1 if bulge else 0) + (1 if row["blocks"] > 3 else 0) + (1 if c.get("HATCH", 0) else 0), 2)
    return row


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus")
    files = []
    for d, _, fs in os.walk(root):
        files += [os.path.join(d, f) for f in fs if f.lower().endswith(".dxf")]
    rows = [profile(f) for f in sorted(files)]
    cols = ["file", "bytes", "read", "dxfversion", "insunits", "entities", "entities_flat", "block_depth", "flat_types"] + MAIN_TYPES + [
        "other_types", "layers_used", "layers_defined", "blocks", "paperspace_ents", "lwpoly_with_bulge",
        "mirrored_inserts", "bbox_w", "bbox_h", "complexity", "layer_names"]
    out = os.path.join(root, "PROFILE.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    ok = [r for r in rows if r.get("read", "").startswith(("ok", "recovered"))]
    print(f"{len(rows)} file, đọc được {len(ok)}, hỏng {len(rows) - len(ok)} -> {out}")
    if ok:
        ent = sorted(r["entities_flat"] for r in ok)
        print(f"thực thể/file SAU KHI MỞ KHỐI: min {ent[0]}, trung vị {ent[len(ent)//2]}, max {ent[-1]}")
        print("phiên bản DXF:", dict(Counter(r["dxfversion"] for r in ok)))
        print("đơn vị ($INSUNITS):", dict(Counter(r["insunits"] for r in ok)), "(0 = không đơn vị, 4 = mm, 6 = m)")
        for t in ("LWPOLYLINE", "ARC", "SPLINE", "HATCH", "INSERT", "DIMENSION", "MTEXT"):
            print(f"  file có {t:<10}: {sum(1 for r in ok if r.get(t, 0) > 0)}")
        print(f"  file có LWPOLYLINE bulge: {sum(1 for r in ok if r.get('lwpoly_with_bulge', 0) > 0)};"
              f" có INSERT lật gương: {sum(1 for r in ok if r.get('mirrored_inserts', 0) > 0)}")


if __name__ == "__main__":
    main()
