# IMDF — quan hệ giữa feature và ràng buộc

- **Câu hỏi nghiên cứu**: Khoá ngoại và ràng buộc hình học/nội dung nào IMDF yêu cầu, ảnh hưởng gì đến pipeline?
- **Kết luận ngắn**: Quan hệ qua `*_id`/`*_ids` (unit.level_id, level.building_ids, footprint.building_ids, opening.level_id, anchor.unit_id…). Ràng buộc không gian chính: unit nằm trong level, unit cùng level không chồng lấn, opening nằm trên biên unit. Toạ độ WGS84, ID UUID duy nhất.
- **Độ tin cậy**: trung bình-thấp. Quy tắc không gian được thấy trong một validator bên thứ ba (IMDFrnt PR #80), không phải spec gốc; spec Apple/OGC không fetch được.

## Chi tiết

### Quan hệ (từ bảng thuộc tính; [chưa xác minh] từng tên trừ ghi chú)
- `unit.level_id → level.id` (xác nhận); `opening.level_id → level.id`; `fixture.level_id`, `detail.level_id`.
- `level.building_ids → building.id` (mảng); `footprint.building_ids → building.id`.
- `building.address_id`, `venue.address_id`, `level.address_id`, `amenity.address_id → address.id`.
- `anchor.unit_id → unit.id`; `occupant.anchor_id → anchor.id`; `fixture.anchor_id`; `amenity.unit_ids → unit.id`.
- `relationship` (file GeoJSON geometry null) nối feature origin/intermediary/destination; không tham chiếu level (imdfjson ghi nhận).
- Bảng PRIMARY_OBJECTIVE ghi `level.building_ids → building.id` — đúng; nhưng chưa nêu venue↔building: quan hệ venue–building **không** có khoá ngoại rõ ràng trong các feature đã liệt kê; thường suy ra qua không gian/`footprint` — [chưa xác minh].

### Ràng buộc hình học và nội dung (nguồn: validator IMDFrnt + đoạn trích spec)
1. Mỗi unit nằm trong biên level tham chiếu.
2. Unit cùng level không chồng lấn diện tích; hợp của chúng nên phủ level (validator bên thứ ba đòi; spec gốc có thể chỉ khuyến nghị — chưa xác minh).
3. Opening nằm trên biên của một unit cùng level (xác nhận qua IMDFrnt); chiều dài ≈ bề rộng cửa; không multi-part (xác nhận qua spec trích).
4. Mỗi level cần ít nhất một opening, trừ trường hợp unit `nonpublic`/`walkway.island` phủ toàn level hoặc có amenity/unit thẳng đứng (elevator, escalator, movingwalkway, ramp, stairs).
5. UUID duy nhất; level cùng building có cùng `ordinal` và chồng diện tích → lỗi.
6. Building display point nằm trong footprint tham chiếu building đó.
7. Polygon: validator Microsoft Places yêu cầu bỏ lỗ (hole) trong walkway — ràng buộc của bên tiêu thụ, không phải IMDF.
8. Toạ độ WGS84 (GeoJSON, RFC 7946) [chưa xác minh trong spec, nhưng nhất quán với Builder-for-Places]; archive gồm `manifest.json` + `*.geojson` theo tên feature; Places từ chối file lạ.
9. `feature_type` phân biệt hoa thường; thuộc tính không nhận diện có thể bị từ chối bởi một số bên tiêu thụ (Places), IMDF cho phép mở rộng (vendor property) — hai điều này mâu thuẫn tuỳ consumer.
10. Manifest: ngôn ngữ mặc định phải khớp khoá nhãn `name` (vd `en-US`).

## Liên quan đến pipeline CAD → BIM → GPKG
- Sinh ID: tạo UUID cho tất cả feature trước, rồi điền khoá ngoại; lưu cột `*_id` dạng TEXT, `*_ids` dạng JSON text.
- Test tự động nên có: unit ⊂ level (shapely `within`/`covers` có dung sai), không chồng lấn (`intersection.area` < ε), opening `touches/intersects` biên unit, ID duy nhất, FK tồn tại.
- Dữ liệu từ IFC thường có khe hở giữa các IfcSpace (tường dày): cần snap/buffer trước khi kiểm "phủ level" — nếu pipeline coi tường là unit vật liệu thì khe được lấp.

## Nguồn
- [IMDFrnt PR #80](https://github.com/adap-c6-fingerprint/IMDFrnt/pull/80) — 2026-11-06
- [IMDF Opening](https://register.apple.com/resources/imdf/types/opening) — 2026-11-06 (đoạn trích)
- [quuppalabs/imdfjson](https://github.com/quuppalabs/imdfjson) — 2026-11-06
- [IMDF-Builder-for-Places](https://github.com/davidhend/IMDF-Builder-for-Places) — 2026-11-06
- [OGC IMDF 1.0.0 Reference](https://docs.ogc.org/cs/20-094/Reference/index.html) — 2026-11-06 (đoạn trích)

## Câu hỏi còn mở
- Quy tắc nào là bắt buộc trong spec và quy tắc nào chỉ là của validator/consumer?
- Quan hệ venue–building; cách biểu diễn `relationship` (origin/destination) cho thang máy/cầu thang.
- IMDF validator chính thức (Apple) có công khai không — chưa tìm thấy.
