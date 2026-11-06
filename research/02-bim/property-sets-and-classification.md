# Property Set, Quantity Set và Classification trong IFC

- **Câu hỏi nghiên cứu**: Thuộc tính và phân loại được gắn vào đối tượng IFC thế nào, tên Pset/Qto/property nào dùng được để ánh xạ sang tag OSM/IMDF?
- **Kết luận ngắn**: Pset (`Pset_*Common`) và Qto (`Qto_*BaseQuantities`) là tập thuộc tính chuẩn; phân loại gắn qua `IfcClassification` + `IfcClassificationReference` + `IfcRelAssociatesClassification`. IfcOpenShell đọc bằng `ifcopenshell.util.element.get_psets`.
- **Độ tin cậy**: trung bình — tên entity/Pset có nguồn; danh sách property đầy đủ của `Pset_DoorCommon` chưa xác minh từ nguồn chính thức.

## Chi tiết

### Property Set / Quantity Set
- `Pset_SpaceCommon`: Pset chung cho mọi `IfcSpace`; có property `IsExternal` (Boolean, thiết kế cho ngoại thất; thêm từ IFC4). Bản 4.4 draft còn liệt kê `NetPlannedArea`, `PubliclyAccessible`, `HandicapAccessible` (bản draft, không dùng làm chuẩn). [S1]
- `Qto_SpaceBaseQuantities`: gồm `NetFloorArea` (IfcQuantityArea — tổng diện tích sàn sử dụng net), `Height`, `GrossPerimeter`, `NetPerimeter`, `FinishCeilingHeight`, `FinishFloorHeight` (Qto mới từ IFC4). [S2]
- `Qto_DoorBaseQuantities` (IFC4 ADD2): `Width`, `Height`, `Perimeter`, `Area`. [S3]
- `Pset_DoorCommon`: nguồn thứ cấp (một file JSON không chính thống) liệt kê `IsExternal`, `FireRating`, `ThermalTransmittance`, `Status`, `WaterTightnessRating` — **chưa xác minh** từ spec; cần đọc trang `Pset_DoorCommon`. [S4]
- Các Pset "Common" đều có tiền tố `Pset_` do buildingSMART định nghĩa; Pset do người dùng tự định nghĩa không được dùng tiền tố `Pset_` (quy ước chung; chưa xác minh trích dẫn trực tiếp).
- Đọc bằng IfcOpenShell: `ifcopenshell.util.element.get_psets(element)` trả dict `{tên_pset: {prop: value, ..., 'id': ...}}` (bản mới thêm khoá `id`); `get_pset(element, name, prop=None, should_inherit=True)` khi biết tên (kế thừa từ type nếu `should_inherit`). Phải truyền **một** element, không phải list. [S5]

### Classification
- `IfcClassification`: định danh hệ phân loại (ví dụ Omniclass, Uniclass, Masterformat, DIN277). Inverse: `ClassificationForObjects` → `IfcRelAssociatesClassification`, `HasReferences` → `IfcClassificationReference`. [S6]
- `IfcClassificationReference`: trỏ tới một mã (notation/key) cụ thể; `ReferencedSource` có thể là `IfcClassification` hoặc `IfcClassificationReference` cha (dựng phân cấp). Ví dụ trong spec: notation Uniclass "L6814" (Tanking). [S6]
- `IfcRelAssociatesClassification`: gắn classification/reference vào đối tượng. Có hai cách mô tả hệ: nhúng cả phân cấp hoặc chỉ tham chiếu bằng key/id. [S6]
- Hệ thống tên thường gặp: Uniclass 2015, OmniClass, UniFormat (PRIMARY_OBJECTIVE). IfcOpenShell API có `classification.add_classification`; Bonsai map Name/Source/Edition (ví dụ "Uniclass 2015", "NBS", "1.8"). [S6]
- `bSDD` (buildingSMART Data Dictionary) là nguồn thuật ngữ cho classification trong IDS/Solibri. [S7]

## Liên quan đến pipeline CAD → BIM → GPKG
- Ánh xạ `unit.category` (IMDF) / `indoor=*` (OSM) có thể dựa vào: `IfcSpace.PredefinedType`, `ObjectType`, `LongName`, và `IfcClassificationReference.Identification` (nếu file có Uniclass/OmniClass).
- `Qto_SpaceBaseQuantities.NetFloorArea` có thể đối chiếu với diện tích tính lại từ polygon (kiểm tra chất lượng).
- `Pset_*Common.IsExternal` → cờ `outdoor`/loại bỏ khỏi indoor map.
- Lưu toàn bộ Pset dạng JSON trong cột `tags`/`properties` của GPKG (giữ nguyên tên `Pset.Property`).

## Nguồn
- [S1] Pset_SpaceCommon IFC 4.3 — https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/Pset_SpaceCommon.htm — truy cập 2026-11-06 (qua WebSearch)
- [S2] Qto_SpaceBaseQuantities — https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Qto_SpaceBaseQuantities.htm — truy cập 2026-11-06
- [S3] Qto_DoorBaseQuantities IFC4 ADD2 — https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2/HTML/schema/ifcsharedbldgelements/qset/qto_doorbasequantities.htm — truy cập 2026-11-06
- [S4] (thứ cấp, độ tin cậy thấp) https://huggingface.co/spaces/Ifcstudio/rutasyhospitales/blob/main/Arquitectura_DD.json — truy cập 2026-11-06
- [S5] ifcopenshell util/element.py — https://github.com/IfcOpenShell/IfcOpenShell/blob/2a22acfdc936bc9ed6d2ff0ec36e76287da08d56/src/ifcopenshell-python/ifcopenshell/util/element.py ; OSArch https://community.osarch.org/discussion/642/ — truy cập 2026-11-06
- [S6] IfcClassification / IfcClassificationReference IFC 4.3 — https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcClassification.htm , https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcClassificationReference.htm — truy cập 2026-11-06
- [S7] Solibri IDS help — https://help.solibri.com/hc/en-us/articles/39702217779223 — truy cập 2026-11-06

## Câu hỏi còn mở
- Danh sách property chính thức của `Pset_DoorCommon`, `Pset_WallCommon` (có `Reference`?), `Pset_BuildingStoreyCommon` — cần đọc spec.
- Revit/ArchiCAD xuất Pset tuỳ chỉnh thế nào (tên Pset không chuẩn) và cách chuẩn hoá.
