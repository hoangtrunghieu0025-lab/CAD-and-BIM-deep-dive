---
id: TASK-011
title: Kiểm tra .gpkg trong QGIS và chụp ảnh
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T02:37:46Z
updated_at: 2026-11-06T02:37:46Z
status: todo
priority: normal
depends_on: [TASK-010]
---

## Mô tả
Mở `.gpkg` đầu ra trong QGIS, kiểm tra vị trí, CRS, lọc theo tầng, style theo `category`; tạo style và ảnh để mobile xem được trên điện thoại.

## Đầu vào (inputs)
- `.gpkg` từ TASK-010

## Đầu ra mong đợi (expected_outputs)
- `docs/qgis-verification.md`: kết quả kiểm tra và vấn đề tìm thấy
- `docs/assets/*.png`: ảnh chụp màn hình
- `config/qgis/*.qml` (style)

## Tiêu chí hoàn thành (acceptance)
- [ ] Tất cả layer load đúng CRS và đúng vị trí trên bản đồ nền
- [ ] Có ≥3 ảnh chụp (toàn cảnh, một tầng, bảng thuộc tính)
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; ghi vào `docs/qgis-verification.md`, `docs/assets/`, `config/qgis/`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | todo | 2026-11-06T02:37:46Z | chưa nhận |

## Nhật ký — claude-laptop
| Thời điểm (UTC) | Trạng thái | Nội dung |
|---|---|---|

## Blocker / câu hỏi mở
-
