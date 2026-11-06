# Phiên F — So sánh, chi phí, khoảng trống và khuyến nghị (TASK-014)

- **Câu hỏi nghiên cứu**: Trên thị trường đã có công cụ sẵn cho bài toán DXF/DWG/IFC → nhận diện phòng/cửa/tầng → georeference → OSM Simple Indoor Tagging + IMDF → GeoPackage → QGIS chưa? Chi phí bao nhiêu? Nên tự xây, mua hay kết hợp?
- **Kết luận ngắn**:
  1. **Không có công cụ nào, mã nguồn mở hay thương mại, làm trọn luồng này.** Không công cụ nào được xác minh là sinh **OSM Simple Indoor Tagging** từ CAD, và không công cụ nào ghi **GPKG chuẩn IMDF**.
  2. **IMDF thì đã có người làm**, nhưng theo kiểu "gói IMDF (ZIP/GeoJSON) để nộp Apple/Microsoft Places", không phải GPKG: FME (có IMDF Reader/Writer, đã tự xác minh trong tài liệu chính hãng), Archilogic (DWG/DXF/PDF → IMDF, giá công khai), Pointr, Mappedin, và ArcGIS Indoors (qua workbench FME).
  3. **Mã nguồn mở chỉ có các "mảnh"**: GDAL/OGR, ezdxf, IfcOpenShell, shapely, geopandas, QGIS. Phần khó nhất (nhận diện phòng/cửa từ CAD, georeference, sinh tag OSM/IMDF, đóng gói IMDF) **phải tự viết**.
  4. **Khuyến nghị: tự xây lõi bằng Python mã nguồn mở** (đúng kế hoạch hiện tại), dùng FME hoặc Archilogic chỉ như **công cụ đối chiếu/xuất gói IMDF** khi thật sự cần nộp cho Apple/Places, và chỉ sau khi có báo giá. Chi tiết ở mục 5.
- **Độ tin cậy**: trung bình-cao. Các điểm quyết định đã được phiên F **tự kiểm lại bằng nguồn gốc** (mục 6). Phần còn lại lấy từ phiên A–E, ghi rõ "theo phiên X, chưa kiểm lại". Giá thương mại phần lớn **không công khai**; không có số nào được ước đoán.
- **Ngày truy cập tất cả nguồn**: 2026-11-06. Thứ tự trình bày: mã nguồn mở trước, thương mại sau (theo quyết định của chủ dự án).

## 1. Bài toán và tiêu chí
Yêu cầu từ `PRIMARY_OBJECTIVE.md` (đã cập nhật): đầu vào DXF/DWG hoặc IFC; phòng/cửa/tầng; georeference; tag OSM SIT; IMDF (16 feature type; gói ZIP có `manifest.json`, bắt buộc `address` và `venue`); ghi `.gpkg`; mở được trong QGIS; chạy tự động (CLI), lý tưởng trên Linux.

Sáu bước của pipeline dùng ở mọi bảng: **1** ingest · **2** CAD→BIM (nhận diện) · **3** extract + georeference · **4** chuẩn hoá OSM/IMDF · **5** ghi GPKG · **6** QGIS.

## 2. Bảng so sánh (mã nguồn mở trước)
Nguồn từng dòng: `open-source-tools.md` (C), `academic-community.md` (E), `commercial-gis-etl.md` (A), `cad-bim-vendors.md` (B), `indoor-mapping-services.md` (D). Ký hiệu "✔F" = phiên F đã tự kiểm; "–" = không có; "?" = chưa xác minh.

### 2a. Mã nguồn mở / miễn phí
| Công cụ | Giấy phép | Vào | Ra | Bước | CLI / Linux | Dùng trực tiếp cho bài toán? |
|---|---|---|---|---|---|---|
| GDAL/OGR | MIT-style; bản mới nhất 3.13.3 (2026-08-18) ✔F | DXF; **không có driver DWG/IFC/IMDF** trong GDAL 3.8.4 hệ thống ✔F | GPKG, GeoJSON… | 1, 5 | CLI, Linux | **Thành phần.** `ogr2ogr` DXF→GPKG chạy ngay nhưng chỉ ra 1 layer `entities`, 51 feature, thuộc tính CAD, CRS rỗng, **không có tag OSM/IMDF** ✔F |
| ezdxf | MIT | DXF | DXF/đối tượng Python | 1, 2 | Python, Linux | Thành phần (đã dùng, xem `research/01-cad`) |
| IfcOpenShell (+IfcConvert) | LGPL-3.0 | IFC | đối tượng, SVG/OBJ/GLB… (không ra GIS) | 1, 2, 3 | Python/CLI, Linux | **Thành phần mạnh** (đã dùng, xem `research/02-bim`) |
| shapely, geopandas, pyogrio, pyproj | (giấy phép chưa kiểm trong phiên F) | – | GPKG… | 2, 3, 5 | Python, Linux | Thành phần (đã dùng) |
| LibreDWG | GPL-3.0 | DWG | DXF | 1 | CLI, Linux | Thành phần cho DWG (chưa thử) |
| ODA File Converter | **đóng**, miễn phí | DWG | DXF | 1 | CLI | Không mã nguồn mở; điều khoản chưa xác minh |
| QGIS | GPL-2.0 | GPKG, DXF… | – | 6 | GUI/PyQGIS | Dùng để xem/kiểm (đã thử nạp GPKG) |
| `BIMtoOSM` | **AGPL-3.0**; 11 sao; commit cuối **2024-08-18** (ngừng) ✔F | IFC | `.osm` (SIT) | 3, 4 | Kotlin | **Gần nhất cho bước 4 (IFC→OSM SIT)** nhưng cũ; chỉ nên **tham khảo ánh xạ** (AGPL) |
| JOSM IndoorHelper | AGPL-3.0 | `.osm`, IFC (qua BIMtoOSM) | `.osm` | 4 | GUI | Chỉnh tay |
| `ifc2indoorgml` | Apache-2.0; ~12 sao; 2022 | IFC | IndoorGML | 3, 4 | ? | Sai định dạng đích; tham khảo |
| `IFC_BuildingEnvExtractor` | LGPL/GPL; 44 sao | IFC | CityJSON (có nội thất) | 1–3 | ? | Thành phần tham khảo |
| `quuppalabs/imdfjson` | Apache-2.0; commit 2026-05-22 ✔F | – | thư viện Java các lớp IMDF | 4 | Java | Tham khảo cấu trúc property IMDF (dự án dùng Python) |
| `davidhend/IMDF-Builder-for-Places` | MIT; commit 2026-10-02 ✔F | **PDF/ảnh** mặt bằng | gói IMDF cho Microsoft Places | 2, 4 | web/Docker | **Tham khảo thuật toán nhận diện phòng/cửa** (Auto-Trace); không nhận DXF/IFC |
| `adap-c6-fingerprint/IMDFrnt` | không khai báo; 2026-11-04 ✔F | IMDF | báo cáo kiểm | kiểm | ? | Có thể dùng để **kiểm IMDF**, chưa đánh giá |
| `S-codex/imdf-conversion-tool`, `bertt/imdf` | MIT; 2022 / 2020 ✔F | GeoJSON / – | IMDF GeoJSON / mô hình .NET | 4 | – | Cũ, nhỏ; tham khảo |
| `area_graph_segment`, `AFPlan`, `CapstoneContour` | chưa rõ / chưa rõ / MIT | DXF / ảnh / GeoJSON | osmAG / phòng / phòng | 2, 3 | – | Nghiên cứu; chỉ tham khảo nhận diện phòng |
| Level Out, ifc2citygml, ifc2geojson, xBIM, Speckle, FreeCAD, Bonsai | AGPL / GPL / MIT / ? / Apache+EE / LGPL / ? | IFC… | CityGML, GeoJSON… | rải rác | – | Tham khảo hoặc ngoài stack (chi tiết trong file C, E) |

### 2b. Thương mại / dịch vụ
| Công cụ | Vào | Ra | Bước | Linux / tự động | Giá công khai? |
|---|---|---|---|---|---|
| **FME Form/Flow** (Safe Software) | DWG/DXF, IFC, GPKG | **IMDF Reader/Writer** (tài liệu FME 2026.3 ✔F), GPKG | 1–5 (ETL) | Windows; Linux một phần (IMDF chưa xác minh); Flow tự động | **Không** — liên hệ báo giá; có "FME Grant" miễn phí cho sinh viên/GV/phi lợi nhuận (theo phiên A, chưa kiểm lại) |
| **Archilogic** | JPG/PNG/PDF/**DWG/DXF** | GeoJSON, IFC, **IMDF**, DXF, SVG, GLTF | 2, 4 | Cloud; API (gói Starter/Pro, theo phiên D) | **Có** ✔F: Starter miễn phí (tối đa 5 floor plan) + $329/floor plan chuyển đổi; Plus $24.90, Professional $59 /floor plan/tháng, gói năm từ 10 floor plan; Enterprise "Custom". **Trang không ghi tiền tệ** (chỉ ký hiệu "$"). IFC chỉ là đầu ra, không nhận làm đầu vào |
| ArcGIS Pro + **Indoors** (Esri) | CAD, Revit, IFC | IMDF **gián tiếp** qua workbench FME Hub + Data Interoperability | 1–4 | Windows; ArcPy | Không — liên hệ Esri |
| Pointr (converter) | DWG/DXF/PDF/GeoJSON | IMDF | 2, 4 | Gửi file, không API công khai | $125/floor plan **chỉ từ nguồn thứ cấp**; chính hãng: liên hệ |
| Mappedin | DWG/DXF/PDF/ảnh | IMDF (enterprise) | 2, 4 | SDK | Không — báo giá |
| MazeMap, Mapsted | ? | ? | – | API | Không — báo giá (MazeMap theo m²) |
| Apple Indoor Maps Program | IMDF | (đích nộp) | – | – | Miễn phí; **không chuyển đổi**, chỉ nhận IMDF có sẵn |
| Spatial Manager (add-in AutoCAD) | DWG | GPKG (hình học/thuộc tính, **không IMDF**) | 1, 5 | Chỉ Windows | Không xác minh ("from") |
| Revit + "BIM 360 Ops" add-in | Revit | IMDF (tài liệu AU 2019) | 4 | Chỉ Windows | Chưa xác minh còn phát hành; giá Autodesk không lấy được (403) |
| Archicad / OpenBuildings Designer / SketchUp | – | IFC | – (nguồn dữ liệu) | Chỉ Windows/macOS | Archicad USD 2.414–5.700/năm; OpenBuildings Designer từ USD 3.844/12 tháng; SketchUp USD 10,75–71,58/tháng (theo phiên B, **chưa kiểm lại**). Đây là phần mềm thiết kế, không thay pipeline |
| Global Mapper, AutoCAD Map 3D | DWG/DXF | GPKG (một phần) | 1, 5 | ? | Global Mapper USD 700–1.750+ **thứ cấp**; Map 3D chưa xác minh |

## 3. Bảng chi phí
**Mã nguồn mở: chi phí bản quyền 0.** Chi phí thật là công sức phát triển phần nhận diện/chuẩn hoá và bảo trì (không có số liệu để ước tính; không bịa). Lưu ý giấy phép: AGPL-3.0 (BIMtoOSM, JOSM IndoorHelper, Level Out) và GPL-3.0 (LibreDWG) có nghĩa vụ chia sẻ mã nguồn nếu nhúng/phân phối; **chỉ tham khảo ý tưởng, không sao chép mã** nếu dự án không muốn chịu nghĩa vụ đó (cần hỏi chủ dự án về mục đích phân phối).

**Thương mại — chỉ những dịch vụ có giá công khai và liên quan trực tiếp tới bước 2/4**:
| Phương án | Giá niêm yết (nguồn) | Chi phí tính ra cho 10 floor plan, 1 năm | Cho 50 floor plan, 1 năm |
|---|---|---|---|
| Archilogic Plus | $24.90/floor plan/tháng, gói năm, tối thiểu 10 floor plan (✔F) | $24.90 × 10 × 12 = **$2.988** | $24.90 × 50 × 12 = **$14.940** |
| Archilogic Professional | $59/floor plan/tháng, gói năm, tối thiểu 10 (✔F) | $59 × 10 × 12 = **$7.080** | $59 × 50 × 12 = **$35.400** |
| Archilogic Starter (trả theo lần) | miễn phí tối đa 5 floor plan; $329/floor plan chuyển đổi (✔F) | $329 × 10 = **$3.290** (chưa rõ 5 floor plan miễn phí có được trừ khỏi phí chuyển đổi không — chưa xác minh) | $329 × 50 = **$16.450** |
| Pointr converter | $125/floor plan (nguồn thứ cấp) | $125 × 10 = $1.250 (chưa xác minh) | $6.250 (chưa xác minh) |
| FME, ArcGIS Indoors, Mappedin, MazeMap, Mapsted | liên hệ báo giá | **không tính được** | **không tính được** |

**Cập nhật 2026-11-06 (TASK-013 phần B): màn hình đặt hàng `app.archilogic.com/order` của chủ dự án hiển thị **"Order total $329.00 USD"** cho việc chuyển đổi 1 file DXF (nút "Process and complete order"; hoàn tiền đầy đủ nếu không hài lòng trong 1 ngày làm việc sau khi giao mô hình). Tiền tệ của khoản phí chuyển đổi $329 vì vậy là **USD (đã xác minh)**; tiền tệ của gói Plus/Professional vẫn chưa ghi trên trang giá. Chưa trả tiền; chưa xác minh được Starter có xuất IMDF.**

Các con số ở cột 3–4 là **phép nhân của phiên F từ giá niêm yết**, chưa gồm thuế/phí khác; tiền tệ trên trang Archilogic **không được ghi** (chỉ ký hiệu "$"); chưa kiểm số "floor plan" có là một tầng hay một bản vẽ. Mẫu của dự án có 2 tầng; số tầng thực tế chưa biết nên bảng dùng 10 và 50 làm kịch bản. Không tính "theo số người dùng" vì các dịch vụ trên tính theo floor plan.

## 4. Khoảng trống (chưa công cụ nào phủ)
| Phần của bài toán | Tình trạng thị trường |
|---|---|
| Nhận diện **phòng/cửa từ DXF/DWG** thuần hình học | Mã nguồn mở: không có giải pháp hoàn chỉnh (chỉ nghiên cứu/ảnh). Thương mại: Archilogic/Pointr/Mappedin làm từ bản vẽ nhưng là dịch vụ kín |
| **Sinh tag OSM Simple Indoor Tagging** từ CAD | Không công cụ nào xác minh được; `BIMtoOSM` (IFC→OSM) là gần nhất nhưng ngừng từ 2024-08 |
| **Ghi GPKG theo IMDF** (mỗi feature type một bảng, feature không geometry thành `attributes`) | Không công cụ nào; công cụ thương mại ra gói IMDF GeoJSON/ZIP |
| **Georeference** từ IFC (`IfcMapConversion`) / control points | Không công cụ chuyển đổi nào xử lý; chỉ có hàm trong IfcOpenShell |
| Kiểm **ràng buộc IMDF** (unit phủ kín level, opening phủ bởi unit…) | Chỉ validator rời (Mappedin web, `IMDFrnt`, validator FME/Apple); chưa đánh giá |
| Chạy **Linux, tự động hoá, tái lặp được** | Chỉ ngăn xếp mã nguồn mở; hầu hết công cụ thương mại chạy Windows |

## 5. Khuyến nghị tự xây / mua / kết hợp
1. **Tự xây lõi bằng mã nguồn mở (khuyến nghị chính).** Các mảnh trưởng thành đã có (GDAL, ezdxf, IfcOpenShell, shapely, geopandas, QGIS); phần còn thiếu (nhận diện, georeference, OSM/IMDF, GPKG theo IMDF, kiểm ràng buộc) chính là giá trị của dự án và **không ai bán sẵn** đúng đầu ra GPKG + OSM SIT. Phù hợp ràng buộc Linux, tự động, tái lặp.
2. **Mua/dùng thương mại chỉ khi có nhu cầu cụ thể về gói IMDF để nộp Apple Indoor Maps hoặc Microsoft Places**: khi đó **Archilogic** (giá công khai, nhận DWG/DXF, xuất IMDF) hoặc **FME** (IMDF Writer, nhưng giá phải báo) là ứng viên; đây là **bước xuất cuối**, không thay thế phần GPKG/OSM của dự án. Cần báo giá FME và kiểm điều khoản Archilogic trước khi cam kết.
3. **Dùng thương mại làm chuẩn đối chiếu** (nếu chủ dự án đồng ý chi một khoản nhỏ hoặc dùng bản dùng thử/Grant): chạy cùng một DXF qua Archilogic/FME rồi so IMDF với kết quả pipeline để phát hiện lỗi mapping. Không bắt buộc.
4. **Rủi ro cần ghi nhận**: (a) khoá nhà cung cấp và quyền dữ liệu của dịch vụ cloud; (b) giấy phép AGPL/GPL nếu dùng lại mã; (c) `BIMtoOSM` và nhiều công cụ cộng đồng ngừng cập nhật; (d) nhiều con số giá chưa xác minh hoặc không có.

## 6. Đối chiếu với thiết kế dự án (TASK-007 / 009 / 010)
- **TASK-007 (mapping)**: không cần đổi phạm vi. Có thể dùng `BIMtoOSM` (đọc, không sao chép mã) làm nguồn tham khảo ánh xạ IFC→SIT, và bảng IMDF đã xác minh trong `research/04`. Nếu sau này có báo giá/dùng thử FME hoặc Archilogic, dùng IMDF họ sinh ra để đối chiếu category.
- **TASK-009 (spec)**: nên **thêm vào phạm vi một mô-đun tuỳ chọn "xuất gói IMDF (manifest.json + *.geojson, ZIP)" từ các bảng GPKG**, vì thị trường chủ yếu tiêu thụ gói IMDF chứ không phải GPKG; GPKG của dự án là dạng lưu trữ/xem trong QGIS. Ghi rõ `venue` + `address` bắt buộc (đã có trong `research/04`).
- **TASK-010 (cài đặt)**: tái sử dụng các thành phần mã nguồn mở đã chọn; tham khảo thuật toán nhận diện phòng/cửa của `IMDF-Builder-for-Places` (MIT, đầu vào là ảnh/PDF nên phải chuyển sang hình học DXF/IFC); cân nhắc `IMDFrnt` làm bộ kiểm IMDF sau khi đọc README. Không tích hợp công cụ thương mại vào pipeline mặc định.
- Task này **chưa thay đổi quyết định** nào; chỉ bổ sung thông tin. Quyết định thêm mô-đun xuất IMDF và có mua/dùng thử thương mại thuộc về chủ dự án.

## 7. Kiểm chéo của phiên F (tự kiểm, 2026-11-06)
| Khẳng định | Kết quả |
|---|---|
| FME có IMDF Reader/Writer | **ĐÚNG** — trang `docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/imdf/imdf.htm` ghi "FME supports both reading from and writing to IMDF" (FME 2026.3) |
| Archilogic giá, định dạng vào/ra, không ghi tiền tệ | **ĐÚNG** — `archilogic.com/pricing`; IFC chỉ là đầu ra, IMDF là đầu ra, DWG chỉ là đầu vào |
| `BIMtoOSM` AGPL-3.0, commit cuối 2024-08-18, 11 sao | **ĐÚNG** (GitHub API) |
| `S-codex/imdf-conversion-tool` (MIT, 2022-07-01), `bertt/imdf` (MIT, 2020-10-23) | **ĐÚNG** (GitHub API) |
| GDAL bản mới nhất 3.13.3 (2026-08-18) | **ĐÚNG** (GitHub API releases/latest) |
| `ogr2ogr` DXF→GPKG: 1 layer `entities`, 51 feature, không tag OSM/IMDF | **ĐÚNG** — phiên F chạy lại độc lập trên `samples/sample-floor-1.dxf` |
| GDAL hệ thống 3.8.4 không có driver DWG/IFC/IMDF | **ĐÚNG** — `ogrinfo --formats` không liệt kê |
| Phiên C: `imdfjson`, `IMDF-Builder-for-Places`, `IMDFrnt` "không tìm thấy" | **SAI** — cả ba tồn tại; đã sửa trong `open-source-tools.md` |
| Script 30 dòng trích 13 phòng từ DXF và 26 IfcSpace/24 IfcDoor từ IFC ra GPKG | **Theo phiên C, chưa tái chạy** (khớp với số liệu đã biết của `samples/`) |
| Giá Archicad, OpenBuildings Designer, SketchUp, Global Mapper, Pointr | **Chưa kiểm lại** (theo phiên A/B/D) |

## Không truy cập được / chưa xác minh (tổng hợp)
- 403: trang sản phẩm `autodesk.com`, bài hướng dẫn `support.safe.com`, trang converter Pointr (cần đăng nhập), một số trang `npm`/`preprints.org`.
- 404/trống: trang giá Global Mapper, BricsCAD, một số đường dẫn `docs.safe.com`, bản mới của trang Esri "Prepare Indoors data for IMDF export".
- Chưa khảo sát: Google, Mapbox; chưa thử chạy: DWG, LibreDWG, JOSM, QGIS GUI.
- Chưa xác minh: giấy phép Bonsai, xBIM, libopencad; Linux của FME IMDF Writer; có hay không công cụ nào xuất OSM SIT chính hãng.

## Nguồn
- Phiên A–E: danh sách nguồn nằm cuối từng file trong thư mục này.
- Kiểm chéo của phiên F: [FME IMDF Reader/Writer](https://docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/imdf/imdf.htm); [Archilogic pricing](https://www.archilogic.com/pricing); GitHub API `rebeccasc/BIMtoOSM`, `quuppalabs/imdfjson`, `davidhend/IMDF-Builder-for-Places`, `adap-c6-fingerprint/IMDFrnt`, `S-codex/imdf-conversion-tool`, `bertt/imdf`, `OSGeo/gdal` (releases/latest); README của `quuppalabs/imdfjson` và `davidhend/IMDF-Builder-for-Places`; chạy `ogr2ogr`/`ogrinfo` trên `samples/` — tất cả 2026-11-06.
