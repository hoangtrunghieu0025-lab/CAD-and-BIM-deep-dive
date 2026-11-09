# Đọc mã nhóm 3: Cloud2BIM, ifc-floorplan, FloorplanTransformation, VecFloorSeg, ifc-bonsai-mcp, A-Scan2BIM

- **Câu hỏi nghiên cứu**: Sáu repo "chưa đọc mã" ở [github-survey-cad-to-ifc](github-survey-cad-to-ifc.md) có phần nào áp dụng được cho converter DXF → IFC?
- **Kết luận ngắn**: Chỉ **Cloud2BIM** (MIT) có giá trị thực dụng cao: mã ghi IFC cho tường/lỗ mở/cửa/phòng ở mức thấp, cùng thuật toán xử lý đường tim tường (nối đầu rời, tách tại giao điểm). **ifc-floorplan** (không giấy phép) hữu ích làm **bộ kiểm tra ngược** IFC → phòng. Bốn repo còn lại chủ yếu học ý tưởng hoặc không liên quan trực tiếp (học sâu trên ảnh/đồ thị, scan, MCP).
- **Độ tin cậy**: trung bình đến cao cho phần mô tả mã đã đọc (clone nông, đọc README, danh sách hàm và các đoạn chính, 2026-11-08). **Chưa chạy mã nào.** Chưa đọc hết từng file lớn (ví dụ `generate_ifc.py` 1526 dòng chỉ đọc phần tường, lỗ mở, vật liệu).

## Tóm tắt từng repo

| Repo | Giấy phép · quy mô · cập nhật | Là gì | Giá trị cho ta |
|---|---|---|---|
| [**VaclavNezerka/Cloud2BIM**](https://github.com/VaclavNezerka/Cloud2BIM) | MIT · ~4,7k dòng Python, 20 commit · 2026-08-10 | Point cloud (E57/XYZ) → IFC bằng thuật toán phân đoạn theo mật độ điểm; bài báo Automation in Construction 177 (2025). README nói bản mở là phiên bản nghiên cứu, bản "AI" sản xuất là thương mại riêng | **Cao.** Xem chi tiết bên dưới |
| [**Show2Instruct/ifc-floorplan**](https://github.com/Show2Instruct/ifc-floorplan) | **Không có file LICENSE** · ~8,9k dòng gồm test, 2 commit · 2026-10-11 | Chiều ngược: IFC → mặt bằng từng tầng (phòng, tường, cửa, đường nối giữa các phòng) ra JSON và SVG; thử trên 208 + 1029 mô hình theo README | **Trung bình, để kiểm tra.** Chỉ học ý tưởng vì không giấy phép |
| [**art-programmer/FloorplanTransformation**](https://github.com/art-programmer/FloorplanTransformation) (Raster-to-Vector, ICCV 2017) | MIT · Lua/Torch7 + Python 2.7, bản PyTorch trong `pytorch/` · commit cuối 2019 | Ảnh mặt bằng raster → vector (tường, cửa, ký hiệu, loại phòng) bằng CNN + quy hoạch số nguyên | **Thấp cho DXF.** Hậu xử lý có ý tưởng nhưng ngăn xếp cũ, cần Gurobi (bộ giải thương mại) |
| [**DrZiji/VecFloorSeg**](https://github.com/DrZiji/VecFloorSeg) | **Không giấy phép** · 5 commit, kèm bản chép `torch_geometric` · 2025-10-06 | Phân đoạn mặt bằng **vector** bằng mạng đồ thị chú ý hai luồng, huấn luyện trên dữ liệu CubiCasa5k đã chuyển thành SVG thô | **Thấp, ý tưởng.** Nặng học sâu (GPU, PyG 2.0.4), dữ liệu phải tải ngoài |
| [**Show2Instruct/ifc-bonsai-mcp**](https://github.com/Show2Instruct/ifc-bonsai-mcp) | MIT · ~17k dòng, 7 commit · 2026-07-10 | Máy chủ MCP cho LLM đọc/tạo/sửa IFC qua Bonsai trong Blender (hơn 50 công cụ, có RAG trên tài liệu IfcOpenShell) | **Thấp cho converter.** Cần Blender + Bonsai; hữu ích cho thao tác tay/kiểm tra bằng LLM |
| [**weiliansong/A-Scan2BIM**](https://github.com/weiliansong/A-Scan2BIM) | **Không giấy phép** · ~21k dòng, 10 commit · 2024-06-14 | Scan-to-BIM "có hỗ trợ": plugin Revit (C#) làm giao diện, máy chủ Python chạy mạng nơ-ron gợi ý tường tiếp theo (BMVC 2023) | **Rất thấp.** Phụ thuộc Revit/Windows; chỉ lấy ý tưởng người-trong-vòng-lặp |

## 1. Cloud2BIM: những phần áp dụng được
**a) Ghi IFC mức thấp (`generate_ifc.py`, lớp `IFCmodel`).** Cùng cách mà một bộ dựng IFC chuẩn nên làm; đối chiếu với POC của ta (chỉ `create_2pt_wall`):
- **Tường có hai biểu diễn**: `Axis` (`IfcPolyline`, `Curve2D`) cho đường tim và `Body` (`SweptSolid`, `IfcRectangleProfileDef` đùn theo Z) cho khối. POC chỉ có khối.
- **Kiểu và vật liệu theo lớp**: `IfcWallType` + `IfcMaterialLayerSet` + `IfcMaterialLayerSetUsage` (`LayerSetDirection=AXIS2`, `OffsetFromReferenceLine = -độ dày/2`), mỗi lớp có `LayerThickness`, `Category`. Đây là chỗ tự nhiên gắn độ dày và vật liệu vào tường thay vì chỉ hình học.
- **Lỗ mở cửa**: `IfcOpeningElement` có profile `IfcArbitraryClosedProfileDef` đùn dọc tường, vị trí tính từ `offset_from_start` và `opening_sill_height`; nối bằng `IfcRelVoidsElement` (tường ↔ lỗ) và `IfcRelFillsElement` (lỗ ↔ cửa/cửa sổ). Cùng ý với `feature.add_feature` + `add_filling` đã thấy ở alvin528/CAD2BIM, nhưng đây là bản tự dựng bằng `create_entity`.
- Ngoài ra: `create_slab`, `create_space` (`IfcSpace`), cột, dầm, cầu thang (mesh), Pset boolean (`create_property_single_value`), gán vật liệu có màu.

**b) Xử lý đường tim tường (`space_generator.py`)**: `process_centerlines` làm lần lượt
1. `find_disconnected_walls`: đếm số lần mỗi đầu mút xuất hiện; tường có đầu mút chỉ xuất hiện 1 lần là chưa nối.
2. `extend_to_centerline`: kéo dài đầu rời tới đường tim tường khác nếu trong ngưỡng `distance_threshold_extension` (`is_point_on_centerline`, `find_intersection`).
3. `process_disconnected_walls` + `divide_wall`: tách tường tại giao điểm (chữ T), bỏ đoạn ngắn hơn `min_wall_length`.
4. `generate_space_boundaries`, `extract_space_dimensions`, `identify_zones`: dựng ranh giới phòng từ các đoạn song song hai mặt tường (`calculate_parallel_segments`).

Đây chính là phần "nối góc / tách tại giao điểm" mà POC của ta chưa có, và bổ sung cho thuật toán ghép hai nét song song của roomgraph.

**Lưu ý**: mã dùng `OwnerHistory` và `create_entity` thủ công (đúng nhưng dài); ta nên dùng `ifcopenshell.api` cho gọn. Mã nhận tường dạng từ điển `{'start_point', 'end_point', 'thickness'...}`, nên tách được thành hàm thuần tuý để dùng trên đoạn tim lấy từ DXF.

## 2. ifc-floorplan: làm bộ kiểm tra ngược
- `fp/extract.py` đọc IFC thành dữ liệu từng tầng, tự quy về mét theo đơn vị của tệp (nên mô hình vẽ bằng mm và m cho kết quả giống nhau); lấy phòng từ `IfcSpace`, **suy ra phòng từ tường** khi thiếu (`infer_rooms`: raster hoá vật cản thành lưới rồi tìm vùng kín, `cell=0.12 m`, `min_area=1.5 m²`).
- `fp/validate.py` có các phép đo tự nhất quán: diện tích dấu chân so với diện tích khai báo, thể tích, và **IoU giữa phòng suy ra và `IfcSpace`** (ngưỡng 0,1 và 0,5). Tác giả nói rõ đây là kiểm tra nhất quán nội bộ, không phải độ chính xác so với công trình thật.
- `fp/connectivity.py`: suy ra phòng nào nối với phòng nào qua cửa (`connected_by_door`, `exterior_door`, `open_passage`).
- Mỗi lần chạy ghi `run.json` (lệnh, dấu vân tay đầu vào/ra, phiên bản gói) và bản sao mã; đáng học cho tính tái lặp.
- **Áp dụng**: kiểm IFC do converter sinh ra bằng cách so phòng suy ra từ tường với `IfcSpace`, và so `IfcSpace` với polyline `A-AREA` trong DXF bằng IoU. Ta đã có `shapely`, tự viết được phần IoU; không cần chép mã (không giấy phép).

## 3. Các repo còn lại
- **FloorplanTransformation**: hậu xử lý (`pytorch/IP.py`, `code/PostProcessing/QP.py`) chọn một tập tường/cửa/ký hiệu nhất quán bằng quy hoạch số nguyên có trọng số (`pointWeight`, `junctionWeight`, `gap`…), có `adjustPoints`/`mergePoints` để căn và gộp điểm gần nhau. Ý tưởng cho dung sai căn/gộp điểm, nhưng ta có đường vector sẵn từ DXF nên không cần phần mạng; cần Gurobi, ngăn xếp Python 2.7/Torch7 đã cũ (bản PyTorch trong `pytorch/` mới hơn).
- **VecFloorSeg**: `Utils/svgUtils.py` đọc SVG mặt bằng (lớp "Wall", "Window", "Door") thành nhãn và đồ thị gồm các đoạn thẳng/điểm giao; mô hình phân loại từng nguyên thủy hình học bằng GNN. Có ích **nếu sau này layer vô nghĩa** và cần phân loại bằng học máy; ngoài ra chưa cần.
- **ifc-bonsai-mcp**: danh mục công cụ (`create_two_point_wall`, `create_polyline_walls(thickness, height, closed)`, cửa với các `operation_type` như `SINGLE_SWING_LEFT`, `DOUBLE_DOOR_SINGLE_SWING`, `SLIDING_TO_LEFT`, và thuộc tính khung `LiningDepth/LiningThickness`) cho thấy tập kiểu cửa và tham số mà Bonsai hỗ trợ; có thể dùng làm bảng giá trị `OperationType` cho `IfcDoor`. Mã phụ thuộc Blender.
- **A-Scan2BIM**: kiến trúc client-server (plugin Revit + máy chủ Python) với người dùng xác nhận từng bước; ý tưởng giao diện "gợi ý rồi xác nhận" nếu sau này làm công cụ bán tự động.

## Liên quan đến pipeline CAD → BIM → GPKG
Bổ sung vào kế hoạch ở [github-survey-cad-to-ifc](github-survey-cad-to-ifc.md):
1. **Nối góc và tách giao điểm** theo trình tự của Cloud2BIM (`find_disconnected_walls` → `extend_to_centerline` → `divide_wall`), áp lên đoạn tim sau khi ghép hai nét song song (roomgraph).
2. **Tường có `Axis` + `Body`, `IfcWallType` + `IfcMaterialLayerSetUsage`** để độ dày và vật liệu đi theo kiểu tường (cũng là chỗ gắn Pset ở bước enrich). Có thể thực hiện bằng `ifcopenshell.api` (`type.assign_type`, `material.add_layer`…, chưa kiểm tên hàm).
3. **Lỗ mở**: `IfcOpeningElement` + `IfcRelVoidsElement` + `IfcRelFillsElement` (hoặc `feature.add_feature/add_filling`).
4. **Kiểm tra ngược** bằng IoU phòng (ý tưởng ifc-floorplan) trong `src/export/validate.py` hoặc mô-đun mới.
5. Bảng `OperationType` cửa lấy từ danh sách đã thấy ở ifc-bonsai-mcp; **đối chiếu với schema IFC4 trước khi dùng** (chưa xác minh với tài liệu IFC chính thức).

## Nguồn
Tất cả truy cập 2026-11-08, clone nông và đọc mã tại máy (không chạy):
- [Cloud2BIM](https://github.com/VaclavNezerka/Cloud2BIM) · [ifc-floorplan](https://github.com/Show2Instruct/ifc-floorplan) · [FloorplanTransformation](https://github.com/art-programmer/FloorplanTransformation) · [VecFloorSeg](https://github.com/DrZiji/VecFloorSeg) · [ifc-bonsai-mcp](https://github.com/Show2Instruct/ifc-bonsai-mcp) · [A-Scan2BIM](https://github.com/weiliansong/A-Scan2BIM)
- Bài báo Cloud2BIM: Zbirovský & Nežerka, Automation in Construction 177 (2025) 106303, doi 10.1016/j.autcon.2025.106303 (theo README, **chưa đọc bài**).

## Câu hỏi còn mở
- Chạy `process_centerlines` của Cloud2BIM trên đoạn tim lấy từ `samples/sample-floor-1.dxf`: chưa làm.
- Bản dựng IFC của Cloud2BIM có mở được và đúng trong Bonsai/FreeCAD: chưa kiểm.
- Giấy phép nội dung từng file (ngoài tệp LICENSE ở gốc) và các dữ liệu kèm theo (`input_e57`, ảnh): chưa kiểm.
- ifc-floorplan và VecFloorSeg không có giấy phép: không được chép mã.
