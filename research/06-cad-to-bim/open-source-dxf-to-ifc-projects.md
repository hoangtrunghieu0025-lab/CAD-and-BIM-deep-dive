# Dự án mã nguồn mở chuyển DXF/CAD → IFC

- **Câu hỏi nghiên cứu**: Đã có converter DXF/DWG → IFC mã nguồn mở nào dùng được hoặc tham khảo được cho pipeline của dự án?
- **Kết luận ngắn**: Không thấy công cụ nào trưởng thành, kiểu "bấm là chạy". Có một script chính thức của IfcOpenShell (`dxf2ifc.py`, chỉ cho polyface mesh, không phải mặt bằng) và một vài dự án nhỏ cá nhân. Gần nhất với bài toán của ta là **SaN-architect-ai** (DXF theo layer → tường/cửa/phòng → IFC2x3, 2 commit, 0 sao). Vì vậy hướng "tự viết bằng `ezdxf` + `ifcopenshell`" vẫn hợp lý, nhưng nên **mượn thiết kế** của SaN-architect-ai (nối đầu mút, dựng góc, khớp cửa vào tường, lỗ mở, bước kiểm tra điểm số).
- **Độ tin cậy**: thấp đến trung bình. Toàn bộ thông tin dưới đây lấy từ trang README, issue, thảo luận và kết quả tìm kiếm. **Chưa clone hay chạy dự án nào** (trừ POC của ta ở [poc-result](poc-result.md)). Số sao/commit/giấy phép là tại thời điểm truy cập 2026-11-08, và các trang không cho thấy ngày commit cuối.

## Chi tiết

| Dự án | Làm gì | Công nghệ | Giấy phép | Mức trưởng thành | Dùng cho ta |
|---|---|---|---|---|---|
| [**vylint-22/SaN-architect-ai**](https://github.com/vylint-22/SaN-architect-ai) | DWG → DXF (ODA File Converter) → phân loại tường/cửa/cửa sổ theo layer → nối đầu mút, dựng góc, tìm phòng → khớp cửa vào tường → IFC2x3 (tường, lỗ mở, `IfcSpace`) → chấm điểm so với DXF | Python 3.10+; mỗi bước đọc/ghi JSON (`SCHEMA.md`) | Chưa chọn (README gợi ý MIT) | MVP, 2 commit, 0 sao; README thừa nhận chưa đạt mục tiêu 95% trên file thật. Chỉ một tầng, tường vuông góc/gần vuông góc | **Gần nhất.** Cấu trúc 5 bước và `layer_config.yaml` tương đồng `config/layer_mapping.yaml` của ta. Đọc code để học cách nối tường, khớp cửa, bước validate. Không phụ thuộc vào nó |
| [**IfcOpenShell `dxf2ifc.py`**](https://github.com/IfcOpenShell/IfcOpenShell/issues/2151) (trong `src/blenderbim`, nay `src/bonsai/scripts`) | Script ví dụ, đọc DXF bằng `ezdxf` và ghi IFC | Python, `ezdxf`, `ifcopenshell` | LGPL (theo IfcOpenShell) | Maintainer gọi là "experimental". Chỉ xử lý `AcDbPolyFaceMesh` (mỗi mặt thành `IfcFace` trong `IfcBuildingElementProxy` ở bản đầu). Issue #2151 báo lỗi với DXF từ AutoCAD qua ODA File Converter; đã đóng bằng PR #8780 (2026-07-19) cho script **bỏ qua** entity không hỗ trợ thay vì lỗi | **Không dùng được cho mặt bằng LINE/LWPOLYLINE.** Chỉ tham khảo cách ghi hình học vào IFC. Maintainer cũng nói IFC biểu diễn được đường/đường cong 2D, không bắt buộc solid hoá |
| [**AMostafaH/CrossBIM**](https://github.com/AMostafaH/CrossBIM) | Ảnh raster → DXF, và DXF → IFC | ASP.NET Core 3.1, NetDXF, Xbim, EmguCV | Không thấy | Đồ án tốt nghiệp, 2 commit, 2 sao. Yêu cầu mỗi hạng mục xây dựng một layer riêng, chỉ bản vẽ kết cấu, mỗi file một mặt bằng | Chỉ tham khảo ý tưởng; khác ngôn ngữ (.NET) |
| [**VDobranov/DXF2IFC2D**](https://github.com/VDobranov/DXF2IFC2D) | Dựng IFC cho dự án Wikihouse từ DXF của máy CNC | Python, `ezdxf`/`ifcopenshell` (theo tag repo) | Không thấy | "Thử nghiệm", 33 commit, 0 sao; cách ánh xạ không được mô tả trong README | Ít liên quan (bản vẽ CNC, không phải kiến trúc) |
| **NetDXF + Xbim** (diễn đàn buildingSMART, [bài này](https://forums.buildingsmart.org/t/converting-dxf-to-ifc-format/3702)) | Người dùng tự viết; chỉ chạy với hình chữ nhật song song trục | .NET | — | Không có mã công bố | Chỉ là bài học: cần xử lý hình chữ nhật xoay (Moult gợi ý chọn đường chéo xa nhất để suy ra kích thước) |

### Dự án gần kề (không nhận DXF, nhưng đáng đọc mã)
- [**sahilyousafp/FloorPlanToIFC**](https://github.com/sahilyousafp/FloorPlanToIFC): ảnh mặt bằng → Mask R-CNN (CubiCasa5K) → IFC4 `IfcWall/IfcDoor/IfcWindow`, có cắt lỗ mở. Dành cho hướng D (AI/ảnh).
- [**joyjo/to-generate-2D-floorplan-CAD-from-3D-point-clouds**](https://github.com/joyjo/to-generate-2D-floorplan-CAD-from-3D-point-clouds): `create_ifc.py` dựng IFC từ tường đã phát hiện; dùng IfcConvert xuất SVG mặt bằng.
- [**Cloud2BIM**](https://arxiv.org/html/2503.11498v2): Python, point cloud → IFC4 bằng IfcOpenShell. Mã sinh IFC dùng làm tham chiếu.
- [**rebeccasc/BIMtoOSM**](https://github.com/rebeccasc/BIMtoOSM) và các công cụ ngược chiều (IFC → mặt bằng): xem `research/05-market-tools/`.

### Đường đi bằng công cụ GUI mã nguồn mở
- **DWG → DXF**: ODA File Converter (miễn phí nhưng **không** mã nguồn mở; giấy phép do ODA đặt, cần kiểm trước khi dùng thương mại) hoặc LibreDWG `dwg2dxf` (GPLv3, mã nguồn mở nhưng chưa hỗ trợ đủ entity). FreeCAD nhập DWG qua một trong hai công cụ này, nên thực chất đi qua DXF ([FreeCAD docs](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FreeCAD_and_DWG_Import.md)).
- **FreeCAD → IFC**: một người dùng OSArch đã chuyển DWG sang dự án IFC qua FreeCAD, nhưng báo điểm sai cao độ và sai tỷ lệ khi mở trong BlenderBIM; thread không có lời giải ([OSArch](https://community-test.osarch.org/thread/2547/p1)). Điều này **chưa xác minh** ở bản mới.
- **Bonsai**: không thấy tài liệu nói rõ Bonsai nhập DXF/DWG; một kết quả tìm kiếm liệt kê ".dxf → .ifc" trong bảng định dạng nhưng trang gốc chưa đọc được. Cách thông dụng là nhập DXF vào Blender làm đường rồi dùng script (maintainer cảnh báo không phải trình xem nào cũng hiển thị biểu diễn dạng đường).

### Video hướng dẫn (YouTube / wiki)
Đã lấy **phụ đề tự động** bằng `yt-dlp` (2026-11-08) và đọc toàn bộ cho 2 video; phụ đề tự động có thể sai chính tả thuật ngữ. Cả hai video **không** giải quyết bài toán mặt bằng CAD → IFC.

| Video | Nội dung thật | Dùng được cho ta? |
|---|---|---|
| [FreeCAD: Converting 2D Plans To 3D. The Very Basics!](https://www.youtube.com/watch?v=qJGhboRjtmg) (MangoJelly, 2025-10-11, ~20 phút) | Ví dụ là **bản vẽ cơ khí nhiều hình chiếu** (hình chiếu bằng + hình chiếu cạnh, dạng SVG; nói DXF/DWG "cùng quy trình"). Quy trình: nhập file → gom nhóm từng hình chiếu → dời/xoay các hình chiếu cho khớp bằng snap → `Upgrade` (Draft) các cạnh thành **wire kín**, kiểm bằng Check Geometry (`closed = true`) → Draft Sketch → Pad/Pocket trong Part Design. Lưu ý: gốc toạ độ file 2D thường ở góc trang, phải dời về tâm trước khi chuyển | **Không phải BIM**: không có tường, tầng, class IFC, không xuất IFC. Chỉ học được: nối cạnh thành wire kín và kiểm tra đóng, gốc toạ độ lệch (trùng rủi ro về toạ độ ta đã ghi) |
| [Your first BIM drawing in 20 mins: Blender, Bonsai and IFC](https://www.youtube.com/watch?v=fxpIg-su-00) (Prof Rino, 2025-11-07, ~24 phút) | Dựng **từ đầu** trong Bonsai, không nhập DXF. IFC4, hệ mét, template demo IFC4; vẽ tường bằng polyline (chọn kiểu tường 300 mm cho tường ngoài, 100 mm cho vách), nhập chiều dài từng đoạn, đóng bằng Shift+C; đổi chiều cao tường qua tham số; thêm cửa/cửa sổ rồi dời bằng `G` + nhập khoảng cách; sau khi dời cửa phải bấm **Shift+G** để lỗ mở trong tường cập nhật; tạo type cửa riêng (duplicate) để đổi kích thước theo từng type; sàn bằng polyline; xuất bản vẽ mặt bằng (cắt ở cao 1 m trên tầng) | Gián tiếp: (1) xác nhận mô hình IFC kiểu "tường theo type + cao độ tham số + cửa tạo lỗ mở" khớp với POC; (2) lỗ mở là bước riêng, phải cập nhật sau khi dời cửa, nên pipeline của ta phải tạo `IfcOpeningElement` có chủ đích |
| `Wg4edLGioPw` (Freecad 2D to 3D Floor Plan - Simple Trick) | `yt-dlp` báo "This video is unavailable" | Không đọc được; bỏ |
| [OSArch wiki — Blender 2D dxf to ifc](https://wiki.osarch.org/blender-2d-dxf-to-ifc/) (cập nhật 2021-11-05) | Đã đọc trang: script Sverchok đùn các hình chữ nhật (lỗ cửa) kèm chữ ghi cao độ thành lỗ mở; mục "step by step" trống, không có link video; mã ở [JanFilipec/Sverchok-Tutorials](https://github.com/JanFilipec/Sverchok-Tutorials/tree/main/2D%20to%20ifcOpening) | Chỉ là ý tưởng lấy cao độ lỗ mở từ chữ trong bản vẽ |

Kết luận: không tìm thấy video nào dạy chuỗi `ezdxf` → `ifcopenshell` dựng tường từ DXF, và không video nào cho thấy nhập DXF mặt bằng thành đối tượng BIM. OSArch có người nói làm thủ công "2D dwg → dxf → IFC" trong Bonsai để bóc khối lượng, nhưng không kèm hướng dẫn.

## Liên quan đến pipeline CAD → BIM → GPKG
- Không có công cụ nào để dùng nguyên. Đề xuất: giữ hướng C (script tự viết) và dùng SaN-architect-ai làm **bản thiết kế tham chiếu**, đặc biệt: (1) nối đầu mút với dung sai, (2) khớp cửa/cửa sổ vào tường gần nhất, (3) bước chấm điểm DXF ↔ IFC (ta có thể làm bằng cách so với đường DXF → GPKG hiện có).
- POC tiếp theo nên thêm: thử clone và chạy SaN-architect-ai trên `samples/sample-floor-1.dxf` (cần đặt `layer_config.yaml` khớp layer mẫu); so kết quả với POC `dxf_walls_to_ifc.py` về số tường, phòng, cửa.
- Ghi chú giấy phép: SaN-architect-ai chưa có giấy phép rõ ràng nên **không sao chép mã** vào repo; chỉ học ý tưởng. LibreDWG là GPLv3, cần cân nhắc nếu đóng gói cùng.

## Nguồn
- [GitHub — vylint-22/SaN-architect-ai](https://github.com/vylint-22/SaN-architect-ai) — truy cập 2026-11-08 (đã đọc README)
- [GitHub — IfcOpenShell issue #2151 (DXF → IFC example script)](https://github.com/IfcOpenShell/IfcOpenShell/issues/2151) — truy cập 2026-11-08
- [GitHub — IfcOpenShell discussion #4293](https://github.com/IfcOpenShell/IfcOpenShell/discussions/4293) — truy cập 2026-11-08
- [buildingSMART forum — Converting DXF to IFC format](https://forums.buildingsmart.org/t/converting-dxf-to-ifc-format/3702) — truy cập 2026-11-08
- [GitHub — AMostafaH/CrossBIM](https://github.com/AMostafaH/CrossBIM) — truy cập 2026-11-08
- [GitHub — VDobranov/DXF2IFC2D](https://github.com/VDobranov/DXF2IFC2D) — truy cập 2026-11-08
- [GitHub — sahilyousafp/FloorPlanToIFC](https://github.com/sahilyousafp/FloorPlanToIFC) — truy cập 2026-11-08 (chỉ tóm tắt tìm kiếm)
- [GitHub — joyjo/to-generate-2D-floorplan-CAD-from-3D-point-clouds](https://github.com/joyjo/to-generate-2D-floorplan-CAD-from-3D-point-clouds) — truy cập 2026-11-08 (chỉ tóm tắt tìm kiếm)
- [arXiv 2503.11498 — Cloud2BIM](https://arxiv.org/html/2503.11498v2) — truy cập 2026-11-08 (chỉ tóm tắt tìm kiếm)
- [FreeCAD docs — FreeCAD and DWG Import](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FreeCAD_and_DWG_Import.md) — truy cập 2026-11-08 (chỉ tóm tắt tìm kiếm)
- [OSArch — DWG → IFC qua FreeCAD](https://community-test.osarch.org/thread/2547/p1) — truy cập 2026-11-08 (chỉ tóm tắt tìm kiếm)

## Câu hỏi còn mở
- Video `Wg4edLGioPw` không còn khả dụng; nếu bạn có video khác về DXF mặt bằng → BIM, đưa link để lấy phụ đề.
- Chạy thật SaN-architect-ai và `dxf2ifc.py` bản Bonsai hiện tại: chưa làm.
- Bonsai/FreeCAD có công cụ nhập DXF → đối tượng BIM (tường, cửa) trực tiếp hay không: chưa xác minh.
- Các dự án thương mại/đóng nguồn (BricsCAD, Trimble…) vẫn chưa khảo sát, xem ghi chú [approaches](cad-to-bim-approaches.md).
- Có thể còn dự án khác mà các lượt tìm kiếm chưa thấy (GitLab, Gitee, repo ít sao).
