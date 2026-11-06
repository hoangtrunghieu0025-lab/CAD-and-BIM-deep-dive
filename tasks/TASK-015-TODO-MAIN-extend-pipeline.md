---
id: TASK-015
title: "[TODO][MAIN] Mở rộng pipeline: đối tượng chưa cài đặt và mẫu bổ sung"
category: MAIN
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T15:08:50+07:00
updated_at: 2026-11-06T15:08:50+07:00
status: todo
priority: normal
depends_on: [TASK-010]
---

# [TODO][MAIN] TASK-015 — Mở rộng pipeline: đối tượng chưa cài đặt và mẫu bổ sung

## Mô tả
Điểm 7–8 trong mục Blocker của TASK-010: các phần spec chưa cài đặt vì thiếu mẫu hoặc ngoài T1–T20. Task này nhóm lại để làm sau khi TASK-010/011 xong, theo thứ tự ưu tiên của chủ dự án. Không chặn TASK-011.

## Đầu vào (inputs)
- `docs/cad-to-gpkg-design.md` (mục 4, 5, 6, 11), `config/tag_mapping.yaml`
- Mục Blocker của TASK-010

## Đầu ra mong đợi (expected_outputs)
- Mẫu bổ sung trong `samples/` (tường dày, `IfcStair`, thang máy, `IfcColumn`, `IfcWindow`, `Pset_DoorCommon`, IFC2X3, ATTRIB trên INSERT) kèm cập nhật `samples/README.md`
- Cài đặt, theo mức ưu tiên: (a) cầu thang/thang máy/cột → `unit`; (b) mode tường `structure`; (c) `opening.door` (type/material/automatic) và `display_point`; (d) `fixture`/`detail`; (e) control points (spec 6.3); (f) kiểm khe giữa unit bằng đường bao độc lập (`A-WALL`/`IfcWall`)
- Test mới cho từng mục, ghi vào nhật ký

## Tiêu chí hoàn thành (acceptance)
- [ ] Mỗi mục (a)–(f) hoặc đã cài đặt có test, hoặc ghi lý do hoãn trong nhật ký
- [ ] `pytest` qua toàn bộ, `check` 0 lỗi trên mẫu cũ và mẫu mới
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; ghi `src/`, `tests/`, `samples/`.
- **claude-mobile**: cập nhật spec/config khi laptop báo thiếu.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | todo | 2026-11-06T15:08:50+07:00 | chưa nhận |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|

## Blocker / câu hỏi mở
-
