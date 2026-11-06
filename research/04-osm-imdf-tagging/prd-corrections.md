# Chỉnh PRIMARY_OBJECTIVE.md — bảng ĐÃ CHỐT (TASK-012)

- **Câu hỏi nghiên cứu**: Dòng nào trong bảng OSM/IMDF/GPKG (mục 3.3 bước 4–5) cần sửa theo nguồn gốc?
- **Kết luận ngắn**: Đã đối chiếu với trang gốc OSM wiki, Apple IMDF, spec GeoPackage và thực nghiệm. **Không sửa `PRIMARY_OBJECTIVE.md`** (chưa được chủ dự án cho phép) — đây là đề xuất đã xác minh để claude-mobile/chủ dự án áp dụng.
- **Độ tin cậy**: cao (mỗi dòng có URL + ngày truy cập 2026-11-06).
- **Trạng thái xác minh**: ĐÃ XÁC MINH (TASK-012, claude-laptop). Hai dòng mobile nghi ngờ nhưng **nay xác định là chưa chính xác** được ghi rõ ở cột "Ghi chú đính chính".

## Bảng đối chiếu

| Dòng trong PRIMARY_OBJECTIVE.md | Kết luận đã xác minh | Ghi chú đính chính so với bản đề xuất vòng 2 | URL gốc |
|---|---|---|---|
| 4a Tầng: `level`, `level:ref`, `repeat_on` | **Đúng.** `repeat_on` chỉ trên node, không gồm tầng khởi đầu; `level` bắt buộc trên mọi phần tử indoor; `min_level`/`max_level` trên building | — | https://wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging |
| 4a Phòng `indoor=room` | **Đúng**; mục đích bằng `room=*` | — | cùng trang |
| 4a Hành lang `indoor=corridor` | **Đúng** | — | cùng trang |
| 4a Tường `indoor=wall` | **Đúng**; ưu tiên way theo đường tim tường | — | cùng trang |
| 4a Cửa `door=*`, `entrance=*` | **Thiếu**: cửa nội bộ = node `indoor=door` + `door=*`; lối vào toà nhà = `entrance=*` (+ `door=*`) | xác nhận đề xuất | cùng trang |
| 4a Cầu thang `highway=steps` | **Chưa đúng cho khu cầu thang**: dùng area `stairs=yes` + `indoor=room\|area`; `highway=steps` **có trong SIT** nhưng chỉ cho từng flight (way) | **Đính chính**: vòng 2 ghi "chưa thấy trong SIT" — thực tế SIT có mục "Steps" dùng `highway=steps` | cùng trang; https://wiki.openstreetmap.org/wiki/Tag:highway=steps |
| 4a Thang máy `highway=elevator` | **Đúng**; area + `area=yes` + `indoor=room\|area`; cửa là node `indoor=door`/`entrance` + `repeat_on` thuộc area | — | https://wiki.openstreetmap.org/wiki/Tag:highway=elevator |
| 4a thiếu | `indoor=level` (outline tầng, tuỳ chọn), `min_level`/`max_level`, `non_existent_levels`, `room=*` | `indoor=level` xác nhận tồn tại (redirect về SIT) | SIT |
| 4b `building` | geometry **null**; polygon ở `footprint` | xác nhận | https://register.apple.com/resources/imdf/types/building |
| 4b `opening` | geometry **LineString**; `door` null hoặc object | xác nhận | https://register.apple.com/resources/imdf/types/opening |
| 4b tường = `fixture` | **Sai**: tường floor-to-ceiling **MUST** là `unit` category `structure` (vật liệu `brick`/`concrete`/`drywall`/`glass`/`wood` tuỳ chọn); `fixture` = tài sản di động/bán cố định | **Đính chính**: `fixture` có category `wall` nhưng không phải cho tường kết cấu (suy luận từ định nghĩa; xem `imdf-feature-types.md`) | https://register.apple.com/resources/imdf/types/unit , .../fixture |
| 4b thiếu feature | IMDF 1.0.0 có **16** feature type; bảng thiếu `geofence`, `kiosk`, `relationship`, `section`; gói cần `manifest.json`; **bắt buộc** chỉ `manifest.json`, `address.geojson`, `venue.geojson` | xác nhận cả 16 tên | https://register.apple.com/resources/imdf/ ; .../reference/reference |
| 4b `level` cột | `category`, `outdoor`, `ordinal`, `name`, `short_name` (name & short_name **bắt buộc**), `building_ids` nullable | bổ sung nullable | https://register.apple.com/resources/imdf/types/level |
| 4b khoá ngoại `level.building_ids → building.id` | **Đúng** (mảng, nullable) | — | cùng trang level |
| 4b `occupant`, `detail`, `fixture` geometry | `occupant` = **null** (bản cũ ghi Point); `detail` = LineString; `fixture` = Polygon | **Đính chính** `imdf-feature-types.md` bản cũ | trang `types/occupant`, `detail`, `fixture` |
| 4b thiếu `venue` / `address` | `venue` (Polygon) và `address` là **bắt buộc** trong gói; mọi feature phải nằm trong venue | mới | .../reference/reference ; .../types/venue |
| Bước 5 "GPKG tự tạo RTree" | Chỉ đúng với GDAL; theo spec RTree là extension `gpkg_rtree_index`; tắt bằng `SPATIAL_INDEX=NO` | xác nhận bằng thực nghiệm | https://www.geopackage.org/spec/ |
| Bước 5 IMDF feature không geometry | Ghi thành bảng `attributes` bằng `pyogrio.write_dataframe(DataFrame thường)` (đã chạy thật). **Không** dùng GeoDataFrame `geometry=[None]` nếu muốn bảng attributes | cụ thể hoá | — (thực nghiệm; xem `geopackage-requirements.md`) |

## Câu hỏi còn mở
- Định nghĩa đầy đủ của Manifest object (chỉ có ví dụ); validator IMDF chính thức; mô tả ngữ nghĩa từng category.
- Chủ dự án quyết định có sửa `PRIMARY_OBJECTIVE.md` mục 3.3 theo bảng trên không (claude-laptop không có quyền sửa).
