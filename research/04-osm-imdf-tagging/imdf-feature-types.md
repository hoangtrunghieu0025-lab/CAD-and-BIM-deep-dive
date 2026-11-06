# IMDF 1.0.0 — feature type và thuộc tính

- **Câu hỏi nghiên cứu**: Các feature IMDF trong bảng PRIMARY_OBJECTIVE có đúng không, thuộc tính bắt buộc/nullable là gì, tường và cửa mô hình hoá ra sao?
- **Kết luận ngắn**: IMDF 1.0.0 có đúng **16 feature_type** (đã xác minh từng trang): `address`, `amenity`, `anchor`, `building`, `detail`, `fixture`, `footprint`, `geofence`, `kiosk`, `level`, `occupant`, `opening`, `relationship`, `section`, `unit`, `venue`. Tường floor-to-ceiling **phải** là `unit` category `structure` (có thể dùng category vật liệu `brick`/`concrete`/`drywall`/`glass`/`wood`); `fixture` là tài sản di động/bán cố định, không phải tường kết cấu. `building`, `occupant`, `address` có geometry **null**; `opening` là **LineString**.
- **Độ tin cậy**: **cao** — đối chiếu trực tiếp 16 trang `types/*` và trang `reference/categories`, `reference/reference` trên `register.apple.com` (đọc 2026-11-06 11:00–11:20 GMT+7). Mục "Chưa xác minh" ở cuối nói rõ phần còn thiếu.
- **Trạng thái xác minh**: ĐÃ XÁC MINH với spec gốc (TASK-012, claude-laptop). Thay thế bản cũ viết theo trí nhớ.

## Chi tiết

### Quy ước chung (đã xác minh)
- Mỗi feature là GeoJSON `Feature` (RFC 7946) có `id` (FEATURE-ID = UUID), `type: "Feature"`, `feature_type`, `geometry`, `properties`.
- Kiểu `null or X` trong cột "Kiểu" nghĩa là **nullable**; không có "null or" nghĩa là **bắt buộc khác null**.
- Tham chiếu khoá ngoại có kiểu riêng: `LEVEL-ID`, `UNIT-ID`, `BUILDING-ID`, `ANCHOR-ID`, `ADDRESS-ID`… (đều là UUID của feature thuộc layer tương ứng, phải tồn tại).
- Gói giao hàng và `manifest.json`: xem `imdf-relations-and-constraints.md`.

### Bảng feature (đã xác minh; nguồn: `https://register.apple.com/resources/imdf/types/<feature>`)

| Feature | Geometry | Thuộc tính (nullable ghi `?`) |
|---|---|---|
| address | **null** | `address`, `unit?`, `locality`, `province?` (ISO 3166-2), `country` (ISO 3166), `postal_code?`, `postal_code_ext?`, `postal_code_vanity?` |
| amenity | Point | `category`, `accessibility?` (mảng), `name?`, `alt_name?`, `hours?`, `phone?`, `website?`, `unit_ids` (mảng UNIT-ID, bắt buộc), `address_id?`, `correlation_id?` |
| anchor | Point | `address_id?`, `unit_id` (bắt buộc) |
| building | **null** | `name?`, `alt_name?`, `category`, `restriction?`, `display_point?`, `address_id?` |
| detail | LineString (LINEAL) | `level_id` |
| fixture | Polygon (POLYGONAL) | `category`, `name?`, `alt_name?`, `anchor_id?`, `level_id`, `display_point?` |
| footprint | Polygon (POLYGONAL) | `category` (`aerial`/`ground`/`subterranean`), `name?`, `building_ids` (≥1, không trùng) |
| geofence | Polygon | `category`, `restriction?`, `name?`, `alt_name?`, `correlation_id?`, `display_point?`, `building_ids?`, `level_ids?`, `parents?` |
| kiosk | Polygon | `name?`, `alt_name?`, `anchor_id?`, `level_id`, `display_point?` |
| level | Polygon | `category`, `restriction?`, `outdoor` (bool), `ordinal` (integer), `name` (LABELS, bắt buộc), `short_name` (LABELS, bắt buộc), `display_point?`, `address_id?`, `building_ids?` |
| occupant | **null** | `name` (bắt buộc), `category`, `anchor_id` (bắt buộc), `hours?`, `phone?`, `website?`, `validity?`, `correlation_id?` |
| opening | **LineString** | `category`, `accessibility?`, `access_control?` (mảng), `door?` (object), `name?`, `alt_name?`, `display_point?`, `level_id` |
| relationship | null hoặc GEOMETRY | `category`, `direction` (`directed`/`undirected`), `origin?`, `intermediary?` (mảng), `destination?`, `hours?` (FEATURE-REFERENCE = `{id, feature_type}`) |
| section | Polygon | `category`, `restriction?`, `accessibility?`, `name?`, `alt_name?`, `display_point?`, `level_id`, `address_id?`, `correlation_id?`, `parents?` |
| unit | Polygon | `category`, `restriction?`, `accessibility?`, `name?`, `alt_name?`, `level_id`, `display_point?` |
| venue | Polygon | `category`, `restriction?`, `name` (bắt buộc), `alt_name?`, `hours?`, `phone?`, `website?`, `display_point` (bắt buộc), `address_id` (bắt buộc) |

Đối tượng `door` trong `opening` (ví dụ trong spec): `{"automatic": true, "material": "glass", "type": "sliding"}`. Giá trị của object `door` (đọc từ `reference/type_designators`, mục Door, TASK-015, 2026-11-06): `type` là null hoặc một trong `movablepartition`, `open`, `revolving`, `shutter`, `sliding`, `swinging`, `turnstile`, `turnstile.fullheight`, `turnstile.waistheight` (9 giá trị; bản trước của file này ghi thêm `door` và `unspecified` lấy từ trang categories, không thuộc danh sách của object); `automatic` là true, false hoặc null; `material` là null hoặc `wood`, `glass`, `metal`, `gate`. Cả ba member đều tuỳ chọn (MAY).

### Category (đã xác minh, nguồn: `.../reference/categories`)
- **unit** (63): `auditorium`, `brick`, `classroom`, `column`, `concrete`, `conferenceroom`, `drywall`, `elevator`, `escalator`, `fieldofplay`, `firstaid`, `fitnessroom`, `foodservice`, `footbridge`, `glass`, `huddleroom`, `kitchen`, `laboratory`, `library`, `lobby`, `lounge`, `mailroom`, `mothersroom`, `movietheater`, `movingwalkway`, `nonpublic`, `office`, `opentobelow`, `parking`, `phoneroom`, `platform`, `privatelounge`, `ramp`, `recreation`, `restroom` (+ `.family`, `.female`, `.female.wheelchair`, `.male`, `.male.wheelchair`, `.transgender`, `.transgender.wheelchair`, `.unisex`, `.unisex.wheelchair`, `.wheelchair`), `road`, `room`, `serverroom`, `shower`, `smokingarea`, `stairs`, `steps`, `storage`, `structure`, `terrace`, `theater`, `unenclosedarea`, `unspecified`, `vegetation`, `waitingroom`, `walkway`, `walkway.island`, `wood`.
- **fixture** (15): `baggagecarousel`, `boardinggate.desk`, `checkin.desk`, `checkin.kiosk`, `desk`, `equipment`, `furniture`, `immigration.desk`, `inspection.desk`, `obstruction`, `securityequipment`, `stage`, `vegetation`, `wall`, `water`.
- **opening** (7): `automobile`, `bicycle`, `emergencyexit`, `pedestrian`, `pedestrian.principal`, `pedestrian.transit`, `service`. (Bản cũ ghi sai `emergency`, `pedestrian.emergency`.)
- **building** (5): `parking`, `transit`, `transit.bus`, `transit.train`, `unspecified`.
- **level** (9): `arrivals`, `arrivals.domestic`, `arrivals.intl`, `departures`, `departures.domestic`, `departures.intl`, `parking`, `transit`, `unspecified`.
- **footprint** (3): `aerial`, `ground`, `subterranean`. **restriction** (2): `employeesonly`, `restricted`.
- **accessibility** (10): `assisted.listening`, `braille`, `hearing`, `hearingloop`, `signlanginterpreter`, `tactilepaving`, `tdd`, `trs`, `volume`, `wheelchair`. **access_control** (8): `badgereader`, `fingerprintreader`, `guard`, `keyaccess`, `outofservice`, `passwordaccess`, `retinascanner`, `voicerecognition`.
- **relationship** (7): `elevator`, `escalator`, `movingwalkway`, `ramp`, `stairs`, `traversal`, `traversal.path`. **geofence** (8): `concourse`, `geofence`, `paidarea`, `platform`, `postsecurity`, `presecurity`, `terminal`, `underconstruction`.
- **section** (71), **amenity** (172), **occupant** (≈1100), **venue** (22, **không phải 27** — bản trước đếm nhầm 5 dòng điều hướng của trang web): `airport`, `airport.intl`, `aquarium`, `businesscampus`, `casino`, `communitycenter`, `conventioncenter`, `governmentfacility`, `healthcarefacility`, `hotel`, `museum`, `parkingfacility`, `resort`, `retailstore`, `shoppingcenter`, `stadium`, `stripmall`, `theater`, `themepark`, `trainstation`, `transitstation`, `university` (đọc lại từ trang categories 2026-11-06 trong TASK-010; đã dùng trong `src/export/imdf_vocab.py`). Các nhóm còn lại không chép lại vì dài.

### Tường — quy tắc gốc (trang `types/unit`)
- "A network of floor-to-ceiling walls or an integrated system of walls and columns **MUST** be modeled as a `structure` Unit." Để mô tả vật liệu có thể dùng category `brick`, `concrete`, `drywall`, `glass`, `wood`. Cột đứng floor-to-ceiling **MUST** là `column` Unit.
- Tường có thể được **đơn giản hoá**: ranh giới unit đi theo mặt tường hoặc đường tưởng tượng; mô hình tường tường minh chỉ khi tường đáng kể về kiến trúc/kích thước ("MAY").
- `fixture` mô hình tài sản di động/bán cố định, bỏ đi không ảnh hưởng kết cấu toà nhà (trang `types/fixture`). Category `wall` có tồn tại trong danh sách `fixture`, nhưng không tìm thấy mô tả riêng cho nó; **suy luận từ định nghĩa fixture** (không ảnh hưởng kết cấu) thì nó chỉ dành cho vách/tường không kết cấu, còn tường kết cấu đi theo quy tắc `structure` ở trên (**suy luận, chưa có câu chữ xác nhận trực tiếp**).
- Opening mô hình vách không floor-to-ceiling kiểu quầy/pony wall (trang `types/opening`).
- Hệ quả cho pipeline: IfcWall kết cấu → `unit` category `structure` (hoặc vật liệu) nếu muốn có hình học tường; hoặc đơn giản hoá (ranh giới unit đi theo mặt tường, không xuất tường).

### Cửa → opening (trang `types/opening`)
- Opening mô hình "presence, location and physical extent (width) of an entrance"; geometry **LineString**, "MUST NOT be a multi-part feature"; độ dài **MUST** xấp xỉ bề rộng lối vào; một opening **MUST NOT** nối các space của hai unit khác nhau theo kiểu mơ hồ ("The same Opening MUST NOT model entrances to spaces modeled as different Units").
- Opening **MUST** được phủ bởi ranh giới của một Unit tại vị trí lối vào ("An Opening MUST be covered by a Unit boundary where the modeled entrance exists").

## Liên quan đến pipeline CAD → BIM → GPKG
- IfcSpace → `unit` (+ `level_id`), IfcBuildingStorey → `level` (`ordinal`, `name`, `short_name` bắt buộc), IfcBuilding → `building` (geometry null) + `footprint` (đường bao, `building_ids`), IfcDoor → `opening` (LineString = bề rộng cửa, `level_id` bắt buộc), IfcStair/IfcTransportElement → `unit` category `stairs`/`elevator`/`escalator`.
- `venue` và `address` là **bắt buộc** trong gói (xem `imdf-relations-and-constraints.md`): pipeline phải sinh `venue` (polygon bao tất cả feature) và ít nhất một `address` kể cả khi IFC thiếu → cần config/giá trị mặc định.
- `level.name` và `level.short_name` bắt buộc → lấy từ `IfcBuildingStorey.Name`/`LongName`.
- `id` UUID: spec yêu cầu "RFC 4122 §4.4 compliant **version 4** UUID" (`reference/type_designators`, đọc 2026-11-06). `uuid5` ổn định nhưng có version nibble = 5 → **không đúng chuẩn**; dùng UUID dạng v4 sinh xác định (`stable_v4`, xem `docs/cad-to-gpkg-design.md`). Cập nhật 2026-11-06 (claude-mobile) sau khi rà N-005.
- Feature geometry null (building, occupant, address, relationship thường): ghi thành bảng `attributes` trong GPKG bằng `pyogrio.write_dataframe(DataFrame thường)` (đã kiểm chứng, xem `geopackage-requirements.md`).

## Nguồn
- [IMDF index (version 1.0.0, last update 2021-10-19)](https://register.apple.com/resources/imdf/) — 2026-11-06
- [types/unit](https://register.apple.com/resources/imdf/types/unit), [fixture](https://register.apple.com/resources/imdf/types/fixture), [opening](https://register.apple.com/resources/imdf/types/opening), [level](https://register.apple.com/resources/imdf/types/level), [building](https://register.apple.com/resources/imdf/types/building), [footprint](https://register.apple.com/resources/imdf/types/footprint), [venue](https://register.apple.com/resources/imdf/types/venue) — 2026-11-06
- Các trang `types/` còn lại: address, amenity, anchor, detail, geofence, kiosk, occupant, relationship, section — 2026-11-06 (cùng gốc `https://register.apple.com/resources/imdf/types/<tên>`)
- [reference/categories](https://register.apple.com/resources/imdf/reference/categories) — 2026-11-06
- [reference/reference (archive, referential IDs)](https://register.apple.com/resources/imdf/reference/reference) — 2026-11-06
- [reference/extensions](https://register.apple.com/resources/imdf/reference/extensions) — 2026-11-06

## Chưa xác minh / câu hỏi mở
- Tập giá trị `material` của `door`; mô tả ngữ nghĩa từng category (trang categories chỉ liệt kê tên).
- Quy tắc validator chính thức của Apple (không tìm thấy công khai).
- Các category dài (amenity, occupant, venue, section) chưa chép lại; không cần cho phạm vi hiện tại.
