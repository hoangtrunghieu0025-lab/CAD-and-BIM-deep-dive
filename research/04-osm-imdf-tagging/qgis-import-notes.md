# Import GPKG IMDF vào QGIS — ghi chú

- **Câu hỏi nghiên cứu**: QGIS đọc GPKG nhiều layer, bảng không geometry và style như thế nào?
- **Kết luận ngắn**: QGIS đọc GPKG qua OGR; file nhiều layer hiện hộp thoại chọn sublayer; bảng attributes hiện như bảng không geometry; style có thể lưu trong bảng `layer_styles` của GPKG. Toàn bộ nội dung ở đây là kiến thức nền, chưa có nguồn gốc xác minh.
- **Độ tin cậy**: thấp — `docs.qgis.org` và `gdal.org` không truy cập được trong phiên này; mọi mục đánh dấu **[chưa xác minh]**.

## Chi tiết (tất cả [chưa xác minh])
- Mở: Layer → Add Layer → Add Vector Layer, hoặc kéo thả vào Browser panel; với GPKG nhiều layer QGIS hỏi chọn sublayer. Bảng attributes (building, address, relationship) có thể thêm như bảng không geometry.
- CRS: layer dùng CRS lưu trong `gpkg_geometry_columns`/`gpkg_spatial_ref_sys`; kiểm trong Layer Properties → Information. Bản đồ nền (XYZ OpenStreetMap) ở EPSG:3857, QGIS reproject nhanh.
- Style: Layer Properties → Style → Save as Default / "Save Style → In Database (GeoPackage)" ghi vào bảng `layer_styles`; mở lại GPKG sẽ nạp style mặc định. Phân loại theo `category` (Categorized renderer), lọc tầng bằng Provider Feature Filter (`"level_id" = '<uuid>'`) hoặc theo `ordinal` qua join; giá trị JSON hiển thị như text.
- Lọc nhiều tầng: dùng filter dựa trên biến/điều kiện hoặc Temporal Controller (dữ liệu không phải thời gian — dùng với cột số có thể; cách này cần thử nghiệm).
- Kiểm tra bằng ảnh chụp màn hình lưu trong `docs/` (do synthesizer).
- GPKG nhiều writer đồng thời: QGIS giữ khoá SQLite; tránh ghi từ script khi đang mở (WAL file `-wal`/`-shm`) — kiến thức nền.

## Liên quan đến pipeline CAD → BIM → GPKG
- Nên ghi sẵn style `.qml` hoặc `layer_styles` cho `unit` (theo category), `opening`, `level`.
- Thêm cột dễ đọc (`level_ordinal` bản sao trên unit) để lọc nhanh trong QGIS mà không cần join — vi phạm chuẩn hoá nhưng tiện; cần thống nhất với IMDF (cột lạ có thể bị consumer từ chối nếu xuất IMDF).

## Nguồn
- [QGIS manual — Opening data](https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/opening_data.html) — chưa đọc được (2026-11-06)
- [GDAL GPKG driver](https://gdal.org/en/stable/drivers/vector/gpkg.html) — chưa đọc được (2026-11-06)

## Câu hỏi còn mở
- Xác minh toàn bộ ghi chú trên bằng tài liệu QGIS khi domain được mở, hoặc bằng thử nghiệm thực tế trong TASK triển khai.
- Cách tốt nhất lọc theo tầng (Temporal Controller vs variable-based filter vs Atlas).
