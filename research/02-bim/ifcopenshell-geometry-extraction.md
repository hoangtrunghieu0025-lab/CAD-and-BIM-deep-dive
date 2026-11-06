# Trích hình học bằng IfcOpenShell

- **Câu hỏi nghiên cứu**: Dùng `ifcopenshell` thế nào để lấy hình học (và thuộc tính) từ IFC theo tầng, chuyển thành polygon cho GeoPackage?
- **Kết luận ngắn**: `ifcopenshell.geom.create_shape` (từng phần tử) hoặc `ifcopenshell.geom.iterator` (đa nhân) trả mesh tam giác (`verts`, `faces`, `edges`); bật `USE_WORLD_COORDS` để có toạ độ thế giới. Footprint 2D = chiếu/cắt mesh bằng `shapely`.
- **Độ tin cậy**: trung bình — code mẫu lấy từ tài liệu v0.7.0; API mới hơn (v0.8) có thể đổi cách tạo `settings` (chưa xác minh).

## Chi tiết

### Đọc file và duyệt cấu trúc
```python
import ifcopenshell
f = ifcopenshell.open("model.ifc")
storeys = f.by_type("IfcBuildingStorey")
spaces  = f.by_type("IfcSpace")
doors   = f.by_type("IfcDoor")
```
- `ifcopenshell.util.element.get_psets(el)` / `get_pset(el, name, prop)` để lấy Pset (một element mỗi lần). [S2]
- `ifcopenshell.util.placement.get_local_placement(placement)` trả ma trận placement; gốc placement không đảm bảo là tâm hình học. [S3]

### Tạo hình học (nguồn: tài liệu v0.7.0) [S1]
```python
import ifcopenshell.geom
settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)   # áp placement vào toạ độ đỉnh
shape = ifcopenshell.geom.create_shape(settings, element)
verts = shape.geometry.verts   # phẳng [x1,y1,z1,x2,...]
faces = shape.geometry.faces   # phẳng, luôn là tam giác
edges = shape.geometry.edges
```
Duyệt toàn file đa nhân:
```python
import multiprocessing
it = ifcopenshell.geom.iterator(settings, f, multiprocessing.cpu_count(), include=spaces)
if it.initialize():
    while True:
        shape = it.get(); el = f.by_id(shape.id)
        # xử lý ...
        if not it.next(): break
```
- Nếu không bật `USE_WORLD_COORDS`, đỉnh nằm trong toạ độ cục bộ và cần nhân `shape.transformation.matrix`. [S1]
- IfcOpenShell tính nội bộ bằng mét; với giá trị đọc thủ công thì nhân `ifcopenshell.util.unit.calculate_unit_scale(f)`. [S1][S4]
- Có thể chọn một representation cụ thể (vd `FootPrint`) rồi truyền vào `create_shape` cùng settings (mô tả trong docs; ví dụ code chưa xác minh). [S4]
- `ifcopenshell.util.shape` có các hàm tiện ích (`get_vertices/get_edges/get_faces`, và `get_footprint_area` theo một câu trả lời diễn đàn; chữ ký chưa xác minh). [S1][S3]

### Công thức footprint 2D theo tầng (đề xuất của dự án)
```python
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

def footprint(shape):
    v = np.array(shape.geometry.verts).reshape(-1, 3)
    t = np.array(shape.geometry.faces).reshape(-1, 3)
    polys = [Polygon(v[i][:, :2]) for i in t if Polygon(v[i][:, :2]).area > 1e-9]
    return unary_union(polys)
```
- Mỗi `IfcSpace` → `footprint` (union các tam giác chiếu xuống XY; mặt đứng suy biến bị lọc theo diện tích). Nhóm theo storey (xem `ifc-spatial-structure.md`).
- Với `IfcDoor`: bbox 2D hoặc minimum_rotated_rectangle của footprint → trục dài → LineString (IMDF `opening`).
- Sau cùng: `make_valid`, áp `IfcMapConversion` (xem `ifc-georeference.md`), ghi bằng `geopandas` (EPSG đích).
- Phương án khác: cắt mesh bằng mặt phẳng ngang (trimesh/shapely) tại cao độ tầng + offset; hoặc `IfcConvert` (CLI) xuất SVG mặt bằng — có tuỳ chọn `--plan` trong commit nhưng ý nghĩa chưa xác minh. [S4]

### Lưu ý
- Hiệu năng: dùng iterator + `include=` để chỉ xử lý space/door.
- Chất lượng: một số IfcSpace không có `Body`; bỏ qua và ghi cảnh báo.
- Đơn vị mm trong file (Revit thường mét/mm) → luôn kiểm tra qua `calculate_unit_scale`.

## Liên quan đến pipeline CAD → BIM → GPKG
Đây là bước 3 "Extract hình học + thuộc tính": kết hợp (a) cây storey/space/door, (b) Pset, (c) footprint, (d) transform địa lý. Khi sinh IFC từ CAD (bước 2), dùng `ifcopenshell.api` để tạo thực thể (chưa nghiên cứu chi tiết trong ghi chú này).

## Nguồn
- [S1] IfcOpenShell geometry_processing.rst v0.7.0 — https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.7.0/src/ifcopenshell-python/docs/ifcopenshell-python/geometry_processing.rst?plain=true — truy cập 2026-11-06
- [S2] util/element.py — https://github.com/IfcOpenShell/IfcOpenShell/blob/2a22acfdc936bc9ed6d2ff0ec36e76287da08d56/src/ifcopenshell-python/ifcopenshell/util/element.py — truy cập 2026-11-06
- [S3] IfcOpenShell util index — https://docs.ifcopenshell.org/autoapi/ifcopenshell/util/index.html ; OSArch https://community.osarch.org/discussion/comment/21649/ — truy cập 2026-11-06
- [S4] IteratorSettings — https://ifcopenshell.github.io/docs/rst_files/class_ifc_geom_1_1_iterator_settings.html — truy cập 2026-11-06

## Câu hỏi còn mở
- API settings trong bản IfcOpenShell mới nhất (0.8.x) — có còn `settings.set(settings.USE_WORLD_COORDS, ...)` hay dùng `ifcopenshell.geom.settings(**{"use-world-coords": True})`?
- Chữ ký `get_footprint_area`; cách chọn representation `FootPrint` bằng `ifcopenshell.util.representation`.
- Cần chạy thử trên file mẫu để kiểm chứng đoạn code trên (chưa chạy; không có Bash).
