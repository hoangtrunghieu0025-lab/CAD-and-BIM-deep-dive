# Spec thiết kế: pipeline CAD / BIM → GeoPackage (OSM + IMDF) → gói IMDF

> Đặc tả để claude-laptop cài đặt (TASK-010). Viết bởi claude-mobile (TASK-009). Mỗi quy tắc dẫn về research; chỗ chưa chốt nằm ở mục 11.
> Tài liệu liên quan: [`PRIMARY_OBJECTIVE.md`](../PRIMARY_OBJECTIVE.md) · [`mapping-design.md`](mapping-design.md) · [`config/layer_mapping.yaml`](../config/layer_mapping.yaml) · [`config/tag_mapping.yaml`](../config/tag_mapping.yaml)

## 1. Mục tiêu và phạm vi

| | |
|---|---|
| Vào | DXF (mỗi file một tầng) và/hoặc IFC (IFC2X3 / IFC4 / IFC4X3); DWG phải đổi sang DXF trước (ngoài phạm vi code) |
| Ra | 1. `<tên>.gpkg` (mỗi feature type IMDF một bảng, có cột tag OSM) 2. `<tên>.imdf.zip` (gói IMDF, bước tuỳ chọn) |
| Kiểm | mở được trong QGIS (TASK-011), qua bộ kiểm ở mục 9 |
| Ngoài phạm vi | 3D, 4D–7D, `amenity`/`occupant`/`kiosk`/`section`/`geofence`/`relationship` (xuất rỗng hoặc bỏ), nhận dạng đối tượng tự động từ nét vẽ không có layer |

## 2. Kiến trúc

```
inputs ─► ingest ─► cad2bim ─► extract ─► normalize ─► export_gpkg ─► validate ─► [export_imdf]
          đọc file   layer→loại   hình học 2D   OSM + IMDF     ghi .gpkg     kiểm tra     .imdf.zip
                     đối tượng    + georef      theo config
```

Cấu trúc thư mục theo `PRIMARY_OBJECTIVE.md` mục 3.4:

| Module (`src/`) | Việc | Hàm chính (chữ ký gợi ý) |
|---|---|---|
| `ingest/` | Đọc DXF/IFC, chuẩn hoá đơn vị | `load_dxf(path) -> DxfSource` · `load_ifc(path) -> IfcSource` · `to_metres(value, unit)` |
| `cad2bim/` | Áp `layer_mapping.yaml`, dựng polygon phòng, gán nhãn, gán tầng | `classify_entities(src, cfg) -> list[Obj]` · `build_spaces(objs) -> list[Space]` · `attach_labels(spaces, labels)` |
| `extract/` | Footprint 2D, thuộc tính, georeference | `space_footprint(ifc_space) -> Polygon` · `door_line(ifc_door, ...) -> LineString` · `georeference(objs, georef_cfg) -> Transformer` |
| `normalize/` | Áp `tag_mapping.yaml` → tag OSM + feature IMDF, sinh `id`, khoá ngoại | `to_features(objs, cfg) -> dict[str, GeoDataFrame/DataFrame]` |
| `export/` | Ghi GPKG, kiểm tra, xuất gói IMDF | `write_gpkg(features, path)` · `validate_gpkg(path) -> Report` · `export_imdf(gpkg, zip_path)` |
| `cli.py` | Giao diện dòng lệnh | xem mục 3 |

**Mô hình trung gian** (dataclass hoặc dict, không phụ thuộc định dạng nguồn): `Obj{id, type, source_kind, source_ref (IfcGloballyUniqueId hoặc "file|layer|handle"), storey_key, geometry (shapely, toạ độ mét cục bộ), props{}}`. Mọi bước sau `ingest` chỉ làm việc với `Obj`.

## 3. Giao diện dòng lệnh

```bash
python -m src.cli build  --project project.yaml --out out/building.gpkg [--allow-unreferenced]
python -m src.cli check  out/building.gpkg
python -m src.cli imdf   out/building.gpkg --out out/building.imdf.zip
```

`project.yaml` (cấu hình mỗi dự án):

```yaml
name: sample-building
mapping: {layers: config/layer_mapping.yaml, tags: config/tag_mapping.yaml}
inputs:
  - {kind: dxf, file: samples/sample-floor-1.dxf, storey: {name: "1", long_name: "Tầng 1", elevation_m: 0.0}}
  - {kind: dxf, file: samples/sample-floor-2.dxf, storey: {name: "2", long_name: "Tầng 2", elevation_m: 3.0}}
  # hoặc: - {kind: ifc, file: samples/sample-building.ifc}   (tầng lấy từ IfcBuildingStorey)
georeference:            # mục 6; bắt buộc trừ khi IFC4+ có IfcMapConversion hoặc dùng --allow-unreferenced
  crs: "EPSG:3405"       # CRS của toạ độ cục bộ sau khi biến đổi (ví dụ VN-2000 / UTM 48N)
  origin: [E0, N0]       # toạ độ (mét) của gốc cục bộ (0,0)
  rotation_deg: 0.0      # góc quay mặt bằng so với trục Đông
  scale: 1.0
venue: {name: "...", category: null, buffer_m: 1.0}      # category: chưa chọn (mục 11)
address: {address: "...", locality: "...", country: "VN"}
```

Mã thoát: `0` ổn · `1` lỗi dữ liệu (kèm báo cáo) · `2` lỗi cấu hình. `build` luôn ghi `out/unmatched_layers.csv` và `out/build_report.json` (số đối tượng theo loại, cảnh báo).

## 4. Các bước chi tiết

### 4.1 `ingest`
| | DXF | IFC |
|---|---|---|
| Thư viện | `ezdxf.readfile` (thất bại → `ezdxf.recover.readfile`; recover chỉ hỗ trợ ASCII) | `ifcopenshell.open` |
| Đơn vị | `doc.units` (`$INSUNITS`); `0` hoặc enum không hỗ trợ → `units.fallback_unit` từ config, ghi cảnh báo | `ifcopenshell.util.unit.calculate_unit_scale(f)` cho **mọi** giá trị độ dài thô |
| Kết quả | entity theo layer + block | `IfcBuildingStorey`, `IfcSpace`, `IfcDoor`, `IfcWall`, … |
Ref: [parsing-with-ezdxf](../research/01-cad/parsing-with-ezdxf.md), [coordinates-and-units](../research/01-cad/coordinates-and-units.md), [ifcopenshell-geometry-extraction](../research/02-bim/ifcopenshell-geometry-extraction.md).

**Lỗi/cảnh báo**: file không đọc được (mã 1), `$INSUNITS=0` (cảnh báo + fallback), OCS có extrusion ≠ (0,0,1): đổi sang WCS bằng `OCS.to_wcs` / `ezdxf.upright` trước khi dùng (không dùng cho TEXT/MTEXT/DIMENSION).

### 4.2 `cad2bim` (chỉ với DXF; IFC bỏ qua bước này)
1. Chuẩn hoá tên layer rồi duyệt `rules` theo thứ tự, khớp đầu tiên thắng ([layer_mapping.yaml](../config/layer_mapping.yaml)); không khớp → `unmatched_layers.csv`.
2. `space`: polyline kín → `Polygon`; hở → thử `shapely.ops.polygonize` từ các LINE cùng layer; vẫn không khép → cảnh báo, bỏ đối tượng.
3. `space_label`: gán text vào polygon phòng chứa điểm chèn (`shapely.contains`); text nằm ngoài mọi phòng → cảnh báo.
4. `door`: INSERT block `DOOR` → điểm chèn + góc quay + thuộc tính từ ATTRIB gắn vào INSERT (giá trị nằm ở ATTRIB, không ở ATTDEF). Đoạn đóng của cửa dựng ở bước 4.4.
5. Tầng: lấy từ `project.yaml` (`storey`), không suy từ nét vẽ.
Ref: [layers-blocks-xref](../research/01-cad/layers-blocks-xref.md), [layer-naming-conventions](../research/01-cad/layer-naming-conventions.md).

### 4.3 `extract` — IFC
| Việc | Cách làm (đã chạy thật trên `samples/`) |
|---|---|
| Tầng của `IfcSpace` | `ifcopenshell.util.element.get_aggregate` (**không** `get_container`: trả `None` khi space được aggregate) |
| Tầng của `IfcDoor`, `IfcWall` | `get_container` (qua `IfcRelContainedInSpatialStructure`) |
| Footprint phòng | ưu tiên representation `FootPrint`; không có → `ifcopenshell.geom` với `USE_WORLD_COORDS`, chiếu `Body` xuống XY, `shapely.unary_union` → `Polygon` (phòng 4×5 m → diện tích 20,0) |
| Cửa → `LineString` | đoạn thẳng dài bằng bề rộng cửa, đặt tại vị trí/hướng cửa; bề rộng = `OverallWidth` → bề rộng opening → `width_fallback_m` |
| Thuộc tính | `get_psets` (ví dụ `Pset_DoorCommon.IsExternal`, `FireExit`; `Pset_SpaceCommon.Reference`) |
Ref: [ifc-spatial-structure](../research/02-bim/ifc-spatial-structure.md), [property-sets-and-classification](../research/02-bim/property-sets-and-classification.md).

### 4.4 `normalize`
- Áp `tag_mapping.yaml`: với mỗi `Obj`, tìm `object_types.<type>`, duyệt `rules` (khớp đầu tiên thắng), sinh **một dòng** gồm thuộc tính IMDF và cột tag OSM.
- `id` = `uuid5(namespace_dự_án, source_ref)`, ổn định giữa các lần chạy.
- Khoá ngoại: `unit.level_id`, `opening.level_id`, `level.building_ids`, `footprint.building_ids`.
- `level`: `storey_index` theo thứ tự cao độ (mặt đất = 0), `ordinal` map riêng.
- `venue`: polygon bao `footprint` + `buffer_m`; `address`, `manifest` từ `project.yaml`.
- Bảng nào cần geometry null (`building`, `address`) → DataFrame thường.
Ref: [osm-simple-indoor-tagging](../research/04-osm-imdf-tagging/osm-simple-indoor-tagging.md), [imdf-feature-types](../research/04-osm-imdf-tagging/imdf-feature-types.md).

### 4.5 `export_gpkg`
- Ghi bằng `pyogrio.write_dataframe` (GeoDataFrame có geometry; **DataFrame thường** cho bảng không geometry — không dùng GeoDataFrame có `geometry=[None]`, vì sẽ thành bảng `features`).
- Ép kiểu geometry về kiểu khai báo của bảng sau `make_valid` (có thể sinh `GeometryCollection`/`Multi*`).
- Mỗi bảng: `fid` (PK tự sinh) + `id TEXT UNIQUE` (UUID IMDF) + `feature_type`.
- Mảng/object (`building_ids`, `name`, `accessibility`…) lưu JSON text bằng `json.dumps(..., ensure_ascii=False)`.
- Spatial index: mặc định bật (GDAL); RTree là extension, không phải bắt buộc của spec.
Ref: [geopackage-requirements](../research/04-osm-imdf-tagging/geopackage-requirements.md).

## 5. Schema GPKG

CRS mọi bảng có geometry: `EPSG:4326` (GeoJSON/IMDF dùng WGS84). Bảng không geometry: `data_type='attributes'`, `srs_id=0`.

**Quy ước cột tag OSM**: tiền tố `osm_` để không đụng cột IMDF (đặc biệt `name`: IMDF là LABELS JSON, OSM là chuỗi). Tên cột không dùng `:`.

| Cột OSM | Tag | | Cột OSM | Tag |
|---|---|---|---|---|
| `osm_indoor` | `indoor` | | `osm_door` | `door` |
| `osm_level` | `level` | | `osm_entrance` | `entrance` |
| `osm_level_ref` | `level:ref` | | `osm_highway` | `highway` |
| `osm_name` | `name` | | `osm_stairs` | `stairs` |
| `osm_ref` | `ref` | | `osm_tags` | phần tag còn lại (JSON) |

**Cột chung** (mọi bảng): `fid`, `id`, `feature_type`, `source_kind` (`dxf`/`ifc`), `source_ref`, `source_class` (IFC class hoặc CAD layer).

| Bảng | Geometry | Cột IMDF (bắt buộc **đậm**) | Cột OSM dùng |
|---|---|---|---|
| `venue` | Polygon | **`category`**, **`name`** (LABELS), **`display_point`**, **`address_id`**, `restriction`, `hours`, `phone`, `website` | — |
| `address` | *không* | **`address`**, **`locality`**, **`country`**, `unit`, `province`, `postal_code` | — |
| `building` | *không* | **`category`** (`unspecified`), `name`, `address_id` | `osm_tags` (`building`, `min_level`, `max_level`) |
| `footprint` | Polygon | **`category`** (`ground`), **`building_ids`** (JSON, ≥1) | — |
| `level` | Polygon | **`category`**, **`outdoor`**, **`ordinal`**, **`name`**, **`short_name`**, `building_ids` | `osm_level`, `osm_level_ref`, `osm_indoor` |
| `unit` | Polygon | **`category`**, **`level_id`**, `name`, `restriction`, `accessibility`, `display_point` | `osm_indoor`, `osm_level`, `osm_level_ref`, `osm_name`, `osm_ref`, `osm_highway`, `osm_stairs` |
| `opening` | LineString | **`category`**, **`level_id`**, `door` (JSON object), `access_control`, `accessibility`, `name` | `osm_indoor`, `osm_door`, `osm_entrance`, `osm_level` |
| `fixture` | Polygon | **`category`**, **`level_id`**, `name` | (tuỳ chọn) |
| `detail` | LineString | **`level_id`** | (tuỳ chọn) |
| `_meta` | *không* | `pipeline_version`, `created`, `source_files` (JSON), `crs_source`, `warnings` (JSON) | — |

Ghi chú: danh sách cột lấy từ [imdf-feature-types](../research/04-osm-imdf-tagging/imdf-feature-types.md) (đọc trang gốc register.apple.com); `venue.category` và định dạng chi tiết của LABELS chưa xác minh (mục 11). `display_point` lưu GeoJSON Point dạng text.

## 6. Quy tắc georeference

Thứ tự ưu tiên (dùng nguồn đầu tiên có):
1. **IFC4+ có `IfcMapConversion` + `IfcProjectedCRS`**: đổi sang mét, rồi `E = Scale·(x·a' − y·b') + Eastings`, `N = Scale·(x·b' + y·a') + Northings`, `H = z·Scale + OrthogonalHeight`, với `(a', b')` là `(XAxisAbscissa, XAxisOrdinate)` **đã chuẩn hoá**; sau đó `pyproj.Transformer.from_crs(<CRS trong IfcProjectedCRS.Name>, "EPSG:4326", always_xy=True)`.
2. **`georeference` trong `project.yaml`** (`crs`, `origin`, `rotation_deg`, `scale`): cùng công thức, dùng cho DXF và IFC2X3.
3. **Control points** (≥ 2 cặp toạ độ cục bộ ↔ toạ độ thật, biến đổi đồng dạng): chỉ thiết kế, chưa bắt buộc cài đặt ở TASK-010.
4. **`IfcSite.RefLatitude/RefLongitude`**: chỉ làm dự phòng, độ chính xác thấp; luôn ghi cảnh báo.
5. Không có nguồn nào: lỗi (mã 1) trừ khi `--allow-unreferenced`; khi đó ghi `srs_id=-1`, `_meta.crs_source='none'`, và `export_imdf` từ chối.

CRS gợi ý cho Việt Nam (đã tra bằng CSDL EPSG qua `pyproj`): `EPSG:4756` (VN-2000 địa lý), `EPSG:3405` / `3406` (UTM 48N / 49N), `5896`–`5899` (TM-3). Quy định phép chiếu theo địa phương chưa xác minh. Ref: [ifc-georeference](../research/02-bim/ifc-georeference.md).

## 7. Mô-đun xuất gói IMDF (`export_imdf`)

*(theo yêu cầu bổ sung của chủ dự án trong TASK-009; kết quả khảo sát công cụ ở `research/05-market-tools/`)*

- **Vào**: `.gpkg` do pipeline tạo (mục 5). **Ra**: `<tên>.imdf.zip` gồm `manifest.json` (bắt buộc), `address.geojson` (bắt buộc), `venue.geojson` (bắt buộc, đúng một Venue) và các `*.geojson` tuỳ chọn (`building`, `footprint`, `level`, `unit`, `opening`, `fixture`, `detail`, …).
- **Chuyển đổi mỗi dòng → GeoJSON Feature**: `{"id": <id>, "type": "Feature", "feature_type": <feature_type>, "geometry": <geometry hoặc null>, "properties": {…}}`; bỏ `fid`, `source_*`, `osm_*`; cột JSON text → object/mảng; bảng `attributes` → `geometry: null`; `building`, `address` không có geometry.
- **Manifest**: các khoá `version` (`"1.0.0"`), `created` (ISO date-time, không múi giờ), `language`, `generated_by`, `extensions`. Chỉ có ví dụ trong spec, **định nghĩa đầy đủ chưa có**, nên coi là suy từ ví dụ.
- **Từ chối** khi: thiếu venue/address, `crs_source='none'`, ràng buộc ở mục 9 loại B không đạt.
- **Đối chiếu**: gói do Archilogic sinh từ DXF mẫu (nếu có) và validator cộng đồng `IMDFrnt` (chưa đánh giá). Ref: [imdf-relations-and-constraints](../research/04-osm-imdf-tagging/imdf-relations-and-constraints.md).

## 8. Thứ tự xử lý và tính tái lập
- Cùng đầu vào + cấu hình + `namespace` → cùng `id` (uuid5) và cùng nội dung GPKG (trừ `_meta.created`).
- Mỗi lần chạy ghi `_meta.source_files` kèm băm (hash) file nguồn.

## 9. Kiểm tra hợp lệ (`check`)

**A. Cấu trúc GPKG** — `application_id = 0x47504B47`; `user_version ≥ 10200`; `gpkg_spatial_ref_sys` có `-1`, `0`, `4326`; `gpkg_contents.data_type` đúng (`features`/`attributes`); `gpkg_geometry_columns` khớp bảng; `PRAGMA integrity_check = ok`; `PRAGMA foreign_key_check` rỗng; `ogrinfo -al -so` đọc được.

**B. Dữ liệu** — CRS 4326 trên mọi bảng có geometry; hình học hợp lệ, không rỗng, đúng kiểu cột; `id` duy nhất và là UUID; mọi khoá ngoại trỏ tới feature tồn tại; các cột bắt buộc không null (`level.name`, `level.short_name`, `venue.name`, …); `building` và `address` không có geometry; `opening` là LineString một phần, nằm trên ranh giới một `unit`; `unit` nằm trong `level`; các `unit` cùng tầng không chồng lấn và hợp ≈ `level` trong dung sai; mọi feature nằm trong `venue`.

## 10. Danh sách test cho TASK-010

| ID | Test | Kỳ vọng (với `samples/`) |
|---|---|---|
| T1 | `ezdxf.readfile` + audit 2 DXF mẫu | 0 lỗi, `doc.units == 6` |
| T2 | `layer_mapping` trên `sample-floor-1.dxf` | 13 space, 13 nhãn, 12 cửa, 13 đối tượng tường, **0 unmatched** |
| T3 | Dựng phòng từ DXF | 13 polygon; phòng 4×5 m có diện tích 20,0 m²; hành lang 24×2 m = 48 m² |
| T4 | Gán nhãn | mỗi phòng nhận đúng mã `P101…P112` |
| T5 | IFC mẫu | 2 tầng, 26 `IfcSpace`, 24 `IfcDoor`, 8 `IfcWall`; tầng của space qua `get_aggregate` |
| T6 | Footprint IFC | cùng diện tích với DXF (sai số ≤ 1e-6 m²) |
| T7 | `normalize` | hành lang → `osm_indoor=corridor` + `unit.category=walkway`; phòng → `osm_indoor=room`; cửa → `osm_indoor=door` + `osm_door=yes` |
| T8 | `id` ổn định | chạy 2 lần → `id` giống hệt |
| T9 | Georeference | điểm gốc cục bộ → đúng E/N rồi đúng lon/lat (so với `pyproj`); thiếu cấu hình → mã thoát 1 |
| T10 | GPKG mục 9-A | tất cả đạt |
| T11 | GPKG mục 9-B | tất cả đạt; cố ý phá 1 khoá ngoại → bị phát hiện |
| T12 | Bảng không geometry | `building`, `address` là `attributes`, `srs_id=0` |
| T13 | Đọc lại | `geopandas.read_file` cho từng bảng ra đúng số dòng và CRS |
| T14 | `export_imdf` | ZIP có đúng 3 file bắt buộc, mỗi `*.geojson` là `FeatureCollection`, `id` UUID, `feature_type` khớp tên file |
| T15 | `export_imdf` từ chối | thiếu venue hoặc `crs_source='none'` → lỗi rõ ràng |
| T16 | QGIS (thủ công, TASK-011) | các layer load đúng CRS/vị trí, lọc theo `level_id` |

## 11. Chưa chốt / rủi ro

| # | Vấn đề | Việc cần làm |
|---|---|---|
| 1 | `venue.category` chưa chọn (27 giá trị của IMDF `reference/categories`) | tra rồi chọn; điền vào `project.yaml` |
| 2 | Dạng LABELS chi tiết (`{"vi": "…"}`?) và định nghĩa Manifest object chưa xác minh | đọc trang `reference` IMDF; nếu lệch thì sửa mục 5 và 7 |
| 3 | Cột OSM của `tag_mapping.yaml` chưa có tiền tố `osm_` | đã đồng bộ ở lần commit này (xem `defaults.gpkg.osm_columns`) |
| 4 | `IfcTransportElement` ELEVATOR chưa kiểm trong schema | laptop thử trên IFC có thang máy |
| 5 | Footprint từ `Body`: file Revit thật có `FootPrint` không; space nhiều tầng | cần file thật |
| 6 | `Scale ≠ 1` và đơn vị mô hình khác mét trong `IfcMapConversion` chưa kiểm | thêm test khi có mẫu |
| 7 | Quy ước layer thực tế ở Việt Nam, `A-GLAZ`/`A-COLS`/`A-STRS` chỉ là gợi ý | cần mẫu bản vẽ thật |
| 8 | Control points (mục 6.3) chưa có thiết kế chi tiết | tách task nếu cần |
| 9 | Quy định pháp lý chọn phép chiếu VN-2000 | hỏi chủ dự án |
| 10 | `display_point` đặt thế nào cho polygon lõm | dùng `representative_point()` của shapely (đề xuất, chưa kiểm) |
