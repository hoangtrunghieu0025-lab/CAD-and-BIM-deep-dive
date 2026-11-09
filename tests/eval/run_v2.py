"""Đánh giá cad2bim v2 trên một hoặc nhiều thư mục DXF; ghi out/eval/<nhãn>.json và in tóm tắt.

Dùng:  .venv/bin/python -u -I tests/eval/run_v2.py <nhãn> <thư_mục_hoặc_file>... [--timeout 300]
Mỗi file: analyze() với giới hạn thời gian; ghi thống kê (đơn vị, loại phần tử, tường ghép/đơn, đầu rời, layer lạ, lỗi).
Chỉ ĐỌC các DXF (dữ liệu không tin cậy)."""
import json, os, signal, statistics, sys, time
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from src.cad2bim.analyze import analyze, load_cfg  # noqa: E402


class Timeout(Exception):
    pass


def _alarm(_s, _f):
    raise Timeout()


def main():
    args = sys.argv[1:]
    timeout = 300
    if "--timeout" in args:
        i = args.index("--timeout")
        timeout = int(args[i + 1])
        del args[i:i + 2]
    label, targets = args[0], args[1:]
    files = []
    for t in targets:
        t = t if os.path.isabs(t) else os.path.join(ROOT, t)
        if os.path.isfile(t):
            files.append(t)
        else:
            files += sorted(os.path.join(d, f) for d, _, fs in os.walk(t) for f in fs if f.lower().endswith(".dxf"))
    cfg = load_cfg()
    signal.signal(signal.SIGALRM, _alarm)
    rows = []
    for k, f in enumerate(files, 1):
        rel = os.path.relpath(f, ROOT)
        t0 = time.time()
        signal.alarm(timeout)
        try:
            m = analyze(f, cfg)
            row = dict(m.stats, path=rel, warnings=len(m.warnings))
        except Timeout:
            row = {"path": rel, "error": f"Timeout>{timeout}s", "bytes": os.path.getsize(f)}
        except Exception as e:  # noqa: BLE001 - ghi mọi lỗi để đo độ bền
            row = {"path": rel, "error": f"{type(e).__name__}: {e}"[:200], "bytes": os.path.getsize(f)}
        finally:
            signal.alarm(0)
        rows.append(row)
        e = row.get("elements") or {}
        print(f"[{k}/{len(files)}] {time.time()-t0:6.1f}s {row.get('error','ok'):<14} {os.path.basename(f)[:46]:<46} {dict(e)}", flush=True)
    os.makedirs(os.path.join(ROOT, "out", "eval"), exist_ok=True)
    out = os.path.join(ROOT, "out", "eval", f"{label}.json")
    json.dump({"label": label, "files": rows}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok = [r for r in rows if "error" not in r]
    print(f"\n== {len(rows)} file: ok {len(ok)}, lỗi {len(rows)-len(ok)} {dict(Counter(r['error'].split(':')[0] for r in rows if 'error' in r))} -> {out}")
    if ok:
        tot = Counter()
        for r in ok:
            tot.update(r["elements"])
        has = {k: sum(1 for r in ok if r["elements"].get(k)) for k in sorted(tot)}
        print("   tổng phần tử:", dict(tot))
        print("   số file có >=1 phần tử loại:", has)
        print("   file có >=1 phần tử bất kỳ:", sum(1 for r in ok if r["elements"]), "/", len(ok))
        print("   đơn vị:", dict(Counter(f"{r['units']}({r['units_how']})" for r in ok)))
        print("   thời gian/file: trung vị %.1fs, max %.1fs; bị cắt (truncated): %d" % (
            statistics.median(r["seconds"] for r in ok), max(r["seconds"] for r in ok), sum(1 for r in ok if r["truncated"])))
        unk = Counter()
        for r in ok:
            for l, n in r["unknown_layers_top"].items():
                unk[l] += n
        print("   layer 'không rõ' nhiều thực thể nhất:", unk.most_common(12))


if __name__ == "__main__":
    main()
