#!/usr/bin/env python3
"""In bảng tất cả task, kiểm tra và đồng bộ quy ước đặt tên (xem tasks/README.md).

  python3 tasks/list.py           in bảng + kiểm tra; thoát mã 1 nếu có cảnh báo
  python3 tasks/list.py --sync    đồng bộ tên file, `title:` và dòng `#` theo
                                  trường `status` và `category` ở frontmatter
                                  (đổi tên bằng `git mv` nếu file đã được git theo dõi)

Nguồn sự thật: trường `status` và `category` trong frontmatter. Chỉ sửa hai trường
này (và bảng Tổng quan), rồi chạy --sync.
Tên file:  TASK-<NNN>-<STATUS>-<CATEGORY>-<slug>.md   (STATUS viết hoa, ví dụ IN_REVIEW)
"""
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

DIR = Path(__file__).resolve().parent
STATUSES = ["todo", "in_progress", "in_review", "blocked", "done", "cancelled"]
CATEGORIES = ["MAIN", "FIX", "SIDE"]
TAG = re.compile(r"^\[[A-Z_]+\]\[[A-Z]+\]\s*")


def split(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def fields(fm_text):
    out = {}
    for line in fm_text.splitlines():
        k, _, v = line.partition(":")
        out[k.strip()] = v.split("  #")[0].strip()
    return out


def want(f, fm):
    tid, st, cat = fm.get("id", "?"), fm.get("status", "?"), fm.get("category", "?")
    clean = TAG.sub("", fm.get("title", "").strip('"'))
    tag = f"[{st.upper()}][{cat}]"
    slug = re.sub(r"^TASK-\d+-(?:[A-Z_]+-(?:MAIN|FIX|SIDE)-)?", "", f.name)[:-3]
    return {
        "title": f'"{tag} {clean}"',
        "h1": f"# {tag} {tid} — {clean}",
        "name": f"{tid}-{st.upper()}-{cat}-{slug}.md",
    }


def sync(f, text, fm_text, body, w):
    fm_text = re.sub(r"^title: .*$", lambda _: f"title: {w['title']}", fm_text, count=1, flags=re.M)
    body = re.sub(r"^# .*$", lambda _: w["h1"], body, count=1, flags=re.M)
    new = f"---\n{fm_text}\n---\n{body}"
    if new != text:
        f.write_text(new, encoding="utf-8")
    if f.name != w["name"]:
        dst = f.with_name(w["name"])
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", f.name], cwd=DIR,
                                 capture_output=True).returncode == 0
        if tracked:
            subprocess.run(["git", "mv", f.name, dst.name], cwd=DIR, check=True)
        else:
            f.rename(dst)
        print(f"đổi tên: {f.name} -> {dst.name}")


do_sync = "--sync" in sys.argv
rows, warns = [], []
for f in sorted(DIR.glob("TASK-*.md")):
    text = f.read_text(encoding="utf-8")
    fm_text, body = split(text)
    fm = fields(fm_text)
    tid, st, cat = fm.get("id", "?"), fm.get("status", "?"), fm.get("category", "?")
    if st not in STATUSES:
        warns.append(f"{tid}: status '{st}' không hợp lệ")
    if cat not in CATEGORIES:
        warns.append(f"{tid}: category '{cat}' không hợp lệ")
    if st in STATUSES and cat in CATEGORIES:
        w = want(f, fm)
        if do_sync:
            sync(f, text, fm_text, body, w)
        else:
            h1 = re.search(r"^# .*$", body, re.M)
            if f.name != w["name"]:
                warns.append(f"{tid}: tên file phải là {w['name']}")
            if fm.get("title") != w["title"]:
                warns.append(f"{tid}: title phải là {w['title']}")
            if not h1 or h1.group(0) != w["h1"]:
                warns.append(f"{tid}: dòng # phải là '{w['h1']}'")
    rows.append((tid, cat, st, fm.get("assignees", ""), TAG.sub("", fm.get("title", "").strip('"')),
                 fm.get("depends_on", "[]")))

if do_sync:
    sys.exit(subprocess.call([sys.executable, __file__]))

for tid, n in Counter(r[0] for r in rows).items():
    if n > 1:
        warns.append(f"{tid}: bị trùng ID ở {n} file")

status = {r[0]: r[2] for r in rows}
print(f"{'ID':9}{'CAT':6}{'STATUS':13}{'AI':32}{'TIÊU ĐỀ'}")
for tid, cat, st, who, title, deps in rows:
    open_deps = [d for d in re.findall(r"TASK-\d+", deps) if status.get(d) != "done"]
    note = f"  (chờ {', '.join(open_deps)})" if open_deps and st in ("todo", "blocked") else ""
    print(f"{tid:9}{cat:6}{st:13}{who:32}{title}{note}")
if warns:
    print("\nCẢNH BÁO (sửa bằng: python3 tasks/list.py --sync):")
    for w in warns:
        print(" -", w)
    sys.exit(1)
