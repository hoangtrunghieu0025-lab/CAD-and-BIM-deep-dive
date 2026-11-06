---
id: TASK-014
title: "[IN_REVIEW][MAIN] Khảo sát công cụ có sẵn trên thị trường cho bài toán CAD/BIM → GPKG (OSM + IMDF) và chi phí"
category: MAIN
assignees: [claude-laptop, claude-mobile]
created_by: claude-laptop
created_at: 2026-11-06T11:38:51+07:00
updated_at: 2026-11-06T12:00:39+07:00
status: in_review
priority: high
depends_on: []
---

# [IN_REVIEW][MAIN] TASK-014 — Khảo sát công cụ có sẵn trên thị trường cho bài toán CAD/BIM → GPKG (OSM + IMDF) và chi phí

## Mô tả
Trước khi xây pipeline (TASK-010) cần biết **đã có công cụ sẵn cho đúng bài toán này chưa**, chi phí bao nhiêu, để quyết định *tự xây / mua / dùng kết hợp* và để **đối chiếu** với thiết kế của dự án. Yêu cầu của chủ dự án: làm **sớm** và **cho phép chạy multi-agent, nhiều phiên song song** để tăng tốc.

Bài toán của dự án (từ `PRIMARY_OBJECTIVE.md`): nhận DXF/DWG hoặc IFC → nhận diện phòng/cửa/tầng → georeference → chuẩn hoá theo **OSM Simple Indoor Tagging** và **IMDF** → ghi **GeoPackage** → mở được trong **QGIS**.

Câu hỏi cần trả lời:
1. Có công cụ (thương mại, miễn phí, mã nguồn mở, dịch vụ cloud) nào làm được **toàn bộ hoặc một phần** luồng trên không? Phần nào của luồng được phủ?
2. **Chi phí**: giá niêm yết (theo người dùng/năm, theo dự án, theo diện tích…), gói miễn phí/dùng thử, chi phí vận hành nếu tự host, giấy phép (mã nguồn mở nào, có ràng buộc thương mại không).
3. Công cụ có đọc **DXF/DWG** và/hoặc **IFC**, xuất **IMDF** hoặc **GPKG**, hỗ trợ **OSM indoor tags**, tự động hoá bằng **CLI/API/script** không, chạy được trên Linux không?
4. Khoảng trống: phần nào của bài toán **chưa công cụ nào** làm tốt (đây là giá trị của việc tự xây).

## Ứng viên gợi ý (CHƯA XÁC MINH — chỉ là điểm xuất phát; phải kiểm tồn tại và tính năng thật, và tìm thêm ứng viên ngoài danh sách)
- Nền tảng ETL/GIS thương mại: FME (Safe Software), ArcGIS Pro / ArcGIS Indoors (Esri).
- Phần mềm CAD/BIM phổ biến và khả năng xuất sang GIS: Autodesk (AutoCAD/Civil 3D/Revit), Bentley.
- Mã nguồn mở: GDAL/OGR (driver DXF, GPKG), IfcOpenShell/IfcConvert, QGIS và plugin của nó, các công cụ indoor của OSM (ví dụ plugin JOSM cho indoor), các thư viện tạo/kiểm IMDF trên GitHub.
- Dịch vụ/chương trình bản đồ trong nhà: Apple Indoor Maps Program, nhà cung cấp indoor mapping thương mại (Mapsted, MazeMap, Pointr, Archilogic… — chỉ là tên để kiểm).
- Dự án học thuật/cộng đồng chuyển IFC → CityGML/IndoorGML/GIS (kể tên nếu tìm thấy; không tự đặt tên).

## Cách chạy multi-agent (được phép)
Chia theo **chủ đề độc lập**, mỗi phiên/agent một chủ đề, ghi **file riêng** để không xung đột git:

| Phiên | Chủ đề | File đầu ra (trong `research/05-market-tools/`) |
|---|---|---|
| A | Công cụ thương mại ETL/GIS: FME, ArcGIS (Pro, Indoors) và tương đương | `commercial-gis-etl.md` |
| B | Công cụ CAD/BIM sẵn có và đường xuất sang GIS/IMDF: Autodesk, Bentley, các add-in | `cad-bim-vendors.md` |
| C | Mã nguồn mở và thư viện: GDAL/OGR, IfcOpenShell, QGIS plugin, JOSM indoor, công cụ IMDF trên GitHub | `open-source-tools.md` |
| D | Dịch vụ/nhà cung cấp indoor mapping (Apple Indoor Maps Program, các hãng indoor) và mô hình giá | `indoor-mapping-services.md` |
| E | Học thuật/cộng đồng: IFC → GIS/IndoorGML/CityGML, bài báo, dự án GitHub | `academic-community.md` |
| F (tổng hợp, làm **sau** khi A–E xong) | Bảng so sánh, bảng chi phí, khoảng trống, khuyến nghị build/buy | `comparison-and-recommendation.md` |

- Mỗi phiên A–E **chỉ ghi vào file của mình** và ghi nguồn (URL + ngày truy cập) **ngay trong file đó**; phiên F gộp nguồn vào `research/sources.md` (chỉ thêm dòng) để tránh nhiều agent cùng sửa một file.
- Có thể chạy A–E đồng thời (subagent hoặc nhiều phiên). Mobile có thể nhận một số phiên nếu mạng cho phép; phiên nào không đọc được trang nào phải ghi "không truy cập được" thay vì đoán.
- Phiên F kiểm tra chéo: mỗi con số giá và mỗi khẳng định tính năng trong bảng phải có nguồn ở file A–E.

## Quyết định của chủ dự án (2026-11-06)
- **Thư mục**: được phép tạo và ghi `research/05-market-tools/` (không cần sửa `CLAUDE.md`; quyết định này thay cho ràng buộc "chỉ `research/01..04`" riêng cho task này).
- **Phạm vi giấy phép**: khảo sát **cả mã nguồn mở và thương mại**, không đặt trần chi phí.
- **Thứ tự ưu tiên**: **mã nguồn mở xếp trước** — trong mọi file và trong bảng so sánh, nhóm mã nguồn mở đứng đầu, rồi đến miễn phí không mở mã nguồn, rồi thương mại. Phiên C (mã nguồn mở) chạy trước hoặc ưu tiên nhiều tài nguyên nhất; kết luận build/buy xét ứng viên mã nguồn mở trước khi nhắc tới phương án trả phí.
- **Đăng ký task**: task được đăng ký trước các task khác của laptop còn `TODO` (TASK-013 là `SIDE`, làm sau).

## Quy tắc nội dung (bắt buộc)
- **Không bịa**: tên sản phẩm, tính năng, giá. Không chắc → ghi "chưa xác minh" (theo `CLAUDE.md`).
- **Giá**: ghi *giá niêm yết*, *đơn vị tính* (người dùng/năm, theo dự án…), *tiền tệ*, *ngày truy cập*, *URL*. Trang ghi "liên hệ báo giá" thì ghi đúng như vậy, **không ước đoán**. Quy đổi VND (nếu có) chỉ là tham khảo, ghi rõ tỉ giá và ngày.
- **Tính năng**: chỉ khẳng định khi có trang tài liệu chính thức hoặc đã chạy thử được; ưu tiên tài liệu chính hãng hơn blog/so sánh bên thứ ba (đánh dấu rõ nguồn thứ cấp).
- Tôn trọng chặn bot: không giả User-Agent, không vượt tường trả phí; trang bị chặn (403) ghi lại và dùng nguồn khác.
- Không gửi thông tin cá nhân, không đăng ký tài khoản hay mua gì trong quá trình khảo sát; dùng bản dùng thử chỉ khi chủ dự án cho phép.
- Viết tiếng Việt, giữ thuật ngữ kỹ thuật tiếng Anh; dùng mẫu `research/_templates/finding.md`.

## Đầu vào (inputs)
- `PRIMARY_OBJECTIVE.md` (mục 3: luồng và yêu cầu), `research/04-osm-imdf-tagging/` (yêu cầu IMDF/OSM/GPKG đã xác minh), `research/02-bim/prd-corrections-01-03.md`, `docs/local-env-report.md` (môi trường: Ubuntu, không GPU rời).

## Đầu ra mong đợi (expected_outputs)
- `research/05-market-tools/*.md` theo bảng trên (thư mục mới; xem Phạm vi ghi).
- `research/05-market-tools/comparison-and-recommendation.md` gồm:
  - **Bảng so sánh**: công cụ × tiêu chí (đọc DXF/DWG, đọc IFC, xuất IMDF, xuất GPKG, OSM indoor tags, CLI/API, chạy trên Linux, giấy phép, phủ bước nào của pipeline).
  - **Bảng chi phí**: công cụ, mô hình giá, giá niêm yết, đơn vị, nguồn, ngày; ước tính tổng chi phí năm đầu cho 1 người dùng và cho 5 người dùng khi có giá công khai.
  - **Khoảng trống** chưa công cụ nào phủ và **khuyến nghị**: tự xây / mua / kết hợp (kèm lý do và rủi ro: khoá nhà cung cấp, giấy phép, bảo trì).
  - **Đối chiếu** với thiết kế dự án: phần nào của TASK-007/009/010 trùng với công cụ sẵn có, có nên điều chỉnh phạm vi không.
- Danh sách "đã thử chạy" (nếu có công cụ mã nguồn mở chạy được trên máy này): lệnh, kết quả, hạn chế.

## Tiêu chí hoàn thành (acceptance)
- [x] Mỗi phiên A–E có file riêng, mỗi công cụ có: mô tả, phủ bước nào của pipeline, định dạng vào/ra, giấy phép/giá, nguồn + ngày truy cập
- [x] Mọi con số giá có nguồn hoặc ghi "liên hệ báo giá"/"chưa xác minh"
- [x] `comparison-and-recommendation.md` có bảng so sánh, bảng chi phí, khoảng trống, khuyến nghị và đối chiếu với TASK-007/009/010
- [x] Ít nhất 2 công cụ mã nguồn mở ứng viên được thử chạy trên mẫu `samples/` (nếu tồn tại công cụ phù hợp), hoặc ghi lý do không thử được
- [x] Nguồn mới được gộp vào `research/sources.md` (chỉ thêm dòng)
- [x] Đã báo cáo cho chủ dự án (laptop: không tự commit)

## Phạm vi từng bên
- **claude-laptop**: có truy cập web rộng; ghi vào `research/05-market-tools/` (thư mục mới tạo cho task này), file task này và thêm dòng vào `research/sources.md`. Theo yêu cầu của chủ dự án, **không tự commit**; báo cáo xong để chủ dự án pull rồi mới commit.
- **claude-mobile**: được nhận một số phiên (A–E) nếu mạng cho phép; chỉ ghi vào file của phiên mình trong `research/05-market-tools/`. Không sửa file của phiên khác.
- Không sửa `PRIMARY_OBJECTIVE.md`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | in_review | 2026-11-06T12:00:39+07:00 | A–F xong; chờ chủ dự án/mobile xem khuyến nghị |
| claude-mobile | todo | 2026-11-06T11:38:51+07:00 | chưa nhận; có thể nhận một số phiên A–E |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T11:42:13+07:00 | todo | Đăng ký task. Chủ dự án trả lời: (1) cho phép tạo `research/05-market-tools/` (đã tạo, có `.gitkeep`); (2) chấp nhận cả công cụ mã nguồn mở lẫn thương mại, **ưu tiên mã nguồn mở xếp lên đầu**. Chưa bắt đầu khảo sát. |
| 2026-11-06T11:47:59+07:00 | in_progress | Chủ dự án ra lệnh chạy. Mở 5 subagent (A thương mại ETL/GIS, B CAD/BIM vendor, C mã nguồn mở, D dịch vụ indoor, E học thuật/cộng đồng) ghi vào `research/05-market-tools/`; phiên F tự làm sau khi A–E xong. Không commit. |
| 2026-11-06T12:00:39+07:00 | in_review | Phiên A–E xong (5 subagent, mỗi bên một file). Phiên F: kiểm chéo bằng nguồn gốc (FME IMDF Reader/Writer, giá Archilogic, GitHub API các repo, GDAL 3.13.3, chạy lại ogr2ogr DXF→GPKG); phát hiện và sửa 1 sai sót của phiên C (3 repo IMDF tồn tại); viết `comparison-and-recommendation.md`; gộp nguồn vào `research/sources.md`. Chưa commit. |

## Kết quả
Ngày 2026-11-06. Khảo sát 5 phiên (subagent song song) + phiên F tổng hợp; file trong `research/05-market-tools/`.

| Phiên | File | Số mục khảo sát | Phát hiện chính |
|---|---|---|---|
| A thương mại ETL/GIS | `commercial-gis-etl.md` | 6 | FME có IMDF Reader/Writer (đã tự xác minh); ArcGIS Indoors ra IMDF gián tiếp qua FME; giá đều "liên hệ báo giá" |
| B CAD/BIM vendor | `cad-bim-vendors.md` | 10 | Không phần mềm CAD/BIM nào xuất thẳng GPKG/IMDF; chỉ Windows/macOS; giá Archicad/OpenBuildings/SketchUp có công khai |
| C mã nguồn mở (ưu tiên) | `open-source-tools.md` | ~18 | Không công cụ nào làm trọn luồng; `ogr2ogr` DXF→GPKG chạy nhưng không có tag OSM/IMDF; BIMtoOSM (IFC→OSM SIT) gần nhất nhưng ngừng từ 2024-08 |
| D dịch vụ indoor | `indoor-mapping-services.md` | 8 | Archilogic nhận DWG/DXF, xuất IMDF; giá công khai ($24.90/$59 /floor plan/tháng; $329/lần); Apple Indoor Maps Program miễn phí nhưng chỉ nhận IMDF |
| E học thuật/cộng đồng | `academic-community.md` | ~20 | Không repo mở nào làm IFC/CAD→IMDF; có IFC→OSM SIT, IFC→IndoorGML, IFC→CityJSON rời rạc |
| F tổng hợp | `comparison-and-recommendation.md` | — | Bảng so sánh, chi phí, khoảng trống, khuyến nghị, đối chiếu TASK-007/009/010 |

**Khuyến nghị**: tự xây lõi bằng Python mã nguồn mở; dùng FME hoặc Archilogic chỉ khi cần gói IMDF để nộp Apple/Microsoft Places (hoặc làm chuẩn đối chiếu), sau khi có báo giá. Đề xuất thêm vào phạm vi TASK-009 một mô-đun tuỳ chọn xuất gói IMDF (ZIP) từ các bảng GPKG.

**Sai sót đã sửa trong quá trình tổng hợp**: phiên C ghi `imdfjson`, `IMDF-Builder-for-Places`, `IMDFrnt` là "không tìm thấy"; phiên F kiểm bằng GitHub API và cả ba tồn tại (đã sửa trong `open-source-tools.md`).

**Hạn chế**: nhiều giá thương mại không công khai hoặc chỉ có từ nguồn thứ cấp; tiền tệ trên trang Archilogic không được ghi; một số trang trả 403/404; chưa khảo sát Google/Mapbox; chưa thử DWG, LibreDWG, JOSM, QGIS GUI.

## Blocker / câu hỏi mở
- ~~Thư mục `research/05-market-tools/`~~ — ĐÃ ĐƯỢC PHÉP (2026-11-06).
- ~~Ngân sách/giấy phép~~ — ĐÃ CHỐT: cả mã nguồn mở và thương mại, mã nguồn mở xếp đầu, không đặt trần chi phí.
- Chờ chủ dự án/mobile xem khuyến nghị (đặc biệt đề xuất thêm mô-đun xuất gói IMDF vào TASK-009) và quyết định có xin báo giá FME / dùng thử Archilogic không.
- Chưa commit (theo yêu cầu chủ dự án).
