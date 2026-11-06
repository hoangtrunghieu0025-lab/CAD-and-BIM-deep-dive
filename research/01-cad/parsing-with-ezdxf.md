# Parse và làm sạch DXF bằng ezdxf (+ shapely)

- **Câu hỏi nghiên cứu**: Quy trình đọc DXF bền vững, trích hình học, và làm sạch để dựng polygon phòng/tường là gì? Hạn chế ngữ nghĩa của CAD ảnh hưởng thế nào?
- **Kết luận ngắn** (2–4 dòng): Dùng `ezdxf.recover.readfile` (tự sửa + audit; chỉ ASCII DXF) rồi duyệt model space theo layer, phân rã INSERT bằng `ezdxf.disassemble.recursive_decompose` (đệ quy, đã xác minh) hoặc `insert.virtual_entities()` (một cấp, MINSERT cần xử lý riêng), chuyển OCS→WCS bằng `entity.ocs().to_wcs(...)` hoặc `ezdxf.upright`, xấp xỉ cung/spline bằng `Path.flattening(distance)`, rồi làm sạch bằng shapely. CAD thiếu quan hệ nên ngữ nghĩa phải suy ra từ layer/block/text và kiểm chứng.
- **Độ tin cậy**: cao cho phần API ezdxf (đã đối chiếu docs `.rst` và mã nguồn gốc trên GitHub, 2026-11-06); phần shapely/quy trình làm sạch là đề xuất thiết kế, chưa kiểm chứng trên dữ liệu thật (đánh dấu "chưa xác minh").
- **Ghi chú kiểm chứng (vòng 2)**: `ezdxf.readthedocs.io` vẫn không phân giải DNS trong phiên này; thay bằng nguồn gốc cùng tác giả: `raw.githubusercontent.com/mozman/ezdxf/master/docs/source/*.rst` (tài liệu) và `src/ezdxf/*.py` (docstring/chữ ký). Là nhánh `master`, có thể lệch bản đã phát hành — nên kiểm lại trên bản ezdxf cài thực tế.

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
- `recover.readfile(filename, errors=...)` trả về `(doc, auditor)`. Ngoại lệ (đã xác minh): `IOError` (không phải DXF / lỗi I/O), `ezdxf.DXFStructureError` (file hỏng), `UnicodeDecodeError` (chỉ khi `errors='strict'`). Ở chế độ mặc định, lỗi giải mã không ném ngoại lệ mà ghi `AuditError.DECODE_ERRORS` vào `Auditor.errors`; `errors='ignore'` ghi `AuditError.DECODING_ERROR` kèm số dòng gần đúng.
- **Chỉ hỗ trợ ASCII DXF** (docs). Chậm hơn `ezdxf.readfile` → nên thử đường nhanh trước, `recover` khi lỗi. Còn có `recover.read` và `recover.explore` (trang docs không mô tả chữ ký/ý nghĩa đầy đủ).
- File có dữ liệu nhị phân (thường trong XRECORD) có thể nạp được nhưng ghi lại có thể tạo DXF hỏng/mất thông tin → pipeline chỉ đọc nên không ghi lại.
- Một số file vẫn hỏng (ví dụ issue #836: HATCH edge type lạ từ Visio — chưa mở lại issue vòng này) — cần đường thoát (báo lỗi, đề xuất sửa bằng CAD).
- DWG: dùng `odafc.readfile` (xem `dxf-dwg-formats.md`).

### 2. Truy vấn entity
- Cú pháp query (đã xác minh, tutorial `getting_data`): `EntityQuery[AttributeQuery]`; phần entity là danh sách tên DXF viết HOA cách nhau bởi khoảng trắng hoặc `*`, tiền tố `!` để loại (`* !LINE`); phần thuộc tính là biểu thức boolean với `and`, `or`, `!`. Ví dụ: `msp.query('LINE[layer=="construction"]')`, `msp.query('*[layer=="construction" and linetype!="DASHED"]')`; có thể nối `result.query(...)`.
- Hoặc lọc `e.dxf.layer` bằng Python. Layer có `is_off()`, `is_frozen()`, `is_locked()` (đã xác minh trong `entities/layer.py`).
- Nhóm theo `e.dxftype()`; thống kê layer × type để lập bảng mapping.

### 3. Phân rã block
- `insert.virtual_entities(*, skipped_entity_callback=None, redraw_order=False)` — "yields the transformed referenced block content as virtual entities" (đã xác minh). **MINSERT**: method không giải thuộc tính MINSERT, chỉ trả sub-entity của INSERT đầu tiên; cần kiểm `insert.mcount > 1` và tự xử lý lưới (đã xác minh).
- `insert.explode(target_layout=None, *, redraw_order=False) -> EntityQuery`: tạo entity thật trong layout đích (sửa bản vẽ → không dùng cho pipeline chỉ đọc). Việc INSERT gốc có bị huỷ hay không: docstring bị cắt trong nội dung đọc được → chưa xác minh.
- Đệ quy block lồng: `ezdxf.disassemble.recursive_decompose(entities) -> Iterable[DXFEntity]` (đã xác minh: "flat stream of DXF entities"; INSERT có `mcount > 1` được khai triển MINSERT; yield ATTRIB của INSERT rồi decompose virtual entities). Việc `virtual_entities()` tự đệ quy qua INSERT lồng: chưa xác minh — dùng `recursive_decompose`.
- Các hàm khác trong `ezdxf.disassemble` (đã xác minh tên): `make_primitive`, `to_primitives(entities, max_flattening_distance=None)`, `to_meshes`, `to_paths(primitives)`, `to_vertices(primitives)`, `to_control_vertices`; lớp `Primitive` (thuộc tính `entity`, `max_flattening_distance`, `path`, `mesh`, `is_empty`; phương thức `vertices()`, `bbox()`).
- **Không hỗ trợ** (docs): "all ACIS based entities, XREF, UNDERLAY, ACAD_TABLE, RAY, XLINE"; entity không hỗ trợ bị bỏ qua (thành primitive rỗng). Từ mã nguồn: cũng không hỗ trợ SHAPE; MTEXT nhúng trong ATTRIB/ATTDEF chưa hỗ trợ. `recursive_decompose` **không áp XCLIP** (docstring mã nguồn; trang docs không nhắc XCLIP).
- Thuộc tính: `insert.attribs` (list[Attrib]), `get_attrib(tag, search_const=False)`, `get_attrib_text(tag, default="", search_const=False)`.
- MLINE: `mline.virtual_entities()` trả LINE, ARC, HATCH (xem `layers-blocks-xref.md`).

### 4. Hình học → shapely
| Entity | Cách chuyển |
|---|---|
| LINE | LineString 2 điểm |
| LWPOLYLINE | điểm (x, y) + bulge → cần chia cung; đóng nếu `closed` |
| ARC/CIRCLE/ELLIPSE/SPLINE | flatten thành đa tuyến bằng `Path.flattening(distance, segments=4)` (đã xác minh chữ ký, adaptive recursive; trả `Iterator[Vec3]`; không trả đỉnh nào cho path rỗng; multi-path thì khe hở không phân biệt được với đoạn thẳng). Có `Path.sub_paths()` để tách single-path, `Path.has_curves`. Báo cáo crash với POLYLINE – issue #663 (chưa mở lại) |
| HATCH | các path biên → polygon (lỗ = boundary lồng) |
| TEXT/MTEXT | Point + chuỗi. MTEXT: `MText.plain_text(split=False, fast=True)` trả text không có mã định dạng (đã xác minh; `fast=False` dùng `ezdxf.tools.text.plain_mtext`) |
- Trang docs "Flatten entities" (`tasks/flatten_entities`) chỉ là placeholder TODO — không dùng làm nguồn.
- Áp OCS→WCS và đơn vị trước (xem `coordinates-and-units.md`).
- Chọn `distance` flatten theo đơn vị (ví dụ 1 mm–10 mm) — đề xuất, chưa xác minh.

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
- Cần test với DXF mẫu nhỏ: (a) phòng khép kín, (b) khe hở ở cửa, (c) INSERT lồng, (d) OCS extrusion −Z, (e) đơn vị mm, (f) MINSERT, (g) MLINE.
- Ghi vào output: `source_layer`, `source_handle` (`e.dxf.handle`) để truy vết về CAD gốc. Lưu ý: entity ảo từ `virtual_entities()` không có handle và không thuộc layout nào (docstring MLINE; tương tự với INSERT chưa xác minh trực tiếp) → với entity ảo, lưu handle của INSERT cha. Handle không phải ID ổn định giữa các phiên bản bản vẽ (chưa xác minh).

## Kết quả chạy thử trên `samples/sample-floor-1.dxf` (TASK-012 phần C, claude-laptop, 2026-11-06)
`ezdxf 1.4.5` trong `.venv`; file mẫu: 13 LWPOLYLINE `A-AREA`, 13 TEXT, 12 INSERT `A-DOOR`, 12 LINE + 1 LWPOLYLINE `A-WALL`.
| Hàm / khẳng định | Kết quả |
|---|---|
| `recover.readfile(path)` → `(doc, auditor)` | ĐÚNG; `auditor.has_errors == False`; `doc.units == 6` (mét). `recover.read`, `recover.explore` cũng tồn tại |
| Query `msp.query('LWPOLYLINE[layer=="A-AREA"]')` | ĐÚNG: 13 kết quả |
| Query `msp.query('* !LINE')` (loại LINE), `msp.query('INSERT TEXT')` | ĐÚNG: 39 và 25 entity |
| `layer.is_off()`, `is_frozen()`, `is_locked()` | TỒN TẠI, chạy được (tất cả `False` trong mẫu) |
| `insert.virtual_entities()` | ĐÚNG: trả `['LINE','ARC']` (nội dung block `DOOR`). Entity ảo **không có handle**: `[None, None]` — xác nhận ghi chú "entity ảo không có handle" |
| `ezdxf.disassemble.recursive_decompose(entities)` | ĐÚNG: luồng phẳng 24 entity cho 12 INSERT (2 entity mỗi cửa) |
| `ezdxf.disassemble`: `make_primitive`, `to_primitives`, `to_meshes`, `to_paths`, `to_vertices`, `to_control_vertices`, `Primitive` | TỒN TẠI (đủ tên đã liệt kê); `to_primitives(msp)` ra 52 primitive |
| `ezdxf.path.make_path(entity).flattening(0.01)` | ĐÚNG: LWPOLYLINE đóng 4 đỉnh → 5 điểm; ARC → 9 điểm (distance 0.01) |
| `MText.plain_text()` | ĐÚNG: `{\fArial|b1;Phòng}\PA1` → `Phòng⏎A1` (xuống dòng) |
| `insert.mcount` | TỒN TẠI (`1` cho INSERT thường) |

CHƯA XÁC MINH (mẫu không có): MINSERT thật (`mcount > 1`), OCS extrusion −Z, MLINE, HATCH, SPLINE/ELLIPSE, block lồng nhiều cấp, xref; quy ước layer NCS/AIA, ISO 13567, BS 1192 (nguồn trả phí/chưa tìm nguồn công khai trong phiên này — vẫn giữ nhãn "chưa xác minh" trong `layer-naming-conventions.md`). Các bước làm sạch shapely mục 5 vẫn là đề xuất, chưa chạy trên dữ liệu thật.

## Nguồn
(Chi tiết URL và ngày truy cập: xem cả `research/01-cad/_sources.md`.)
- [ezdxf docs `drawing/recover.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/drawing/recover.rst) — truy cập 2026-11-06 (nguồn của trang https://ezdxf.readthedocs.io/en/stable/drawing/recover.html)
- [ezdxf docs `disassemble.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/disassemble.rst) và [`src/ezdxf/disassemble.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/disassemble.py) — truy cập 2026-11-06
- [ezdxf `src/ezdxf/entities/insert.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/insert.py) — truy cập 2026-11-06
- [ezdxf `src/ezdxf/entities/mline.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/mline.py) — truy cập 2026-11-06
- [ezdxf `src/ezdxf/entities/mtext.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/mtext.py) — truy cập 2026-11-06
- [ezdxf `src/ezdxf/entities/layer.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/layer.py) — truy cập 2026-11-06
- [ezdxf `src/ezdxf/path/path.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/path/path.py) — truy cập 2026-11-06
- [ezdxf tutorial `getting_data.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/tutorials/getting_data.rst) — truy cập 2026-11-06
- [ezdxf `tasks/flatten_entities.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/tasks/flatten_entities.rst) — truy cập 2026-11-06 (chỉ TODO)
- [ezdxf issue #836 (recover fail HATCH)](https://github.com/mozman/ezdxf/issues/836) — truy cập 2026-11-06 (qua kết quả tìm kiếm vòng 1, chưa mở lại)
- [ezdxf issue #663 (path.flattening crash)](https://github.com/mozman/ezdxf/issues/663) — truy cập 2026-11-06 (qua kết quả tìm kiếm vòng 1, chưa mở lại)

## Câu hỏi còn mở
- Chưa đọc trực tiếp host `ezdxf.readthedocs.io` (DNS vẫn bị chặn); đã thay bằng nguồn GitHub. Cần kiểm lại tên hàm trên bản ezdxf cài thực tế (nhánh `master` có thể mới hơn bản phát hành).
- `Path.flattening` "có từ 0.15.1" (khẳng định cũ) — chưa xác minh, đã bỏ khỏi bảng.
- Dung sai snap/flatten tối ưu; xử lý tường vẽ bằng 2 đường song song để ra footprint IfcWall.
- `virtual_entities()` có đệ quy block lồng không; INSERT gốc có bị huỷ khi `explode()` không (docstring bị cắt).
- Hiệu năng với file lớn (hàng trăm nghìn entity) — chưa xác minh.
