# Khoá liên kết GUID (IfcGloballyUniqueId) và nối 3D với 4D/5D/7D/GIS

- **Câu hỏi nghiên cứu**: GUID là gì, nối 3D với 4D/5D/7D/GIS thế nào, rủi ro mất ổn định?
- **Kết luận ngắn**: `IfcGloballyUniqueId` là chuỗi 22 ký tự mã hoá số 128-bit, giữ ở `IfcRoot.GlobalId`; làm khoá nối. 4D nối qua `IfcRelAssignsToProcess`, 5D qua `IfcRelAssignsToControl`, 7D/IoT qua bảng ngoài có cột GUID. GUID có thể đổi khi công cụ tạo lại; cần quy ước lưu GUID bền.
- **Độ tin cậy**: cao cho chuyển đổi GUID↔UUID (đã chạy thật bằng `ifcopenshell.guid`, TASK-012); độ ổn định GUID của Revit/Unity và phần GIS/IMDF vẫn trung bình / đề xuất.

## Chi tiết

### Định dạng
- GUID 128-bit, kiểu `IfcGloballyUniqueId`, chuỗi cố định 22 ký tự, bảng 64 ký tự `0-9A-Za-z_$`. Cách mã hoá khác base64 thông dụng: byte đầu chiếm 2 ký tự, các byte sau nhóm 3 byte → 4 ký tự; vì vậy ký tự đầu chỉ là 0–3. Lịch sử: R1.5.1 dùng 20 ký tự (base-85), R2x chuyển 22 ký tự (base64).
- Thuộc tính `GlobalId` của `IfcRoot` mang kiểu này (theo trang spec là "được tham chiếu bởi IfcRoot"). Mọi entity kế thừa IfcRoot (sản phẩm, quan hệ, task, cost item...) đều có GlobalId. Thư viện `ifcopenshell.guid` chuyển 22-char ↔ UUID: **đã xác minh** — `guid.expand(gid)` trả chuỗi hex **32 ký tự không có dấu gạch**, `uuid.UUID(hex=guid.expand(gid))` cho UUID chuẩn, `guid.compress(hex)` đảo ngược đúng; `guid.new()` sinh GUID mới. Ví dụ: `1TGflo42n9vRyAeKkmV_BN` → `5d429bf2102c49e5bf0aa14bb07fe2d7` → `5d429bf2-102c-49e5-bf0a-a14bb07fe2d7`.
- IMDF yêu cầu `id` dạng UUID (FEATURE-ID = UUID, **đã xác minh** từ spec IMDF); IFC GUID giải mã được sang UUID 128-bit (cách trên). Lưu ý: UUID suy từ `expand` không nhất thiết là UUID phiên bản 4 hợp lệ về bit version; để UUID chuẩn và ổn định có thể dùng `uuid5(namespace, GlobalId)` (**đã xác minh** `uuid5` cho kết quả ổn định giữa các lần chạy).

### Cách nối
| Chiều | Phía "3D" | Phía mở rộng | Khoá nối |
|---|---|---|---|
| 4D | IfcProduct.GlobalId | IfcTask, TaskTime | `IfcRelAssignsToProcess` (RelatedObjects → RelatingProcess); hoặc bảng task↔GlobalId |
| 5D | IfcElement (+ Qto) | IfcCostItem | `IfcRelAssignsToControl`; hoặc bảng BoQ có cột GlobalId |
| 6D | IfcSpace/IfcElement/IfcMaterial | kết quả mô phỏng/LCA | bảng ngoài theo GlobalId (đề xuất) |
| 7D | IfcElement/IfcSpace | COBie Component/Space, bản ghi CMMS, sensor | cột GUID/ExternalIdentifier trong bảng tài sản (COBie còn có trường ID riêng — chưa xác minh) |
| GIS | IfcBuilding/Storey/Space | feature GPKG/IMDF | cột `global_id` + `id` UUID ổn định |

### Rủi ro ổn định
- Revit: IFC GUID dẫn xuất từ `UniqueId` của element; Revit hướng tới GUID nhất quán giữa các lần export; undo xoá có thể đổi UniqueId nên đổi GUID. Có tuỳ chọn lưu IFC GUID vào parameter để tái dùng ở lần export sau; không thể chỉ định UniqueId tuỳ ý.
- Game engine/công cụ trung gian: nghiên cứu Preprints (2025) nêu GUID bị sinh lại khi file `.meta` của Unity mất.
- Sửa mô hình có thể tách/gộp element → GUID mới; quan hệ 4D/5D/7D phải có quy trình rà soát (đề xuất).
- Trong pipeline CAD→BIM của dự án, CAD không có GUID: phải sinh GUID ổn định (vd. UUID v5 từ tên dự án + layer + handle DXF — đề xuất) để chạy lại ra cùng ID.

### Georeference làm khoá nối không gian
`IfcMapConversion` (Eastings, Northings, OrthogonalHeight, XAxisAbscissa/Ordinate, Scale) + `IfcProjectedCRS` (EPSG) chuyển toạ độ cục bộ sang CRS chiếu. Lưu ý: góc xoay suy từ true north có thể lệch do biến dạng bản đồ; scale cần ≥2 điểm; BIM Fit Check (buildingSMART DE) chỉ ra IFC thiếu hướng dẫn chọn IfcMapConversion vs IfcRigidOperation và `IfcProjectedCRS` chỉ có VerticalDatum dạng text tự do.

## Liên quan đến pipeline CAD → BIM → GPKG
- Mỗi layer GPKG nên có cột `global_id` (IFC 22-char) và `id` (UUID) để quay về IFC, nối bảng 4D/5D/7D phi hình học.
- Cần cấu hình georeference tường minh; nếu IFC thiếu IfcMapConversion thì dùng control points.

## Kết quả xác minh (TASK-012, claude-laptop, 2026-11-06)
| Khẳng định | Kết quả | Cách kiểm |
|---|---|---|
| GlobalId dài 22 ký tự | ĐÚNG (`ifcopenshell.guid.new()` → 22 ký tự) | chạy |
| Ký tự đầu chỉ 0–3 | KHÔNG KIỂM (mẫu một giá trị bắt đầu `1`) | — |
| `IfcRelAssignsToProcess` (4D), `IfcRelAssignsToControl` (5D) làm khoá nối | ĐÚNG về entity | schema |
| Revit giữ GUID qua export, Unity `.meta`, BIM Fit Check | CHƯA XÁC MINH | — |

## Nguồn
- [IFC4.1 — IfcGloballyUniqueId](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_1/FINAL/HTML/schema/ifcutilityresource/lexical/ifcgloballyuniqueid.htm) — truy cập 2026-11-06
- [IFC 4.3 — IfcGloballyUniqueId](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcGloballyUniqueId.htm) — truy cập 2026-11-06
- [Autodesk — Unique Id and IFC GUID](https://blog.autodesk.io/unique-id-and-ifc-guid/) — truy cập 2026-11-06
- [Autodesk — Consistency of IFC GUID and UniqueId](https://blog.autodesk.io/consistency-of-ifc-guid-and-uniqueid/) — truy cập 2026-11-06
- [Preprints — IfcGUID study](https://www.preprints.org/frontend/manuscript/d4b00d4875eb9e128e889191f16c0b9a/download_pub) — truy cập 2026-11-06
- [IfcGref TU Delft](https://ifcgref.bk.tudelft.nl/templates/guid.html) — truy cập 2026-11-06
- [BIMcollab — IFC world coordinates](https://helpcenter.bimcollab.com/en/articles/326917-coordinating-ifc-models-with-world-coordinate-system-information) — truy cập 2026-11-06
- [buildingSMART DE — BIM Fit Check georeferencing](https://programm.dvw.de/intergeo-agenda-en/ergebnisse-des-buildingsmart-bim-fit-check-zur-georeferenzierung-und-trassierung) — truy cập 2026-11-06

## Câu hỏi còn mở
- Hàm chuyển GUID↔UUID trong ifcopenshell và quy ước UUID cho IMDF.
- COBie có lưu GlobalId/ExternalIdentifier trong bảng nào (chưa xác minh).
- ArchiCAD/khác có ổn định GUID như Revit không.
