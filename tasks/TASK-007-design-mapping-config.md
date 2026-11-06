---
id: TASK-007
title: Thiết kế bảng mapping CAD/IFC → OSM → IMDF
assignees: [claude-mobile, claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T02:37:46Z
updated_at: 2026-11-06T02:37:46Z
status: todo
priority: high
depends_on: [TASK-002, TASK-003, TASK-005]
---

## Mô tả
Chuyển bảng mapping trong `PRIMARY_OBJECTIVE.md` thành file cấu hình dùng được bởi code. Mobile soạn bản nháp từ research; laptop thử trên file mẫu thật và báo chỗ cần chỉnh.

## Đầu vào (inputs)
- `research/01-cad/`, `research/02-bim/`, `research/04-osm-imdf-tagging/`
- File mẫu trong `samples/` (từ TASK-008)

## Đầu ra mong đợi (expected_outputs)
- `config/layer_mapping.yaml` (CAD layer → loại đối tượng)
- `config/tag_mapping.yaml` (IFC class / loại đối tượng → tag OSM → IMDF feature + category)
- `docs/mapping-design.md` (giải thích các quyết định, trường hợp ngoại lệ)

## Tiêu chí hoàn thành (acceptance)
- [ ] Mọi giá trị OSM/IMDF trong file đều có nguồn trong `research/04-*`
- [ ] Laptop xác nhận đã chạy thử mapping trên ≥1 file mẫu DXF và ≥1 file IFC, ghi kết quả vào nhật ký
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: soạn `config/*.yaml` và `docs/mapping-design.md`.
- **claude-laptop**: chỉ ghi nhật ký task này và đề xuất chỉnh sửa trong mục Blocker / câu hỏi mở; sửa trực tiếp `config/*.yaml` chỉ sau khi mobile đã đặt trạng thái `in_review`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | todo | 2026-11-06T02:37:46Z | chưa nhận |
| claude-laptop | todo | 2026-11-06T02:37:46Z | chưa nhận |

## Nhật ký — claude-mobile
| Thời điểm (UTC) | Trạng thái | Nội dung |
|---|---|---|

## Nhật ký — claude-laptop
| Thời điểm (UTC) | Trạng thái | Nội dung |
|---|---|---|

## Blocker / câu hỏi mở
-
