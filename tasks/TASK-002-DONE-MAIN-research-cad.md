---
id: TASK-002
title: "[DONE][MAIN] Nghiên cứu CAD (DWG/DXF, layer, block, xref, toạ độ)"
category: MAIN
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T11:43:57+07:00
status: done
priority: high
depends_on: []
---

# [DONE][MAIN] TASK-002 — Nghiên cứu CAD (DWG/DXF, layer, block, xref, toạ độ)

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
| claude-mobile | done | 2026-11-06T11:43:57+07:00 | vòng 2: đã đối chiếu API ezdxf với docs/mã nguồn GitHub; còn mục NCS/ISO/xref layer chưa xác minh (host bị chặn) |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T10:00:00+07:00 | in_review | Viết xong dxf-dwg-formats, layers-blocks-xref, coordinates-and-units, layer-naming-conventions, parsing-with-ezdxf trong research/01-cad/; nguồn ở research/01-cad/_sources.md (chưa sửa sources.md theo chỉ đạo). Chưa commit/push (không có Bash). |
| 2026-11-06T10:34:15+07:00 | in_review | Vòng 2 xác minh: ezdxf.readthedocs.io vẫn bị chặn DNS nên đối chiếu qua nguồn gốc GitHub (docs .rst + mã nguồn). 32 khẳng định đã xác minh, 6 đã sửa (khoá odafc `linux_exec_path`→`unix_exec_path`; bảng phiên bản DXF; disassemble nêu đúng tên hàm thay "Path/MeshBuilder"; virtual_entities một cấp + cảnh báo MINSERT; modelspace().units luôn 0; GEODATA có trong ezdxf), 14 vẫn chưa xác minh (NCS/AIA, ISO 13567, BS1192, `xref|layer`, `*U`, LibreDWG 99%, v.v.). Chỉ ghi trong research/01-cad/ (kèm _sources.md mới) và file task; chưa commit. |
| 2026-11-06T11:43:57+07:00 | done | Rà soát kết quả xác minh của claude-laptop (TASK-012, commit 26869c0); chủ dự án cho phép áp dụng đề xuất vào PRIMARY_OBJECTIVE.md. Đánh dấu done. |

## Blocker / câu hỏi mở
- ezdxf.readthedocs.io và nationalcadstandard.org không fetch được (DNS bị chặn); thông tin lấy qua tóm tắt WebSearch, cần đối chiếu lại tài liệu gốc.
- Chưa xác minh: ezdxf giải dependent layer xref `xref|layer`, GEODATA/georeference trong DXF, điều khoản ODA File Converter, layer thực tế ở Việt Nam (cần mẫu thật).
