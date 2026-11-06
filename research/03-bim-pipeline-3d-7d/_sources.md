# Nguồn bổ sung — TASK-004 (chưa gộp vào research/sources.md)

## Vòng 2 xác minh (2026-11-06)
Không thêm nguồn mới được xác minh. Toàn bộ WebFetch tới các host dưới đây đều lỗi DNS `getaddrinfo ENOTFOUND` (host chưa nằm trong danh sách mạng được phép của phiên), nên không đối chiếu được trang gốc:

| URL đã thử | Mục đích | Kết quả (2026-11-06) |
|---|---|---|
| https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcTask.htm | thuộc tính IfcTask | ENOTFOUND |
| https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcTaskTime.htm | IfcTaskTime | ENOTFOUND |
| https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRelAssignsToProcess.htm | deprecated RelatingProcess | ENOTFOUND |
| https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWorkSchedule.htm | IfcWorkSchedule | ENOTFOUND |
| https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_TaskCommon.htm | Pset_TaskCommon | ENOTFOUND |
| https://docs.ifcopenshell.org/autoapi/ifcopenshell/guid/index.html | hàm GUID<->UUID | ENOTFOUND |
| https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcTask.htm | thử host dự phòng | ENOTFOUND |

Các mục chưa thử do cùng nguyên nhân (cùng host): IfcCostSchedule/IfcCostItem/IfcCostValue/IfcAppliedValue, Pset nhiệt 6D, bảng COBie-IFC, ifcopenshell.api.sequence/Ifc4D.

Cần làm: cho phép `ifc43-docs.standards.buildingsmart.org` và `docs.ifcopenshell.org` trong cài đặt mạng của phiên, rồi chạy lại vòng xác minh.
