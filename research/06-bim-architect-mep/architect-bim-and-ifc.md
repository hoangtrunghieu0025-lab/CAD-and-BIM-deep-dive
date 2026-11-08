# BIM Architect (Kiến trúc) — vai trò và đối tượng IFC

- **Câu hỏi nghiên cứu**: Mô hình kiến trúc (Architectural BIM) gồm những đối tượng/quan hệ IFC nào, và phần nào phục vụ pipeline CAD → BIM → GPKG?
- **Kết luận ngắn**: Mô hình kiến trúc là "xương sống không gian" của mọi bộ môn: tường, sàn, cửa, mái, cầu thang… (nhóm `IfcBuiltElement`) cùng `IfcSpace` (phòng). Tường–cửa liên kết qua chuỗi `IfcRelVoidsElement` → `IfcOpeningElement` → `IfcRelFillsElement`. Phòng và ranh giới phòng (`IfcRelSpaceBoundary`) là nguồn chính cho lớp `unit`/`room` của IMDF/OSM indoor.
- **Độ tin cậy**: cao cho phần schema (đọc trực tiếp schema `IFC4X3_ADD2` trong `ifcopenshell 0.9.0.post1`, 2026-11-08); trung bình cho phần quy trình (nguồn thứ cấp/vendor).

## Chi tiết

### 1. Phân cấp lớp (đã xác minh bằng schema IFC4X3_ADD2)
- `IfcWall`, `IfcCurtainWall`, `IfcDoor`, `IfcWindow`, `IfcStair`, `IfcRamp`, `IfcRoof`, `IfcCovering` đều: `< IfcBuiltElement < IfcElement < IfcProduct < IfcObject < IfcObjectDefinition < IfcRoot`. (Lưu ý: ở IFC4 tên là `IfcBuildingElement`; IFC4X3 đổi thành `IfcBuiltElement` — dùng IFC4 thì tra tên cũ.)
- `IfcSpace < IfcSpatialStructureElement < IfcSpatialElement < IfcProduct …` — phòng là phần tử **không gian**, không phải `IfcElement`.
- `IfcOpeningElement < IfcFeatureElementSubtraction < IfcFeatureElement < IfcElement` — ô trống dùng để khoét tường/sàn.

### 2. Quan hệ then chốt (thuộc tính đọc từ schema)
| Quan hệ | Thuộc tính | Ý nghĩa |
|---|---|---|
| `IfcRelVoidsElement` | `RelatingBuildingElement`, `RelatedOpeningElement` | Opening khoét vào tường/sàn (1–1; phép trừ hình học) |
| `IfcRelFillsElement` | `RelatingOpeningElement`, `RelatedBuildingElement` | Cửa/cửa sổ lấp vào opening |
| `IfcRelSpaceBoundary` | `RelatingSpace`, `RelatedBuildingElement`, `ConnectionGeometry`, `PhysicalOrVirtualBoundary`, `InternalOrExternalBoundary` | Phòng nào giáp phần tử nào → suy ra phòng liền kề, cửa nối phòng |
| `IfcRelContainedInSpatialStructure` | `RelatedElements`, `RelatingStructure` | Phần tử thuộc tầng (`IfcBuildingStorey`) |
| `IfcRelAggregates` | `RelatingObject`, `RelatedObjects` | Phân rã (vd. tầng thuộc toà nhà) |

Chuỗi cửa: `IfcWall —IfcRelVoidsElement→ IfcOpeningElement —IfcRelFillsElement→ IfcDoor`. Nguồn: tài liệu IFC4.3 (kết quả tìm kiếm; trang gốc trả 403 qua proxy nên chỉ dùng phần khớp với schema đã đọc).

### 3. Pset/Qto kiến trúc hay dùng (trích từ template IFC4X3 của ifcopenshell)
- `Pset_WallCommon` (IfcWall): `Reference, Status, AcousticRating, FireRating, Combustible, SurfaceSpreadOfFlame, ThermalTransmittance, IsExternal, LoadBearing, ExtendToStructure, Compartmentation`.
- `Pset_DoorCommon`: gồm `FireRating, SecurityRating, IsExternal, ThermalTransmittance, GlazingAreaFraction…`; `Pset_WindowCommon`: thêm `HasSillExternal, HasDrive, SmokeStop, FireExit…`.
- `Pset_SlabCommon`: `PitchAngle, LoadBearing, IsExternal, FireRating…`.
- `Qto_WallBaseQuantities`: `Length, Width, Height, GrossFootPrintArea, NetFootPrintArea, GrossSideArea, NetSideArea, GrossVolume, NetVolume, GrossWeight, NetWeight`. `Qto_DoorBaseQuantities`: `Width, Height, Perimeter, Area`.
- `IsExternal` là cờ hữu ích để phân biệt tường ngoài/trong khi xuất `IMDF footprint/level`.

### 4. Vai trò kiến trúc sư trong quy trình BIM (nguồn thứ cấp)
Một BEP mẫu liệt kê trách nhiệm của kiến trúc sư trên Revit: lập chương trình (programming), mô hình hiện trạng, kiểm tra quy chuẩn, tạo thiết kế, điều phối thiết kế, xuất bản vẽ, mô hình hoàn công. Mô hình kiến trúc được **link** vào mô hình MEP/kết cấu để điều phối.

## Liên quan đến pipeline CAD → BIM → GPKG
- CAD plan (layer tường/cửa/phòng) → ánh xạ sang `IfcWall`/`IfcDoor`/`IfcSpace` + `IfcRelContainedInSpatialStructure` theo tầng.
- Đầu ra GPKG: `IfcSpace` → polygon `unit` (IMDF) / `indoor=room` (OSM); `IfcDoor` + `IfcRelSpaceBoundary` → `opening`/`door=*`; tầng → `level`. Cần đối chiếu chi tiết với `research/04-osm-imdf-tagging/`.

## Nguồn
- Schema IFC4X3_ADD2 qua `ifcopenshell.ifcopenshell_wrapper` / `ifcopenshell.util.pset` (0.9.0.post1) — kiểm trực tiếp 2026-11-08
- [IfcRelVoidsElement – IFC 4.3.2 (kết quả tìm kiếm)](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcRelVoidsElement.htm) — truy cập 2026-11-08 (qua WebSearch; WebFetch bị 403)
- [Revit BEP mẫu – slideshare](https://es.slideshare.net/rdaepct/bim-execution-plan-138267781) — truy cập 2026-11-08 (qua tóm tắt tìm kiếm, độ tin cậy thấp)

## Câu hỏi còn mở
- `IfcCurtainWall` (phân rã mullion/plate) chưa đọc được định nghĩa chính thức — chưa xác minh.
- Chưa kiểm `IfcRelSpaceBoundary` mức 2nd-level trong file IFC xuất từ Revit thực tế.
