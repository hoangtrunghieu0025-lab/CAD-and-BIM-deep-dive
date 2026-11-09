# Các hướng chuyển dữ liệu CAD sang BIM

- **Câu hỏi nghiên cứu**: Có những cách nào để biến bản vẽ CAD (DWG/DXF) thành mô hình BIM có thông tin (IFC/Revit/ArchiCAD), và hướng nào hợp với pipeline của dự án?
- **Kết luận ngắn**: Có 4 hướng: (A) dựng tay trên underlay, (B) công cụ có sẵn bán tự động (Revit/ArchiCAD/BricsCAD…), (C) script tự viết (`ezdxf` + `ifcopenshell`, Dynamo), (D) AI nhận dạng bản vẽ 2D. Với pipeline hiện tại, hướng C là hợp nhất vì tái lặp được và xuất IFC trực tiếp. Hướng D chưa đủ tin cậy để dùng một mình.
- **Độ tin cậy**: trung bình. Các nguồn là bài hướng dẫn của hãng, diễn đàn và bài tổng quan học thuật. Chỉ POC ở mục C được chạy thật (xem [poc-result](poc-result.md)). Hiệu quả thực tế của plugin thương mại **chưa xác minh**.

## Chi tiết

| Hướng | Cách làm | Độ tự động | Điểm mạnh | Hạn chế |
|---|---|---|---|---|
| **A. Dựng tay trên underlay** | Link/import DWG làm nền trong Revit; trace bằng công cụ Wall hoặc Pick Lines. ArchiCAD: đưa DWG vào Worksheet làm Trace Reference rồi vẽ tường đè lên | Thấp | Chất lượng và kiểm soát cao nhất | Tốn công; phụ thuộc người làm |
| **B. Công cụ có sẵn, bán tự động** | ArchiCAD: Magic Wand (giữ Space + công cụ Wall, bấm vào line/polyline/polygon). Revit: Pick Lines. BricsCAD: quảng bá chuyển bản vẽ line sang 3D BIM. Một số công cụ CAD-to-IFC cho gán layer → class IFC | Trung bình | Nhanh khi bản vẽ sạch | Magic Wand bị lỗi nếu DWG vào dạng block/Drawing hoặc nét đứt quanh cửa/cửa sổ; Revit tạo tường chỉ từ đoạn đơn, không từ polycurve và không từ đường dốc |
| **C. Script tự viết** | `ezdxf` đọc DXF → ánh xạ layer → tạo `IfcWall`… bằng `ifcopenshell.api` (hoặc Dynamo/pyRevit/Revit API cho Revit) | Cao nếu layer chuẩn | Tái lặp, kiểm soát được, xuất IFC thẳng, khớp `config/layer_mapping.yaml` | Phải tự xử lý đóng/nối nét, cao độ, độ dày, cửa trong tường. Chưa có converter mã nguồn mở trưởng thành để dùng sẵn; dự án gần nhất là SaN-architect-ai (MVP, 0 sao). Xem [open-source-dxf-to-ifc-projects](open-source-dxf-to-ifc-projects.md) |
| **D. AI/Computer Vision** | Nhận dạng tường, ký hiệu từ PDF/ảnh bằng CNN/Faster R-CNN… | Cao về lý thuyết | Dùng được khi chỉ có ảnh/PDF | Bài tổng quan ISARC 2021 kết luận chưa có chuyển đổi 2D → BIM giàu ngữ nghĩa hoàn toàn tự động; chiều cao thường đặt mặc định hay nhập tay, cầu thang ít được nghiên cứu, lỗi bản vẽ xử lý kém |

### Ghi chú thêm
- **Revit**: Wall chỉ tạo từ đoạn thẳng/cung đơn; polyline phải tách thành từng đoạn và phải phẳng. Dynamo chuyển được polycurve DWG thành model line. Script cộng đồng có sẵn nhưng không tạo cửa/cửa sổ hay tường cong (nguồn: diễn đàn, độ tin cậy thấp).
- **IfcOpenShell**: `ifcopenshell.api.geometry.create_2pt_wall(file, element, context, p1, p2, elevation, height, thickness, is_si=True)` tạo tường giữa hai điểm, chỉ hỗ trợ context `Model/Body/MODEL_VIEW`. **Đã xác minh** bằng `inspect` trên `ifcopenshell 0.9.0.post1` cài trong `.venv`. Tường nhiều đoạn: gọi một lần cho mỗi đoạn, hoặc dựng profile bằng `ShapeBuilder.polyline` rồi extrude (OSArch, chưa tự chạy).
- **Hướng D, ví dụ**: pipeline nhiều giai đoạn dùng Faster R-CNN trên bộ CubiCasa5k (arXiv 2306.01642); bộ dữ liệu tổng hợp >1.000 BIM kèm mặt bằng (Automation in Construction, tập 181).

## Liên quan đến pipeline CAD → BIM → GPKG
- `src/cad2bim` hiện trích đối tượng từ DXF ra mô hình trung gian; bước còn thiếu là **ghi ra IFC**. POC cho thấy có thể làm từ cùng `layer_mapping.yaml`.
- Với dự án (dữ liệu mặt bằng tầng để làm bản đồ trong nhà), không cần LOD cao: tường extrude + `IfcSpace` từ polyline `A-AREA` + cửa là đủ.

## Nguồn
- [BIM Corner — DWG to IFC step by step](https://bimcorner.com/migration-of-cad-dwg-models-to-ifc-step-by-step-guide/) — truy cập 2026-11-08
- [NOVEDGE — Preparing DWG files for reliable IFC export](https://novedge.com/blogs/design-news/autocad-tip-preparing-dwg-files-for-reliable-ifc-export) — truy cập 2026-11-08 (chỉ đọc tóm tắt kết quả tìm kiếm)
- [Graphisoft — How to model wall from a 2D line (Magic Wand)](https://support.graphisoft.com/hc/en-us/articles/23126601413649-How-to-model-wall-from-a-2D-line) — truy cập 2026-11-08 (tóm tắt tìm kiếm)
- [Graphisoft — Tips to import DWG files as Trace Reference](https://community.graphisoft.com/t5/Data-Exchange-articles/Tips-to-Import-DWG-Files-as-Trace-Reference/ta-p/303459) — truy cập 2026-11-08 (tóm tắt tìm kiếm)
- [Autodesk Revit — Import walls / tạo tường từ underlay](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-DocumentPresent/files/GUID-0805BFCA-44E1-4DF4-9875-8238C7AB406E.htm) — truy cập 2026-11-08 (chỉ thấy tiêu đề; chưa đọc nội dung)
- [Speckle community — DWG to Revit separation lines](https://speckle.community/t/dwg-to-revit-separation-lines/11612) — truy cập 2026-11-08 (tóm tắt tìm kiếm)
- [IfcOpenShell docs — create_2pt_wall](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/geometry/create_2pt_wall/index.html) — truy cập 2026-11-08; chữ ký hàm kiểm lại bằng `inspect` trên bản cài local
- [ISARC 2021 — Systematic review of automated BIM modelling for existing buildings from 2D documentation](https://www.iaarc.org/publications/2021_proceedings_of_the_38th_isarc/a_systematic_review_of_automated_bim_modelling_for_existing_buildings_from_2d_documentation.html) — truy cập 2026-11-08 (tóm tắt tìm kiếm)
- [arXiv 2306.01642 — Automatic reconstruction of semantic 3D models from 2D floor plans](https://arxiv.org/abs/2306.01642v1) — truy cập 2026-11-08 (tóm tắt tìm kiếm)

## Câu hỏi còn mở
- Hiệu quả thật của plugin thương mại (BricsCAD, Trimble Quadri, WiseBIM…) trên bản vẽ Việt Nam: chưa xác minh, cần bản dùng thử.
- Hướng D có dùng được với mặt bằng PDF/ảnh của người dùng không: chưa thử.
