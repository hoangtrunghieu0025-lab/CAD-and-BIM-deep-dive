# src/ — pipeline CAD/BIM → GeoPackage (OSM + IMDF)

Cài đặt theo `docs/cad-to-gpkg-design.md` (TASK-010). Chạy từ gốc repo, trong `.venv`:

```bash
.venv/bin/python -m src.cli build --project samples/project-dxf.yaml --out out/building.gpkg   # DXF (mỗi file một tầng) hoặc IFC
.venv/bin/python -m src.cli check out/building.gpkg                                          # kiểm tra mục 9 của spec
.venv/bin/python -m src.cli imdf  out/building.gpkg --out out/building.imdf.zip              # gói IMDF (manifest.json + *.geojson)
.venv/bin/python -m pytest                                                                   # toàn bộ test (T1–T15, T17–T20)
```

Mã thoát: `0` ổn · `1` lỗi dữ liệu · `2` lỗi cấu hình. `build` ghi thêm `unmatched_layers.csv` và `build_report.json` cạnh `.gpkg`.

| Module | Việc |
|---|---|
| `ingest/` | đọc DXF (`ezdxf`, có `recover`) và IFC (`ifcopenshell`); chuẩn hoá đơn vị về mét |
| `cad2bim/` | áp `config/layer_mapping.yaml` lên DXF: phòng (polygon), nhãn, cửa |
| `extract/` | IFC: tầng, footprint, đoạn cửa; `georef.py`: IfcMapConversion / project.yaml / IfcSite |
| `normalize/` | `config/tag_mapping.yaml` → bảng IMDF + cột `osm_*`; id `stable_v4`; nhãn LABELS |
| `export/` | ghi GPKG, kiểm hợp lệ (`validate.py`), xuất gói IMDF |

Dữ liệu mẫu: `samples/project-dxf.yaml`, `samples/project-ifc.yaml` (toạ độ georeference và địa chỉ chỉ là minh hoạ). Kết quả mẫu: `samples/out/`.
Chưa cài đặt: control points (spec 6.3), `fixture`/`detail`, cầu thang/thang máy/cột/cửa sổ từ IFC, GPKG nhiều toà nhà.
