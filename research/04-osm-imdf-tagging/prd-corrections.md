# Đề xuất chỉnh PRIMARY_OBJECTIVE.md — TASK-005 (vòng 2)

- **Câu hỏi nghiên cứu**: Dòng nào trong bảng OSM/IMDF (mục 3.3 bước 4–5) cần sửa theo nguồn gốc?
- **Kết luận ngắn**: Vòng 2 KHÔNG xác minh được thêm gì: `wiki.openstreetmap.org`, `register.apple.com`, `www.geopackage.org`, `gdal.org`, `docs.qgis.org` vẫn trả `getaddrinfo ENOTFOUND` (thử 2026-11-06, WebFetch) nên chưa thể đọc trang gốc. Bảng dưới là đề xuất dựa trên kết quả vòng 1 (đoạn trích tìm kiếm + repo GitHub), tất cả giữ nhãn **chưa xác minh từ trang gốc**. Không sửa PRIMARY_OBJECTIVE.md.
- **Độ tin cậy**: thấp-trung bình.

## Bảng đối chiếu

| Dòng trong PRIMARY_OBJECTIVE.md | Nội dung đề xuất (theo bằng chứng vòng 1) | Trạng thái | URL cần đọc để chốt |
|---|---|---|---|
| 4a Tầng: `level`, `level:ref`, `repeat_on` | Các tag tồn tại; `repeat_on` không gồm tầng gốc | đoạn trích, chưa xác minh | https://wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging |
| 4a Phòng: `indoor=room` | Đúng; thêm `room=*` cho mục đích | đoạn trích | cùng trang trên |
| 4a Tường: `indoor=wall` | Đúng | đoạn trích | cùng trang trên |
| 4a Cửa: `door=*`, `entrance=*` | Thiếu `indoor=door` (cửa trong nhà); `entrance=*` cho lối vào toà nhà | đoạn trích | cùng trang trên |
| 4a Cầu thang: `highway=steps` | Theo SIT là `stairs=yes` + `indoor=room/area`; `highway=steps` là tag OSM chung | đoạn trích | cùng trang trên; https://wiki.openstreetmap.org/wiki/Tag:highway=steps |
| 4a Thang máy: `highway=elevator` | Có thật; kèm `indoor=room/area` | đoạn trích | https://wiki.openstreetmap.org/wiki/Tag:highway=elevator |
| 4a thiếu | `indoor=level`, `min_level`/`max_level` | chưa xác minh | https://wiki.openstreetmap.org/wiki/Tag:indoor=level |
| 4b `building` | Geometry null; polygon ở `footprint` | đoạn trích (Apple/OGC) | https://register.apple.com/resources/imdf/types/building |
| 4b `opening` | Geometry LineString, `door` là object/null | đoạn trích | https://register.apple.com/resources/imdf/types/opening |
| 4b `fixture` = tường | Nhiều khả năng sai: tường dùng `unit` category vật liệu | chưa xác minh (trí nhớ + bên thứ ba) | https://register.apple.com/resources/imdf/types/unit , .../fixture |
| 4b thiếu feature | `geofence`, `kiosk`, `relationship`, `section` (tổng 16) và `manifest.json` | số 16 từ đoạn trích; tên chưa xác minh | https://register.apple.com/resources/imdf/ |
| 4b `level` cột | `ordinal`, `short_name`, `outdoor` có thật | đoạn trích | https://register.apple.com/resources/imdf/types/level |
| 4b khoá ngoại `level.building_ids` | Đúng (mảng) | chưa xác minh | cùng trang level |
| Bước 5 "GPKG tự tạo RTree" | Chỉ đúng với GDAL; theo spec RTree là extension | kiến thức nền | https://www.geopackage.org/spec/ ; https://gdal.org/en/stable/drivers/vector/gpkg.html |
| Bước 5 IMDF feature không geometry | Ghi thành bảng attributes | kiến thức nền | GDAL GPKG driver |

## Câu hỏi còn mở
- Cần allow 5 domain trong network settings của session rồi chạy lại vòng xác minh.
