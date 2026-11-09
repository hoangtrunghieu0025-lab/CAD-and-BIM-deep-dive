# Khảo sát GitHub theo từ khoá: repo nào áp dụng được cho converter DXF → IFC

- **Câu hỏi nghiên cứu**: Theo bộ từ khoá (CAD2BIM, Scan2BIM, Floor Plan Parsing/Reconstruction, Blueprint Vectorization, IFC Generation, DXF/DWG To IFC, Point Cloud To BIM, LLM/VLM BIM…), repo mã nguồn mở nào có ý tưởng hoặc mã đáng áp dụng cho converter DXF → IFC của dự án?
- **Kết luận ngắn**: Có 3 repo **giấy phép MIT, đã đọc mã** đáng học nhất: **Mcrauli/dwg2ifc** (DXF/DWG → IFC4 theo layer, solid tham số, profile TOML), **aec-platform/roomgraph** (thuật toán ghép hai nét song song thành tường có độ dày, lấy lỗ mở từ khoảng hở, dựng phòng) và **naquib0513/2D23D** (nối đoạn tường, xử lý giao điểm, Pset "provisional"). Các lượt trước kết luận "chưa có converter nào trưởng thành"; điều đó **vẫn đúng với bản dùng ngay**, nhưng tôi đã bỏ sót dwg2ifc và roomgraph vì lúc đó chỉ dùng tìm kiếm web. Phần còn lại (scan-to-BIM, AI nhận dạng, LLM) là hướng khác, chỉ nên tham khảo.
- **Độ tin cậy**: trung bình đến cao. Số sao, giấy phép, ngày push lấy từ API tìm kiếm của GitHub ngày 2026-11-08 (số liệu thay đổi). Các repo ở nhóm A và B đã clone và đọc mã, **chưa chạy**. Nhóm C chỉ có siêu dữ liệu và mô tả, **chưa đọc mã**.

## Cách tìm
- Gọi `api.github.com/search/repositories` (chưa đăng nhập, giới hạn ~10 lần/phút) với: `DXF IFC converter`, `DXF to IFC`, `DWG to IFC`, `CAD2BIM`, `floor plan IFC ifcopenshell`, `scan2bim`, `point cloud to IFC`, `floorplan vectorization`, `ezdxf ifcopenshell`, `floor plan to BIM`, `LLM BIM IFC`; cộng 3 lượt tìm web cho các từ khoá học thuật.
- **Chưa tìm riêng**: `Blueprint Vectorization`, `Architectural Drawing Parsing`, `CAD Semantic Segmentation`, `Generative BIM`, `VLM BIM`, `OpenBIM AI`, `Semantic BIM Reconstruction`, `pdf to IFC` (hết hạn mức API); chỉ được phủ gián tiếp qua các truy vấn gần nghĩa. Có thể còn sót.

## A. Đã đọc mã, giấy phép MIT — áp dụng được

| Repo | Làm gì | Phần đáng áp dụng | Hạn chế |
|---|---|---|---|
| [**Mcrauli/dwg2ifc**](https://github.com/Mcrauli/dwg2ifc) (MIT, Python ≥3.12, ~24k dòng gồm test; 39 commit, push 2026-05-29; bản `0.3.0-alpha31`) | DXF/DWG → IFC4 cho thiết kế lạnh/HVAC Phần Lan. Layer → loại IFC bằng **profile TOML** (`profiles/`, `mapper.py`: glob không phân biệt hoa thường, **khớp đầu tiên thắng**, tự bỏ tiền tố xref `xref\|layer`); mỗi luật mang chiều cao/độ dày mặc định, `pset_overrides` | (1) `ifc_writer/builders.py` `add_wall`: tường là **`IfcExtrudedAreaSolid` + `IfcRectangleProfileDef`** theo đường tim (solid tham số, không phải mesh), đặt bằng ma trận xoay; (2) `add_door`, `add_window`, `add_slab`, `add_provision_for_void`; (3) **GUID ổn định** từ GUID trong DWG (XDATA) để cập nhật lại không đổi định danh; (4) gộp nhiều tầng: `world_Z = cao độ tầng + dxf_Z`; (5) `quality.py` báo cáo kiểm tra phân loại; (6) đọc `INSERT.virtual_entities()` để áp phép biến đổi block, đọc `ATTRIB` | Chuyên ngành (HVAC, phân loại RAVA/Talo2000, Pset `FI_*` tiếng Phần Lan). Cửa là hộp chứ không cắt lỗ trong tường (`PROVISIONFORVOID` chỉ cho lỗ kỹ thuật). Layer không khớp luật **bị bỏ im lặng**. DWG cần AutoCAD (`accoreconsole`), không cần cho DXF. Đang alpha |
| [**aec-platform/roomgraph**](https://github.com/aec-platform/roomgraph) (MIT, Python, không phụ thuộc; 17 commit, push 2026-08-10) | **PDF vector** mặt bằng → phòng, diện tích, cửa/cửa sổ, đồ thị kề phòng; xuất JSON, GeoJSON, IFC4 thô, SVG. README có nhãn tiếng Việt, đọc tỉ lệ từ ký hiệu kích thước/thanh tỉ lệ | `walls.py`: **tường vẽ bằng hai nét song song** → gom đoạn lên **đường thẳng vô hạn**, ghép cặp qua bề dày hợp lý, **lỗ mở đọc từ khoảng hở** của cặp đường. Chính là điểm POC của ta còn thiếu (POC coi mỗi LINE là một tường). Cũng có `rooms.py`/`planar.py` (dựng phòng từ đồ thị phẳng), `scale.py`, `symbols/` (nhận ký hiệu cửa), `export/ifc.py` (`IfcWallStandardCase` có lỗ thật, `IfcDoor`/`IfcWindow` lấp lỗ, `IfcSpace`) | Đầu vào là PDF, không phải DXF (cần thay lớp đọc bằng `ezdxf`, phần hình học thuần Python dùng lại được). README nói IFC "rough — mọi chiều cao là giả định" |
| [**naquib0513/2D23D**](https://github.com/naquib0513/2D23D) (MIT; 4 commit, push 2025-11-08) | DXF mặt bằng (xuất từ Revit) → IFC4 "giàn" tạm thời: lưới, tường, cột, sàn, móng, cửa. README: kiểm trên 1 công trình 7 tầng, 54 MB DXF, 1038 tường, 35 giây (số liệu của tác giả, **chưa kiểm**) | `detection/wall_detector.py` (`merge_wall_segments`: nối đoạn thẳng hàng/chạm đầu, dung sai điểm và góc), `wall_intersections.py` (phát hiện giao điểm, chỉnh hình học tại góc), `ifc_generator.py` (`_add_provisional_pset`: Pset đánh dấu phần tử là tạm), `spatial_index.py` | Thiên về mô hình kết cấu theo lưới trục; phụ thuộc quy ước xuất DXF của Revit. Mới ở "Phase 1" |

**Các hành động áp dụng đề xuất** (xếp theo giá trị/công sức):
1. Ghép hai nét song song thành một tường có độ dày và lấy lỗ mở từ khoảng hở (theo ý tưởng `roomgraph/walls.py`); đây là bước còn thiếu lớn nhất của POC.
2. Tường dạng `IfcExtrudedAreaSolid` theo đường tim như `add_wall` của dwg2ifc, hoặc tiếp tục `create_2pt_wall` của IfcOpenShell (cùng kết quả, ít mã hơn).
3. Cắt lỗ cho cửa: dùng `feature.add_feature` + `add_filling` (từ alvin528/CAD2BIM) hoặc cách của roomgraph.
4. Cấu hình luật theo **profile** như dwg2ifc (mỗi luật: mẫu layer, class, chiều cao/độ dày mặc định, Pset); tương đương `config/layer_mapping.yaml` nhưng thêm Pset theo luật và log layer không khớp (dwg2ifc bỏ im lặng, ta đã ghi `unmatched_layers.csv`).
5. GUID ổn định để cập nhật lại không đổi định danh.
6. Pset đánh dấu "provisional/giả định" (2D23D, alvin528) cho cao độ và độ dày.

## B. Đã đọc mã, **không** nên dùng làm nền

| Repo | Lý do |
|---|---|
| [Kevinscsatoshi/ifcbim](https://github.com/Kevinscsatoshi/ifcbim), [alvin528/CAD2BIM](https://github.com/alvin528/CAD2BIM) | Đã đánh giá ở [cad2bim-and-ifcbim-code-review](cad2bim-and-ifcbim-code-review.md) |
| [GabxSup/DWG-to-IFC-Converter](https://github.com/GabxSup/DWG-to-IFC-Converter) | 88 dòng, 3 commit, không giấy phép; chú thích trong mã nói chưa đùn hình ("in a real app, we would extrude") |
| [Abdallah-Sallem/2D_to_3D-from-DXF-to-IFC](https://github.com/Abdallah-Sallem/2D_to_3D-from-DXF-to-IFC) | Tên dễ gây hiểu nhầm: README là **mô tả ngôn ngữ tự nhiên → IFC** qua LLM Mistral, không đọc DXF; không giấy phép |
| [mtak35/cad2ingetrazo](https://github.com/mtak35/cad2ingetrazo) | CAD → mô hình trong phần mềm IngeTrazo, giấy phép **GPL-3.0**, mã gắn chặt với ứng dụng đó; chưa đọc sâu |
| CrossBIM (.NET), SaN-architect-ai | Xem [open-source-dxf-to-ifc-projects](open-source-dxf-to-ifc-projects.md) |

## C. Chưa đọc mã — siêu dữ liệu GitHub và mô tả, tham khảo ý tưởng
> **Cập nhật 2026-11-08**: sáu repo trong nhóm này (Cloud2BIM, A-Scan2BIM, FloorplanTransformation, VecFloorSeg, ifc-bonsai-mcp, ifc-floorplan) đã được đọc mã ở [github-group3-code-review](github-group3-code-review.md); các dòng dưới giữ nguyên để lưu vết lần khảo sát đầu.

| Nhóm / từ khoá | Repo (sao · giấy phép · push) | Ghi chú |
|---|---|---|
| Scan2BIM / Point Cloud To BIM | [VaclavNezerka/Cloud2BIM](https://github.com/VaclavNezerka/Cloud2BIM) (151★ · MIT · 2026-08) ; [weiliansong/A-Scan2BIM](https://github.com/weiliansong/A-Scan2BIM) (75★ · không giấy phép · 2024-06) ; [vijayjayakumar-skema/scan2bim](https://github.com/vijayjayakumar-skema/scan2bim) (MIT, point cloud phòng → IFC) | Cloud2BIM có pipeline Python sinh IFC4 bằng IfcOpenShell (bài arXiv 2503.11498): đọc mã phần ghi IFC khi cần |
| Floor plan → BIM bằng AI | [zssjh/ArrangementNet](https://github.com/zssjh/ArrangementNet) (40★ · C++ · 2023) ; [Mr-Daker/Floor-Plan](https://github.com/Mr-Daker/Floor-Plan) (SegFormer/Mask2Former → BIM) ; [newva/dwg-bim_AI](https://github.com/newva/dwg-bim_AI) (MIT) ; [hyunjun97/Multiview2BIM](https://github.com/hyunjun97/Multiview2BIM) | Hướng ảnh/PDF; ta chưa cần |
| Vectorization / Floor Plan Parsing | [art-programmer/FloorplanTransformation](https://github.com/art-programmer/FloorplanTransformation) (687★ · MIT · Lua, ICCV 2017) ; [DrZiji/VecFloorSeg](https://github.com/DrZiji/VecFloorSeg) (69★, phân đoạn mặt bằng **dạng vector**) ; [luozn15/FloorplanGAN](https://github.com/luozn15/FloorplanGAN) (MIT) ; [TINY-KE/FloorPlanParser](https://github.com/TINY-KE/FloorPlanParser) | VecFloorSeg gần CAD vector nhất: ý tưởng phân loại phần tử trên đồ thị đoạn thẳng khi tên layer vô nghĩa |
| CAD dữ liệu | [FloorPlanCAD](https://huggingface.co/datasets/Voxel51/FloorPlanCAD) (bộ dữ liệu ký hiệu CAD, bài ICCV 2021; trang gốc đã ngừng 2022 theo thẻ Hugging Face) | Có thể dùng đánh giá phân loại ký hiệu nếu sau này làm AI |
| LLM / VLM BIM | [Show2Instruct/ifc-bonsai-mcp](https://github.com/Show2Instruct/ifc-bonsai-mcp) (67★ · MIT) ; [MCP4IFC](https://show2instruct.github.io/mcp4ifc/) (arXiv 2511.05533) ; [ryanultralife/llm-bim](https://github.com/ryanultralife/llm-bim) (MIT) ; [nbharathik/ifc-console](https://github.com/nbharathik/ifc-console) (Apache-2.0) ; [mac999/BIM_LLM_code_agent](https://github.com/mac999/BIM_LLM_code_agent) | Dùng để **hỏi đáp/chỉnh sửa IFC** hoặc sinh IFC từ mô tả; có thể làm công cụ kiểm tra IFC sau khi chuyển, không thay bước DXF → IFC |
| Công cụ gộp | [datadrivenconstruction/cad2data-Revit-IFC-DWG](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG) (547★ · giấy phép `NOASSERTION`) ; [OpenAEC-Foundation/building-py](https://github.com/OpenAEC-Foundation/building-py) (52★) ; [cad-gis-bim-interop](https://github.com/cad-gis-bim-interop/cad-gis-bim-interop) | Chưa xác minh: cad2data có vẻ dùng bộ chuyển đổi nhị phân bên ngoài (chưa mở), cần đọc giấy phép trước khi dùng |
| Ngược chiều (kiểm tra) | [Show2Instruct/ifc-floorplan](https://github.com/Show2Instruct/ifc-floorplan) | IFC → phòng/diện tích dạng JSON/SVG: dùng để kiểm chéo IFC của ta |
| arXiv | `arxiv.org/search/?query=CAD2BIM` trả **0 kết quả** | Bài liên quan ở các note khác (arXiv 2306.01642, ISARC 2021, 2503.11498, 2511.05533) |

## Liên quan đến pipeline CAD → BIM → GPKG
- **Ưu tiên đọc sâu** (và nếu được thì chạy trong môi trường cách ly) theo thứ tự: roomgraph `walls.py` → dwg2ifc `ifc_writer/builders.py` + `mapper.py` + `profiles/` → 2D23D `wall_detector.py` + `wall_intersections.py`.
- **Giấy phép**: cả ba là MIT, cho phép tái sử dụng khi giữ thông báo bản quyền; vẫn nên viết lại theo thiết kế của ta thay vì sao chép nguyên khối (dwg2ifc gắn chặt miền HVAC Phần Lan).
- Cấu trúc đề xuất cho `src/cad2bim`: `segments → wall_pairs (roomgraph-style) → rooms → openings → ifc_writer → enrich`, tái dùng `layer_mapping.yaml` và log layer lạ.
- Sau khi có IFC, dùng `ifc-floorplan` (hoặc `src/extract/ifc.py` sẵn có) để kiểm chéo với DXF → GPKG.

## Nguồn
- [GitHub Search API](https://docs.github.com/en/rest/search/search#search-repositories) — truy cập 2026-11-08 (siêu dữ liệu sao, giấy phép, ngày push)
- Các repo trong bảng — truy cập 2026-11-08; **đã clone và đọc mã**: Mcrauli/dwg2ifc, aec-platform/roomgraph, naquib0513/2D23D, GabxSup/DWG-to-IFC-Converter, Abdallah-Sallem/2D_to_3D-from-DXF-to-IFC (+ hai repo ở note trước). Còn lại chỉ siêu dữ liệu hoặc tóm tắt tìm kiếm.
- [Raster-to-Vector (art-programmer)](https://github.com/art-programmer/FloorplanTransformation), [FloorPlanCAD — Hugging Face](https://huggingface.co/datasets/Voxel51/FloorPlanCAD), [FloorPlanCAD arXiv 2105.07147](https://arxiv.org/abs/2105.07147), [MCP4IFC arXiv 2511.05533](https://arxiv.org/html/2511.05533v1) — tóm tắt tìm kiếm

## Câu hỏi còn mở
- Chạy dwg2ifc và roomgraph trên `samples/sample-floor-1.dxf` (cần tạo profile cho layer mẫu, hoặc chuyển DXF → PDF vector cho roomgraph): chưa làm.
- Thuật toán ghép cặp đường của roomgraph có chịu được DXF thật (nét đứt, nhiều lớp, tường cong): chưa kiểm.
- Các từ khoá chưa tìm riêng (xem mục "Cách tìm"): cần chạy lại khi API hết giới hạn.
- Giấy phép đầy đủ của dwg2ifc, roomgraph, 2D23D: mới thấy file LICENSE và nhãn MIT của API, chưa đối chiếu nội dung từng file.
