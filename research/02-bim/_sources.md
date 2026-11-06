# Log nguồn TASK-012 — research/02-bim

Cập nhật bởi claude-laptop, 2026-11-06. Thay log vòng 2 của claude-mobile (khi đó DNS bị chặn).

| Nguồn | Dùng cho | Trạng thái |
|---|---|---|
| `ifcopenshell 0.9.0.post1` — schema EXPRESS bundled (`ifcopenshell_wrapper.schema_by_name`: `IFC2X3`, `IFC4`, `IFC4X3_ADD2`) | supertype, attribute, OPTIONAL/REQUIRED, enum | ĐÃ DÙNG (thay cho trang spec) |
| `ifcopenshell.util.pset.get_template("IFC4"/"IFC4X3")` | danh sách property của Pset/Qto | ĐÃ DÙNG |
| `ifcopenshell.api.georeference`, `ifcopenshell.util.geolocation`, `util.element`, `util.placement`, `util.shape`, `util.representation`, `util.unit`, `geom` | chữ ký + chạy thử | ĐÃ CHẠY (mẫu `samples/sample-building.ifc`) |
| `pyproj 3.8.0` CSDL EPSG v12.029 | mã VN-2000 | ĐÃ DÙNG |
| https://ifc43-docs.standards.buildingsmart.org/ , https://standards.buildingsmart.org/ | spec IFC | HTTP 403 (chặn bot) — KHÔNG đọc được, không vượt chặn |
| https://docs.ifcopenshell.org/ | docs IfcOpenShell | HTTP 200, chưa dùng làm nguồn |
| https://raw.githubusercontent.com/buildingSMART/IDS/development/Schema/ids.xsd | IDS 1.0.0 | ĐÃ ĐỌC |
