# IMDF — quan hệ giữa feature, ràng buộc và gói giao hàng

- **Câu hỏi nghiên cứu**: Khoá ngoại, ràng buộc hình học/nội dung và cấu trúc gói nào IMDF yêu cầu, ảnh hưởng gì đến pipeline?
- **Kết luận ngắn**: Quan hệ qua `*_id`/`*_ids` (đã xác minh từ bảng thuộc tính các trang `types/*`). Ràng buộc không gian trong spec dùng MUST: unit nằm trong level; **các unit cùng level không được có symmetrical difference với level** (tức hợp các unit phải phủ kín level); opening phải được phủ bởi ranh giới một unit; mọi feature nằm trong polygon venue. Gói giao hàng là ZIP gồm `manifest.json` + các file `*.geojson`; **chỉ `manifest.json`, `address.geojson`, `venue.geojson` là bắt buộc**.
- **Độ tin cậy**: **cao** cho nội dung trích từ spec gốc (`register.apple.com`, đọc 2026-11-06); các quy tắc của validator/consumer bên thứ ba tách riêng ở mục cuối, **chưa xác minh với spec**.
- **Trạng thái xác minh**: ĐÃ XÁC MINH phần spec (TASK-012, claude-laptop). Thay bản cũ dựa vào validator bên thứ ba.

## Chi tiết

### Quan hệ khoá ngoại (đã xác minh từ các trang `types/*`)
| Từ | Thuộc tính | Tới | Nullable / bội số |
|---|---|---|---|
| unit, opening, fixture, kiosk, detail, section | `level_id` | level | bắt buộc |
| level | `building_ids` | building | nullable (mảng) |
| footprint | `building_ids` | building | bắt buộc, ≥1, không trùng |
| venue | `address_id` | address | **bắt buộc** |
| building, level, section, amenity, anchor | `address_id` | address | nullable |
| anchor | `unit_id` | unit | bắt buộc |
| amenity | `unit_ids` | unit | bắt buộc (mảng) |
| occupant, fixture, kiosk | `anchor_id` | anchor | occupant: bắt buộc; fixture/kiosk: nullable |
| geofence | `building_ids`, `level_ids`, `parents` | building, level, geofence | nullable (mảng) |
| section | `parents` | section | nullable (mảng) |
| relationship | `origin`, `intermediary`, `destination` | FEATURE-REFERENCE `{id, feature_type}` | nullable; "MUST be specified if destination is null / origin is null" |

- **Quan hệ venue–building không có khoá ngoại**: spec dùng quan hệ **không gian** — "ALL other features MUST be within the polygonal boundary of the Venue" (trang `types/venue`). Building nối qua `footprint.building_ids` và `level.building_ids`.
- `building.display_point` "MUST be located within a Footprint referencing the Building" (trang `types/building`).
- Khi Venue và Building là một thì tên đặt ở Venue, Building MAY có name null (trang `types/venue`).

### Ràng buộc hình học và nội dung (MUST/SHOULD trích từ spec)
1. **Unit ⊂ Level**: "each Unit MUST be within its respective Level boundary" (`types/level`).
2. **Unit phủ kín Level, không chồng**: "Symmetrical difference MUST NOT exist among Units that reference the same Level" và "between the union of Units and their referenced Level" (`types/unit`, `types/level`). Hệ quả: khe giữa các IfcSpace (do tường dày) **phải được lấp** (bằng unit `structure`/vật liệu hoặc bằng cách snap ranh giới unit ra mặt/tim tường).
3. **Opening**: geometry LineString không multi-part; độ dài xấp xỉ bề rộng lối vào; "MUST be covered by a Unit boundary where the modeled entrance exists"; không nối hai unit khác nhau theo một opening duy nhất (`types/opening`).
4. **Mỗi Level phải được tham chiếu bởi ít nhất một Opening**, ngoại lệ: Level trùng với một unit `nonpublic` hoặc `walkway.island`, hoặc có Amenity mô hình khả năng di chuyển thẳng đứng nằm trong Level (`types/level`). Unit `stairs`/`elevator`/`escalator`... "MUST have at least one Opening when the Unit models a vertical traversal capability to a different Level" (`types/opening`, phần quy tắc theo category).
5. **Level**: phải tham chiếu Building nếu nằm trong hoặc thuộc kết cấu toà nhà; `outdoor=false` nếu bên trong toà nhà, `true` nếu bên ngoài; `ordinal=0` cho tầng thấp nhất có lối vào mặt đất, `-1` cho tầng ngầm sát mặt đất; hai Level cùng Building và cùng `ordinal` không được chồng/nằm trong nhau (`types/level`).
6. **Footprint**: `building_ids` ≥1, không trùng; `ground` footprint phải phủ phần các tầng "lộ ra" ở mặt đất khi địa hình dốc (`types/footprint`, `types/level`).
7. **Relationship** (dùng cho đi một chiều qua opening): `category="traversal"`, `direction="directed"`, `intermediary` tham chiếu Opening, `origin`/`destination` là hai Unit hai bên Opening (`types/relationship`).
8. `feature_type` đúng 1 trong 16 giá trị; `id` là UUID (FEATURE-ID). *Tính duy nhất toàn cục của UUID*: chưa tìm thấy câu MUST rõ ràng trong các trang đã đọc.

### Gói giao hàng (đã xác minh, trang `reference/reference`)
- "Datasets MUST be delivered as ZIP compressed archives using the `.zip` filename extension."
- "Archives MUST contain a Manifest object supplied in a dedicated file named `manifest.json`."
- "Features MUST be packaged as homogenous GeoJSON FeatureCollections in dedicated files using the `.geojson` filename extension."
- File **bắt buộc**: `manifest.json`, `address.geojson`, `venue.geojson` ("FeatureCollection of the lone Venue feature"). File **tuỳ chọn**: `amenity`, `anchor`, `building`, `detail`, `fixture`, `footprint`, `kiosk`, `level`, `occupant`, `opening`, `relationship`, `section`, `geofence`, `unit` (mỗi cái `<tên>.geojson`).
- Manifest: ví dụ trong trang `reference/extensions` có các khoá `version` ("1.0.0"), `created` (ISO date-time, không múi giờ), `language` ("en-US"), `generated_by` (nullable), `extensions` (mảng Extension Identifier, tuỳ chọn). Định nghĩa đầy đủ của Manifest object **chưa tìm thấy trang riêng** (`types/manifest` trả 404) → chỉ dựa vào ví dụ.
- Mở rộng: Extension Identifier dạng `imdf:extension:<provider>:<name>#<version>`; extension "MUST NOT change the semantics of Feature types, Feature members or properties" của spec (`reference/extensions`). → thêm cột lạ (vd `global_id`) vào layer IMDF phải khai báo extension hoặc tách ra bảng riêng khi xuất IMDF.

### Quy tắc của bên thứ ba — CHƯA XÁC MINH với spec (giữ từ bản cũ)
- Validator IMDFrnt PR #80 (adap-c6-fingerprint): các kiểm tra hình học bổ sung (display point trong footprint, level cùng ordinal chồng diện tích…). Một phần trùng với spec ở trên; phần còn lại chưa đối chiếu.
- Microsoft Places yêu cầu bỏ lỗ (hole) trong walkway; Places từ chối file/thuộc tính lạ — ràng buộc của bên tiêu thụ, không phải IMDF.
- Khẳng định "thuộc tính không nhận diện có thể bị từ chối bởi consumer" mâu thuẫn với cơ chế extension: coi là ràng buộc của từng consumer.

## Liên quan đến pipeline CAD → BIM → GPKG
- Sinh ID: tạo UUID cho tất cả feature trước, rồi điền khoá ngoại; `*_id` TEXT, `*_ids` JSON text (xem `geopackage-requirements.md`).
- Test tự động nên có (theo spec): unit ⊂ level (shapely `within`/`covers`, dung sai); không chồng lấn và **hợp unit = level** (symmetrical difference ≈ 0 trong dung sai; spec cho phép "discernible" tới 0,2 m ở tỉ lệ 1:500 giữa hai Level — là dung sai giữa các Level, không phải giữa unit và level); opening cắt/nằm trên biên unit; mọi FK tồn tại; level có ≥1 opening (trừ ngoại lệ); `venue` và `address` có mặt.
- Bắt buộc sinh `venue` (polygon bao hết) + `address` + `manifest.json` khi xuất IMDF; GPKG chỉ là dạng lưu trữ trung gian, cần bước xuất ZIP riêng nếu muốn gói IMDF thật.
- IFC thường có khe giữa IfcSpace: để thoả "phủ kín level", cần chiến lược lấp khe (unit `structure` cho tường, hoặc snap) — quyết định thiết kế cho TASK-007/009.

## Nguồn
- [IMDF types/unit](https://register.apple.com/resources/imdf/types/unit), [level](https://register.apple.com/resources/imdf/types/level), [opening](https://register.apple.com/resources/imdf/types/opening), [venue](https://register.apple.com/resources/imdf/types/venue), [building](https://register.apple.com/resources/imdf/types/building), [footprint](https://register.apple.com/resources/imdf/types/footprint), [relationship](https://register.apple.com/resources/imdf/types/relationship) — 2026-11-06
- [IMDF reference/reference](https://register.apple.com/resources/imdf/reference/reference) — 2026-11-06
- [IMDF reference/extensions](https://register.apple.com/resources/imdf/reference/extensions) — 2026-11-06
- (Bên thứ ba, chưa đối chiếu) [IMDFrnt PR #80](https://github.com/adap-c6-fingerprint/IMDFrnt/pull/80), [quuppalabs/imdfjson](https://github.com/quuppalabs/imdfjson), [IMDF-Builder-for-Places](https://github.com/davidhend/IMDF-Builder-for-Places) — 2026-11-06

## Chưa xác minh / câu hỏi mở
- Định nghĩa đầy đủ của Manifest object (chỉ có ví dụ); quy tắc tính duy nhất UUID; có validator chính thức công khai của Apple không (chưa tìm thấy).
- Cách biểu diễn `relationship` cho thang máy/cầu thang nhiều tầng (có mục "vertical traversal" trong trang `types/relationship`, chưa đọc chi tiết).
