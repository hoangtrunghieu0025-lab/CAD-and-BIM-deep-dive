# Nguồn — TASK-005 (OSM / IMDF / GeoPackage / QGIS)

Ghi chú: ở phiên này các host sau KHÔNG truy cập được (lỗi DNS, ngoài danh sách domain cho phép): `wiki.openstreetmap.org`, `www.openstreetmap.org`, `register.apple.com`, `docs.ogc.org`, `www.geopackage.org`, `gdal.org`, `docs.qgis.org`, `docs.safe.com`. Các URL dưới đây được tìm thấy qua WebSearch (chỉ đọc được đoạn trích của máy tìm kiếm), trừ khi cột Chủ đề ghi "đã fetch". Cần mở các domain trên để xác minh bản gốc.

| Nguồn | URL | Chủ đề | Ngày truy cập |
|---|---|---|---|
| OSM Wiki — Simple Indoor Tagging (chỉ đoạn trích tìm kiếm) | https://wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging | indoor=room/area/corridor/wall, level:ref, repeat_on, door, stairs | 2026-11-06 |
| OSM Wiki — Tag:indoor=level (đoạn trích) | https://wiki.openstreetmap.org/wiki/Tag:indoor=level | level, repeat_on | 2026-11-06 |
| OSM Wiki — Tag:highway=elevator (đoạn trích) | https://wiki.openstreetmap.org/wiki/Tag:highway=elevator | thang máy, cửa thang máy, repeat_on | 2026-11-06 |
| OSM Wiki — Indoor (key) (đoạn trích) | https://wiki.openstreetmap.org/wiki/Indoor | indoor=* | 2026-11-06 |
| IMDF — Unit (đoạn trích) | https://register.apple.com/resources/imdf/types/unit | unit: level_id, category | 2026-11-06 |
| IMDF — Opening (đoạn trích) | https://register.apple.com/resources/imdf/types/opening | opening: LineString, door, độ dài ≈ bề rộng | 2026-11-06 |
| IMDF — Level (đoạn trích) | https://register.apple.com/resources/imdf/types/level | level | 2026-11-06 |
| IMDF — Type Designators (đoạn trích) | https://register.apple.com/resources/imdf/reference/type_designators | kiểu dữ liệu (UUID, WEBSITE, …) | 2026-11-06 |
| IMDF — Glossary (đoạn trích) | https://register.apple.com/resources/imdf/glossary | thuật ngữ, ví dụ | 2026-11-06 |
| OGC IMDF 1.0.0 Reference (đoạn trích) | https://docs.ogc.org/cs/20-094/Reference/index.html | 16 feature_type, quy tắc chung | 2026-11-06 |
| Apple Developer News — IMDF thành OGC Community Standard (đã fetch) | https://developer.apple.com/news/?id=8lmz909p | phiên bản IMDF 1.0.0, trạng thái OGC | 2026-11-06 |
| WWDC19 241 — Adding Indoor Maps to your App and Website (đoạn trích) | https://developer.apple.com/videos/play/wwdc2019/241/ | level/unit/opening mô tả, access_control | 2026-11-06 |
| quuppalabs/imdfjson README (đã fetch) | https://github.com/quuppalabs/imdfjson | relationship geometry null, name/alt_name/short_name khác nhau theo feature | 2026-11-06 |
| davidhend/IMDF-Builder-for-Places (đã fetch) | https://github.com/davidhend/IMDF-Builder-for-Places | gói zip IMDF, building geometry null, hole trong walkway, một số unit category | 2026-11-06 |
| adap-c6-fingerprint/IMDFrnt PR #80 (đã fetch) | https://github.com/adap-c6-fingerprint/IMDFrnt/pull/80 | quy tắc không gian: unit trong level, không chồng lấn, opening trên biên unit | 2026-11-06 |
| GeoPackage — Getting started (đoạn trích) | https://www.geopackage.org/guidance/getting-started | gpkg_spatial_ref_sys tối thiểu 3 dòng | 2026-11-06 |
| Rust crate geopackage test container.rs (đoạn trích) | https://docs.rs/crate/geopackage/0.3.0/source/tests/container.rs | application_id 0x47504B47, srs -1/0/4326 | 2026-11-06 |
| OGC GeoPackage 12-128r19 (CHƯA đọc được) | https://docs.ogc.org/is/12-128r19/12-128r19.html | đặc tả gốc — cần xác minh | 2026-11-06 |
| GDAL GeoPackage driver (CHƯA đọc được) | https://gdal.org/en/stable/drivers/vector/gpkg.html | layer creation options — cần xác minh | 2026-11-06 |
| QGIS manual — Opening data (CHƯA đọc được) | https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/opening_data.html | import gpkg — cần xác minh | 2026-11-06 |
