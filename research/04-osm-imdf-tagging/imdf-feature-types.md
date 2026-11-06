# IMDF 1.0.0 — feature type và thuộc tính

- **Câu hỏi nghiên cứu**: Các feature IMDF trong bảng PRIMARY_OBJECTIVE (venue, building, footprint, level, unit, opening, fixture, detail, amenity, occupant, anchor, address) có đúng không, thuộc tính bắt buộc là gì?
- **Kết luận ngắn**: Tất cả 12 feature trong bảng đều có thật. IMDF 1.0.0 có 16 feature_type: bảng thiếu `geofence`, `kiosk`, `relationship`, `section`. Hai điểm bảng chưa chính xác: `building` có geometry null (không phải polygon; polygon nằm ở `footprint`); tường trong IMDF thường là `unit` với category vật liệu chứ chưa chắc `fixture`.
- **Độ tin cậy**: thấp-trung bình. `register.apple.com` và `docs.ogc.org` không truy cập được; chỉ xác nhận được qua đoạn trích tìm kiếm: số lượng 16 feature_type, unit.level_id/category, opening LineString + `door`, building geometry null, name/short_name khác nhau theo feature. Bảng thuộc tính bên dưới dựa phần lớn vào trí nhớ → đánh dấu **[chưa xác minh]**; phải đối chiếu lại trên trang `types/<feature>`.

## Chi tiết

Quy ước chung (đã xác nhận một phần): GeoJSON, mỗi feature có `id` (UUID), `feature_type`, `geometry`, `properties`; `feature_type` phân biệt hoa thường, thuộc 1 trong 16 giá trị. IMDF 1.0.0 là OGC Community Standard (Apple News 2021-02-23).

16 feature_type: `address`, `amenity`, `anchor`, `building`, `detail`, `fixture`, `footprint`, `geofence`, `kiosk`, `level`, `occupant`, `opening`, `relationship`, `section`, `unit`, `venue` **[danh sách đầy đủ chưa xác minh từng tên; con số 16 đã xác nhận]**.

### Thuộc tính các feature dùng trong dự án (**[chưa xác minh]** trừ khi ghi khác)
"Bắt buộc" = thành viên phải có mặt trong `properties` (một số cho phép `null`). Cần kiểm lại cột nullable trong bản gốc.

| Feature | Geometry | Thuộc tính | Ghi chú |
|---|---|---|---|
| venue | Polygon/MultiPolygon | `category`, `restriction`, `name`, `alt_name`, `hours`, `phone`, `website`, `display_point`, `address_id` | `address_id` tham chiếu `address`; `hours` là chuỗi opening_hours kiểu OSM, `phone` E.164, `website` http/https (đã xác nhận qua đoạn trích OGC). |
| building | **null** (đã xác nhận) | `name`, `alt_name`, `category`, `restriction`, `display_point`, `address_id` | Hình học của building lấy từ `footprint.building_ids`. |
| footprint | Polygon/MultiPolygon | `category` (ground/aerial/subterranean), `name`, `building_ids` | Chỉ có `name` (không alt_name — đã xác nhận qua imdfjson). |
| level | Polygon/MultiPolygon | `category`, `restriction`, `outdoor`, `ordinal`, `name`, `short_name`, `display_point`, `address_id`, `building_ids` | `ordinal` số nguyên (0 = mặt đất, âm = tầng hầm); có `name` và `short_name` (đã xác nhận qua đoạn trích Apple/WWDC). |
| unit | Polygon/MultiPolygon | `category`, `restriction`, `accessibility`, `name`, `alt_name`, `level_id`, `display_point` | `level_id` đã xác nhận. |
| opening | **LineString** (đã xác nhận) | `category`, `accessibility`, `access_control`, `door`, `name`, `alt_name`, `display_point`, `level_id` | `door` là null hoặc object `{type, material, automatic}`; `type` ∈ swinging/sliding/revolving/turnstile… (đã xác nhận 4 giá trị đầu qua đoạn trích). Độ dài ≈ bề rộng lối đi; không multi-part. |
| fixture | Polygon (có thể LineString) | `category`, `name`, `alt_name`, `anchor_id`, `level_id`, `display_point` | Category cụ thể chưa nhớ chắc. |
| detail | LineString/Polygon | `level_id` | Nét chi tiết trang trí, không có category. |
| amenity | Point | `category`, `accessibility`, `name`, `alt_name`, `hours`, `phone`, `website`, `unit_ids`, `address_id`, `correlation_id` | |
| occupant | Point | `category`, `anchor_id`, `name`, `hours`, `phone`, `website`, `validity`, `correlation_id` | Gắn vào `anchor`. |
| anchor | Point | `address_id`, `unit_id` | |
| address | null | `address`, `unit`, `locality`, `province`, `country`, `postal_code`, `postal_code_ext`, `postal_code_vanity` | |

Thiếu trong bảng PRIMARY_OBJECTIVE: `section` (nhóm trong unit), `kiosk`, `geofence`, `relationship` (geometry null, lưu như file GeoJSON không geometry — theo imdfjson), cùng file `manifest.json`.

### Unit category — các giá trị dùng nhiều (**[chưa xác minh]** toàn bộ, trừ `walkway`, `nonpublic`, `walkway.island`, `conferenceroom`, `lobby`, `storage`... thấy trong tài liệu bên thứ ba)
`room`, `restroom`(+ biến thể `.male/.female/.unisex/.wheelchair`), `walkway`, `walkway.island`, `lobby`, `stairs`, `steps`, `elevator`, `escalator`, `movingwalkway`, `ramp`, `nonpublic`, `storage`, `parking`, `opentobelow`, `unenclosedarea`, `structure`, `column`, `unspecified`, và nhóm vật liệu tường `brick`, `concrete`, `drywall`, `glass`, `steelbeam`, `wood`. → Nếu đúng, bảng PRIMARY_OBJECTIVE nên ghi "tường → `unit` category vật liệu (hoặc `structure`)" thay vì mặc định `fixture`.

Opening category (nhớ): `pedestrian`, `pedestrian.principal`, `pedestrian.emergency`, `emergency`, `service`, `automobile`... **[chưa xác minh]**.

## Liên quan đến pipeline CAD → BIM → GPKG
- IfcSpace → unit (+ `level_id`), IfcBuildingStorey → level, IfcBuilding → building (không geometry) + footprint (đường bao), IfcDoor → opening (LineString = đoạn bề rộng cửa nằm trên biên unit), IfcStair/IfcTransportElement → unit category `stairs`/`elevator`.
- `id` UUID: dùng UUID ổn định (vd uuid5 từ IfcGloballyUniqueId); IFC GUID 22 ký tự base64 không phải UUID.
- Feature không geometry (building, address, relationship) → bảng thuộc tính trong GPKG (xem `geopackage-requirements.md`).

## Nguồn
- [IMDF Unit](https://register.apple.com/resources/imdf/types/unit) — 2026-11-06 (đoạn trích)
- [IMDF Opening](https://register.apple.com/resources/imdf/types/opening) — 2026-11-06 (đoạn trích)
- [IMDF Level](https://register.apple.com/resources/imdf/types/level) — 2026-11-06 (đoạn trích)
- [OGC IMDF 1.0.0 Reference](https://docs.ogc.org/cs/20-094/Reference/index.html) — 2026-11-06 (đoạn trích)
- [Apple News: IMDF OGC](https://developer.apple.com/news/?id=8lmz909p) — 2026-11-06
- [quuppalabs/imdfjson](https://github.com/quuppalabs/imdfjson) — 2026-11-06
- [IMDF-Builder-for-Places](https://github.com/davidhend/IMDF-Builder-for-Places) — 2026-11-06

## Câu hỏi còn mở
- Cột bắt buộc/nullable chính xác của từng feature; danh sách đầy đủ category của unit, opening, fixture, amenity, venue, building.
- Tường: unit vật liệu hay fixture? Cần đọc trang `types/fixture`, `types/unit`.
