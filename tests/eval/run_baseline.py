"""Đường cơ sở (M0): chạy khâu cad2bim HIỆN CÓ trên mọi DXF trong một thư mục và ghi chỉ số.

Dùng:  .venv/bin/python -I tests/eval/run_baseline.py [thư_mục=samples/corpus] [nhãn=baseline]
Ghi:   out/eval/<nhãn>.json  và in bảng tóm tắt. Chỉ ĐỌC các DXF (dữ liệu không tin cậy).
Chỉ số theo bản vẽ: đọc được?, số thực thể ở modelspace, bao nhiêu khớp luật / bị bỏ qua (ignore) /
không khớp, số đối tượng sinh ra theo loại, số cảnh báo, lỗi (nếu có), thời gian."""
import json, os, sys, time
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from src import cad2bim                      # noqa: E402
from src.config import DataError, load_yaml  # noqa: E402
from src.ingest.dxf import load_dxf          # noqa: E402
from src.model import Model, Storey          # noqa: E402


def run_one(path, layers, tags, fallback_unit):
    r = {"file": os.path.basename(path), "bytes": os.path.getsize(path)}
    t0 = time.time()
    try:
        src = load_dxf(path, fallback_unit)
    except DataError as e:
        r["error"] = f"DataError: {e}"
        return r
    msp = list(src.msp)
    r["entities"] = len(msp)
    r["inserts"] = sum(1 for e in msp if e.dxftype() == "INSERT")
    r["layers_used"] = len({e.dxf.layer for e in msp})
    r["factor"] = src.factor
    model = Model()
    storey = Storey(key="k", name="1", long_name="1", elevation_m=0.0, source_kind="dxf", source_ref="eval")
    try:
        cad2bim.build(src, storey, layers, tags, model)
    except Exception as e:  # noqa: BLE001 - ghi nhận mọi lỗi để đo độ bền
        r["error"] = f"{type(e).__name__}: {e}"[:200]
    unmatched = sum(model.unmatched.values())
    matched = sum(v for k, v in model.counts.items() if k.startswith("dxf:"))
    r["matched"] = matched
    r["unmatched"] = unmatched
    r["ignored_or_other"] = r["entities"] - matched - unmatched
    r["objs"] = dict(Counter(o.type for o in model.objs))
    r["n_objs"] = len(model.objs)
    r["warnings"] = len(model.warnings)
    r["classified_frac"] = round(matched / r["entities"], 3) if r["entities"] else None
    r["top_unmatched_layers"] = [f"{l}/{t}:{n}" for (l, t), n in sorted(model.unmatched.items(), key=lambda kv: -kv[1])[:4]]
    r["seconds"] = round(time.time() - t0, 3)
    return r


def main():
    root = os.path.join(ROOT, sys.argv[1]) if len(sys.argv) > 1 and not os.path.isabs(sys.argv[1]) else (sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "samples", "corpus"))
    label = sys.argv[2] if len(sys.argv) > 2 else "baseline"
    layers = load_yaml(os.path.join(ROOT, "config", "layer_mapping.yaml"))
    tags = load_yaml(os.path.join(ROOT, "config", "tag_mapping.yaml"))
    fb = layers.get("units", {}).get("fallback_unit", "m")
    files = sorted(os.path.join(d, f) for d, _, fs in os.walk(root) for f in fs if f.lower().endswith(".dxf"))
    rows = [run_one(f, layers, tags, fb) for f in files]
    os.makedirs(os.path.join(ROOT, "out", "eval"), exist_ok=True)
    out = os.path.join(ROOT, "out", "eval", f"{label}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"label": label, "root": os.path.relpath(root, ROOT), "files": rows}, fh, ensure_ascii=False, indent=1)
    ok = [r for r in rows if "error" not in r]
    err = [r for r in rows if "error" in r]
    nonempty = [r for r in ok if r["entities"] > 0]
    print(f"{len(rows)} file: chạy xong {len(ok)}, lỗi {len(err)}; có thực thể {len(nonempty)} -> {out}")
    if err:
        print("  lỗi:", dict(Counter(r["error"].split(":")[0] for r in err)))
    gen = [r for r in nonempty if r["n_objs"] > 0]
    print(f"  có sinh ra ít nhất 1 đối tượng: {len(gen)}/{len(nonempty)}")
    if nonempty:
        fr = sorted(r["classified_frac"] for r in nonempty)
        print(f"  tỉ lệ thực thể (modelspace) khớp luật: trung vị {fr[len(fr)//2]:.3f}, max {fr[-1]:.3f}, bằng 0 ở {sum(1 for x in fr if x == 0)}/{len(fr)} file")
        tot = Counter()
        for r in ok:
            tot.update(r["objs"])
        print("  tổng đối tượng theo loại:", dict(tot))
        top = Counter()
        for r in nonempty:
            for s in r["top_unmatched_layers"]:
                top[s.split(":")[0]] += int(s.split(":")[1])
        print("  layer/loại không khớp nhiều nhất:", top.most_common(6))


if __name__ == "__main__":
    main()
