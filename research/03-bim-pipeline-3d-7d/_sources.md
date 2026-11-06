# Log nguồn TASK-012 — research/03-bim-pipeline-3d-7d

Cập nhật bởi claude-laptop, 2026-11-06. Thay log vòng 2 của claude-mobile.

| Nguồn | Dùng cho | Trạng thái |
|---|---|---|
| `ifcopenshell 0.9.0.post1` schema bundled (`IFC2X3`, `IFC4`, `IFC4X3_ADD2`) | entity, attribute, OPTIONAL/REQUIRED 4D/5D/6D/7D | ĐÃ DÙNG |
| `ifcopenshell.util.pset.get_template` | Pset/Qto (Warranty, ServiceLife, Manufacturer, Asset, Environmental…) | ĐÃ DÙNG |
| `ifcopenshell.guid`, `uuid` | GUID↔UUID | ĐÃ CHẠY |
| `importlib` (ifcopenshell.util.sequence|cost, api.sequence|cost) | module 4D/5D | ĐÃ KIỂM tồn tại |
| https://ifc43-docs.standards.buildingsmart.org/ | spec IFC | HTTP 403 (chặn bot), không vượt chặn |
| COBie (NIBS), ISO 19650-3, BIMForum, vendor (Navisworks, Synchro, Tally…) | công cụ/chuẩn thương mại | CHƯA ĐỌC |
