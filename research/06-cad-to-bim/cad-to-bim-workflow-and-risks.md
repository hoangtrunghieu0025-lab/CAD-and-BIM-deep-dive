# Quy trình CAD → BIM đề xuất, ánh xạ layer → IFC và rủi ro

- **Câu hỏi nghiên cứu**: Quy trình chuẩn từng bước, bảng ánh xạ layer → class IFC và các rủi ro khi chuyển DXF/DWG sang IFC?
- **Kết luận ngắn**: Quy trình 8 bước (chuẩn hoá → ánh xạ layer → trích hình học → dựng đối tượng → cấu trúc không gian → thuộc tính → kiểm tra → thử trên một tầng). Rủi ro lớn nhất là bản vẽ 2D thiếu cao độ/độ dày và đặt tên layer không thống nhất.
- **Độ tin cậy**: trung bình. Các bước 1–6 theo hướng dẫn BIM Corner; mapping class IFC lấy từ `docs/mapping-design.md`; POC chạy thật trên mẫu của dự án.

## Chi tiết

### Quy trình 8 bước
1. **Chuẩn hoá CAD**: kiểm đơn vị (`$INSUNITS`; 0 = unitless thì lấy từ config), PURGE/AUDIT/xoá layer thừa, xử lý xref (bind hoặc gom), tách theo bộ môn và theo tầng.
2. **Ánh xạ layer → loại đối tượng**: dùng `config/layer_mapping.yaml` (khớp đầu tiên thắng; layer lạ ghi vào `unmatched_layers.csv`).
3. **Trích hình học**: LINE/LWPOLYLINE → đoạn tim tường; polyline kín → footprint phòng; INSERT block → cửa/thiết bị (điểm chèn + góc xoay).
4. **Dựng đối tượng IFC**: tường bằng extrude theo đoạn, sàn/phòng từ profile, cửa là `IfcDoor` gắn vào tường.
5. **Cấu trúc không gian**: `IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey`, gán phần tử bằng `spatial.assign_container`.
6. **Thuộc tính**: tên, `PredefinedType`, vật liệu, Pset (xem [property-sets](../02-bim/property-sets-and-classification.md)).
7. **Kiểm tra chất lượng**: mở lại bằng `ifcopenshell`, so số lượng và bounding box với DXF; mở thử bằng Bonsai/FreeCAD (xem TASK-016).
8. **Thử trên một tầng** trước khi chạy cả toà nhà.

### Bảng ánh xạ layer → class IFC
Layer lấy từ `config/layer_mapping.yaml` (nhãn `sample` = đã khớp mẫu của dự án; `example` = tên theo NCS/AIA, chưa đối chiếu chuẩn gốc).

| Layer CAD | Hình học nguồn | Class IFC | Ghi chú | Trạng thái |
|---|---|---|---|---|
| `A-WALL` | LINE / LWPOLYLINE | `IfcWall` | Cao độ và độ dày là tham số nhập tay | sample (POC đã chạy) |
| `A-AREA` | LWPOLYLINE kín | `IfcSpace` | Nhãn từ `A-AREA-IDEN` gán vào `Name` | sample |
| `A-DOOR` | INSERT (block `DOOR`) | `IfcDoor` | Cần tạo lỗ mở (`IfcOpeningElement`) nếu muốn đúng hình học | sample |
| `A-GLAZ` | — | `IfcWindow` | | unverified |
| `A-COLS` | — | `IfcColumn` | | unverified |
| `A-STRS` | — | `IfcStair` | | unverified |

### Rủi ro và cách giảm
| Rủi ro | Vì sao | Giảm thiểu |
|---|---|---|
| Thiếu cao độ, độ dày | CAD 2D không mang thông tin này | Tham số theo layer/loại; bảng mặc định theo dự án; ghi rõ là giả định |
| Tên layer không thống nhất | Mapping không khớp | Chuẩn hoá tên, báo layer lạ, bổ sung rule |
| Tường là nét đôi hoặc đứt quanh cửa | Không suy ra được đường tim | Gộp/nối nét trước; có thể dùng hai nét song song → một tường |
| Đơn vị sai, toạ độ lệch | `$INSUNITS` = 0 hay base point khác nhau | Bắt buộc `fallback_unit`; kiểm bounding box |
| Mất thông tin khi DWG → IFC | Block/thuộc tính không tự thành Pset | Lập bảng ánh xạ thuộc tính; đọc `ATTRIB` của INSERT |
| Phát hiện lỗi muộn | Không thử nghiệm sớm | Chạy thử một tầng (bước 8) |
| Mô hình chỉ ở LOD thấp | Chỉ đủ cho mặt bằng | Chấp nhận cho bản đồ trong nhà; ghi LOD đạt được (xem [lod-mvd-ids](../02-bim/lod-mvd-ids.md)) |

## Liên quan đến pipeline CAD → BIM → GPKG
Bước 4 chưa có trong `src/` (hiện chỉ trích DXF → GPKG và IFC → GPKG). Đề xuất thêm mô-đun `src/cad2bim/ifc_writer.py` dùng lại luồng của [POC](poc-result.md). Khi đó chuỗi CAD → IFC → GPKG chạy trọn trong repo và kiểm chéo được hai đường (DXF → GPKG trực tiếp và DXF → IFC → GPKG).

## Nguồn
- [BIM Corner — DWG to IFC step by step](https://bimcorner.com/migration-of-cad-dwg-models-to-ifc-step-by-step-guide/) — truy cập 2026-11-08 (đã đọc trang)
- [`docs/mapping-design.md`](../../docs/mapping-design.md), [`config/layer_mapping.yaml`](../../config/layer_mapping.yaml) — tài liệu nội bộ của dự án
- Các nguồn khác xem cuối [cad-to-bim-approaches](cad-to-bim-approaches.md)

## Câu hỏi còn mở
- Lỗ mở cửa trong tường (`IfcOpeningElement` + `IfcRelVoidsElement`): chưa thử trong POC.
- Tách hai nét song song thành một tường có độ dày đúng: chưa thử.
- Layer thật của bản vẽ người dùng khác mẫu thế nào: cần file thật.
