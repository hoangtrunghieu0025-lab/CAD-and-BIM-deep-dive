# Hệ toạ độ và đơn vị trong CAD/DXF

- **Câu hỏi nghiên cứu**: WCS/OCS/UCS là gì, đơn vị bản vẽ lưu ở đâu, và cần chuẩn hoá gì trước khi georeference?
- **Kết luận ngắn** (2–4 dòng): DXF lưu toạ độ ở WCS hoặc OCS (không bao giờ UCS); entity có extrusion ≠ (0,0,1) cần chuyển OCS→WCS (hoặc `ezdxf.upright`). Đơn vị nằm ở header `$INSUNITS` (`doc.units`) nhưng API ezdxf không có đơn vị và nhiều file để 0 (unitless) hoặc sai, nên phải cấu hình/kiểm tra thủ công. Toạ độ thường là cục bộ, không có CRS.
- **Độ tin cậy**: trung bình–cao — dựa trên tài liệu ezdxf và Autodesk DXF reference (qua kết quả tìm kiếm).

## Chi tiết

### WCS, OCS, UCS
- **WCS**: hệ toạ độ thế giới cố định, toạ độ cuối cùng cần có.
- **OCS**: hệ riêng của entity "phẳng" (CIRCLE, ARC, LWPOLYLINE, TEXT, INSERT…) xác định bởi vector extrusion qua thuật toán arbitrary axis; điểm lưu trong OCS để tiết kiệm. Extrusion (0,0,1) ⇒ OCS trùng WCS. ezdxf không tự chuyển OCS→WCS; dùng `entity.ocs().to_wcs(...)`. LWPOLYLINE có thêm `elevation`.
- **UCS**: hệ người dùng, chỉ phục vụ nhập liệu; file không ghi UCS đang dùng nên toạ độ trong DXF là WCS/OCS. `ezdxf.math.UCS` chuyển đổi khi cần.
- `ezdxf.upright` lật entity extrusion (0,0,-1) về (0,0,1) cho Circle/Arc/Ellipse, giúp tránh lỗi mirror khi dùng thư viện không hiểu OCS.
- Một số entity (ví dụ Ellipse) có extrusion nhưng không thiết lập OCS.

### Đơn vị
- `$INSUNITS` trong header = đơn vị chèn của model space; `doc.units` là shortcut (có validate). Giá trị: 0 unitless, 1 inch, 4 mm, 5 cm, 6 m (còn các giá trị khác trong enum `ezdxf.units`). Paper space và block layout dùng thuộc tính `units` của layout; `modelspace().units` luôn 0.
- Tham số này chỉ ảnh hưởng cách ứng dụng CAD diễn giải; **API ezdxf không có đơn vị** — toạ độ là số thuần.
- `ezdxf.units.conversion_factor(source, target)` cho hệ số quy đổi.
- `$MEASUREMENT` (imperial/metric) chỉ liên quan hatch pattern/linetype, không phải đơn vị chiều dài.
- Bản vẽ Việt Nam thường vẽ bằng mm (hoặc m/cm) — chưa xác minh tỉ lệ phổ biến; không nên tin `$INSUNITS` mà không kiểm tra bằng kích thước điển hình (cửa ~0.8–1.0 m, phòng ~3–6 m).

### Tỉ lệ và vị trí
- Model space vẽ tỉ lệ 1:1 theo đơn vị thiết kế; tỉ lệ in nằm ở viewport/dimension scale (`$DIMSCALE`, `$LTSCALE`) — không áp lên hình học.
- Toạ độ thường là cục bộ (gốc tuỳ ý) hoặc toạ độ lớn (hệ quốc gia cắt phần đầu) → độ chính xác float; nên trừ một điểm gốc trước khi tính hình học rồi cộng lại khi biến đổi CRS.
- Header có `$EXTMIN/$EXTMAX` (khung bao) để kiểm tra nhanh; có thể lỗi thời (chưa xác minh khi file bị sửa bằng script).
- Không có CRS chuẩn trong DXF thông thường. AutoCAD Map 3D/Civil 3D có thể lưu thông tin geographic location (chưa xác minh trong ezdxf) — nên không giả định.

## Liên quan đến pipeline CAD → BIM → GPKG
- Bước chuẩn hoá: đọc `doc.units`; nếu 0 thì lấy từ config dự án (`units: mm`) và quy đổi sang mét bằng `conversion_factor`; ghi đơn vị đã dùng vào metadata.
- Chuyển mọi entity sang WCS (OCS→WCS, `upright`), bỏ z hoặc giữ z làm `elevation` theo tầng.
- Georeference: DXF thiếu CRS ⇒ cần tham số bổ sung (điểm điều khiển ≥2 cho similarity transform, hoặc origin + rotation + CRS EPSG) trong config; chuyển bằng `pyproj`/`shapely.affinity`. Đây sẽ tương ứng với `IfcMapConversion`/`IfcProjectedCRS` nếu đi qua IFC.
- Validate: kiểm tra bounding box sau biến đổi có nằm trong vùng hợp lý (VN-2000/UTM hoặc WGS84).

## Nguồn
- [ezdxf — DXF Units](https://ezdxf.readthedocs.io/en/stable/concepts/units.html) — truy cập 2026-11-06 (qua kết quả tìm kiếm)
- [ezdxf — General Document how-to](https://ezdxf.readthedocs.io/en/stable/howto/document.html) — truy cập 2026-11-06
- [ezdxf — Coordinate Systems](https://ezdxf.readthedocs.io/en/stable/concepts/coordinates.html) — truy cập 2026-11-06
- [ezdxf — OCS](https://ezdxf.readthedocs.io/en/stable/concepts/ocs.html) — truy cập 2026-11-06
- [ezdxf — Tutorial for OCS/UCS usage](https://ezdxf.readthedocs.io/en/stable/tutorials/ocs_usage.html) — truy cập 2026-11-06
- [Autodesk — Object Coordinate Systems (OCS) in DXF](https://help.autodesk.com/cloudhelp/2018/ENU/AutoCAD-DXF/files/GUID-D99F1509-E4E4-47A3-8691-92EA07DC88F5.htm) — truy cập 2026-11-06

## Câu hỏi còn mở
- Thông tin geolocation trong DXF/DWG (GEODATA object) và ezdxf đọc được không (chưa xác minh).
- Đơn vị thực tế phổ biến của bản vẽ Việt Nam (cần mẫu thật).
- Ngưỡng làm tròn/snap phù hợp theo đơn vị.
