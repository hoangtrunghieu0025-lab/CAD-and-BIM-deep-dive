# FreeCAD và IfcOpenShell: phần nào đã chuyển DXF → IFC, phần nào làm giàu thông tin IFC

- **Câu hỏi nghiên cứu**: Hai dự án mã nguồn mở FreeCAD và IfcOpenShell đã làm được gì cho chuyển DXF → IFC, và có sẵn cơ chế nào để tự động làm giàu thông tin (Pset, phân loại, vật liệu) cho IFC không?
- **Kết luận ngắn**: Cả hai chỉ làm được **từng đoạn**, không có đường tự động trọn vẹn DXF → IFC giàu thông tin. FreeCAD nhập DXF thành đối tượng Draft (hình học + layer), người dùng phải tự "Convert to BIM" từng đối tượng; mã nhập DXF **không có dòng nào nhắc IFC**. IfcOpenShell cho thư viện để **ghi** IFC và để **làm giàu** (Pset, phân loại, vật liệu) rất đủ, nhưng script `dxf2ifc.py` chỉ cho polyface mesh. Vì vậy phần "layer → class IFC → Pset" vẫn phải tự viết, và IfcOpenShell là nền tảng phù hợp để làm.
- **Độ tin cậy**: cao cho phần **đọc mã và chạy thật tại máy** (FreeCAD 1.1.4 AppImage đang chạy, IfcOpenShell 0.9.0.post1 trong `.venv`); trung bình cho phần tài liệu (lấy từ kết quả tìm kiếm). Chưa chạy Bonsai.

## Chi tiết

### 1. FreeCAD (đọc mã trong `Mod/Draft` và `Mod/BIM` của bản 1.1.4)

| Khâu | Có sẵn gì | Mức tự động |
|---|---|---|
| Nhập DXF | `Draft/importDXF.py` đọc DXF bằng thư viện riêng; **layer thành Draft layer** (`locateLayer` → `Draft.make_layer`), giữ màu. Kết quả là đối tượng Draft (đường, wire, text…). `grep Ifc importDXF.py` = **0 kết quả**, tức nhập DXF không gán class IFC nào | Hoàn toàn tự động cho hình học, **không** cho ngữ nghĩa BIM |
| Đường → tường | `Arch.makeWall(baseobj, height, length, width, align, offset, …)`; lệnh `BIM_Wall` dựng tường từ đường/wire/sketch đã chọn. Tài liệu: có thể chọn nhiều đường một lúc rồi bấm Wall; hướng trái/phải có thể bị lật và phải chỉnh `Align` | Bán tự động: người chọn đối tượng, chiều cao/độ dày là tham số |
| Đổi hàng loạt | `bimcommands/BimConvert.py` (`BIM_Convert`): chọn đối tượng, chọn loại trong danh sách cố định (Wall, Structure, Rebar, Window, Stairs, Roof, Panel, Frame, Space, Equipment, Component) và gọi `Arch.make<Loại>(obj)` cho **mọi đối tượng đã chọn** | Bán tự động: một loại cho mỗi lần chọn, **không** suy ra loại từ tên layer. Có thể viết script lọc theo layer rồi gọi `Arch.makeWall` (**ý tưởng, chưa thử**) |
| Gán IFC | `BimIfcElements` (Manage IFC Elements): quản lý loại IFC và vật liệu của từng phần tử khi xuất | Thủ công qua giao diện, nhóm theo loại/vật liệu/cây |
| Thuộc tính | `BimIfcProperties`: thêm Pset/thuộc tính từ danh sách định nghĩa `Presets/pset_definitions.csv`, đọc CSV tuỳ biến `CustomPsets.csv` (dấu `;`); `BimIfcQuantities`: số lượng; `BimClassification`: phân loại | Thủ công; **CSV chỉ là bảng định nghĩa Pset**, không tự áp theo layer |
| Kiểm tra | `BimPreflight`: bộ kiểm tra trước khi xuất IFC | Tự động chạy, người đọc kết quả |
| Ghi IFC | `importers/exportIFC.py` (xuất từ đối tượng Arch); module `nativeifc/` (`ifc_tools.py`, `ifc_psets.py`, `ifc_classification.py`…) dùng `ifcopenshell` để làm việc trực tiếp trên IFC | Tự động |

Nhận xét: cái FreeCAD thiếu cho bài toán là đúng cái ta cần, **bảng layer → loại BIM**. Hạ tầng "đối tượng → IFC có Pset" đã có, nhưng bước ở giữa phải do người hoặc script.

### 2. IfcOpenShell (đã chạy thật trong `.venv`)

| Khâu | Có sẵn gì |
|---|---|
| DXF → IFC | `dxf2ifc.py` (Bonsai/BlenderBIM) chỉ xử lý polyface mesh, xem [open-source-dxf-to-ifc-projects](open-source-dxf-to-ifc-projects.md). Không có bộ nhập DXF mặt bằng nào được thấy trong tài liệu hay kết quả tìm kiếm |
| Dựng hình học | `api.geometry.create_2pt_wall` (đã xác minh ở [approaches](cad-to-bim-approaches.md)), `util.shape_builder` |
| Pset | `api.pset.add_pset`, `edit_pset`, `assign_pset`, `add_qto`/`edit_qto`, `remove_pset`; `api.pset_template.*` để tạo mẫu Pset tuỳ biến |
| Mẫu Pset chuẩn | `util.pset.get_template("IFC4")` trả danh sách Pset/thuộc tính chuẩn theo schema. **Đã chạy**: `Pset_WallCommon` có `Reference, Status, AcousticRating, FireRating, Combustible, SurfaceSpreadOfFlame, ThermalTransmittance, IsExternal, LoadBearing, ExtendToStructure, Compartmentation`. Có thể dùng để kiểm tên thuộc tính trước khi ghi, tránh bịa tên |
| Phân loại | `api.classification.add_classification`, `add_reference`, `edit_*`, `remove_*` |
| Vật liệu | `api.material.*` (đã dùng `add_material`, `assign_material`) |
| Truy vấn | `util.selector.filter_elements(file, "IfcWall")` và truy vấn kiểu bộ lọc; `util.element.get_psets`, `get_material` |
| Kiểm tra | IDS qua gói `ifctester` và vá hàng loạt qua `ifcpatch`: **không có trong `.venv` và chưa kiểm** trong phiên này |

**Thử làm giàu tự động** (`poc/enrich_ifc_demo.py`, chạy trên IFC 16 tường của POC): tự thêm `Pset_WallCommon` (`IsExternal`, `LoadBearing`, `Reference`), một Pset tự đặt `Pset_ProjectCustom` (`SourceLayer = A-WALL`, `AssumedHeight_m = 3.0`), vật liệu `Concrete` và một tham chiếu phân loại cho cả 16 tường. Đọc lại bằng `util.element.get_psets` ra đúng giá trị. Giá trị là **giả định/ví dụ**: `IsExternal = False` chỉ để minh hoạ, mã phân loại `XX.01` và tên hệ phân loại là giả, và chưa mở bằng Bonsai/FreeCAD.

### 3. "Làm giàu" nên lấy thông tin từ đâu
Nguồn tự động hoá khả thi (đều do ta quyết định, không phải công cụ tự suy ra):
1. **Layer CAD** → class IFC, `PredefinedType`, vật liệu mặc định (bảng trong `config/layer_mapping.yaml`).
2. **Thuộc tính của block** (`ATTRIB` của `INSERT`) và **chữ trong bản vẽ** (tên phòng, mã cửa) → `Name`, `Reference`, Pset.
3. **Hình học** → số lượng (chiều dài, diện tích phòng) cho `Qto_*`.
4. **Bảng tra theo dự án** (CSV): loại tường → độ dày, vật liệu, FireRating.
5. Thông tin không có trong CAD 2D (cao độ, `IsExternal`, `LoadBearing`) chỉ có thể là **mặc định có ghi chú giả định** hoặc để trống.

## Liên quan đến pipeline CAD → BIM → GPKG
- Đề xuất kiến trúc: giữ `ezdxf` đọc DXF và `ifcopenshell.api` ghi IFC; thêm bước "enrich" đọc một bảng CSV/YAML (layer hoặc loại đối tượng → Pset/vật liệu/phân loại), dùng `util.pset.get_template` để kiểm tên thuộc tính. Mô-đun gợi ý: `src/cad2bim/ifc_writer.py` và `ifc_enrich.py`.
- FreeCAD dùng làm **công cụ kiểm tra bằng mắt và Preflight**, không phải khâu chuyển đổi chính. Nếu muốn thử đường FreeCAD: nhập DXF → script lọc layer → `Arch.makeWall`/`makeSpace` → `BIM_IfcProperties` → xuất IFC; việc này nên giao claude-laptop (cần GUI).
- Việc POC kế tiếp (thêm vào danh sách trong [poc-result](poc-result.md)): tích hợp `enrich_ifc_demo.py` thành bước đọc bảng ánh xạ; thử `Arch.makeWall` hàng loạt theo layer trong `freecadcmd`.

## Kiểm lại lần 2 (2026-11-08, theo phản hồi của người dùng)
Người dùng gửi danh sách link FreeCAD/IfcOpenShell/Bonsai và nhận xét lần đọc đầu chưa kỹ. Đã kiểm lại link và đọc sâu hơn mã.

**Link người dùng gửi (kiểm bằng `curl`)**: mở được (200): `github.com/FreeCAD/FreeCAD`, `wiki.freecad.org/{BIM_Workbench, Arch_Workbench, Arch_IFC}`, trang `robertmassaioli.github.io/.../ifc-import-export/`, `Mod/BIM`, `Mod/Draft`, `Mod/Import`, `mozman/ezdxf`. **Hỏng (404)**: `src/Mod/Arch` (Arch đã gộp vào `Mod/BIM`: `Arch.py`, `ArchWall.py`… nằm trong `Mod/BIM` ở bản 1.1.4), `IfcOpenShell/.../v0.8.3/src/ifcopenshell-python`, `.../v0.8.3/src/bonsai` và `github.com/IfcOpenShell/bonsai`. Mã Bonsai hiện nằm trong `IfcOpenShell/IfcOpenShell` tại `src/bonsai` (đã clone thưa, HEAD 2026-11-08).

**FreeCAD: đọc sâu hơn (bản 1.1.4 tại máy)**
- *Tường từ đường*: `ArchWall.getExtrusionData` lấy đối tượng nền (đường, wire, sketch), bề rộng (`Width`, hoặc `OverrideWidth` theo từng đoạn) và căn lề `Align` = Left/Right/Center (cũng theo từng đoạn qua `OverrideAlign`), dùng `DraftGeomUtils` (có `offsetWire`) để dựng biên dạng. Tức FreeCAD có xử lý góc cho **wire nối liền**, nhưng bắt người dùng đưa vào wire đã nối.
- *Nối tường*: `mergeShapes` ghi rõ **"Not currently implemented"** (trả về `None`); `areSameWallTypes` chỉ so `Width/Height/Align`.
- *Nối đoạn rời thành wire*: `Draft/draftfunctions/upgrade.py` `makeWires` dùng `Part.sortEdges` rồi `Part.Wire`; `makeFaces` dựng mặt từ wire kín. Đây là phép hình học thuần, không gán ngữ nghĩa.
- *Phòng*: `ArchSpace` dùng thuộc tính `Boundaries` (do người dùng chọn đối tượng/mặt), `getShape` tính hình từ các mặt biên đó; không tự dò phòng từ tường.
- *Xuất IFC*: `exportIFC.getIfcTypeFromObj` lấy class từ thuộc tính `IfcType` của đối tượng, nếu thiếu thì từ kiểu Draft qua bảng dịch, nếu vẫn không biết thì `IfcBuildingElementProxy`. Không có suy luận từ layer hay hình học.
- *Kết luận phù hợp nhận xét của người dùng*: FreeCAD giả định ngữ nghĩa đã được người dùng chọn (`makeWall`, `makeSpace`, `BIM_Convert`…) và **không có bộ máy "đường bất kỳ → tự nhận là tường"**. Khoảng trống nằm ở lớp hiểu CAD / trích ngữ nghĩa chứ không ở lớp xuất IFC. (Đã khớp với phát hiện lần đầu: `importDXF.py` không nhắc IFC.)

**IfcOpenShell và Bonsai: đọc sâu hơn**
- `src/bonsai/scripts/dxf2ifc.py` (125 dòng): chỉ xử lý `POLYLINE` dạng polyface mesh, tạo `IfcBuildingElementProxy` với `IfcFacetedBrep`, `Name` = tên layer; entity khác in "Skipping unsupported entity". **Giấy phép GPL-3.0 (theo tiêu đề tệp, Bonsai)**, nên không được chép vào repo của ta.
- Bonsai **không có chức năng nhập DXF**: các lần nhắc `dxf` trong `bonsai/tool/drawing.py` và `module/drawing/operator.py` chỉ là **xuất** bản vẽ SVG → DXF (`convert_svg_to_dxf`, dùng `ezdxf`, hoặc lệnh `svg2dxf` ngoài như `pstoedit`). Đóng câu hỏi mở trước đó.
- Thư viện `ifcopenshell.api` (0.9.0.post1, đã kiểm chữ ký) có sẵn: `geometry.add_wall_representation(context, length, height, thickness, offset, x_angle, clippings, booleans)` (hỗ trợ `clippings`: cắt vát đầu tường, hữu ích cho góc), `add_axis_representation`, `add_door_representation`, `add_window_representation`, `add_slab_representation(depth, polyline=…)`, `add_footprint_representation`; `feature.add_feature` / `add_filling`; `type.assign_type`; `material.add_layer`, `edit_layer_usage`. `ShapeBuilder` có `extrude`, `block`, `get_polyline_coords`…
- **Đã chạy thử** (`poc/ifc_opening_test.py`, 0.9.0.post1): tường 6 m dựng bằng `add_wall_representation`, lỗ 1,0 × 2,1 m bằng `add_feature`, cửa lấp bằng `add_filling` → có 1 `IfcRelVoidsElement` và 1 `IfcRelFillsElement`, hình học tường đổi từ 8 sang 16 đỉnh (bị khoét). Vậy `add_feature/add_filling` **chạy được trên 0.9.0.post1** với tường dựng kiểu này. Chưa mở bằng Bonsai/FreeCAD để xem bằng mắt.

**Thứ tự đọc người dùng đề xuất** (ezdxf → FreeCAD Draft → FreeCAD Arch → IfcOpenShell → Bonsai): đã đi qua cả 5; riêng ezdxf mới dùng, chưa đọc sâu mã ezdxf.

## Nguồn
- Mã nguồn FreeCAD 1.1.4 tại máy: `Mod/Draft/importDXF.py`, `Mod/BIM/bimcommands/{BimConvert,BimIfcElements,BimIfcProperties,BimPreflight}.py`, `Mod/BIM/Arch.py`, `Mod/BIM/nativeifc/` — đọc 2026-11-08 (FreeCAD 1.1.4 AppImage, bản dựng 2026-09-28)
- IfcOpenShell 0.9.0.post1 trong `.venv` (chạy thật, 2026-11-08)
- [FreeCAD docs — BIM Workbench](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/BIM_Workbench.md) và [Arch Wall](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Arch_Wall.md) — truy cập 2026-11-08 (tóm tắt tìm kiếm)
- [IfcOpenShell docs — api.pset](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/pset/index.html), [add_pset](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/pset/add_pset/index.html), [edit_pset](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/pset/edit_pset/index.html), [api.classification](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/classification/index.html), [api.pset_template](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/pset_template/index.html) — truy cập 2026-11-08 (tóm tắt tìm kiếm; chữ ký hàm đã kiểm bằng chạy thật)

## Câu hỏi còn mở
- Bonsai có công cụ nhập DXF → đối tượng BIM không: chưa xác minh (không thấy trong tìm kiếm).
- `ifctester` (IDS) và `ifcpatch` có dùng được để kiểm/làm giàu hàng loạt cho IFC của ta: chưa cài, chưa thử.
- Kịch bản `Arch.makeWall` hàng loạt theo layer trong `freecadcmd`: chưa chạy.
- Mã phân loại thật (Uniclass, OmniClass…) nên dùng cho dự án: chưa chọn, cần người dùng quyết định.
