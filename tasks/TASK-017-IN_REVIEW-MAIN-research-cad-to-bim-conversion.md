---
id: TASK-017
title: "[IN_REVIEW][MAIN] Nghiên cứu cách chuyển dữ liệu CAD sang BIM"
category: MAIN
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-08T04:12:01+07:00
updated_at: 2026-11-08T04:15:10+07:00
status: in_review
priority: normal
depends_on: [TASK-002, TASK-003]
---

# [IN_REVIEW][MAIN] TASK-017 — Nghiên cứu cách chuyển dữ liệu CAD sang BIM

## Mô tả
Nghiên cứu các cách chuyển bản vẽ CAD (DWG/DXF, 2D và 3D) thành mô hình BIM có thông tin (IFC/Revit/ArchiCAD): hướng tiếp cận, công cụ, quy trình, rủi ro mất thông tin. Kết quả bổ sung cho bước "CAD → BIM" trong `PRIMARY_OBJECTIVE.md` mục 3 và không trùng với TASK-014 (khảo sát công cụ CAD/BIM → GPKG).

Các hướng cần khảo sát:
- Dựng lại thủ công trên nền underlay (Revit/ArchiCAD).
- Bán tự động bằng plugin hoặc script: Revit API/Dynamo/pyRevit, `ezdxf` + `ifcopenshell`, BlenderBIM/Bonsai, FreeCAD.
- Scan-to-BIM và AI/Computer Vision trên bản vẽ 2D (PDF/ảnh).
- Quy trình chuẩn: dọn CAD, ánh xạ layer → loại đối tượng IFC, trích hình học, gán cao độ/thuộc tính (Pset), kiểm tra chất lượng.
- Rủi ro: thiếu cao độ ở CAD 2D, layer đặt tên không thống nhất, mất thông tin khi DWG → IFC, mức LOD.

## Đầu vào (inputs)
- `research/01-cad/`, `research/02-bim/`, `docs/cad-vs-bim.md`, `docs/mapping-design.md`
- `samples/` (DXF/IFC mẫu) để đối chiếu ví dụ

## Đầu ra mong đợi (expected_outputs)
- `research/06-cad-to-bim/*.md`, mỗi ghi chú theo mẫu `research/_templates/finding.md`
- Dòng nguồn mới (URL + ngày truy cập) trong `research/sources.md` (chỉ thêm dòng cuối)
- Mục "Đề xuất" nêu cách chuyển phù hợp nhất cho pipeline của dự án (kèm các việc POC nên làm)

## Tiêu chí hoàn thành (acceptance)
- [x] So sánh được ít nhất 4 hướng tiếp cận (ưu/nhược, độ tự động, độ chính xác, chi phí)
- [x] Mọi khẳng định kỹ thuật có nguồn; điều chưa chắc ghi "chưa xác minh"
- [x] Có quy trình đề xuất từng bước và bảng ánh xạ layer CAD → class IFC (khớp `docs/mapping-design.md`)
- [x] Liệt kê rủi ro và hạn chế, kèm cách giảm thiểu
- [x] Có danh sách việc POC tiếp theo (nếu cần giao claude-laptop)

## Phạm vi từng bên
- **claude-mobile**: toàn bộ (nghiên cứu, ghi vào `research/06-cad-to-bim/`).

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | in_review | 2026-11-08T04:15:10+07:00 | Xong 3 ghi chú + POC; chờ người dùng rà |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-08 04:12 | todo | Tạo task theo yêu cầu của người dùng |
| 2026-11-08 04:30 | in_review | Viết research/06-cad-to-bim/ (3 ghi chú, POC DXF → IFC chạy được 16 IfcWall), thêm 6 nguồn vào sources.md. Việc POC tiếp theo (A-AREA→IfcSpace, A-DOOR→IfcDoor, mở bằng Bonsai/FreeCAD) đề xuất giao claude-laptop |
| 2026-11-08 05:00 | in_review | Theo phản hồi người dùng: khảo sát thêm dự án mã nguồn mở DXF/DWG → IFC (SaN-architect-ai, IfcOpenShell dxf2ifc.py, CrossBIM, DXF2IFC2D…) vào `research/06-cad-to-bim/open-source-dxf-to-ifc-projects.md`; bổ sung 3 nguồn còn thiếu và 11 nguồn mới vào `sources.md`. Chưa clone/chạy dự án nào. Việc POC mới: chạy SaN-architect-ai trên `samples/sample-floor-1.dxf` và so với POC của ta |
| 2026-11-08 06:00 | in_review | Theo phản hồi người dùng: đọc mã FreeCAD 1.1.4 và chạy IfcOpenShell tại máy, viết `freecad-ifcopenshell-dxf-to-ifc-and-enrichment.md` + `poc/enrich_ifc_demo.py` (làm giàu Pset/vật liệu/phân loại cho 16 tường POC). Lấy phụ đề 2 video YouTube, cập nhật `open-source-dxf-to-ifc-projects.md`. Thêm 8 dòng nguồn. Chưa thử Bonsai, ifctester, ifcpatch |
| 2026-11-08 07:00 | in_review | Theo link người dùng gửi: clone và đọc mã Kevinscsatoshi/ifcbim (không giấy phép) và alvin528/CAD2BIM (Apache-2.0), viết `cad2bim-and-ifcbim-code-review.md`, thêm 4 dòng nguồn. Chưa chạy mã của hai repo |
| 2026-11-08 08:00 | in_review | Theo danh sách từ khoá của người dùng: tìm GitHub bằng API + web, viết `github-survey-cad-to-ifc.md`. Đã clone và đọc mã Mcrauli/dwg2ifc, aec-platform/roomgraph, naquib0513/2D23D (đều MIT) cùng 2 repo stub. Phần còn lại chỉ siêu dữ liệu. Một số từ khoá chưa tìm vì hết hạn mức API. Chưa chạy mã nào. Thêm 14 dòng nguồn |
| 2026-11-08 09:00 | in_review | Theo yêu cầu 'đọc mã nhóm 3': clone và đọc mã Cloud2BIM, ifc-floorplan, FloorplanTransformation, VecFloorSeg, ifc-bonsai-mcp, A-Scan2BIM, viết `github-group3-code-review.md`; thêm 4 dòng nguồn. Chưa chạy mã nào |
| 2026-11-08 10:00 | in_review | Theo phản hồi 'chưa check kỹ': kiểm link người dùng gửi (4 link 404), đọc sâu ArchWall/ArchSpace/upgrade/exportIFC của FreeCAD 1.1.4 và mã Bonsai (không có nhập DXF; dxf2ifc.py GPL-3.0). Chạy thử voids/fills trên ifcopenshell 0.9.0.post1 (`poc/ifc_opening_test.py`): chạy được. Cập nhật `freecad-ifcopenshell-dxf-to-ifc-and-enrichment.md` + 4 dòng nguồn |
| 2026-11-08 11:00 | in_review | Theo yêu cầu 'đọc sâu thêm': đọc FreeCAD `offsetWire`/`connect`, tái hiện bằng shapely (L mitre 1,6 m²; T union 1,98), thử ezdxf (bulge, INSERT lật gương cần WCS), đối chiếu `src/cad2bim` (bỏ bulge, chưa mở INSERT). Viết `wall-corner-joins-and-ezdxf-details.md`. Chưa sửa mã trong `src/` |
| 2026-11-08 12:00 | in_review | Theo yêu cầu 'thử bước nối góc': `poc/wall_corner_join_trial.py` (noding + linemerge + buffer mitre + kéo dài đầu rời) chạy trên sample-floor-1.dxf: mẫu sạch +0,04 m² so với POC cũ (4 góc ngoài), ca hở 0,15–0,30 m mất 10/13 phòng nếu không kéo dài, có kéo dài thì khôi phục đúng. Mẫu quá sạch, chưa thử bản vẽ thật. Ghi kết quả vào `wall-corner-joins-and-ezdxf-details.md` |

## Blocker / câu hỏi mở
- Chưa rõ người dùng muốn đích là Revit, ArchiCAD hay IFC thuần; mặc định nghiên cứu cả ba, ưu tiên IFC.
