---
id: TASK-012
title: "[IN_REVIEW][FIX] Xác minh nghiên cứu IFC/BIM 3D–7D/OSM/IMDF/GeoPackage với nguồn gốc"
category: FIX
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T10:41:42+07:00
updated_at: 2026-11-06T11:28:22+07:00
status: in_review
priority: high
depends_on: [TASK-001]
---

# [IN_REVIEW][FIX] TASK-012 — Xác minh nghiên cứu IFC/BIM 3D–7D/OSM/IMDF/GeoPackage với nguồn gốc

## Mô tả
**Task gốc cần sửa:** TASK-002, TASK-003, TASK-004, TASK-005 (nghiên cứu mới ở mức `IN_REVIEW`, chưa xác minh với nguồn gốc). Chặn: TASK-006, TASK-007, TASK-009, và qua đó TASK-010.

Các ghi chú trong `research/02-bim/`, `research/03-bim-pipeline-3d-7d/`, `research/04-osm-imdf-tagging/` mới dựa trên đoạn trích tìm kiếm và trí nhớ của agent, chưa đối chiếu nguồn gốc (xem `IMPORTANT_NOTIFICATIONS.md`). Hãy kiểm chứng bằng cách đọc nguồn gốc và/hoặc chạy thực nghiệm trên máy local. Không dùng cách vượt chặn bot (giả User-Agent…).

## Đầu vào (inputs)
- `research/02-bim/*.md`, `research/03-bim-pipeline-3d-7d/*.md`, `research/04-osm-imdf-tagging/*.md`
- `research/04-osm-imdf-tagging/prd-corrections.md` (bảng các dòng nghi sai trong `PRIMARY_OBJECTIVE.md`)
- Các `_sources.md` trong ba thư mục trên (log URL đã thử và checklist cần kiểm)
- Môi trường local từ TASK-001, file mẫu từ TASK-008 (`samples/`)

## Đầu ra mong đợi (expected_outputs)
- Ghi chú trong ba thư mục `research/` được sửa: sai→đúng, thêm URL nguồn gốc + ngày truy cập; nhãn "chưa xác minh" chỉ còn ở chỗ thật sự không kiểm chứng được (kèm lý do).
- `research/04-osm-imdf-tagging/prd-corrections.md` cập nhật thành bảng đã chốt (đúng/sai/thiếu + URL).
- `research/sources.md`: thêm dòng nguồn mới.
- Mục "Kết quả" cuối file task này: bảng tổng hợp số khẳng định đã xác minh / đã sửa / còn chưa xác minh theo từng thư mục.

## Danh sách ưu tiên cần kiểm
**A. OSM / IMDF / GeoPackage / QGIS (research/04)**
- OSM: `indoor=door` + `door=*` (cửa), `entrance=*`; cầu thang `stairs=yes` vs `highway=steps`; thang máy; `room=*`; `indoor=level`; `repeat_on`.
- IMDF 1.0.0: 16 feature_type; cột bắt buộc/nullable của từng feature; danh sách category (unit, opening, fixture, amenity…); tường là `unit` hay `fixture`; quan hệ venue–building; `manifest.json`; quy tắc của spec vs chỉ của validator.
- GeoPackage: `application_id`, `user_version`, header blob, RTree là extension, bảng attributes không có geometry; cách `pyogrio`/`geopandas` ghi; **thử thật**: ghi `.gpkg` nhỏ rồi `ogrinfo -al -so` và mở trong QGIS.
- QGIS: mở GPKG nhiều layer, style lưu trong `layer_styles`, lọc theo level.

**B. IFC / IfcOpenShell (research/02, 03)**
- Supertype `IfcSpace` (IFC4.3), `IfcBuildingStorey.Elevation`; `IfcMapConversion` (công thức ma trận, chuẩn hoá `XAxisAbscissa/Ordinate`, `Scale`, `SourceCRS`, `WorldCoordinateSystem`, `TrueNorth`).
- Property đầy đủ `Pset_DoorCommon`, `Pset_SpaceCommon`; `Qto_SpaceBaseQuantities`, `Qto_DoorBaseQuantities`.
- 4D/5D: `IfcWorkSchedule`/`IfcTask`/`IfcTaskTime`/`IfcRelAssignsToProcess` (và `RelatingProcess` deprecated ở 4.2?), `Pset_TaskCommon`, `IfcCostSchedule`/`IfcCostItem`/`IfcCostValue`.
- **Thử thật bằng ifcopenshell** trên `samples/*.ifc`: `ifcopenshell.util.element.get_container`, `util.shape` (footprint), `api.georeference`, `util.geolocation`, `ifcopenshell.guid` (GUID↔UUID), khác biệt settings 0.7.x vs 0.8.x; chạy thử đoạn code footprint trong `research/02-bim/ifcopenshell-geometry-extraction.md`.
- IDS: 6 facet, `ifctester`.

**C. CAD (còn sót từ TASK-002)**: quy ước layer NCS/AIA, ISO 13567, BS 1192 (nếu tìm được nguồn công khai); chạy thử vài hàm `ezdxf` đã ghi trong `research/01-cad/parsing-with-ezdxf.md` trên `samples/*.dxf`.

## Tiêu chí hoàn thành (acceptance)
- [x] Mỗi nhóm A, B có bảng kết quả (đã xác minh / đã sửa / chưa xác minh) trong mục "Kết quả"
- [x] Các đoạn code mẫu trong ghi chú đã chạy thử, ghi rõ lệnh và kết quả (hoặc ghi lỗi)
- [x] `prd-corrections.md` đã chốt
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: được sửa `research/02-bim/`, `research/03-bim-pipeline-3d-7d/`, `research/04-osm-imdf-tagging/`, `research/01-cad/` (chỉ phần C), `research/sources.md` (chỉ thêm dòng) và file task này. Không sửa `PRIMARY_OBJECTIVE.md`.
- **claude-mobile**: chỉ đọc các thư mục trên trong lúc task này chạy.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | in_review | 2026-11-06T11:16:02+07:00 | xác minh xong A/B/C; chờ mobile rà và chủ dự án quyết định sửa PRIMARY_OBJECTIVE |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T11:02:10+07:00 | in_progress | Nhận task. Bắt đầu đọc research/02..04, prd-corrections.md và các _sources.md. |
| 2026-11-06T11:28:22+07:00 | in_review | Theo yêu cầu chủ dự án: rà toàn bộ `PRIMARY_OBJECTIVE.md` cho luồng 01–03, ghi `research/02-bim/prd-corrections-01-03.md` (6 đề xuất sửa nhỏ: dòng 15, 27/56–57, 90, 96, 132, 147–163; phần còn lại đúng hoặc chưa xác minh). |

## Kết quả
Ngày 2026-11-06, claude-laptop (máy local). **Đếm theo số dòng trong các bảng "Kết quả xác minh"/đối chiếu của từng ghi chú; xấp xỉ, không phải kiểm toán từng câu.** "Chưa xác minh" = không có nguồn miễn phí đọc được hoặc cần dữ liệu/phần mềm thật.

| Nhóm / thư mục | Đã xác minh đúng | Đã sửa (sai → đúng) | Chưa xác minh (kèm lý do) |
|---|---|---|---|
| A. `research/04-osm-imdf-tagging` (OSM, IMDF, GeoPackage, QGIS) | ~33 | ~10 | ~8: Manifest object đầy đủ (không có trang riêng, 404); mô tả ngữ nghĩa category; validator IMDF chính thức; `door=*` giá trị; thao tác GUI QGIS (để TASK-011); `gdal.org` 429 |
| B. `research/02-bim` + `research/03-bim-pipeline-3d-7d` (IFC, IfcOpenShell, 4D–7D, GUID, IDS) | ~38 | ~10 | ~20: spec buildingSMART 403 (dùng schema bundled thay thế); FootPrint thật từ Revit; IFC2X3 georef; `Scale`≠1; `ifctester`; LOIN/MVD/IDM; COBie/ISO 19650-3; công cụ thương mại (Navisworks, Synchro, Tally…); độ ổn định GUID Revit/Unity |
| C. `research/01-cad` (ezdxf, phần chạy thử) | ~11 | 0 | ~8: MINSERT/OCS/MLINE/HATCH/SPLINE/block lồng/xref (mẫu không có); NCS/AIA, ISO 13567, BS 1192 (nguồn trả phí/chưa tìm) |

### Sai/thiếu quan trọng đã sửa (ảnh hưởng thiết kế)
1. **IMDF `occupant` có geometry null** (ghi chú cũ: Point); `detail` là LineString; `fixture` là Polygon; `opening` category là `automobile/bicycle/emergencyexit/pedestrian(.principal/.transit)/service` (cũ ghi sai).
2. **Tường**: floor-to-ceiling **MUST** là `unit` `structure` (vật liệu tuỳ chọn); `fixture` không dành cho tường kết cấu (kết luận của mobile "tường là unit" đúng một phần; `fixture` có category `wall` nhưng chỉ suy luận là không kết cấu).
3. **Unit phải phủ kín Level** là MUST trong spec (cũ nghi chỉ là validator) → pipeline phải lấp khe giữa IfcSpace.
4. **Gói IMDF**: bắt buộc chỉ `manifest.json`, `address.geojson`, `venue.geojson`; `venue.address_id` và `venue.display_point` bắt buộc; `level.name` và `short_name` bắt buộc.
5. **OSM**: `highway=steps` **có** trong SIT nhưng chỉ cho từng flight; khu cầu thang là `stairs=yes`; `level` bắt buộc; `repeat_on` chỉ trên node.
6. **GeoPackage**: bảng không geometry phải ghi bằng `pyogrio.write_dataframe(DataFrame thường)`; GeoDataFrame `geometry=[None]` ra bảng `features` (không phải `attributes`). `user_version` phụ thuộc GDAL (10200 với GDAL 3.8.4, 10400 với 3.12.4).
7. **IFC**: `get_container(space)` trả `None` nếu space được aggregate (dùng `get_aggregate`); `GeodeticDatum` OPTIONAL ở IFC4 (cũ ghi bắt buộc); `IfcCoordinateReferenceSystem.Name` OPTIONAL ở 4.3; `auto_xyz2enh` chuẩn hoá `XAxisAbscissa/Ordinate`; `Pset_TaskCommon` **không tồn tại**; `IfcWorkControl.StartTime` REQUIRED.
8. **Tự phát hiện lỗi của mình (TASK-008)**: `samples/sample-building.ifc` khai báo đơn vị mm nhưng thuộc tính gán tay (`Elevation`, `OverallWidth`) là mét → đã sửa bằng cách đặt đơn vị mét trong `samples/generate_samples.py` và sinh lại IFC (hình học vẫn 34/34).

### Việc cần chủ dự án / mobile
- Bảng đã chốt cho `PRIMARY_OBJECTIVE.md` mục 3.3 (OSM/IMDF/GPKG) ở `research/04-osm-imdf-tagging/prd-corrections.md`, và phần CAD/BIM/3D–7D ở `research/02-bim/prd-corrections-01-03.md` (laptop không có quyền sửa file gốc).
- Mobile rà lại rồi mới đánh dấu 002–005 `DONE`; sau đó TASK-007, 009 có thể bắt đầu.


## Blocker / câu hỏi mở
- Spec IFC trên buildingSMART trả 403 (chặn bot); không vượt chặn. Nếu mobile/chủ dự án cần trích dẫn trực tiếp trang spec, cần mở bằng trình duyệt thật.
- Chưa commit/push (theo yêu cầu của chủ dự án: báo cáo trước, pull rồi mới commit).
