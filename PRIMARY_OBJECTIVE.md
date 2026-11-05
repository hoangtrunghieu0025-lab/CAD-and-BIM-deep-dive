# PRIMARY OBJECTIVE

> Mục tiêu chính của dự án **CAD-and-BIM-deep-dive**: hiểu CAD/BIM, nắm được pipeline dữ liệu BIM (3D → 4D → … → 7D) và xây dựng luồng chuyển dữ liệu **CAD → BIM → GeoPackage (.gpkg)** chuẩn hoá theo **OSM tagging** và **IMDF**, import được vào **QGIS**.

---

## 1. Tìm hiểu CAD và BIM

### 1.1. CAD (Computer-Aided Design)
- **Bản chất**: tập hợp các đối tượng hình học (line, polyline, arc, circle, hatch, text, block/insert) gắn với **layer**; chủ yếu là bản vẽ 2D, thiếu ngữ nghĩa (một đường thẳng không "biết" nó là tường hay cột).
- **Định dạng phổ biến**:
  | Định dạng | Ghi chú |
  |---|---|
  | DWG | Nhị phân, của Autodesk, phổ biến nhất |
  | DXF | Dạng trao đổi (text/ASCII), dễ parse – thư viện `ezdxf` |
  | DGN | MicroStation (Bentley) |
  | SVG/PDF | Bản vẽ vector xuất ra, mất nhiều thông tin |
- **Khái niệm cần nắm**: layer, block/attribute, xref, đơn vị bản vẽ, hệ toạ độ cục bộ (WCS/UCS), tỉ lệ, model space vs paper space.
- **Hạn chế**: không có quan hệ giữa đối tượng, quy ước đặt tên layer tuỳ từng đơn vị thiết kế, khó tái sử dụng dữ liệu.

### 1.2. BIM (Building Information Modeling)
- **Bản chất**: mô hình thông tin toà nhà – mỗi đối tượng (tường, sàn, cửa, thiết bị…) là một **thực thể có ngữ nghĩa**, có hình học 3D, thuộc tính, quan hệ và vòng đời.
- **Định dạng / chuẩn**:
  - **IFC** (ISO 16739, buildingSMART) – chuẩn mở, trung lập: `IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcSpace / IfcWall / IfcDoor …`
  - **RVT** (Revit), **NWD/NWC** (Navisworks), **SKP**, **ArchiCAD PLN** – định dạng độc quyền.
  - **COBie**, **BCF**, **gbXML**, **CityGML** – các chuẩn bổ trợ (bàn giao vận hành, trao đổi issue, mô phỏng năng lượng, GIS 3D).
- **Khái niệm cần nắm**: Property Set (Pset), Quantity Set, Classification (Uniclass, OmniClass, UniFormat), LOD/LOI, Level of Development, IDS (Information Delivery Specification), IDM/MVD.
- **Công cụ**: IfcOpenShell, BlenderBIM/Bonsai, FreeCAD, xBIM, Speckle, Revit + Dynamo.

### 1.3. So sánh CAD vs BIM

| Tiêu chí | CAD | BIM |
|---|---|---|
| Đơn vị dữ liệu | Hình học (đường, mặt) | Đối tượng có ngữ nghĩa |
| Thuộc tính | Ít / tuỳ layer | Phong phú (Pset, vật liệu, chi phí…) |
| Quan hệ | Không có | Có (chứa, nối, bao quanh, thuộc về) |
| Chiều | Chủ yếu 2D | 3D + thời gian + chi phí + vận hành |
| Trao đổi | DWG/DXF | IFC |

---

## 2. Pipeline dữ liệu BIM: 3D → 4D → 5D → 6D → 7D

```
Thiết kế (CAD/2D) ─► Mô hình 3D BIM ─► 4D (thời gian) ─► 5D (chi phí) ─► 6D (bền vững/năng lượng) ─► 7D (vận hành & bảo trì / FM)
                          │                                                                                │
                          └──────────────── IFC / COBie / Digital Twin / GIS ◄─────────────────────────────┘
```

| Chiều | Nội dung | Dữ liệu thêm vào | Ví dụ công cụ / chuẩn |
|---|---|---|---|
| **2D** | Bản vẽ kỹ thuật | Hình học phẳng, layer | AutoCAD, DWG/DXF |
| **3D** | Mô hình hình học + thuộc tính | Hình học 3D, vật liệu, Pset, phân loại | Revit, ArchiCAD, IFC |
| **4D** | Tiến độ thi công | Gắn task/schedule vào từng cấu kiện (`IfcTask`, `IfcWorkSchedule`) | Navisworks, Synchro, MS Project/Primavera |
| **5D** | Chi phí | Khối lượng (Quantity Take-off), đơn giá, dự toán | CostX, Revit schedules, `IfcCostItem` |
| **6D** | Bền vững / năng lượng | Hiệu suất năng lượng, vật liệu, carbon | gbXML, EnergyPlus, Insight |
| **7D** | Vận hành & bảo trì (FM / Asset Mgmt) | Thông tin tài sản, bảo hành, lịch bảo trì, sensor/IoT | COBie, CAFM/CMMS, Digital Twin |

**Việc cần làm trong phần này**
- [ ] Mô tả data model ở mỗi bước (input → xử lý → output) và dữ liệu nào được **bổ sung** ở từng chiều.
- [ ] Xác định khoá liên kết (GUID – `IfcGloballyUniqueId`) để nối mô hình 3D với tiến độ (4D), chi phí (5D), tài sản (7D).
- [ ] Phân biệt dữ liệu **hình học** và **thông tin phi hình học** và cách lưu (IFC, DB quan hệ, graph).
- [ ] Xác định phần nào của pipeline có thể đưa sang **GIS** (indoor mapping, quản lý tài sản, digital twin).

---

## 3. Luồng extract dữ liệu: CAD → BIM → GeoPackage (QGIS)

### 3.1. Mục tiêu
Xây dựng một pipeline tự động, lặp lại được, nhận **bản vẽ CAD** (DWG/DXF) hoặc **mô hình BIM** (IFC) và xuất ra file **`.gpkg`** chuẩn, trong đó dữ liệu đã được **chuẩn hoá tag theo OSM (Simple Indoor Tagging)** và **cấu trúc theo IMDF (Indoor Mapping Data Format)**, mở trực tiếp được trong **QGIS**.

### 3.2. Sơ đồ luồng

```
┌─────────────┐   ┌────────────────┐   ┌───────────────────┐   ┌──────────────────────┐   ┌──────────────┐   ┌─────────┐
│ 1. Ingest   │──►│ 2. CAD → BIM   │──►│ 3. Extract hình   │──►│ 4. Chuẩn hoá         │──►│ 5. Ghi GPKG  │──►│ 6. QGIS │
│ DWG/DXF/IFC │   │ (nhận diện đối │   │ học + thuộc tính  │   │ OSM tagging + IMDF   │   │ + validate   │   │ import  │
│             │   │ tượng, gán lớp)│   │ + georeference    │   │ mapping              │   │              │   │ & kiểm  │
└─────────────┘   └────────────────┘   └───────────────────┘   └──────────────────────┘   └──────────────┘   └─────────┘
```

### 3.3. Chi tiết từng bước

**Bước 1 – Ingest & tiền xử lý**
- Đọc DXF bằng `ezdxf`; DWG chuyển sang DXF bằng ODA File Converter / LibreDWG; IFC đọc bằng `ifcopenshell`.
- Chuẩn hoá đơn vị (mm/m), loại bỏ layer rác, làm sạch hình học (đóng polyline, snap, loại điểm trùng).

**Bước 2 – CAD → BIM (làm giàu ngữ nghĩa)**
- Lập **bảng ánh xạ layer → loại đối tượng** (ví dụ `A-WALL` → `IfcWall`, `A-DOOR` → `IfcDoor`, `A-AREA` → `IfcSpace`) dạng file cấu hình YAML/JSON để tuỳ biến theo từng dự án.
- Dựng polygon từ đường biên (`shapely.polygonize`), nhận diện phòng/không gian, gán tầng (`IfcBuildingStorey`) theo file/ layer/ cao độ.
- Gán thuộc tính từ block attribute / text (tên phòng, số phòng, diện tích).
- (Tuỳ chọn) Sinh file IFC trung gian bằng `ifcopenshell` để làm "nguồn sự thật" BIM.

**Bước 3 – Extract hình học & thuộc tính**
- Với IFC: duyệt `IfcSpace`, `IfcWall`, `IfcDoor`, `IfcWindow`, `IfcStair`, `IfcBuildingStorey`…; lấy footprint 2D mỗi tầng (cắt mặt phẳng ngang / `ifcopenshell.geom` + `shapely`).
- **Georeference**: xác định CRS đích (ví dụ EPSG:4326 hoặc CRS địa phương như VN-2000/UTM 48N–49N), dùng `IfcMapConversion` / `IfcProjectedCRS` hoặc điểm điều khiển (control points) để biến đổi toạ độ cục bộ → toạ độ thực.

**Bước 4 – Chuẩn hoá: OSM tagging & IMDF**

*4a. OSM Simple Indoor Tagging* – mỗi đối tượng được gán tag chuẩn OSM, ví dụ:

| Đối tượng | Tag OSM |
|---|---|
| Tầng | `level=*`, `level:ref=*`, `repeat_on=*` |
| Phòng / không gian | `indoor=room`, `ref=*`, `name=*` |
| Hành lang | `indoor=corridor` |
| Tường | `indoor=wall` |
| Cửa | `door=*`, `entrance=*` |
| Cầu thang / thang máy | `highway=steps`, `highway=elevator` |
| Khu vực | `indoor=area` |
| Toà nhà | `building=*`, `building:levels=*` |

*4b. IMDF* – ánh xạ vào các feature type chuẩn (mỗi loại là một layer/ file GeoJSON, ở đây là một bảng trong GPKG):

| IMDF feature | Nguồn từ BIM/CAD | Ghi chú |
|---|---|---|
| `venue` | Khu/ công trình tổng | Polygon bao ngoài |
| `building` | `IfcBuilding` | |
| `footprint` | Đường bao toà nhà | |
| `level` | `IfcBuildingStorey` | `ordinal`, `short_name`, `outdoor` |
| `unit` | `IfcSpace` | `category` (room, walkway, restroom, elevator…) |
| `opening` | `IfcDoor` | `category` (door, …) |
| `fixture` | Tường, vách, thiết bị cố định | |
| `detail` | Đường nét chi tiết | |
| `amenity`, `occupant`, `anchor`, `address` | Thông tin bổ sung | Tuỳ dữ liệu có sẵn |

- Mỗi feature có `id` (UUID – nên tái sử dụng `IfcGloballyUniqueId`/ sinh UUID ổn định), `feature_type`, `geometry`, `properties`.
- Xây quan hệ qua khoá ngoại: `unit.level_id → level.id`, `level.building_ids → building.id`…
- Lập **bảng mapping category** (IFC class / CAD layer ⇄ OSM tag ⇄ IMDF category) trong một file cấu hình duy nhất để dễ bảo trì.

**Bước 5 – Xuất GeoPackage chuẩn**
- Dùng `geopandas` / `fiona` / `pyogrio` ghi `.gpkg` với **mỗi IMDF feature type = một layer** (`venue`, `building`, `level`, `unit`, `opening`, `fixture`, …).
- Bắt buộc:
  - Gán **CRS** rõ ràng (ví dụ EPSG:4326) cho mọi layer.
  - Hình học hợp lệ (`make_valid`), đúng kiểu (Polygon/ LineString/ Point), không rỗng.
  - Cột thuộc tính có kiểu xác định; các tag OSM giữ ở các cột riêng hoặc cột `tags` (JSON).
  - Có spatial index (GPKG tự tạo RTree) và bảng `gpkg_contents`/ `gpkg_geometry_columns` hợp lệ.
- Validate: `ogrinfo -al -so`, kiểm tra bằng `pytest`, IMDF validator (nếu xuất thêm GeoJSON), kiểm tra topology (unit không chồng lấn, nằm trong level).

**Bước 6 – Import & kiểm tra trong QGIS**
- Mở `.gpkg` bằng *Layer → Add Layer → Add Vector Layer*, xác nhận tất cả layer load đúng CRS, đúng vị trí trên bản đồ nền.
- Đi kèm file style `.qml` (hoặc style lưu trong GPKG – `layer_styles`) để hiển thị theo `category` và lọc theo `level`.
- (Tuỳ chọn) dùng QGIS Temporal/ Variable-based filter để chuyển giữa các tầng.

### 3.4. Đề xuất cấu trúc repo

```
CAD-and-BIM-deep-dive/
├── PRIMARY_OBJECTIVE.md        # file này
├── docs/                       # ghi chú nghiên cứu CAD, BIM, 4D–7D
├── config/
│   ├── layer_mapping.yaml      # CAD layer  → loại đối tượng
│   └── tag_mapping.yaml        # IFC/CAD    → OSM tags → IMDF category
├── src/
│   ├── ingest/                 # đọc DWG/DXF/IFC
│   ├── cad2bim/                # nhận diện đối tượng, dựng space
│   ├── extract/                # hình học, thuộc tính, georeference
│   ├── normalize/              # OSM tagging + IMDF mapping
│   └── export/                 # ghi GPKG + validate
├── samples/                    # file CAD/IFC mẫu nhỏ
├── tests/
└── out/                        # .gpkg đầu ra (gitignore)
```

### 3.5. Công nghệ đề xuất
Python 3.11+, `ezdxf`, `ifcopenshell`, `shapely`, `pyproj`, `geopandas`, `pyogrio`, GDAL/OGR, `pytest`, QGIS 3.x.

---

## 4. Kết quả cần đạt (Definition of Done)

- [ ] Tài liệu tóm tắt **CAD vs BIM**, các định dạng và khái niệm chính (`docs/`).
- [ ] Tài liệu mô tả **pipeline BIM 3D → 4D → 5D → 6D → 7D** với dữ liệu ở từng bước.
- [ ] Bảng mapping **CAD layer / IFC class → OSM tag → IMDF category** dạng file cấu hình.
- [ ] Script/CLI chạy được: `input (DXF/IFC) → output .gpkg`.
- [ ] File `.gpkg` đầu ra: CRS đúng, hình học hợp lệ, các layer theo IMDF, tag OSM chuẩn.
- [ ] Import vào **QGIS** thành công, hiển thị đúng vị trí/ tầng/ phân loại (kèm ảnh chụp màn hình trong `docs/`).
- [ ] Test tự động cho các bước chính và một bộ dữ liệu mẫu.

## 5. Lộ trình gợi ý

1. **Nghiên cứu**: CAD, BIM/IFC, 4D–7D, OSM Simple Indoor Tagging, IMDF.
2. **Thiết kế mapping**: layer/IFC class → OSM tag → IMDF category.
3. **Prototype**: DXF/IFC mẫu nhỏ → GPKG một tầng.
4. **Mở rộng**: nhiều tầng, georeference, quan hệ IMDF đầy đủ, validate.
5. **Hoàn thiện**: style QGIS, test, tài liệu, CLI.

## 6. Tham khảo

- IFC / buildingSMART: https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/
- IfcOpenShell: https://ifcopenshell.org/
- ezdxf: https://ezdxf.readthedocs.io/
- OSM Simple Indoor Tagging: https://wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging
- IMDF (Apple): https://register.apple.com/resources/imdf/
- GeoPackage (OGC): https://www.geopackage.org/
- QGIS: https://qgis.org/
