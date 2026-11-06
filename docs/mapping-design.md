# Thiết kế mapping CAD / IFC → OSM → IMDF

> Bản nháp của claude-mobile (TASK-007). Hai file cấu hình: [`config/layer_mapping.yaml`](../config/layer_mapping.yaml) (CAD layer → loại đối tượng) và [`config/tag_mapping.yaml`](../config/tag_mapping.yaml) (loại đối tượng / IFC class → tag OSM → feature IMDF). Mỗi quy tắc trong YAML có nhãn `status` (`verified` / `sample` / `example` / `unverified`).

## 1. Luồng dùng hai file

```
DXF ─ layer_mapping.yaml ─► loại đối tượng (space, wall, door…) ┐
                                                                  ├─ tag_mapping.yaml ─► tag OSM + feature IMDF ─► GPKG
IFC ─ IFC class (IfcSpace, IfcDoor…) ─────────────────────────────┘
```

## 2. Bảng ánh xạ chính

| Đối tượng | Nguồn CAD (mẫu) | Nguồn IFC | Tag OSM | Feature IMDF | Trạng thái |
|---|---|---|---|---|---|
| Tầng | 1 file DXF = 1 tầng (chưa có chuẩn) | `IfcBuildingStorey` | `level`, `level:ref`, (`indoor=level`) | `level` (`ordinal`, `name`, `short_name` bắt buộc) | verified |
| Toà nhà | — | `IfcBuilding` | `building=yes`, `min_level`/`max_level` | `building` (geometry null) + `footprint` | verified |
| Phòng | `A-AREA` (polyline kín) + nhãn `A-AREA-IDEN` | `IfcSpace` | `indoor=room` | `unit` category `room` | verified |
| Hành lang | `A-AREA` có tên "hành lang" | `IfcSpace` | `indoor=corridor` | `unit` category `walkway` | verified (regex tên là lựa chọn dự án) |
| Cửa nội bộ | `A-DOOR` (INSERT block `DOOR`) | `IfcDoor` | node `indoor=door` + `door=yes` | `opening` (LineString) category `pedestrian` | verified |
| Lối vào toà nhà | — | `IfcDoor` có `Pset_DoorCommon.IsExternal` | `entrance=yes` + `door=yes` | `opening` | verified |
| Tường | `A-WALL` | `IfcWall` | `indoor=wall` | mặc định **không xuất** (đơn giản hoá); tuỳ chọn `unit` category `structure` | verified |
| Cầu thang | `A-STRS`? (chưa xác minh) | `IfcStair` | area `stairs=yes` + `indoor=room` | `unit` category `stairs` | verified |
| Thang máy | — | `IfcTransportElement` ELEVATOR? | area `highway=elevator` + `area=yes` + `indoor=room` | `unit` category `elevator` | unverified (class IFC) |
| Cột | `A-COLS`? | `IfcColumn` | — | `unit` category `column` | verified (IMDF) |
| Cửa sổ | `A-GLAZ`? | `IfcWindow` | `window=yes` | không xuất | unverified |

Nguồn: [osm-simple-indoor-tagging](../research/04-osm-imdf-tagging/osm-simple-indoor-tagging.md), [imdf-feature-types](../research/04-osm-imdf-tagging/imdf-feature-types.md), [imdf-relations-and-constraints](../research/04-osm-imdf-tagging/imdf-relations-and-constraints.md), [layer-naming-conventions](../research/01-cad/layer-naming-conventions.md), [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md).

## 3. Các quyết định thiết kế

1. **Khớp đầu tiên thắng**, rule cụ thể đứng trước rule chung. Ví dụ `A-AREA-IDEN` (nhãn) phải đứng trước `A-AREA`, nếu không pattern `^A-AREA(-.*)?$` nuốt luôn lớp nhãn.
2. **Tên layer chuẩn hoá trước khi so khớp** (viết hoa, bỏ khoảng trắng, bỏ tiền tố xref `XREF|`). Layer không khớp rule nào thì **báo cáo, không báo lỗi** (`out/unmatched_layers.csv`) để người dùng bổ sung rule. Ref: [layer-naming-conventions](../research/01-cad/layer-naming-conventions.md).
3. **`level` OSM và `ordinal` IMDF tách riêng**: một bên là số vật lý (0 = mặt đất), một bên là thứ tự hiển thị; không ép bằng nhau. Ref: [osm-simple-indoor-tagging](../research/04-osm-imdf-tagging/osm-simple-indoor-tagging.md).
4. **Tường mặc định đơn giản hoá**: IMDF cho phép ranh giới `unit` đi theo mặt tường; nếu xuất tường floor-to-ceiling thì **bắt buộc** là `unit` category `structure`, không phải `fixture`. Công tắc `object_types.wall.imdf.mode: simplified | structure`.
5. **Cầu thang**: khu cầu thang là area `stairs=yes`; `highway=steps` chỉ dành cho từng đợt bậc (way). Không dùng `highway=steps` cho cả khu.
6. **Tầng của `IfcSpace` lấy bằng `get_aggregate`**, tầng của `IfcDoor`/`IfcWall` lấy bằng `get_container` (khác quan hệ). Ref: [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md).
7. **Footprint phòng**: ưu tiên representation `FootPrint`; mẫu chỉ có `Body` nên chiếu `Body` xuống XY. Ref: [ifcopenshell-geometry-extraction](../research/02-bim/ifcopenshell-geometry-extraction.md).
8. **Gói IMDF bắt buộc** `venue` + `address` + `manifest.json` phải được sinh dù nguồn thiếu; giá trị mặc định nằm trong `imdf_package`. GPKG chỉ là lưu trữ trung gian, muốn có gói IMDF thật cần bước xuất ZIP riêng.
9. **Cột GPKG**: cột riêng cho tag hay dùng (`level_ref` thay cho `level:ref` vì ký tự `:`), phần còn lại vào cột JSON `osm_tags`.

## 4. Trường hợp ngoại lệ

| Tình huống | Xử lý trong config |
|---|---|
| Polyline phòng không khép kín | `require_closed: true`; thử `shapely.ops.polygonize` từ các LINE cùng layer |
| `$INSUNITS = 0` (unitless) | `units.fallback_unit` (m); `conversion_factor` ném `TypeError` với 0, 8, 9, 21–24 nên phải bắt lỗi |
| `IfcDoor.OverallWidth` thiếu (OPTIONAL) | lấy theo opening, nếu không có thì `width_fallback_m: 0.9` (mặc định dự án) |
| IFC2X3 không có `IfcMapConversion` | dùng control points / `IfcSite.RefLatitude/RefLongitude` (xem PRIMARY_OBJECTIVE bước 3) |
| Bản vẽ dùng tên layer tiếng Việt | profile `vn_local` đang tắt (`profiles_disabled`), cần mẫu thật để bật |

## 5. Còn chưa xác minh / việc cho claude-laptop

- **Layer ngoài mẫu**: `A-GLAZ`, `A-COLS`, `A-STRS`, `A-FLOR` chỉ là gợi ý NCS/AIA (nhãn `example`/`unverified`); danh sách major group chính thức chưa đối chiếu. Xem [layer-naming-conventions](../research/01-cad/layer-naming-conventions.md).
- **`venue.category`**: phải là 1 trong **22** giá trị của IMDF `reference/categories` (đã chép ở `config/tag_mapping.yaml`). Bắt buộc đặt trong `project.yaml`; mẫu dùng `businesscampus`, công trình thật do chủ dự án chọn.
- **`IfcTransportElement` ELEVATOR**: tên class/enum và ánh xạ chưa kiểm trong schema.
- **`door=*`, `room=*`**: các giá trị hợp lệ chưa đọc (`Key:door`, `Key:room`); config chỉ dùng `door=yes` (loại chưa rõ, đã xác minh) và không gán `room=*`.
- **LABELS và Manifest** đã xác minh ([type_designators](https://register.apple.com/resources/imdf/reference/type_designators), [manifest](https://register.apple.com/resources/imdf/manifest)); còn mở cách hiểu "Labels MUST not contain mixed case characters" (đã chọn viết hoa).
- **Ngưỡng**: `buffer_m: 1.0` cho venue và `width_fallback_m: 0.9` là lựa chọn dự án.
- **Cần laptop**: chạy thử mapping trên `samples/*.ifc` (IfcSpace, IfcDoor, IfcWall, quy tắc corridor theo `LongName`) và ghi kết quả vào nhật ký TASK-007.

## 6. Xử lý 10 đề xuất của claude-laptop sau khi chạy thử (N-005)

Laptop chạy thử trên `samples/` (DXF: 13 phòng gồm 12 `default-room` + 1 `corridor`, 12/12 opening nằm trên ranh giới unit; IFC: 26 `IfcSpace`, 24 `IfcDoor`, 2 level, hợp unit khớp đường bao 24×12) và đưa 10 đề xuất. Cách xử lý:

| # | Đề xuất | Quyết định | Nơi thay đổi |
|---|---|---|---|
| 1 | `level.name`/`short_name`: spec cấm "mixed case" | **Chấp nhận.** Nhãn tầng viết hoa toàn bộ; `short_name` ngắn từ tên tầng ("1", "B1"), `name` từ `long_name`. LABELS là `{"vi": "…"}` (đã xác minh). Cách hiểu "mixed case" vẫn chưa xác minh | `defaults.labels`, `storey.label_rule` |
| 2 | Vị trí cửa IFC vs DXF lệch 0,45 m | **Chấp nhận.** Tâm lấy từ hình học opening → bbox cửa → placement + `placement_anchor`; hướng theo trục X; thêm test kiểm tâm (phép kiểm "trên ranh giới" không đủ) | `door.geometry_source`, spec T19 |
| 3 | `namespace` còn `null` | **Đã chốt** một UUID cố định. Phát hiện thêm: IMDF yêu cầu id là **UUID v4**, `uuid5` không đúng → đổi sang `stable_v4` | `defaults.ids` |
| 4 | Chọn tầng 0 (`storey_index`) | **Chấp nhận.** Tầng có \|Elevation\| nhỏ nhất = 0, ghi đè bằng `ground_storey`; thiếu Elevation → placement Z → thứ tự file + cảnh báo | `storey.index_rule` |
| 5 | Tầng cho DXF | **Chấp nhận.** Lấy từ `project.yaml` (`inputs[].storey`), không suy từ tên file | `storey.dxf_source`, spec §3 |
| 6 | Regex mã phòng | **Chấp nhận.** `ref_pattern: ^[A-Za-z]{1,3}\d{1,4}$`; không khớp thì làm `name` (lựa chọn dự án) | `space.osm_common.ref_pattern` |
| 7 | Opening từ DXF | **Chấp nhận.** Tâm = điểm chèn, hướng = góc quay INSERT, bề rộng = độ dài LINE trong block `DOOR` | `door.geometry_source.dxf`, spec §4.2 |
| 8 | Regex tên phòng (NFD, false positive) | **Chấp nhận.** Chuẩn hoá NFC trước khi so khớp; neo ở đầu tên; cho phép ghi đè bằng `IfcSpace.ObjectType` | `defaults.labels`, `space.rules` |
| 9 | `ref` cho corridor | **Chấp nhận.** Corridor không gán `ref` (`osm_omit: [ref]`) | `space.rules[corridor]` |
| 10 | Ca chưa kiểm được trên mẫu | **Ghi nhận, hoãn.** Cần mẫu bổ sung (tường dày, `IfcStair`, thang máy, `IfcWindow`, Pset cửa, IFC2X3, ATTRIB trên INSERT, layer tiếng Việt, georeference). Giữ nhãn `unverified` trong config | spec §11; việc của laptop sau TASK-007 |

## 7. Kiểm tra đã làm (claude-mobile)

Chạy `layer_mapping.yaml` trên `samples/sample-floor-1.dxf` (ezdxf, schema DXF, `$INSUNITS = 6`): mọi entity đều khớp đúng rule, không có entity nào `UNMATCHED`:

| Layer | Loại | Rule | Số lượng |
|---|---|---|---|
| `A-AREA` | LWPOLYLINE | `space-boundary` | 13 |
| `A-AREA-IDEN` | TEXT | `space-label` | 13 |
| `A-DOOR` | INSERT | `door` | 12 |
| `A-WALL` | LINE / LWPOLYLINE | `wall` | 12 / 1 |

Khớp số liệu trong `samples/README.md`. `tag_mapping.yaml` mới chỉ kiểm cú pháp YAML; chưa chạy trên IFC.
