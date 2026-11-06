# Georeference trong IFC: IfcMapConversion, IfcProjectedCRS, IfcSite

- **Câu hỏi nghiên cứu**: IFC lưu thông tin địa lý thế nào và làm sao biến toạ độ cục bộ thành toạ độ CRS đích (EPSG)?
- **Kết luận ngắn**: IFC4+ dùng `IfcMapConversion` (nguồn: hệ toạ độ model của `IfcGeometricRepresentationContext`; đích: `IfcProjectedCRS`) gồm Eastings/Northings/OrthogonalHeight, XAxisAbscissa/XAxisOrdinate, Scale. Phép biến đổi: scale → quay → tịnh tiến. `IfcSite.RefLatitude/RefLongitude/RefElevation` chỉ là điểm tham chiếu thô.
- **Độ tin cậy**: cao sau TASK-012 cho thuộc tính và công thức (kiểm bằng schema `ifcopenshell 0.9.0.post1` và chạy `util.geolocation`); trang spec buildingSMART trả 403 với `curl` nên không đọc trực tiếp. Mục "chưa xác minh" ở cuối.

## Chi tiết

### IfcMapConversion (IFC4.3)
- Kế thừa `IfcCoordinateOperation` (có `SourceCRS`, `TargetCRS`, cả hai REQUIRED). Rule: `TargetCRS` phải là `IfcProjectedCRS`. **Đã xác minh**: với file đã georeference, `SourceCRS` là `IfcGeometricRepresentationContext` (context Model), `TargetCRS` là `IfcProjectedCRS`. [S1]
- Attribute: `Eastings`, `Northings`, `OrthogonalHeight` (IfcLengthMeasure, bắt buộc); `XAxisAbscissa`, `XAxisOrdinate`, `Scale` (IfcReal, optional). [S1]
- Phép biến đổi: scale (một hệ số `Scale` cho cả x,y,z, dùng đổi đơn vị) → quay (góc θ = arctan(XAxisOrdinate / XAxisAbscissa)) → tịnh tiến (Eastings, Northings, OrthogonalHeight). `IfcMapConversionScaled` là subtype cho phép scale khác nhau theo trục (**đã xác minh tồn tại trong IFC4X3_ADD2, không có trong IFC4**). [S1]
- Ví dụ thật (mẫu IfcOpenShell, Sydney): Eastings 334871.85, Northings 6252295.02, OrthogonalHeight 12.0, XAxisAbscissa 2.59808, XAxisOrdinate -1.5, Scale 1.0, trỏ tới `IfcProjectedCRS` tên `EPSG:7856`. Lưu ý (2.59808, -1.5) không chuẩn hoá (độ dài 3.0). **Đã xác minh**: `ifcopenshell.util.geolocation.auto_xyz2enh` **chuẩn hoá** cặp này khi tính (khớp công thức bên dưới với (a,b) chuẩn hoá, không khớp bản chưa chuẩn hoá). [S1]
- Công thức dạng ma trận: E = Scale·(x·a − y·b) + Eastings; N = Scale·(x·b + y·a) + Northings; H = z·Scale + OrthogonalHeight, với (a,b) = (XAxisAbscissa, XAxisOrdinate) chuẩn hoá. **Đã xác minh bằng thực nghiệm** (ifcopenshell 0.9.0.post1): với Eastings 334871.85, Northings 6252295.02, (a,b)=(2.59808,-1.5), Scale 1: điểm (10,0) → (334880.5103, 6252290.02), (0,10) → (334876.85, 6252303.6803), (10,5) → (334883.0103, 6252294.3501) — khớp tới 4 chữ số thập phân với công thức có chuẩn hoá. Chưa kiểm khi `Scale≠1`, hay khi đơn vị model khác mét.

### IfcProjectedCRS
- Kế thừa `IfcCoordinateReferenceSystem`: `Name`, `Description`, `GeodeticDatum` (**đã xác minh**: OPTIONAL ở cả IFC4 và IFC4X3_ADD2 trong schema bundled của ifcopenshell; ghi chú cũ "IFC4: bắt buộc" **không đúng với schema này**). `Name` là REQUIRED trong IFC4 nhưng **OPTIONAL trong IFC4X3_ADD2**; `VerticalDatum` thuộc `IfcCoordinateReferenceSystem` ở IFC4 nhưng chuyển xuống `IfcProjectedCRS` ở 4.3. Riêng `IfcProjectedCRS`: `VerticalDatum`, `MapProjection` (ví dụ UTM, Gauss-Krueger), `MapZone` (ví dụ 32 cho UTM32), `MapUnit` (`IfcNamedUnit`, phải là đơn vị độ dài). [S2]
- Các trường này không đủ định nghĩa phép chiếu đầy đủ; thực tế đặt mã EPSG vào `Name` (ví dụ "EPSG:7856"). [S1][S3]
- Dự án VN: dùng `Name = "EPSG:xxxx"` cho VN-2000 / UTM tương ứng (**đã tra** bằng CSDL EPSG v12.029 trong `pyproj 3.8.0`: VN-2000 địa lý `EPSG:4756`; `EPSG:3405` UTM 48N, `EPSG:3406` UTM 49N; TM-3 theo kinh tuyến trục `EPSG:5896`–`5899`, `9205`–`9218` (vd `9210` = TM-3 105-45, `9211` = TM-3 106-00); chưa đối chiếu mã nào dùng cho từng tỉnh).

### IfcSite
- `RefLatitude`, `RefLongitude`: optional `IfcCompoundPlaneAngleMeasure` (độ, phút, giây, và phần triệu giây); dấu: bắc dương/nam âm. `RefElevation`: optional length, so với mực nước biển. Docs IFC4x2: lat/long chỉ để tương thích ngược, giả định WGS84 và một `IfcSite` duy nhất. Giá trị thứ tư chia cho 1.000.000. [S4]
- Đây là nguồn dự phòng nếu không có `IfcMapConversion` (độ chính xác thấp, không có hướng).

### IfcOpenShell
- `ifcopenshell.api.georeference`: `add_georeferencing(file, ifc_class='IfcMapConversion', name='EPSG:3857')`, `edit_georeferencing(file, coordinate_operation=None, projected_crs=None)`, `remove_georeferencing`, ngoài ra `edit_true_north`, `edit_wcs` (**đã xác minh** chữ ký trong 0.9.0). **Lưu ý**: phải `import ifcopenshell.api.georeference` tường minh (module nạp lazy, `ifcopenshell.api.georeference` không tự có sau `import ifcopenshell.api`). [S5]
- `ifcopenshell.util.geolocation.auto_xyz2enh(ifc, x, y, z)` đổi toạ độ cục bộ → E/N/H dựa trên `IfcMapConversion` của file. [S5]
- Với `pyproj`: nếu EPSG đích ≠ 4326, `Transformer.from_crs(<EPSG của IfcProjectedCRS>, 4326, always_xy=True)`.

## Liên quan đến pipeline CAD → BIM → GPKG
1. Đọc `IfcProjectedCRS.Name` (tìm EPSG) + `IfcMapConversion` → hàm local→map.
2. Nhớ đơn vị: geometry iterator IfcOpenShell trả mét; `Eastings/Northings` theo `MapUnit` của CRS (có thể khác đơn vị model) — cần chuẩn hoá. [S6]
3. Nếu không có `IfcMapConversion`: dùng `IfcSite.RefLatitude/Longitude` (độ chính xác thấp) hoặc control points người dùng cung cấp trong config; ghi cảnh báo.
4. Ghi GPKG ở EPSG:4326 (cho IMDF/GeoJSON) và có thể kèm layer CRS địa phương.

## Kết quả xác minh (TASK-012, claude-laptop, 2026-11-06)
| Khẳng định | Kết quả | Cách kiểm |
|---|---|---|
| `IfcMapConversion`: Eastings, Northings, OrthogonalHeight REQUIRED; XAxisAbscissa, XAxisOrdinate, Scale OPTIONAL | ĐÚNG (IFC4 và IFC4X3_ADD2) | schema |
| `IfcProjectedCRS`: MapProjection, MapZone, MapUnit OPTIONAL; thêm VerticalDatum ở 4.3 | ĐÚNG | schema |
| `IfcSite.RefLatitude/RefLongitude` OPTIONAL `IfcCompoundPlaneAngleMeasure`, `RefElevation` OPTIONAL | ĐÚNG | schema |
| Công thức `E = Scale·(x·a' − y·b') + E0`, `N = Scale·(x·b' + y·a') + N0`, `H = z·Scale + OrthogonalHeight`, (a',b') chuẩn hoá | ĐÚNG với Scale=1 (khớp `auto_xyz2enh` ≤ 1e-4) | chạy |
| `pyproj.Transformer.from_crs("EPSG:32648","EPSG:4326",always_xy=True)` dùng được | ĐÚNG (chạy; kết quả (102.325, 56.386) cho giá trị Sydney đặt nhầm zone, chỉ để thử API) | chạy |
| Mã EPSG VN-2000 | ĐÃ TRA (xem trên) | `pyproj.database.query_crs_info` |
| IFC2X3 dùng `ePSet_MapConversion`/`ePSet_ProjectedCRS` | CHƯA XÁC MINH (không có trong schema IFC2X3 của ifcopenshell; là Pset quy ước) | — |
| Vai trò `WorldCoordinateSystem`/`TrueNorth`; `Scale` ≠ 1 và đơn vị model ≠ mét | CHƯA XÁC MINH | — |

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
