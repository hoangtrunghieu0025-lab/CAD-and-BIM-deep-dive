---
id: TASK-004
title: "[IN_REVIEW][MAIN] Nghiên cứu pipeline BIM 3D → 4D → 5D → 6D → 7D"
category: MAIN
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T10:34:15+07:00
status: in_review
priority: normal
depends_on: []
---

# [IN_REVIEW][MAIN] TASK-004 — Nghiên cứu pipeline BIM 3D → 4D → 5D → 6D → 7D

## Mô tả
Làm rõ dữ liệu được thêm ở từng chiều, chuẩn và công cụ liên quan, khoá liên kết (GUID), COBie, digital twin/FM, và phần nào có thể đưa sang GIS.

## Đầu vào (inputs)
- `PRIMARY_OBJECTIVE.md` mục 2

## Đầu ra mong đợi (expected_outputs)
- `research/03-bim-pipeline-3d-7d/*.md`: `dimensions-overview`, `4d-schedule`, `5d-cost-quantities`, `6d-sustainability`, `7d-facility-management-cobie`, `guid-linking`
- Mỗi ghi chú theo `research/_templates/finding.md`, có nguồn (URL + ngày truy cập), nguồn mới thêm vào `research/sources.md`; chỗ chưa chắc ghi "chưa xác minh".

## Tiêu chí hoàn thành (acceptance)
- [ ] Có bảng "chiều → dữ liệu thêm → chuẩn/class IFC liên quan → công cụ" có nguồn
- [ ] Nêu cách nối 3D với 4D/5D/7D qua GUID
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: toàn bộ; chỉ ghi vào `research/03-bim-pipeline-3d-7d/` và `research/sources.md`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | in_review | 2026-11-06T10:34:15+07:00 | vòng 2 xác minh: host spec vẫn không resolve DNS; 0 xác minh / 0 sửa; chờ mở mạng |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T10:30:00+07:00 | in_review | Viết xong dimensions-overview, 4d-schedule, 5d-cost-quantities, 6d-sustainability, 7d-facility-management-cobie, guid-linking, _sources.md trong research/03-bim-pipeline-3d-7d/. WebFetch bị chặn nên chỉ dùng kết quả WebSearch; nguồn ghi ở _sources.md (chưa gộp vào sources.md). Chưa push. |
| 2026-11-06T10:34:15+07:00 | in_review | Vòng 2 xác minh: WebFetch tới ifc43-docs.standards.buildingsmart.org, standards.buildingsmart.org, docs.ifcopenshell.org đều lỗi DNS ENOTFOUND (host chưa được phép trong phiên). Kết quả: 0 khẳng định xác minh / 0 sửa / toàn bộ nhãn "chưa xác minh" giữ nguyên (IfcTask/IfcTaskTime/RelatingProcess deprecated, Pset_TaskCommon, IfcCostValue/IfcAppliedValue, Pset nhiệt 6D, ánh xạ COBie-IFC, ifcopenshell.guid, api.sequence/Ifc4D). Ghi các URL đã thử vào _sources.md. Cần mở host rồi chạy lại. |

## Blocker / câu hỏi mở
- WebFetch bị chặn host (standards.buildingsmart.org, nibs.org, docs.ifcopenshell.org...); nếu cho phép mạng, cần đọc toàn văn IfcTask/IfcCostItem/COBie-IFC mapping để xác minh.
- Chưa xác minh: Pset nhiệt IFC cho 6D, IfcCostValue, khác biệt COBie v3 vs v2.4, ISO 19650-3 gốc, hàm GUID↔UUID của ifcopenshell.
- Điều phối cần gộp `_sources.md` vào `research/sources.md`, commit và push.
