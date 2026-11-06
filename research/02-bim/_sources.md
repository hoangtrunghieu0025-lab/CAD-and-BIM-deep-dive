# Nguồn bổ sung — TASK-003 vòng 2 (xác minh lại)

Không sửa `research/sources.md`; điều phối viên gộp nếu cần.

## Kết quả vòng 2 (2026-11-06)
Không có nguồn mới nào đọc được. Các host dưới đây vẫn không phân giải DNS (`getaddrinfo ENOTFOUND`) trong phiên này, nên chưa xác minh được khẳng định nào so với trang spec gốc:

| Host | Trang đã thử | Kết quả |
|---|---|---|
| ifc43-docs.standards.buildingsmart.org | `.../IFC4x3/HTML/lexical/IfcSpace.htm`, `IfcBuildingStorey.htm`, `IfcMapConversion.htm`, `Pset_DoorCommon.htm`, `Pset_SpaceCommon.htm`, `Qto_SpaceBaseQuantities.htm`, `Qto_DoorBaseQuantities.htm` | ENOTFOUND (7/7), truy cập 2026-11-06 |
| docs.ifcopenshell.org | `/autoapi/ifcopenshell/util/element/index.html` | ENOTFOUND, truy cập 2026-11-06 |

Theo hướng dẫn của công cụ (host nằm ngoài danh sách domain cho phép của phiên), đã dừng thử thêm host khác. Cần thêm hai host trên vào network allowlist của phiên rồi chạy lại vòng xác minh.

## Danh sách việc cần kiểm khi host mở
- IfcSpace: supertype trong 4.3; Name/LongName.
- IfcBuildingStorey.Elevation.
- IfcMapConversion: công thức, chuẩn hoá XAxisAbscissa/XAxisOrdinate, Scale, SourceCRS, WorldCoordinateSystem, TrueNorth.
- Pset_DoorCommon, Pset_SpaceCommon (đầy đủ property); Qto_SpaceBaseQuantities, Qto_DoorBaseQuantities.
- IDS: 6 facet, ifctester.
- IfcOpenShell: util.element.get_container, util.shape.get_footprint_area, geom.settings 0.7 vs 0.8, api.georeference, util.geolocation.
