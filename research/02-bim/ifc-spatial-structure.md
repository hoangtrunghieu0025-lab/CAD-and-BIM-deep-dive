# Cấu trúc không gian IFC: IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace

- **Câu hỏi nghiên cứu**: IFC tổ chức cây không gian thế nào, quan hệ nào gắn Space/Door vào tầng, và lấy footprint 2D của `IfcSpace`/`IfcDoor` theo từng tầng ra sao?
- **Kết luận ngắn**: Cây không gian dựng bằng `IfcRelAggregates` (Project → Site → Building → BuildingStorey → Space); phần tử vật lý (tường, cửa…) gắn vào tầng bằng `IfcRelContainedInSpatialStructure`. Footprint 2D lấy từ representation có `RepresentationIdentifier` = `FootPrint` nếu có, nếu không thì phải tự chiếu/cắt hình học `Body` (đề xuất của dự án, không phải quy định của chuẩn).
- **Độ tin cậy**: trung bình. Tên class/thuộc tính có nguồn qua kết quả tìm kiếm trích đoạn từ trang spec buildingSMART; không fetch trực tiếp được trang spec (host `*.buildingsmart.org` bị chặn trong môi trường này) nên các chi tiết đánh dấu "chưa xác minh" cần kiểm lại.

## Chi tiết

### 1. Cây phân rã không gian (IFC4.3)
- Dạng đơn giản nhất từ cao xuống thấp: `IfcProject` → `IfcSite` → `IfcFacility` (hoặc subtype) → `IfcFacilityPart` → `IfcSpace`. `IfcSite`, `IfcFacilityPart`, `IfcSpace` là tuỳ chọn; với toà nhà `IfcBuildingStorey` thay cho `IfcFacilityPart`. [S1]
- IFC4.3 thêm `IfcFacility` với các subtype `IfcBridge`, `IfcBuilding`, `IfcMarineFacility`, `IfcRailway`, `IfcRoad` và `IfcFacilityPart` trừu tượng (`IfcBridgePart`, `IfcFacilityPartCommon`...). `IfcBuilding` vẫn là subtype của `IfcFacility` — nghĩa là pipeline nên chấp nhận cả `IfcBuilding` lẫn `IfcFacility` tổng quát. [S1]
- Quan hệ dựng cây: `IfcRelAggregates` (1-n, nối đúng hai cấp liền kề; cấp cao nhất gắn với `IfcProject` bằng `IfcRelAggregates`; cấu trúc phải không vòng). Theo bảng "General Usage" của trang Spatial Decomposition, `IfcBuilding` có thể chứa `IfcBuildingStorey` và `IfcSpace`; `IfcSite` có thể chứa `IfcBuilding`, `IfcFacility`… [S1]
- `IfcSpatialZone`: vùng chức năng/đa ngành, đưa vào cây bằng `IfcRelContainedInSpatialStructure` (và có thể aggregate). [S1]
- IFC4: mọi spatial structure element phải được `IfcRelAggregates` với một spatial structure element khác hoặc với `IfcProject`. [S1]

### 2. IfcSpace
- `IfcSpace` kế thừa `IfcSpatialStructureElement` (IFC4; trong IFC4.3 thuộc nhánh `IfcSpatialElement` — chưa xác minh chi tiết supertype 4.3). [S2]
- Spec: space gắn với một building storey (hoặc với site nếu là không gian ngoài trời) và đóng vai trò container cho các phần tử liên quan. [S2]
- Thuộc tính: `PredefinedType : OPTIONAL IfcSpaceTypeEnum` (nếu `USERDEFINED` thì `ObjectType` phải có; `ObjectType` thường chứa phân loại chức năng); `ElevationWithFlooring : OPTIONAL IfcLengthMeasure` (cao độ mặt sàn hoàn thiện, tương đối với `IfcBuilding.ElevationOfRefHeight`). [S2]
- Inverse: `ContainsElements` → `IfcRelContainedInSpatialStructure`; `IsDecomposedBy` → `IfcRelAggregates`. [S2]
- Tên (`Name`/`LongName`) và số phòng: `Name`/`LongName` là attribute kế thừa của spatial element (chưa xác minh trực tiếp từ spec trong phiên này); `Pset_SpaceCommon` có `IsExternal` (xem `property-sets-and-classification.md`).

### 3. IfcBuildingStorey
- Subtype của `IfcSpatialStructureElement`; có attribute `Elevation` (cao độ tầng) — **chưa xác minh** trong phiên này (trang spec không fetch được; thông tin từ kiến thức chung). Cần kiểm lại tại trang `IfcBuildingStorey` của IFC4.3.
- Dùng `Elevation` (và/hoặc `Name`) để suy ra `level.ordinal`/`short_name` của IMDF.

### 4. Cách lấy footprint 2D của IfcSpace / IfcDoor theo tầng

**Bước chung — gom phần tử theo tầng**
- `IfcSpace`: đi từ `IfcBuildingStorey` qua `IsDecomposedBy` (`IfcRelAggregates`) để lấy các `IfcSpace` con; ngoài ra kiểm tra thêm `ContainsElements` phòng khi file đặt space bằng containment. [S1][S2]
- `IfcDoor`: là phần tử vật lý, thường gắn tầng bằng `IfcRelContainedInSpatialStructure` (`RelatingStructure` = storey). Cửa nằm trong tường qua `IfcRelFillsElement` với `IfcOpeningElement`. [S2][S5]
- Trong IfcOpenShell: dùng `ifcopenshell.util.element` (module chứa các hàm lấy quan hệ phổ biến; tên hàm `get_container` chưa xác minh trong tài liệu) hoặc tự duyệt inverse `IsDecomposedBy` / `ContainsElements`. [S6]

**Footprint IfcSpace**
1. Ưu tiên: tìm trong `Representation.Representations` một `IfcShapeRepresentation` có `RepresentationIdentifier == 'FootPrint'` — spec định nghĩa là "2D Foot print ... projected to ground view". [S3] Dữ liệu thường là curve 2D (`RepresentationType` 'GeometricCurveSet'/'Curve2D' theo implementer agreement CV-2x3-168 cho IFC2x3 — kiểm tra lại cho IFC4/4.3). [S3]
2. Dự phòng: dùng representation `Body` → triangulate bằng `ifcopenshell.geom` với `use-world-coords` → chiếu mọi tam giác xuống XY và `shapely.unary_union`; hoặc cắt ở `z = Elevation_tầng + h` (ví dụ +1.0 m — con số chọn của dự án, không phải của chuẩn) rồi polygonize. [S6][S7]
3. Kết quả là polygon theo toạ độ thế giới của model (đơn vị mét nếu dùng iterator của IfcOpenShell); sau đó áp `IfcMapConversion` (xem `ifc-georeference.md`).
4. Lưu ý: bao quanh phòng có thể có lỗ (cột) → giữ interior rings; space có thể là hình dạng đa tầng (double height) → gán theo storey chứa nó.

**Footprint IfcDoor**
1. Cửa không có footprint "diện tích" ý nghĩa; trong IMDF `opening` là **LineString** đi qua bề dày tường. Cách đề xuất: lấy bounding box 2D của hình học `Body` (hoặc `FootPrint`/`Plan` nếu có) đã ở toạ độ thế giới; trục dài nhất của bbox là đoạn cửa. (Đề xuất của dự án.)
2. Kích thước: `OverallWidth`/`OverallHeight` (IFC4.3: optional; nếu bỏ trống thì lấy theo hình học `IfcOpeningElement` mà cửa lấp). Chiều mở cửa theo trục +y của local placement. `OverallWidth` được quy ước là bề rộng ô mở, không phải cả khuôn. [S5]
3. Local placement của cửa tham chiếu (`PlacementRelTo`) tới placement của opening mà nó lấp (`IfcRelFillsElement`). [S5] → có thể dùng vị trí + hướng từ ma trận placement (`ifcopenshell.util.placement.get_local_placement`) và `OverallWidth` để dựng đoạn thẳng, nhưng placement origin có thể không phải tâm cửa. [S6]
4. Tầng của cửa = storey chứa (containment). Cửa không ở trực tiếp storey (ví dụ lồng trong `IfcElementAssembly`) → leo cây decomposition lên.

## Liên quan đến pipeline CAD → BIM → GPKG
- IMDF `level` ← `IfcBuildingStorey`; `unit` ← `IfcSpace` (polygon); `opening` ← `IfcDoor` (LineString); `building` ← `IfcBuilding` (hoặc `IfcFacility`).
- Khoá ngoại IMDF (`unit.level_id`) lấy từ cây `IfcRelAggregates`/containment; dùng `GlobalId` làm cơ sở sinh UUID ổn định.
- Khi bước CAD → BIM sinh IFC trung gian: phải tạo đủ `IfcProject`→`IfcSite`→`IfcBuilding`→`IfcBuildingStorey`→`IfcSpace` bằng `IfcRelAggregates` và gắn phần tử bằng `IfcRelContainedInSpatialStructure`.

## Nguồn
- [S1] IFC 4.3 Spatial Decomposition / Spatial Composition (buildingSMART) — https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Aggregation/Spatial_Decomposition/content.html — truy cập 2026-11-06 (qua WebSearch, không fetch được trực tiếp)
- [S2] IfcSpace, IFC 4.3.2.0 — https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcSpace.htm ; web-ifc IFC4X3.IfcSpace https://thatopen.github.io/engine_web-ifc/docs/classes/ifc_schema.IFC4X3.IfcSpace.html — truy cập 2026-11-06
- [S3] IfcShapeRepresentation, IFC 4.3 — https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcShapeRepresentation.htm ; CV-2x3-168 — https://standards.buildingsmart.org/documents/Implementation/IFC_Implementation_Agreements/CV-2x3-168.html — truy cập 2026-11-06
- [S5] IfcDoor, IFC 4.3 — https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDoor.htm — truy cập 2026-11-06
- [S6] IfcOpenShell util docs — https://docs.ifcopenshell.org/autoapi/ifcopenshell/util/index.html ; OSArch https://community.osarch.org/discussion/comment/21664/ — truy cập 2026-11-06
- [S7] IfcOpenShell geometry processing — https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.7.0/src/ifcopenshell-python/docs/ifcopenshell-python/geometry_processing.rst?plain=true — truy cập 2026-11-06

## Câu hỏi còn mở
- `IfcBuildingStorey.Elevation` và supertype chính xác của `IfcSpace` trong 4.3 — cần đọc trực tiếp spec.
- Trong các file thực tế (Revit export), `IfcSpace` có `FootPrint` hay chỉ `Body`? Cần thử với file mẫu.
- Space do Revit xuất thường nằm dưới storey bằng `IfcRelAggregates`; có file dùng containment — chưa kiểm chứng.
- Cách xử lý cửa/phần tử nằm ở storey khác với tường (cửa kép tầng).
