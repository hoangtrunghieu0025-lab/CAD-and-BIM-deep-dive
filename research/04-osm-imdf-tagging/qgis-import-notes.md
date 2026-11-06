# Import GPKG IMDF vào QGIS — ghi chú

- **Câu hỏi nghiên cứu**: QGIS đọc GPKG nhiều layer, bảng không geometry và style như thế nào?
- **Kết luận ngắn**: QGIS 3.44.7 (PyQGIS headless) nạp được cả layer polygon (EPSG:4326), layer `GEOMETRY` có geometry NULL và bảng `attributes`; bảng attributes và layer geometry-null được nhận là **không có geometry** (`wkbType=100`, `geometryType=4`). Lưu style qua `saveStyleToDatabase` tạo bảng `layer_styles` trong GPKG (không đăng ký trong `gpkg_extensions`). Bộ lọc `setSubsetString("\"level_id\" = 'L1'")` hoạt động.
- **Độ tin cậy**: **trung bình-cao** cho phần đã chạy thật bằng PyQGIS; các thao tác giao diện (menu, hộp thoại) **chưa kiểm** — để TASK-011 (cần GUI).
- **Trạng thái xác minh**: ĐÃ XÁC MINH MỘT PHẦN bằng thực nghiệm (TASK-012, claude-laptop, 2026-11-06). `docs.qgis.org` đọc được (HTTP 200) nhưng chưa dùng làm nguồn.

## Đã kiểm chứng bằng PyQGIS (QGIS 3.44.7, offscreen, file `.gpkg` thử do `pyogrio` ghi)
| Phép thử | Kết quả |
|---|---|
| `QgsVectorLayer("<gpkg>\|layername=unit","unit","ogr")` | `isValid=True`, `geometryType=2` (polygon), `wkbType=3`, CRS `EPSG:4326`, đếm đúng feature |
| Layer `features` kiểu GEOMETRY có geometry NULL | `isValid=True`, `wkbType=100` (NoGeometry), CRS rỗng |
| Bảng `attributes` (không geometry) | `isValid=True`, `wkbType=100`, CRS rỗng; QGIS xử lý như bảng thuộc tính |
| Renderer `QgsCategorizedSymbolRenderer("category", ...)` + `layer.saveStyleToDatabase(name, desc, True, "")` | thành công (cảnh báo deprecated: API cũ); tạo bảng `layer_styles` cột `id, f_table_catalog, f_table_schema, f_table_name, f_geometry_column, styleName, styleQML, styleSLD, useAsDefault, description, owner, ui, update_time`; 1 hàng `('unit','unit_style',useAsDefault=1)`; **không có hàng nào trong `gpkg_extensions`** ngoài RTree |
| `setSubsetString("\"level_id\" = 'L1'")` | áp dụng được, đếm lại feature |

## Chưa xác minh (thao tác giao diện, để TASK-011)
- Hộp thoại chọn sublayer khi mở GPKG nhiều layer; vị trí menu "Layer → Add Layer → Add Vector Layer", kéo thả vào Browser; "Save Style → In Database (GeoPackage)" trong Layer Properties.
- Cách tốt nhất lọc theo tầng khi xem nhiều tầng (variable-based filter vs Temporal Controller vs Atlas); Temporal Controller cho dữ liệu không phải thời gian.
- Cảnh báo khoá SQLite / file `-wal`/`-shm` khi ghi script lúc QGIS đang mở (kiến thức nền, chưa thử).
- Ảnh chụp màn hình lưu trong `docs/` (do synthesizer hoặc TASK-011).

## Liên quan đến pipeline CAD → BIM → GPKG
- Nên ghi sẵn style cho `unit` (theo `category`), `opening`, `level` (qua `.qml` hoặc `layer_styles`).
- Thêm cột dễ đọc (`level_ordinal` bản sao trên unit) để lọc nhanh mà không cần join — vi phạm chuẩn hoá; cột lạ phải loại khi xuất IMDF (xem `imdf-relations-and-constraints.md`, mục extension).
- Bảng attributes xem được trong QGIS như bảng không hình học; không cần xử lý đặc biệt.

## Nguồn
- Thực nghiệm PyQGIS/QGIS 3.44.7 (hệ thống `/usr/bin/python3`, `QT_QPA_PLATFORM=offscreen`) — 2026-11-06; script không lưu trong repo.
- [QGIS manual — Opening data](https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/opening_data.html) — HTTP 200 truy cập được 2026-11-06, **chưa đọc nội dung**.

## Câu hỏi còn mở
- Xác nhận các thao tác GUI bằng TASK-011; đối chiếu bản docs QGIS khi cần trích dẫn.
