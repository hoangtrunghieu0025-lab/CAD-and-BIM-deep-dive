# Nối góc tường (FreeCAD `offsetWire`) và các chi tiết ezdxf cần chú ý

- **Câu hỏi nghiên cứu**: FreeCAD tạo biên dạng tường có góc từ đường tim như thế nào, ta tái hiện bằng thư viện nào, và `ezdxf` có những chi tiết nào dễ sai khi đọc DXF mặt bằng?
- **Kết luận ngắn**: FreeCAD dịch từng đoạn tim sang hai phía theo độ rộng và căn lề, rồi **nối các đoạn đã dịch bằng giao điểm của hai đường kéo dài** (mitre). Đúng phép này có sẵn trong `shapely` (`buffer`/`offset_curve` với `join_style='mitre'`), nên không cần tự viết. Với `ezdxf`: `make_path` xử lý bulge đúng; cung/đường tròn nằm trong INSERT bị **lật gương** lưu theo OCS nên phải đổi sang WCS; mã hiện tại của ta xử lý OCS cho LWPOLYLINE nhưng **bỏ bulge** và chưa mở khối INSERT.
- **Độ tin cậy**: cao cho các phép đo đã chạy trong `.venv` (shapely 2.2.0, ezdxf 1.4.5); trung bình cho phần mô tả mã FreeCAD (đã đọc `offsets.py` và `connect`, chưa đọc hết mọi nhánh). Phần "mã hiện tại của ta" chỉ đọc các dòng 40–60 và 100–131 của `src/cad2bim/__init__.py`, chưa rà toàn bộ.

## Chi tiết

### 1. FreeCAD: `DraftGeomUtils.offsetWire` + `connect` (bản 1.1.4)
- Đầu vào: wire (danh sách cạnh đã sắp), `widthList` (độ rộng từng đoạn), `alignList` (Left/Right/Center từng đoạn). Có hai chế độ:
  - `occ=True`: gọi `wire.makeOffset` của OpenCascade (offset cả wire, bộ nén sẵn của OCC).
  - Mặc định: tự **dịch từng cạnh** theo vector pháp tuyến nhân độ rộng (Center dùng nửa độ rộng), rồi gọi `connect(edges, closed)`.
- `connect` (`draftgeoutils/intersections.py`): với mỗi cặp cạnh liên tiếp tính giao điểm của hai đường **kéo dài** (`findIntersection(prev, curr, True, True)`); nếu có nhiều giao điểm lấy điểm gần đầu cạnh hiện tại nhất; điểm đó thành đầu/cuối mới của hai cạnh. **Nếu hai cạnh song song (không có giao điểm)** thì chèn thêm một đoạn nối giữa đầu cuối cũ. Hỗ trợ cả đoạn thẳng lẫn cung tròn.
- Giới hạn: yêu cầu wire đã nối liền và đã sắp thứ tự. `ArchWall.mergeShapes` (gộp hai tường chung đầu mút) ghi "Not currently implemented". FreeCAD không tự nối các tường rời hay xử lý giao chữ T.

### 2. Tái hiện bằng `shapely` (đã chạy, shapely 2.2.0)
| Phép thử | Kết quả | Ý nghĩa |
|---|---|---|
| Tim chữ L (5 m + 3 m), dày 0,2: `buffer(0.1, cap_style='flat', join_style='mitre')` | diện tích **1,6** = 0,2 × 8, hợp lệ, 6 đỉnh | Góc mitre đầy đủ, giống kết quả của `connect` |
| `offset_curve(±0.1, join_style='mitre')` hai phía | độ dài 7,8 và 8,2 | Hai biên trái/phải (cho kiểm tra hoặc dựng profile) |
| Hai tường chữ T (6 m ngang, 4 m dọc) rồi `unary_union` | diện tích **1,98** (tổng 2,0 trừ phần chồng 0,02), 1 `Polygon` | Gộp tường giao chữ T được bằng `unary_union` |
| Nhánh T dừng sát mặt tường (hụt 0,1) | vẫn ra 1 `Polygon` | Hai tường chạm mặt thì vẫn hợp nhất; **kẽ hở thật sự lớn hơn dung sai** thì phải kéo dài đầu rời trước (ý tưởng `extend_to_centerline` của Cloud2BIM) |

Hệ quả cho thiết kế: bước nối góc có thể là `LineString` tim (đã nối) → `buffer` mitre theo độ dày; các tường chữ T → `unary_union`; chỉ phần **đóng kẽ hở** (kéo dài đầu rời) là phải tự viết. Chưa kiểm với góc rất nhọn (mitre quá dài, cần `mitre_limit`) hay tường cong.

### 3. ezdxf 1.4.5: các chi tiết dễ sai (đã chạy thử)
- **Bulge**: `LWPOLYLINE.get_points("xy")` **bỏ bulge**. `ezdxf.path.make_path(pl)` dựng đường có cung; thử polyline 3 điểm có bulge = 1 ở đoạn đầu cho độ dài **9,283** ≈ 2π + 3 (đúng nửa đường tròn R = 2 cộng đoạn 3), `has_arc = True`. (Lưu ý định dạng điểm: `format="xyb"` mới nhận bulge; `"xyse"` là độ rộng đầu/cuối, không phải bulge.)
- **INSERT**: `Insert.virtual_entities()` trả về thực thể đã áp phép biến đổi khối. Với `xscale = -1` và xoay 90°, cung trong khối có `extrusion = (0, 0, -1)` và tâm thô `(-2, 1)` (OCS); đổi sang **WCS** bằng `e.ocs().to_wcs(e.dxf.center)` ra `(2, 1)` đúng. **Dùng `e.dxf.center` trực tiếp sẽ sai vị trí.** (`ocs` là phương thức, không phải thuộc tính.)
- **Đơn vị**: `ezdxf.units.conversion_factor(MM, M) = 0.001`; `$INSUNITS = 0` là không đơn vị, nên giữ `fallback_unit` (ta đã có).
- **Truy vấn nhanh**: `msp.query('LINE[layer=="A-WALL"]')` lọc thực thể theo loại và layer.
- `recover.readfile`/`explore` có sẵn để đọc file DXF hỏng (chưa thử).

### 4. Mã hiện tại của ta so với các điểm trên (`src/cad2bim/__init__.py`, đọc một phần)
- `_wcs_xy` đã xử lý OCS cho LWPOLYLINE (tốt) nhưng dùng `get_points("xy")` nên **bulge bị bỏ**: tường là polyline cong sẽ thành dây cung. Nên thay bằng `make_path(...).flattening(...)` (ta đã dùng `flattening` ở nhánh HATCH).
- INSERT: mã dùng điểm chèn `e.dxf.insert` và suy bề rộng cửa từ LINE đầu tiên trong khối; chưa mở khối bằng `virtual_entities()`, nên chưa lấy hướng mở cửa, cung quét hay hình dạng khối thật. Cung/đường tròn trong khối sẽ gặp vấn đề OCS ở mục 3 nếu sau này dùng.

## Kết quả thử bước nối góc (2026-11-08)
Script: [`poc/wall_corner_join_trial.py`](poc/wall_corner_join_trial.py) (chỉ in số liệu, không ghi file, không sửa `src/`). Chạy: `python -I wall_corner_join_trial.py samples/sample-floor-1.dxf 0.2 A-WALL <gap> <tol>`. Đường tim: 16 đoạn của `A-WALL` (khung ngoài 24 × 12 m là một polyline kín, hai tường hành lang y = 5 và y = 7 chạy suốt, 10 vách ngăn dọc), độ dày giả định 0,2 m.

**Cách làm**: (1) *noding*: `unary_union` các đoạn để tách tại mọi giao điểm; (2) `linemerge` ghép thành chuỗi qua nút bậc 2; (3) `buffer(cap phẳng, mitre, mitre_limit = 5)` từng chuỗi rồi `unary_union`; (4) tuỳ chọn `extend_free_ends`: đầu mút không chạm đoạn nào thì bắn tia theo hướng đoạn, kéo dài tới giao điểm gần nhất trong dung sai.

**[A] Mẫu gốc (sạch)**
| | Số phần tử | Diện tích tường | Phòng (lỗ) |
|---|---|---|---|
| POC cũ: mỗi đoạn một hộp riêng | 16 | cộng riêng 34,00; hợp nhất 33,48 (trùng nhau 0,52) | 13 |
| Nối góc | 36 chuỗi tim sau khi tách chữ T | **33,52** | 13 |

Chênh lệch +0,04 m² đúng bằng 4 góc ngoài × (0,1 × 0,1): POC cũ để thiếu một ô vuông 0,1 × 0,1 m ở mỗi góc khung ngoài. Tổng chiều dài tim sau tách = 170 m, khớp tổng ban đầu (72 + 48 + 50).

**[B] Ca lỗi cố ý**: rút ngắn đầu 10 vách ngăn (đầu chạm tường hành lang) một khoảng *gap*; dung sai kéo dài *tol* = 0,3 m.
| gap (m) | Không kéo dài | Có kéo dài |
|---|---|---|
| 0,08 (< nửa độ dày 0,1) | hình hợp nhất **giống hệt** mẫu gốc (13 phòng), nhưng chỉ có 26 chuỗi tim thay vì 36 | 10 đầu được kéo dài, 36 chuỗi, giống mẫu gốc |
| 0,15 | **3 phòng** (mất 10 phòng vì vách không còn khép kín), sai khác 0,10 m² | 13 phòng, sai khác 0 |
| 0,30 (= tol) | 3 phòng, sai khác 0,40 m² | 13 phòng, sai khác 0 (kéo dài chạm đúng biên dung sai) |

**Nhận xét**
- Khe hở nhỏ hơn nửa độ dày không thấy được ở hình khối nhưng **vẫn làm đứt kết nối đường tim** (26 so với 36 chuỗi); điều này ảnh hưởng quan hệ nối tường trong IFC và bước dò phòng. Nên kéo dài đầu rời **trước** khi dựng đối tượng, không chỉ dựa vào hình hợp nhất.
- Khe hở từ 0,15 m trở lên làm mất phòng nếu dựng phòng bằng polygonize từ tường (ở đây: 13 → 3). Bước đóng kẽ hở là bắt buộc nếu ta suy phòng từ tường thay vì dùng `A-AREA`.
- Trường hợp gap = tol vẫn pass là do kéo dài kiểm tra bao gồm biên; không nên dựa vào giá trị biên, chọn `tol` lớn hơn khe hở dự kiến rõ rệt.

**Giới hạn của phép thử (cần ghi rõ)**
- Mẫu quá sạch: các đầu mút trùng chính xác, mọi góc vuông, mọi tường cùng độ dày. Đây là phép thử *chức năng*, **không** chứng minh độ bền trên bản vẽ thật.
- Chưa thử *kéo dài nhầm* (đầu tường cố ý để hở, ví dụ lối đi) khi `tol` quá lớn, góc nhọn, tường cong, đường tim chồng lên nhau (hai nét song song của cùng một tường: bước ghép nét theo roomgraph chưa làm).
- Chưa dựng IFC từ kết quả này; chưa so với `src/cad2bim` hiện tại.

## Liên quan đến pipeline CAD → BIM → GPKG
1. Bước "nối góc": tim đã nối → `buffer(mitre)` → `unary_union` cho giao chữ T; tự viết phần **kéo dài đầu rời** (theo Cloud2BIM). Đặt `mitre_limit` hợp lý và kiểm góc nhọn.
2. Đọc hình học bằng `make_path` để giữ cung; đổi mọi toạ độ cung/tròn sang WCS.
3. Nếu cần dùng hình dạng khối cửa, mở bằng `virtual_entities()` và lấy toạ độ qua WCS.
4. Việc POC kế tiếp: thử bước 1 trên `samples/sample-floor-1.dxf` (16 đoạn A-WALL) và so diện tích/số tường với POC hiện tại.

## Nguồn
- Mã FreeCAD 1.1.4 tại máy: `Mod/Draft/draftgeoutils/offsets.py` (`offsetWire`), `Mod/Draft/draftgeoutils/intersections.py` (`connect`), `Mod/BIM/ArchWall.py` — đọc 2026-11-08
- shapely 2.2.0, ezdxf 1.4.5 trong `.venv` (chạy thật, 2026-11-08)
- Mã nội bộ `src/cad2bim/__init__.py` (đọc một phần)

## Câu hỏi còn mở
- `buffer(mitre)` với góc nhọn dưới 30°, tường cong, tường dày khác nhau tại một nút: chưa thử.
- `connect` của FreeCAD với cung tròn kề đoạn thẳng: đã thấy trong mã, chưa chạy.
- Hành vi `make_path` với polyline có độ rộng thay đổi (`has_width`): chưa thử.
