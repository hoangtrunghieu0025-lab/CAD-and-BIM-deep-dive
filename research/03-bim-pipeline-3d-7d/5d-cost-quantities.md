# 5D — Chi phí và khối lượng

- **Câu hỏi nghiên cứu**: Khối lượng và chi phí được lưu/nối vào cấu kiện 3D thế nào?
- **Kết luận ngắn**: Khối lượng lấy từ `IfcElementQuantity` (Qto_* như `Qto_WallBaseQuantities`); chi phí nằm trong `IfcCostSchedule` chứa các `IfcCostItem`, nối với cấu kiện qua `IfcRelAssignsToControl` để tính theo quantity. Công cụ: Revit schedules, IfcOpenShell Ifc5D/Bonsai. Chất lượng quantity từ mesh cần kiểm lại.
- **Độ tin cậy**: cao cho cấu trúc entity và Qto (kiểm bằng schema và template của `ifcopenshell 0.9.0.post1`, TASK-012); công cụ thương mại chưa xác minh.

## Chi tiết

### Dữ liệu thêm ở 5D
Quantity (chiều dài, diện tích, thể tích...), đơn giá, tổng chi phí, cấu trúc phân cấp hạng mục (WBS/BoQ), có thể gắn mã phân loại.

### Class IFC
- `IfcCostSchedule`: gom các `IfcCostItem` — dùng cho dự toán, bảng khối lượng, hoặc nhúng dữ liệu chi phí vào tài liệu khác (vd. work order).
- `IfcCostItem`: IFC4 nêu có thể tính từ quantity của đối tượng qua `IfcRelAssignsToControl`; nguồn quantity có thể là occurrence của IfcElement, IfcTask hoặc IfcResource. Quan hệ: RelatingControl = cost item, RelatedObjects = cấu kiện có quantity được dùng. Cost item lồng nhau qua `IfcRelNests`; cost item tổng hợp gán vào schedule bằng `IfcRelAssignsToControl`.
- IFC2x3 dùng subtype riêng `IfcRelSchedulesCostItems` (⊂ `IfcRelAssignsToControl`); **đã xác minh**: entity này chỉ có ở IFC2X3, **không có** ở IFC4 và IFC4X3_ADD2 (dùng `IfcRelAssignsToControl` trực tiếp).
- Khối lượng: `Qto_WallBaseQuantities` **đã xác minh** (IFC4 và 4.3): `Length`, `Width`, `Height`, `GrossFootprintArea`/`NetFootprintArea` (4.3 viết `...FootPrint...`), `GrossSideArea`, `NetSideArea`, `GrossVolume`, `NetVolume`, `GrossWeight`, `NetWeight`. Định nghĩa tính (trừ opening…) chưa đọc.
- Giá trị tiền: `IfcCostItem` (IFC4/4.3) có `PredefinedType`, `CostValues` (OPTIONAL, dạng danh sách `IfcCostValue`), `CostQuantities` (OPTIONAL); `IfcCostValue` ⊂ `IfcAppliedValue`; `IfcCostSchedule` có `PredefinedType`, `Status`, `SubmittedOn`, `UpdateDate` (**đã xác minh**). IFC2X3 `IfcCostValue` có `CostType` REQUIRED, bị bỏ ở IFC4.

### Công cụ
- IfcOpenShell `Ifc5D`: tiện ích thao tác dữ liệu chi phí với định dạng/báo cáo; commit 2026 cho thấy export ODS/XLSX khớp cột bảng cost của Bonsai (ID, Name, Quantity, Value, Total Cost) và CSV giữ cột bổ sung để `csv2ifc` nhập lại.
- Bonsai/BlenderBIM: thêm `IfcElementQuantity` (thảo luận OSArch).
- Cảnh báo: người dùng BlenderBIM báo NetSideArea tính từ mesh không trừ đúng IfcOpeningElement — nên đối chiếu bằng viewer khác trước khi dùng cho bóc tách.
- CostX, Revit schedules, Vico: có trong PRIMARY_OBJECTIVE; chưa xác minh bằng nguồn riêng.

### Quy trình dữ liệu
Input: IFC có hình học + (hoặc tạo) Qto → bóc khối lượng theo GlobalId → ghép đơn giá (CSDL giá/phân loại) → output: IfcCostSchedule hoặc bảng BoQ (xlsx/csv) có cột GlobalId.

## Liên quan đến pipeline CAD → BIM → GPKG
- Có thể xuất `area` của IfcSpace (Qto_SpaceBaseQuantities — tên Qto chưa xác minh trong phiên này) vào thuộc tính `unit`; chi phí không thuộc IMDF.

## Kết quả xác minh (TASK-012, claude-laptop, 2026-11-06)
| Khẳng định | Kết quả | Cách kiểm |
|---|---|---|
| `IfcCostSchedule`, `IfcCostItem`, `IfcCostValue`, `IfcRelAssignsToControl`, `IfcRelNests` tồn tại và quan hệ như mô tả | ĐÚNG | schema IFC4/IFC4X3_ADD2 |
| `IfcRelSchedulesCostItems` chỉ ở IFC2X3 | ĐÚNG | schema 3 phiên bản |
| `Qto_WallBaseQuantities` có `NetSideArea`, `NetVolume` | ĐÚNG | template |
| Tên Qto cho IfcSpace: `Qto_SpaceBaseQuantities` | ĐÚNG, có `NetFloorArea`, `GrossFloorArea`… (xem `02-bim/property-sets-and-classification.md`) | template |
| BlenderBIM NetSideArea tính từ mesh không trừ IfcOpeningElement | CHƯA XÁC MINH (báo cáo người dùng) | — |
| CostX, Revit schedules, Vico, Ifc5D export xlsx/ods | CHƯA XÁC MINH | — |

## Nguồn
- [IFC4 — IfcCostItem](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcsharedmgmtelements/lexical/ifccostitem.htm) — truy cập 2026-11-06
- [IFC4 — IfcCostSchedule](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcsharedmgmtelements/lexical/ifccostschedule.htm) — truy cập 2026-11-06
- [IFC2x3 — IfcRelSchedulesCostItems](https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ifcsharedmgmtelements/lexical/ifcrelschedulescostitems.htm) — truy cập 2026-11-06
- [IFC 4.3 — Qto_WallBaseQuantities](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/Qto_WallBaseQuantities.htm) — truy cập 2026-11-06
- [IfcOpenShell mirror — ifc5d cost export commit](https://dev.glassvision.dedyn.io/Glassvision/IfcOpenShell/src/commit/e308ecaeb4278a292e7754378ae3dac128c99b5d) — truy cập 2026-11-06
- [OSArch — IfcElementQuantity in BlenderBIM](https://community.osarch.org/discussion/867/) — truy cập 2026-11-06

## Câu hỏi còn mở
- IfcCostValue/IfcAppliedValue và đơn vị tiền tệ; ánh xạ với phân loại (Uniclass/OmniClass).
- Có Qto chuẩn cho IfcSpace và tên chính xác.
