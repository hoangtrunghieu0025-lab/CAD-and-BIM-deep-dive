"""Dựng kho bản vẽ THẬT cục bộ từ thư mục tải về của người dùng: samples/corpus_real/{raw,dxf}.

Dùng:  <python có libarchive-c> -I samples/build_real_corpus.py [thư_mục_nguồn=~/Downloads] [--no-convert]
Bước làm:
  1. Chỉ SAO CHÉP (không di chuyển/sửa file gốc): file .dwg/.dxf rời và file .dwg/.dxf lấy từ các .rar
     (bỏ .bak, .png, .url, desktop.ini...). RAR đọc bằng libarchive-c, không chạy gì trong file nén.
  2. Ghi MANIFEST.csv: đường dẫn, nguồn, kích thước, sha256, định dạng/phiên bản, URL trang gốc (đọc
     từ file .url trong rar), tình trạng giấy phép.
  3. Chuyển .dwg -> .dxf R2018 bằng ODA File Converter (đường dẫn qua biến môi trường ODA_FILE_CONVERTER,
     mặc định ~/apps/ODAFileConverter/*.AppImage). DXF có sẵn trong gói được giữ nguyên ở raw/ để so sánh.
GIẤY PHÉP: các file này tải từ trang chia sẻ miễn phí, KHÔNG rõ giấy phép tái phân phối -> chỉ dùng nội bộ để
kiểm thử, KHÔNG commit, KHÔNG đăng lại. Thư mục corpus_real/ phải nằm trong .gitignore."""
import csv, glob, hashlib, os, re, shutil, subprocess, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "corpus_real")
RAW, DXF = os.path.join(OUT, "raw"), os.path.join(OUT, "dxf")
DWG_VER = {"AC1006": "R10", "AC1009": "R11/12", "AC1012": "R13", "AC1014": "R14", "AC1015": "2000", "AC1018": "2004",
           "AC1021": "2007", "AC1024": "2010", "AC1027": "2013", "AC1032": "2018"}
KEEP = (".dwg", ".dxf")


def slug(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")[:80]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fmt(path):
    with open(path, "rb") as f:
        head = f.read(8)
    m = re.match(rb"AC10\d\d", head)
    if m:
        v = m.group(0).decode()
        return f"DWG {v} ({DWG_VER.get(v, '?')})"
    return "DXF" if path.lower().endswith(".dxf") else "?"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = os.path.expanduser(args[0] if args else "~/Downloads")
    convert = "--no-convert" not in sys.argv
    os.makedirs(RAW, exist_ok=True)
    rows = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def add(rel, origin, url):
        p = os.path.join(RAW, rel)
        note = ""
        if rel.lower().endswith(".dxf") and fmt(p).startswith("DWG"):       # đuôi sai: nội dung là DWG nhị phân
            new = rel[:-4] + ".dwg"
            os.replace(p, os.path.join(RAW, new))
            note = f"gói gốc đặt đuôi .dxf nhưng nội dung là DWG; đổi đuôi từ {os.path.basename(rel)}"
            rel, p = new, os.path.join(RAW, new)
        rows.append(dict(rel_path=rel, origin=origin, bytes=os.path.getsize(p), sha256=sha(p), format=fmt(p),
                         provenance_url=url, license_status="UNKNOWN - tải về từ trang chia sẻ; chỉ dùng nội bộ, không phân phối",
                         added_utc=now, note=note))

    # 1) file rời
    for f in sorted(glob.glob(os.path.join(src, "*"))):
        if f.lower().endswith(KEEP) and os.path.isfile(f):
            rel = os.path.join("loose", os.path.basename(f))
            os.makedirs(os.path.dirname(os.path.join(RAW, rel)), exist_ok=True)
            shutil.copy2(f, os.path.join(RAW, rel))
            add(rel, "Downloads (file rời)", "")
    # 2) các gói .rar
    try:
        import libarchive
    except ImportError:
        print("thiếu libarchive-c: bỏ qua các gói .rar (pip install libarchive-c; cần libarchive.so.13)")
        libarchive = None
    if libarchive:
        for rar in sorted(glob.glob(os.path.join(src, "*.rar"))):
            name = slug(os.path.splitext(os.path.basename(rar))[0])
            url = ""
            wanted = []
            with libarchive.file_reader(rar) as a:                       # lượt 1: tìm URL gốc trong .url
                for e in a:
                    if e.isdir:
                        continue
                    if e.pathname.lower().endswith(".url") and not url and "Useful files" not in e.pathname:
                        txt = b"".join(e.get_blocks()).decode("utf-8", "replace")
                        m = re.search(r"^URL=(\S+)", txt, re.M)
                        url = m.group(1) if m else ""
            with libarchive.file_reader(rar) as a:                       # lượt 2: lấy .dwg/.dxf
                for e in a:
                    if e.isdir or not e.pathname.lower().endswith(KEEP):
                        continue
                    parts = [slug(p) for p in e.pathname.replace("\\", "/").split("/") if p not in ("", ".", "..")]
                    rel = os.path.join(name, *parts[1:] if len(parts) > 1 else parts)
                    dst = os.path.join(RAW, rel)
                    if not os.path.abspath(dst).startswith(os.path.abspath(RAW) + os.sep):
                        continue                                          # chống ghi ra ngoài thư mục
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    with open(dst, "wb") as fh:
                        for blk in e.get_blocks():
                            fh.write(blk)
                    add(rel, f"rar: {os.path.basename(rar)}", url)
    with open(os.path.join(OUT, "MANIFEST.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    n_dwg = sum(1 for r in rows if r["format"].startswith("DWG"))
    print(f"đã sao {len(rows)} file ({n_dwg} DWG, {len(rows) - n_dwg} DXF) vào {RAW}; MANIFEST.csv ghi xong")

    # 3) chuyển DWG -> DXF
    if not convert:
        return
    oda = os.environ.get("ODA_FILE_CONVERTER") or (glob.glob(os.path.expanduser("~/apps/ODAFileConverter/*.AppImage")) or [""])[0]
    if not oda:
        print("không thấy ODA File Converter (đặt ODA_FILE_CONVERTER); bỏ qua bước chuyển")
        return
    os.makedirs(DXF, exist_ok=True)
    env = dict(os.environ, DISPLAY=os.environ.get("DISPLAY", ":0"))
    # tham số: vào, ra, phiên bản, loại, đệ quy=1, audit=1, bộ lọc chỉ .dwg
    cmd = [oda, RAW, DXF, "ACAD2018", "DXF", "1", "1", "*.dwg"]
    print("chạy:", " ".join(cmd))
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=3600)
    print("ODA exit", r.returncode, (r.stderr or "")[-300:].strip())
    got = [os.path.join(d, f) for d, _, fs in os.walk(DXF) for f in fs if f.lower().endswith(".dxf")]
    print(f"đã tạo {len(got)} file DXF trong {DXF}")


if __name__ == "__main__":
    main()
