# Kết quả POC: DXF (layer `A-WALL`) → IFC4

- **Câu hỏi nghiên cứu**: Một script ngắn có dựng được `IfcWall` từ layer `A-WALL` của mẫu DXF không?
- **Kết luận ngắn**: Có. 16 đoạn tường (12 LINE + 4 cạnh của 1 LWPOLYLINE kín) → 16 `IfcWall` trong `Level 1`, mỗi tường sinh ra được hình học (hộp 8 đỉnh).
- **Độ tin cậy**: cao cho phạm vi đã thử (một mẫu, chỉ tường); chưa thử cửa, phòng, bản vẽ thật.

## Chi tiết
- Script: [`poc/dxf_walls_to_ifc.py`](poc/dxf_walls_to_ifc.py).
- Lệnh đã chạy (môi trường `.venv`, `ifcopenshell 0.9.0.post1`, `ezdxf 1.4.5`):
  `python -I research/06-cad-to-bim/poc/dxf_walls_to_ifc.py samples/sample-floor-1.dxf <out.ifc> 3.0 0.2`
- Kiểm tra: mở lại IFC → `len(by_type("IfcWall")) == 16`; tầng `Level 1`; `ifcopenshell.geom.create_shape` trên tường đầu tiên trả 8 đỉnh.
- File IFC đầu ra đặt ngoài repo (thư mục tạm của phiên), chưa kiểm bằng Bonsai/FreeCAD.
- Giả định: đơn vị DXF là mét (mẫu có `doc.units == 6`); cao 3,0 m và dày 0,2 m là tham số nhập tay.
- Giới hạn: tường nối chưa xử lý góc (mỗi đoạn là một hộp riêng), chưa nối hai nét song song.

## Liên quan đến pipeline CAD → BIM → GPKG
Mở rộng cho `A-AREA` → `IfcSpace` và `A-DOOR` → `IfcDoor` rồi đưa vào `src/cad2bim` là việc POC tiếp theo (đề xuất giao claude-laptop, vì cần mở kết quả bằng Bonsai/FreeCAD).

## Nguồn
- Chạy trực tiếp trên môi trường của dự án, 2026-11-08. Tham khảo [IfcOpenShell docs — create_2pt_wall](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/geometry/create_2pt_wall/index.html) — truy cập 2026-11-08.

## Câu hỏi còn mở
- Xem [cad-to-bim-workflow-and-risks](cad-to-bim-workflow-and-risks.md), mục "Câu hỏi còn mở".
