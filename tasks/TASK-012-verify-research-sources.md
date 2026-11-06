---
id: TASK-012
title: Xác minh nghiên cứu IFC/BIM 3D–7D/OSM/IMDF/GeoPackage với nguồn gốc
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T10:41:42+07:00
updated_at: 2026-11-06T10:41:42+07:00
status: todo
priority: high
depends_on: [TASK-001]
---

## Mô tả
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
- [ ] Mỗi nhóm A, B có bảng kết quả (đã xác minh / đã sửa / chưa xác minh) trong mục "Kết quả"
- [ ] Các đoạn code mẫu trong ghi chú đã chạy thử, ghi rõ lệnh và kết quả (hoặc ghi lỗi)
- [ ] `prd-corrections.md` đã chốt
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: được sửa `research/02-bim/`, `research/03-bim-pipeline-3d-7d/`, `research/04-osm-imdf-tagging/`, `research/01-cad/` (chỉ phần C), `research/sources.md` (chỉ thêm dòng) và file task này. Không sửa `PRIMARY_OBJECTIVE.md`.
- **claude-mobile**: chỉ đọc các thư mục trên trong lúc task này chạy.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | todo | 2026-11-06T10:41:42+07:00 | chưa nhận |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|

## Kết quả
(claude-laptop điền khi xong)

## Blocker / câu hỏi mở
-
