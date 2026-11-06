# Phiên D — Dịch vụ và nhà cung cấp indoor mapping

Ngày truy cập tất cả nguồn: 2026-11-06 (trừ khi ghi khác). Ký hiệu: [CHÍNH HÃNG] = đã đọc trang chính hãng qua WebFetch; [THỨ CẤP] = chỉ thấy qua kết quả tìm kiếm/bên thứ ba.

## Câu hỏi nghiên cứu
Đã có dịch vụ/nhà cung cấp indoor mapping nào nhận CAD/BIM (DXF/DWG/IFC) và trả IMDF/GeoJSON, mô hình giá và giá công khai ra sao, có xuất dữ liệu offline (tránh khoá nhà cung cấp) không?

## Kết luận ngắn
- CÓ dịch vụ nhận DXF/DWG và xuất IMDF: Archilogic (đầu vào JPG/PNG/PDF/DWG/DXF; đầu ra gồm GeoJSON, IFC, IMDF, DXF), giá công khai $24.90–$59/floor plan/tháng hoặc $329/lần chuyển đổi (Starter). Pointr IMDF Converter (cho Microsoft Places) niêm yết $125/floor plan nhưng chỉ qua nguồn thứ cấp. Mappedin nhận DWG/DXF/PDF/ảnh và có IMDF export (dành enterprise, giá không công khai).
- Apple Indoor Maps Program: miễn phí (không phí đăng ký/IMDF/positioning) nhưng không phải dịch vụ chuyển đổi; bạn phải tự có IMDF hoặc dùng bên thứ ba. Không có dịch vụ nào xác minh được xuất GPKG trực tiếp; không thấy dịch vụ nhận IFC rồi ra IMDF (Archilogic xuất IFC chứ nhập IFC chưa xác minh).
- Hầu hết hãng (MazeMap, Mappedin, Mapsted, Pointr, Esri, FME) "báo giá"; không ước đoán số.

## Độ tin cậy
Trung bình. Giá Archilogic và FAQ/chương trình Apple đọc từ trang chính hãng. Giá Pointr $125, giá Esri, Mappedin $165/map/tháng là thứ cấp. Giá có thể đổi; trang Archilogic không nêu tiền tệ.

---

## A. Chương trình công khai / miễn phí

### Apple Indoor Maps Program (Apple Business Register + IMDF Sandbox)
- **Nhà cung cấp & loại:** Apple; chương trình đăng ký/onboarding (không phải dịch vụ chuyển đổi).
- **URL:** https://register.apple.com/indoor ; FAQ https://register.apple.com/resources/indoor/program/faq
- **Mô tả:** Giúp tổ chức tạo indoor map dùng IMDF (các file GeoJSON); có IMDF Sandbox để xem/sửa nhỏ; sau đó khảo sát RF bằng app Apple Indoor Survey để định vị qua Wi-Fi hiện có; hiển thị bằng MapKit/MapKit JS. Dành cho tổ chức có không gian lớn (sân bay, trung tâm thương mại, bệnh viện, đại học, văn phòng...). Liên hệ: indoor@apple.com, imdfquestions@apple.com [CHÍNH HÃNG, register.apple.com/indoor]. FAQ nêu Apple Maps chỉ thêm indoor map cho khu vực công cộng của sân bay khi có phép của chủ/vận hành; danh sách quốc gia đăng ký gồm USA, UK, Canada, Germany, Japan [CHÍNH HÃNG, FAQ]. (Hai trang hơi khác phạm vi: trang chương trình nói tổ chức lớn nói chung; FAQ nói về hiển thị trong Apple Maps — cần đọc kỹ khi quyết định.)
- **Đầu vào/đầu ra:** Đầu vào là IMDF (tự tạo hoặc qua công cụ bên thứ ba). Không nhận DXF/DWG/IFC trực tiếp. Không có GPKG/OSM tags.
- **Phủ bước pipeline:** Chỉ đích nộp của bước 4 (IMDF). Không phủ 1,2,3,5,6.
- **API/tự động hoá:** FAQ: Apple không cung cấp public API cho indoor maps; tổ chức kiểm soát nhà phát triển nào truy cập; hiển thị qua MapKit/MapKit JS. Upload qua ABR (Apple Business Register) — tự động hoá chưa xác minh.
- **Mô hình giá & GIÁ:** Miễn phí. "Apple does not charge for registration, for using IMDF, or for the indoor positioning service." (https://register.apple.com/indoor, 2026-11-06). Chi phí thực tế nằm ở việc tạo IMDF và khảo sát.
- **Khoá nhà cung cấp/quyền dữ liệu:** IMDF là chuẩn mở (OGC Community Standard, theo kết quả tìm kiếm [THỨ CẤP] tới docs.ogc.org/cs/20-094); dữ liệu của mình. Positioning và hiển thị gắn hệ Apple. Điều khoản dữ liệu chi tiết chưa xác minh.
- **Mạnh/hạn chế:** Mạnh: miễn phí, có Sandbox kiểm lỗi, có validation (theo [THỨ CẤP]: Apple validate chi tiết, georeference kiểm tay). Hạn chế: không chuyển đổi; yêu cầu quyền chủ sở hữu/tổ chức; phạm vi địa lý hạn chế.
- **Nguồn:** https://register.apple.com/indoor ; https://register.apple.com/resources/indoor/program/faq (cả hai 2026-11-06).
- **Chưa xác minh:** Điều khoản dữ liệu; yêu cầu validate chi tiết (chỉ từ tóm tắt tìm kiếm); API upload tự động.

### Safe Software FME (FME Form) — workbench CAD → IMDF
- **Nhà cung cấp & loại:** Safe Software; phần mềm ETL thương mại (không phải SaaS chuyển đổi dạng "gửi file").
- **URL:** https://fme.safe.com ; bài hướng dẫn https://support.safe.com/hc/en-us/articles/25407420486669 (HTTP 403 khi fetch — không đọc được).
- **Mô tả:** [THỨ CẤP, từ kết quả tìm kiếm] Series 3 phần "Converting CAD Datasets to IMDF": Part 1 tiền xử lý DWG, Part 3 georeference rồi chuyển sang IMDF theo quy ước đặt tên. Apple FAQ liệt kê FME dùng để chuyển đổi và validate IMDF (không để tạo/hiển thị) [CHÍNH HÃNG, FAQ Apple]. Esri doc nói xuất ArcGIS Indoors → IMDF cần Data Interoperability + workbench trên FME Hub [THỨ CẤP qua tìm kiếm].
- **Đầu vào/đầu ra:** DWG đã làm sạch → IMDF (từ tutorial, thứ cấp). FME nói chung đọc/ghi GPKG, IFC (khả năng chung của FME, chưa đọc lại trên trang chính hãng phiên này).
- **Phủ bước:** 1 (ingest), 3 (georeference), 4 (IMDF), có thể 5 (ghi GPKG) — nhưng cần tự dựng workflow, không tự nhận diện phòng/cửa hoàn toàn.
- **API/tự động hoá:** FME Flow (server) cho tự động hoá — tính năng chung, chưa xác minh chi tiết phiên này.
- **Mô hình giá & GIÁ:** Thuê bao năm theo quy mô tổ chức/triển khai/engine capacity; KHÔNG niêm yết giá — "báo giá qua form" (https://fme.safe.com/pricing/, 2026-11-06). Có FME Grant Program miễn phí cho phi lợi nhuận/giảng viên/sinh viên.
- **Khoá nhà cung cấp:** Workspace là định dạng riêng của FME; dữ liệu đầu ra là chuẩn mở.
- **Mạnh/hạn chế:** Mạnh: gần nhất với pipeline đề xuất, đầu ra mở. Hạn chế: giá cao/không công khai, vẫn cần quy ước layer CAD và tiền xử lý thủ công.
- **Nguồn:** https://fme.safe.com/pricing/ ; kết quả tìm kiếm tới support.safe.com (Part 1, Part 3), engage.safe.com/presentations/producing-apple-imdf-datasets-fme/ (2026-11-06).
- **Chưa xác minh:** nội dung bài hướng dẫn (403), danh sách format chính thức, mức giá.

## B. Dịch vụ thương mại (giá công khai trước)

### Archilogic
- **Nhà cung cấp & loại:** Archilogic; SaaS chuyển floor plan thành bản đồ/mô hình số, có API.
- **URL:** https://www.archilogic.com/pricing ; developers.archilogic.com (được trang giá liên kết, chưa fetch).
- **Mô tả:** Nền tảng chuyển floor plan thành dữ liệu không gian có editor, API, webhooks. Có trang Microsoft Places (https://www.archilogic.com/microsoft-places, chỉ thấy qua tìm kiếm).
- **Đầu vào/đầu ra:** Đầu vào JPG, PNG, PDF, DWG, DXF (IFC không có trong danh sách). Đầu ra: JPG, PNG, SVG, DXF, GeoJSON, IFC, GLTF, IMDF [CHÍNH HÃNG, trang giá]. GPKG: không có. OSM tags: không nêu.
- **Phủ bước:** 1, 3 (một phần), 4 (IMDF/GeoJSON). Không GPKG (bước 5 tự làm từ GeoJSON), 6 sau đó.
- **API/tự động hoá:** API và webhooks ở Starter và Professional; Plus không có API; Floor Plan SDK ở Enterprise (Starter cũng liệt kê) [CHÍNH HÃNG].
- **Mô hình giá & GIÁ** (trang https://www.archilogic.com/pricing, 2026-11-06; ký hiệu "$", tiền tệ không nêu):
  - Starter: miễn phí, giới hạn 5 floor plan; mỗi chuyển đổi $329 (một lần).
  - Plus: $24.90 / floor plan / tháng, gói năm từ 10 floor plan.
  - Professional: $59 / floor plan / tháng, gói năm từ 10 floor plan.
  - Enterprise: custom (liên hệ).
- **Khoá nhà cung cấp/quyền dữ liệu:** Xuất được nhiều format mở (kể cả IMDF/GeoJSON), giảm khoá; quyền dữ liệu/ToS chưa đọc. Trang nói "Export in any format" ở Plus/Starter [THỨ CẤP qua tìm kiếm].
- **Mạnh/hạn chế:** Mạnh: giá công khai rõ, nhận DXF/DWG, ra IMDF/GeoJSON. Hạn chế: không có GPKG/OSM tags; không xác nhận IFC đầu vào; chất lượng nhận diện phòng/cửa trên CAD thật chưa kiểm; tính theo floor plan nên toà nhiều tầng đắt.
- **Nguồn:** https://www.archilogic.com/pricing (2026-11-06).
- **Chưa xác minh:** tiền tệ, điều khoản dữ liệu, độ chính xác đầu ra IMDF so với Apple validator, IFC input.

### Pointr (IMDF Converter / MapScale / Microsoft Places converter)
- **Nhà cung cấp & loại:** Pointr; nhà cung cấp indoor mapping/wayfinding/positioning; có công cụ IMDF Conversion.
- **URL:** https://www.pointr.tech/ ; https://converter.pointr.cloud/ (redirect 302 sang https://msplaces.pointr.cloud/ — trang chỉ hiện "Signing you in…", không đọc được); docs https://docs-dev.pointr.tech/... (chỉ hiện tiêu đề).
- **Mô tả:** Trang chủ liệt kê "AI Mapping (MapScale)", "IMDF Conversion", SDK iOS/Android/Web, gói "Maps" và "Maps & Location" [CHÍNH HÃNG]. Apple FAQ liệt kê Pointr trong nền tảng IMDF bên thứ ba [CHÍNH HÃNG].
- **Đầu vào/đầu ra:** [THỨ CẤP, tìm kiếm tóm tắt docs] mỗi lần một toà; mỗi file chứa một floor plan; mỗi file ≤ 50 MB. Định dạng đầu vào cụ thể chưa xác minh. Đầu ra IMDF (theo tên công cụ).
- **Phủ bước:** 4 (IMDF); các bước khác chưa xác minh.
- **API/tự động hoá:** SDK/API cho bản đồ (trang chủ); API cho converter chưa xác minh.
- **Mô hình giá & GIÁ:** Trang chủ không niêm yết giá. Converter Microsoft Places: $125 / floor plan [THỨ CẤP, kết quả tìm kiếm; chưa xác minh trên trang chính hãng; tiền tệ/ngày chưa rõ]. Gói Maps: liên hệ.
- **Khoá:** chưa xác minh.
- **Mạnh/hạn chế:** Có thể rẻ để thử cho IMDF theo tầng; không xác minh được trực tiếp.
- **Nguồn:** https://www.pointr.tech/ ; tìm kiếm 2026-11-06.
- **Chưa xác minh:** giá $125, định dạng vào, điều khoản.

### Mappedin
- **Nhà cung cấp & loại:** Mappedin; SaaS indoor mapping/wayfinding, có Editor, SDK.
- **URL:** https://www.mappedin.com/pricing ; https://mappedin.com/resources/blog/product-101-imdf-export
- **Mô tả:** IMDF export chuyển dữ liệu venue trong Mappedin Editor sang IMDF để đưa vào Apple Indoor Maps Program; cần config file, tài khoản Apple Business Register; nhằm khách hàng enterprise; chuyển floor plan sang IMDF cho Microsoft Places miễn phí [CHÍNH HÃNG, blog, 2026-11-06].
- **Đầu vào/đầu ra:** Đầu vào floor plan DWG, DXF, PDF, PNG, JPEG, WebP [CHÍNH HÃNG, trang giá]. Đầu ra IMDF. GPKG/IFC: không nêu.
- **Phủ bước:** 1, 3, 4 (trong Mappedin).
- **API/tự động hoá:** SDK (Mappedin 3D renderer); export/API công khai chưa mô tả trên trang giá.
- **Mô hình giá & GIÁ:** Thuê bao theo diện tích (sq ft/m²), theo toà/campus; không niêm yết; tháng-tháng/năm/nhiều năm; dịch vụ tạo bản đồ tính thêm; bắt đầu miễn phí (trang giá, 2026-11-06). Kết quả tìm kiếm thứ cấp nêu $165/map/tháng (Pro) và $25/map/tháng (Plus, thông báo cũ) — [THỨ CẤP, chưa xác minh, không dùng làm giá chính thức].
- **Khoá:** Dữ liệu nằm trong Editor; IMDF export dành enterprise, cần liên hệ. 
- **Nguồn:** hai URL trên.
- **Chưa xác minh:** giá thực tế, API export, quyền dữ liệu.

### MazeMap
- **Nhà cung cấp & loại:** MazeMap; SaaS indoor maps (giáo dục, bệnh viện, doanh nghiệp).
- **URL:** https://mazemap.com/our-maps/pricing
- **Mô tả/Mô hình giá:** Giá theo diện tích m² cần lập bản đồ cộng giải pháp mua kèm; không niêm yết giá, cần form báo giá, phản hồi 1–2 ngày làm việc. Enterprise Package: bản đồ trong/ngoài nhà, API embed, Map Editor, customer success manager, POI import, path navigation. "Map and data export" là add-on, không nêu format hay giá [CHÍNH HÃNG, 2026-11-06].
- **Đầu vào/đầu ra:** chưa xác minh (không nêu trên trang giá). IMDF/GPKG: không nêu.
- **Phủ bước:** chưa xác minh; có vẻ chủ yếu 4/hiển thị trong hệ MazeMap.
- **GIÁ:** "Liên hệ báo giá".
- **Khoá:** Export là add-on tính phí -> rủi ro khoá cao.
- **Chưa xác minh:** format đầu vào/ra.

### Mapsted
- **Nhà cung cấp & loại:** Mapsted; indoor mapping/positioning.
- **URL:** https://www.mapsted.com/pricing (trang chỉ chứa form liên hệ/Request Demo; không có giá).
- **Mô tả:** Thông cáo 2021 [THỨ CẤP: edacafe.com/nbc/articles/1/1882138/...] nói Mapsted bán gói self-serve theo diện tích; không thấy giá hiện hành. Gartner [THỨ CẤP]: giá theo bậc (số địa điểm, diện tích, add-on).
- **GIÁ:** "Liên hệ báo giá"; hỗ trợ DWG/IMDF/export: chưa xác minh.

### Esri ArcGIS Indoors
- **Nhà cung cấp & loại:** Esri; extension ArcGIS (thương mại).
- **URL:** https://pro.arcgis.com/en/pro-app/3.0/help/data/indoors/prepare-indoors-data-for-imdf-export.htm
- **Mô tả:** Quy trình xuất IMDF: chạy Generate Unit Openings (cần door detail lines kiến trúc) rồi export; yêu cầu tổ chức ArcGIS có Indoors extension [CHÍNH HÃNG, 2026-11-06]. Kết quả tìm kiếm [THỨ CẤP] nói xuất cần Data Interoperability + workbench FME Hub và output là .zip GeoJSON.
- **Đầu vào/đầu ra:** Mô hình ArcGIS Indoors (có thể nạp từ CAD/BIM — chưa đọc chi tiết) → IMDF. Apple FAQ liệt kê Esri ArcGIS Indoors là nền tảng IMDF [CHÍNH HÃNG].
- **Phủ bước:** 3, 4 (và GIS gốc, GDB; ghi GPKG qua ArcGIS Pro là khả năng chung, chưa xác minh trong ngữ cảnh này), 6 không (dùng ArcGIS).
- **GIÁ:** Không niêm yết. Nguồn thứ cấp (softwarefinder.com) ước $21,000–$30,000/năm và Esri community nhắc $0.03–$0.07/sq ft — [THỨ CẤP, chưa xác minh, không dùng]. Chính thức: liên hệ Esri.
- **Khoá:** hệ sinh thái Esri; đầu ra IMDF mở.
- **Chưa xác minh:** giá, định dạng CAD/BIM vào.

### Các nền tảng khác (chỉ nêu theo Apple FAQ [CHÍNH HÃNG])
Autodesk BIM 360 Ops, LocusLabs, Visioglobe được Apple FAQ liệt kê là nền tảng IMDF bên thứ ba. Chưa khảo sát thêm; giá/đầu vào chưa xác minh. Mapwize (ServiceNow mua 2021, [THỨ CẤP]) — giá không công khai; Pointr có trang "Mapwize alternative" (chưa đọc).
Google/Mapbox: chưa tìm thấy chương trình indoor tương đương IMDF trong phiên này (chưa xác minh, chưa khảo sát đủ).
Dịch vụ vẽ lại PDF→DWG trên Fiverr/CAD Crowd (chỉ ra DWG, không ra IMDF) — [THỨ CẤP], chỉ hữu ích cho tiền xử lý.

---

## Bảng tóm tắt

| Dịch vụ | Vào | Ra | API | Giá công khai | Xuất offline/khoá |
|---|---|---|---|---|---|
| Apple Indoor Maps Program | IMDF | (đích nộp) | Không public API | Miễn phí | Chuẩn mở; hiển thị gắn Apple |
| FME (Safe) | DWG (tutorial) | IMDF | FME Flow (chưa xác minh) | Báo giá | Đầu ra mở |
| Archilogic | JPG/PNG/PDF/DWG/DXF | GeoJSON, IFC, IMDF, DXF, SVG, GLTF | Có (Starter/Pro) | $329/lần; $24.90 và $59/floor plan/tháng | Xuất nhiều format |
| Pointr converter | chưa xác minh | IMDF | chưa xác minh | $125/floor plan (thứ cấp) | chưa xác minh |
| Mappedin | DWG/DXF/PDF/ảnh | IMDF (enterprise) | SDK | Báo giá | Export qua liên hệ |
| MazeMap | chưa xác minh | chưa xác minh | API embed | Báo giá (theo m²) | Export là add-on |
| Mapsted | chưa xác minh | chưa xác minh | chưa xác minh | Báo giá | chưa xác minh |
| Esri ArcGIS Indoors | mô hình Indoors | IMDF | ArcGIS | Báo giá | Đầu ra mở |

## Nguồn
- https://register.apple.com/indoor (2026-11-06)
- https://register.apple.com/resources/indoor/program/faq (2026-11-06)
- https://www.archilogic.com/pricing (2026-11-06)
- https://www.mappedin.com/pricing (2026-11-06)
- https://mappedin.com/resources/blog/product-101-imdf-export (2026-11-06)
- https://mazemap.com/our-maps/pricing (2026-11-06)
- https://www.mapsted.com/pricing (2026-11-06)
- https://www.pointr.tech/ (2026-11-06)
- https://fme.safe.com/pricing/ (2026-11-06)
- https://pro.arcgis.com/en/pro-app/3.0/help/data/indoors/prepare-indoors-data-for-imdf-export.htm (2026-11-06)
- Thứ cấp (WebSearch 2026-11-06): support.safe.com Part 1/3, edacafe.com Mapsted 2021, softwarefinder.com, community.esri.com, gartner.com, capterra.com, docs.ogc.org/cs/20-094

## Không truy cập được / chưa xác minh
- https://support.safe.com/hc/en-us/articles/25407420486669: HTTP 403.
- https://converter.pointr.cloud/ → msplaces.pointr.cloud: chỉ "Signing you in…"; docs.pointr.tech chỉ có tiêu đề. Giá $125 và ràng buộc 50 MB chỉ từ tóm tắt tìm kiếm.
- Chưa đọc: developers.archilogic.com, Mapsted trang sản phẩm, Visioglobe, LocusLabs, Autodesk, Google/Mapbox, OGC IMDF standard.
- Tiền tệ của Archilogic; điều khoản quyền dữ liệu của mọi nhà cung cấp; khả năng nhận IFC đầu vào; xuất GPKG trực tiếp: chưa xác minh.
