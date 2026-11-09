# MEP (Cơ – Điện – Nước) — hệ thống và đối tượng IFC

- **Câu hỏi nghiên cứu**: MEP gồm những hệ thống/thiết bị nào, được mô hình trong IFC ra sao (hệ thống, cổng kết nối, phân cấp lớp), và phần nào dùng được cho pipeline?
- **Kết luận ngắn**: MEP = HVAC (cơ), Điện, Cấp–thoát nước (+ PCCC). Trong IFC, mọi thiết bị/ống/cáp là `IfcDistributionElement`; chúng được gom vào `IfcDistributionSystem` (kiểu hệ thống theo enum) và nối nhau qua `IfcDistributionPort` + `IfcRelConnectsPorts`. Với GIS/indoor map, MEP ít khi xuất thẳng; giá trị chủ yếu ở **điểm tài sản** (thiết bị, terminal) và liên kết với `IfcSpace`.
- **Độ tin cậy**: cao cho lớp/enum/thuộc tính (đọc schema IFC4X3_ADD2 trong ifcopenshell, 2026-11-08); trung bình cho thuật ngữ Revit (qua kết quả tìm kiếm, không fetch được help.autodesk.com).

## Chi tiết

### 1. Ba (bốn) bộ môn
| Bộ môn | Nội dung | Ví dụ lớp IFC (đã xác minh) |
|---|---|---|
| **M – HVAC** | ống gió, miệng gió, quạt, thiết bị lạnh/sưởi | `IfcDuctSegment`, `IfcDuctFitting`, `IfcAirTerminal`, `IfcFan`, `IfcBoiler` |
| **E – Điện** | tủ điện, cáp, máng cáp, đèn, cảm biến | `IfcElectricDistributionBoard`, `IfcCableSegment`, `IfcCableCarrierSegment`, `IfcLightFixture`, `IfcLamp`, `IfcSensor` |
| **P – Cấp thoát nước** | ống, van, bơm, thiết bị vệ sinh | `IfcPipeSegment`, `IfcPipeFitting`, `IfcValve`, `IfcPump`, `IfcSanitaryTerminal` |
| **FP – PCCC** (thường đi kèm) | đầu phun, đường ống chữa cháy | `IfcFireSuppressionTerminal` + `IfcPipeSegment` |

### 2. Cây phân cấp (xác minh schema)
`IfcDistributionElement < IfcElement`, với nhánh `IfcDistributionFlowElement` chia: `IfcFlowSegment` (Duct/Pipe/Cable/CableCarrier segment), `IfcFlowFitting`, `IfcFlowTerminal` (AirTerminal, SanitaryTerminal, LightFixture, Lamp, FireSuppressionTerminal), `IfcFlowController` (Valve, ElectricDistributionBoard), `IfcFlowMovingDevice` (Pump, Fan), `IfcEnergyConversionDevice` (Boiler); nhánh `IfcDistributionControlElement` (Sensor).

### 3. Hệ thống và kết nối
- `IfcDistributionSystem < IfcSystem < IfcGroup`; `IfcDistributionCircuit` là lớp con (mạch điện/chất lỏng). Phần tử được gán vào hệ thống qua `IfcRelAssignsToGroup` (`RelatedObjects`, `RelatingGroup`).
- `IfcDistributionSystemEnum` (IFC4X3_ADD2) có 50 giá trị, gồm: `AIRCONDITIONING, CHILLEDWATER, CONDENSERWATER, DOMESTICCOLDWATER, DOMESTICHOTWATER, DRAINAGE, SEWAGE, STORMWATER, RAINWATER, VENT, VENTILATION, EXHAUST, HEATING, REFRIGERATION, FIREPROTECTION, ELECTRICAL, LIGHTING, EARTHING, LIGHTNINGPROTECTION, COMMUNICATION, DATA, TELEPHONE, SECURITY, CONTROL, GAS, FUEL, COMPRESSEDAIR, VACUUM, WATERSUPPLY, WASTEWATER…`, cộng `USERDEFINED`, `NOTDEFINED`.
- Cổng: `IfcDistributionPort < IfcPort < IfcProduct`, thuộc tính `FlowDirection` (`SINK`, `SOURCE`, `SOURCEANDSINK`, `NOTDEFINED`), `PredefinedType` (`CABLE, CABLECARRIER, DUCT, PIPE, WIRELESS…`), `SystemType`. Nối: `IfcRelConnectsPorts(RelatingPort, RelatedPort, RealizingElement)`. Tài liệu ghi: nếu port có system type thì chỉ nối được với port cùng system type.
- Điều khiển: `IfcRelFlowControlElements(RelatedControlElements, RelatingFlowElement)` gắn cảm biến/bộ điều khiển vào phần tử dòng chảy.
- Gắn port vào phần tử cha dùng `IfcRelNests` (theo mẫu IFC4+; chi tiết chưa đọc từ trang gốc).

### 4. Pset/Qto MEP (template IFC4X3 trong ifcopenshell)
- `Pset_DuctSegmentTypeCommon`: `CrossSectionShape, WorkingPressure, TemperatureRange, NominalDiameterOrWidth, NominalHeight…`
- `Pset_PipeSegmentTypeCommon`: `WorkingPressure, TemperatureRange, NominalDiameter, InnerDiameter, OuterDiameter, Length`.
- `Pset_AirTerminalTypeCommon`: `AirTerminalShape, FaceType, AirFlowRateRange, ThrowLength, …`; `Pset_PumpTypeCommon`: `FlowRateRange, ConnectionSize, NetPositiveSuctionHead…`; `Pset_LightFixtureTypeCommon`: `NumberOfSources, TotalWattage, LightFixtureMountingType…`.
- `Pset_ElectricalDeviceCommon`: `RatedCurrent, RatedVoltage, PowerFactor, IP_Code, IK_Code, Power…`.
- `Pset_DistributionSystemCommon` chỉ có `Reference`; `Pset_DistributionPortCommon`: `PortNumber, ColourCode`.
- `Qto_DuctSegmentBaseQuantities`: `Length, GrossCrossSectionArea, NetCrossSectionArea, OuterSurfaceArea, GrossWeight`; `Qto_PipeSegmentBaseQuantities` tương tự + `NetWeight, FootPrintArea`.
- Các Pset ở trên là **Pset của IFC** (tên chuẩn); Revit khi xuất IFC còn thêm Pset riêng — chưa xác minh.

### 5. Thuật ngữ Revit MEP (nguồn thứ cấp)
- Duct system: Supply Air, Return Air, Exhaust Air. Piping: Sanitary, Domestic Hot Water, Domestic Cold Water, Other; fire protection: wet/dry/pre-action. Electrical có lớp hệ thống như fire alarm, security (API Revit). "Power circuit" chưa xác nhận từ nguồn.
- **Room vs Space**: Room là phần tử kiến trúc; Space là phần tử MEP dùng cho phân tích thể tích/tải nhiệt; Space nằm trong file MEP (host) và có thể lấy tên/số từ Room của model kiến trúc được link. Tương ứng IFC: cả hai đều xuất thành `IfcSpace` (cách phân biệt khi xuất: chưa xác minh).
- Connector ở trạng thái "Undefined" làm hỏng tạo system tự động.

## Liên quan đến pipeline CAD → BIM → GPKG
- CAD MEP thường chỉ là layer (`M-DUCT`, `E-POWR`, `P-PIPE`… — quy ước tuỳ đơn vị, xem `research/01-cad/layer-naming-conventions.md`): chỉ có hình học, không có port/system → khó dựng graph.
- Hướng khả thi: xuất **điểm** thiết bị/terminal (đèn, miệng gió, thiết bị vệ sinh) làm POI/asset gắn `IfcSpace` chứa nó; tuyến ống/cáp có thể là LineString trong lớp phụ (ngoài IMDF/OSM chuẩn — cần quyết định phạm vi).
- 7D/FM: `IfcDistributionSystem` + COBie `System`/`Component` là cầu nối (xem `research/03-bim-pipeline-3d-7d/7d-facility-management-cobie.md`).

## Nguồn
- Schema IFC4X3_ADD2 + template Pset qua ifcopenshell 0.9.0.post1 — kiểm trực tiếp 2026-11-08
- [IfcDistributionPort / Port Connectivity – buildingSMART](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcsharedbldgserviceelements/lexical/ifcdistributionport.htm) — truy cập 2026-11-08 (qua kết quả tìm kiếm)
- [Revit API – MEP system classification enum (2026)](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/43ec0d75-d6bb-2d08-a920-9715e83040e7.htm) — truy cập 2026-11-08 (qua kết quả tìm kiếm)
- [Autodesk – About Spaces](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-MEPEng/files/GUID-B876A6F6-4091-40CA-ADCD-AA5D0EFC5EE3.htm) — truy cập 2026-11-08 (qua kết quả tìm kiếm)
- [Autodesk – Customize System Types](https://help.autodesk.com/cloudhelp/2020/ENU/Revit-Model/files/GUID-0E860EB4-62A7-4B5A-89A4-FEA563232E18.htm) — truy cập 2026-11-08 (qua kết quả tìm kiếm)

## Câu hỏi còn mở
- Chưa đọc trực tiếp trang IFC cho `IfcDistributionSystem`, `IfcRelNests` với port.
- Cách Revit xuất Room/Space sang IFC và Pset MEP riêng của Revit: chưa xác minh.
- Cable tray trong Revit: chưa tìm được nguồn.
