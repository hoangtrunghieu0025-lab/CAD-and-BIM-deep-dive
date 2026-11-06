---
id: TASK-005
title: Nghiên cứu OSM Simple Indoor Tagging, IMDF và GeoPackage
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T09:37:46+07:00
status: in_review
priority: high
depends_on: []
---

## Mô tả
Tìm hiểu tag indoor của OSM, các feature type và ràng buộc của IMDF, yêu cầu GeoPackage hợp lệ và cách QGIS đọc.

## Đầu vào (inputs)
- `PRIMARY_OBJECTIVE.md` mục 3.3 (bước 4–6)
- Wiki OSM Simple Indoor Tagging, đặc tả IMDF (Apple), đặc tả OGC GeoPackage

## Đầu ra mong đợi (expected_outputs)
- `research/04-osm-imdf-tagging/*.md`: `osm-simple-indoor-tagging`, `imdf-feature-types`, `imdf-relations-and-constraints`, `geopackage-requirements`, `qgis-import-notes`
- Mỗi ghi chú theo `research/_templates/finding.md`, có nguồn (URL + ngày truy cập), nguồn mới thêm vào `research/sources.md`; chỗ chưa chắc ghi "chưa xác minh".

## Tiêu chí hoàn thành (acceptance)
- [ ] Mỗi tag OSM và feature IMDF nêu trong bảng của `PRIMARY_OBJECTIVE.md` đã được đối chiếu với nguồn; chỗ sai hoặc thiếu được ghi rõ
- [ ] Liệt kê thuộc tính bắt buộc của từng feature IMDF dùng trong dự án
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: toàn bộ; chỉ ghi vào `research/04-osm-imdf-tagging/` và `research/sources.md`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | in_review | 2026-11-06T10:30:00+07:00 | 5 ghi chú + _sources.md xong; nhiều mục chưa xác minh do domain bị chặn |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T10:30:00+07:00 | in_review | Viết 5 ghi chú + `_sources.md` trong research/04-osm-imdf-tagging/. Nguồn gốc (wiki OSM, Apple IMDF, OGC, GDAL, QGIS) không truy cập được; chỉ có đoạn trích tìm kiếm + repo GitHub. Chưa push (người điều phối commit). |

## Blocker / câu hỏi mở
- Cần cho phép domain: wiki.openstreetmap.org, register.apple.com, docs.ogc.org, www.geopackage.org, gdal.org, docs.qgis.org để xác minh thuộc tính bắt buộc IMDF, category, door=*, yêu cầu GPKG.
- Nguồn mới nằm ở `research/04-osm-imdf-tagging/_sources.md`, chờ điều phối gộp vào `research/sources.md`.
