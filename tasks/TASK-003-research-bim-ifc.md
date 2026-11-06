---
id: TASK-003
title: Nghiên cứu BIM và IFC (cấu trúc không gian, Pset, georeference)
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T02:37:46Z
updated_at: 2026-11-06T02:37:46Z
status: in_review
priority: high
depends_on: []
---

## Mô tả
Tìm hiểu BIM/IFC: cấu trúc `IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace`, property set, phân loại, LOD/LOI, MVD/IDS, georeference (`IfcMapConversion`, `IfcProjectedCRS`), `ifcopenshell` để trích hình học.

## Đầu vào (inputs)
- `PRIMARY_OBJECTIVE.md` mục 1.2
- Đặc tả IFC (buildingSMART), tài liệu IfcOpenShell

## Đầu ra mong đợi (expected_outputs)
- `research/02-bim/*.md`: `ifc-spatial-structure`, `property-sets-and-classification`, `lod-mvd-ids`, `ifc-georeference`, `ifcopenshell-geometry-extraction`
- Mỗi ghi chú theo `research/_templates/finding.md`, có nguồn (URL + ngày truy cập), nguồn mới thêm vào `research/sources.md`; chỗ chưa chắc ghi "chưa xác minh".

## Tiêu chí hoàn thành (acceptance)
- [ ] Có đủ 5 chủ đề, nêu đúng tên class/thuộc tính IFC có nguồn
- [ ] Có đoạn nói rõ cách lấy footprint 2D của `IfcSpace`/`IfcDoor` theo tầng
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: toàn bộ; chỉ ghi vào `research/02-bim/` và `research/sources.md`.

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
