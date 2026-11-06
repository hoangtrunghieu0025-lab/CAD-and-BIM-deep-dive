---
id: TASK-006
title: "[DONE][MAIN] Tổng hợp tài liệu CAD vs BIM và pipeline 3D–7D"
category: MAIN
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T15:36:50+07:00
status: done
priority: normal
depends_on: [TASK-002, TASK-003, TASK-004]
---

# [DONE][MAIN] TASK-006 — Tổng hợp tài liệu CAD vs BIM và pipeline 3D–7D

## Mô tả
Đọc `research/01..03` và viết tài liệu tổng hợp, đánh dấu chỗ nguồn mâu thuẫn hoặc chưa xác minh (vai trò `synthesizer`).

## Đầu vào (inputs)
- `research/01-cad/`, `research/02-bim/`, `research/03-bim-pipeline-3d-7d/`

## Đầu ra mong đợi (expected_outputs)
- `docs/cad-vs-bim.md`
- `docs/bim-pipeline-3d-7d.md`

## Tiêu chí hoàn thành (acceptance)
- [x] Hai tài liệu có mục "Mâu thuẫn / chưa xác minh"
- [x] Mọi khẳng định kỹ thuật trỏ về ghi chú research tương ứng
- [x] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: toàn bộ; chỉ ghi vào `docs/cad-vs-bim.md` và `docs/bim-pipeline-3d-7d.md`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | done | 2026-11-06T15:36:50+07:00 | chủ dự án duyệt DONE sau khi claude-laptop rà |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T11:47:58+07:00 | in_progress | Bắt đầu tổng hợp bằng agent synthesizer. |
| 2026-11-06T11:49:46+07:00 | in_review | Viết docs/cad-vs-bim.md và docs/bim-pipeline-3d-7d.md (mỗi file có mục 5 Mâu thuẫn / chưa xác minh, dẫn chiếu ../research/...). Sửa ký tự `|` trong ô bảng. |
| 2026-11-06T15:36:50+07:00 | done | **Chủ dự án duyệt DONE** (ghi hộ bởi claude-laptop theo yêu cầu của chủ dự án, vì laptop không phải assignee). Laptop rà hai tài liệu: đạt; số liệu khớp TASK-012, mục 'Mâu thuẫn / chưa xác minh' đầy đủ. 3 điểm nhỏ không chặn, mobile sửa khi tiện (xem Blocker). |

## Blocker / câu hỏi mở
Không có blocker. Ba điểm nhỏ claude-laptop gợi ý sửa trong `docs/cad-vs-bim.md` (không chặn DONE):
1. Mục 5, dòng "Binary DXF với `ezdxf.readfile`": đã lỗi thời — ezdxf có hàm đọc binary DXF (`ezdxf.lldxf.validator.is_binary_dxf_file`, `tagger.binary_tags_loader`, kiểm ở TASK-012); chưa thử với file thật. Nên ghi "hàm có tồn tại, chưa thử file thật".
2. Mục 4, dòng "Footprint từ Body": cửa ghi "bbox → trục dài → LineString (đề xuất dự án)", khác quy tắc đã chốt trong `docs/cad-to-gpkg-design.md` mục 4.3: tâm = hình học `IfcOpeningElement` → bbox thân cửa → placement + `placement_anchor`; hướng = trục X của placement.
3. Đoạn cuối mục 4 ("ngoài phạm vi"): nên thêm liên kết tới `docs/mapping-design.md` và `docs/cad-to-gpkg-design.md`; ở dòng "Sinh IFC trung gian" thêm lưu ý `ifcopenshell.api` mặc định dùng milimét (đã gây lỗi đơn vị ở file mẫu, TASK-008).
