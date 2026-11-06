---
id: TASK-007
title: "[IN_REVIEW][MAIN] Thiết kế bảng mapping CAD/IFC → OSM → IMDF"
category: MAIN
assignees: [claude-mobile, claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T11:55:16+07:00
status: in_review
priority: high
depends_on: [TASK-002, TASK-003, TASK-005]
---

# [IN_REVIEW][MAIN] TASK-007 — Thiết kế bảng mapping CAD/IFC → OSM → IMDF

## Mô tả
Chuyển bảng mapping trong `PRIMARY_OBJECTIVE.md` thành file cấu hình dùng được bởi code. Mobile soạn bản nháp từ research; laptop thử trên file mẫu thật và báo chỗ cần chỉnh.

## Đầu vào (inputs)
- `research/01-cad/`, `research/02-bim/`, `research/04-osm-imdf-tagging/`
- File mẫu trong `samples/` (từ TASK-008)

## Đầu ra mong đợi (expected_outputs)
- `config/layer_mapping.yaml` (CAD layer → loại đối tượng)
- `config/tag_mapping.yaml` (IFC class / loại đối tượng → tag OSM → IMDF feature + category)
- `docs/mapping-design.md` (giải thích các quyết định, trường hợp ngoại lệ)

## Tiêu chí hoàn thành (acceptance)
- [ ] Mọi giá trị OSM/IMDF trong file đều có nguồn trong `research/04-*`
- [ ] Laptop xác nhận đã chạy thử mapping trên ≥1 file mẫu DXF và ≥1 file IFC, ghi kết quả vào nhật ký
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: soạn `config/*.yaml` và `docs/mapping-design.md`.
- **claude-laptop**: chỉ ghi nhật ký task này và đề xuất chỉnh sửa trong mục Blocker / câu hỏi mở; sửa trực tiếp `config/*.yaml` chỉ sau khi mobile đã đặt trạng thái `in_review`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | in_review | 2026-11-06T11:55:16+07:00 | config + docs xong, chờ laptop thử trên IFC |
| claude-laptop | todo | 2026-11-06T11:55:16+07:00 | chờ thử mapping trên samples/*.ifc |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T11:55:16+07:00 | in_review | Soạn config/layer_mapping.yaml, config/tag_mapping.yaml, docs/mapping-design.md. Chạy layer_mapping trên samples/sample-floor-1.dxf: 13 A-AREA + 13 nhãn + 12 cửa + 13 tường, 0 UNMATCHED (khớp samples/README). tag_mapping mới kiểm cú pháp YAML, chưa chạy trên IFC. |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|

## Blocker / câu hỏi mở
- Nhờ claude-laptop: chạy thử `tag_mapping.yaml` trên `samples/sample-building.ifc` (IfcSpace, IfcDoor, IfcWall; rule corridor theo `LongName` = "Hanh lang"), ghi kết quả vào nhật ký claude-laptop. Sửa trực tiếp `config/*.yaml` được phép từ bây giờ (mobile đã `in_review`).
- Câu hỏi mở: xem mục 5 của `docs/mapping-design.md` (venue.category, IfcTransportElement, door=*/room=*, LABELS).
