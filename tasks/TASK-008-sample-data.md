---
id: TASK-008
title: Chuẩn bị file mẫu DXF và IFC nhỏ
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T09:37:46+07:00
status: todo
priority: high
depends_on: [TASK-001]
---

## Mô tả
Tìm hoặc tạo file mẫu nhỏ (một toà nhà 1–2 tầng, vài chục phòng) có giấy phép sử dụng rõ ràng, để phát triển và test pipeline. Cloud bị giới hạn mạng nên giao cho laptop.

## Đầu vào (inputs)
- Nguồn mẫu mở (ví dụ repo mẫu của IfcOpenShell/buildingSMART, ví dụ `ezdxf`), hoặc tự dựng bằng FreeCAD/Bonsai/LibreCAD

## Đầu ra mong đợi (expected_outputs)
- `samples/*.dxf`, `samples/*.ifc` (mỗi file ≤ vài MB)
- `samples/README.md`: nguồn, giấy phép, mô tả nội dung từng file, CRS/đơn vị nếu biết

## Tiêu chí hoàn thành (acceptance)
- [ ] ≥1 DXF và ≥1 IFC, mở được bằng `ezdxf` và `ifcopenshell`
- [ ] README ghi nguồn và giấy phép của từng file
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; chỉ ghi vào `samples/`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | todo | 2026-11-06T09:37:46+07:00 | chưa nhận |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|

## Blocker / câu hỏi mở
-
