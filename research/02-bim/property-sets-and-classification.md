# Property Set, Quantity Set và Classification trong IFC

- **Câu hỏi nghiên cứu**: Thuộc tính và phân loại được gắn vào đối tượng IFC thế nào, tên Pset/Qto/property nào dùng được để ánh xạ sang tag OSM/IMDF?
- **Kết luận ngắn**: Pset (`Pset_*Common`) và Qto (`Qto_*BaseQuantities`) là tập thuộc tính chuẩn; phân loại gắn qua `IfcClassification` + `IfcClassificationReference` + `IfcRelAssociatesClassification`. IfcOpenShell đọc bằng `ifcopenshell.util.element.get_psets`.
- **Độ tin cậy**: cao sau TASK-012 — danh sách property của các Pset/Qto đã trích từ **template chính thức đi kèm `ifcopenshell 0.9.0.post1`** (`ifcopenshell.util.pset.get_template`, bản IFC4 và IFC4X3); phần classification/bSDD chưa kiểm.

## Chi tiết

### Property Set / Quantity Set
- `Pset_SpaceCommon`: Pset chung cho `IfcSpace`. **Đã xác minh** property (giống nhau ở IFC4 và IFC4X3): `Reference`, `IsExternal`, `GrossPlannedArea`, `NetPlannedArea`, `PubliclyAccessible`, `HandicapAccessible` (nên `NetPlannedArea`, `PubliclyAccessible`, `HandicapAccessible` **không phải** chỉ ở bản draft 4.4 như ghi chú cũ). `ApplicableEntity`: `IfcSpace` (IFC4) / `IfcSpatialElement,IfcSpatialElementType` (4.3). [S1]
- `Qto_SpaceBaseQuantities`: **đã xác minh** đủ 13 quantity (IFC4 và 4.3): `Height`, `FinishCeilingHeight`, `FinishFloorHeight`, `GrossPerimeter`, `NetPerimeter`, `GrossFloorArea`, `NetFloorArea`, `GrossWallArea`, `NetWallArea`, `GrossCeilingArea`, `NetCeilingArea`, `GrossVolume`, `NetVolume`. [S2]
- `Qto_DoorBaseQuantities`: `Width`, `Height`, `Perimeter`, `Area` (**đã xác minh**, IFC4 và 4.3). [S3]
- `Pset_DoorCommon`: **đã xác minh** 19 property (IFC4 và 4.3): `Reference`, `Status`, `FireRating`, `AcousticRating`, `SecurityRating`, `DurabilityRating`, `HygrothermalRating`, `WaterTightnessRating`, `MechanicalLoadRating`, `WindLoadRating`, `Infiltration`, `IsExternal`, `ThermalTransmittance`, `GlazingAreaFraction`, `HandicapAccessible`, `FireExit`, `HasDrive`, `SelfClosing`, `SmokeStop`. Danh sách trong nguồn thứ cấp là tập con đúng. [S4]
- Các Pset "Common" đều có tiền tố `Pset_` do buildingSMART định nghĩa; Pset do người dùng tự định nghĩa không được dùng tiền tố `Pset_` (quy ước chung; chưa xác minh trích dẫn trực tiếp).
- Đọc bằng IfcOpenShell: `ifcopenshell.util.element.get_psets(element)` trả dict `{tên_pset: {prop: value, ..., 'id': ...}}` (bản mới thêm khoá `id`); `get_pset(element, name, prop=None, should_inherit=True)` khi biết tên (kế thừa từ type nếu `should_inherit`). Phải truyền **một** element, không phải list. **Đã xác minh chữ ký (0.9.0)**: `get_psets(element, psets_only=False, qtos_only=False, should_inherit=True, verbose=False)` và `get_pset(element, name, prop=None, psets_only=False, qtos_only=False, should_inherit=True, verbose=False)`. [S5]

### Classification
- `IfcClassification`: định danh hệ phân loại (ví dụ Omniclass, Uniclass, Masterformat, DIN277). Inverse: `ClassificationForObjects` → `IfcRelAssociatesClassification`, `HasReferences` → `IfcClassificationReference`. [S6]
- `IfcClassificationReference`: trỏ tới một mã (notation/key) cụ thể; `ReferencedSource` có thể là `IfcClassification` hoặc `IfcClassificationReference` cha (dựng phân cấp). Ví dụ trong spec: notation Uniclass "L6814" (Tanking). [S6]
- `IfcRelAssociatesClassification`: gắn classification/reference vào đối tượng. Có hai cách mô tả hệ: nhúng cả phân cấp hoặc chỉ tham chiếu bằng key/id. [S6]
- Hệ thống tên thường gặp: Uniclass 2015, OmniClass, UniFormat (PRIMARY_OBJECTIVE). IfcOpenShell API có `classification.add_classification(file, classification)`, `add_reference`, `edit_*`, `remove_*` (**đã xác minh** tồn tại); Bonsai map Name/Source/Edition (ví dụ "Uniclass 2015", "NBS", "1.8"). [S6]
- `bSDD` (buildingSMART Data Dictionary) là nguồn thuật ngữ cho classification trong IDS/Solibri. [S7]

## Liên quan đến pipeline CAD → BIM → GPKG
- Ánh xạ `unit.category` (IMDF) / `indoor=*` (OSM) có thể dựa vào: `IfcSpace.PredefinedType`, `ObjectType`, `LongName`, và `IfcClassificationReference.Identification` (nếu file có Uniclass/OmniClass).
- `Qto_SpaceBaseQuantities.NetFloorArea` có thể đối chiếu với diện tích tính lại từ polygon (kiểm tra chất lượng).
- `Pset_*Common.IsExternal` → cờ `outdoor`/loại bỏ khỏi indoor map.
- Lưu toàn bộ Pset dạng JSON trong cột `tags`/`properties` của GPKG (giữ nguyên tên `Pset.Property`).

## Kết quả xác minh (TASK-012, claude-laptop, 2026-11-06)
| Khẳng định | Kết quả | Cách kiểm |
|---|---|---|
| Danh sách property `Pset_SpaceCommon`, `Pset_DoorCommon`, `Qto_SpaceBaseQuantities`, `Qto_DoorBaseQuantities` | ĐÚNG, đầy đủ (xem trên) | `ifcopenshell.util.pset.get_template("IFC4"/"IFC4X3")` |
| `Pset_WallCommon.ThermalTransmittance`, `Qto_WallBaseQuantities.NetSideArea` tồn tại | ĐÚNG | cùng cách; khác biệt tên: IFC4 `GrossFootprintArea`/`NetFootprintArea`, 4.3 `GrossFootPrintArea`/`NetFootPrintArea` (chữ P hoa) |
| `Pset_Warranty`, `Pset_ServiceLife`, `Pset_ManufacturerTypeInformation` tồn tại | ĐÚNG; xem `03-bim-pipeline-3d-7d/7d-facility-management-cobie.md` | cùng cách |
| Quy ước tiền tố `Pset_` chỉ cho buildingSMART | CHƯA XÁC MINH | — |
| `IfcClassification`/`IfcClassificationReference`/`IfcRelAssociatesClassification`, bSDD | CHƯA XÁC MINH trực tiếp (chỉ API tồn tại) | — |

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
