---
id: TASK-003
title: "[DONE][MAIN] Nghiên cứu BIM và IFC (cấu trúc không gian, Pset, georeference)"
category: MAIN
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T11:43:57+07:00
status: done
priority: high
depends_on: []
---

# [DONE][MAIN] TASK-003 — Nghiên cứu BIM và IFC (cấu trúc không gian, Pset, georeference)

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
| claude-mobile | done | 2026-11-06T11:43:57+07:00 | vòng 2 xác minh: host spec vẫn không phân giải DNS; chưa xác minh thêm được; chờ allowlist |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T10:00:00+07:00 | in_review | Viết 5 ghi chú trong research/02-bim/ (spatial structure, Pset/classification, LOD-MVD-IDS, georeference, ifcopenshell) + _sources.md; có đoạn footprint IfcSpace/IfcDoor theo tầng |
| 2026-11-06T10:34:15+07:00 | in_review | Vòng 2 xác minh lại: 0 khẳng định đã xác minh / 0 đã sửa / toàn bộ mục "chưa xác minh" giữ nguyên. Lý do: ifc43-docs.standards.buildingsmart.org (7 trang) và docs.ifcopenshell.org vẫn lỗi ENOTFOUND trong phiên này; nội dung 5 ghi chú không đổi; ghi kết quả + danh sách việc cần kiểm vào research/02-bim/_sources.md |
| 2026-11-06T11:43:57+07:00 | done | Rà soát kết quả xác minh của claude-laptop (TASK-012, commit 26869c0); chủ dự án cho phép áp dụng đề xuất vào PRIMARY_OBJECTIVE.md. Đánh dấu done. |

## Blocker / câu hỏi mở
- WebFetch bị chặn tới *.buildingsmart.org và docs.ifcopenshell.org; nguồn lấy qua WebSearch nên chưa xác minh trực tiếp: IfcBuildingStorey.Elevation, công thức IfcMapConversion, Pset_DoorCommon, IDM, API settings IfcOpenShell 0.8.
- Cần thêm các host trên vào allowlist nếu muốn xác minh; code footprint chưa chạy thử (không có Bash).
- Mục "Đã push lên main" do điều phối viên thực hiện.
