---
id: TASK-002
title: Nghiên cứu CAD (DWG/DXF, layer, block, xref, toạ độ)
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T02:37:46Z
updated_at: 2026-11-06T02:37:46Z
status: todo
priority: high
depends_on: []
---

## Mô tả
Tìm hiểu CAD ở mức đủ để đọc và làm sạch dữ liệu bằng `ezdxf`: định dạng, cấu trúc, quy ước đặt tên layer, hệ toạ độ/đơn vị, hạn chế ngữ nghĩa.

## Đầu vào (inputs)
- `PRIMARY_OBJECTIVE.md` mục 1.1
- Tài liệu `ezdxf` và đặc tả DXF công khai

## Đầu ra mong đợi (expected_outputs)
- `research/01-cad/*.md`: ít nhất các chủ đề `dxf-dwg-formats`, `layers-blocks-xref`, `coordinates-and-units`, `layer-naming-conventions`, `parsing-with-ezdxf`
- Mỗi ghi chú theo `research/_templates/finding.md`, có nguồn (URL + ngày truy cập), nguồn mới thêm vào `research/sources.md`; chỗ chưa chắc ghi "chưa xác minh".

## Tiêu chí hoàn thành (acceptance)
- [ ] Có đủ 5 chủ đề trên, mỗi ghi chú có kết luận ngắn và nguồn
- [ ] Có mục "Liên quan đến pipeline CAD → BIM → GPKG" trong từng ghi chú
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: toàn bộ; chỉ ghi vào `research/01-cad/` và `research/sources.md` (thêm dòng).

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
