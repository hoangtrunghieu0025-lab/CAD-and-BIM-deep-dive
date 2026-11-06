# Phiên B — Phần mềm CAD/BIM và đường xuất sang GIS/IMDF

Ngày truy cập tất cả nguồn: 2026-11-06 (trừ khi ghi khác). Quy ước: "SC" = nguồn thứ cấp (bên thứ ba, không phải chính hãng). Tên "Pipeline bước 1–6" theo đề bài: 1 ingest, 2 CAD→BIM, 3 extract+georeference, 4 chuẩn hoá OSM/IMDF, 5 ghi GPKG, 6 QGIS.

## Câu hỏi nghiên cứu
Phần mềm CAD/BIM phổ biến (Autodesk, Bentley, Graphisoft, Trimble/SketchUp, Vectorworks, FreeCAD/IfcOpenShell) và các add-in có xuất trực tiếp sang GIS/GPKG/IMDF/IFC không, tự động hoá được không, chạy Linux không, giá bao nhiêu?

## Kết luận ngắn
- Trong phạm vi đã xác minh, KHÔNG có phần mềm CAD/BIM chính hãng nào xuất trực tiếp ra GPKG có cấu trúc OSM Simple Indoor Tagging; chỉ thấy: (a) add-in Autodesk "BIM 360 Ops Revit Add-in" có nút xuất IMDF (tài liệu AU 2019, sản phẩm gắn BIM 360 Ops, chưa xác minh còn phát hành), (b) Spatial Manager (bên thứ ba, Windows) xuất được GPKG từ AutoCAD nhưng đó là xuất hình học/thuộc tính, không phải IMDF, (c) Esri ArcGIS Indoors có quy trình IMDF dựa trên workbench FME (cần Indoors + Data Interoperability).
- Các phần mềm thương mại đều Windows (hoặc Windows/macOS), không có Linux; tự động hoá có (Revit API, Archicad C++ API, APS Design Automation) nhưng đều cần license thương mại. Đường duy nhất chạy Linux + miễn phí là IfcOpenShell/FreeCAD, không phải CAD thương mại.
- Giá thương mại: Archicad Studio USD 2.414/năm; Collaborate USD 2.840/năm; OpenBuildings Designer từ USD 3.844/12 tháng (chính hãng); Autodesk (AutoCAD/Revit) KHÔNG lấy được giá chính hãng (403/placeholder). Kết luận: CAD/BIM thương mại chỉ nên là nguồn dữ liệu đầu vào (IFC/DWG), không thay thế pipeline tự xây.

## Độ tin cậy
Trung bình. Trang Autodesk chính hãng (autodesk.com sản phẩm) trả 403 nên thiếu giá và tính năng chính hãng của AutoCAD/Revit/Civil 3D; thông tin các sản phẩm đó dựa vào help.autodesk.com (truy cập được) và nguồn thứ cấp. Giá Archicad, SketchUp, Bentley là chính hãng; giá Vectorworks không lấy được từ trang chính hãng.

---

## A. Miễn phí / mã nguồn mở

### IfcOpenShell (kèm Bonsai) và FreeCAD (đường IFC)
- Nhà cung cấp & loại: cộng đồng tình nguyện; thư viện/toolkit mã nguồn mở. FreeCAD là CAD/BIM mã nguồn mở dùng IfcOpenShell cho IFC.
- URL chính thức: https://ifcopenshell.org/ ; FreeCAD wiki https://wiki.freecad.org/Arch_IFC (trả "Access Denied" do Anubis, không đọc được).
- Mô tả: IfcOpenShell "open source toolkit and geometry engine", đọc/ghi/sửa IFC, binding C++, Python, TypeScript; chạy Windows, Mac, Linux, web; hỗ trợ IFC2X3, IFC4, IFC4X3; có API tạo 2D drawing, clash detection, chuyển đổi sang >10 định dạng khác (nguồn: ifcopenshell.org, 2026-11-06). Phiên bản tải hiện hiển thị: 0.9.1.
- Đầu vào/đầu ra: IFC (SPF, JSON, XML, HDF5, SQL...). DXF/DWG, GPKG, IMDF, OSM tags: chưa xác minh trên trang này. Mã nguồn FreeCAD exportIFC.py dùng IfcOpenShell (SC: bản mirror GitHub/gitea qua WebSearch).
- Phủ pipeline: bước 1 (đọc IFC), 3 (trích hình học/thuộc tính IfcSpace, IfcDoor, IfcBuildingStorey bằng script — khả năng, chưa xác minh trang chính hãng cho georeference), không tự có bước 4–6.
- CLI/API & Linux: Python API, chạy headless, Linux có.
- Giá & giấy phép: miễn phí. Giấy phép: trang chủ ghi "free software"; LGPL theo danh mục Anaconda (SC: https://anaconda.org/freecad/ifcopenshell, "LGPL-3.0-or-later" cho ifcopenshell-python). Giá niêm yết: 0, tiền tệ không áp dụng, ngày 2026-11-06.
- Điểm mạnh/hạn chế: nền tảng tốt nhất để tự xây bước 1–3 trên Linux; không phải công cụ "bấm nút ra IMDF/GPKG".
- Nguồn: https://ifcopenshell.org/ (2026-11-06); https://anaconda.org/freecad/ifcopenshell (SC, 2026-11-06).
- Chưa xác minh: đặc điểm Bonsai (chỉ thấy tên ở chân trang), tính năng georeference IfcMapConversion của IfcOpenShell, trạng thái giấy phép chính xác của FreeCAD (chỉ thấy qua mirror).

### Autodesk "revit-ifc" (add-in IFC mã nguồn mở cho Revit)
- Nhà cung cấp & loại: Autodesk; mã nguồn mở trên GitHub.
- URL: https://github.com/Autodesk/revit-ifc
- Mô tả: mã .NET Revit dùng cho Link IFC, IFC export và UI export; bản mã nguồn mở ghi đè bản kèm Revit; có DLL độc quyền Autodesk.SteelConnections.ASIFC.DLL chỉ dùng cho dự án.
- Đầu vào/đầu ra: IFC (xuất/liên kết). Không có GPKG/IMDF.
- Phủ pipeline: bước 1 (sinh IFC từ Revit; nguồn dữ liệu).
- CLI/API & Linux: dựng và chạy trên Windows (Visual Studio, Revit.exe); không Linux.
- Giá & giấy phép: mã nguồn LGPL v2.0 (theo trang GitHub); giá 0 cho add-in, nhưng cần Revit (xem dưới). Ngày 2026-11-06.
- Điểm mạnh/hạn chế: cách chuẩn để lấy IFC từ Revit; hỗ trợ Revit 2019+ (bản mới nhất và hai bản trước có sửa lỗi).
- Nguồn: https://github.com/Autodesk/revit-ifc (2026-11-06).
- Chưa xác minh: ngày commit mới nhất.

---

## B. Thương mại

### Autodesk Revit (+ Revit IFC export, BIM 360 Ops Revit Add-in, APS)
- Nhà cung cấp & loại: Autodesk; BIM thương mại, thuê bao.
- URL chính thức: https://www.autodesk.com/products/revit/overview — trả 403, không truy cập được.
- Mô tả (có nguồn): Help chính hãng có trang "IFC Export Setup Options" (ví dụ https://help.autodesk.com/cloudhelp/2026/ENU/Revit-DocumentPresent/files/GUID-E029E3AD-1639-4446-A935-C9796BC34C95.htm; nội dung chi tiết lấy qua tóm tắt tìm kiếm, chưa đọc trọn trang): chọn IFC version/setup, xuất liên kết, property sets, base quantities, chỉ xuất level có Building Story. Revit API có `IFCExportOptions` để xuất IFC bằng code (https://help.autodesk.com/cloudhelp/2024/PTB/Revit-API/files/Revit_API_Developers_Guide/Advanced_Topics/Export/Revit_API_Revit_API_Developers_Guide_Advanced_Topics_Export_IFC_Export_html.html, qua tóm tắt tìm kiếm). Có blog APS về xuất IFC bằng Revit Design Automation (https://aps.autodesk.com/blog/export-ifc-rvt-using-revit-automation-api-part-ii, chưa đọc trọn).
- Add-in IMDF: tài liệu Autodesk University 2019 (BLD322176, Mark Mergenschroer, đọc trọn PDF) mô tả "BIM 360 Ops Revit Add-in": nút "BIM 360 Ops Indoor Map", thêm tham số indoor map vào Project Information, điền `imdf_ordinal` cho từng level, geo-locate bằng Project Base Point/Survey Point (lat/long/elevation/angle to true north), chọn category hiển thị (Doors, Floors, Rooms, Walls, Windows, Stairs...), chỉ hỗ trợ Revit file độc lập; mục tiêu "Transform a Revit file with IMDF to create an Indoor Map" dùng Apple Indoor Positioning. Nguồn: https://static.au-uw2-stg.autodesk.com/Class_Handout_BLD322176_Mark_Mergenschroer.pdf và trang class https://www.autodesk.com/autodesk-university/class/Revit-BIM-360-Ops-Exporting-Asset-and-Location-Data-Facilities-Management-2019 (trang class: 403 khi fetch; tóm tắt qua tìm kiếm).
- Đầu vào/đầu ra: đọc RVT; ghi IFC; IMDF qua add-in BIM 360 Ops (tài liệu 2019); DWG/DXF xuất: chưa xác minh trong phiên này; GPKG: không thấy.
- Phủ pipeline: bước 1, 3 (có georeference trong Revit), và (nếu add-in còn dùng được) bước 4 IMDF. Ghi GPKG/QGIS: không.
- CLI/API & Linux: Revit API (C#, Windows); APS Design Automation chạy trên cloud (tính phí theo Flex token); không Linux desktop.
- Giá & giấy phép: giá thuê bao Revit: chưa xác minh (trang chính hãng 403). Thương mại, thuê bao. APS Model Derivative: IFC được tính "complex job" (0,5 Flex token) theo tóm tắt tìm kiếm của trang APS pricing (SC-ish, chưa đọc trực tiếp; trang pricing redirect, giá USD/token chưa lấy được).
- Điểm mạnh/hạn chế: nguồn IFC/RVT phổ biến nhất; IMDF add-in là lead duy nhất nhưng gắn BIM 360 Ops (sản phẩm cũ, có thể đã ngừng), cần đúng workflow Apple.
- Nguồn: URL ở trên (2026-11-06).
- Chưa xác minh: add-in BIM 360 Ops còn tải được không; giá Revit; tương thích Revit bản mới; APS pricing chi tiết.

### Autodesk AutoCAD / AutoCAD Map 3D / Civil 3D
- Nhà cung cấp & loại: Autodesk; CAD thương mại, thuê bao.
- URL chính thức: https://www.autodesk.com/products/autocad/overview và /subscribe — 403, không truy cập được. Trang EU https://www-int.autodesk.com/eu/products/autocad/subscribe truy cập được nhưng giá hiển thị placeholder "$000.00" (không có số); có ghi thuê bao tháng/1 năm/3 năm, giảm 10% cho 3 năm.
- Mô tả (có nguồn): Help Map 3D: hộp thoại Export ánh xạ đối tượng DWG sang FDO feature class; nêu SHP, SDF, Oracle (https://help.autodesk.com/cloudhelp/2027/ENU/MAP3D-Use/files/GUID-93D7E402-07DD-4303-82D4-CE29AE0AC632.htm; trang không liệt kê đầy đủ định dạng). What's New 2027 (https://help.autodesk.com/cloudhelp/2027/ENU/MAP3D-WhatsNew/files/GUID-5400F410-99B5-4059-B221-63C079FFBDEC.htm): thêm xuất FDO layer sang KML; FDO SQLite 3.50.4; PostGIS 3.6; không nhắc GeoPackage. FDO dùng SQLite, không phải GeoPackage chính thức: kết luận "Map 3D không có xuất GPKG gốc" là suy luận từ việc không thấy trong tài liệu, không phải khẳng định.
- Đầu vào/đầu ra: DWG, DXF; xuất SHP, SDF, KML, SQLite (FDO), PostGIS...; IFC: chưa xác minh phiên này; GPKG, IMDF: không thấy trong tài liệu chính hãng.
- Phủ pipeline: bước 1, 3 (Map 3D có hệ toạ độ), một phần 5 (qua SQLite/SHP). 
- CLI/API & Linux: có API (.NET, ObjectARX, LISP) — chưa xác minh trang chính hãng; chỉ Windows (theo SC Spatial Manager "Windows only").
- Giá: Giá niêm yết chính hãng không truy cập được. Nguồn thứ cấp (SC, không dùng làm giá chuẩn): các blog ghi khoảng USD 2.030/năm cho AutoCAD (chưa kiểm). Ghi nhận: giá thật phụ thuộc vùng.
- Điểm mạnh/hạn chế: Map 3D rất mạnh cho DWG→GIS nhưng không có IMDF, không rõ GPKG, Windows.
- Chưa xác minh: giá, GPKG trong FDO của Map 3D, Civil 3D (không khảo sát riêng).

### Spatial Manager for AutoCAD (add-in bên thứ ba)
- Nhà cung cấp & loại: Spatial Manager; plug-in thương mại cho AutoCAD, BricsCAD, ZWCAD, GstarCAD và bản Desktop độc lập.
- URL: https://www.spatialmanager.com/ ; https://www.spatialmanager.com/spm-forautocad/features/export-spatial-data/optimized-export/
- Mô tả (có nguồn): xuất dữ liệu không gian sang nhiều định dạng, gồm GeoPackage (GPKG), SHP, KML/KMZ, SQLite, GML, GeoJSON, DGN, DXF, LandXML, PostGIS, SQL Server Spatial; tính năng nằm trong edition Professional; chạy AutoCAD/Map 3D/Civil 3D/AutoCAD Architecture 2013–2027, Windows only, không tương thích AutoCAD LT.
- Đầu vào/đầu ra: DXF/DWG (qua host CAD), GPKG xuất/nhập; IFC/IMDF: trang chính không nhắc IFC, BIM, IMDF. OSM: có thể đọc (read-only).
- Phủ pipeline: bước 3 (xuất toạ độ/hệ quy chiếu), 5 (GPKG). Không có nhận diện phòng/cửa, không IMDF.
- CLI/API & Linux: chưa xác minh (không thấy tài liệu CLI); Windows only.
- Giá & giấy phép: chưa xác minh — trang prices chỉ ghi "from" không có số; "all application licenses include one year of free Updates and Support"; loại giấy phép (vĩnh viễn/thuê bao) không nêu. URL https://www.spatialmanager.com/prices/ , 2026-11-06.
- Điểm mạnh/hạn chế: xuất GPKG trực tiếp từ DWG nhanh, nhưng phải có AutoCAD (thương mại) và không chuẩn hoá indoor.
- Nguồn: URL ở trên (2026-11-06).
- Chưa xác minh: giá; Spatial Manager Desktop đọc DXF/DWG không cần AutoCAD (chỉ thấy gợi ý "DXF-based import/export").

### Esri ArcGIS Pro / ArcGIS Indoors (đường BIM→GIS→IMDF, tham khảo)
- Nhà cung cấp & loại: Esri; GIS thương mại. Không phải CAD nhưng là đường BIM→GIS→IMDF chính hãng.
- URL: https://doc.esri.com/en/arcgis-pro/latest/help/data/revit/what-is-bim-data-.html ; https://pro.arcgis.com/en/pro-app/3.0/help/data/indoors/prepare-indoors-data-for-imdf-export.htm
- Mô tả (có nguồn): ArcGIS Pro đọc RVT (Revit 2021–2026 cho Pro 3.7) và IFC (IFC2X3, IFC4, IFC4X3...) như workspace chỉ đọc, mỗi category thành feature class điểm/đường/vùng/multipatch; cần file PRJ hợp lệ và có thể cần file WLD3 để đặt đúng vị trí; Floorplan feature class ban đầu không có cho IFC (SC/blog Esri: Pro 3.2 thêm tool Import IFC to Indoor Dataset, ghi ra file geodatabase). IMDF: trang Esri yêu cầu tổ chức ArcGIS có extension Indoors; tool Generate Unit Openings tạo opening dạng line; trang này không nhắc FME. Bước chuyển IMDF dùng workbench FME "ArcGIS Indoors Model to IMDF" qua Data Interoperability Extension (theo tóm tắt tìm kiếm của trang Esri và bài hướng dẫn FME [SC] https://support.safe.com/hc/en-us/articles/25407628986381-Converting-ArcGIS-Indoors-Data-to-IMDF).
- Đầu vào/đầu ra: RVT, IFC → file geodatabase; IMDF (zip GeoJSON) qua FME; GPKG: không thấy trong các trang đọc.
- Phủ pipeline: 1, 3, 4 (IMDF), nhưng ghi file geodatabase thay vì GPKG.
- CLI/API & Linux: arcpy (Windows). Linux: chưa xác minh.
- Giá: chưa xác minh (không khảo sát trang giá Esri).
- Điểm mạnh/hạn chế: gần nhất với "IFC/Revit → IMDF" nhưng khoá trong hệ sinh thái Esri, giấy phép cao, đầu ra không phải GPKG.
- Chưa xác minh: giá ArcGIS Indoors/Data Interoperability, chạy trên Linux (ArcGIS Enterprise có Linux nhưng chưa kiểm chứng cho các tool này).

### Bentley OpenBuildings Designer / MicroStation
- Nhà cung cấp & loại: Bentley Systems; BIM/CAD thương mại.
- URL: https://www.bentley.com/software/openbuildings-designer/
- Mô tả (có nguồn): "Exchange IFC, RFA, and DWG data across disciplines in a federated environment"; IFC và COBie là định dạng trao đổi; "Integrate real-time GIS data directly into designs"; DWG qua RealDWG; không nhắc API trên trang. Wiki Bentley (SC-chính hãng cộng đồng, qua tóm tắt tìm kiếm): MicroStation chỉ xem/tham chiếu IFC, xuất IFC cần OpenBuildings Designer (File > Export > IFC); một người dùng FME báo exporter hay gán ifcBuildingElementProxy (ý kiến một người dùng, không chính thức).
- Đầu vào/đầu ra: DWG, IFC, DGN; GPKG/IMDF: không thấy.
- Phủ pipeline: bước 1 (IFC/DWG), 3 một phần.
- CLI/API & Linux: chưa xác minh. Yêu cầu hệ thống: Windows 10/11 64-bit hoặc Windows Server 2016/2019, RAM 16 GB tối thiểu — không Linux.
- Giá & giấy phép: "Starting at $3,844.00 USD" cho thuê bao Virtuoso 12 tháng, gồm 1 license + 2 Keys; ghi "varies per region". URL https://www.bentley.com/software/openbuildings-designer/ , truy cập 2026-11-06. Bản vĩnh viễn kèm SELECT: cần báo giá (SC FitGap).
- Điểm mạnh/hạn chế: IFC tốt cho dự án Bentley, nhưng Windows và không có xuất GIS indoor.
- Nguồn: URL trên; https://communities.bentley.com/products/microstation/w/microstation__wiki/36079/how-can-i-convert-dgn-to-ifc (301 sang bentleysystems.service-now.com, chưa đọc trọn).
- Chưa xác minh: giá MicroStation; OpenCities Map; OpenRoads/OpenSite; GPKG trong sản phẩm Bentley.

### Graphisoft Archicad
- Nhà cung cấp & loại: Graphisoft (nhóm Nemetschek); BIM thương mại.
- URL: https://www.graphisoft.com/en-us/pricing/ ; https://www.graphisoft.com/en-us/plans-and-products/archicad-studio/
- Mô tả (có nguồn): IFC export có geo-referencing từ Archicad 23: nhập Survey Point (Geo Referencing Map), cần điền Geodetic Datum và Map Projection; xuất IFC 2x3 thành 2 property set, IFC4 tạo IfcMapConversion/IfcProjectedCRS (https://helpcenter.graphisoft.com/ — đường dẫn user-guide/89325 bị chuyển hướng; nội dung lấy từ kết quả tìm kiếm, và bài SC https://centralinnovation.com/resources/exporting-ifc-from-archicad-location). Một người dùng cộng đồng báo IFC4 không mang georeference (ý kiến một người dùng, chưa rõ kết cục). API: C/C++ API Development Kit, Windows và macOS (trang 2016–2017, có thể cũ); Python add-on thử nghiệm cho Archicad 23 (cộng đồng).
- Đầu vào/đầu ra: IFC import/export, DWG/DXF (chưa xác minh trong phiên này); GPKG/IMDF: không thấy.
- Phủ pipeline: bước 1, 3 (IFC có CRS).
- CLI/API & Linux: C++ API; trang sản phẩm: desktop macOS và Windows, không nhắc Linux.
- Giá & giấy phép (chính hãng, USD, theo seat, chưa thuế, ngày 2026-11-06): Studio USD 2.414 trả trước 1 năm (USD 201/tháng), USD 345 nếu trả tháng; Collaborate USD 2.840/năm (USD 237/tháng), USD 406 trả tháng; Max USD 5.700/năm (USD 475/tháng), USD 800 trả tháng; 3 năm: 7.242 / 8.520 / 17.100 tổng. "Final price depends on your billing country". Thuê bao; có bản EDU miễn phí cho sinh viên/giáo viên và dùng thử miễn phí. Nguồn: https://www.graphisoft.com/en-us/pricing/.
- Điểm mạnh/hạn chế: IFC4 có CRS (nếu cấu hình đúng); không có đường IMDF/GPKG; không Linux.
- Chưa xác minh: DWG/DXF; sự tồn tại Archicad MCP (Beta) chỉ thấy tên trên trang Studio, không tính năng.

### Trimble SketchUp
- Nhà cung cấp & loại: Trimble; 3D modeling/BIM nhẹ, thuê bao.
- URL: https://sketchup.trimble.com/buy/pricing ; https://help.sketchup.com/en/importing-and-exporting-ifc-files
- Mô tả (có nguồn): xuất IFC 2x3 và IFC 4 (SketchUp 2026; bản ≤2025 chỉ 2x3 trên Windows, macOS chỉ IFC 4); tuỳ chọn Standard IFC Spatial Hierarchy (IfcProject, IfcSite, IfcBuilding); xuất Tessellation hoặc Body; CRS xuất qua Trimble Geodetic Library, không có CRS thì thực thể CRS bị xoá; một số thực thể có thể không xuất.
- Đầu vào/đầu ra: IFC import/export; DWG ("Enhanced IFC and DWG compatibility" nằm ở gói Pro); GPKG/IMDF: không.
- Phủ pipeline: bước 1 (nguồn IFC; hạn chế chất lượng ngữ nghĩa theo diễn đàn SketchUp—ý kiến người dùng).
- CLI/API & Linux: Ruby API (chưa xác minh trang); Studio ghi "Windows only"; Linux không thấy.
- Giá (chính hãng, USD, per user, per month, billed annually, 2026-11-06): Go 10,75; Pro 33,25; Studio 71,58; Pro Scan 41,58; Pro Civil Contractor 41,58; Pro Advanced Workflows 49,92. Education: student/educator 55 (tiền tệ không ghi trên trang), K-12 miễn phí. Nguồn: https://sketchup.trimble.com/buy/pricing.
- Điểm mạnh/hạn chế: rẻ nhất trong nhóm thương mại; dữ liệu phòng/cửa thường không có ngữ nghĩa IFC tốt.
- Chưa xác minh: Trimble Connect, Tekla Structures (chưa khảo sát), liệu IFC export nằm ở gói Pro hay Go (trang ghi Pro).

### Vectorworks (Architect / Landmark / Design Suite)
- Nhà cung cấp & loại: Vectorworks, Inc.; CAD/BIM thương mại.
- URL: https://www.vectorworks.net/architect/buy ; https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Georeference/GIS_and_georeferencing.htm
- Mô tả (có nguồn): Help 2026: nhập và xuất Shapefile và ảnh georeference; georeference qua Georeference command, Geolocate tool, Survey Point tool; Architect và Landmark có đầy đủ công cụ, Spotlight hạn chế. GeoPackage: không được nhắc. IFC: xuất .ifc/.ifczip/.ifcxml với IFC 2x2, 2x3, 4; IFC 4 xuất toạ độ geolocated cùng CRS (theo tóm tắt tìm kiếm từ help.vectorworks 2022); Landmark được buildingSMART chứng nhận IFC2x3 và IFC4 (tài liệu Vectorworks, qua tìm kiếm).
- Đầu vào/đầu ra: DWG/DXF, IFC, SHP; GPKG, IMDF: không thấy.
- Phủ pipeline: bước 1, 3.
- CLI/API & Linux: chưa xác minh (Vectorworks có Python/VectorScript — chưa đọc tài liệu); Linux không thấy.
- Giá: chưa xác minh từ trang chính hãng — trang buy chỉ có tuỳ chọn "Monthly" và "Annual", không hiện số. Nguồn thứ cấp (SC, dùng tham khảo, không phải niêm yết): Design Suite ~USD 1.980/năm, Architect ~USD 1.530/năm (nhiều trang tổng hợp).
- Điểm mạnh/hạn chế: có xuất Shapefile gốc và IFC4 có CRS; chưa thấy GPKG/IMDF.

---

## Bảng tóm tắt

| Công cụ | Loại | DXF/DWG | IFC | GPKG | IMDF | Tự động hoá | Linux | Giá niêm yết |
|---|---|---|---|---|---|---|---|---|
| IfcOpenShell/FreeCAD | OSS | chưa xác minh | đọc/ghi | không (tự viết) | không | Python | Có | 0 |
| Autodesk revit-ifc | OSS add-in | — | xuất | không | không | .NET | Không | 0 (cần Revit) |
| Revit (+BIM 360 Ops add-in) | Thương mại | chưa xác minh | xuất | không | có (add-in 2019, chưa xác minh còn dùng) | Revit API, APS | Không | Chưa xác minh (403) |
| AutoCAD / Map 3D | Thương mại | DWG/DXF | chưa xác minh | không thấy | không | API (chưa xác minh) | Không | Chưa xác minh (403) |
| Spatial Manager (AutoCAD) | Add-in thương mại | qua host | không nhắc | Có | không | chưa xác minh | Không | Chưa xác minh ("from") |
| Esri ArcGIS Pro/Indoors | GIS thương mại | — | đọc | không (File GDB) | Có (qua FME) | arcpy | chưa xác minh | Chưa xác minh |
| Bentley OpenBuildings Designer | Thương mại | DWG | xuất | không thấy | không | chưa xác minh | Không | từ USD 3.844/12 tháng |
| Archicad | Thương mại | chưa xác minh | xuất (CRS) | không | không | C++ API | Không | USD 2.414–5.700/năm |
| SketchUp | Thương mại | DWG (Pro) | xuất | không | không | Ruby (chưa xác minh) | Không | USD 10,75–71,58/tháng (annual) |
| Vectorworks | Thương mại | DWG/DXF | xuất | không thấy | không | chưa xác minh | Không | Chưa xác minh |

## Nguồn
- https://ifcopenshell.org/ (2026-11-06)
- https://github.com/Autodesk/revit-ifc (2026-11-06)
- https://help.autodesk.com/cloudhelp/2027/ENU/MAP3D-Use/files/GUID-93D7E402-07DD-4303-82D4-CE29AE0AC632.htm (2026-11-06)
- https://help.autodesk.com/cloudhelp/2027/ENU/MAP3D-WhatsNew/files/GUID-5400F410-99B5-4059-B221-63C079FFBDEC.htm (2026-11-06)
- https://static.au-uw2-stg.autodesk.com/Class_Handout_BLD322176_Mark_Mergenschroer.pdf (2026-11-06, đọc trọn)
- https://www-int.autodesk.com/eu/products/autocad/subscribe (2026-11-06; giá là placeholder)
- https://www.spatialmanager.com/ , /spm-forautocad/features/export-spatial-data/optimized-export/ , /prices/ (2026-11-06)
- https://doc.esri.com/en/arcgis-pro/latest/help/data/revit/what-is-bim-data-.html (2026-11-06)
- https://pro.arcgis.com/en/pro-app/3.0/help/data/indoors/prepare-indoors-data-for-imdf-export.htm (2026-11-06, trang lưu trữ)
- https://support.safe.com/hc/en-us/articles/25407628986381-Converting-ArcGIS-Indoors-Data-to-IMDF (SC, chỉ qua kết quả tìm kiếm)
- https://www.bentley.com/software/openbuildings-designer/ (2026-11-06)
- https://www.graphisoft.com/en-us/pricing/ ; https://www.graphisoft.com/en-us/plans-and-products/archicad-studio/ (2026-11-06)
- https://sketchup.trimble.com/buy/pricing ; https://help.sketchup.com/en/importing-and-exporting-ifc-files (2026-11-06)
- https://app-help.vectorworks.net/2026/eng/VW2026_Guide/Georeference/GIS_and_georeferencing.htm ; https://www.vectorworks.net/architect/buy (2026-11-06)
- SC: https://anaconda.org/freecad/ifcopenshell ; https://centralinnovation.com/resources/exporting-ifc-from-archicad-location ; trang giá tổng hợp Vectorworks/AutoCAD (chỉ qua WebSearch).

## Không truy cập được / chưa xác minh
- Không truy cập được (403): https://www.autodesk.com/products/autocad/overview , /products/autocad/subscribe , /products/revit/overview , autodesk.ca (AutoCAD LT subscribe), trang class AU 2020 (Indoor Maps Facilities).
- Chuyển hướng không theo: helpcenter.graphisoft.com/user-guide/89325 ; communities.bentley.com wiki (sang service-now); aps.autodesk.com/pricing.
- Chặn bot: wiki.freecad.org (Anubis, "Access Denied"). 404: graphisoft.com/buy-archicad; bricscad.octave.com/bricscad/pricing.
- Chưa xác minh: giá AutoCAD/Revit/Civil 3D/MicroStation/Vectorworks/Spatial Manager/Esri; còn phát hành của BIM 360 Ops Revit add-in; Civil 3D, Trimble Connect, Tekla, BricsCAD, Allplan (chưa khảo sát); API/CLI của Spatial Manager, Vectorworks, SketchUp; hỗ trợ Linux của các tool Esri; GPKG trong FDO của Map 3D.
