# Georeference trong IFC: IfcMapConversion, IfcProjectedCRS, IfcSite

- **Câu hỏi nghiên cứu**: IFC lưu thông tin địa lý thế nào và làm sao biến toạ độ cục bộ thành toạ độ CRS đích (EPSG)?
- **Kết luận ngắn**: IFC4+ dùng `IfcMapConversion` (nguồn: hệ toạ độ model của `IfcGeometricRepresentationContext`; đích: `IfcProjectedCRS`) gồm Eastings/Northings/OrthogonalHeight, XAxisAbscissa/XAxisOrdinate, Scale. Phép biến đổi: scale → quay → tịnh tiến. `IfcSite.RefLatitude/RefLongitude/RefElevation` chỉ là điểm tham chiếu thô.
- **Độ tin cậy**: trung bình — tên thuộc tính khớp nhiều nguồn; công thức và chi tiết `SourceCRS` ở mức tóm tắt.

## Chi tiết

### IfcMapConversion (IFC4.3)
- Kế thừa `IfcCoordinateOperation` (có `SourceCRS`, `TargetCRS`). Rule: `TargetCRS` phải là `IfcProjectedCRS`. [S1]
- Attribute: `Eastings`, `Northings`, `OrthogonalHeight` (IfcLengthMeasure, bắt buộc); `XAxisAbscissa`, `XAxisOrdinate`, `Scale` (IfcReal, optional). [S1]
- Phép biến đổi: scale (một hệ số `Scale` cho cả x,y,z, dùng đổi đơn vị) → quay (góc θ = arctan(XAxisOrdinate / XAxisAbscissa)) → tịnh tiến (Eastings, Northings, OrthogonalHeight). `IfcMapConversionScaled` là subtype cho phép scale khác nhau theo trục. [S1]
- Ví dụ thật (mẫu IfcOpenShell, Sydney): Eastings 334871.85, Northings 6252295.02, OrthogonalHeight 12.0, XAxisAbscissa 2.59808, XAxisOrdinate -1.5, Scale 1.0, trỏ tới `IfcProjectedCRS` tên `EPSG:7856`. Lưu ý (2.59808, -1.5) không chuẩn hoá (độ dài 3.0) — nên chuẩn hoá khi dùng; **chưa xác minh** quy ước chuẩn hoá. [S1]
- Công thức dạng ma trận: E = Scale·(x·a − y·b) + Eastings; N = Scale·(x·b + y·a) + Northings; H = z·Scale + OrthogonalHeight, với (a,b) = (XAxisAbscissa, XAxisOrdinate) chuẩn hoá. Đây là suy ra từ mô tả "scale→rotate→translate" — **chưa đối chiếu** trực tiếp với trang spec; nên kiểm bằng `ifcopenshell.util.geolocation`.

### IfcProjectedCRS
- Kế thừa `IfcCoordinateReferenceSystem`: `Name`, `Description`, `GeodeticDatum` (IFC4.3: optional; IFC4: bắt buộc). Riêng `IfcProjectedCRS`: `VerticalDatum`, `MapProjection` (ví dụ UTM, Gauss-Krueger), `MapZone` (ví dụ 32 cho UTM32), `MapUnit` (`IfcNamedUnit`, phải là đơn vị độ dài). [S2]
- Các trường này không đủ định nghĩa phép chiếu đầy đủ; thực tế đặt mã EPSG vào `Name` (ví dụ "EPSG:7856"). [S1][S3]
- Dự án VN: dùng `Name = "EPSG:xxxx"` cho VN-2000 / UTM tương ứng (mã EPSG cụ thể của VN-2000 chưa xác minh trong phiên này — cần tra).

### IfcSite
- `RefLatitude`, `RefLongitude`: optional `IfcCompoundPlaneAngleMeasure` (độ, phút, giây, và phần triệu giây); dấu: bắc dương/nam âm. `RefElevation`: optional length, so với mực nước biển. Docs IFC4x2: lat/long chỉ để tương thích ngược, giả định WGS84 và một `IfcSite` duy nhất. Giá trị thứ tư chia cho 1.000.000. [S4]
- Đây là nguồn dự phòng nếu không có `IfcMapConversion` (độ chính xác thấp, không có hướng).

### IfcOpenShell
- `ifcopenshell.api.georeference`: `add_georeferencing` (thêm entity rỗng), `edit_georeferencing` (điền projected CRS và map conversion), `remove_georeferencing`. [S5]
- `ifcopenshell.util.geolocation.auto_xyz2enh(ifc, x, y, z)` đổi toạ độ cục bộ → E/N/H dựa trên `IfcMapConversion` của file. [S5]
- Với `pyproj`: nếu EPSG đích ≠ 4326, `Transformer.from_crs(<EPSG của IfcProjectedCRS>, 4326, always_xy=True)`.

## Liên quan đến pipeline CAD → BIM → GPKG
1. Đọc `IfcProjectedCRS.Name` (tìm EPSG) + `IfcMapConversion` → hàm local→map.
2. Nhớ đơn vị: geometry iterator IfcOpenShell trả mét; `Eastings/Northings` theo `MapUnit` của CRS (có thể khác đơn vị model) — cần chuẩn hoá. [S6]
3. Nếu không có `IfcMapConversion`: dùng `IfcSite.RefLatitude/Longitude` (độ chính xác thấp) hoặc control points người dùng cung cấp trong config; ghi cảnh báo.
4. Ghi GPKG ở EPSG:4326 (cho IMDF/GeoJSON) và có thể kèm layer CRS địa phương.

## Nguồn
- [S1] IfcMapConversion IFC 4.3.2 — https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcMapConversion.htm ; ifc-georef (Rust) https://docs.rs/crate/ifc-georef/latest/source/src/conversion/map.rs — truy cập 2026-11-06 (qua WebSearch)
- [S2] IfcProjectedCRS IFC 4.3 — https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcProjectedCRS.htm — truy cập 2026-11-06
- [S3] buildingSMART forum, Geolocation in IFC2X3 and IFC4 — https://forums.buildingsmart.org/t/geolocation-standards-in-ifc2x3-and-ifc4/2329 — truy cập 2026-11-06
- [S4] IfcSite (IFC4x2) — https://nibs.org/files/docs/IFC4x2_Bridge/schema/ifcproductextension/lexical/ifcsite.htm — truy cập 2026-11-06
- [S5] IfcOpenShell georeference commits (secondhand) — https://dev.glassvision.dedyn.io/Glassvision/IfcOpenShell/commit/052d6e2254065b8d125b99625078679ed861522d — truy cập 2026-11-06
- [S6] IfcOpenShell geometry processing — https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.7.0/src/ifcopenshell-python/docs/ifcopenshell-python/geometry_processing.rst?plain=true — truy cập 2026-11-06

## Câu hỏi còn mở
- Công thức chính xác và có cần chuẩn hoá (XAxisAbscissa, XAxisOrdinate) — đọc lại spec.
- `SourceCRS` trỏ vào `IfcGeometricRepresentationContext` thế nào, và vai trò `WorldCoordinateSystem`/`TrueNorth` (chưa tìm được nguồn).
- Mã EPSG VN-2000 theo múi, và cách xử lý file IFC2x3 (không có `IfcMapConversion`; thường dùng Pset `ePSet_MapConversion`/`ePSet_ProjectedCRS` — chưa xác minh).
