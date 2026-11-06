---
id: TASK-011
title: "[IN_REVIEW][MAIN] Kiểm tra .gpkg trong QGIS và chụp ảnh"
category: MAIN
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T17:22:01+07:00
status: in_review
priority: normal
depends_on: [TASK-010]
---

# [IN_REVIEW][MAIN] TASK-011 — Kiểm tra .gpkg trong QGIS và chụp ảnh

## Mô tả
Mở `.gpkg` đầu ra trong QGIS, kiểm tra vị trí, CRS, lọc theo tầng, style theo `category`; tạo style và ảnh để mobile xem được trên điện thoại.

## Đầu vào (inputs)
- `.gpkg` từ TASK-010

## Đầu ra mong đợi (expected_outputs)
- `docs/qgis-verification.md`: kết quả kiểm tra và vấn đề tìm thấy
- `docs/assets/*.png`: ảnh chụp màn hình
- `config/qgis/*.qml` (style)

## Tiêu chí hoàn thành (acceptance)
- [ ] Tất cả layer load đúng CRS và đúng vị trí trên bản đồ nền — CRS và vị trí khớp số liệu (đã kiểm); **phần 'trên bản đồ nền' chưa kiểm** (nền OSM không với tới được); chờ chủ dự án kiểm trong QGIS thật
- [ ] Có ≥3 ảnh chụp (toàn cảnh, một tầng, bảng thuộc tính) — có 4 ảnh dựng bằng engine QGIS (không phải ảnh chụp giao diện); chờ ảnh GUI thật của chủ dự án
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; ghi vào `docs/qgis-verification.md`, `docs/assets/`, `config/qgis/`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | in_review | 2026-11-06T16:38:02+07:00 | kiểm bằng PyQGIS xong; chờ chủ dự án kiểm trong QGIS thật (nền bản đồ, ảnh chụp GUI) |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T16:32:55+07:00 | in_progress | Nhận task (TASK-010 đã DONE). Không có công cụ chụp màn hình trên máy; dùng PyQGIS để nạp layer, tạo style `.qml` và dựng ảnh bản đồ/bảng thuộc tính. |
| 2026-11-06T16:38:02+07:00 | in_review | **Kiểm bằng QGIS 3.44.7 (PyQGIS, không giao diện) trên bản sao `sample-dxf.gpkg`.** 5 layer có geometry + 2 bảng thuộc tính nạp hợp lệ, CRS EPSG:4326, số dòng khớp (1/1/2/26/24; address, building 1). Vị trí: gốc cục bộ → lon 105.8487265, lat 21.0226788, extent `unit` chứa điểm này (khớp số liệu); chưa kiểm với nền OSM (`tile.openstreetmap.org` không với tới được từ máy này). Lọc tầng bằng `level_id`: 13 unit + 12 opening mỗi tầng. Tạo 5 style `config/qgis/*.qml` (nạp lại được), 4 ảnh **dựng bằng engine QGIS** (không phải ảnh chụp cửa sổ; máy không có công cụ chụp màn hình), `docs/qgis-verification.md` (7 vấn đề, mục 6). Phát hiện: hai tầng chồng khít khi không lọc; QGIS làm đổi file `.gpkg` khi mở (khôi phục bằng git, dùng bản sao); `setSubsetString` lỗi khi nhiều layer cùng mở ở chế độ không giao diện nhưng lọc trong URI hoạt động; EPSG:4326 hiển thị hơi méo (dùng CRS dự án 3405). **Chưa làm / chờ chủ dự án**: kiểm vị trí trên nền bản đồ thật, 3 ảnh chụp giao diện (hướng dẫn ở mục 7 của báo cáo). |
| 2026-11-06T17:22:01+07:00 | in_review | Chủ dự án mở `.gpkg` trong QGIS thật và gửi 6 ảnh chụp giao diện (đã xem rồi **xoá theo yêu cầu**, không đưa vào repo). Xác nhận trong QGIS thật: 7 layer nạp được; bố cục đúng (12 phòng, hành lang, 6 cửa mỗi bên); 5 file `.qml` nạp đúng sau khi áp lại (opening đỏ phân loại, unit 7 loại + nhãn mã phòng, venue viền cam nét đứt). **Còn lại**: lọc `osm_level='0'` cho một tầng (nhãn đang lẫn hai tầng), đặt CRS dự án EPSG:3405 (đang ở 4326 nên hình hơi méo), thêm nền bản đồ, rồi chụp 3 ảnh cuối (toàn cảnh có nền, một tầng đã lọc, bảng thuộc tính). |

## Blocker / câu hỏi mở
- Chờ chủ dự án: kiểm toà nhà nằm đúng khu vực Hà Nội trên nền bản đồ thật trong QGIS và chụp 3 ảnh giao diện (xem `docs/qgis-verification.md` mục 7).
- Mở: nên có file dự án `.qgz` dựng sẵn với bộ lọc theo tầng? (hiện hai tầng chồng khít khi không lọc).
