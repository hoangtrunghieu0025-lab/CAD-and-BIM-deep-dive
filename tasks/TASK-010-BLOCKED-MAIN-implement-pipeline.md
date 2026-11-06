---
id: TASK-010
title: "[BLOCKED][MAIN] Cài đặt pipeline DXF/IFC → GPKG và test"
category: MAIN
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T10:34:56+07:00
status: blocked
priority: high
depends_on: [TASK-001, TASK-007, TASK-008, TASK-009]
---

# [BLOCKED][MAIN] TASK-010 — Cài đặt pipeline DXF/IFC → GPKG và test

## Mô tả
Cài đặt theo `docs/cad-to-gpkg-design.md`: đọc DXF/IFC, áp mapping, georeference, chuẩn hoá OSM/IMDF, ghi `.gpkg`, kèm test tự động.

## Đầu vào (inputs)
- `docs/cad-to-gpkg-design.md`, `config/*.yaml`, `samples/`

## Đầu ra mong đợi (expected_outputs)
- Code trong `src/`, test trong `tests/`
- CLI chạy được: `python -m src.cli <input> <output.gpkg>` (hoặc tương đương nêu trong spec)
- `.gpkg` mẫu nhỏ (≤ vài MB) vào `samples/out/` nếu dung lượng cho phép

## Tiêu chí hoàn thành (acceptance)
- [ ] `pytest` qua toàn bộ test trong spec
- [ ] `ogrinfo -al -so` liệt kê đủ layer IMDF, CRS đúng
- [ ] Chỗ spec thiếu/sai được báo trong mục Blocker / câu hỏi mở (mobile sẽ cập nhật spec)
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; ghi vào `src/`, `tests/`, `requirements.txt`, `samples/out/`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | blocked | 2026-11-06T10:34:56+07:00 | chờ TASK-007 (config) và TASK-009 (spec) |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T10:34:56+07:00 | blocked | Chưa bắt đầu. `docs/cad-to-gpkg-design.md` và `config/*.yaml` chưa tồn tại; TASK-007 và TASK-009 đang `todo`. |

## Blocker / câu hỏi mở
- Bên chặn: claude-mobile. Cần TASK-007 (`config/*.yaml`) và TASK-009 (`docs/cad-to-gpkg-design.md`) xong. Lưu ý IMPORTANT_NOTIFICATIONS: mapping OSM/IMDF phải được xác minh với spec gốc trước khi cứng hoá vào code.
