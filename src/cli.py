"""Giao diện dòng lệnh (spec mục 3).

    python -m src.cli build --project samples/project-dxf.yaml --out out/building.gpkg [--allow-unreferenced]
    python -m src.cli check out/building.gpkg
    python -m src.cli imdf  out/building.gpkg --out out/building.imdf.zip

Mã thoát: 0 ổn · 1 lỗi dữ liệu (kèm báo cáo) · 2 lỗi cấu hình.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .config import ConfigError, DataError, Project
from .export.gpkg import write_gpkg
from .export.imdf import ImdfExportError, export_imdf
from .export.validate import check_gpkg
from .pipeline import run

EXIT_OK, EXIT_DATA, EXIT_CONFIG = 0, 1, 2


def _build(args: argparse.Namespace) -> int:
    project = Project(args.project)
    res = run(project, allow_unreferenced=args.allow_unreferenced)
    out = Path(args.out)
    write_gpkg(res.features, out, res.meta)
    out_dir = out.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "unmatched_layers.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["layer", "entity_type", "count"])
        for (layer, et), n in sorted(res.model.unmatched.items()):
            w.writerow([layer, et, n])
    report = {
        "gpkg": str(out), "tables": {k: len(v) for k, v in res.features.items()},
        "counts": res.model.counts, "unmatched": [
            {"layer": l, "entity_type": e, "count": n} for (l, e), n in sorted(res.model.unmatched.items())],
        "warnings": res.model.warnings, "georeference": res.georef.describe(),
    }
    (out_dir / "build_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"đã ghi {out} — " + ", ".join(f"{k}={v}" for k, v in report["tables"].items()))
    for w_ in res.model.warnings:
        print("  cảnh báo:", w_)
    return EXIT_OK


def _check(args: argparse.Namespace) -> int:
    rep = check_gpkg(args.gpkg)
    for f in rep.findings:
        print(f"[{f.level}] {f.code}: {f.message}")
    print(f"kiểm tra: {'ĐẠT' if rep.ok else 'KHÔNG ĐẠT'} ({len(rep.errors)} lỗi, "
          f"{len(rep.findings) - len(rep.errors)} cảnh báo, {len(rep.checked)} nhóm đạt)")
    return EXIT_OK if rep.ok else EXIT_DATA


def _imdf(args: argparse.Namespace) -> int:
    z = export_imdf(args.gpkg, args.out, language=args.language)
    print(f"đã ghi {z}")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m src.cli", description="CAD/BIM -> GeoPackage (OSM + IMDF) -> gói IMDF")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="DXF/IFC -> .gpkg")
    b.add_argument("--project", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--allow-unreferenced", action="store_true")
    b.set_defaults(fn=_build)
    c = sub.add_parser("check", help="kiểm tra .gpkg (mục 9)")
    c.add_argument("gpkg")
    c.set_defaults(fn=_check)
    i = sub.add_parser("imdf", help=".gpkg -> gói IMDF (.zip)")
    i.add_argument("gpkg")
    i.add_argument("--out", required=True)
    i.add_argument("--language", default="vi-VN")
    i.set_defaults(fn=_imdf)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except ConfigError as e:
        print(f"lỗi cấu hình: {e}", file=sys.stderr)
        return EXIT_CONFIG
    except ImdfExportError as e:
        print(f"lỗi xuất IMDF: {e}", file=sys.stderr)
        return EXIT_DATA
    except DataError as e:
        print(f"lỗi dữ liệu: {e}", file=sys.stderr)
        return EXIT_DATA


if __name__ == "__main__":
    sys.exit(main())
