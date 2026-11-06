# Phiên C — Công cụ mã nguồn mở

Ngày truy cập tất cả nguồn: 2026-11-06 (trừ khi ghi khác). Người thực hiện: agent nghiên cứu (TASK-014, Phiên C).

## Câu hỏi nghiên cứu

Có công cụ/thư viện MÃ NGUỒN MỞ nào làm sẵn (một phần hoặc toàn bộ) luồng CAD/BIM (DXF/DWG, IFC) → nhận diện phòng/cửa/tầng → georeference → chuẩn hoá OSM Simple Indoor Tagging / IMDF → ghi GeoPackage → mở trong QGIS không? Mỗi công cụ phủ bước nào, giấy phép, mức độ hoạt động, và thử chạy thực tế trên `samples/sample-floor-1.dxf` và `samples/sample-building.ifc`.

## Kết luận ngắn

1. Không tìm thấy công cụ mã nguồn mở nào làm trọn luồng. Có các "mảnh" trưởng thành cho bước 1 (GDAL/OGR, ezdxf, IfcOpenShell, LibreDWG) và bước 5–6 (GDAL GPKG, QGIS), nhưng bước 2 (CAD→BIM/semantic: nhận diện phòng/cửa), bước 3 (georeference) và bước 4 (sinh tag OSM/IMDF) hầu như phải tự viết.
2. Công cụ gần "bước 4" nhất: `rebeccasc/BIMtoOSM` (IFC → OSM data, Kotlin, AGPL-3.0, tích hợp JOSM IndoorHelper, README ghi "đang viết lại từ đầu", commit cuối 2024-08-18) và `area_graph_segment` (DXF → OSM XML dạng osmAG cho robot, không phải Simple Indoor Tagging chuẩn). Về IMDF chỉ thấy tiện ích nhỏ/ít hoạt động (S-codex/imdf-conversion-tool, bertt/imdf); validator IMDF phổ biến (Mappedin, FME) không rõ mã nguồn mở.
3. Thử chạy xác nhận: `ogr2ogr` DXF→GPKG chạy được ngay (51 feature, 1 layer `entities`, CRS không xác định/placeholder, chỉ có thuộc tính CAD, không có tag OSM/IMDF); GDAL 3.8.4 hệ thống không mở được IFC. Với ezdxf + IfcOpenShell + shapely + geopandas, ~30 dòng Python đã tách được 13 phòng từ DXF và 26 IfcSpace + 24 IfcDoor từ IFC ra GPKG kèm tag `indoor`/`level` thô.
4. Chi phí bản quyền bằng 0; chi phí thật là công sức phát triển phần logic nhận diện/chuẩn hoá và bảo trì.

## Độ tin cậy

- Cao: giấy phép/phiên bản/ngày lấy từ GitHub API, PyPI, LICENSE gốc; kết quả thử chạy tự chạy.
- Trung bình: mô tả tính năng lấy từ README/tài liệu chính thức (đã đọc) hoặc từ kết quả WebSearch (đánh dấu "[thứ cấp]").
- Thấp/chưa xác minh: những mục ghi rõ "chưa xác minh". Các tên `imdfjson`, `IMDF-Builder-for-Places`, `IMDFrnt`: phiên C không tìm thấy, nhưng **phiên F đã kiểm lại bằng GitHub API (2026-11-06) và cả ba đều TỒN TẠI** — xem mục "Hiệu đính của phiên F" ở cuối file.

---

## Công cụ khảo sát

### GDAL/OGR (ogr2ogr, ogrinfo, driver DXF / CAD(DWG) / GPKG)

- **Loại & giấy phép:** thư viện + CLI. Giấy phép "MIT style" theo `LICENSE.TXT` (GitHub API trả `NOASSERTION` vì file gộp nhiều giấy phép thành phần; MIT = kết luận từ văn bản LICENSE.TXT, đã đọc).
- **URL:** https://github.com/OSGeo/gdal ; https://gdal.org/en/stable/drivers/vector/dxf.html ; https://gdal.org/en/stable/drivers/vector/cad.html
- **Bản mới nhất & hoạt động:** release mới nhất v3.13.3 (2026-08-18); commit cuối 2026-11-03 (GitHub API). Máy này có GDAL 3.8.4 (2024-02-08), cũ hơn bản mới nhất.
- **Mô tả (tài liệu chính thức):** DXF driver đọc DXF mọi phiên bản AutoCAD gần đây (từ 3.12 đọc cả Binary DXF), ghi DXF tương thích AutoCAD 2004; không georeferencing. TEXT/MTEXT thành POINT có thuộc tính `Text`; INSERT mặc định bị "inline" (gộp hình học block vào MULTILINESTRING); với `DXF_INLINE_BLOCKS=FALSE` INSERT thành POINT với `BlockName/BlockScale/BlockAngle/BlockAttributes` và có layer `blocks`; HATCH → POLYGON; `DXF_CLOSED_LINE_AS_POLYGON` cho polygon từ polyline kín. Driver CAD (DWG) **chỉ đọc**, dựa libopencad, hỗ trợ POINT/LINE/CIRCLE/ARC/3DFACE (trang không liệt kê phiên bản DWG và không nêu giấy phép libopencad).
- **Đầu vào/đầu ra:** vào DXF, DWG (hạn chế), GeoJSON…; ra GPKG, GeoJSON. Không có driver IFC (đã thử: `ogrinfo` báo "not recognized as a supported file format"). Không sinh IMDF/OSM tag.
- **Phủ bước:** 1 (ingest DXF), một phần 3 (chỉ chuyển CRS nếu đã biết CRS), 5 (ghi GPKG), 6 (QGIS dùng chung GDAL). Không phủ 2, 4.
- **CLI/API & Linux:** `ogr2ogr`, `ogrinfo`, binding Python (`osgeo`), pyogrio; Linux đầy đủ.
- **Chi phí:** 0 bản quyền; chi phí vận hành ≈ công sức viết bước làm sạch/gán thuộc tính.
- **Điểm mạnh/hạn chế:** chạy ngay, ổn định, ghi GPKG chuẩn. Hạn chế: entity CAD thô (không biết đâu là phòng/cửa), block cửa bị inline thành đường, CRS không có; DWG chỉ đọc và chỉ vài loại entity.
- **Đã thử chạy?** Có (xem "Kết quả thử chạy" mục A). Chưa thử DWG vì repo không có mẫu DWG.
- **Nguồn:** các URL trên + `LICENSE.TXT` raw GitHub (2026-11-06).
- **Chưa xác minh:** danh sách phiên bản DWG mà libopencad đọc được; giấy phép libopencad; DXF Binary chỉ có từ GDAL 3.12 (theo tài liệu) nên máy này (3.8.4) không có.

### ezdxf

- **Loại & giấy phép:** thư viện Python; MIT (README + GitHub API).
- **URL:** https://github.com/mozman/ezdxf
- **Bản mới nhất & hoạt động:** 1.4.5 trên PyPI (2026-10-16); commit cuối 2026-11-02. README: yêu cầu Python ≥ 3.11. (Repo không dùng GitHub Releases: API `releases/latest` trả 404.)
- **Mô tả:** đọc/ghi/sửa DXF; có add-on `odafc` làm cầu nối tới ODA File Converter (README).
- **Đầu vào/đầu ra:** DXF (đọc/ghi); DWG chỉ gián tiếp qua ODA File Converter (không mã nguồn mở). Không GPKG/IMDF/OSM.
- **Phủ bước:** 1 và 2 (đọc entity, block INSERT, thuộc tính block, TEXT, tên layer — phù hợp để viết logic nhận diện phòng/cửa theo layer `A-AREA`, `A-DOOR`…).
- **CLI/API & Linux:** API Python (có CLI phụ); Linux OK.
- **Chi phí:** 0; công sức viết logic.
- **Điểm mạnh/hạn chế:** truy cập trực tiếp entity gốc (giữ block DOOR, góc xoay, điểm chèn) — hơn GDAL ở chỗ không mất ngữ nghĩa block. Không có nhận diện ngữ nghĩa sẵn.
- **Đã thử chạy?** Có (mục B): đọc được layer, 13 LWPOLYLINE A-AREA, 13 TEXT, 12 INSERT DOOR kèm điểm chèn/góc xoay.
- **Nguồn:** https://github.com/mozman/ezdxf/blob/master/README.md (raw), https://pypi.org/pypi/ezdxf/json (2026-11-06).
- **Chưa xác minh:** hỗ trợ DXF R12→R2018 chi tiết (không đọc tài liệu phiên bản).

### LibreDWG

- **Loại & giấy phép:** thư viện C + công cụ CLI; GPL-3.0 (GitHub API).
- **URL:** https://github.com/LibreDWG/libredwg
- **Bản mới nhất & hoạt động:** release 0.14 (2026-06-27); commit cuối 2026-11-05.
- **Mô tả (README):** "free C library to read and write DWG files"; decoder đọc được mọi phiên bản DWG, chỉ một số đối tượng R2010+ rất nâng cao bị bỏ qua; writer dùng được trừ R2007.
- **Đầu vào/đầu ra:** DWG ↔ DXF (công cụ `dwg2dxf`; tên CLI lấy theo kiến thức chung, chưa chạy). Trong môi trường này `dwg2dxf` không có sẵn (`which` không tìm thấy).
- **Phủ bước:** 1 (DWG→DXF để đưa vào ezdxf/GDAL).
- **CLI/API & Linux:** có; Linux OK. GPL-3.0 là điểm cần cân nhắc nếu liên kết (link) vào sản phẩm đóng; dùng như tiến trình CLI riêng thường ít ràng buộc hơn (đánh giá pháp lý: chưa xác minh).
- **Chi phí:** 0; cần tự build (chưa thử).
- **Đã thử chạy?** Không: chưa cài (cần biên dịch từ mã nguồn/gói hệ thống, nằm ngoài giới hạn "không cài gói hệ thống") và không có mẫu DWG.
- **Nguồn:** https://github.com/LibreDWG/libredwg (README raw, GitHub API), 2026-11-06.
- **Chưa xác minh:** chất lượng chuyển đổi thực tế trên DWG thương mại; có binary dựng sẵn cho Linux hay không.

### ODA File Converter (đối chứng, KHÔNG mã nguồn mở)

- **Loại & giấy phép:** ứng dụng đóng của Open Design Alliance, miễn phí tải (theo đề bài; điều khoản sử dụng/thương mại hoá chưa xác minh).
- **URL:** https://www.opendesign.com/guestfiles/oda_file_converter (link lấy từ README ezdxf; chưa truy cập trang này).
- **Vai trò:** DWG↔DXF; ezdxf có add-on `odafc` gọi nó; plugin QGIS "Precisa — DWG Batch Converter" cũng nói fallback sang ODA File Converter (mô tả trên plugins.qgis.org).
- **Đã thử chạy?** Không (không mã nguồn mở, không tải).
- **Chưa xác minh:** điều khoản giấy phép, giới hạn phân phối lại, bản Linux.

### IfcOpenShell (thư viện Python/C++) và IfcConvert

- **Loại & giấy phép:** thư viện + CLI; LGPL-3.0 (GitHub API).
- **URL:** https://github.com/IfcOpenShell/IfcOpenShell ; https://docs.ifcopenshell.org/
- **Bản mới nhất & hoạt động:** `ifcopenshell` 0.9.0.post1 trên PyPI (2026-10-15); commit cuối 2026-11-06; có nhiều bản alpha Bonsai hàng ngày (2026-11-05/06). `ifcconvert-0.9.0post1` có binary Linux x64 trên GitHub Releases.
- **Mô tả (chạy thật + `--help`):** IfcConvert xuất .dae, .glb, .igs, .obj, .stp, .svg (mặt bằng 2D), .ttl (WKT), .json, .xml, .ifc. Không có đầu ra GeoJSON/GPKG/IMDF. Thư viện Python có `ifcopenshell.util.element` (psets, container/aggregate), `ifcopenshell.geom` (hình học), `ifcopenshell.util.geolocation` (có hàm `auto_local2global`, `get_crs`, `enh2xyz`… — tên hàm lấy từ `dir()`, chưa đọc tài liệu chi tiết).
- **Đầu vào/đầu ra:** vào IFC2x3/IFC4/IFC4X3; ra như trên. Không GPKG/IMDF/OSM.
- **Phủ bước:** 1 (đọc IFC), 3 (trích hình học/tầng/phòng; georeference qua IfcMapConversion/IfcProjectedCRS và tiện ích geolocation, chưa thử vì mẫu không có), một phần 2 (đã có sẵn ngữ nghĩa IfcSpace/IfcDoor/IfcBuildingStorey — không cần "nhận diện").
- **CLI/API & Linux:** API Python (`pip`), CLI `IfcConvert`; Linux OK.
- **Chi phí:** 0 bản quyền; công sức viết bộ xuất GPKG/IMDF/OSM.
- **Điểm mạnh/hạn chế:** thư viện IFC mã nguồn mở trưởng thành nhất; lấy được tên phòng, tầng, cửa, kích thước cửa. Hạn chế: không có bộ xuất GIS; mẫu IFC không có toạ độ địa lý (`IfcSite.RefLatitude` = None, không có `IfcMapConversion`).
- **Đã thử chạy?** Có (mục B, C): `IfcConvert` ra SVG/GLB/XML/OBJ; Python trích 26 IfcSpace, 24 IfcDoor, 2 tầng, ghi GPKG.
- **Nguồn:** GitHub API, PyPI JSON, `IfcConvert --help` (2026-11-06).
- **Chưa xác minh:** hành vi georeference trên IFC có IfcMapConversion thật; hiệu năng trên mô hình lớn.

### Bonsai (trước đây BlenderBIM)

- **Loại & giấy phép:** add-on Blender trong monorepo IfcOpenShell. Giấy phép riêng của Bonsai: chưa xác minh (repo tổng là LGPL-3.0 theo API).
- **URL:** https://github.com/IfcOpenShell/IfcOpenShell (thư mục bonsai); releases tag `bonsai-0.9.0post1` (2026-10-15) và alpha hằng ngày 0.9.1 (2026-11-05/06) — danh sách release qua GitHub API.
- **Vai trò:** biên tập IFC/BIM trong Blender; có quản lý georeference IFC (nhận định từ kiến thức chung, chưa đọc tài liệu trong phiên này → chưa xác minh).
- **Phủ bước:** 2 (CAD→BIM thủ công/bán tự động nếu người dùng dựng lại mô hình), nhưng cần GUI Blender, không phải pipeline tự động.
- **Đã thử chạy?** Không (cần Blender + GUI).
- **Chưa xác minh:** khả năng nhập DXF làm lớp nền, chạy headless.

### QGIS và plugin liên quan

- **Loại & giấy phép:** ứng dụng GIS desktop; GPL-2.0 (GitHub API).
- **URL:** https://github.com/qgis/QGIS ; kho plugin https://plugins.qgis.org/
- **Bản mới nhất & hoạt động:** tag `final-3_44_15` (2026-09-25); commit cuối 2026-11-06.
- **Mô tả:** mở GPKG và DXF/DWG qua GDAL/OGR. Quét `plugins.xml` (QGIS 3.44, tải 2026-11-06) tìm từ khoá `ifc|indoor|imdf|dxf|dwg|bim`:
  - Không có plugin nhập IFC hay IMDF.
  - Plugin liên quan CAD (chỉ đọc mô tả, chưa kiểm giấy phép/chất lượng): *AnotherDXFImporter* 1.4.6 (2026-06-04, "DXF to Shape/GeoPackage, optional georeferencing"), *CAD To GIS Convert* 1.5.1 (2026-10-11, DXF/DWG→GPKG), *DXF2GIS* 1.0.0 (2026-10-19), *02CadGis* 4.3.0 (2026-11-02), *Precisa DWG Batch Converter* 2.5.
  - Liên quan indoor: *Mappedin MVF Importer* 2.0.3 (2025-09-22; định dạng MVF của Mappedin, không phải IMDF), *Indoor Schematic* 0.2 (2020), *Floor plan filter* 1.1.0 (2026-04-24; chỉ lọc tầng), *Add BIM Data Dictionary Semantics* 1.1 (bSDD), *Speckle* 2.18.0 (2024-03-14).
- **Phủ bước:** 6 (hiển thị, kiểm tra GPKG); một phần 1/5 qua plugin DXF→GPKG.
- **Chi phí:** 0; chi phí = chuẩn hoá style/layer.
- **Đã thử chạy?** Không mở GUI QGIS; chỉ kiểm tra GPKG đầu ra đọc được bằng `ogrinfo` (GDAL, lõi QGIS dùng). Việc mở trong QGIS chưa kiểm trực tiếp.
- **Nguồn:** GitHub API; `https://plugins.qgis.org/plugins/plugins.xml?qgis=3.44` (2026-11-06).
- **Chưa xác minh:** giấy phép từng plugin, chất lượng, phiên bản QGIS 4 hỗ trợ.

### JOSM IndoorHelper (plugin) và công cụ OSM indoor

- **Loại & giấy phép:** plugin Java cho JOSM; AGPL-3.0 (GitHub API).
- **URL:** https://github.com/JOSM/indoorhelper ; https://wiki.openstreetmap.org/wiki/JOSM/Plugins/indoorhelper ; https://josm.openstreetmap.de/wiki/Help/Plugin/IndoorHelper
- **Bản mới nhất & hoạt động:** release v269 (2026-08-12); commit cuối 2026-11-02.
- **Mô tả [thứ cấp qua WebSearch, trích từ wiki OSM/JOSM]:** tạo/kiểm/xem bản đồ indoor theo Simple Indoor Tagging; nút gắn tag, tạo multipolygon đơn giản, validate, tự gắn `level`, hỗ trợ `repeat_on=*` cho thang/ thang máy; preset ví dụ toilet `indoor=room`, `amenity=toilets`, `female=yes`. Tích hợp BIMtoOSM để nhập BIM (README BIMtoOSM đã đọc xác nhận: nhập qua JOSM IndoorHelper).
- **Phủ bước:** 4 (biên tập & kiểm tag OSM indoor, thủ công); 2/3 một phần qua BIMtoOSM.
- **Đầu vào/đầu ra:** IFC (qua BIMtoOSM) → dữ liệu OSM (.osm). Không GPKG trực tiếp.
- **CLI/API & Linux:** GUI JOSM (Java), không phải CLI hàng loạt; Linux OK.
- **Đã thử chạy?** Không (GUI; chưa cài JOSM).
- **Chưa xác minh:** nội dung wiki OSM trực tiếp (WebFetch/curl tới wiki.openstreetmap.org: WebFetch lỗi, curl trả mã 000); tài liệu JOSM chi tiết.

### BIMtoOSM (rebeccasc)

- **Loại & giấy phép:** thư viện/parser Kotlin (Gradle); AGPL-3.0 (GitHub API + badge README).
- **URL:** https://github.com/rebeccasc/BIMtoOSM ; wiki https://rebeccasc.github.io/BIMtoOSM/
- **Bản mới nhất & hoạt động:** không có release (API 404); commit cuối 2024-08-18; 11 sao. README ghi "Currently, the source code is being rebuilt from scratch and the API might change".
- **Mô tả (README đã đọc):** parser chuyển BIM → dữ liệu OpenStreetMap; ví dụ `BIMtoOSMParser(config).parse("path.ifc")` rồi `Exporter.exportOSM(...)`. Phụ thuộc `opensourceBIM/IfcPlugins` (AGPL-3.0, Java) và JTS.
- **Phủ bước:** 3–4 (IFC → OSM indoor); đây là ứng viên gần nhất với đề bài về phía OSM.
- **Hạn chế:** không có GPKG/IMDF; Java/Kotlin (khác stack Python hiện có); dự án nhỏ, ngừng cập nhật ≈ 2,2 năm; ánh xạ tag chi tiết (indoor=*, door=*) chưa kiểm.
- **Đã thử chạy?** Không (không có release dựng sẵn; cần Gradle/JDK, ngoài phạm vi cài đặt).
- **Chưa xác minh:** danh sách tag đầu ra, mức độ làm việc với IFC4, tình trạng bản "rebuilt".

### area_graph_segment (JohnnyLin7)

- **Loại & giấy phép:** Python; giấy phép không ghi (GitHub API `license: null`) → chưa xác minh.
- **URL:** https://github.com/JohnnyLin7/area_graph_segment (API báo "Moved Permanently" tới repo id 892503851; commit cuối 2026-07-14, 21 sao qua API lần theo redirect).
- **Mô tả [thứ cấp, WebSearch tóm tắt README/bài arXiv 2507.00552]:** CAD floor plan → OSM XML dạng osmAG (phòng + topology lối đi) cho điều hướng robot; chuỗi DXF → SVG → PNG → area-graph segmentation → osmAG; DWG cần ODA File Converter.
- **Phủ bước:** 2/3 (suy ra phòng bằng phân đoạn ảnh), 4 một phần (osmAG ≠ Simple Indoor Tagging).
- **Đã thử chạy?** Không.
- **Chưa xác minh:** giấy phép, định dạng tag đầu ra.

### ifc2indoorgml (UNSW GRID Lab)

- **Loại & giấy phép:** C++ (dựa IFC++); Apache-2.0 (GitHub API).
- **URL:** https://github.com/grid-unsw/ifc2indoorgml ; bài báo https://ual.sg/publication/2022-isprs-ifc-2-indoorgml/
- **Hoạt động:** commit cuối 2022-10-05, 12 sao (GitHub API); README chỉ trỏ tới Installation Guide PDF.
- **Mô tả [thứ cấp qua WebSearch]:** sinh IndoorGML từ IFC kiến trúc.
- **Phủ bước:** 3–4 theo hướng IndoorGML (không phải OSM/IMDF). Tham khảo hơn là dùng.
- **Đã thử chạy?** Không (C++, không có binary; ngừng cập nhật).

### IMDF: công cụ cộng đồng tìm được

Kiểm tra qua GitHub API và README:

| Repo | Giấy phép | Commit cuối | Mô tả |
|---|---|---|---|
| https://github.com/S-codex/imdf-conversion-tool | MIT | 2022-07-01 | Python ≥3.7; `python imdf_tool.py <input geojson dir> <output dir>`; "Convert Geojson data to conform Apple's IMDF format"; README nêu hạn chế: toạ độ `venue` phải là danh sách lồng 3 cấp |
| https://github.com/bertt/imdf | MIT | 2020-10-23 | Thư viện .NET Standard 2.1 [thứ cấp qua WebSearch]; phạm vi hiện thực: chỉ feature type Venue |
| https://github.com/IBM/Apple-Indoor-Maps | không ghi | 2022-02-25 (archived) | chưa đọc README → chưa xác minh nội dung |
| https://github.com/indoorequal/indoorequal.org | AGPL-3.0 | 2026-11-05 | "web based indoor viewer that display vector tiles as well as GeoJSON, OSM and IMDF files" (mô tả GitHub); chỉ xem |
| luminouxx/IMDFlex | — | — | API GitHub trả 404 cho đường dẫn này; WebSearch nói là ứng dụng iOS tạo IMDF; không xác minh được |

Validator: *Mappedin IMDF Validator* (https://developer.mappedin.com/docs/tools/imdf-validator) — chạy trong trình duyệt, kiểm schema + business rules, chế độ Strict/Loose, "all processing occurs in the browser"; trang KHÔNG nói mã nguồn mở hay giấy phép. *Safe/FME IMDFValidator* là sản phẩm FME (thương mại, ngoài phạm vi). Apple có IMDF Sandbox/Register (https://register.apple.com/resources/imdf/) — không phải mã nguồn mở. Đặc tả IMDF OGC: https://docs.ogc.org/cs/20-094/ — [thứ cấp] address.geojson và venue.geojson là bắt buộc.
Không có gói PyPI tên `imdf`, `pyimdf`, `imdf-validator`, `imdfjson` (PyPI JSON trả không tồn tại, 2026-11-06).

- **Phủ bước:** 4 (đóng gói IMDF) — chỉ ở mức tiện ích nhỏ; không có công cụ sinh đủ 16 feature type từ CAD/BIM.
- **Đã thử chạy?** Không (S-codex tool cần GeoJSON đầu vào đúng cấu trúc; chưa có GeoJSON IMDF-ready; ưu tiên thời gian cho GDAL/IfcOpenShell).

### xBIM (Xbim Essentials)

- **Loại & giấy phép:** thư viện .NET đọc/ghi IFC. GitHub API trả `NOASSERTION`, không tìm thấy `LICENSE.md` (404) → giấy phép chưa xác minh.
- **URL:** https://github.com/xBimTeam/XbimEssentials
- **Bản mới nhất & hoạt động:** release 6.0.517 (2025-04-18); commit cuối 2026-08-28.
- **Phủ bước:** 1–3 (đọc IFC trong hệ .NET). Không có đầu ra GIS. So với IfcOpenShell, ít liên quan nếu stack là Python.
- **Đã thử chạy?** Không (.NET, ngoài stack).
- **Chưa xác minh:** giấy phép, hỗ trợ IFC4X3, chạy Linux.

### Speckle

- **Loại & giấy phép:** nền tảng trao đổi dữ liệu AEC. `speckle-server`: Apache-2.0 trừ thư mục `workspaces` và `gatekeeper` thuộc "Speckle Enterprise Edition license" (LICENSE gốc đã đọc). `specklepy`: Apache-2.0 (GitHub API).
- **URL:** https://github.com/specklesystems/speckle-server ; https://github.com/specklesystems/specklepy
- **Bản mới nhất & hoạt động:** server 2.31.14 (2026-06-15), commit 2026-11-06; specklepy 2026.9.1 (2026-10-21).
- **Vai trò:** kênh nhận dữ liệu từ Revit/Rhino/…, có connector QGIS (plugin "Speckle" 2.18.0 trên kho plugin QGIS, cập nhật cuối 2024-03-14). Không phải bộ chuyển CAD→OSM/IMDF. Mô tả server tự-host và chi phí hosting: chưa xác minh.
- **Đã thử chạy?** Không (cần server/tài khoản; không liên quan trực tiếp luồng file → GPKG).

### FreeCAD

- **Loại & giấy phép:** ứng dụng CAD/BIM; LGPL-2.1 (GitHub API).
- **URL:** https://github.com/FreeCAD/FreeCAD
- **Bản mới nhất & hoạt động:** 1.1.4 (2026-09-28); commit cuối 2026-11-05.
- **Vai trò:** có workbench BIM/Arch (kiến thức chung, chưa kiểm trong phiên này); tiềm năng nhập DXF/IFC và xuất, nhưng không phải pipeline headless sẵn cho GIS. Mức "thành phần/thủ công".
- **Đã thử chạy?** Không (nặng, GUI).
- **Chưa xác minh:** khả năng nhập/xuất cụ thể, chạy headless.

### Thư viện hỗ trợ đã dùng khi thử: shapely, geopandas, pyogrio

Chỉ là thành phần Python (phiên bản trong `.venv` của repo, in ra bằng lệnh kiểm: ezdxf 1.4.5, ifcopenshell 0.9.0.post1, shapely 2.2.0, geopandas 1.2.0, pyogrio 0.13.0). Dùng cho hình học (polygonize/contains), ghi GPKG. Giấy phép không kiểm trong phiên này (chưa xác minh).
`chrieke/geojson-validator` (MIT, commit cuối 2026-08-02): validator GeoJSON chung, không phải IMDF.

---

## Bảng tóm tắt (công cụ × tiêu chí)

| Công cụ | Giấy phép | Hoạt động (commit cuối / bản) | Vào | Ra | Bước | Dùng ngay? |
|---|---|---|---|---|---|---|
| GDAL/OGR | MIT-style | 2026-11-03 / 3.13.3 | DXF, DWG(hạn chế) | GPKG, GeoJSON | 1,5,(3),6 | Thành phần; DXF→GPKG thô chạy ngay |
| ezdxf | MIT | 2026-11-02 / 1.4.5 | DXF | DXF | 1,2 | Thành phần (cần logic) |
| LibreDWG | GPL-3.0 | 2026-11-05 / 0.14 | DWG | DXF | 1 | Thành phần (chưa thử) |
| ODA File Converter | đóng | — | DWG | DXF | 1 | Không mã nguồn mở |
| IfcOpenShell/IfcConvert | LGPL-3.0 | 2026-11-06 / 0.9.0.post1 | IFC | SVG, OBJ, GLB, XML… | 1,2,3 | Thành phần mạnh |
| Bonsai | chưa xác minh | 2026-11-06 (alpha) | IFC | IFC | 2 | GUI, thủ công |
| QGIS | GPL-2.0 | 2026-11-06 / 3.44.15 | GPKG, DXF… | — | 6 | Dùng ngay để xem |
| QGIS plugin DXF→GPKG | chưa kiểm | 2026 | DXF/DWG | GPKG | 1,5 | Thành phần, chưa đánh giá |
| JOSM IndoorHelper | AGPL-3.0 | 2026-11-02 / v269 | .osm, IFC (BIMtoOSM) | .osm | 4 | GUI thủ công |
| BIMtoOSM | AGPL-3.0 | 2024-08-18 / không release | IFC | .osm | 3,4 | Gần nhất nhưng ngừng cập nhật |
| area_graph_segment | chưa rõ | 2026-07-14 | DXF | osmAG (.osm) | 2,3 | Nghiên cứu, không chuẩn SIT |
| ifc2indoorgml | Apache-2.0 | 2022-10-05 | IFC | IndoorGML | 3,4* | Không đúng định dạng đích |
| S-codex imdf tool | MIT | 2022-07-01 | GeoJSON | IMDF GeoJSON | 4 | Nhỏ, hạn chế |
| bertt/imdf | MIT | 2020-10-23 | — | .NET models | 4 | Cũ, chỉ Venue [thứ cấp] |
| Mappedin validator | không rõ | — | IMDF zip | báo cáo | 4 (kiểm) | Web, không rõ nguồn mở |
| xBIM | chưa xác minh | 2026-08-28 / 6.0.517 | IFC | — | 1 | .NET, ngoài stack |
| Speckle | Apache-2.0 (+EE) | 2026-11-06 | nhiều | nhiều | trao đổi | Không phải bộ chuyển |
| FreeCAD | LGPL-2.1 | 2026-11-05 / 1.1.4 | DXF/IFC (chưa kiểm) | — | 2 | GUI |

---

## Kết quả thử chạy

Môi trường: GDAL 3.8.4 hệ thống; `.venv` của repo (ezdxf 1.4.5, ifcopenshell 0.9.0.post1, shapely 2.2.0, geopandas 1.2.0, pyogrio 0.13.0 — chỉ chạy, không cài thêm vào); IfcConvert 0.9.0post1 tải từ GitHub Releases vào thư mục tạm. Mẫu chỉ được đọc. Đầu ra tại `/tmp/claude-1001/-home-hieuht50/01890cce-facc-4d1f-8ee7-2350ff23b1fc/scratchpad/c_tools/`. Script thử: `.../c_tools/t.py`.

**A. GDAL — DXF → GPKG**

```
ogrinfo -so -al samples/sample-floor-1.dxf
ogr2ogr -f GPKG c_tools/floor1.gpkg samples/sample-floor-1.dxf
ogrinfo -so c_tools/floor1.gpkg ; ogrinfo -dialect sqlite -sql "select Layer, SubClasses, ST_GeometryType(geom), count(*) ... group by ..." floor1.gpkg
```
- Driver DXF; một layer duy nhất `entities`, 51 feature, extent (0,0)–(24,12), geometry "Unknown (any)".
- Trường: Layer, PaperSpace, SubClasses, Linetype, EntityHandle, Text (không có tag OSM/IMDF, không có level).
- Phân bố: A-AREA LWPOLYLINE→LINESTRING 13 (chưa thành polygon); A-AREA-IDEN TEXT→POINT Z 13 (Text P101…); A-DOOR INSERT→MULTILINESTRING 12 (block cửa bị inline, mất tên block/góc); A-WALL LINE 12 + LWPOLYLINE 1.
- CRS: DXF không CRS; GPKG ghi "Undefined geographic SRS" (placeholder, không đúng ý nghĩa), toạ độ là mét cục bộ (0–24) → cần georeference riêng.
- `ogrinfo` trên `sample-building.ifc`: `ERROR 4: ... not recognized as a supported file format` (GDAL không có driver IFC). Driver DWG ("CAD", read-only) có trong danh sách format; chưa thử vì không có mẫu DWG.

**B. ezdxf + shapely + geopandas (DXF → phòng) và IfcOpenShell (IFC → phòng/cửa)**

Chạy: `.venv/bin/python -I c_tools/t.py c_tools`.
- DXF: layers `0, Defpoints, A-WALL, A-DOOR, A-AREA, A-AREA-IDEN`; `$INSUNITS`=6 (mét); blocks `DOOR` (INSERT tại (2,5) góc 0, (2,7) góc 180, không có attribute); ghép 13 LWPOLYLINE A-AREA với TEXT bên trong → 13 phòng, tổng diện tích 288 m², cả 13 có tên. Ghi `rooms_dxf.gpkg` (layer `rooms`, 13 feature, cột `name`, `indoor=room`, `level=1`, `ref`); CRS: không có (pyogrio cảnh báo "crs was not provided"; GPKG ghi "Undefined SRS" ENGCRS).
- IFC: IFC4; 26 IfcSpace, 24 IfcDoor (ví dụ "Cua P101", OverallWidth 0.9), 8 IfcWall, 2 IfcBuildingStorey ("Tầng 1" z=0, "Tầng 2" z=3.0), 1 IfcSite, 1 IfcBuilding. Tên phòng P101…, 2 hành lang (HL100, HL200, LongName "Hanh lang"). Lưu ý kỹ thuật: cần `use-world-coords=True` để có toạ độ thế giới (lần chạy đầu không bật nên mọi phòng trùng nhau tại gốc), và tầng của IfcSpace lấy qua `get_aggregate` (không phải `get_container`). Kết quả: footprint bằng convex hull của đỉnh mesh → ghi `spaces_ifc.gpkg` (layer `spaces`, 26 feature: 13/tầng; `indoor=room` 24, `indoor=corridor` 2 theo LongName). Mẫu IFC không có `IfcSite.RefLatitude/RefLongitude` và không có `IfcMapConversion` → không có georeference; CRS GPKG không xác định.
- Hạn chế quan sát: footprint dùng convex hull (đủ cho phòng chữ nhật, sai với phòng hình chữ L); cửa chưa chuyển thành điểm `indoor=door`; chưa có `stairs`/`elevator` (mẫu không có); chưa xuất thuộc tính `door=*`.

**C. IfcConvert 0.9.0post1 (binary Linux)**

```
IfcConvert samples/sample-building.ifc c_tools/ifcc/out.svg ; ... out.glb ; ... out.xml ; ... out.obj
```
Cả bốn lệnh thành công (26 đối tượng hình học; out.svg 7.928 byte mặt bằng 2D, out.xml 19.027 byte, out.glb 13.044 byte; OBJ có 8 nhóm `o/g`). Không có định dạng GIS (GeoJSON/GPKG).

**Không thử được:** DWG (không có mẫu; LibreDWG chưa cài), JOSM/IndoorHelper/BIMtoOSM (GUI/JDK), QGIS GUI (chỉ xác nhận GPKG đọc được bằng GDAL), S-codex imdf tool, Bonsai, FreeCAD, Speckle, xBIM.

**Kết luận từ thử chạy:** không công cụ nào trực tiếp sinh được tag OSM Simple Indoor Tagging hay IMDF; phần "indoor=room/corridor", "level" ở trên là script ad-hoc của phiên này (chưa kiểm chuẩn tag, chưa có door=*/repeat_on).

---

## Khoảng trống: phần nào KHÔNG công cụ mã nguồn mở nào làm sẵn

1. **CAD→BIM/semantic (bước 2):** nhận diện phòng/cửa/cầu thang từ DXF/DWG (theo layer, block, text; đóng polygon phòng từ tường nếu không có polyline kín) — chỉ có nghiên cứu (`area_graph_segment`, thứ cấp) và không có công cụ sản xuất. Phải tự viết (ezdxf + shapely).
2. **Georeference (bước 3):** không công cụ tự động đặt DXF/IFC cục bộ lên toạ độ thật; cần điểm neo/CRS do người dùng cung cấp. IfcOpenShell chỉ có tiện ích biến đổi khi IFC đã có IfcMapConversion.
3. **Chuẩn hoá OSM Simple Indoor Tagging (bước 4):** chỉ BIMtoOSM (IFC→OSM, ngừng cập nhật, README nói đang viết lại) và JOSM IndoorHelper (thủ công); không có bộ chuyển DXF→SIT, và không ghi GPKG.
4. **Đóng gói/kiểm IMDF (bước 4):** không có thư viện IMDF trưởng thành mã nguồn mở được xác minh (chỉ S-codex 2022, bertt 2020); validator đã biết (Mappedin, FME, Apple Sandbox) không được xác nhận là mã nguồn mở. Bắt buộc address/venue, manifest và 16 feature type phải tự hiện thực (có thể dùng JSON Schema nếu lấy được từ đặc tả — chưa xác minh).
5. **Đầu-cuối:** không có pipeline file → GPKG → QGIS trọn gói. GPKG ghi và mở QGIS thì có sẵn.

## Nguồn

(Tất cả truy cập 2026-11-06.)
- GitHub API: `https://api.github.com/repos/<owner>/<repo>` và `/releases/latest` cho OSGeo/gdal, qgis/QGIS, mozman/ezdxf, LibreDWG/libredwg, IfcOpenShell/IfcOpenShell, JOSM/indoorhelper, rebeccasc/BIMtoOSM, xBimTeam/XbimEssentials, specklesystems/speckle-server, specklesystems/specklepy, FreeCAD/FreeCAD, grid-unsw/ifc2indoorgml, JohnnyLin7/area_graph_segment, S-codex/imdf-conversion-tool, bertt/imdf, IBM/Apple-Indoor-Maps, indoorequal/indoorequal.org, chrieke/geojson-validator, opensourceBIM/IfcPlugins.
- https://raw.githubusercontent.com/OSGeo/gdal/master/LICENSE.TXT ; https://raw.githubusercontent.com/specklesystems/speckle-server/main/LICENSE ; https://raw.githubusercontent.com/mozman/ezdxf/master/README.md ; https://raw.githubusercontent.com/LibreDWG/libredwg/master/README ; https://raw.githubusercontent.com/rebeccasc/BIMtoOSM/master/README.md ; https://raw.githubusercontent.com/S-codex/imdf-conversion-tool/main/README.md
- https://gdal.org/en/stable/drivers/vector/dxf.html ; https://gdal.org/en/stable/drivers/vector/cad.html
- https://pypi.org/pypi/ezdxf/json ; https://pypi.org/pypi/ifcopenshell/json ; GitHub Releases `ifcconvert-0.9.0post1`
- https://plugins.qgis.org/plugins/plugins.xml?qgis=3.44
- https://developer.mappedin.com/docs/tools/imdf-validator
- [thứ cấp, WebSearch] https://wiki.openstreetmap.org/wiki/JOSM/Plugins/indoorhelper ; https://josm.openstreetmap.de/wiki/Help/Plugin/IndoorHelper ; https://ual.sg/publication/2022-isprs-ifc-2-indoorgml/ ; https://register.apple.com/resources/imdf/reference/type_designators ; https://docs.ogc.org/cs/20-094/ ; https://support.safe.com/hc/en-us/articles/25407401856653 ; https://arxiv.org/pdf/2507.00552v3 ; https://github.com/bertt/imdf
- Thử chạy cục bộ: lệnh và đầu ra ghi ở mục trên.

## Không truy cập được / chưa xác minh

- https://wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging và `.../JOSM/Plugins/indoorhelper`: WebFetch lỗi, `curl` trả mã 000 (không phải 403/429); nội dung IndoorHelper/SIT chỉ có qua WebSearch (thứ cấp).
- https://docs.ifcopenshell.org/ifcconvert/usage.html: WebFetch trả nội dung bị cắt (chỉ menu); thay bằng `IfcConvert --help` chạy thật.
- ~~Không tìm thấy `imdfjson`, `IMDF-Builder-for-Places`, `IMDFrnt`~~ — **SAI, đã hiệu đính** (xem cuối file). Vẫn không xác minh được: `luminouxx/IMDFlex` (API 404, WebSearch nói là app iOS).
- Giấy phép chưa xác minh: Bonsai, xBIM, libopencad, area_graph_segment, IBM/Apple-Indoor-Maps, các plugin QGIS, shapely/geopandas/pyogrio; validator Mappedin không nêu mã nguồn mở.
- ODA File Converter, Esri ArcGIS Indoors, FME: ngoài phạm vi mã nguồn mở, chỉ nhắc để đối chiếu.
- DWG thực tế: chưa thử với LibreDWG/GDAL CAD vì thiếu mẫu và quyền cài.
- Mở thực tế trong QGIS GUI: chưa làm.

## Hiệu đính của phiên F (2026-11-06)
Phiên C kết luận ba kho dưới đây "không tìm thấy". Kiểm lại bằng `https://api.github.com/repos/<owner>/<repo>` và README gốc: **cả ba tồn tại**. Đây là sai sót của phiên C (không phải của nguồn).

| Kho | Giấy phép | Commit gần nhất | Sao | Nội dung (theo README) | Dùng lại cho dự án |
|---|---|---|---|---|---|
| `quuppalabs/imdfjson` | Apache-2.0 | 2026-05-22 | 1 | Thư viện Java (Jackson) với các lớp IMDF theo spec; README dẫn Maven Central (`com.quuppa.imdf:imdfjson`, ví dụ bản 1.0.2) | Thành phần cho bước 4 nếu dùng Java; dự án dùng Python nên chỉ để tham khảo cấu trúc property |
| `davidhend/IMDF-Builder-for-Places` | MIT | 2026-10-02 | 0 | Ứng dụng web (Docker) tạo IMDF cho Microsoft Places: **tải PDF/ảnh mặt bằng**, đặt phần tử bằng giao diện, có "Auto-Trace Rooms" (nhận diện tường, phòng, cửa bằng cung mở cửa, hành lang `walkway`); fork của `loryanstrant/IMDF-Builder-for-Places`, xuất gói tương thích Places | Tham khảo thuật toán nhận diện phòng/cửa; **đầu vào là PDF/ảnh, không phải DXF/IFC**, xuất để import Microsoft Places |
| `adap-c6-fingerprint/IMDFrnt` | không khai báo | 2026-11-04 | 1 | Validator/công cụ IMDF (chưa đọc README trong phiên F) | Chưa đánh giá |

Các số liệu giấy phép, ngày commit, số sao ở bảng trên lấy từ GitHub API ngày 2026-11-06; nội dung cột "Nội dung" của hai kho đầu lấy từ README. Kho thứ ba chưa đọc README.
