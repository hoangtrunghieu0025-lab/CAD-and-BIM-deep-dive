# CAD vs BIM và hệ quả cho pipeline CAD → BIM → GPKG

> Tổng hợp từ `research/01-cad/` và `research/02-bim/` (đã xác minh một phần trong TASK-012). Mỗi mục trỏ về ghi chú gốc; nhãn "chưa xác minh" lấy nguyên từ ghi chú.

## 1. Bản chất

| | CAD (DWG/DXF) | BIM (IFC) |
|---|---|---|
| Đơn vị dữ liệu | Entity hình học gắn `layer` | Đối tượng có ngữ nghĩa (`IfcWall`, `IfcSpace`…) |
| Ngữ nghĩa | Chỉ qua tên layer/block/text, không ở hình học ([layer-naming-conventions](../research/01-cad/layer-naming-conventions.md)) | Class + Pset/Qto + classification ([property-sets-and-classification](../research/02-bim/property-sets-and-classification.md)) |
| Quan hệ | Không có (cửa không "biết" nằm trong tường nào) ([parsing-with-ezdxf](../research/01-cad/parsing-with-ezdxf.md)) | `IfcRel*` (aggregate, containment…) ([ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md)) |
| Toạ độ | WCS/OCS, thường cục bộ, không CRS ([coordinates-and-units](../research/01-cad/coordinates-and-units.md)) | Có thể georeference bằng `IfcMapConversion` (IFC4+) ([ifc-georeference](../research/02-bim/ifc-georeference.md)) |
| Khoá định danh | `handle` (không ổn định giữa phiên bản — chưa xác minh) | `GlobalId` 22 ký tự ([guid-linking](../research/03-bim-pipeline-3d-7d/guid-linking.md)) |

## 2. Định dạng

| Định dạng | Ghi chú | Nguồn |
|---|---|---|
| DXF | Trao đổi, chủ yếu ASCII; `ezdxf` đọc/ghi R12 → R2018; `ezdxf.recover` chỉ ASCII | [dxf-dwg-formats](../research/01-cad/dxf-dwg-formats.md) |
| DWG | Nhị phân độc quyền; đọc qua ODA File Converter (`ezdxf.addons.odafc`) hoặc LibreDWG `dwg2dxf` (GPLv3+) | [dxf-dwg-formats](../research/01-cad/dxf-dwg-formats.md) |
| IFC | Cây `IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace`; IFC4.3 thêm `IfcFacility` ⊃ `IfcBuilding` | [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md) |

Lưu ý: ODA `readfile` chạy ứng dụng ngoài, docs ezdxf cảnh báo bảo mật; trên Linux headless có thể cần `xvfb`; khoá cấu hình là `unix_exec_path`, không phải `linux_exec_path` ([dxf-dwg-formats](../research/01-cad/dxf-dwg-formats.md)).

## 3. Khái niệm chính

| Khái niệm | Điểm cần nhớ | Nguồn |
|---|---|---|
| Layer | Nhãn nhóm duy nhất để suy ngữ nghĩa; có `is_off/is_frozen/is_locked` | [layers-blocks-xref](../research/01-cad/layers-blocks-xref.md) |
| Block/INSERT/ATTRIB | ATTRIB đọc từ INSERT; `recursive_decompose` để phân rã lồng; MINSERT (`mcount > 1`) cần xử lý riêng | [layers-blocks-xref](../research/01-cad/layers-blocks-xref.md) |
| Xref | ezdxf không tự nạp nội dung xref; `disassemble` bỏ qua XREF, cần cảnh báo | [layers-blocks-xref](../research/01-cad/layers-blocks-xref.md) |
| Model/paper space | Chỉ lấy model space | [layers-blocks-xref](../research/01-cad/layers-blocks-xref.md) |
| WCS/OCS/UCS | DXF lưu WCS hoặc OCS, không bao giờ UCS | [coordinates-and-units](../research/01-cad/coordinates-and-units.md) |
| Pset/Qto | `Pset_SpaceCommon`, `Qto_SpaceBaseQuantities`… (property đã trích từ template ifcopenshell) | [property-sets-and-classification](../research/02-bim/property-sets-and-classification.md) |
| LOIN/MVD/IDS | LOIN (ISO 7817-1) = nhu cầu thông tin; MVD = tập con schema; IDS = XML kiểm model (6 facet, đã xác minh qua `ids.xsd`) | [lod-mvd-ids](../research/02-bim/lod-mvd-ids.md) |

## 4. Hệ quả cho pipeline

| Chủ đề | Quy tắc | Nguồn |
|---|---|---|
| Layer mapping | File cấu hình, regex/glob + ignore + fallback `unknown`; chuẩn hoá (upper-case, bỏ tiền tố `xref\|`); `A-WALL/A-DOOR/A-AREA` chỉ là ví dụ, không phải quy định | [layer-naming-conventions](../research/01-cad/layer-naming-conventions.md) |
| OCS → WCS | `entity.ocs().to_wcs(...)`; `ezdxf.upright` sửa tại chỗ và không dùng cho TEXT/MTEXT/DIMENSION; MLINE đã ở WCS | [coordinates-and-units](../research/01-cad/coordinates-and-units.md) |
| Đơn vị `$INSUNITS` | Đọc `doc.units`; nếu 0 (unitless) lấy từ config; `conversion_factor` ném `TypeError` với 0, 8, 9, 21–24 | [coordinates-and-units](../research/01-cad/coordinates-and-units.md) |
| Đơn vị IFC | Nhân `calculate_unit_scale` với mọi giá trị độ dài đọc thô (`Elevation`, `OverallWidth`); chỉ `create_shape` trả mét | [ifcopenshell-geometry-extraction](../research/02-bim/ifcopenshell-geometry-extraction.md) |
| Georeference | `IfcMapConversion`/`IfcProjectedCRS` chỉ từ IFC4 (không có ở IFC2X3); fallback: `IfcSite.RefLatitude/RefLongitude` (thô, WGS84) hoặc control points; DXF có thể có `GEODATA` (R2010+, không giả định) | [ifc-georeference](../research/02-bim/ifc-georeference.md), [prd-corrections-01-03](../research/02-bim/prd-corrections-01-03.md), [coordinates-and-units](../research/01-cad/coordinates-and-units.md) |
| Công thức map | E = Scale·(x·a − y·b) + E0; N = Scale·(x·b + y·a) + N0; (a,b) được chuẩn hoá — đã kiểm với Scale = 1 | [ifc-georeference](../research/02-bim/ifc-georeference.md) |
| EPSG VN-2000 (đã tra) | `EPSG:4756` (địa lý), `3405` (UTM 48N), `3406` (UTM 49N), TM-3 `5896`–`5899`, `9205`–`9218` | [ifc-georeference](../research/02-bim/ifc-georeference.md) |
| `IfcSpace` aggregate vs container | Space gắn tầng bằng `IfcRelAggregates`; `IfcDoor`/`IfcWall` bằng `IfcRelContainedInSpatialStructure`. `get_container(space)` trả `None` với space aggregate — dùng `get_aggregate` (đã chạy thật) | [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md) |
| Footprint từ Body | Ưu tiên representation `FootPrint` nếu có; không thì triangulate `Body` (`USE_WORLD_COORDS`) → chiếu XY → `shapely.unary_union` (phòng 4×5 → 20.0, đã chạy). Cửa: bbox/rectangle → trục dài → LineString (đề xuất dự án) | [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md), [ifcopenshell-geometry-extraction](../research/02-bim/ifcopenshell-geometry-extraction.md) |
| CAD → polygon phòng | `shapely.ops.polygonize` từ đường tường, hoặc biên HATCH; gắn tên phòng bằng point-in-polygon; lưu `source_layer`, `source_handle` (INSERT cha cho entity ảo) | [parsing-with-ezdxf](../research/01-cad/parsing-with-ezdxf.md) |
| Sinh IFC trung gian | Phải dựng đủ chuỗi aggregate + containment | [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md) |

Mapping CAD/IFC → OSM → IMDF chi tiết thuộc luồng 04 (`research/04-osm-imdf-tagging/`), ngoài phạm vi tài liệu này. Các cặp lớp đã có căn cứ ở luồng 01–02: layer `type: space` / `IfcSpace` → IMDF `unit`; `IfcBuildingStorey` → `level`; `IfcDoor` → `opening` (LineString); `IfcBuilding` → `building` ([ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md)).

## 5. Mâu thuẫn / chưa xác minh

| Mục | Tình trạng | Nguồn |
|---|---|---|
| `ezdxf.readthedocs.io` | Không phân giải DNS; dùng mã/docs nhánh `master` trên GitHub, có thể lệch bản phát hành | [parsing-with-ezdxf](../research/01-cad/parsing-with-ezdxf.md) |
| Tên layer NCS/AIA (`A-AREA`, `A-FLOR`, `A-GLAZ`…), ISO 13567, BS 1192 | Chưa xác minh từ trang gốc (host bị chặn, chuẩn trả phí); các nguồn còn mâu thuẫn về minor/major group tự định nghĩa | [layer-naming-conventions](../research/01-cad/layer-naming-conventions.md) |
| Layer tiếng Việt (`TUONG`, `CUA`…), đơn vị phổ biến của bản vẽ VN | Chưa xác minh, cần mẫu thật | [layer-naming-conventions](../research/01-cad/layer-naming-conventions.md), [coordinates-and-units](../research/01-cad/coordinates-and-units.md) |
| Binary DXF với `ezdxf.readfile` | Chưa xác minh (chỉ biết `recover` chỉ ASCII) | [dxf-dwg-formats](../research/01-cad/dxf-dwg-formats.md) |
| Tên cấu hình ODA | Docs tự mâu thuẫn (`linux_exec_path` vs `unix_exec_path`); lấy theo mã nguồn | [dxf-dwg-formats](../research/01-cad/dxf-dwg-formats.md) |
| Mất mát khi DWG → DXF (proxy, ACIS, ACAD_TABLE); điều khoản ODA | Chưa xác minh | [dxf-dwg-formats](../research/01-cad/dxf-dwg-formats.md) |
| `xref\|layer`, block ẩn `*U<n>` (dynamic block) | Nguồn thứ cấp; cách ezdxf đọc layer có `|` chưa xác minh | [layers-blocks-xref](../research/01-cad/layers-blocks-xref.md) |
| GEODATA thực tế (Civil 3D, Việt Nam); `$EXTMIN/$EXTMAX` lỗi thời | Chưa xác minh | [coordinates-and-units](../research/01-cad/coordinates-and-units.md) |
| Chưa chạy trên mẫu: MINSERT, OCS −Z, MLINE, HATCH, SPLINE, xref; bước làm sạch shapely | Chưa xác minh | [parsing-with-ezdxf](../research/01-cad/parsing-with-ezdxf.md) |
| Representation `FootPrint` từ Revit; `IfcRelFillsElement`; space đa tầng | Chưa xác minh (mẫu chỉ có `Body`) | [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md) |
| IFC2X3 dùng `ePSet_MapConversion`/`ePSet_ProjectedCRS`; `WorldCoordinateSystem`/`TrueNorth`; `Scale ≠ 1`, đơn vị ≠ mét | Chưa xác minh | [ifc-georeference](../research/02-bim/ifc-georeference.md) |
| Quy định pháp lý chọn phép chiếu VN-2000 theo tỉnh | Chưa xác minh; không khẳng định mã bắt buộc | [prd-corrections-01-03](../research/02-bim/prd-corrections-01-03.md) |
| Ghi chú cũ sai, đã sửa: `IfcProjectedCRS.GeodeticDatum` "bắt buộc ở IFC4" (thực tế OPTIONAL); `IfcSpace` chỉ thuộc `IfcSpatialElement` (thực tế qua `IfcSpatialStructureElement`) | Đã sửa theo schema; đừng dùng bản cũ | [ifc-georeference](../research/02-bim/ifc-georeference.md), [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md) |
| LOIN/ISO 7817-1, BIMForum LOD, mvdXML, IDM, `ifctester` | Chưa xác minh; "LOD" hiểu là Level of Detail/Development tuỳ nguồn | [lod-mvd-ids](../research/02-bim/lod-mvd-ids.md) |
| Quy ước tiền tố `Pset_`; classification/bSDD | Chưa xác minh trực tiếp | [property-sets-and-classification](../research/02-bim/property-sets-and-classification.md) |
| DGN, RVT/NWD/SKP/PLN, COBie/BCF/gbXML/CityGML, "DWG phổ biến nhất" | Chưa xác minh | [prd-corrections-01-03](../research/02-bim/prd-corrections-01-03.md) |
| Trang spec buildingSMART trả 403 | Phần lớn kiểm bằng schema ifcopenshell 0.9.0.post1, không đọc spec trực tiếp | [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md) |
