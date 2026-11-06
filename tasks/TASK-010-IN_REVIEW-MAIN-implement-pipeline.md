---
id: TASK-010
title: "[IN_REVIEW][MAIN] Cài đặt pipeline DXF/IFC → GPKG và test"
category: MAIN
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T15:00:02+07:00
status: in_review
priority: high
depends_on: [TASK-001, TASK-007, TASK-008, TASK-009]
---

# [IN_REVIEW][MAIN] TASK-010 — Cài đặt pipeline DXF/IFC → GPKG và test

## Mô tả
Cài đặt theo `docs/cad-to-gpkg-design.md`: đọc DXF/IFC, áp mapping, georeference, chuẩn hoá OSM/IMDF, ghi `.gpkg`, kèm test tự động.

## Đầu vào (inputs)
- `docs/cad-to-gpkg-design.md`, `config/*.yaml`, `samples/`

## Đầu ra mong đợi (expected_outputs)
- Code trong `src/`, test trong `tests/`
- CLI chạy được: `python -m src.cli <input> <output.gpkg>` (hoặc tương đương nêu trong spec)
- `.gpkg` mẫu nhỏ (≤ vài MB) vào `samples/out/` nếu dung lượng cho phép

## Tiêu chí hoàn thành (acceptance)
- [x] `pytest` qua toàn bộ test trong spec
- [x] `ogrinfo -al -so` liệt kê đủ layer IMDF, CRS đúng
- [x] Chỗ spec thiếu/sai được báo trong mục Blocker / câu hỏi mở (mobile sẽ cập nhật spec)
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; ghi vào `src/`, `tests/`, `requirements.txt`, `samples/out/`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | in_review | 2026-11-06T15:00:02+07:00 | cài đặt xong, 60 test qua; chờ mobile rà mục Blocker và chủ dự án push |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T15:08:50+07:00 | in_review | **Xử lý mục Blocker (9 điểm).** 1: venue.category = 22 giá trị (đã đối chiếu trang categories); sửa 3 chỗ (tag_mapping.yaml, spec mục 11, mapping-design mục 5); là trường bắt buộc trong project.yaml, mẫu dùng businesscampus (công trình thật do chủ dự án chọn). 2: chấp nhận vá srs_id=-1; đã ghi vào spec 6.5. 3: **đổi manifest.language thành `vi`** để cùng tag với khoá LABELS (spec chưa có câu rõ về so khớp `vi` và `vi-VN`); cần laptop đổi mặc định `vi-VN` trong src/cli.py, src/config.py, src/export/imdf.py. 4: chấp nhận, kiểm 'unit phủ kín level' là tautology với dữ liệu tự sinh; đã ghi chú trong spec mục 9; kiểm khe có nghĩa cần đường bao độc lập (TASK-015). 5: chấp nhận `short_name_rule: trailing_token`, ghi đè được bằng inputs[].storey.short_name. 6: chấp nhận venue.building_name (đã vào spec mục 3). 7 và 8: gom vào TASK-015 (mẫu bổ sung + đối tượng chưa cài đặt); giữ nhãn unverified. 9: chấp nhận. Chưa đọc mã src/, chưa chạy pytest. |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T10:34:56+07:00 | blocked | Chưa bắt đầu. `docs/cad-to-gpkg-design.md` và `config/*.yaml` chưa tồn tại; TASK-007 và TASK-009 đang `todo`. |
| 2026-11-06T14:47:20+07:00 | in_progress | Hết blocked: TASK-001, 007, 008, 009 đều `DONE`. Bắt đầu đọc spec và cài đặt `src/`, `tests/`. |
| 2026-11-06T15:00:02+07:00 | in_review | **Cài đặt xong theo `docs/cad-to-gpkg-design.md`.** Mã: `src/` (`config`, `model`, `pipeline`, `cli`, `ingest/`, `cad2bim/`, `extract/`, `normalize/`, `export/`), `src/README.md`; test: `tests/` (**60 test qua**, ~26 s): T1–T15 và T17–T20 tự động; **T16 (QGIS giao diện) để TASK-011**. CLI: `python -m src.cli build|check|imdf` (mã thoát 0/1/2, đã test). Dự án mẫu: `samples/project-dxf.yaml`, `samples/project-ifc.yaml`; kết quả mẫu nhỏ ở `samples/out/` (`sample-dxf.gpkg` 236 KB, `sample-ifc.gpkg` 240 KB, `sample-dxf.imdf.zip` 5,5 KB). **Kết quả**: cả DXF (2 file) và IFC đều ra 1 venue, 1 address, 1 building, 1 footprint, 2 level, 26 unit, 24 opening; `check` ĐẠT 0 lỗi/0 cảnh báo; `ogrinfo -al -so` liệt kê venue/footprint/level/unit/opening (CRS EPSG:4326) + address/building/_meta (attributes); tâm cửa IFC = tâm cửa DXF (T19, ~1 mm); id đều UUID v4 và ổn định giữa các lần chạy; QGIS 3.44.7 (PyQGIS) nạp hợp lệ cả 7 layer, extent quanh Hà Nội, lọc `osm_level='1'` ra 13 unit. Bộ `check` đã được thử âm tính (FK hỏng, unit chồng lấn, opening lệch ranh giới, thiếu venue, category/nhãn/id sai, cột bắt buộc null đều bị bắt). Chưa có gì được push (chờ chủ dự án). |

## Blocker / câu hỏi mở
Không có blocker. Các điểm **spec thiếu/sai/cần xác nhận** phát hiện khi cài đặt (mobile cập nhật spec nếu đồng ý):
1. **`venue.category` có 22 giá trị, không phải 27** (spec mục 11 dòng 1, `config/tag_mapping.yaml` dòng ~40, `docs/mapping-design.md` mục 5). Con số 27 là sai sót của laptop ở TASK-012 (đếm nhầm 5 dòng điều hướng của trang). Đã sửa `research/04-osm-imdf-tagging/imdf-feature-types.md` và dùng 22 giá trị trong `src/export/imdf_vocab.py`. Chọn tạm `businesscampus` cho dự án mẫu; mobile/chủ dự án chọn giá trị thật.
2. **`srs_id=-1` khi không georeference (spec 6.5)**: GDAL mặc định ghi `srs_id=99999` (SRS tuỳ chỉnh). Pipeline vá về `-1` (metadata và header blob geometry), có test; hệ quả: khi `--allow-unreferenced` không tạo RTree.
3. **Khoá ngôn ngữ LABELS và manifest**: manifest `language="vi-VN"` nhưng LABELS dùng khoá `"vi"` (T17). Chưa tìm thấy câu spec nói so khớp theo tag chính hay đầy đủ; pipeline và `check` đang chấp nhận khoá `"vi"`. Cần xác nhận (hoặc đổi manifest `vi`).
4. **Kiểm "unit phủ kín level" (mục 9-B) là tautology với dữ liệu do pipeline sinh**, vì spec định nghĩa `level` = hợp các unit. Nó chỉ có ý nghĩa với GPKG ngoài. Phần thật sự phát hiện khe giữa unit là cảnh báo "lỗ/khe bên trong level" (đã có). Nếu muốn kiểm khe thật, spec cần nguồn đường bao độc lập (ví dụ đường bao tường `A-WALL`/IfcWall).
5. **Quy tắc đặt nhãn tầng IFC**: spec nói `short_name` ngắn ("1"); với IFC (`IfcBuildingStorey.Name`='Tầng 1') pipeline rút số cuối chuỗi (`short_from_name`: 'Tầng 1'→'1', 'B1'→'B1', không có số thì giữ nguyên). Đây là quy ước mới của laptop, cần mobile xác nhận hoặc thay bằng cấu hình.
6. **Khoá cấu hình thêm vào `project.yaml`** (không có trong spec): `venue.building_name` (tuỳ chọn, tên toà nhà khi IFC không có). `ground_storey` đã có ở `tag_mapping.yaml`.
7. **Chưa cài đặt** (ngoài phạm vi T1–T20 hoặc thiếu dữ liệu thử): control points (spec 6.3), `fixture`/`detail`, IfcStair / thang máy / IfcColumn / IfcWindow / mode tường `structure`, GPKG nhiều toà nhà, `opening.door` (type/material/automatic), `display_point` cho unit/level; đường `FootPrint` thật của IfcSpace và `IfcOpeningElement` (mẫu chỉ có Body, không có opening) mới thử bằng mã, chưa có file thật.
8. **Tâm cửa IFC trên mẫu chỉ đến từ `placement_with_anchor`** (mẫu không có hình học cửa nên không thử được hai nhánh ưu tiên); pipeline ghi cảnh báo mỗi lần chạy. Cần file IFC thật để xác nhận `placement_anchor`.
9. **Hạn chế đã biết**: `export_imdf` yêu cầu `check` không lỗi; `check` chuyển sang UTM (`estimate_utm_crs`) để kiểm hình học theo mét, dung sai 1 mm và 1e-3 m².
