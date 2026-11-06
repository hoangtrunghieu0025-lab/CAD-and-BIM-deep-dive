# Kiểm tra `.gpkg` trong QGIS (TASK-011)

> Kiểm bằng **QGIS 3.44.7** qua PyQGIS (không mở giao diện), trên bản sao của `samples/out/sample-dxf.gpkg`. Các ảnh trong `docs/assets/qgis-0*.png` do **engine QGIS dựng**, **không phải ảnh chụp cửa sổ** (máy không có công cụ chụp màn hình). Phần kiểm bằng giao diện thật và nền bản đồ còn chờ chủ dự án (mục 6).

## 1. Layer nạp được

| Layer | Hợp lệ | CRS | Số dòng | Kiểu |
|---|---|---|---|---|
| `venue` | có | EPSG:4326 | 1 | Polygon |
| `footprint` | có | EPSG:4326 | 1 | Polygon |
| `level` | có | EPSG:4326 | 2 | Polygon |
| `unit` | có | EPSG:4326 | 26 | Polygon |
| `opening` | có | EPSG:4326 | 24 | LineString |
| `address`, `building` | có | — | 1 mỗi bảng | không geometry (bảng thuộc tính) |

Bảng không geometry (`address`, `building`) được QGIS nhận là bảng thuộc tính, như thiết kế.

## 2. Vị trí

- Gốc cục bộ `(0,0)` được đặt tại E=588000, N=2325000 (EPSG:3405) trong `samples/project-dxf.yaml`. QGIS đổi ra **lon 105.8487265, lat 21.0226788** (khoảng Hà Nội, toạ độ minh hoạ).
- Extent của `unit` là lon 105.8487265–105.8489581, lat 21.0226776–21.0227872 và **chứa** điểm gốc đó → vị trí khớp số liệu.
- Kích thước toà nhà trên bản đồ khớp 24 × 12 m.
- **Chưa kiểm với nền bản đồ**: `tile.openstreetmap.org` không truy cập được từ máy chạy kiểm tra (`curl` mã `000`). Cần kiểm bằng QGIS thật (mục 6).

## 3. Lọc theo tầng

| Tầng (`ordinal`) | unit | opening |
|---|---|---|
| 0 (TẦNG 1) | 13 | 12 |
| 1 (TẦNG 2) | 13 | 12 |

Lọc bằng biểu thức `"level_id" = '<id của level>'`. Tổng 26 unit và 24 opening khớp bảng gốc.

## 4. Style (`config/qgis/*.qml`)

| File | Cách tô |
|---|---|
| `unit.qml` | phân loại theo `category` (`room` xanh nhạt, `walkway` vàng nhạt, `restroom`, `stairs`, `elevator`, `structure`, `column` có màu riêng, còn lại xám); nhãn = `coalesce("osm_ref","osm_name")` |
| `opening.qml` | đoạn đỏ dày theo `category` (`pedestrian` đỏ, `emergencyexit` xanh lá) |
| `level.qml` | chỉ viền xanh dương, không tô |
| `footprint.qml` | chỉ viền đen mảnh |
| `venue.qml` | viền cam nét đứt, nền vàng rất nhạt |

Cả 5 file nạp lại được bằng `loadNamedStyle` (kiểm lại trên layer mới: `unit` và `opening` là `categorizedSymbol`, `unit` bật nhãn).

## 5. Ảnh (dựng bằng QGIS)

| File | Nội dung |
|---|---|
| `docs/assets/qgis-01-overview.png` | toàn cảnh: venue, footprint, level, unit, opening (cả 2 tầng chồng nhau) |
| `docs/assets/qgis-02-floor1-categories.png` | tầng 1: 12 phòng P101–P112, hành lang, 12 cửa |
| `docs/assets/qgis-03-floor2.png` | tầng 2 |
| `docs/assets/qgis-04-unit-attribute-table.png` | bảng thuộc tính `unit` (12 dòng đầu) |

## 6. Vấn đề tìm thấy

1. **Hai tầng chồng khít khi không lọc.** Cả hai tầng cùng footprint nên ở ảnh toàn cảnh nhãn lẫn (P101, P207, P108…). Muốn xem một tầng phải lọc theo `level_id` (hoặc `osm_level`). Đề xuất: khi người dùng thật mở file, dùng bộ lọc/rule theo `level`; chưa có file `.qgz` dựng sẵn.
2. **QGIS làm thay đổi file khi mở.** Sau khi mở `samples/out/sample-dxf.gpkg` trong QGIS thì git thấy file bị sửa (đã khôi phục bằng `git checkout`). Khi thử nên mở **bản sao**. Chưa xác định nguyên nhân (nghi QGIS cập nhật chế độ journal/metadata).
3. **`setSubsetString` khi mở nhiều layer cùng một GPKG** (chế độ không giao diện): `featureCount()` trả `-1` kèm lỗi "unable to open database file" và ảnh dựng ra trống; lọc khai báo trong URI (`|subset=…`) hoạt động bình thường. Chưa rõ có gặp trong QGIS giao diện không; nếu gặp thì dùng bộ lọc trong hộp thoại Layer Properties hoặc rule-based style.
4. **Hiển thị trong EPSG:4326 hơi méo**: 1° kinh độ ngắn hơn 1° vĩ độ ở vĩ độ 21° (hệ số ≈ 0,93) và lưới UTM nghiêng nhẹ (hội tụ kinh tuyến), nên phòng 4×5 m trông cao hơn và mép nghiêng. Đặt **CRS dự án là EPSG:3405** (VN-2000 / UTM 48N) để xem đúng tỉ lệ; dữ liệu vẫn nằm ở 4326.
5. **Cột `name` của `unit` rỗng với DXF** (nhãn chỉ có mã phòng); nhãn hiển thị dùng `osm_ref`. Với hành lang dùng `osm_name`.
6. **Nền OSM không tải được** ở máy kiểm tra (không với tới `tile.openstreetmap.org`); chưa kiểm vị trí trên nền bản đồ thật.
7. PyQGIS không giao diện báo lỗi phân đoạn (segfault) lúc thoát; không ảnh hưởng kết quả (mọi ảnh và số liệu đã ghi xong trước đó).

## 7. Việc còn lại cho chủ dự án (QGIS thật)

1. Mở QGIS, **Layer → Add Layer → Add Vector Layer**, chọn **bản sao** của `samples/out/sample-dxf.gpkg`, chọn tất cả 7 layer.
2. Đặt CRS dự án = EPSG:3405; thêm nền XYZ (OpenStreetMap hoặc nền khác) ở dưới cùng; **zoom tới layer `venue`** và xem toà nhà có nằm ở khu vực Hà Nội không.
3. Với mỗi layer: chuột phải → Properties → Style → **Load Style** → chọn file `.qml` cùng tên trong `config/qgis/`.
4. Lọc tầng: Layer Properties → **Source → Query Builder**, đặt `"level_id" = '<id của level tầng 1>'` cho `unit`, `opening`, `level`.
5. Chụp 3 ảnh: **toàn cảnh có nền**, **một tầng đã lọc có nhãn**, **bảng thuộc tính** (F6) và bỏ vào `docs/assets/` (tên bắt đầu `qgis-gui-`); tránh để lộ thanh tab/thông tin cá nhân của trình duyệt.
