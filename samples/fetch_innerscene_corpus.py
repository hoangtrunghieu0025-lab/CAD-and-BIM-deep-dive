"""Tải bộ bản vẽ DXF kiểm thử từ thư viện Innerscene (CC0) về samples/corpus/innerscene/.

Dùng:  python -I samples/fetch_innerscene_corpus.py [--dry-run] [--max-mep N] [--max-plan N]
       [--max-total-mb M] [--delay S]

Cách làm có trách nhiệm:
  * Đọc robots.txt và chỉ gọi URL mà nhóm User-agent "*" cho phép; khoảng cách giữa hai yêu cầu
    >= max(--delay, Crawl-delay trong robots.txt) (mặc định 3 giây).
  * Danh sách bản vẽ lấy từ sitemap_index.xml -> sitemap/library.xml (không dùng trang có "?").
  * Mỗi file ghi vào MANIFEST.csv: slug, URL trang, URL tải, kích thước, sha256, thời điểm,
    nhóm chọn (mep/plan), và `cc0_in_file` (dòng 999 của chính file có nhắc CC0 hay không).
  * Chỉ giữ file trông giống DXF dạng văn bản; bỏ qua file > 20 MB.
Giấy phép dữ liệu: CC0 1.0 theo điều khoản Innerscene (https://www.innerscene.com/tools/library/terms),
đọc ngày 2026-11-08. Dữ liệu tải về là DỮ LIỆU KHÔNG TIN CẬY: chỉ đọc bằng ezdxf, không chạy gì từ file."""
import argparse, csv, hashlib, os, re, sys, time, urllib.error, urllib.request, urllib.robotparser
from datetime import datetime, timezone

BASE = "https://www.innerscene.com"
UA = "cad-bim-research-fetch/1.0 (software test corpus; polite crawl)"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus", "innerscene")
OUT_DWG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus", "innerscene_dwg")
# Nhóm MEP: phải có từ chỉ hệ thống VÀ từ chỉ dạng bản vẽ (mặt bằng/sơ đồ), để bỏ chi tiết vật tư lẻ.
MEP_SYS = ("electrical", "hvac", "plumbing", "duct", "wiring", "sprinkler", "mep", "single-line", "lighting",
           "fire-alarm", "drainage", "sanitary", "ventilation", "air-condition", "panel-schedule", "ladder", "power")
MEP_FORM = ("plan", "layout", "diagram", "schematic", "riser", "single-line", "schedule", "mep")
# Thiết bị/ký hiệu MEP (cơ, điện, cấp thoát nước): nhóm "mep-sym", dùng thử nhận dạng khối INSERT/thiết bị điểm.
MEP_EQUIP = ("diffuser", "damper", "grille", "ahu", "chiller", "boiler", "fan-coil", "vav", "thermostat", "valve", "pump",
             "sprinkler", "luminaire", "light-fixture", "downlight", "switch", "socket", "outlet", "distribution-board",
             "panel-board", "breaker", "transformer", "wc", "basin", "sink", "shower", "urinal", "bathtub", "cistern",
             "water-heater", "pipe", "duct", "hvac", "plumbing", "electrical", "fire-alarm", "smoke-detector", "manhole",
             "floor-drain", "cable-tray", "conduit")
PLAN_KW = ("plan", "floor", "layout")
PLAN_BLD = ("villa", "apartment", "house", "office", "school", "hospital", "clinic", "hotel", "warehouse",
            "restaurant", "store", "shop", "residence", "building", "bhk", "bedroom", "flat", "studio", "cabin")
EXCLUDE = ("elevation", "detail", "symbol", "icon", "logo", "furniture", "chair", "table", "sofa", "tree",
           "plant", "vehicle", "bolt", "gear", "pcb", "hydrant", "grate", "ring", "bench", "sign", "rack")
TAG_PAGES = {"mep": "mep", "plan": "floor-plans", "arch": "architecture"}

_last = [0.0]


def polite_get(url, rp, delay):
    if not rp.can_fetch("*", url):
        raise PermissionError(f"robots.txt không cho phép {url}")
    wait = delay - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read(25 * 1024 * 1024 + 1)
            return data, r.geturl(), r.headers
    finally:
        _last[0] = time.time()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-mep", type=int, default=60)
    ap.add_argument("--max-plan", type=int, default=90)
    ap.add_argument("--max-mep-sym", type=int, default=0, help="số ký hiệu/thiết bị MEP (nhóm mep-sym)")
    ap.add_argument("--max-total-mb", type=float, default=150.0)
    ap.add_argument("--delay", type=float, default=3.0)
    ap.add_argument("--out-root", default=None, help="thư mục gốc ghi dữ liệu (mặc định samples/corpus)")
    ap.add_argument("--dwg-only", action="store_true", help="chỉ giữ file DWG nhị phân, bỏ DXF")
    a = ap.parse_args()

    global OUT, OUT_DWG
    if a.out_root:
        OUT = os.path.join(a.out_root, "innerscene")
        OUT_DWG = os.path.join(a.out_root, "innerscene_dwg")
    rp = urllib.robotparser.RobotFileParser()
    # tải robots.txt bằng đúng User-Agent của ta (urllib mặc định có thể bị 403 -> parser hiểu là cấm hết)
    rb = urllib.request.urlopen(urllib.request.Request(BASE + "/robots.txt", headers={"User-Agent": UA}), timeout=30).read()
    rp.parse(rb.decode("utf-8", "replace").splitlines())
    delay = max(a.delay, float(rp.crawl_delay("*") or 0))
    print(f"delay = {delay}s")

    lib, _, _ = polite_get(BASE + "/sitemap/library.xml", rp, delay)
    slugs = sorted({m for m in re.findall(r"/tools/library/drawings/([a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-f]{8})</loc>", lib.decode("utf-8", "replace"))})
    print(f"sitemap: {len(slugs)} bản vẽ")
    # 1) ưu tiên các trang chuyên mục có phân loại thật (không dùng ?page= vì robots cấm)
    seed = {}
    for grp, tag in TAG_PAGES.items():
        html, _, _ = polite_get(f"{BASE}/tools/library/drawings/tag/{tag}", rp, delay)
        for sl in re.findall(r'href="/tools/library/drawings/([a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-f]{8})"', html.decode("utf-8", "replace")):
            seed.setdefault(sl, "mep" if grp == "mep" else "plan")
    # 2) bổ sung theo từ khoá trong tên, có luật chặt hơn
    mep, plan, sym = [], [], []
    for sl in slugs:
        if sl in seed:
            continue
        is_mep_plan = any(k in sl for k in MEP_SYS) and any(k in sl for k in MEP_FORM)
        is_mep_equip = any(k in sl for k in MEP_EQUIP)
        if is_mep_plan and not any(x in sl for x in EXCLUDE if x not in ("symbol", "icon")):
            mep.append(sl)
        elif is_mep_equip and not any(x in sl for x in ("hydrant", "grate", "ring", "bench", "sign", "logo", "furniture", "tree", "plant")):
            sym.append(sl)
        elif any(x in sl for x in EXCLUDE):
            continue
        elif any(k in sl for k in PLAN_KW) and any(k in sl for k in PLAN_BLD):
            plan.append(sl)
    seed_mep = [x for x, g in seed.items() if g == "mep"]
    seed_plan = [x for x, g in seed.items() if g == "plan"]
    pick = ([(x, "mep") for x in (seed_mep + mep)[: a.max_mep]] + [(x, "mep-sym") for x in sym[: a.max_mep_sym]]
            + [(x, "plan") for x in (seed_plan + plan)[: a.max_plan]])
    print(f"seed theo chuyên mục: mep={len(seed_mep)} plan/arch={len(seed_plan)}; thêm theo từ khoá: mep={len(mep)} mep-sym={len(sym)} plan={len(plan)}; chọn {len(pick)}")
    if a.dry_run:
        for s, g in pick:
            print(" ", g, s)
        return

    os.makedirs(OUT, exist_ok=True)
    mpath = os.path.join(OUT, "MANIFEST.csv")
    os.makedirs(OUT_DWG, exist_ok=True)
    dpath = os.path.join(OUT_DWG, "MANIFEST.csv")
    have = set()
    skpath = os.path.join(OUT, "SKIPPED.txt")
    if os.path.exists(skpath):
        with open(skpath, encoding="utf-8") as f:
            have |= {ln.split("\t")[0] for ln in f if ln.strip()}
    for mp in (mpath, dpath):
        if os.path.exists(mp):
            with open(mp, newline="", encoding="utf-8") as f:
                have |= {r["slug"] for r in csv.DictReader(f)}
    new = not os.path.exists(mpath)
    total = sum(os.path.getsize(os.path.join(OUT, x)) for x in os.listdir(OUT) if x.endswith(".dxf"))
    cols = ["slug", "group", "page_url", "download_url", "bytes", "sha256", "fetched_at_utc", "cc0_in_file", "license", "source"]
    dnew = not os.path.exists(dpath)
    with open(mpath, "a", newline="", encoding="utf-8") as mf, open(dpath, "a", newline="", encoding="utf-8") as df:
        w = csv.DictWriter(mf, fieldnames=cols)
        wd = csv.DictWriter(df, fieldnames=cols)
        if new:
            w.writeheader()
        if dnew:
            wd.writeheader()
        ok = skipped = 0
        for s, g in pick:
            if s in have:
                continue
            if total > a.max_total_mb * 1024 * 1024:
                print("đạt giới hạn dung lượng, dừng")
                break
            try:
                data, final, _h = polite_get(f"{BASE}/api/library/{s}/download", rp, delay)
            except (urllib.error.URLError, PermissionError, TimeoutError) as e:
                print(f"  bỏ qua {s}: {e}")
                skipped += 1
                continue
            head = data[:4096].decode("latin-1", "replace")
            if re.match(r"AC10\d\d", head) and len(data) <= 20 * 1024 * 1024:   # DWG nhị phân: lưu riêng, chờ bộ chuyển đổi
                fn = os.path.join(OUT_DWG, s + ".dwg")
                with open(fn, "wb") as f:
                    f.write(data)
                wd.writerow(dict(slug=s, group=g, page_url=f"{BASE}/tools/library/drawings/{s}", download_url=final,
                                 bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                                 fetched_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 cc0_in_file="n/a (DWG nhị phân)", license="CC0-1.0 (Innerscene terms)", source="innerscene.com"))
                df.flush()
                print(f"  dwg {g:<4} {len(data):>9} B  {s}  ({head[:6]})")
                continue
            if len(data) > 20 * 1024 * 1024 or not re.search(r"^\s*0\s*\r?\n\s*SECTION", head, re.M | re.I) and not head.lstrip().startswith("999"):
                print(f"  bỏ qua {s}: không giống DXF văn bản hoặc quá lớn ({len(data)} B)")
                with open(skpath, "a", encoding="utf-8") as sf:
                    sf.write(f"{s}\tkhông phải DXF/DWG ({len(data)} B)\n")
                skipped += 1
                continue
            if a.dwg_only:
                print(f"  (bỏ DXF) {s}")
                continue
            fn = os.path.join(OUT, s + ".dxf")
            with open(fn, "wb") as f:
                f.write(data)
            total += len(data)
            w.writerow(dict(slug=s, group=g, page_url=f"{BASE}/tools/library/drawings/{s}", download_url=final,
                            bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                            fetched_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            cc0_in_file="CC0" in head, license="CC0-1.0 (Innerscene terms)", source="innerscene.com"))
            mf.flush()
            ok += 1
            print(f"  ok {g:<4} {len(data):>9} B  {s}")
    print(f"xong: {ok} file mới, {skipped} bỏ qua, tổng {total/1024/1024:.1f} MB tại {OUT}")


if __name__ == "__main__":
    sys.exit(main())
