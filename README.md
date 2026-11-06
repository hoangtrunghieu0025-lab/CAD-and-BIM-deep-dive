# CAD-and-BIM-deep-dive

Dự án xây bộ chuyển đổi rule-based từ CAD (DXF/DWG) và BIM (IFC) sang GeoPackage, chuẩn hoá theo OSM Simple Indoor Tagging và IMDF, mở được trong QGIS. Tệp này hướng dẫn cách đọc các file và thư mục.

## Nên đọc 

1. PRIMARY_OBJECTIVE.md: mục tiêu và phạm vi của dự án.
2. src/README.md: cách chạy pipeline; sau đó đọc code trong src/.
3. reports/: các báo cáo tóm tắt cho mentor, mới nhất xếp cuối theo tên file.
4. docs/: kiến thức nghiên cứu được.

## Thư mục và file ở gốc

| Đường dẫn | Nội dung |
|---|---|
| PRIMARY_OBJECTIVE.md | Mục tiêu dự án (không tự ý sửa) |
| CLAUDE.md, AGENTS.md | Quy tắc chung cho các agent: ngôn ngữ, nguồn, phân quyền ghi |
| collab/CONTRACT.md | Quy ước cộng tác giữa claude-mobile và claude-laptop |
| IMPORTANT_NOTIFICATIONS.md | Thông báo giữa hai agent và chủ dự án (N-001...), đọc khi cần biết quyết định gần nhất |
| requirements.txt | Thư viện Python cần cài |
| out/ | Thư mục đầu ra khi chạy thử (nội dung không theo dõi) |

## Từng thư mục

| Thư mục | Nội dung | Đọc khi |
|---|---|---|
| reports/ | Báo cáo tóm tắt, tên theo mẫu report-năm-tháng-ngày-giờphút.md, mỗi file gồm 5 mục đánh số | Muốn biết tình hình mới nhất |
| tasks/ | Mỗi file một việc (TASK-NNN-trạng thái-loại-tên.md), kèm nhật ký làm việc; tasks/README.md giải thích cách đặt tên, tasks/list.py in bảng tổng hợp | Muốn biết ai làm gì, đã xong chưa |
| research/ | Ghi chú nghiên cứu có nguồn, chia theo chủ đề (bảng dưới); research/sources.md gom mọi nguồn | Muốn kiểm chứng một khẳng định kỹ thuật |
| docs/ | Tài liệu tổng hợp từ research: so sánh, thiết kế, báo cáo kiểm tra | Muốn hiểu thiết kế và kết quả |
| config/ | layer_mapping.yaml (layer CAD sang loại đối tượng), tag_mapping.yaml (loại đối tượng sang tag OSM và IMDF), qgis/ (5 file style .qml) | Muốn đổi luật chuyển đổi |
| src/ | Mã nguồn pipeline | Muốn đọc hoặc sửa code |
| tests/ | Test tự động (pytest) | Muốn biết hành vi được bảo đảm |
| samples/ | Dữ liệu mẫu DXF/IFC tự sinh, file cấu hình dự án mẫu, samples/out/ chứa kết quả GPKG và gói IMDF | Muốn chạy thử |
| .claude/agents/ | Định nghĩa các agent nghiên cứu | Chỉ cần khi quản lý agent |

## research/

| Thư mục | Chủ đề |
|---|---|
| 01-cad | Định dạng DXF/DWG, layer, block, xref, toạ độ và đơn vị, đọc bằng ezdxf |
| 02-bim | Cấu trúc không gian IFC, hình học, georeference, Pset, LOD/MVD/IDS |
| 03-bim-pipeline-3d-7d | BIM 3D đến 7D: tiến độ, chi phí, bền vững, quản lý vận hành, liên kết GUID |
| 04-osm-imdf-tagging | OSM Simple Indoor Tagging, 16 loại feature IMDF, yêu cầu GeoPackage, nhập vào QGIS, bảng đính chính PRIMARY_OBJECTIVE |
| 05-market-tools | Khảo sát công cụ trên thị trường: mã nguồn mở, thương mại, chi phí, khuyến nghị |

Mỗi ghi chú mở đầu bằng câu hỏi nghiên cứu, kết luận ngắn, độ tin cậy. Các file _sources.md liệt kê nguồn đã thử.

## docs/

| File | Nội dung |
|---|---|
| cad-vs-bim.md | CAD khác BIM thế nào |
| bim-pipeline-3d-7d.md | Các chiều BIM từ 3D đến 7D |
| mapping-design.md | Thiết kế ánh xạ layer/class sang tag |
| cad-to-gpkg-design.md | Đặc tả pipeline (spec) |
| local-env-report.md | Môi trường máy local: công cụ đã cài |
| qgis-verification.md | Kết quả kiểm tra GPKG trong QGIS |

## src/

Luồng xử lý: ingest, cad2bim hoặc extract, georeference, normalize, export, validate.

| Đường dẫn | Việc |
|---|---|
| cli.py | Lệnh build, check, imdf |
| pipeline.py | Nối các bước |
| config.py, model.py | Đọc cấu hình dự án; cấu trúc dữ liệu trung gian |
| ingest/ | Đọc DXF và IFC |
| cad2bim/ | Áp luật layer lên DXF để dựng phòng, cửa, cầu thang... |
| extract/ | Lấy đối tượng từ IFC; georeference (extract/georef.py) |
| normalize/ | Gán tag OSM và IMDF, tạo id, nhãn, cửa, xử lý chồng lấn |
| export/ | Ghi GPKG, kiểm tra, xuất gói IMDF (.zip) |

## Chạy nhanh

    .venv/bin/python -m src.cli build --project samples/project-dxf.yaml --out out/building.gpkg
    .venv/bin/python -m src.cli check out/building.gpkg
    .venv/bin/python -m src.cli imdf out/building.gpkg --out out/building.imdf.zip
    .venv/bin/python -m pytest

Chi tiết xem src/README.md.
