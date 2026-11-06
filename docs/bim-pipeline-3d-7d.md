# Pipeline BIM 3D → 7D

> Tổng hợp từ `research/03-bim-pipeline-3d-7d/` (đã xác minh class IFC bằng schema ifcopenshell 0.9.0.post1, TASK-012).
>
> **Quy ước dự án**: 6D = bền vững/năng lượng, 7D = vận hành & bảo trì (FM). Đây là **quy ước**, không phải định nghĩa thống nhất — xem mục 5 và [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md).

## 1. Bảng chiều → dữ liệu → class IFC → công cụ

| Chiều | Dữ liệu thêm | Class IFC / chuẩn (đã kiểm schema) | Công cụ ví dụ | Nguồn |
|---|---|---|---|---|
| 2D | Hình học phẳng, layer | DWG/DXF (ngoài IFC) | AutoCAD, ezdxf | [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md) |
| 3D | Hình học, vật liệu, Pset, quan hệ không gian | `IfcProject/Site/Building/BuildingStorey/Space`, `IfcRoot.GlobalId` | Revit, ArchiCAD, IfcOpenShell, Bonsai | [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md) |
| 4D | Task, thời lượng, ngày, quan hệ task–cấu kiện | `IfcWorkSchedule`, `IfcTask`, `IfcTaskTime` (IFC4+), `IfcRelAssignsToProcess` | Navisworks TimeLiner, Synchro, MS Project, P6, module IfcOpenShell `util/api.sequence` | [4d-schedule](../research/03-bim-pipeline-3d-7d/4d-schedule.md) |
| 5D | Quantity, đơn giá, tổng chi phí | `IfcCostSchedule`, `IfcCostItem`, `IfcRelAssignsToControl`, `IfcElementQuantity`/`Qto_*BaseQuantities` | Revit schedules, CostX, module IfcOpenShell `util/api.cost`, Bonsai | [5d-cost-quantities](../research/03-bim-pipeline-3d-7d/5d-cost-quantities.md) |
| 6D (bền vững) | Thông số nhiệt, vật liệu, năng lượng, carbon | gbXML (ngoài IFC), `IfcRelSpaceBoundary`, `Pset_WallCommon.ThermalTransmittance`, `Pset_EnvironmentalImpactIndicators/Values` | EnergyPlus, DesignBuilder, Tally, One Click LCA, EC3 | [6d-sustainability](../research/03-bim-pipeline-3d-7d/6d-sustainability.md) |
| 7D (FM) | Mã tài sản, bảo hành, tuổi thọ, bảo trì, sensor | COBie (MVD của IFC), `Pset_Warranty`, `Pset_ServiceLife`, `Pset_ManufacturerTypeInformation`, `Pset_Asset`, `IfcZone`/`IfcSystem`; ISO 19650-3 (AIM) | CAFM/CMMS, Autodesk Tandem, Azure Digital Twins | [7d-facility-management-cobie](../research/03-bim-pipeline-3d-7d/7d-facility-management-cobie.md) |

Chi tiết đã xác minh đáng chú ý:
- 4D: `IfcWorkControl.StartTime` REQUIRED; `IfcTask.IsMilestone` REQUIRED; `Pset_TaskCommon` **không tồn tại** ([4d-schedule](../research/03-bim-pipeline-3d-7d/4d-schedule.md)).
- 5D: `IfcRelSchedulesCostItems` chỉ có ở IFC2X3; IFC4+ dùng `IfcRelAssignsToControl` ([5d-cost-quantities](../research/03-bim-pipeline-3d-7d/5d-cost-quantities.md)).
- 6D: `Pset_SpaceThermalDesign` có ở IFC4, không có trong template IFC4X3 ([6d-sustainability](../research/03-bim-pipeline-3d-7d/6d-sustainability.md)).
- 7D: `Pset_Warranty` IFC4.3 bỏ `WarrantyEndDate`; `IfcZone` ⊂ `IfcSystem` ở IFC4/4.3 ([7d-facility-management-cobie](../research/03-bim-pipeline-3d-7d/7d-facility-management-cobie.md)).

## 2. Khoá liên kết GUID

| Chiều | Phía 3D | Phía mở rộng | Khoá nối |
|---|---|---|---|
| 4D | `IfcProduct.GlobalId` | `IfcTask`/`TaskTime` | `IfcRelAssignsToProcess` hoặc bảng task↔GlobalId |
| 5D | `IfcElement` (+Qto) | `IfcCostItem` | `IfcRelAssignsToControl` hoặc BoQ có cột GlobalId |
| 6D | `IfcSpace`/`IfcElement`/`IfcMaterial` | kết quả mô phỏng/LCA | bảng ngoài theo GlobalId (đề xuất) |
| 7D | `IfcElement`/`IfcSpace` | COBie, CMMS, sensor | cột GUID/ExternalIdentifier |
| GIS | `IfcBuilding/Storey/Space` | feature GPKG/IMDF | `global_id` + `id` UUID ổn định |

Nguồn: [guid-linking](../research/03-bim-pipeline-3d-7d/guid-linking.md).

| Điểm | Nội dung (đã chạy thật) |
|---|---|
| Định dạng | `IfcGloballyUniqueId` 22 ký tự, thuộc tính `IfcRoot.GlobalId` |
| Sang UUID | `uuid.UUID(hex=ifcopenshell.guid.expand(gid))`; ngược lại `guid.compress` |
| ID cho IMDF | IMDF cần UUID; UUID từ `expand` không đảm bảo bit version v4; `stable_v4(namespace, GlobalId)` (UUID v4 sinh xác định, xem `docs/cad-to-gpkg-design.md`) cho kết quả ổn định |
| CAD không có GUID | Phải sinh ID ổn định (ví dụ `stable_v4` từ dự án + layer + handle — đề xuất) |

## 3. Hình học vs phi hình học

| Loại | Lưu ở đâu | Nguồn |
|---|---|---|
| Hình học | representation của `IfcProduct` trong IFC | [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md) |
| Phi hình học | Pset/Qto, `IfcRel*`, process/cost; có thể tách ra DB quan hệ/graph (RDF) nối bằng GUID | [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md) |
| COBie | Dạng bảng (19 bảng) hoặc IFC | [7d-facility-management-cobie](../research/03-bim-pipeline-3d-7d/7d-facility-management-cobie.md) |

## 4. Phần nào đưa sang GIS

| Chiều | Giá trị cho GIS | Cách đưa sang (đa số là đề xuất, chưa kiểm chứng) | Nguồn |
|---|---|---|---|
| 3D | Cao | Footprint theo tầng (`IfcBuildingStorey`, `IfcSpace`) + georeference | [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md) |
| 4D | Thấp | Bảng `task_assignment(task_id, start, finish, global_id)` cạnh GPKG; QGIS Temporal Controller nếu có trường thời gian | [4d-schedule](../research/03-bim-pipeline-3d-7d/4d-schedule.md) |
| 5D | Thấp | Chỉ diện tích `IfcSpace` (`Qto_SpaceBaseQuantities.NetFloorArea`) vào `unit`; chi phí không thuộc IMDF | [5d-cost-quantities](../research/03-bim-pipeline-3d-7d/5d-cost-quantities.md) |
| 6D | Thấp | Diện tích/thể tích, vật liệu chính, vùng nhiệt làm thuộc tính; footprint toà nhà cho phân tích năng lượng đô thị (chưa nghiên cứu) | [6d-sustainability](../research/03-bim-pipeline-3d-7d/6d-sustainability.md) |
| 7D | Cao nhất | Space → `unit`, Floor → `level`, Facility → `building`; asset → `amenity`/`fixture`/`occupant` hoặc layer asset kèm `asset_id`, `global_id` | [7d-facility-management-cobie](../research/03-bim-pipeline-3d-7d/7d-facility-management-cobie.md) |

## 5. Mâu thuẫn / chưa xác minh

| Mục | Tình trạng | Nguồn |
|---|---|---|
| Định nghĩa 6D/7D | **Mâu thuẫn giữa nguồn**: khảo sát Charef 2018 (6D = bền vững, 7D = FM) vs Designing Buildings/Saxon (6D = FM, 7D = cảm biến/phân tích). Dự án chọn quy ước ở đầu tài liệu. Nên đặt tên bảng theo nội dung (schedule, cost, sustainability, FM) | [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md) |
| Khảo sát Charef, Designing Buildings, RDF/Pulse | Chưa xác minh với nguồn gốc | [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md) |
| Chuẩn "nD" chính thức | Chưa tìm thấy | [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md) |
| Navisworks, Synchro, MS Project/P6; gói riêng "Ifc4D"/"Ifc5D" | Chưa xác minh (chỉ xác nhận module `util/api.sequence|cost`; `recalculate_schedule` cần `networkx`) | [4d-schedule](../research/03-bim-pipeline-3d-7d/4d-schedule.md) |
| `RelatingProcess` "deprecated ở IFC4x2" | Chưa xác minh (schema IFC4/4.3 cho thấy REQUIRED) | [4d-schedule](../research/03-bim-pipeline-3d-7d/4d-schedule.md) |
| CostX, Revit schedules, Vico, xuất xlsx/ods | Chưa xác minh | [5d-cost-quantities](../research/03-bim-pipeline-3d-7d/5d-cost-quantities.md) |
| NetSideArea từ mesh BlenderBIM không trừ opening | Báo cáo người dùng, chưa xác minh — đối chiếu trước khi bóc tách | [5d-cost-quantities](../research/03-bim-pipeline-3d-7d/5d-cost-quantities.md) |
| gbXML, EnergyPlus, Tally, One Click LCA, EC3; khớp `IfcMaterial` ↔ EPD; "Insight" còn được hỗ trợ không | Chưa xác minh; độ tin cậy 6D thấp–trung bình | [6d-sustainability](../research/03-bim-pipeline-3d-7d/6d-sustainability.md), [prd-corrections-01-03](../research/02-bim/prd-corrections-01-03.md) |
| COBie 19 bảng, v2.4 vs v3 (bản tóm tắt còn DRAFT), ánh xạ COBie ↔ IFC/Pset, ISO 19650-3/AIM, digital twin | Chưa xác minh (thiếu bảng NIBS, văn bản ISO) | [7d-facility-management-cobie](../research/03-bim-pipeline-3d-7d/7d-facility-management-cobie.md) |
| `WarrantyGuarantorLabor` | Không có trong template IFC4/4.3 (có thể thuộc IFC2X3, chưa kiểm) | [7d-facility-management-cobie](../research/03-bim-pipeline-3d-7d/7d-facility-management-cobie.md) |
| Ký tự đầu GUID chỉ 0–3 | Chưa kiểm (mẫu 1 giá trị) | [guid-linking](../research/03-bim-pipeline-3d-7d/guid-linking.md) |
| Revit/Unity giữ GUID; BIM Fit Check; ArchiCAD; COBie lưu GlobalId ở bảng nào | Chưa xác minh | [guid-linking](../research/03-bim-pipeline-3d-7d/guid-linking.md) |
| Đưa bảng 4D/5D/6D sang GPKG; cách dùng COBie Coordinate | Đề xuất thiết kế, chưa kiểm chứng | [dimensions-overview](../research/03-bim-pipeline-3d-7d/dimensions-overview.md), [7d-facility-management-cobie](../research/03-bim-pipeline-3d-7d/7d-facility-management-cobie.md) |
