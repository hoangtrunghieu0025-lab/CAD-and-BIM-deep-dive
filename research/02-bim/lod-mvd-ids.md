# LOD/LOI, MVD và IDS

- **Câu hỏi nghiên cứu**: Ba khái niệm LOD/LOI (LOIN), MVD và IDS khác nhau thế nào và dùng ra sao để xác định/kiểm tra IFC đầu vào cho pipeline?
- **Kết luận ngắn**: LOIN (ISO 7817-1) là khung "cần thông tin gì" (hình học + thông tin chữ số); MVD là tập con schema IFC cho một kịch bản trao đổi (gắn với một phiên bản IFC, định dạng mvdXML); IDS là file XML máy đọc được để kiểm tra model có đáp ứng yêu cầu thông tin hay không — phù hợp nhất để kiểm đầu vào của pipeline.
- **Độ tin cậy**: IDS **cao** (đã đọc `ids.xsd` 1.0.0 gốc trên GitHub buildingSMART, TASK-012); MVD/LOIN/IDM vẫn **trung bình** (chưa đọc văn bản gốc; ISO 7817-1 trả phí).

## Chi tiết

### LOD / LOI / LOIN
- ISO 7817-1:2024 (trước đó BS EN 17412-1:2020, đã rút) định nghĩa Level of Information Need; nội dung chính là hai nhóm thông tin: hình học (LOD) và chữ số/phi hình học (LOI). Khung này khuyến khích mô tả cụ thể nhu cầu thông tin thay vì nhãn đơn giản LOD/LOG/LOI. Phần 2 (hướng dẫn) và 3 (schema máy đọc) còn đang phát triển tại thời điểm nguồn viết. [S1][S2]
- BIMForum LOD Specification (bản 2024, Part I) là tài liệu tham chiếu cho phần hình học (LOD 100–500 theo thông lệ Mỹ; mức số cụ thể không trích ở nguồn đã đọc — chưa xác minh). [S1]
- Ý nghĩa với pipeline: model từ CAD→BIM đạt LOD thấp (chỉ footprint + cao độ) vẫn đủ cho indoor map; cần xác định tối thiểu: `IfcBuildingStorey` + `IfcSpace` có hình học + tên/mã phòng.

### MVD (Model View Definition)
- MVD là tập con của schema IFC, đặc tả yêu cầu cho một kịch bản trao đổi; luôn gắn với một phiên bản IFC (IFC2x3, IFC4). Cơ sở dữ liệu MVD ở technical.buildingsmart.org. [S3]
- Định dạng hình thức hoá: mvdXML (bản mới nhất 1.1, 2016) gồm model view, exchange requirement, concept template. [S3][S4]
- IFC4 Reference View (RV 1.2, mvdXML): biểu diễn hình học/quan hệ đơn giản hoá để phối hợp thiết kế, receiver không sửa model. IFC4 Design Transfer View (DTV 1.1, bản draft): chuyển giao dữ liệu hình học nâng cao một chiều. MVD khác nhau (vd IFC4precast) không tương thích với Reference View. [S3]
- IDM (Information Delivery Manual): chưa xác minh trong phiên này (nguồn chỉ nhắc MVD). 

### IDS (Information Delivery Specification)
- File XML (schema `ids.xsd` do buildingSMART công bố; phiên bản 1.0) gồm các *specification*, mỗi cái có phần *applicability* (áp dụng cho phần tử nào) và *requirements* (phần tử phải có gì). [S5][S6]
- Sáu loại facet: `entity`, `attribute`, `classification`, `property`, `material`, `partOf` — **đã xác minh** từ `ids.xsd` (xs:element tương ứng trong `applicabilityType`). Entity facet: IFC Class + Predefined Type; attribute: Name + Value; classification: System + Value (`system` bắt buộc, `value` tuỳ chọn); property: propertySet + baseName + value. Phần tử gốc `<ids>` gồm `info` (có `title` bắt buộc) và `specifications`; mỗi `specification` có `ifcVersion` (bắt buộc, danh sách trong `IFC2X3`, `IFC4`, `IFC4X3_ADD2`), `applicability` và `requirements` (tuỳ chọn). Tên miền giá trị có thể kiểm với bSDD. [S5][S6]
- Khẳng định "IDS 1.0 chỉ cho một entity facet trong applicability": **ĐÚNG** theo `ids.xsd` 1.0.0 — `applicabilityType` có `entity minOccurs=0` (tối đa 1) cùng các facet khác `maxOccurs=unbounded`; requirements: entity facet không có cardinality. [S5]
- Công cụ: Solibri IDS Editor; thư viện `ifctester` của IfcOpenShell (chưa xác minh trong phiên này).

## Liên quan đến pipeline CAD → BIM → GPKG
- Viết một IDS tối thiểu cho "IFC đủ điều kiện sang indoor GPKG": có `IfcBuildingStorey` (attribute `Name`, `Elevation`), `IfcSpace` (attribute `Name`/`LongName`, Pset `Pset_SpaceCommon`), `IfcDoor`; model có `IfcMapConversion` + `IfcProjectedCRS` (kiểm bằng script, vì IDS tập trung vào property/attribute).
- Khi tự sinh IFC từ CAD, nhắm tới Reference View (hình học đơn giản) là đủ.

## Kết quả xác minh (TASK-012, claude-laptop, 2026-11-06)
| Khẳng định | Kết quả | Cách kiểm |
|---|---|---|
| IDS có 6 facet: entity, attribute, classification, property, material, partOf | ĐÚNG | `https://raw.githubusercontent.com/buildingSMART/IDS/development/Schema/ids.xsd` (version="1.0.0") |
| Applicability chỉ có tối đa 1 entity facet | ĐÚNG | cùng XSD |
| IDS hỗ trợ IFC2X3, IFC4, IFC4X3_ADD2 | ĐÚNG (enum `ifcVersion`) | cùng XSD |
| Thư viện `ifctester` của IfcOpenShell | CHƯA XÁC MINH (chưa cài trong venv; không có trong `requirements.txt`) | — |
| LOIN/ISO 7817-1, BIMForum LOD, mvdXML 1.1, IDM | CHƯA XÁC MINH (nguồn trả phí/chưa đọc) | — |

## Nguồn
- [S1] BIMplus: ISO 7817 LOIN — https://bimplus.co.uk/new-level-of-information-need-standard-published — truy cập 2026-11-06
- [S2] BIMForum, Level of Information Need and LOD — https://bimforum.org/event/level-of-information-need-and-lod/ — truy cập 2026-11-06
- [S3] buildingSMART MVD — https://technical.buildingsmart.org/?p=68 ; MVD Database https://technical.buildingsmart.org/standards/ifc/mvd/mvd-database/ — truy cập 2026-11-06
- [S4] mvdXML repo — https://github.com/buildingSMART/mvdXML — truy cập 2026-11-06
- [S5] van Berlo 2023, IDS — https://repositum.tuwien.at/bitstream/20.500.12708/189486/1/van%20Berlo-2023-IDS%20%20Information%20Delivery%20Specification-vor.pdf ; IDS MCP design https://glama.ai/mcp/servers/@vinnividivicci/ifc-ids-mcp/blob/198583a8916c9d036fdcefd919e661ba0d5dffdb/DESIGN_SPECIFICATION.md — truy cập 2026-11-06
- [S6] Solibri IDS — https://help.solibri.com/hc/en-us/articles/39702217779223 — truy cập 2026-11-06

## Câu hỏi còn mở
- Số hiệu IDS phiên bản mới nhất (1.0 hay mới hơn tại 2026-11) và trạng thái chuẩn hoá — chưa xác minh.
- IDM (ISO 29481) liên hệ ra sao với MVD/IDS.
- Có MVD cho IFC4.3 không (chưa xác minh).
