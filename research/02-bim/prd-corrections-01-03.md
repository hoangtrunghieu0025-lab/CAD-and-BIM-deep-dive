# Rà PRIMARY_OBJECTIVE.md cho luồng 01 (CAD), 02 (BIM/IFC), 03 (3D–7D)

- **Câu hỏi nghiên cứu**: Những dòng nào trong `PRIMARY_OBJECTIVE.md` thuộc luồng 01–03 cần giữ, sửa hoặc bổ sung theo bằng chứng?
- **Kết luận ngắn**: Không có dòng nào sai nghiêm trọng như bảng OSM/IMDF (luồng 04). Cần sửa/bổ sung nhỏ ở **5 chỗ**: DXF còn có dạng binary (dòng 15); `IfcMapConversion`/`IfcProjectedCRS` **không có ở IFC2X3** và VN-2000 còn có các mã TM-3 (dòng 96); `shapely.polygonize` nên ghi rõ `shapely.ops.polygonize` (dòng 90); `fiona` không cần (dòng 132); hai thuật ngữ cần chú thích (LOD/LOI, định nghĩa 6D/7D). Phần lớn dòng còn lại **đúng nhưng chưa thể xác minh miễn phí** (phần mềm thương mại, tiêu chuẩn trả phí).
- **Độ tin cậy**: cao cho các dòng kiểm bằng schema/chạy thật; "chưa xác minh" được ghi rõ ở từng dòng.
- **Trạng thái xác minh**: ĐÃ RÀ (TASK-012, claude-laptop, 2026-11-06). **Không sửa `PRIMARY_OBJECTIVE.md`** (chưa được chủ dự án cho phép); đây là đề xuất.
- **Vị trí file**: đặt tạm ở `research/02-bim/` vì nằm trong phạm vi ghi của TASK-012; có thể chuyển sang `docs/` khi synthesizer gộp.

Nhãn: **ĐÚNG** · **SỬA** · **BỔ SUNG** · **CHƯA XÁC MINH** (không có nguồn miễn phí đọc được hoặc không thuộc khả năng kiểm bằng thực nghiệm).

## Bảng đối chiếu (theo số dòng của `PRIMARY_OBJECTIVE.md` hiện tại)

| Dòng | Nội dung PRD | Nhãn | Ghi chú / đề xuất | Căn cứ |
|---|---|---|---|---|
| 14 | DWG: nhị phân, của Autodesk, phổ biến nhất | ĐÚNG (nhị phân độc quyền) / CHƯA XÁC MINH ("phổ biến nhất") | Giữ; "phổ biến nhất" là nhận định, không kiểm | `research/01-cad/dxf-dwg-formats.md` |
| 15 | DXF: "Dạng trao đổi (text/ASCII)" | **SỬA nhẹ** | DXF còn có biến thể **binary**; `ezdxf` đọc được (`ezdxf.lldxf.validator.is_binary_dxf_file`, `tagger.binary_tags_loader` tồn tại), nhưng `ezdxf.recover` chỉ hỗ trợ ASCII. Đề xuất: "Dạng trao đổi (thường ASCII, có biến thể binary)" | chạy `ezdxf 1.4.5`; ghi chú 01 |
| 15 | thư viện `ezdxf` | ĐÚNG | Chạy thật: đọc DXF, query, disassemble | `01-cad/parsing-with-ezdxf.md` |
| 16–17 | DGN (MicroStation), SVG/PDF | CHƯA XÁC MINH | Không nằm trong nghiên cứu luồng 01 | — |
| 18 | WCS/UCS, xref, đơn vị, tỉ lệ, model/paper space | ĐÚNG khái niệm, **BỔ SUNG** | DXF lưu toạ độ ở **WCS hoặc OCS, không bao giờ UCS**; entity có extrusion ≠ (0,0,1) cần OCS→WCS; đơn vị ở `$INSUNITS` nhưng nhiều file để 0/sai. Đề xuất thêm "OCS" vào danh sách khái niệm | `01-cad/coordinates-and-units.md` (ezdxf `$INSUNITS`: mẫu của dự án đọc ra `doc.units == 6`) |
| 19 | Hạn chế của CAD | ĐÚNG | Quy ước layer ở Việt Nam: chưa xác minh | `01-cad/layer-naming-conventions.md` |
| 24 | `IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace/IfcWall/IfcDoor` | ĐÚNG, giản lược; **BỔ SUNG** | Đã xác minh trên mẫu: `IfcSpace` gắn tầng bằng `IfcRelAggregates`; `IfcWall`/`IfcDoor` gắn bằng `IfcRelContainedInSpatialStructure` (không phải con của Space). IFC4.3: `IfcBuilding` ⊂ `IfcFacility`. `IfcSite` tuỳ chọn (theo ghi chú 02, nguồn spec qua tìm kiếm — **chưa xác minh trực tiếp**). "ISO 16739" chưa kiểm | schema `ifcopenshell`; `02-bim/ifc-spatial-structure.md` |
| 25–26 | RVT/NWD/NWC/SKP/PLN; COBie, BCF, gbXML, CityGML | CHƯA XÁC MINH | Định dạng/chuẩn ngoài phạm vi kiểm bằng thực nghiệm | — |
| 27 | LOD/LOI, "Level of Development"; IDS; IDM/MVD | **SỬA gợi ý** (LOD) · ĐÚNG (IDS) · CHƯA XÁC MINH (IDM/MVD) | ISO 7817-1 dùng thuật ngữ *Level of Information Need* (LOIN), "LOD" cũng thường hiểu là *Level of Detail/Development* tuỳ nguồn — nên chú thích; ISO trả phí nên **chưa xác minh**. IDS: đã xác minh 6 facet và `ifcVersion` ∈ {IFC2X3, IFC4, IFC4X3_ADD2} từ `ids.xsd` | `02-bim/lod-mvd-ids.md` |
| 28 | IfcOpenShell, BlenderBIM/Bonsai, FreeCAD, xBIM, Speckle, Revit + Dynamo | ĐÚNG (IfcOpenShell) / CHƯA XÁC MINH (còn lại) | IfcOpenShell 0.9.0.post1 chạy được. Bonsai/FreeCAD chưa cài (TASK-013) | `docs/local-env-report.md` |
| 54 | 4D: `IfcTask`, `IfcWorkSchedule` | ĐÚNG, **BỔ SUNG** | Thêm `IfcTaskTime` (IFC4+; IFC2X3 không có) và `IfcRelAssignsToProcess` (RelatingProcess REQUIRED). `Pset_TaskCommon` **không tồn tại** | schema IFC2X3/IFC4/IFC4X3_ADD2 |
| 54 | Navisworks, Synchro, MS Project/Primavera | CHƯA XÁC MINH | Phần mềm thương mại | `03-bim-pipeline-3d-7d/4d-schedule.md` |
| 55 | 5D: `IfcCostItem` | ĐÚNG, **BỔ SUNG** | Thêm `IfcCostSchedule`, `IfcRelAssignsToControl`, `Qto_*BaseQuantities`. IFC2X3 dùng `IfcRelSchedulesCostItems` (không có ở IFC4+) | schema; template Pset |
| 55 | CostX, Revit schedules | CHƯA XÁC MINH | — | — |
| 56 | 6D: gbXML, EnergyPlus, **Insight** | CHƯA XÁC MINH | Không kiểm được; "Insight" (Autodesk) có thể không còn được hỗ trợ — **chưa kiểm tra**. Định nghĩa 6D **không thống nhất** giữa các nguồn (6D = bền vững hay FM): PRD chọn 6D = bền vững, nên ghi rõ "quy ước của dự án" | `03-bim-pipeline-3d-7d/dimensions-overview.md` |
| 57 | 7D: COBie, CAFM/CMMS, Digital Twin | ĐÚNG hướng / CHƯA XÁC MINH chi tiết | `Pset_Warranty`, `Pset_ServiceLife`, `Pset_ManufacturerTypeInformation`, `Pset_Asset` tồn tại (khác biệt IFC4 ↔ 4.3) | template Pset |
| 61 | Khoá GUID = `IfcGloballyUniqueId` | ĐÚNG, **BỔ SUNG** | Thuộc tính là `IfcRoot.GlobalId` (kiểu `IfcGloballyUniqueId`), 22 ký tự; đổi sang UUID bằng `ifcopenshell.guid.expand` + `uuid.UUID(hex=...)` (đã chạy) | `03-bim-pipeline-3d-7d/guid-linking.md` |
| 62–63 | Việc cần làm: hình học vs phi hình học, đưa sang GIS | — | Đã có ghi chú tương ứng; chưa là khẳng định kỹ thuật cần sửa | — |
| 85 | DWG→DXF bằng ODA File Converter / LibreDWG | ĐÚNG, **BỔ SUNG** | LibreDWG: GPL v3+; ODA File Converter: miễn phí nhưng **không mã nguồn mở**, điều khoản chưa xác minh → cân nhắc giấy phép nếu phân phối. Test CI nên dùng DXF (không phụ thuộc converter) | `01-cad/dxf-dwg-formats.md` (README LibreDWG, docs ezdxf `odafc`) |
| 86 | Chuẩn hoá đơn vị (mm/m) | ĐÚNG, **BỔ SUNG** | Đọc `doc.units` (`$INSUNITS`); nếu 0 (unitless) phải lấy từ config. Với IFC dùng `ifcopenshell.util.unit.calculate_unit_scale` cho **mọi giá trị độ dài thô** (đã gặp lỗi này trong chính file mẫu) | `02-bim/ifcopenshell-geometry-extraction.md` |
| 89 | Ví dụ layer `A-WALL`/`A-DOOR`/`A-AREA` | ĐÚNG là ví dụ; CHƯA XÁC MINH khớp NCS/AIA | Quy ước thật khác nhau theo đơn vị thiết kế: mapping nên dùng regex/glob + fallback, không cứng tên | `01-cad/layer-naming-conventions.md` |
| 90 | `shapely.polygonize` | **SỬA nhẹ** | Cả `shapely.polygonize` (trả `GeometryCollection` khi gọi với mảng) và `shapely.ops.polygonize` (generator) tồn tại ở shapely 2.2.0. Nên ghi rõ **`shapely.ops.polygonize`**; đã chạy: 4 LineString khép kín → 1 Polygon | chạy `shapely 2.2.0` |
| 92 | Sinh IFC trung gian bằng `ifcopenshell` | ĐÚNG (khả thi) | Đã làm trong `samples/generate_samples.py` bằng `ifcopenshell.api`. Lưu ý: `unit.assign_unit` mặc định **milimét** | TASK-008 |
| 95 | Duyệt `IfcSpace/IfcWall/IfcDoor/IfcWindow/IfcStair/IfcBuildingStorey`; footprint bằng `ifcopenshell.geom` + `shapely` | ĐÚNG | Tất cả class tồn tại ở IFC2X3, IFC4, IFC4X3_ADD2. Code footprint đã chạy (phòng 4×5 → diện tích 20.0). Lấy tầng của `IfcSpace` bằng `get_aggregate` (không phải `get_container`) | chạy trên `samples/` |
| 96 | Georeference: `IfcMapConversion`/`IfcProjectedCRS`; "VN-2000/UTM 48N–49N" | **SỬA / BỔ SUNG** | (1) Hai entity này **không có ở IFC2X3** → cần fallback (control points / `IfcSite.RefLatitude/RefLongitude`). (2) `XAxisAbscissa/Ordinate` được chuẩn hoá khi tính. (3) VN-2000 UTM 48N = `EPSG:3405`, 49N = `EPSG:3406`, địa lý `EPSG:4756`; ngoài ra còn VN-2000 TM-3 (`EPSG:5896–5899`, `9205–9218`). PRD chỉ nêu UTM; **quy định pháp lý Việt Nam về phép chiếu chưa xác minh** nên không khẳng định mã nào là bắt buộc | schema; `pyproj 3.8.0` (EPSG v12.029); `02-bim/ifc-georeference.md` |
| 132 | Ghi GPKG bằng `geopandas` / `fiona` / `pyogrio` | **SỬA nhẹ** | `fiona` **không cài** trong `.venv` và không cần: `geopandas 1.2.0` dùng `pyogrio`. Đề xuất bỏ `fiona` khỏi danh sách | `requirements.txt`; chạy |
| 147–163 | Cấu trúc repo: `docs/` = "ghi chú nghiên cứu CAD, BIM, 4D–7D" | **SỬA nhẹ** (không nhất quán) | Thực tế: ghi chú nghiên cứu ở `research/NN-*`, `docs/` chỉ synthesizer ghi (xem `CLAUDE.md`). Đề xuất cập nhật sơ đồ cho khớp | `CLAUDE.md`; thư mục repo |
| 166 | Python 3.11+, `ezdxf`, `ifcopenshell`, `shapely`, `pyproj`, `geopandas`, `pyogrio`, GDAL, `pytest`, QGIS 3.x | ĐÚNG | Chạy được: Python 3.12.3, GDAL 3.8.4 (hệ thống), QGIS 3.44.7; `requirements.txt` đã có | TASK-001 |
| 190–196 | URL tham khảo | ĐÚNG phần lớn | HTTP 2026-11-06: `ifcopenshell.org` 200, `register.apple.com` 200, `geopackage.org` 200, `qgis.org` 200; `buildingsmart.org/...` **403** (chặn bot, không phải link hỏng); `ezdxf.readthedocs.io` **429** (rate limit); `wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging` không phản hồi trong 30 giây ở lần thử này (trang `action=raw` cùng wiki đọc được) | `curl` |

## Tóm tắt đề xuất sửa `PRIMARY_OBJECTIVE.md` (luồng 01–03)
1. Dòng 15: DXF "thường ASCII, có biến thể binary".
2. Dòng 90: ghi `shapely.ops.polygonize`.
3. Dòng 96: nêu `IfcMapConversion`/`IfcProjectedCRS` chỉ từ IFC4; thêm fallback cho IFC2X3; thêm các mã VN-2000 (TM-3) hoặc ghi "chọn theo quy định địa phương".
4. Dòng 132: bỏ `fiona`.
5. Dòng 147–150 (sơ đồ repo): đồng bộ `research/` và `docs/` với `CLAUDE.md`.
6. Dòng 27 và 56–57: chú thích LOD/LOIN và rằng định nghĩa 6D/7D là quy ước của dự án.

## Chưa xác minh (giữ nguyên, không đề xuất sửa)
Định dạng độc quyền (RVT, NWD, SKP, PLN, DGN), các chuẩn COBie/BCF/gbXML/CityGML, ISO 16739 và ISO 7817-1, tên layer theo NCS/AIA, và mọi phần mềm thương mại ở dòng 28, 54–57.

## Nguồn
- Schema EXPRESS và template Pset đi kèm `ifcopenshell 0.9.0.post1` (IFC2X3, IFC4, IFC4X3_ADD2) — 2026-11-06
- `shapely 2.2.0`, `pyproj 3.8.0` (CSDL EPSG v12.029), `ezdxf 1.4.5`, `geopandas 1.2.0` chạy thật trong `.venv` — 2026-11-06
- [IDS ids.xsd 1.0.0](https://raw.githubusercontent.com/buildingSMART/IDS/development/Schema/ids.xsd) — 2026-11-06
- Các ghi chú đã verify: `research/01-cad/*`, `research/02-bim/*`, `research/03-bim-pipeline-3d-7d/*` (xem mục "Kết quả xác minh" trong từng file)
- Bảng OSM/IMDF/GPKG tương ứng (luồng 04): `research/04-osm-imdf-tagging/prd-corrections.md`

## Câu hỏi còn mở
- Chủ dự án quyết định có áp dụng 6 đề xuất trên vào `PRIMARY_OBJECTIVE.md` không (laptop không có quyền sửa file đó).
- Quy định pháp lý về hệ toạ độ VN-2000 theo tỉnh/thành; trạng thái hiện tại của Autodesk Insight.
