---
id: TASK-009
title: Viết spec thiết kế pipeline CAD → BIM → GPKG
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T02:37:46Z
updated_at: 2026-11-06T02:37:46Z
status: todo
priority: high
depends_on: [TASK-005, TASK-007]
---

## Mô tả
Viết đặc tả để laptop cài đặt: module, hàm, input/output từng bước, schema bảng GPKG theo IMDF, quy tắc georeference, kiểm tra hợp lệ.

## Đầu vào (inputs)
- `PRIMARY_OBJECTIVE.md` mục 3
- `config/*.yaml`, `research/04-osm-imdf-tagging/`

## Đầu ra mong đợi (expected_outputs)
- `docs/cad-to-gpkg-design.md`: sơ đồ, giao diện CLI (`input → output.gpkg`), schema từng layer, danh sách kiểm tra (CRS, hình học hợp lệ, quan hệ khoá ngoại)

## Tiêu chí hoàn thành (acceptance)
- [ ] Mỗi bước nêu rõ input, output, lỗi có thể gặp
- [ ] Có danh sách test mà TASK-010 phải qua
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: toàn bộ; chỉ ghi vào `docs/cad-to-gpkg-design.md`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | todo | 2026-11-06T02:37:46Z | chưa nhận |

## Nhật ký — claude-mobile
| Thời điểm (UTC) | Trạng thái | Nội dung |
|---|---|---|

## Blocker / câu hỏi mở
-
