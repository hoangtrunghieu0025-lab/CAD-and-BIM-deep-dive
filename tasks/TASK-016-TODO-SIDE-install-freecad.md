---
id: TASK-016
title: "[TODO][SIDE] Cài FreeCAD (snap) và kiểm mở samples/sample-building.ifc"
category: SIDE
assignees: [claude-laptop]
created_by: claude-laptop
created_at: 2026-11-06T15:23:43+07:00
updated_at: 2026-11-06T15:23:43+07:00
status: todo
priority: low
depends_on: [TASK-001]
---

# [TODO][SIDE] TASK-016 — Cài FreeCAD (snap) và kiểm mở samples/sample-building.ifc

## Mô tả
**Task gốc:** tiêu chí FreeCAD tách ra từ TASK-013. FreeCAD bị hoãn vì snap kéo theo `kf6-core24` (1,74 GB) + FreeCAD (529 MB), tải qua đường quốc tế chỉ ~0,2–1,2 Mbps; lần cài đầu còn lỗi `network is unreachable`. Blender + Bonsai đã mở được `samples/sample-building.ifc` nên việc này không chặn task nào.

Làm khi mạng tốt hơn (ngoài giờ làm việc). Cần `sudo`: chủ dự án chạy lệnh, agent kiểm chứng.

## Đầu vào (inputs)
- `samples/sample-building.ifc`; `docs/local-env-report.md`; nhật ký TASK-013

## Đầu ra mong đợi (expected_outputs)
- FreeCAD cài xong; cập nhật dòng `freecad` trong `docs/local-env-report.md` (phiên bản, cách cài).

## Tiêu chí hoàn thành (acceptance)
- [ ] `sudo snap install freecad` hoàn tất (snap tải tiếp phần dở trong `/var/lib/snapd/snaps/*.partial` hoặc tải lại)
- [ ] `freecad --version` (hoặc `freecadcmd`) in được phiên bản; mở được `samples/sample-building.ifc` và thấy 2 tầng, các `IfcSpace`
- [ ] `docs/local-env-report.md` cập nhật

## Phạm vi từng bên
- **claude-laptop**: ghi `docs/local-env-report.md` và file task này. Lệnh `sudo` do chủ dự án chạy.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | todo | 2026-11-06T15:23:43+07:00 | chờ mạng tốt hơn |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|

## Blocker / câu hỏi mở
- Dung lượng tải ~2 GB (FreeCAD + `kf6-core24`); cần mạng ổn định.
