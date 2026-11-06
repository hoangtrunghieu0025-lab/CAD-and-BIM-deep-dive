# GeoPackage hợp lệ — yêu cầu và lưu ý cho dữ liệu IMDF

- **Câu hỏi nghiên cứu**: Một .gpkg hợp lệ cần gì, ghi bằng `pyogrio`/`geopandas` ra sao, và có điểm nào trong mục 3.3 bước 5 cần chỉnh?
- **Kết luận ngắn**: GPKG là SQLite với `application_id = 0x47504B47` ("GPKG") và `user_version` 5 chữ số `MMmmPP` (1.3.0 → 10300; quan sát: GDAL 3.12.4 ghi `10400`, GDAL 3.8.4 hệ thống ghi `10200`). `gpkg_spatial_ref_sys` tối thiểu 3 dòng (4326, −1, 0). **RTree là extension** `gpkg_rtree_index` (đăng ký trong `gpkg_extensions`); GDAL tạo mặc định, tắt bằng layer option `SPATIAL_INDEX=NO`. Bảng không geometry = `data_type='attributes'`. **`layer_styles` không thuộc spec**, do QGIS/GDAL tạo.
- **Độ tin cậy**: **cao** — đối chiếu spec OGC GeoPackage 1.4 (`geopackage.org/spec/`) và chạy thực nghiệm (GDAL 3.12.4 qua `pyogrio` 0.13.0, GDAL 3.8.4 `ogrinfo`, QGIS 3.44.7), 2026-11-06.
- **Trạng thái xác minh**: ĐÃ XÁC MINH (TASK-012, claude-laptop). Các mục "chưa xác minh" cuối file.

## Chi tiết

### Yêu cầu lõi (đã xác minh từ spec 1.4)
- `application_id` = 0x47504B47 (= 1196444487); `user_version` là số nguyên 5 chữ số major·2 chữ số minor·2 chữ số bug-fix, ví dụ 1.3.0 → 0x283C (10300). Test của spec: fail nếu `user_version < 10200`.
- `gpkg_spatial_ref_sys` phải chứa tối thiểu: `srs_id=4326` (WGS-84, EPSG), `-1` ("undefined" Cartesian), `0` ("undefined" geographic). Quan sát thực tế: file mới ghi bằng GDAL có đúng 3 dòng này `[(-1,'NONE',-1),(0,'NONE',0),(4326,'EPSG',4326)]`.
- `gpkg_contents.data_type`: `features` | `attributes` | `tiles` (hoặc giá trị của extension). "SHALL contain a row with data_type `attributes` for each attributes data table".
- `gpkg_geometry_columns`: 1 dòng/feature table (`table_name`, `column_name`, `geometry_type_name`, `srs_id`, `z`, `m`).
- Geometry blob = `GeoPackageBinary`: header magic `0x4750` ("GP"), version, flags, srs_id, envelope tuỳ chọn, rồi WKB.
- Extension: mỗi hàng `gpkg_extensions` có `extension_name` dạng `<author>_<name>`, ký tự `[a-zA-Z0-9_]`. RTree: `extension_name='gpkg_rtree_index'`, một hàng cho mỗi cột geometry được index, scope `write-only`.
- `layer_styles`: **0 lần xuất hiện trong spec** → không phải chuẩn; do QGIS (và GDAL) tạo.

### Quan sát thực nghiệm (ghi bằng `geopandas.to_file` / `pyogrio.write_dataframe`, driver GPKG)
Môi trường: `pyogrio 0.13.0` (kèm GDAL **3.12.4**), `geopandas 1.2.0`; `ogrinfo` hệ thống là GDAL **3.8.4**, QGIS **3.44.7**.
| Phép thử | Kết quả |
|---|---|
| GeoDataFrame polygon, crs=4326 | bảng `unit`: PK `fid INTEGER`, cột geometry tên **`geom`** kiểu khai báo `POLYGON`, `gpkg_contents.data_type='features'`, `srs_id=4326`; `gpkg_extensions` có hàng `gpkg_rtree_index` + bảng `rtree_unit_geom*` (tự tạo) |
| `PRAGMA integrity_check` / `foreign_key_check` | `ok` / rỗng |
| GeoDataFrame với `geometry=[None]` (geopandas) | **không** thành bảng attributes: thành `features` kiểu `GEOMETRY` (kèm RTree) với geometry NULL; srs_id vẫn 4326 |
| `pyogrio.write_dataframe(pd.DataFrame thường, ...)` | thành bảng **`attributes`**: `gpkg_contents.data_type='attributes'`, `srs_id=0`, không có hàng trong `gpkg_geometry_columns` — **cách đúng cho feature IMDF không geometry** (building, address, occupant…) |
| Cột JSON (chuỗi `json.dumps`) | lưu thành `TEXT` (GDAL không tự gán subtype JSON ở đây); mảng/object IMDF (`building_ids`, `name`) lưu JSON text |
| `layer_options={"SPATIAL_INDEX":"NO"}` | không tạo RTree; `gpkg_extensions` thậm chí **không được tạo** → xác nhận RTree là tuỳ chọn |
| `user_version` theo phiên bản GDAL | GDAL 3.12.4 (pyogrio) → `10400` (GPKG 1.4.0); GDAL 3.8.4 (`ogr2ogr` hệ thống) → `10200` (1.2.0); cả hai `application_id=0x47504b47`, đều ≥ 10200 nên qua test của spec |
| Đọc lại | `ogrinfo -so -al` (GDAL 3.8.4): `FID Column = fid`, `Geometry Column = geom`, `Geometry: Polygon`, CRS `ID["EPSG",4326]`; file ghi bởi GDAL mới hơn đọc được bằng GDAL/QGIS cũ hơn |

### Đối chiếu bước 5 trong PRIMARY_OBJECTIVE
| Mục trong bước 5 | Nhận xét (đã xác minh) |
|---|---|
| Gán CRS EPSG:4326 cho mọi layer | Đúng; IMDF dùng GeoJSON (RFC 7946, WGS84) nên xuất IMDF cần 4326. Layer attributes có `srs_id=0`. |
| `make_valid`, đúng kiểu, không rỗng | Đúng (đề xuất của dự án); `make_valid` có thể sinh GeometryCollection/Multi* → ép về kiểu cột trước khi ghi, vì cột khai báo 1 kiểu. |
| Mỗi IMDF feature type = một layer | Đúng; `building`, `address`, `occupant`, (`relationship`) geometry null → ghi bằng `pyogrio.write_dataframe` với DataFrame thường (attributes). |
| Tag OSM ở cột riêng hoặc cột `tags` JSON | Khả thi; mọi kiểu mảng/map lưu `TEXT`. Tránh `:` trong tên cột (`level:ref`) → dùng `level_ref`. |
| "GPKG tự tạo RTree" | **Chỉ đúng với GDAL** (mặc định `SPATIAL_INDEX=YES`); theo spec đó là extension `gpkg_rtree_index`. |
| `gpkg_contents` / `gpkg_geometry_columns` hợp lệ | Kiểm bằng `ogrinfo -al -so` + truy vấn SQLite (`application_id`, SRS, contents, geometry_columns, extensions) + `PRAGMA integrity_check`. |

### Lưu ý thiết kế riêng
- `fid` (INTEGER PK) khác IMDF `id` (UUID): thêm cột `id TEXT`, có thể đánh `UNIQUE`.
- `name` IMDF là LABELS (object ngôn ngữ→chuỗi) → JSON text; `building_ids`, `unit_ids` → JSON mảng text.
- Giữ cột `feature_type` để xuất ngược GeoJSON IMDF; geometry 2D, cao độ nằm trong `ordinal`.
- Hai phiên bản GDAL cùng tồn tại trên máy (venv `pyogrio` GDAL 3.12.4 và hệ thống 3.8.4); pipeline ghi bằng venv, QGIS đọc bằng thư viện hệ thống — đã thử, tương thích.

## Liên quan đến pipeline CAD → BIM → GPKG
(1) ghi bằng `geopandas`/`pyogrio` driver GPKG; (2) feature không geometry → `pyogrio.write_dataframe` với DataFrame thường; (3) kiểm sau ghi bằng test tự động: `application_id`, 3 dòng SRS tối thiểu, `gpkg_contents.data_type` đúng, `gpkg_geometry_columns` khớp, `integrity_check`, `foreign_key_check`; (4) FK IMDF kiểm bằng test riêng (xem `imdf-relations-and-constraints.md`).

## Nguồn
- [OGC GeoPackage Encoding Standard 1.4 (HTML)](https://www.geopackage.org/spec/) — 2026-11-06 (đọc trực tiếp; cũng tải `https://www.geopackage.org/spec140/` và `.../spec131/`)
- Thực nghiệm: `pyogrio 0.13.0`/GDAL 3.12.4, `geopandas 1.2.0`, `ogrinfo` GDAL 3.8.4, `sqlite3` — 2026-11-06 (script chạy trong phiên TASK-012, không lưu trong repo)

## Chưa xác minh / câu hỏi mở
- Danh sách requirement bắt buộc đánh số theo spec, và validator GPKG chính thức dùng offline (chưa tìm/chạy).
- Subtype JSON của OGR theo phiên bản GDAL (ở đây cột chuỗi vẫn là TEXT); `gdal.org` trả 429 (rate limit) khi thử nên chưa đọc trang driver GPKG.
