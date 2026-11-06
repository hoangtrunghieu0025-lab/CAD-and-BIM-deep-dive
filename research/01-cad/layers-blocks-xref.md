# Layer, block, attribute, xref, model/paper space

- **Câu hỏi nghiên cứu**: Các cấu trúc tổ chức dữ liệu trong DXF (layer, block/INSERT/ATTRIB, xref, layout) hoạt động ra sao và cần xử lý gì khi parse?
- **Kết luận ngắn** (2–4 dòng): Layer là nhãn nhóm duy nhất có sẵn để suy ngữ nghĩa; block (INSERT) mang vị trí + biến đổi, ATTRIB mang thuộc tính (số phòng, tên…) và phải đọc từ INSERT chứ không phải từ block definition. Xref là tham chiếu file ngoài, ezdxf không tự nạp nội dung xref. Đối tượng cần lấy ở model space; paper space chứa viewport/khung in.
- **Độ tin cậy**: trung bình — dựa trên tài liệu ezdxf (qua kết quả tìm kiếm); hành vi xref phụ thuộc phần mềm.

## Chi tiết

### Layer
- Mỗi entity có thuộc tính `layer` (chuỗi). Layer table có trạng thái (on/off, frozen, locked) và màu/linetype. Layer tắt/frozen thường là "rác" hoặc bản vẽ nền cần loại (chưa xác minh quy ước cụ thể — nên là tuỳ chọn cấu hình).
- Ngữ nghĩa nằm ở tên layer (xem `layer-naming-conventions.md`), không ở hình học.

### Block, INSERT, ATTDEF/ATTRIB
- Block definition chứa entity cục bộ; `INSERT` là tham chiếu khối với điểm chèn, scale, rotation (và có thể mảng row/column).
- `ATTDEF` nằm trong block definition và là mẫu; `ATTRIB` gắn vào từng `INSERT` (`insert.attribs`). Đọc giá trị: `insert.get_attrib_text("TAG")` / `get_attrib(tag)`; `search_const=True` để tìm cả ATTDEF hằng số mà một số ứng dụng không gắn thành ATTRIB.
- `insert.explode()` tách entity vào layout đích và huỷ INSERT gốc; `insert.virtual_entities()` trả về entity đã biến đổi mà không sửa bản vẽ — phù hợp cho pipeline chỉ đọc.
- Module `ezdxf.disassemble` phân rã đệ quy INSERT và entity có `virtual_entities()` thành luồng phẳng; không hỗ trợ ACIS, XREF, UNDERLAY, ACAD_TABLE, RAY, XLINE, và không áp XCLIP.
- Block lồng nhau: biến đổi phải tích luỹ (matrix) — dùng virtual_entities/disassemble thay vì tự nhân ma trận.
- Dynamic block (AutoCAD): chưa xác minh cách ezdxf xử lý biến thể hiển thị; thường xuất hiện dưới dạng block ẩn tên `*U<n>`.

### Xref
- Block có cờ xref và đường dẫn file (thuộc tính block `xref_path`); nội dung nằm ở file ngoài.
- Layer phụ thuộc xref có dạng `TENXREF|TENLAYER` trong AutoCAD (quy ước ứng dụng, được ARCHICAD và CADTutor xác nhận); ezdxf không dùng định dạng này khi tự import (dùng `$0$` prefix). Việc ezdxf đọc/giải xref tự động: chưa xác minh — nên giả định không.
- Hệ quả: nếu bản vẽ kiến trúc tham chiếu nền (xref) cho tường/lưới trục, DXF đơn lẻ sẽ thiếu dữ liệu; cần bind xref (trong CAD) hoặc nạp từng file và gộp.
- ezdxf có `ezdxf.xref` (Loader, ConflictPolicy) để nạp tài nguyên từ file khác.

### Model space vs paper space
- Model space (`doc.modelspace()`) chứa hình học thật theo đơn vị thiết kế; paper space layouts chứa khung in, viewport, chú thích tỉ lệ. Pipeline chỉ lấy model space (mặc định), tránh trùng lặp do viewport/khung.
- Viewport có thể có scale và crop khác nhau; không dùng cho toạ độ thực.

### Entity thường gặp cần xử lý
LINE, LWPOLYLINE, POLYLINE (2D/3D), ARC, CIRCLE, ELLIPSE, SPLINE, HATCH (đường biên rất hữu ích để lấy polygon phòng), TEXT/MTEXT, INSERT, DIMENSION, SOLID/3DFACE, MLINE (chưa xác minh hỗ trợ). Các entity dạng ACIS (3DSOLID) không phân rã được.

## Liên quan đến pipeline CAD → BIM → GPKG
- Đọc `msp = doc.modelspace()`; lọc theo layer đã ánh xạ; với INSERT dùng `virtual_entities()` để lấy hình học thật đã biến đổi, và `attribs` để lấy ref/name phòng → thuộc tính `ref`, `name` (OSM) hoặc `name`/`alt_name` của unit (IMDF).
- Tên block cũng là tín hiệu phân loại (cửa, thiết bị, ký hiệu phòng) — thêm bảng ánh xạ `block name → loại` trong `layer_mapping.yaml`.
- Xref: phát hiện (`doc.blocks` có xref) và cảnh báo trong báo cáo ingest; không im lặng bỏ qua.
- HATCH boundary có thể dùng như nguồn polygon phòng (cách khác với `polygonize` từ đường tường).

## Nguồn
- [ezdxf — Insert](https://ezdxf.readthedocs.io/en/stable/blocks/insert.html) — truy cập 2026-11-06 (qua kết quả tìm kiếm)
- [ezdxf — Attdef/Attrib](https://ezdxf.readthedocs.io/en/stable/blocks/attrib.html) — truy cập 2026-11-06 (qua kết quả tìm kiếm)
- [ezdxf — Block](https://ezdxf.readthedocs.io/en/stable/blocks/block.html) — truy cập 2026-11-06 (qua kết quả tìm kiếm)
- [ezdxf — Tutorial for Blocks](https://ezdxf.readthedocs.io/en/stable/tutorials/blocks.html) — truy cập 2026-11-06
- [ezdxf — Disassemble](https://ezdxf.readthedocs.io/en/stable/disassemble.html) — truy cập 2026-11-06
- [ezdxf xref.py (GitHub)](https://github.com/mozman/ezdxf/blob/master/src/ezdxf/xref.py) — truy cập 2026-11-06
- [Graphisoft — Interoperability (xref layer "XREF | LAYER")](https://help.graphisoft.com/AC/23/JPN/_AC23_Help/110_Interoperability/110_Interoperability-27.htm) — truy cập 2026-11-06
- [CADTutor — vplayer scope (layer xref chứa "|")](https://www.cadtutor.net/forum/topic/60698-vplayer-scope) — truy cập 2026-11-06

## Câu hỏi còn mở
- ezdxf xử lý dependent layer `xref|layer` khi đọc thế nào (chưa xác minh).
- Dynamic block, MLINE, proxy entity: cách trích hình học (chưa xác minh).
- Quy ước xử lý layer off/frozen: bỏ hay giữ (nên thử trên dữ liệu thật).
