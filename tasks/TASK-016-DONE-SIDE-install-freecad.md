---
id: TASK-016
title: "[DONE][SIDE] Cài FreeCAD (snap) và kiểm mở samples/sample-building.ifc"
category: SIDE
assignees: [claude-laptop]
created_by: claude-laptop
created_at: 2026-11-06T15:23:43+07:00
updated_at: 2026-11-09T07:00:37+07:00
status: done
priority: low
depends_on: [TASK-001]
---

# [DONE][SIDE] TASK-016 — Cài FreeCAD (snap) và kiểm mở samples/sample-building.ifc

## Mô tả
**Task gốc:** tiêu chí FreeCAD tách ra từ TASK-013. FreeCAD bị hoãn vì snap kéo theo `kf6-core24` (1,74 GB) + FreeCAD (529 MB), tải qua đường quốc tế chỉ ~0,2–1,2 Mbps; lần cài đầu còn lỗi `network is unreachable`. Blender + Bonsai đã mở được `samples/sample-building.ifc` nên việc này không chặn task nào.

Làm khi mạng tốt hơn (ngoài giờ làm việc). Cần `sudo`: chủ dự án chạy lệnh, agent kiểm chứng.

## Đầu vào (inputs)
- `samples/sample-building.ifc`; `docs/local-env-report.md`; nhật ký TASK-013

## Đầu ra mong đợi (expected_outputs)
- FreeCAD cài xong; cập nhật dòng `freecad` trong `docs/local-env-report.md` (phiên bản, cách cài).

## Tiêu chí hoàn thành (acceptance)
- [x] FreeCAD đã cài bằng snap **hoặc AppImage** (đổi theo yêu cầu người dùng 2026-11-08: mạng đã nhanh ~35 Mbps; AppImage `~/apps/FreeCAD_1.1.4-Linux-x86_64-py311.AppImage`, 783 MB, không cần `sudo` và không kéo `kf6-core24`)
- [x] FreeCAD chạy được và xác định được phiên bản (1.1.4, theo thanh tiêu đề cửa sổ); mở được `samples/sample-building.ifc` và thấy 2 tầng (Tầng 1 = 0 mm, Tầng 2 = 3000 mm), các `IfcSpace` (xem ảnh `samples/Pasted image (2).png`; đếm bằng ifcopenshell: 2 tầng, 26 IfcSpace)
- [x] `docs/local-env-report.md` cập nhật

## Phạm vi từng bên
- **claude-laptop**: ghi `docs/local-env-report.md` và file task này. Lệnh `sudo` do chủ dự án chạy.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | done | 2026-11-09T07:00:37+07:00 | FreeCAD 1.1.4 (AppImage) mở được IFC mẫu; đóng theo yêu cầu chủ dự án |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-08 04:25 | in_progress | Người dùng tải AppImage FreeCAD 1.1.4 (mạng ~35 Mbps), tôi chuyển vào `~/apps/`. Sửa tiêu chí "snap" thành "snap hoặc AppImage" theo yêu cầu người dùng. `--version` chỉ in cảnh báo QThreadStorage, chưa lấy được số phiên bản; đang chạy kiểm mở IFC ở chế độ console |
| 2026-11-08 04:39 | in_review | Ảnh chụp của người dùng (`samples/Pasted image.png`, `samples/Pasted image (2).png`): FreeCAD 1.1.4 mở `sample-building.ifc`, bảng BIM có Tầng 1 (0 mm) và Tầng 2 (3000 mm), cây có P101–P112, HL100, Cua P1xx, tường ngoài. `ifcopenshell` đếm 2 IfcBuildingStorey và 26 IfcSpace. Cập nhật docs/local-env-report.md. Chưa commit |
| 2026-11-09 07:00 | done | Đóng task theo yêu cầu của chủ dự án (ghi bởi claude-mobile). |

## Blocker / câu hỏi mở
- Dung lượng tải ~2 GB (FreeCAD + `kf6-core24`); cần mạng ổn định.
