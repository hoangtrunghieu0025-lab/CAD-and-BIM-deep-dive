# Parse và làm sạch DXF bằng ezdxf (+ shapely)

- **Câu hỏi nghiên cứu**: Quy trình đọc DXF bền vững, trích hình học, và làm sạch để dựng polygon phòng/tường là gì? Hạn chế ngữ nghĩa của CAD ảnh hưởng thế nào?
- **Kết luận ngắn** (2–4 dòng): Dùng `ezdxf.recover.readfile` (tự sửa + audit) rồi duyệt model space theo layer, phân rã INSERT bằng `virtual_entities()`/`disassemble`, chuyển OCS→WCS, xấp xỉ cung/spline bằng flattening, rồi làm sạch bằng shapely (`unary_union`, `polygonize`, `make_valid`, buffer nhỏ). CAD thiếu quan hệ nên ngữ nghĩa phải suy ra từ layer/block/text và kiểm chứng.
- **Độ tin cậy**: trung bình — API ezdxf lấy từ tài liệu (qua tìm kiếm); phần shapely/quy trình làm sạch là đề xuất thiết kế, chưa kiểm chứng trên dữ liệu thật (đánh dấu "chưa xác minh").

## Chi tiết

### 1. Nạp file
```python
import ezdxf
from ezdxf import recover
doc, auditor = recover.readfile("plan.dxf")   # sửa lỗi + audit tự động
if auditor.has_errors:
    auditor.print_error_report()
msp = doc.modelspace()
```
- `recover.readfile()` trả về `(doc, auditor)`; có thể ném `DXFStructureError` hoặc `UnicodeDecodeError` (khi `errors='strict'`); lỗi giải mã trong XRECORD được ghi là `AuditError.DECODE_ERRORS`. Một số file vẫn hỏng (ví dụ issue #836: HATCH edge type lạ từ Visio) — cần đường thoát (báo lỗi, đề xuất sửa bằng CAD).
- Ghi lại file đã recover có thể mất thông tin; pipeline chỉ đọc nên không cần ghi lại.
- DWG: dùng `odafc.readfile` (xem `dxf-dwg-formats.md`).

### 2. Truy vấn entity
- `msp.query('LWPOLYLINE[layer=="A-WALL"]')` hoặc lọc `e.dxf.layer` (cú pháp query: chưa kiểm chứng trong phiên này; có trong tài liệu ezdxf "Retrieve DXF entities").
- Nhóm theo `e.dxftype()`; thống kê layer × type để lập bảng mapping.

### 3. Phân rã block
- `insert.virtual_entities()` trả về entity đã áp biến đổi; đệ quy với block lồng. `ezdxf.disassemble` cho luồng phẳng và hàm lấy entity dưới dạng `Path`/`MeshBuilder` (tên hàm cụ thể: chưa xác minh trong phiên này). Không hỗ trợ XREF, ACIS, UNDERLAY, ACAD_TABLE, RAY, XLINE; không áp XCLIP.
- Thuộc tính: `insert.attribs`, `get_attrib_text(tag)`.

### 4. Hình học → shapely
| Entity | Cách chuyển |
|---|---|
| LINE | LineString 2 điểm |
| LWPOLYLINE | điểm (x, y) + bulge → cần chia cung; đóng nếu `closed` |
| ARC/CIRCLE/ELLIPSE/SPLINE | flatten thành đa tuyến (ezdxf `Path.flattening(distance)`, có từ 0.15.1; từng có báo cáo crash với POLYLINE – issue #663) |
| HATCH | các path biên → polygon (lỗ = boundary lồng) |
| TEXT/MTEXT | Point + chuỗi (MTEXT có mã định dạng cần làm sạch, ví dụ `plain_text()` — chưa xác minh tên) |
- Áp OCS→WCS và đơn vị trước (xem `coordinates-and-units.md`).
- Chọn `distance` flatten theo đơn vị (ví dụ 1 mm–10 mm).

### 5. Làm sạch hình học (đề xuất, chưa xác minh trên mẫu thật)
1. Loại điểm trùng, đoạn độ dài ~0, entity ngoài vùng bao bất thường (outlier cách xa gốc).
2. Snap đầu mút: làm tròn toạ độ theo lưới dung sai (ví dụ 1 mm) hoặc `shapely.set_precision`.
3. Nối line rời: `shapely.ops.linemerge`; làm nút giao: `unary_union` rồi `shapely.ops.polygonize` để dựng face; loại face rác (diện tích quá nhỏ), xác định face "ngoài".
4. Đóng khe nhỏ ở cửa/tường: buffer(+tol).buffer(−tol) hoặc nối thủ công theo vị trí INSERT cửa.
5. `shapely.make_valid`, kiểm `is_valid`, `is_empty`, loại self-intersection.
6. Gán thuộc tính cho polygon bằng `Point in Polygon` với TEXT/ATTRIB (tên/số phòng) và đa giác `A-AREA` nếu có.
7. Gán tầng: theo tên file, layer chứa số tầng, hoặc nhiều layout/khung bản vẽ trong một file (cần tách vùng).

### 6. Hạn chế ngữ nghĩa cần ghi nhận
- Không có quan hệ giữa đối tượng (cửa không "biết" nằm trong tường nào); tường thường là 2 đường song song, không phải polygon; ngữ nghĩa phụ thuộc đặt tên layer; cùng một mặt bằng có thể trùng lặp nét (đường vẽ đôi) — cần dedup.
- Annotation (kích thước, hatch trang trí) lẫn với hình học thật.
- Độ tin cậy suy luận phải được ghi (`confidence`/`source_layer`) vào thuộc tính để người dùng QC trong QGIS.

## Liên quan đến pipeline CAD → BIM → GPKG
- Mô-đun `ingest/` (recover + audit + units) → `cad2bim/` (mapping layer, polygonize, gán thuộc tính) → xuất dạng trung gian (GeoDataFrame theo `type`, CRS cục bộ) trước khi `extract/` georeference.
- Cần test với DXF mẫu nhỏ: (a) phòng khép kín, (b) khe hở ở cửa, (c) INSERT lồng, (d) OCS extrusion −Z, (e) đơn vị mm.
- Ghi vào output: `source_layer`, `source_handle` (`e.dxf.handle`) để truy vết về CAD gốc; handle là thuộc tính DXF — dùng cho trace, không phải ID ổn định giữa các phiên bản bản vẽ (chưa xác minh).

## Nguồn
- [ezdxf — Recover module](https://ezdxf.readthedocs.io/en/stable/drawing/recover.html) — truy cập 2026-11-06 (qua kết quả tìm kiếm)
- [ezdxf — Disassemble](https://ezdxf.readthedocs.io/en/stable/disassemble.html) — truy cập 2026-11-06
- [ezdxf — Insert](https://ezdxf.readthedocs.io/en/stable/blocks/insert.html) — truy cập 2026-11-06
- [ezdxf — Tutorial for Blocks](https://ezdxf.readthedocs.io/en/stable/tutorials/blocks.html) — truy cập 2026-11-06
- [ezdxf — Flatten entities task](https://ezdxf.readthedocs.io/en/stable/tasks/flatten_entities.html) — truy cập 2026-11-06 (nội dung chưa đọc được)
- [ezdxf issue #836 (recover fail HATCH)](https://github.com/mozman/ezdxf/issues/836) — truy cập 2026-11-06
- [ezdxf issue #663 (path.flattening crash)](https://github.com/mozman/ezdxf/issues/663) — truy cập 2026-11-06
- [ezdxf — General Document how-to](https://ezdxf.readthedocs.io/en/stable/howto/document.html) — truy cập 2026-11-06

## Câu hỏi còn mở
- Chưa đọc trực tiếp trang tutorial `getting_data` và `addons/drawing`/`path` (host readthedocs không fetch được); cần kiểm lại tên hàm trên bản ezdxf cài thực tế.
- Dung sai snap/flatten tối ưu; xử lý tường vẽ bằng 2 đường song song để ra footprint IfcWall.
- Hiệu năng với file lớn (hàng trăm nghìn entity) — chưa xác minh.
