---
id: TASK-008
title: "[DONE][MAIN] Chuẩn bị file mẫu DXF và IFC nhỏ"
category: MAIN
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T14:18:40+07:00
status: done
priority: high
depends_on: [TASK-001]
---

# [DONE][MAIN] TASK-008 — Chuẩn bị file mẫu DXF và IFC nhỏ

## Mô tả
Tìm hoặc tạo file mẫu nhỏ (một toà nhà 1–2 tầng, vài chục phòng) có giấy phép sử dụng rõ ràng, để phát triển và test pipeline. Cloud bị giới hạn mạng nên giao cho laptop.

## Đầu vào (inputs)
- Nguồn mẫu mở (ví dụ repo mẫu của IfcOpenShell/buildingSMART, ví dụ `ezdxf`), hoặc tự dựng bằng FreeCAD/Bonsai/LibreCAD

## Đầu ra mong đợi (expected_outputs)
- `samples/*.dxf`, `samples/*.ifc` (mỗi file ≤ vài MB)
- `samples/README.md`: nguồn, giấy phép, mô tả nội dung từng file, CRS/đơn vị nếu biết

## Tiêu chí hoàn thành (acceptance)
- [x] ≥1 DXF và ≥1 IFC, mở được bằng `ezdxf` và `ifcopenshell`
- [x] README ghi nguồn và giấy phép của từng file
- [x] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; chỉ ghi vào `samples/`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | done | 2026-11-06T14:18:40+07:00 | file mẫu xong, đã kiểm chứng; câu hỏi LICENSE còn mở |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T10:25:44+07:00 | in_review | Tự sinh 2 DXF + 1 IFC4 (24 phòng, 2 tầng) bằng `samples/generate_samples.py`; ezdxf audit 0 lỗi, ifcopenshell dựng hình học 34/34. Ghi `samples/README.md`. |
| 2026-11-06T11:16:02+07:00 | in_review | Sửa lỗi phát hiện khi làm TASK-012: IFC mẫu khai báo đơn vị mm nên `Elevation`/`OverallWidth` gán tay sai đơn vị. Đặt đơn vị mét trong `generate_samples.py`, sinh lại `sample-building.ifc` (26 IfcSpace, 8 IfcWall, 24 IfcDoor; hình học 34/34). DXF không đổi. |
| 2026-11-06T14:18:40+07:00 | done | Đặt DONE: mọi tiêu chí thoả, file đầu ra đã có trên `origin/main` (kiểm bằng `git cat-file`). Lý do: TASK-010 phụ thuộc task này phải `DONE`. |

## Blocker / câu hỏi mở
- Repo chưa có LICENSE; cần chủ repo chọn giấy phép cho dữ liệu mẫu (gợi ý CC0).
