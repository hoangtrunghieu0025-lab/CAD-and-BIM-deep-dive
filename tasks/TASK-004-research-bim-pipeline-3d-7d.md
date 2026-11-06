---
id: TASK-004
title: Nghiên cứu pipeline BIM 3D → 4D → 5D → 6D → 7D
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T02:37:46Z
updated_at: 2026-11-06T02:37:46Z
status: in_review
priority: normal
depends_on: []
---

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
| claude-mobile | in_review | 2026-11-06T03:30:00Z | đã viết 6 ghi chú + _sources.md; chờ commit/push và gộp nguồn |

## Nhật ký — claude-mobile
| Thời điểm (UTC) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T03:30:00Z | in_review | Viết xong dimensions-overview, 4d-schedule, 5d-cost-quantities, 6d-sustainability, 7d-facility-management-cobie, guid-linking, _sources.md trong research/03-bim-pipeline-3d-7d/. WebFetch bị chặn nên chỉ dùng kết quả WebSearch; nguồn ghi ở _sources.md (chưa gộp vào sources.md). Chưa push. |

## Blocker / câu hỏi mở
- WebFetch bị chặn host (standards.buildingsmart.org, nibs.org, docs.ifcopenshell.org...); nếu cho phép mạng, cần đọc toàn văn IfcTask/IfcCostItem/COBie-IFC mapping để xác minh.
- Chưa xác minh: Pset nhiệt IFC cho 6D, IfcCostValue, khác biệt COBie v3 vs v2.4, ISO 19650-3 gốc, hàm GUID↔UUID của ifcopenshell.
- Điều phối cần gộp `_sources.md` vào `research/sources.md`, commit và push.
