# Thiết kế lại khung `cad2bim` từ các ý tưởng đã khảo sát

- **Câu hỏi nghiên cứu**: Khung `cad2bim` nên được tổ chức thế nào để (a) vẫn phục vụ đường DXF → GPKG/IMDF hiện có, (b) thêm đầu ra IFC có thông tin, (c) đánh giá khách quan và sửa lỗi theo từng đợt chạy trên bộ bản vẽ đa dạng?
- **Kết luận ngắn**: Tách `cad2bim.build` (hàm đơn khối ~140 dòng) thành các tầng có hợp đồng dữ liệu rõ: **đọc → phân loại theo luật → làm sạch đoạn thẳng → dựng tường/lỗ mở/phòng → mô hình BIM có truy vết → các đầu ra** (GPKG/IMDF cũ, IFC mới, kiểm tra). Mô hình `Model/Obj` hiện có giữ làm *góc nhìn 2D* cho `normalize`/`export`, không phá vỡ đường cũ. Mọi suy đoán (độ dày, cao độ, loại) phải ghi `assumption` kèm nguồn. Có sẵn một **bộ đánh giá theo bộ bản vẽ** để mỗi lần sửa mã đo lại các chỉ số.
- **Độ tin cậy**: đây là **đề xuất thiết kế**, chưa cài đặt. Các thành phần nền đã được thử riêng lẻ (nối góc bằng `shapely`, lỗ mở bằng `feature.add_feature/add_filling` trên IfcOpenShell 0.9.0.post1, đọc cung/INSERT bằng `ezdxf`); tên class IFC4 đã kiểm bằng schema trong `ifcopenshell`. Các thuật toán lấy từ repo khác (ghép hai nét song song của roomgraph, kéo dài đầu rời của Cloud2BIM) mới đọc mã, **chưa chạy trên dữ liệu thật**.

## 0. Phát hiện từ dữ liệu thật (cập nhật sau khi tải corpus, 2026-11-08)
Đã tải corpus công khai (xem `samples/corpus/README.md`) và chạy **khâu `cad2bim` hiện có** trên đó (`tests/eval/run_baseline.py`, nhãn `baseline-m0-pre-refactor`, kết quả trong `out/eval/`).

| Số liệu | Giá trị |
|---|---|
| Số file DXF trong corpus | 80 (Innerscene CC0: 51; GitHub CC0: 29) |
| Đọc được bằng `ezdxf` | 80/80, chạy `cad2bim.build` không lỗi nào |
| Phiên bản DXF | R2000 đến R2018 (AC1015, 1018, 1021, 1024, 1027, 1032) |
| Đơn vị `$INSUNITS` | 79 file mm, 1 file inch |
| Thực thể trung vị / lớn nhất sau khi mở khối INSERT | 13 / 1298 |
| File có LWPOLYLINE bulge, ARC, HATCH, INSERT | 20, 19, 4, 49 |
| File có tên layer khớp mẫu NCS đang dùng (`A-WALL`, `A-DOOR`, `A-AREA`, `A-GLAZ`, `A-COLS`, `A-STRS`) | **0** |
| Layer phổ biến | `0` (55 file), `A-BORDER` và `A-TEXT` (17), `WALLS/DOORS/WINDOWS/TEXT` (3) |
| **Đường cơ sở: số file mà luật hiện tại nhận dạng được ít nhất 1 thực thể** | **0/78** (78 file có thực thể) |

Ý nghĩa:
1. **Luật layer kiểu NCS hiện tại trượt hoàn toàn** trên dữ liệu thật. Trong các mặt bằng phức tạp nhất (800–1300 thực thể), toàn bộ nét tường, cửa, đồ nội thất nằm chung 1–2 layer (`A-BORDER`, `A-TEXT`) hoặc layer `0`, nên **tên layer không mang ngữ nghĩa**. Ít file hơn có layer tiếng Anh đơn giản (`WALLS`, `DOORS`, `WINDOWS`, `FURNITURE`).
2. Đây là minh chứng trực tiếp cho khoảng trống Geometry → Semantic. Khung phải có **tầng thứ hai ngoài tên layer**: (a) hồ sơ luật có bí danh (WALLS, TUONG…), (b) suy luận theo hình học (hai nét song song = tường; INSERT có cung quét = cửa), (c) `INSERT`: tên khối (`DOOR`, `WINDOW`…) là tín hiệu mạnh hơn tên layer.
3. Phần lớn hình học nằm trong **khối INSERT**: `read` bắt buộc phải mở khối (`virtual_entities`) ngay từ đầu, vì hiện `build` chỉ duyệt modelspace.
4. Corpus này nghiêng về **mặt bằng nhà ở/phòng khám cỡ nhỏ và chi tiết**; bản vẽ MEP toà nhà đầy đủ ít (nhiều bản MEP thật chỉ có định dạng DWG). Chỉ số corpus nhiều khả năng đo độ bền và độ phủ hơn là độ đúng.

## 1. Nguyên tắc thiết kế (rút từ khảo sát)

| # | Nguyên tắc | Nguồn ý tưởng | Hệ quả |
|---|---|---|---|
| P1 | **Tách "hiểu" khỏi "ghi"**: bước suy luận ngữ nghĩa cho ra một mô hình trung gian tường minh, bước ghi IFC chỉ biên dịch mô hình đó | alvin528/CAD2BIM; nhận xét về khoảng trống Geometry → Semantic (FreeCAD, IfcOpenShell đều không có engine này) | `ifc_writer` không đọc DXF, không đoán |
| P2 | **Luật khai báo, không mã cứng**: layer **và tên khối** → loại → mặc định → Pset nằm trong cấu hình | dwg2ifc (profile TOML), `config/layer_mapping.yaml` của ta | thêm bản vẽ mới = thêm luật, không sửa mã |
| P3 | **Không đoán im lặng**: mỗi giá trị suy đoán có `claim_state` (observed / derived / assumed), `assumption`, `source_refs` | alvin528 (`claim_state`), 2D23D (Pset "provisional"), ifcbim (Pset nguồn gốc) | cao độ, độ dày, `IsExternal`… luôn có dấu vết |
| P4 | **Hình học tham số, không mesh** | dwg2ifc, Cloud2BIM (so với ifcbim/alvin528 dùng mesh) | tường = đường tim + độ dày + chiều cao (`Axis` + `Body`) |
| P5 | **Hình học sạch trước, ngữ nghĩa sau** (nối góc, kéo dài đầu rời, tách giao chữ T) | Cloud2BIM, FreeCAD `offsetWire/connect`, roomgraph | thuật toán thuần hình học bằng `shapely`, kiểm riêng được |
| P6 | **Dùng thư viện cho phần phổ thông**: `ifcopenshell.api`, `shapely`, `ezdxf.path` | thử nghiệm của ta | chỉ tự viết phần chưa có ở đâu |
| P7 | **Kiểm tra nhiều lớp và đo được** | ifc-floorplan (IoU phòng, đo nhất quán), ifcbim (báo cáo entity bỏ qua) | bộ đánh giá chạy tự động trên cả bộ bản vẽ |
| P8 | **Tái lặp**: GUID ổn định từ id nguồn, ghi phiên bản, tham số, hash đầu vào | dwg2ifc, alvin528, ifc-floorplan (`run.json`) | hai lần chạy cùng đầu vào ra cùng IFC |
| P9 | **Giấy phép**: chỉ học ý tưởng từ mã không giấy phép; viết lại, không chép | ifcbim, ifc-floorplan, SaN-architect-ai, `dxf2ifc.py` (GPL-3.0) | ghi nguồn ý tưởng trong docstring |

## 2. Kiến trúc đề xuất

### 2.1 Hiện trạng (đọc `src/pipeline.py`, `src/model.py`, `src/cad2bim/__init__.py`)
`ingest` → `cad2bim.build` (một hàm: duyệt entity, khớp luật, cắt hình, suy bề rộng cửa, ghép nhãn, polygonize) → `Model(storeys, objs, warnings, unmatched…)` → `georef` → `normalize.to_features` → `export_gpkg` / `export_imdf` / `validate`. `Obj` là đối tượng 2D cho bản đồ (`space`, `door`, `wall`, `outline`, `stair`, `column`, `fixture`, `detail`). Tường dạng LINE/polyline hở **không** thành đối tượng (chỉ polygon kín có độ dày).

### 2.2 Đích
```
DXF ──► [0 read]      DxfSource: đơn vị, layer đã chuẩn hoá, thực thể phẳng hoá về WCS
         │              (make_path cho cung, virtual_entities cho INSERT, OCS→WCS)
         ▼
        [1 classify]  RuleSet: khớp layer/loại/block → (kind, ifc class, defaults, psets); báo unmatched
         │
         ▼
        [2 segments]  làm sạch đường tim: snap, kéo dài đầu rời, noding (tách chữ T), ghép chuỗi
         │
         ▼
        [3 walls]     ghép hai nét song song → tường có độ dày; thiếu thì lấy độ dày theo luật
         │            (đánh dấu assumed); buffer mitre; hợp nhất
         ▼
        [4 openings]  INSERT cửa/cửa sổ + khoảng hở trong tường → gắn vào tường chủ (host)
         │
         ▼
        [5 spaces]    phòng từ A-AREA (+nhãn); dự phòng polygonize từ tường đã khép kín
         │
         ▼
       BimModel  ◄── mọi phần tử: id ổn định, class, hình học tham số, storey, source_refs,
         │            claim_state, assumptions, props/psets
         ├──► adapter 2D ──► Model/Obj cũ ──► georef ► normalize ► GPKG ► IMDF   (giữ nguyên)
         ├──► ifc_writer ──► IFC4 ──► enrich (Pset/vật liệu/phân loại) ──► validate_ifc
         └──► report.json (thống kê, giả định, unmatched, bỏ qua)
```
Đường IFC → GPKG hiện có (`ingest.ifc`, `extract.ifc`) **không đổi**; nó trở thành bên kiểm chéo: `DXF → IFC → GPKG` so với `DXF → GPKG`.

### 2.3 Bố cục mô-đun (đề xuất)
| Tệp | Trách nhiệm | Lấy ý tưởng / mã sẵn |
|---|---|---|
| `cad2bim/__init__.py` | mặt tiền giữ nguyên chữ ký `build(...)`, gọi các tầng | giữ tương thích test cũ |
| `cad2bim/rules.py` | `norm_layer`, `match_rule`, `RuleSet` có mặc định (cao, dày, vật liệu), Pset theo luật, tên class IFC | mã hiện có + profile của dwg2ifc |
| `cad2bim/read.py` | phẳng hoá thực thể: `make_path(...).flattening` (giữ bulge), `ocs().to_wcs`, `INSERT.virtual_entities()`, đổi đơn vị | ezdxf; sửa bỏ bulge và OCS cung/tròn |
| `cad2bim/segments.py` | snap, `extend_free_ends`, noding bằng `unary_union`, `linemerge` | Cloud2BIM; **đã thử** trên mẫu |
| `cad2bim/walls.py` | ghép cặp đường song song → (đường tim, độ dày); buffer mitre; hợp nhất | roomgraph `walls.py`; FreeCAD `connect`; **đã thử** mitre/union |
| `cad2bim/openings.py` | cửa/cửa sổ từ INSERT (vị trí, bề rộng, hướng mở) và từ khoảng hở; gán tường chủ gần nhất | mã cửa hiện có; roomgraph (khoảng hở); Cloud2BIM (voids/fills) |
| `cad2bim/spaces.py` | phòng, nhãn, polygonize | tách từ `build` hiện có |
| `cad2bim/elements.py` | dataclass `BimElement`, `Provenance`, `BimModel` | alvin528 (truy vết) |
| `cad2bim/ifc_writer.py` | IFC4: `IfcProject/Site/Building/Storey`, `IfcWallType` + `IfcMaterialLayerSetUsage`, tường `Axis` + `Body`, lỗ mở voids/fills, `IfcSpace`, GUID ổn định | Cloud2BIM; IfcOpenShell `api.*`; dwg2ifc |
| `cad2bim/enrich.py` | bảng CSV/YAML → Pset/vật liệu/phân loại; kiểm tên thuộc tính bằng `util.pset.get_template` | `poc/enrich_ifc_demo.py` |
| `cad2bim/validate_ifc.py` | mở lại IFC, đếm, bounding box, IoU phòng, đối chiếu GPKG | ifc-floorplan (ý tưởng) |
| `tests/eval/` | bộ chạy đánh giá theo bộ bản vẽ | xem mục 5 |

### 2.4 Hợp đồng dữ liệu `BimElement` (đề xuất)
```
id            str   ổn định: sha1("file|layer|handle|chỉ số") -> IFC GlobalId
kind          wall | door | window | space | slab | column | stair | duct | pipe | terminal | equipment | proxy
ifc_class     tên class IFC4 (kiểm theo schema)       predefined_type  str | None
storey        key tầng
geometry      wall: {axis: LineString, thickness, height, align} | footprint: Polygon | point: {xy, rotation, size}
host_id       với door/window: id tường chủ            opening: {width, height, sill}
props         dict (Name, Description, Reference…)    psets  dict[str, dict]
provenance    source_refs: ["file|layer|handle", …]
              claim_state: observed | derived | assumed      (theo từng trường quan trọng)
              assumptions: ["thickness=0.2 m (luật A-WALL, không có nét đôi)"]
              confidence: high | medium | low
```
`claim_state` theo từng trường: ví dụ độ dày `derived` khi ghép được cặp nét song song, `assumed` khi lấy từ luật.

## 3. Thuật toán từng tầng (trạng thái kiểm chứng)

| Tầng | Thuật toán | Trạng thái |
|---|---|---|
| read | `ezdxf.path.make_path` cho LWPOLYLINE có bulge; `e.ocs().to_wcs` cho cung/tròn; `INSERT.virtual_entities()` | **đã thử** trên mẫu tổng hợp (độ dài cung đúng; tâm cung lật gương cần WCS) |
| classify | luật neo regex, khớp đầu thắng, bỏ tiền tố xref, thêm mặc định/Pset theo luật; layer lạ vào báo cáo | có sẵn (cần thêm mặc định/Pset) |
| segments | snap → `extend_free_ends` (tia theo hướng đoạn, dung sai `tol`) → `unary_union` → `linemerge` | **đã thử** trên mẫu: khôi phục đúng 13 phòng với khe hở 0,15–0,30 m; chưa thử bản vẽ thật |
| walls | gom đoạn lên đường thẳng vô hạn, ghép cặp qua khoảng độ dày cho phép, lỗ mở = khoảng hở của cặp; mitre bằng `buffer(join_style='mitre')` | mitre/union **đã thử**; **ghép cặp chưa cài đặt/chưa thử** (chỉ đọc mã roomgraph) |
| openings | cửa từ INSERT: vị trí, bề rộng (từ LINE lớn nhất trong khối hoặc `ATTRIB`), góc; tường chủ = tường gần nhất; khoét lỗ voids/fills | voids/fills **đã thử** (IfcOpenShell 0.9.0.post1); gán tường chủ chưa cài đặt |
| spaces | `A-AREA` + nhãn; polygonize tường khép kín khi thiếu | có sẵn; phần polygonize dựa trên tường chưa nối |
| ifc_writer | tường: `add_wall_representation` hoặc profile + `IfcExtrudedAreaSolid` (có `Axis`); kiểu tường + material layer set; `add_slab_representation(polyline=…)` cho phòng | từng hàm API **đã kiểm chữ ký**; ghi toàn bộ chưa cài đặt |
| enrich | bảng ánh xạ → `pset.add_pset/edit_pset`, `material.*`, `classification.*` | **đã chạy** demo 16 tường |
| validate_ifc | mở lại bằng `ifcopenshell`; đối chiếu số lượng/bbox; IoU phòng (IFC vs `A-AREA`) | chưa cài đặt |

### 3.1 Mở rộng MEP (đề xuất, chưa thử)
- Hai dạng mới ngoài tường/phòng: **phần tử tuyến** (đường tim + kích thước/đường kính → ống, ống gió, máng cáp) và **phần tử điểm** (INSERT → thiết bị đầu cuối/thiết bị).
- Class IFC4 liên quan đã kiểm tồn tại trong schema: `IfcPipeSegment`, `IfcDuctSegment`, `IfcCableCarrierSegment`, `IfcCableSegment`, `IfcFlowSegment`, `IfcFlowTerminal`, `IfcAirTerminal`, `IfcSanitaryTerminal`, `IfcLightFixture`, `IfcValve`, `IfcPump`, `IfcElectricDistributionBoard`, `IfcFireSuppressionTerminal`, `IfcDistributionElement` (đều không trừu tượng trong schema đang dùng).
- Luật layer MEP khác nhiều theo quy ước từng công ty; cần luật riêng theo hồ sơ (profile) thay vì một bảng chung. dwg2ifc (CABLELADDER/PIPE/EVAPORATOR theo layer `KYL-*`) là ví dụ cho kiểu luật, không dùng lại được nguyên.
- Hệ thống (`IfcSystem`) và kết nối cổng (`IfcDistributionPort`) **chưa nghiên cứu**; không đưa vào mốc đầu.

## 4. Mở rộng cấu hình `layer_mapping.yaml` (đề xuất)
Giữ nguyên các khoá hiện có (`pattern`, `entity_types`, `type`, `ifc`, `require_closed`, `block_pattern`…). Thêm tuỳ chọn:
```yaml
defaults:                      # áp cho luật không khai báo riêng
  wall:  {height_m: 3.0, thickness_m: 0.2, material: Concrete}
tolerances:
  snap_m: 0.01                 # gộp đầu mút trùng
  extend_m: 0.30               # kéo dài đầu rời tới đường tim (đặt lớn hơn khe hở dự kiến)
  pair_thickness_m: [0.06, 0.60]   # khoảng độ dày khi ghép hai nét song song
  min_wall_len_m: 0.30
  mitre_limit: 5.0
rules:
  - id: wall
    pattern: '^A-WALL(-.*)?$'
    thickness_source: pair|param   # ghép nét; nếu không ghép được thì dùng defaults (assumed)
    psets: {Pset_WallCommon: {IsExternal: false, LoadBearing: false}}   # là GIẢ ĐỊNH, ghi vào assumptions
```
Mọi giá trị trong `psets` có `status: assumed` mặc định để không bị hiểu nhầm là dữ liệu quan sát.

## 5. Bộ đánh giá (để sửa lỗi theo từng đợt)

**Bộ dữ liệu theo tầng**
1. **Đơn vị/tổng hợp**: DXF sinh bằng `ezdxf` có kiểm soát (góc vuông/xiên, khe hở, nét đôi, bulge, INSERT lật gương, đơn vị khác nhau). Có đáp án đúng, chạy trong CI nhanh.
2. **Mẫu của dự án**: `samples/*.dxf` (đáp án đã biết).
3. **Corpus công khai**: `samples/corpus/` (Innerscene CC0 ~100 bản vẽ; GitHub CC0; có `MANIFEST.csv` ghi nguồn, hash, giấy phép). Không có đáp án, chấm bằng chỉ số nội tại.
4. **Độ bền**: các tệp DXF "khó" (phiên bản cũ, hỏng nhẹ, thực thể lạ) để đảm bảo không sập: chỉ yêu cầu "không ném lỗi, báo cáo rõ".

**Chỉ số (mỗi bản vẽ, ghi JSON)**
| Nhóm | Chỉ số | Ý nghĩa |
|---|---|---|
| Đọc | đọc được/khôi phục/lỗi; số thực thể theo loại; thực thể bị bỏ qua và lý do | độ phủ |
| Phân loại | % thực thể khớp luật / bỏ qua / không khớp; top layer không khớp | chất lượng luật |
| Hình học | tổng chiều dài tim trước/sau (phải bảo toàn); tỉ lệ đầu rời còn lại; số khe hở đã đóng; số tường sau noding | độ sạch |
| Tường | % tường có độ dày từ ghép nét (derived) so với từ luật (assumed); diện tích thân tường | độ tin cậy giả định |
| Lỗ mở | số cửa/cửa sổ có tường chủ; số `IfcRelVoidsElement`/`IfcRelFillsElement` | tính đúng đắn |
| Phòng | số phòng; IoU phòng từ tường vs `A-AREA` (nếu có) | nhất quán |
| IFC | mở lại được; tạo hình học được cho mọi sản phẩm; số sản phẩm theo class; thiếu Pset bắt buộc | hợp lệ |
| Chéo đường | DXF→GPKG vs DXF→IFC→GPKG: lệch số lượng/diện tích | không hồi quy |
| Vận hành | thời gian, bộ nhớ | hiệu năng |

**Cách chạy**: `python -m tests.eval run --corpus samples/corpus --out out/eval/<nhãn>.json`, rồi `compare a.json b.json` in các chỉ số xấu đi/tốt lên. Ngưỡng hồi quy tối thiểu ở mức đơn vị/tổng hợp (có đáp án); với corpus chỉ cảnh báo (không có đáp án).

**Quy trình sửa lỗi**: chạy → xem các bản vẽ có chỉ số xấu nhất → tìm nguyên nhân → thêm một ca tổng hợp tái hiện lỗi vào tầng 1 → sửa → chạy lại; không sửa nếu chưa có ca tái hiện.

## 6. Lộ trình (đề xuất, mỗi mốc kiểm được độc lập)
| Mốc | Nội dung | Kết quả kiểm |
|---|---|---|
| M0 | Bộ đánh giá + hồ sơ corpus (`profile_corpus.py`, `tests/eval/run_baseline.py`) trên mã **hiện có** — **đã làm**: 80 file, 0/78 nhận dạng được | có đường cơ sở (baseline) để so |
| M1 | Tách `build` thành `rules/read/spaces`; **mở khối INSERT**; sửa bulge và OCS cung/tròn; thêm bí danh layer/khối | test cũ vẫn qua; số file nhận dạng được > 0/78 |
| M2 | `segments` + `walls` (noding, kéo dài đầu rời, mitre, ghép nét song song) | chỉ số Hình học/Tường tăng trên tổng hợp và corpus |
| M3 | `openings` + `ifc_writer` tối thiểu (tường, cửa có lỗ, phòng) | IFC mở được trong ifcopenshell, FreeCAD, Bonsai |
| M4 | `enrich` + `validate_ifc` + kiểm chéo GPKG | chỉ số IFC/Chéo đường |
| M5 | Mở rộng MEP (tuyến/điểm) cho một hồ sơ layer cụ thể | cần bản vẽ MEP thật |
Phân vai gợi ý: claude-mobile viết M0–M2 (thuần Python, kiểm tự động); claude-laptop kiểm bằng GUI ở M3 (FreeCAD/Bonsai).

## 7. Rủi ro và việc cần chốt với người dùng
- **Đầu vào thật khác corpus công khai**: bản vẽ Việt Nam/dự án cụ thể có quy ước layer riêng; cần file thật để chỉnh luật.
- **DWG**: hiện chỉ DXF. Nhận DWG cần ODA File Converter (đóng nguồn, kiểm giấy phép) hoặc LibreDWG (GPL-3.0, chưa đủ entity).
- **IFC4 hay thêm IFC2x3**; **độ dày tường** lấy từ nét đôi hay luôn tham số; **mức LOD** chấp nhận.
- **Corpus công khai nhiều bản vẽ là chi tiết/ký hiệu, không phải mặt bằng toà nhà**: chỉ số trên corpus chủ yếu đo độ bền và độ phủ, không đo độ đúng.
- **Dung sai** (`snap`, `extend`, `pair_thickness`) phụ thuộc đơn vị và tỉ lệ bản vẽ; cần chọn theo đơn vị đã chuẩn hoá sang mét và hiệu chỉnh trên dữ liệu thật.
- **Chưa kiểm**: ghép cặp nét song song; gán tường chủ cho cửa; hiệu năng trên bản vẽ lớn (2D23D báo 54 MB DXF/35 s là số liệu của tác giả, chưa kiểm).

## Liên quan đến pipeline CAD → BIM → GPKG
Tài liệu này mô tả khung chính của bước `cad2bim` trong [docs/cad-to-gpkg-design.md](../../docs/cad-to-gpkg-design.md) mục 4.2 và đề xuất cập nhật đó khi được chấp thuận (chỉ `synthesizer` được ghi vào `docs/`).

## Nguồn
- Ghi chú nội bộ: [cad2bim-and-ifcbim-code-review](cad2bim-and-ifcbim-code-review.md), [github-survey-cad-to-ifc](github-survey-cad-to-ifc.md), [github-group3-code-review](github-group3-code-review.md), [freecad-ifcopenshell-dxf-to-ifc-and-enrichment](freecad-ifcopenshell-dxf-to-ifc-and-enrichment.md), [wall-corner-joins-and-ezdxf-details](wall-corner-joins-and-ezdxf-details.md), [open-source-dxf-to-ifc-projects](open-source-dxf-to-ifc-projects.md)
- Mã hiện tại của dự án: `src/pipeline.py`, `src/model.py`, `src/cad2bim/__init__.py`, `config/layer_mapping.yaml` (đọc 2026-11-08)
- Tên class IFC4: kiểm trực tiếp bằng `ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4")` (0.9.0.post1, 2026-11-08)

## Câu hỏi còn mở
- Ghép hai nét song song có chạy được trên DXF thật không (nét đứt, nhiều lớp)? Chưa cài đặt.
- Tách `build` có giữ nguyên toàn bộ test hiện có không? Chưa thử; cần chạy `pytest` trước và sau.
- Nên đổi `Obj` thành `BimElement` hẳn hay giữ hai lớp (adapter)? Đề xuất adapter để không phá đường GPKG/IMDF; cần xác nhận.
- Bản vẽ MEP toà nhà thật: nhiều bản có sẵn chỉ ở định dạng DWG; cần bộ chuyển DWG → DXF (ODA File Converter hoặc LibreDWG, chưa cài) — cần người dùng quyết định.
