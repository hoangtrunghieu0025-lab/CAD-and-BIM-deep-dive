# Hệ toạ độ và đơn vị trong CAD/DXF

- **Câu hỏi nghiên cứu**: WCS/OCS/UCS là gì, đơn vị bản vẽ lưu ở đâu, và cần chuẩn hoá gì trước khi georeference?
- **Kết luận ngắn** (2–4 dòng): DXF lưu toạ độ ở WCS hoặc OCS (không bao giờ UCS); entity có extrusion ≠ (0,0,1) cần chuyển OCS→WCS (hoặc `ezdxf.upright`). Đơn vị nằm ở header `$INSUNITS` (`doc.units`) nhưng API ezdxf không có đơn vị và nhiều file để 0 (unitless) hoặc sai, nên phải cấu hình/kiểm tra thủ công. Toạ độ thường là cục bộ, không có CRS.
- **Độ tin cậy**: cao cho phần ezdxf (đối chiếu docs `.rst` + mã nguồn trên GitHub, 2026-11-06; host readthedocs vẫn bị chặn DNS nên dùng `raw.githubusercontent.com/mozman/ezdxf/master`); trung bình cho phần Autodesk DXF reference (chưa mở lại trực tiếp).

## Chi tiết

### WCS, OCS, UCS
- **WCS**: hệ toạ độ thế giới cố định, toạ độ cuối cùng cần có.
- **OCS**: hệ riêng của entity "phẳng" (CIRCLE, ARC, LWPOLYLINE, TEXT, INSERT…) xác định bởi vector extrusion qua thuật toán arbitrary axis; điểm lưu trong OCS. Extrusion (0,0,1) ⇒ OCS trùng WCS. "Elevation" = khoảng cách từ mặt phẳng xy của entity đến gốc WCS/OCS (docs `concepts/ocs`); tạo OCS bằng `entity.ocs()`.
- **Đã xác minh** (`concepts/coordinates.rst`): "all coordinates stored in DXF files are always WCS or OCS never UCS"; ezdxf "does not automatically convert OCS into WCS" — dùng lớp `ezdxf.math.OCS` / `ezdxf.math.UCS`.
- `DXFGraphic.ocs() -> OCS` (đã xác minh, `entities/dxfgfx.py`): với entity có thuộc tính `extrusion` thì trả `OCS(extrusion)` (mặc định (0,0,1)); với entity không hỗ trợ OCS trả OCS "pass-through". `OCS.to_wcs(point)`, `OCS.from_wcs(point)`, `OCS.points_to_wcs(points)`, `OCS.points_from_wcs(points)` (đã xác minh, `math/ucs.py`). Ví dụ: `wcs = e.ocs().to_wcs(Vec3(x, y, e.dxf.elevation))` (ví dụ minh hoạ, chưa chạy thử).
- **UCS**: hệ người dùng, chỉ phục vụ nhập liệu; file không ghi UCS đang dùng ("no method to determine which UCS was active") nên toạ độ trong DXF là WCS/OCS.
- `ezdxf.upright` (đã xác minh, `upright.py`): `upright(entity) -> None` "flips an inverted OCS defined by extrusion vector (0, 0, -1)" về dạng (0,0,1); entity có extrusion khác hoặc không hỗ trợ bị bỏ qua im lặng; `upright_all(entities)` cho cả tập. Hỗ trợ: CIRCLE, ARC, SOLID, TRACE, LWPOLYLINE, HATCH, MPOLYGON, INSERT; ELLIPSE (chỉ lật vector extrusion); POLYLINE chỉ 2D. **Không dùng được** cho TEXT, MTEXT, DIMENSION hay entity chứa text. Lưu ý: `upright` sửa entity tại chỗ (mutate) — pipeline chỉ đọc nên dùng `to_wcs` hoặc làm trên bản sao.
- Ellipse "có extrusion nhưng không thiết lập OCS" (khẳng định cũ): chưa xác minh trực tiếp (docs `ocs` không nhắc Ellipse); chỉ biết `upright` xử lý Ellipse đặc biệt (chỉ lật extrusion).
- MLINE không phải entity OCS: mọi đỉnh là WCS (docs `dxfentities/mline`).

### Đơn vị
- `$INSUNITS` trong header = đơn vị của model space/tài liệu ("the most important setting"); `doc.units` là shortcut có validate, tương đương `doc.header['$INSUNITS']` (đã xác minh, `concepts/units.rst`). Giá trị (đã xác minh, `units.py`): 0 Unitless, 1 Inches, 2 Feet, 3 Miles, 4 Millimeters, 5 Centimeters, 6 Meters, 7 Kilometers, … 14 Decimeters, … 21–24 US Survey Feet/Inch/Yard/Mile; enum là `ezdxf.enums.InsertUnits`. Docs: "most common units are 6 for meters and 1 for inches".
- Docs: giá trị `units` của **modelspace layout** "always set to 0" (không phải đơn vị model space) — đơn vị model space đọc từ `doc.units`/`$INSUNITS`. (Phần "paper space/block layout dùng `units` của layout" trong bản cũ: chưa xác minh trực tiếp.)
- Tham số này chỉ ảnh hưởng cách ứng dụng CAD diễn giải; **API ezdxf không có đơn vị** — toạ độ là số thuần (khẳng định cũ, nhất quán với docs nhưng chưa có câu trích nguyên văn).
- `ezdxf.units.conversion_factor(source_units, target_units) -> float` (đã xác minh): ví dụ `conversion_factor(MM, CM)` = 0.1. **Cạm bẫy**: các giá trị 0 (unitless), 8, 9, 21–24 không có hệ số mét → `TypeError("Unsupported conversion.")` — phải xử lý trường hợp `doc.units == 0` bằng config trước khi gọi.
- `$MEASUREMENT` "controls whether the current drawing uses imperial or metric hatch pattern and linetype files", độc lập với `$INSUNITS` (đã xác minh).
- Bản vẽ Việt Nam thường vẽ bằng mm (hoặc m/cm) — chưa xác minh tỉ lệ phổ biến; không nên tin `$INSUNITS` mà không kiểm tra bằng kích thước điển hình (cửa ~0.8–1.0 m, phòng ~3–6 m).

### Tỉ lệ và vị trí
- Model space vẽ tỉ lệ 1:1 theo đơn vị thiết kế; tỉ lệ in nằm ở viewport/dimension scale (`$DIMSCALE`, `$LTSCALE`) — không áp lên hình học.
- Toạ độ thường là cục bộ (gốc tuỳ ý) hoặc toạ độ lớn (hệ quốc gia cắt phần đầu) → độ chính xác float; nên trừ một điểm gốc trước khi tính hình học rồi cộng lại khi biến đổi CRS.
- Header có `$EXTMIN/$EXTMAX` (khung bao) để kiểm tra nhanh; có thể lỗi thời (chưa xác minh khi file bị sửa bằng script).
- Không có CRS chuẩn trong DXF thông thường (khẳng định cũ, thực nghiệm; vẫn nên coi là mặc định).
- **GEODATA (đã xác minh có trong ezdxf)**: đối tượng `GEODATA` gắn với modelspace, cần DXF R2010 (AC1024) trở lên, nằm trong section OBJECTS, liên kết qua extension dictionary của BLOCK_RECORD modelspace. Đọc bằng `doc.modelspace().get_geodata() -> Optional[GeoData]` (trả `None` nếu không có); tạo bằng `new_geodata(dxfattribs=None)`. Thuộc tính: `coordinate_type` (unknown / local grid / projected grid / geographic), `coordinate_system_definition` (chuỗi XML định nghĩa CRS, gồm số EPSG và thứ tự trục), `design_point` (WCS), `reference_point` (toạ độ địa lý, chỉ dùng với local grid), `north_direction` (vector 2D, góc xoay quanh design point), `source_vertices`/`target_vertices` (cặp đỉnh 2D để biến đổi sang WGS84, EPSG:4326). Phần nào của biến đổi dùng được và độ phủ thực tế ở file Việt Nam / Civil 3D: chưa xác minh, cần mẫu thật. Không giả định file có GEODATA.

## Liên quan đến pipeline CAD → BIM → GPKG
- Bước chuẩn hoá: đọc `doc.units`; nếu 0 thì lấy từ config dự án (`units: mm`) và quy đổi sang mét bằng `conversion_factor` (không gọi với 0 — sẽ `TypeError`); ghi đơn vị đã dùng vào metadata.
- Thử `modelspace().get_geodata()`: nếu có, dùng làm gợi ý georeference (kèm xác nhận của người dùng); nếu `None`, dùng tham số config.
- Chuyển mọi entity sang WCS (`ocs().to_wcs`, hoặc `upright` cho entity được hỗ trợ — TEXT/MTEXT/DIMENSION phải dùng `to_wcs`), bỏ z hoặc giữ z làm `elevation` theo tầng.
- Georeference: DXF thiếu CRS ⇒ cần tham số bổ sung (điểm điều khiển ≥2 cho similarity transform, hoặc origin + rotation + CRS EPSG) trong config; chuyển bằng `pyproj`/`shapely.affinity`. Đây sẽ tương ứng với `IfcMapConversion`/`IfcProjectedCRS` nếu đi qua IFC.
- Validate: kiểm tra bounding box sau biến đổi có nằm trong vùng hợp lý (VN-2000/UTM hoặc WGS84).

## Nguồn
- [ezdxf `docs/source/concepts/units.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/concepts/units.rst) (nguồn của https://ezdxf.readthedocs.io/en/stable/concepts/units.html) — truy cập 2026-11-06
- [ezdxf `src/ezdxf/units.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/units.py) — truy cập 2026-11-06
- [ezdxf `docs/source/concepts/coordinates.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/concepts/coordinates.rst) — truy cập 2026-11-06
- [ezdxf `docs/source/concepts/ocs.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/concepts/ocs.rst) — truy cập 2026-11-06
- [ezdxf `src/ezdxf/entities/dxfgfx.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/dxfgfx.py) (`ocs()`) — truy cập 2026-11-06
- [ezdxf `src/ezdxf/math/ucs.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/math/ucs.py) (`OCS.to_wcs`…) — truy cập 2026-11-06
- [ezdxf `src/ezdxf/upright.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/upright.py), [`docs/source/upright.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/upright.rst) — truy cập 2026-11-06
- [ezdxf `docs/source/dxfobjects/geodata.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/dxfobjects/geodata.rst), [`src/ezdxf/layouts/layout.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/layouts/layout.py) (`get_geodata`/`new_geodata`) — truy cập 2026-11-06
- [ezdxf — Tutorial for OCS/UCS usage](https://ezdxf.readthedocs.io/en/stable/tutorials/ocs_usage.html) — truy cập 2026-11-06 (vòng 1, qua tìm kiếm; chưa mở lại)
- [Autodesk — Object Coordinate Systems (OCS) in DXF](https://help.autodesk.com/cloudhelp/2018/ENU/AutoCAD-DXF/files/GUID-D99F1509-E4E4-47A3-8691-92EA07DC88F5.htm) — truy cập 2026-11-06 (vòng 1, chưa mở lại)

## Câu hỏi còn mở
- GEODATA: tồn tại và đọc được trong ezdxf (đã xác minh); còn mở: file thực tế (Civil 3D/Map 3D, Việt Nam) có điền không, và cách dùng `source_vertices`/`target_vertices`.
- `$EXTMIN/$EXTMAX` có thể lỗi thời và các giá trị `units` của paper space/block layout: chưa xác minh.
- Đơn vị thực tế phổ biến của bản vẽ Việt Nam (cần mẫu thật).
- Ngưỡng làm tròn/snap phù hợp theo đơn vị.
