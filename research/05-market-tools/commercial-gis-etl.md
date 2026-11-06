# Phiên A — Nền tảng ETL/GIS thương mại

Ngày truy cập tất cả nguồn: 2026-11-06 (trừ khi ghi khác). Công cụ tìm kiếm/đọc web trả về bản tóm tắt do mô hình nhỏ sinh ra từ trang; các trích dẫn dưới đây là diễn giải từ tóm tắt đó, KHÔNG phải đọc nguyên văn từng trang (xem mục "chưa xác minh").

## Câu hỏi nghiên cứu
Có nền tảng ETL/GIS sẵn trên thị trường đọc được CAD/BIM (DXF, DWG, IFC) và xuất ra IMDF / GeoPackage / OSM indoor tags không? Chi phí? Hỗ trợ CLI/API/Linux?

## Kết luận ngắn
- FME (Safe Software) là ứng viên duy nhất xác minh được có **IMDF Writer chính hãng** (cộng DWG/DXF, IFC, GeoPackage reader/writer; chạy Linux cho ACAD/IFC/GPKG). Giá FME: **không niêm yết, phải liên hệ báo giá**.
- ArcGIS Pro + ArcGIS Indoors nhập CAD (.dwg/.dgn), Revit, IFC vào Indoors database; xuất IMDF **gián tiếp** qua workbench FME Hub, cần extension Data Interoperability. Giá: **không niêm yết trên trang đã đọc**, liên hệ Esri sales.
- Pointr (dịch vụ chuyển DWG/DXF → IMDF) là dịch vụ gửi file, không có giá/API công khai. Không công cụ nào xác minh được xuất OSM Simple Indoor Tagging.

## Độ tin cậy
Trung bình. Tính năng FME/Esri lấy từ trang chính hãng (qua WebFetch/WebSearch) nên khá tin cậy; giá hầu hết không công khai. Một số trang trả 404/403.

## Nhóm miễn phí / mã nguồn mở (tham chiếu, không phải trọng tâm Phiên A)

### GDAL/OGR (driver DXF)
- Nhà cung cấp & loại: dự án mã nguồn mở (OSGeo). Giấy phép: trang driver không nêu (chưa xác minh trên trang này).
- URL: https://gdal.org/en/stable/drivers/vector/dxf.html
- Mô tả: driver DXF đọc ASCII DXF mọi phiên bản AutoCAD gần đây (từ GDAL 3.12 đọc cả binary DXF); ghi DXF định dạng AutoCAD 2004. DXF coi như không có georeference qua OGR; entity 3D solid bị bỏ qua mặc định; chỉ ghi được một layer.
- I/O: DXF đọc/ghi. DWG: trang này không nói (chưa xác minh, có trang driver "AutoCAD DWG" riêng chưa đọc). IFC/IMDF/OSM tags: chưa xác minh trong phiên này.
- Pipeline: một phần bước 1, 3 (đọc hình học), 5 (ghi GPKG qua driver GPKG — chưa xác minh trong phiên này).
- CLI/Linux: có CLI (ogr2ogr) — chưa xác minh trong phiên này; chạy Linux là thực tế phổ biến nhưng chưa kiểm trên trang.
- Giá: miễn phí (không có giá). Nguồn: URL trên, 2026-11-06.
- Hạn chế: không nhận diện phòng/cửa, không IMDF.

## Nhóm thương mại

### FME (Safe Software) — FME Form / FME Flow
- Nhà cung cấp & loại: Safe Software; nền tảng ETL/tích hợp dữ liệu không gian thương mại. Sản phẩm trên trang giá: FME Form, FME Flow, FME Flow Hosted, FME Realize.
- URL chính thức: https://fme.safe.com/pricing/ ; https://docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/imdf/imdf.htm
- Mô tả: FME hỗ trợ đọc và ghi IMDF. Dataset IMDF là thư mục GeoJSON, mỗi feature type một file; writer tự tạo manifest.json, reproject mọi geometry sang WGS84, tham số coordinate precision 1–15 (docs.safe.com, trang IMDF Reader/Writer và Writer Parameters). Safe có bài hướng dẫn chuyển ArcGIS Indoors → IMDF bằng FME Form (support.safe.com bài 25407628986381 — truy cập bị 403, chỉ thấy qua tóm tắt tìm kiếm) và bản thông báo "Safe Software's FME supports IMDF" (https://www.safe.com/company-updates/safe-softwares-fme-supports-imdf, chỉ thấy qua kết quả tìm kiếm).
- I/O:
  - DXF/DWG: đọc/ghi, "up to and including 2022"; format ACAD dùng Autodesk RealDWG; bảng nền tảng của trang ACAD ghi Reader/Writer = có trên FME Form/Flow/Flow Hosted (cột Linux), còn bảng RealDWG riêng ghi Linux không hỗ trợ (cách ghép cột do công cụ trích xuất, nên xác nhận lại trên trang gốc). Nguồn: https://docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/acad/acad.htm
  - IFC: trang IFC cũ (deprecated từ FME 2025.0, "replaced by the IFC Reader/Writer" mới) nêu đọc IFC2x/2x2/2x3/4, ghi IFC2x3 hoặc IFC4, có trên Windows/Linux/Mac. Nguồn: https://docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/ifc/ifc.htm . Chưa đọc trang format IFC mới.
  - IMDF: đọc + ghi (FME Form, FME Flow; không có trên FME Flow Hosted). Bảng hệ điều hành của trang IMDF khó đọc; tìm kiếm cho thấy writer trên Windows 64-bit — chưa xác minh Linux.
  - GPKG: OGC GeoPackage Reader/Writer, đọc/ghi, Windows/Linux/Mac. Nguồn: https://docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/ogcgeopackage/ogcgeopackage.htm (chỉ thấy qua kết quả tìm kiếm).
  - OSM indoor tags: chưa xác minh (FME có OSM reader nhưng không kiểm trong phiên này; không có transformer sẵn đã xác minh để gắn Simple Indoor Tagging).
- Phủ pipeline: 1 ingest (có), 2 CAD→BIM (không — không có bước tự nhận diện phòng/cửa tự động; phải tự dựng workspace với transformer), 3 extract+georeference (có, thủ công qua workspace/transformer), 4 chuẩn hoá IMDF (writer có, quy tắc phải tự lập; có transformer IMDFValidator trên FME Hub), 5 ghi GPKG (có), 6 QGIS (gián tiếp, qua file GPKG).
- CLI/API & Linux: FME Flow có tự động hoá server (lịch, webhook, REST) — chi tiết CLI/REST chưa đọc trang chính hãng trong phiên này (chưa xác minh). Reader/Writer ACAD, IFC, GPKG có trên Linux; IMDF Linux chưa xác minh.
- Giá & giấy phép: KHÔNG niêm yết. Trang giá ghi giá phụ thuộc quy mô tổ chức, mô hình triển khai (on-premises, cloud, hybrid) và mức sử dụng (engine capacity); đăng ký theo năm; năm đầu gồm Annual Maintenance, gia hạn hằng năm; liên hệ sales/biểu mẫu báo giá. Tiền tệ: không nêu. Dùng thử: trang giá không đề cập (chưa xác minh trang riêng). Chương trình FME Grant: sinh viên giấy phép FME Form miễn phí 4 tháng; giáo viên được cấp miễn phí FME Form hoặc Flow; tổ chức phi lợi nhuận/từ thiện miễn phí theo xét duyệt. Nguồn: https://fme.safe.com/pricing/ , 2026-11-06. Yêu cầu loại giấy phép của IMDF writer: tài liệu cũ ghi cần Professional Edition trở lên, tài liệu mới ghi "FME Desktop License" (nguồn thứ cấp qua tóm tắt tìm kiếm; mâu thuẫn, chưa xác minh).
- Điểm mạnh: công cụ duy nhất xác minh được có IMDF writer chính hãng + GPKG + DWG/IFC; hạ tầng ETL tự động hoá được; có validator.
- Hạn chế: không tự phát hiện phòng/cửa từ CAD; giá không công khai; DXF/DWG dùng RealDWG (hạn chế Linux/ghi); chi phí giấy phép có thể lớn so với tự xây bằng thư viện mở.
- Nguồn: các URL trên, 2026-11-06.
- Chưa xác minh: giá cụ thể; IMDF trên Linux; CLI/REST của FME Flow; OSM tags; trang IFC mới; trang docs.safe.com đường dẫn "FME-Readers-Writers" trả 404 (dùng đường dẫn "FME-ReadersWriters").

### ArcGIS Pro + ArcGIS Indoors (Esri)
- Nhà cung cấp & loại: Esri; GIS desktop/SaaS thương mại; Indoors là bộ sản phẩm trên ArcGIS Pro/Enterprise/Online.
- URL chính thức: https://doc.esri.com/en/arcgis-pro/latest/help/data/indoors/get-started-with-arcgis-indoors.html ; https://doc.esri.com/en/arcgis-pro/latest/help/data/indoors/choose-a-licensing-configuration.html ; https://doc.esri.com/en/arcgis-pro/latest/help/data/indoors/create-the-indoors-geodatabase.html
- Mô tả: Create Indoors Database tạo workspace theo ArcGIS Indoors Information Model (site, facility, level, unit, details...) trong file geodatabase hoặc enterprise geodatabase branch-versioned. Trong toolbox Indoors có Import CAD To Indoor Dataset (.dwg, .dgn), Import BIM To Indoor Dataset (Revit .rvt), Import IFC To Indoor Dataset (.ifc) (kết quả tìm kiếm tóm tắt trang create-the-indoors-geodatabase / data creation workflow). Georeference CAD/BIM thực hiện trong ArcGIS Pro.
- I/O: DWG/DGN, IFC, RVT → Indoors geodatabase. IMDF: xuất qua workbench "ArcGIS Indoors Model to IMDF" tải từ FME Hub, chạy bằng Data Interoperability extension; cần chạy Generate Unit Openings trước (tài liệu Esri phần cấu hình indoor positioning, và trang "Prepare Indoors data for IMDF export" — bản ArcGIS Pro 2.7/3.0 tìm thấy qua tìm kiếm; bản latest chuyển hướng sang doc.esri.com nhưng nội dung không đọc được). Data Interoperability hỗ trợ DWG/DXF reader/writer (tóm tắt tìm kiếm trang "supported formats"); IFC đọc (tài liệu ArcMap cũ); GeoPackage qua Data Interoperability chưa xác minh. GPKG: ArcGIS Pro nói chung hỗ trợ GeoPackage nhưng không xác minh trong phiên này. OSM tags: chưa xác minh.
- Phủ pipeline: 1 ingest (có), 2 CAD→BIM (một phần: import vào mô hình Indoors, cần cấu hình mapping), 3 georeference (có trong Pro), 4 IMDF (gián tiếp qua FME Hub workbench; OSM không), 5 GPKG (chưa xác minh), 6 QGIS (qua export).
- CLI/API & Linux: ArcGIS Pro là ứng dụng Windows (kiến thức chung, chưa xác minh trong phiên này); geoprocessing tool gọi được bằng ArcPy (chưa đọc trang chính hãng). Linux: chưa xác minh.
- Giá & giấy phép: KHÔNG niêm yết trên các trang đã đọc. Trang https://www.esri.com/en-us/arcgis/products/arcgis-online/pricing và https://esri.com/en-us/store/arcgis-pro không có số giá; user type là giấy phép theo năm (Creator = Pro Basic, Professional = Pro Standard, Professional Plus = Pro Advanced + extension); liên hệ Esri sales 1-800-447-9778 hoặc biểu mẫu. Indoors có 3 cấu hình: Indoors Pro (Named User, bán riêng), Indoors Maps (cấp tổ chức, gồm Indoors Pro không giới hạn cho thành viên), Indoors Spaces (add-on của Maps); routable network cần thêm Network Analyst và 3D Analyst; hỗ trợ từ ArcGIS Pro 3.0 trở lên. Trang licensing không có giá. Giá Data Interoperability: chưa xác minh. Dùng thử/học thuật: chưa xác minh.
- Điểm mạnh: nhập CAD/BIM sâu, mô hình Indoors, quy trình floor-aware đầy đủ.
- Hạn chế: IMDF không native (phụ thuộc FME), phụ thuộc hệ sinh thái Esri, tốn chi phí, khó tự động hoá headless trên Linux.
- Nguồn: URL trên, 2026-11-06.
- Chưa xác minh: tất cả giá; Linux; GPKG; nội dung trang "Prepare Indoors data for IMDF export" bản mới.

### Pointr — dịch vụ chuyển đổi IMDF
- Nhà cung cấp & loại: Pointr (pointr.tech); nhà cung cấp indoor-positioning/mapping, dịch vụ chuyển đổi.
- URL chính thức: https://pointr.tech/technology/imdf
- Mô tả: "conversion tool and dedicated mapping team" chuyển nhiều định dạng bản đồ sang IMDF, bằng engine MapScale AI; định dạng nhập hỗ trợ: DWG, DXF, PDF (Vector), GeoJSON; kết quả dùng để đưa địa điểm lên Apple Maps, Google Maps, Microsoft Places. Trang tự nhận là "Apple-certified" trong kết quả tìm kiếm (tóm tắt, không xác minh chứng nhận).
- I/O: DWG, DXF, PDF vector, GeoJSON → IMDF. GPKG, IFC, OSM tags: không thấy.
- Phủ pipeline: 2–4 dạng dịch vụ (chuyển sàn CAD → IMDF); không phủ 5–6.
- CLI/API & Linux: trang không mô tả API hay tự phục vụ; dạng gửi file và nhận IMDF. Linux không áp dụng.
- Giá: trang không nêu giá; chỉ có "Get in Touch". Liên hệ báo giá.
- Điểm mạnh: nhận diện tự động từ CAD sang IMDF, đúng mục tiêu. Hạn chế: dịch vụ đóng, không GPKG/OSM, không tự động hoá nội bộ, phụ thuộc nhà cung cấp.
- Nguồn: https://pointr.tech/technology/imdf , 2026-11-06.
- Chưa xác minh: giá, API, chất lượng, có xuất GPKG hay không.

### Global Mapper / Global Mapper Pro (Blue Marble Geographics)
- Nhà cung cấp & loại: Blue Marble Geographics; GIS desktop thương mại (giấy phép vĩnh viễn + bảo trì).
- URL chính thức: https://www.bluemarblegeo.com/global-mapper/
- Mô tả: danh sách định dạng chính thức liệt kê DWG và DXF nhập/xuất; GeoPackage là loại nhập được (tài liệu lệnh IMPORT), có hỗ trợ import/export GeoPackage ở mức tóm tắt tìm kiếm; IFC "basic" được thêm từ v22.1 (release notes), hiện trạng không xác nhận. Nguồn: https://bluemarblegeo.com/knowledgebase/global-mapper-20-1/File_Formats.htm , https://bluemarblegeo.com/knowledgebase/global-mapper-25-1/cmd/IMPORT.htm (đọc qua tóm tắt tìm kiếm, không fetch trực tiếp).
- I/O: DXF/DWG có; GPKG có (một phần); IFC hạn chế; IMDF: không thấy; OSM indoor tags: không thấy.
- Phủ pipeline: 1, 3, 5 một phần; không 2, 4.
- CLI/API & Linux: có script/command (trang lệnh IMPORT); Linux: chưa xác minh (nhiều khả năng chỉ Windows, chưa kiểm).
- Giá: trang thông báo giá Global Mapper 26.0 trả 404; nguồn thứ cấp (Fitgap, qua tìm kiếm, có thể lỗi thời) ghi Pro node-locked USD 1,750, floating 2,625, bảo trì 12 tháng 610; Capterra (thứ cấp) ghi từ USD 700 một lần. Giá chính hãng hiện tại: chưa xác minh.
- Điểm mạnh: giá thấp tương đối, tiện CAD/GIS. Hạn chế: không IMDF, không hiểu mô hình indoor.
- Chưa xác minh: IFC hiện tại; giá chính hãng; Linux.

### AutoCAD Map 3D toolset (Autodesk)
- Nhà cung cấp & loại: Autodesk; toolset GIS trong AutoCAD.
- URL: https://www.autodesk.com/de/products/autocad/included-toolsets/autocad-map-3d ; https://help.autodesk.com/cloudhelp/2025/ENU/MAP3D-WhatsNew/files/GUID-3A5EDBB6-6DDA-4805-8584-2B2F1433CE52.htm
- Mô tả: Map 3D được ghi là gồm trong AutoCAD 2026/2027 (trang vùng ngôn ngữ, qua tìm kiếm). Provider FDO GeoPackage (từ Map 3D 2025) "cho phép truy cập dữ liệu GIS lưu trong file GeoPackage" — đọc/hiển thị/chỉnh sửa; xuất sang GPKG không được xác nhận. IFC, IMDF: không thấy.
- Phủ: 1, một phần 3, 5 (không xác nhận). Windows desktop (chưa xác minh). Giá: không kiểm; chưa xác minh.
- Hạn chế: không IMDF/OSM.

## Bảng tóm tắt

| Công cụ | DXF/DWG | IFC | Xuất IMDF | GPKG | OSM tags | CLI/tự động | Linux | Giá |
|---|---|---|---|---|---|---|---|---|
| GDAL/OGR | DXF có; DWG chưa xác minh | chưa xác minh | không | chưa xác minh | không | ogr2ogr (chưa xác minh) | chưa xác minh | miễn phí |
| FME Form/Flow | đọc/ghi (đến 2022) | đọc/ghi | có (writer native) | đọc/ghi | chưa xác minh | FME Flow (chưa xác minh chi tiết) | ACAD/IFC/GPKG có; IMDF chưa xác minh | liên hệ báo giá; thuê bao năm; Grant miễn phí cho SV/GV/phi lợi nhuận |
| ArcGIS Pro + Indoors | DWG/DGN import; Interop DWG/DXF | IFC import | gián tiếp (workbench FME Hub + Data Interoperability) | chưa xác minh | chưa xác minh | ArcPy chưa xác minh | chưa xác minh | liên hệ Esri sales |
| Pointr | DWG, DXF, PDF, GeoJSON | không thấy | có (dịch vụ) | không thấy | không thấy | không (gửi file) | n/a | liên hệ |
| Global Mapper | DWG/DXF | basic/chưa xác nhận | không thấy | có (một phần) | không thấy | có (script) | chưa xác minh | chính hãng chưa xác minh; thứ cấp USD 700–1,750+ |
| AutoCAD Map 3D | DWG gốc | không thấy | không | đọc (FDO) | không | không kiểm | chưa xác minh | chưa xác minh |

## Nguồn (truy cập 2026-11-06)
- https://fme.safe.com/pricing/
- https://docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/imdf/imdf.htm (và imdf_writer.htm — chỉ qua tìm kiếm)
- https://docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/acad/acad.htm
- https://docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/ifc/ifc.htm
- https://docs.safe.com/fme/html/FME-Form-Documentation/FME-ReadersWriters/ogcgeopackage/ogcgeopackage.htm (qua tìm kiếm)
- https://www.safe.com/company-updates/safe-softwares-fme-supports-imdf (qua tìm kiếm)
- https://doc.esri.com/en/arcgis-pro/latest/help/data/indoors/choose-a-licensing-configuration.html
- https://doc.esri.com/en/arcgis-pro/latest/help/data/indoors/create-the-indoors-geodatabase.html (qua tìm kiếm)
- https://doc.esri.com/en/arcgis-pro/latest/help/data/indoors/get-started-with-arcgis-indoors.html
- https://pro.arcgis.com/en/pro-app/2.7/help/data/indoors/prepare-indoors-data-for-imdf-export.htm (qua tìm kiếm)
- https://www.esri.com/en-us/arcgis/products/arcgis-online/pricing ; https://esri.com/en-us/store/arcgis-pro
- https://pointr.tech/technology/imdf
- https://gdal.org/en/stable/drivers/vector/dxf.html
- https://help.autodesk.com/cloudhelp/2025/ENU/MAP3D-WhatsNew/files/GUID-3A5EDBB6-6DDA-4805-8584-2B2F1433CE52.htm
- Global Mapper: bluemarblegeo.com knowledgebase (qua tìm kiếm); giá thứ cấp: Fitgap, Capterra (qua tìm kiếm)

## Không truy cập được / chưa xác minh
- support.safe.com bài "Converting ArcGIS Indoors Data to IMDF": 403.
- https://www.bluemarblegeo.com/global-mapper-26-0-price-notification/ : 404.
- docs.safe.com đường dẫn "FME-Readers-Writers/..." (imdf, dwg, geopackage): 404 (đúng là "FME-ReadersWriters").
- https://pro.arcgis.com/.../latest/... chuyển hướng sang doc.esri.com; trang "Prepare Indoors data for IMDF export" bản mới trả nội dung rỗng.
- Giá cụ thể: FME, ArcGIS Pro/Indoors/Data Interoperability, Pointr, Autodesk, Global Mapper (chính hãng) đều chưa có số niêm yết; không ước đoán.
- Chưa tìm thấy công cụ xuất OSM Simple Indoor Tagging; chưa khảo sát các ETL khác (Hexagon, Bentley, Trimble, Hale studio...).
