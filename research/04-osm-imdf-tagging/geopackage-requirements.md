# GeoPackage hợp lệ — yêu cầu và lưu ý cho dữ liệu IMDF

- **Câu hỏi nghiên cứu**: Một .gpkg hợp lệ cần gì, và có điểm nào trong mục 3.3 bước 5 cần chỉnh?
- **Kết luận ngắn**: GPKG là SQLite với `application_id = 0x47504B47`, bảng `gpkg_spatial_ref_sys` (tối thiểu 3 dòng: -1, 0, 4326), `gpkg_contents`, `gpkg_geometry_columns`. RTree là *extension* (`gpkg_rtree_index`), GDAL bật mặc định. IMDF feature không có geometry nên là bảng thuộc tính; mảng/object phải lưu JSON text.
- **Độ tin cậy**: trung bình-thấp — xác nhận được application_id và 3 dòng SRS qua đoạn trích; phần còn lại là kiến thức nền **[chưa xác minh]** (docs.ogc.org, geopackage.org, gdal.org không truy cập được).

## Chi tiết

### Yêu cầu lõi
- SQLite 3, `PRAGMA application_id = 0x47504B47` ("GPKG") — xác nhận. `user_version` mã hoá phiên bản (vd 10300 cho 1.3.0) — chưa xác minh.
- `gpkg_spatial_ref_sys`: tối thiểu 3 dòng srs_id = 4326 (WGS84), -1 (undefined Cartesian), 0 (undefined geographic) — xác nhận (guidance + test crate). CRS khác (vd 32648, 4756…) phải được thêm vào bảng này (GDAL tự thêm).
- `gpkg_contents`: mỗi layer có dòng với `table_name`, `data_type` (`features` | `attributes` | `tiles`), `identifier`, `srs_id`, bbox (min_x…).
- `gpkg_geometry_columns`: một dòng cho mỗi feature table (`table_name`, `column_name`, `geometry_type_name`, `srs_id`, `z`, `m`).
- Bảng features: có khoá chính integer (thường `fid`) và cột geometry dạng blob GeoPackageBinary (header "GP", version, flags, srs_id, envelope tuỳ chọn, rồi WKB) **[chưa xác minh chi tiết]**.
- Một cột geometry chỉ có 1 kiểu khai báo (POLYGON, MULTIPOLYGON, LINESTRING, POINT hoặc GEOMETRY).
- Bảng thuộc tính (không geometry): `data_type='attributes'` trong `gpkg_contents`, không có dòng trong `gpkg_geometry_columns`.
- Extension khai báo trong `gpkg_extensions`; RTree: bảng ảo `rtree_<table>_<geomcol>` + trigger, khai báo `gpkg_rtree_index`. `layer_styles` là quy ước của QGIS/GDAL, không thuộc spec lõi **[chưa xác minh]**.

### Đối chiếu bước 5 trong PRIMARY_OBJECTIVE
| Mục trong bước 5 | Nhận xét |
|---|---|
| Gán CRS cho mọi layer (EPSG:4326) | Đúng. IMDF/GeoJSON cần WGS84; nếu muốn dùng CRS địa phương (VN-2000) thì layer export IMDF vẫn phải chuyển về 4326. |
| `make_valid`, đúng kiểu, không rỗng | Đúng; lưu ý `make_valid` có thể trả GeometryCollection/MultiPolygon → ép về kiểu cột. |
| Mỗi IMDF feature type = một layer | Đúng, nhưng `building`, `address`, `relationship` không có geometry → ghi thành bảng attributes (`geopandas` cần `ogr` với geometry None; pyogrio có thể ghi bảng không geometry — [chưa xác minh] cách làm). |
| Tag OSM ở cột riêng hoặc cột `tags` JSON | Khả thi; GPKG không có kiểu mảng/map; OGR có subtype JSON (từ GDAL 3.x — phiên bản chưa xác minh) hoặc lưu TEXT. |
| "GPKG tự tạo RTree" | Chỉ đúng với GDAL (`SPATIAL_INDEX=YES` mặc định); theo spec RTree là extension tuỳ chọn. Cần kiểm `gpkg_extensions` sau khi ghi. |
| Bảng `gpkg_contents`/`gpkg_geometry_columns` hợp lệ | Đúng; kiểm bằng `ogrinfo -al -so`, `PRAGMA integrity_check`, `PRAGMA foreign_key_check` ([chưa xác minh] tên kiểm tra chính thức; có thể dùng validator OGC/`gpkg` test). |

### Lưu ý thiết kế riêng
- `fid` (integer) khác IMDF `id` (UUID): thêm cột `id TEXT UNIQUE`.
- `name` IMDF là object nhãn đa ngôn ngữ `{"en": "…"}` → cột JSON text; `building_ids`, `unit_ids` → JSON mảng text.
- Tên cột `feature_type` có thể giữ để xuất ngược ra GeoJSON IMDF.
- Giữ geometry 2D (IMDF GeoJSON 2D); thông tin cao độ lưu trong `ordinal`/cột riêng.
- Không dùng tên bảng có ký tự đặc biệt; tên bảng GPKG = tên feature type IMDF (`unit`, `level`…).

## Liên quan đến pipeline CAD → BIM → GPKG
Quyết định: (1) ghi bằng GDAL/pyogrio ở driver GPKG, (2) kiểm sau ghi: `application_id`, SRS, `gpkg_contents`, `gpkg_geometry_columns`, RTree, (3) FK kiểm bằng test riêng (xem `imdf-relations-and-constraints.md`).

## Nguồn
- [GeoPackage — Getting started](https://www.geopackage.org/guidance/getting-started) — 2026-11-06 (đoạn trích)
- [Rust crate geopackage test container.rs](https://docs.rs/crate/geopackage/0.3.0/source/tests/container.rs) — 2026-11-06 (đoạn trích)
- [OGC GeoPackage 12-128r19](https://docs.ogc.org/is/12-128r19/12-128r19.html) — chưa đọc được
- [GDAL GPKG driver](https://gdal.org/en/stable/drivers/vector/gpkg.html) — chưa đọc được

## Câu hỏi còn mở
- Số phiên bản `user_version` hiện hành (1.3.x/1.4.x?), danh sách requirement bắt buộc đánh số.
- Cách ghi bảng không geometry bằng geopandas/pyogrio; subtype JSON theo phiên bản GDAL.
- Công cụ validate GPKG chính thức nào dùng được offline.
