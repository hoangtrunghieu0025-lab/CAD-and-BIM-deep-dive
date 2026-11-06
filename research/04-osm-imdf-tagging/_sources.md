# Log nguồn TASK-012 — research/04-osm-imdf-tagging

Cập nhật bởi claude-laptop, 2026-11-06 (máy local, `curl` mặc định, không giả User-Agent). Thay bản log vòng 2 của claude-mobile (khi đó mọi URL thất bại `ENOTFOUND`).

| URL | Dùng cho | Trạng thái |
|---|---|---|
| https://wiki.openstreetmap.org/w/index.php?title=Simple_Indoor_Tagging&action=raw | tag indoor | ĐÃ ĐỌC |
| https://wiki.openstreetmap.org/w/index.php?title=Tag:highway%3Delevator&action=raw | thang máy | ĐÃ ĐỌC |
| https://wiki.openstreetmap.org/w/index.php?title=Tag:highway%3Dsteps&action=raw | bậc thang | ĐÃ ĐỌC |
| https://wiki.openstreetmap.org/w/index.php?title=Tag:indoor%3Dlevel&action=raw ; ...title=Indoor&action=raw | chuyển hướng | ĐÃ ĐỌC (redirect về SIT / Key:indoor) |
| https://register.apple.com/resources/imdf/ | IMDF 1.0.0 | ĐÃ ĐỌC |
| https://register.apple.com/resources/imdf/types/{address,amenity,anchor,building,detail,fixture,footprint,geofence,kiosk,level,occupant,opening,relationship,section,unit,venue} | 16 feature type | ĐÃ ĐỌC (16/16) |
| https://register.apple.com/resources/imdf/reference/{categories,reference,extensions,geo_type_designators,type_designators} | category, gói giao hàng, extension, kiểu | ĐÃ ĐỌC |
| https://register.apple.com/resources/imdf/types/manifest | Manifest object | HTTP 404 (không có trang) |
| https://www.geopackage.org/spec/ (và /spec140/, /spec131/) | GeoPackage 1.4 | ĐÃ ĐỌC (HTML ~1,4 MB) |
| https://docs.ogc.org/cs/20-094/Reference/index.html | OGC IMDF | HTTP 200 nhưng trang ~435 byte (mục lục/redirect), không dùng |
| https://gdal.org/en/stable/drivers/vector/gpkg.html | GDAL driver | HTTP 429 (rate limit), chưa đọc |
| https://docs.qgis.org/... | QGIS manual | HTTP 200, chưa đọc nội dung; kiểm bằng PyQGIS thay thế |

Thực nghiệm (không phải URL): `pyogrio 0.13.0`/GDAL 3.12.4, `geopandas 1.2.0`, GDAL 3.8.4 (`ogrinfo`, `ogr2ogr`), `sqlite3`, PyQGIS (QGIS 3.44.7).

Nguồn bên thứ ba đã dùng ở vòng 1 (chưa đối chiếu, xem `imdf-relations-and-constraints.md` mục cuối): quuppalabs/imdfjson, davidhend/IMDF-Builder-for-Places, adap-c6-fingerprint/IMDFrnt PR #80, developer.apple.com/news/?id=8lmz909p.
