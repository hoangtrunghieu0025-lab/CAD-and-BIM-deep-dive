# 7D — Vận hành & bảo trì (FM), COBie, digital twin

- **Câu hỏi nghiên cứu**: Dữ liệu vận hành/tài sản được bàn giao thế nào (COBie, IFC), nối với CAFM/CMMS và digital twin ra sao?
- **Kết luận ngắn**: COBie là tập con phi hình học của BIM, định nghĩa như một MVD của IFC và có dạng bảng tính (19 bảng); dùng bàn giao sang CMMS. Digital twin nối BIM với dữ liệu IoT chủ yếu qua khoá ID (GUID). 7D ở đây = FM; một số nguồn định nghĩa khác (xem `dimensions-overview.md`).
- **Độ tin cậy**: trung bình — COBie khá rõ qua NIBS/NBS; ánh xạ COBie↔IFC chi tiết chỉ lấy từ nguồn thứ cấp; ISO 19650-3 chưa đọc văn bản gốc.

## Chi tiết

### COBie
- Định nghĩa NIBS: tập con của BIM, dữ liệu phi đồ hoạ, định nghĩa là MVD của IFC, cũng biểu diễn dạng spreadsheet; giao ở các mốc dự án, đầy đủ khi bàn giao; mục đích giảm/loại độ trễ giữa bàn giao và lúc FM vận hành được.
- Có COBie v3 (NIBS; bản tóm tắt buildingSMART còn là DRAFT 06/2022). Khác biệt so với v2.4: chưa xác minh.
- Cấu trúc bảng (slide ĐH Charlotte): 19 bảng, gom nhóm tổng quát, không gian (Level, Zone, SpaceType, Space, Coordinate...) và tài sản (Type, Component, System, Attribute...). Bentley liệt kê bảng bắt buộc: Contact, Facility, Floor, Space, Type, Component; có điều kiện: Zone, Attribute.
- Ánh xạ sang IFC (nguồn thứ cấp, cần đối chiếu bảng NIBS "COBie V3 IFC"): Facility ↔ IfcBuilding trong IfcProject/IfcSite (IfcFacility có ở IFC4.3 nhưng COBie dùng IfcBuilding); Floor ↔ IfcBuildingStorey; Space ↔ IfcSpace; Zone ↔ IfcZone; Type ↔ các IfcElementType; Component ↔ IfcElement occurrence; System ↔ IfcSystem.
- Pset liên quan (bảng NIBS): bảo hành → `Pset_Warranty` (WarrantyStartDate, WarrantyGuarantorLabor...); `Pset_ServiceLife.ServiceLifeDuration` ↔ COBie ExpectedLife; `Pset_ManufacturerTypeInformation` cho thông tin nhà sản xuất/model. Tên thuộc tính thay đổi theo phiên bản (vd. WarrantyPeriod đổi kiểu ở IFC4 ADD2).
- Anh: Phụ lục quốc gia BS EN ISO 19650-2 (01/2019) nêu thông tin phi hình học nên cấu trúc theo COBie.

### ISO 19650-3 và AIM
Theo một nguồn thực hành (thứ cấp): Part 3 quản lý thông tin giai đoạn vận hành, gồm AIR, bàn giao từ giai đoạn delivery, và tích hợp FM/CAFM/CMMS; AIM hình thành từ PIM khi bàn giao. Chưa xác minh với văn bản ISO/BSI. Nguồn tìm thấy về trang ISO 19650-3 ghi nhãn không khớp, không dùng.

### Digital twin và FM
- Nghiên cứu smart campus (arXiv 2512.12149): mỗi phần tử Revit có GUID khớp với bản ghi trong kho dữ liệu cảm biến; dữ liệu qua Wi-Fi/MQTT lên gateway/cloud; nền tảng như Autodesk Tandem hoặc Azure Digital Twins.
- Demonstrator Cambridge: kết hợp IFC, dữ liệu BMS, quản lý không gian, IoT thời gian thực và asset registry.
- Rủi ro: ID bị tái tạo ở công cụ trung gian (xem `guid-linking.md`); CAFM thường không native tuân ISO 19650 nên cần cầu nối (nguồn thứ cấp).
- Trang vendor (iFactory) khẳng định phải ánh xạ cảm biến với GUID — chỉ là marketing, không dùng làm bằng chứng.

### Dữ liệu 7D cần bổ sung vào mô hình
Định danh tài sản (mã tài sản, serial), nhà sản xuất/model, bảo hành, tuổi thọ, lịch bảo trì, hệ thống (System), vị trí (Space/Floor), liên hệ (Contact), tài liệu. Thuộc tính cảm biến/IoT thường sống ngoài IFC (time-series DB), nối bằng GUID.

## Liên quan đến pipeline CAD → BIM → GPKG
- Đây là chiều có nhiều giá trị nhất cho GIS: Space → IMDF `unit`, Floor → `level`, Facility → `building`; Type/Component có thể thành `amenity`/`fixture`/`occupant` hoặc layer riêng (asset points) kèm `asset_id`, `global_id`. COBie Space (tên, mã phòng, diện tích) cung cấp thuộc tính `name`, `ref` OSM. Đề xuất thiết kế — chưa kiểm chứng.
- COBie Coordinate cho phép đặt vị trí; cách dùng với GPKG chưa xác minh.

## Nguồn
- [NIBS — COBie v3](https://www.nibs.org/cobie) — truy cập 2026-11-06
- [buildingSMART — COBie v3 Executive Summary DRAFT](https://www.buildingsmart.org/wp-content/uploads/2022/11/COBie-v3-Standard_Executive-Summary_DRAFT061322.pdf) — truy cập 2026-11-06
- [NIBS — COBie V3 IFC resource](https://www.nibs.org/sites/default/files/docs/40-Resource-COBie-V3_IFC.pdf) — truy cập 2026-11-06
- [NBS — What is COBie](https://www.thenbs.com/knowledge/what-is-cobie) — truy cập 2026-11-06
- [UNC Charlotte — COBie slides](https://bim.charlotte.edu/wp-content/uploads/sites/1263/2025/08/COBie_Slides.pdf) — truy cập 2026-11-06
- [Alberta — COBie guide](https://www.alberta.ca/system/files/tr-tdseriers25-cobie.pdf) — truy cập 2026-11-06
- [Bentley — COBie worksheets](https://DOCS.BENTLEY.COM/LiveContent/web/OpenBuildings Designer Help-v5.1.2/en/GUID-3EEA72DE-7171-4AC9-CF8F-11745EE659BC.html) — truy cập 2026-11-06
- [IFC 4.3 — Pset_Warranty](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/Pset_Warranty.htm) — truy cập 2026-11-06
- [IFC 4.4 dev — Pset_ServiceLife](https://standards.buildingsmart.org/IFC/DEV/IFC4_4/HTML/lexical/Pset_ServiceLife.html) — truy cập 2026-11-06
- [arXiv 2512.12149 — Digital Twin Smart Campus FM](https://arxiv.org/pdf/2512.12149) — truy cập 2026-11-06
- [UCL — From BIM to Digital Twin](https://discovery-pp.ucl.ac.uk/10082757/1/Lu_From%20BIM%20to%20Digital%20Twin_DT%20group.pdf) — truy cập 2026-11-06

## Câu hỏi còn mở
- Khác biệt COBie v3 vs v2.4 và trạng thái phát hành chính thức.
- Bảng ánh xạ COBie↔IFC chính thức (đọc PDF NIBS toàn văn).
- Văn bản ISO 19650-3 gốc; vai trò IfcSensor/IfcActuator/IfcAsset (chưa xác minh).
