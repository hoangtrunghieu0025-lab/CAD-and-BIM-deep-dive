# Phiên E — Học thuật và dự án cộng đồng

Ngày truy cập tất cả nguồn: 2026-11-06. Bước pipeline: 1 ingest, 2 nhận diện phòng/cửa/tầng, 3 georeference, 4 chuẩn hoá (SIT/IMDF), 5 ghi GPKG, 6 mở QGIS.

## Câu hỏi nghiên cứu
Đã có nghiên cứu học thuật / dự án cộng đồng nào (đặc biệt có mã nguồn mở) chuyển IFC/CAD sang dữ liệu GIS trong nhà (IndoorGML, CityGML, OSM indoor, IMDF), trích navigation graph, nhận diện phòng từ CAD — và dùng lại được đến đâu cho luồng CAD/BIM → GeoPackage?

## Kết luận ngắn
- IFC → IndoorGML, IFC → OSM indoor (SIT) và IFC → CityGML/CityJSON đều có repo mã nguồn mở, nhưng đều là công cụ lẻ, đa số kiểu prototype/học thuật, một số đã lưu trữ hoặc nói rõ là đang xây lại.
- KHÔNG tìm thấy repo mã nguồn mở nào làm IFC/CAD → IMDF trọn vẹn (chỉ thấy FME thương mại, và gói npm indoorgml-to-imdf chưa đọc được). Không tìm thấy repo nào làm DXF/DWG → IMDF hoặc OSM indoor.
- Không có công cụ nào ghi GPKG trực tiếp; nhận diện phòng từ DXF thuần hình học chưa có giải pháp sẵn đáng tin (chỉ có repo ảnh/GeoJSON). Hướng thực tế: ghép thành phần (IfcOpenShell, ezdxf, Shapely, BIMtoOSM làm tham khảo ánh xạ) và tự viết phần IMDF + GPKG.

## Độ tin cậy
Trung bình. Thông tin repo lấy từ trang GitHub qua WebFetch (tóm tắt tự động): giấy phép/sao đọc được, nhưng NGÀY COMMIT CUỐI hầu như không hiển thị → "chưa xác minh". Một số trang trả 403/lỗi kết nối (xem cuối file).

## IFC → IndoorGML

### ifc2indoorgml (GRID Lab UNSW) + bài báo ISPRS 2022
- Loại: repo + bài báo.
- URL: https://github.com/grid-unsw/ifc2indoorgml ; https://ual.sg/publication/2022-isprs-ifc-2-indoorgml/ ; DOI https://doi.org/10.5194/isprs-archives-xliii-b4-2022-295-2022
- Năm: 2022.
- Mô tả: bài "ifc2indoorgml: An open-source tool for generating IndoorGML from IFC" (Diakite, Díaz-Vilariño, Biljecki, Isikdag, Simmons, Li, Zlatanova). Abstract: IFC chi tiết nhưng phức tạp; IndoorGML trừu tượng hơn, phù hợp điều hướng; công cụ nhằm khuyến khích tạo và chia sẻ mô hình IndoorGML.
- Đầu vào/ra: IFC → IndoorGML.
- Mã nguồn: có. Giấy phép Apache-2.0; 12 sao; 7 commit; README trỏ tới Installation Guide PDF. Ngôn ngữ: suy từ tên file là C++/CMake/Qt (trang không liệt kê; theo kết quả tìm kiếm là C++ dùng IFC++). Hoạt động: chưa xác minh (không thấy ngày commit; chỉ 7 commit).
- Mức dùng lại: thành phần/tham khảo (IndoorGML không phải đích của dự án; hữu ích để tham chiếu cách trích navigation graph từ IFC; có GUI Qt, khó nhúng vào pipeline Python).
- Phủ bước: 1, 2 (một phần), 4 (IndoorGML, không phải IMDF/SIT).
- Nguồn: các URL trên, 2026-11-06.
- Chưa xác minh: ngày commit cuối, ngôn ngữ chính xác, có sinh được door/connection đầy đủ không, có xử lý georeference không.

### Level Out (Bauhaus-Universität Weimar) — IFC → CityGML / IndoorGML / OSM
- Loại: dự án nghiên cứu + repo + talk FOSSGIS 2023.
- URL: https://bauinformatik.github.io/levelout ; https://github.com/bauinformatik/levelout ; web app https://github.com/bauinformatik/levelout-web ; talk https://pretalx.com/fossgis2023/talk/NBNV3B/
- Năm: 2022–2023 (tài trợ mFUND, 04/2022–06/2023).
- Mô tả: talk (Tauscher, Krishnakumar) trích floor plan 2.5D từ IFC, ánh xạ vào mô hình trung gian rồi sinh CityGML, IndoorGML, OpenStreetMap; kiểm chứng trên 2 toà nhà đại học và 1 trung tâm hành chính đang xây; nhấn mạnh open source.
- Đầu vào/ra: IFC (qua BIMserver) → CityGML, IndoorGML, OSM.
- Mã nguồn: có (BIMserver plugin bundle, Java/Maven). Giấy phép AGPL-3.0; 3 sao; 317 commit. README: phần build còn TODO, cần cài thủ công 2 JAR gml/indoorgml 2.6.2-SNAPSHOT. Hoạt động: chưa xác minh (dự án tài trợ kết thúc 06/2023).
- Mức dùng lại: chỉ tham khảo / thành phần khái niệm (mô hình trung gian 2.5D từ IFC là ý tưởng sát nhất với nhu cầu; nhưng phụ thuộc BIMserver, AGPL).
- Phủ bước: 1, 2, 4 (OSM nhưng chưa xác nhận có theo SIT), không có 5/6.
- Nguồn: URL trên, 2026-11-06.
- Chưa xác minh: ngày commit, chất lượng đầu ra OSM, ngôn ngữ chính xác, trạng thái bảo trì.

### Bài báo navigation graph từ IFC (TU Delft, 2026)
- Loại: luận án.
- URL: https://repository.tudelft.nl/record/uuid:ba9ea5f6-abdf-44e4-8a6f-cb50bdf804f2 (tiêu đề theo kết quả tìm kiếm: "From IFC BIM to Semantically Enriched 2.5D Indoor Navigation Graphs for Congestion-Aware Pedestrian Simulation")
- Năm: 2026 (theo kết quả tìm kiếm).
- Mô tả (từ snippet tìm kiếm, chưa đọc trang): áp dụng cho ga metro, đồ thị 18.454 nút / 134.852 cạnh trên 3 tầng.
- Mã nguồn: chưa xác minh (trang không tải được: ECONNREFUSED).
- Mức dùng lại: chỉ tham khảo.
- Phủ bước: 2 (nav graph).
- Nguồn: kết quả WebSearch 2026-11-06.
- Chưa xác minh: toàn bộ chi tiết, có code không.

## IFC → CityGML

### ifc2citygml (TU Delft 3D)
- Loại: repo (đã lưu trữ).
- URL: https://github.com/tudelft3d/ifc2citygml (URL tudelft-gist cũ chuyển hướng đến đây)
- Năm: GeoBIM, lưu trữ 2023-04-04.
- Mô tả: README: chuyển IFC2x3 sang CityGML LOD3, LOD2 và LOD4 "có thể"; gồm ifc2off (IfcOpenShell + OpenCascade) và off2citygml (CGAL). Tác giả ghi "We do not maintain this code anymore" và trỏ tới esri_geobim.
- Mã nguồn: có, GPL-3.0, 74 sao, 19 fork, archived/read-only.
- Mức dùng lại: chỉ tham khảo (không bảo trì, GPL, chủ yếu vỏ ngoài). Nguồn khác (luận án Donkers) cho biết phòng không phát hiện được từ hình học — chưa đọc trực tiếp.
- Phủ bước: 1, 4 (CityGML ngoài phạm vi đích).
- Nguồn: URL trên, 2026-11-06.
- Chưa xác minh: chất lượng LoD4.

### IfcEnvelopeExtractor / IFC_BuildingEnvExtractor (TU Delft, GISmantike)
- Loại: repo + bài báo (IJGI 2025, doi 10.3390/ijgi14120465, van der Vaart, Arroyo Ohori, Stoter; theo kết quả tìm kiếm).
- URL: https://github.com/tudelft3d/IFC_BuildingEnvExtractor ; https://www.preprints.org/manuscript/202509.2284 (preprint trả 403, chỉ lấy từ snippet)
- Năm: 2025.
- Mô tả (README): chuyển IFC (IFC2x3, IFC4, IFC4x3 ADD2) sang mô hình GIS ở nhiều LoD; đầu ra CityJSON, tuỳ chọn STEP, OBJ, DXF, báo cáo JSON. Có trích phòng dựa trên hình học IfcSpace (LoD 0.2/1.2/2.2/3.2) và storey (LoD 0.2, 0.3); "Generate interior" mặc định tắt; không có IfcSpace thì không xuất space; trích apartment còn đang phát triển.
- Mã nguồn: có. Dual LGPL-3.0/GPL-3.0; 44 sao; 640 commit; README nêu tài trợ đến 11/2026 (một kết quả tìm kiếm ghi 08/2026 — mâu thuẫn, chưa xác minh). Ngôn ngữ: C++ (CMake), GUI Python (suy từ cấu trúc). Hoạt động: có vẻ đang hoạt động, ngày commit cuối chưa xác minh.
- Mức dùng lại: thành phần (nguồn polygon phòng/storey từ IfcSpace; CityJSON, không phải GPKG).
- Phủ bước: 1, 2, một phần 3.
- Nguồn: URL trên, 2026-11-06.
- Chưa xác minh: georeference, cửa, ngày commit.

### esri_geobim (TU Delft)
- Loại: repo. URL: https://github.com/tudelft3d/esri_geobim — WebFetch lỗi "socket hang up". Chỉ biết qua search snippet: build bằng IfcConvert + CMake, binary `tudelft_esri_geobim`. Tất cả chi tiết khác: chưa xác minh. Trang dự án: https://3d.bk.tudelft.nl/projects/geobim/ (chỉ qua search).

### BIMConvertToGeo (SEUZFY)
- Loại: repo. URL: https://github.com/SEUZFY/BIMConvertToGeo — chỉ thấy trong kết quả tìm kiếm (C++ IFC → CityJSON theo snippet); chưa mở. Chưa xác minh giấy phép/trạng thái.

## IFC/CAD → IMDF hoặc OSM indoor

### BIMtoOSM (Rebecca Schmidt)
- Loại: repo (parser IFC → OSM).
- URL: https://github.com/rebeccasc/BIMtoOSM ; https://rebeccasc.github.io/BIMtoOSM
- Mô tả (README): parse IFC4 / IFC2x3 TC1, giảm hình học 3D xuống 2D, xuất OSM theo Simple Indoor Tagging. Ánh xạ: slab/column → indoor=area; wall → indoor=wall; door → door=yes; stair → highway=steps; window đang làm; material không hỗ trợ. Cấu hình: engine BODY hoặc BOUNDING_BOX (mặc định), gộp node gần nhau. Xuất `.osm` hoặc dùng qua API Kotlin; đã tích hợp vào JOSM IndoorHelper (bản cũ hơn).
- Mã nguồn: có. AGPL-3.0; 11 sao; 3 fork; 176 commit. README cảnh báo "being rebuilt from scratch, API might change". Ngôn ngữ: JVM (Java/Kotlin, suy). Hoạt động: chưa xác minh ngày commit.
- Mức dùng lại: tham khảo mạnh (bảng ánh xạ IFC → SIT) / thành phần; AGPL cần cân nhắc khi nhúng; đầu ra OSM XML, không phải GPKG; chưa có phòng IfcSpace → indoor=room trong danh sách ánh xạ đọc được.
- Phủ bước: 1, 2 (một phần), 4 (SIT).
- Nguồn: 2 URL trên, 2026-11-06.
- Chưa xác minh: có xử lý IfcSpace/level không, georeference.

### JOSM IndoorHelper
- Loại: plugin repo. URL: https://www.github.com/JOSM/indoorhelper ; wiki https://wiki.openstreetmap.org/wiki/JOSM/Plugins/indoorhelper
- Mô tả: plugin JOSM tạo/kiểm tra/xem bản đồ indoor theo Simple Indoor Tagging. Wiki (qua search) liệt kê "import BIM data (beta)". Trang GitHub không nêu rõ IFC import.
- Mã nguồn: có, AGPL-3.0, 13 sao, 8 fork, 270 commit; theo search lần push gần nhất 2025-03-12 (chưa xác minh trực tiếp).
- Mức dùng lại: thành phần thủ công / validator SIT; không tự động hoá được trong pipeline.
- Phủ bước: 4 (SIT), một phần 1.
- Chưa xác minh: chất lượng import IFC hiện tại.

### ifc2geojson (bertt)
- Loại: repo. URL: https://github.com/bertt/ifc2geojson
- Mô tả: "Experimental tool library for converting IFC model to GeoJSON (per storey)". Lệnh mẫu `ifc2geojson -i file.ifc`.
- Mã nguồn: có, MIT, 8 sao, 25 commit; .NET/C# (xbim, GeoJSON.Net — suy từ dependency). Theo search, push cuối 01/2020 → coi như không hoạt động (chưa xác minh trực tiếp).
- Mức dùng lại: chỉ tham khảo (GeoJSON theo tầng, không IMDF).
- Phủ bước: 1, 2 (một phần).
- Chưa xác minh: định dạng đầu ra cụ thể.

### FME IFC → IMDF (thương mại, đối chứng)
- URL: https://support.safe.com/hc/en-us/articles/25407623541517-Converting-IFC-to-IMDF (403 khi fetch); https://support.safe.com/hc/en-us/articles/25407643555085 (chỉ qua search). Theo search, FME có workspace/template IFC và DWG → IMDF và IMDFValidator transformer. Không phải mã nguồn mở; chi phí không ước đoán. Chi tiết: chưa xác minh.

### indoorgml-to-imdf (npm)
- URL: https://npmjs.com/package/indoorgml-to-imdf — 403, chỉ thấy tên và mô tả ngắn qua search (IndoorGML → IMDF, Node.js). Giấy phép, repo, chất lượng: chưa xác minh.

### Không tìm thấy
- Công cụ mã nguồn mở IFC → IMDF hoặc DXF/DWG → IMDF/OSM indoor: không thấy qua các truy vấn đã chạy (xem "Khoảng trống").

## Nhận diện phòng từ CAD / semantic enrichment

### cansik/architectural-floor-plan (AFPlan)
- Loại: repo. URL: https://github.com/cansik/architectural-floor-plan
- Mô tả (README): phát hiện phòng nhanh trên floor plan: làm sạch hình thái học, ML + convex hull đóng khe hở, connected component. Vào: ảnh; ra: CSV hoặc SVG; DWG/DXF "đã chuẩn bị" nhưng thư viện chuyển đổi chưa đánh giá giấy phép.
- Mã nguồn: có; giấy phép không nêu trên trang (chưa xác minh); 405 sao, 87 fork, 428 commit; Java/Gradle JDK 11+ (suy). Search ghi push cuối 10/2021.
- Mức dùng lại: chỉ tham khảo (đầu vào ảnh raster, không phải DXF vector).
- Phủ bước: 2.

### waddason/CapstoneContour
- Loại: repo sinh viên (IP-Paris cho VINCI-ENERGIES/DIANE). URL: https://github.com/waddason/CapstoneContour
- Mô tả: phát hiện phòng trong floor plan AutoCAD; 3 mô hình: SegmentBasedClustering (hình học), CapstoneVisionSegmentation (CV2), SAMSegmentation (SAM, GPU). Vào: GeoJSON xuất từ AutoCAD (shapely GeometryCollection); ra: GeoJSON đường viền phòng.
- Mã nguồn: có, MIT, 1 sao, 126 commit; "closed to contributions". Ngôn ngữ: Python (suy). Hoạt động: chưa xác minh.
- Mức dùng lại: thành phần/tham khảo (mô hình hình học trên GeoJSON phù hợp sau bước DXF → GeoJSON); độ chính xác chưa được kiểm chứng.
- Phủ bước: 2.

### Bloch, Wu, Alnuzha, Borrmann (TUM) — graph-based semantic enrichment
- Loại: bài báo (EC3 2024, theo search). URL: https://mediatum.ub.tum.de/download/1749097/1749097.pdf (chỉ qua search snippet, chưa mở). Snippet: Girvan-Newman tách căn hộ, GNN phân loại phòng. Mã nguồn, cửa: chưa xác minh. Mức: chỉ tham khảo.

### archit-app (PyPI)
- URL: https://pypi.org/project/archit-app/ — chỉ qua search: thư viện Python floor plan, đọc/ghi DXF, xuất GeoJSON, dùng quy ước layer riêng; không nhắc IMDF. Giấy phép/repo: chưa xác minh.

### Mẫu DXF → GeoJSON (ezdxf/GeoPandas)
- URL: https://expandmapping.substack.com/p/mapping-a-floor-plan-cad-file-in — chỉ search snippet; ý: ezdxf → GeoJSON → GeoPandas; chưa mở. Bước polygonize polyline kín thành phòng (ví dụ Shapely `polygonize`) KHÔNG thấy repo có sẵn.

## Chuẩn liên quan

### IndoorGML (OGC)
- URL: https://www.ogc.org/standards/indoorgml/ ; https://docs.ogc.org/is/22-045r5/22-045r5.html
- Mô tả: mô hình dữ liệu mở + schema XML cho không gian trong nhà phục vụ điều hướng, là application schema của GML 3.2.1 (bản 1.x). Phiên bản liệt kê: 2.0 Part 1 Conceptual Model (22-045r5), 1.1 (19-011r4), 1.0.x. OGC công bố 2.0 Part 1 ngày 2025-08-28 (qua search); 2.0 tách mô hình khái niệm khỏi encoding; Part 2 chưa xác minh. Miễn phí tải.
- Phủ: tham chiếu cho nav graph (bước 2/4).

### CityGML (OGC)
- URL: chỉ qua search (TUM): https://www.asg.ed.tum.de/en/gis/projects/citygml-30/ ; chuẩn không đọc trực tiếp.
- CityGML 3.0: LoD4 bị bỏ, nội thất tích hợp vào LoD0–3; khái niệm Space/SpaceBoundary; có thể ánh xạ sang IndoorGML (theo nguồn thứ cấp). Part 1 được OGC thông qua 09/2021 (nguồn thứ cấp). Chưa xác minh bản gốc.

### IMDF (Apple, OGC Community Standard)
- URL: https://docs.ogc.org/cs/20-094/
- Mô tả: OGC Community Standard 1.0.0 (20-094), công bố 2021-02-18; mô hình tổng quát cho không gian trong nhà, đối tượng là GeoJSON (RFC 7946). Đề xuất bởi Apple, Autodesk, Esri, Google, NYC DoITT, Ordnance Survey, Safe Software. Nội dung cố định tại OGC; bản mới nhất do Apple lưu trữ riêng. Cộng đồng Safe nói IMDF có schema cố định, phải ánh xạ dữ liệu nguồn vào các feature type định sẵn.
- Liên hệ với IndoorGML: khác mục đích — IndoorGML cho mạng điều hướng/topology, IMDF cho bản đồ hiển thị/định vị; IMDF dùng GeoJSON nên gần GPKG/QGIS hơn.

## Bảng tóm tắt

| Mục | Hướng | Mã nguồn / giấy phép | Dùng lại | Bước |
|---|---|---|---|---|
| ifc2indoorgml | IFC → IndoorGML | có, Apache-2.0, 12 sao | thành phần/tham khảo | 1,2,4 |
| Level Out | IFC → CityGML/IndoorGML/OSM | có, AGPL-3.0, 3 sao | tham khảo | 1,2,4 |
| ifc2citygml | IFC → CityGML | có, GPL-3.0, archived | tham khảo | 1,4 |
| IFC_BuildingEnvExtractor | IFC → CityJSON (+space) | có, LGPL/GPL-3.0, 44 sao | thành phần | 1,2,3 |
| BIMtoOSM | IFC → OSM SIT | có, AGPL-3.0, 11 sao | tham khảo/thành phần | 1,2,4 |
| JOSM IndoorHelper | OSM SIT editor, IFC beta | có, AGPL-3.0 | thủ công | 4 |
| ifc2geojson | IFC → GeoJSON/tầng | có, MIT, ~2020 | tham khảo | 1,2 |
| FME IFC/DWG → IMDF | → IMDF | thương mại | đối chứng | 1–4 |
| AFPlan | ảnh → phòng | có, giấy phép chưa rõ | tham khảo | 2 |
| CapstoneContour | GeoJSON(CAD) → phòng | có, MIT | thành phần/tham khảo | 2 |
| IMDF / IndoorGML / CityGML | chuẩn | mở | đặc tả | 4 |

## Khoảng trống học thuật/cộng đồng
- Không có repo mở IFC → IMDF hoặc CAD (DXF/DWG) → IMDF/OSM indoor; không có công cụ nào ghi GPKG.
- Nhận diện phòng từ DXF vector (polygonize, đóng khe cửa, gán tên phòng từ text/block) chưa có giải pháp mở hoàn chỉnh; các repo tìm thấy dùng ảnh hoặc GeoJSON.
- Georeference (CRS, điểm khống chế) hầu như không được các công cụ trên mô tả.
- Ngày commit/hoạt động của hầu hết repo chưa xác minh; nhiều repo là sản phẩm dự án tài trợ hữu hạn.
- Giấy phép copyleft (AGPL/GPL) hạn chế nhúng trực tiếp; nên chỉ dùng làm tham khảo ánh xạ hoặc gọi như tiến trình ngoài (cần tư vấn pháp lý).

## Nguồn (truy cập 2026-11-06)
- https://github.com/grid-unsw/ifc2indoorgml
- https://ual.sg/publication/2022-isprs-ifc-2-indoorgml/
- https://bauinformatik.github.io/levelout ; https://github.com/bauinformatik/levelout
- https://pretalx.com/fossgis2023/talk/NBNV3B/
- https://github.com/tudelft3d/ifc2citygml
- https://github.com/tudelft3d/IFC_BuildingEnvExtractor
- https://github.com/rebeccasc/BIMtoOSM ; https://rebeccasc.github.io/BIMtoOSM
- https://www.github.com/JOSM/indoorhelper
- https://github.com/bertt/ifc2geojson
- https://github.com/cansik/architectural-floor-plan
- https://github.com/waddason/CapstoneContour
- https://www.ogc.org/standards/indoorgml/
- https://docs.ogc.org/cs/20-094/ (qua search)
- Kết quả WebSearch (snippet): docs.ogc.org/is/22-045r5, asg.ed.tum.de CityGML 3.0, mediatum.ub.tum.de TUM paper, expandmapping.substack.com, pypi.org/project/archit-app

## Không truy cập được / chưa xác minh
- https://github.com/tudelft3d/esri_geobim — socket hang up.
- https://repository.tudelft.nl/record/uuid:ba9ea5f6-abdf-44e4-8a6f-cb50bdf804f2 — ECONNREFUSED.
- https://support.safe.com/hc/en-us/articles/25407623541517-Converting-IFC-to-IMDF — 403.
- https://npmjs.com/package/indoorgml-to-imdf — 403.
- https://www.preprints.org/manuscript/202509.2284 — 403.
- Không mở trực tiếp: docs.ogc.org IMDF/IndoorGML 2.0 PDF, bài TUM EC3 2024, BIMConvertToGeo, archit-app, IMDF spec của Apple.
- Ngày commit cuối của hầu hết repo GitHub: trang không hiển thị.
