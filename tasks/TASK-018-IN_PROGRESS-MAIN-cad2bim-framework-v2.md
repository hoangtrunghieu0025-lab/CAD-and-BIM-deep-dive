---
id: TASK-018
title: "[IN_PROGRESS][MAIN] Khung cad2bim v2: đọc/phân loại/làm sạch hình học/tường và bộ đánh giá trên corpus"
category: MAIN
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-08T23:10:00+07:00
updated_at: 2026-11-09T15:20:00+07:00
status: in_progress
priority: high
depends_on: [TASK-010, TASK-017]
---

# [IN_PROGRESS][MAIN] TASK-018 — Khung cad2bim v2: đọc/phân loại/làm sạch hình học/tường và bộ đánh giá trên corpus

## Mô tả
Tổ chức lại bước `cad2bim` (hiện là một hàm `build` ~140 dòng trong `src/cad2bim/__init__.py`) thành các tầng có hợp đồng dữ liệu rõ, dựa trên các ý tưởng đã khảo sát ở TASK-017, để về sau dựng được BIM (IFC) từ DXF kiến trúc và MEP. Task này làm **M0–M2** của lộ trình; phần ghi IFC, làm giàu, kiểm IFC và MEP (M3–M5) tách thành task sau khi M2 xong (xem "Ngoài phạm vi").

Thiết kế đầy đủ và lý do: `research/06-cad-to-bim/cad2bim-framework-design.md` (đọc trước khi làm). Task này là bản chốt phạm vi và tiêu chí; khi mâu thuẫn, **task này thắng** và thiết kế phải được cập nhật theo.

**Vì sao làm (số liệu thật, 2026-11-08)**: chạy khâu `cad2bim` hiện có trên `samples/corpus/` (80 file DXF CC0, `tests/eval/run_baseline.py`, nhãn `baseline-m0-pre-refactor`) cho kết quả **0/78 file có thực thể nào được nhận dạng**, không lỗi nào. Nguyên nhân: không file nào dùng layer kiểu NCS (`A-WALL`, `A-DOOR`, `A-AREA`…) mà luật hiện tại khớp; mặt bằng phức tạp nhất dồn mọi thứ vào `A-BORDER`/`A-TEXT` hoặc layer `0`, và phần lớn hình học nằm trong khối INSERT mà `build` chưa mở. Test hiện có: 102 passed (xuất phát).

## Bộ khung mới

### Các tầng và hợp đồng
```
DXF ► [0 read] ► [1 classify] ► [2 segments] ► [3 walls] ► [4 openings*] ► [5 spaces]
      DxfSource   RuleSet        SegmentSet     WallSet      OpeningSet      SpaceSet
                                                     (* chỉ khung, cài đặt ở M3)
                          └────────────► BimModel (phần tử có id ổn định + truy vết) ──► adapter 2D ► Model/Obj cũ ► GPKG/IMDF
```
| Tầng | Mô-đun (`src/cad2bim/`) | Việc | Mốc |
|---|---|---|---|
| 0 read | `read.py` | phẳng hoá thực thể về WCS: mở khối INSERT (`virtual_entities`), giữ cung của LWPOLYLINE (`ezdxf.path.make_path(...).flattening`), đổi OCS→WCS cho ARC/CIRCLE, đổi đơn vị | M1 |
| 1 classify | `rules.py` | `norm_layer`, `match_rule`; luật theo **layer và tên khối**, bí danh (WALLS/TUONG…), mặc định (cao/dày/vật liệu), Pset mặc định gắn nhãn `assumed`; báo unmatched | M1 |
| 2 segments | `segments.py` | snap đầu mút, kéo dài đầu rời tới đường tim trong dung sai, noding (tách chữ T), ghép chuỗi | M2 |
| 3 walls | `walls.py` | ghép hai nét song song thành (đường tim, độ dày); không ghép được thì độ dày theo luật (`assumed`); buffer mitre + hợp nhất | M2 |
| 5 spaces | `spaces.py` | phòng từ `A-AREA`/HATCH, nhãn, polygonize (tách nguyên từ `build`) | M1 |
| mô hình | `elements.py` | `BimElement` (id ổn định, kind, class IFC, hình học, `source_refs`, `claim_state`, `assumptions`, `confidence`), `BimModel` + adapter sang `Model/Obj` | M1 (khung), M2 (dùng) |
| mặt tiền | `__init__.py` | giữ chữ ký `build(src, storey, layers_cfg, tags_cfg, model)` để `pipeline.py` và test cũ không đổi | M1 |
| đánh giá | `tests/eval/` | runner, so sánh hai lần chạy, ca tổng hợp có đáp án | M0–M2 |

`BimElement` (hợp đồng, đề xuất chi tiết ở thiết kế mục 2.4): `id` (băm ổn định từ `file|layer|handle|chỉ số`), `kind`, `ifc_class`, `storey`, hình học (tường: `axis` + `thickness` + `height`; vùng: `Polygon`; điểm: toạ độ + góc + kích thước), `host_id`, `props`, `psets`, `source_refs`, `claim_state` ∈ {observed, derived, assumed}, `assumptions`, `confidence`.

### Nguyên tắc (ràng buộc cho mọi mốc)
- **P1** tách "hiểu" khỏi "ghi": tầng 0–5 không ghi IFC; `ifc_writer` (task sau) chỉ biên dịch `BimModel`.
- **P2** luật khai báo trong cấu hình, không mã cứng tên layer.
- **P3** mọi giá trị suy đoán (độ dày, cao, Pset) ghi `claim_state`/`assumptions`; không đoán im lặng.
- **P4** hình học tham số (đường tim + độ dày + cao), không mesh.
- **P5** làm sạch hình học trước, ngữ nghĩa sau; thuật toán thuần `shapely` để kiểm riêng.
- **P6** dùng thư viện (`ezdxf.path`, `shapely`, `ifcopenshell.api`) cho phần phổ thông.
- **P7** mọi thay đổi có chỉ số đo được trên bộ đánh giá; sửa lỗi theo quy trình "ca tái hiện → sửa → chạy lại".
- **P8** tái lập: id ổn định, ghi phiên bản/tham số/hash đầu vào.
- **P9** giấy phép: chỉ học ý tưởng từ mã không giấy phép; mã MIT/Apache viết lại theo thiết kế của ta; không chép mã GPL.

## Nguồn lấy ý tưởng (ghi rõ để truy vết và tuân thủ giấy phép)
Ghi chú chi tiết nằm trong `research/06-cad-to-bim/`; URL và ngày truy cập nằm ở `research/sources.md`. Cột "Cách dùng" là **chính sách** cho task này.

| Ý tưởng áp dụng | Nguồn | Giấy phép | Cách dùng | Tầng |
|---|---|---|---|---|
| Luật dạng profile: glob không phân biệt hoa thường, khớp đầu thắng, bỏ tiền tố xref, mặc định cao/dày và Pset theo luật | [Mcrauli/dwg2ifc](https://github.com/Mcrauli/dwg2ifc) | MIT | viết lại; ghi nguồn ý tưởng trong docstring | rules |
| Đọc khối bằng `INSERT.virtual_entities()`, đọc `ATTRIB` | dwg2ifc; ezdxf | MIT | dùng API ezdxf | read |
| Ghép hai nét song song: gom đoạn lên đường thẳng vô hạn, ghép cặp qua khoảng độ dày, lỗ mở = khoảng hở | [aec-platform/roomgraph](https://github.com/aec-platform/roomgraph) (`walls.py`) | MIT | viết lại; chưa chạy mã gốc | walls |
| Kéo dài đầu tường rời tới đường tim, tách tường tại giao điểm chữ T | [VaclavNezerka/Cloud2BIM](https://github.com/VaclavNezerka/Cloud2BIM) (`space_generator.py`) | MIT | viết lại; **đã thử** nguyên lý trên mẫu (`poc/wall_corner_join_trial.py`) | segments |
| Nối đoạn tim thẳng hàng/chạm đầu có dung sai, xử lý giao điểm | [naquib0513/2D23D](https://github.com/naquib0513/2D23D) | MIT | viết lại | segments |
| Nối góc mitre: dịch từng đoạn rồi nối bằng giao điểm hai đường kéo dài | FreeCAD `DraftGeomUtils.offsetWire`/`connect` ([FreeCAD](https://github.com/FreeCAD/FreeCAD)) | LGPL-2.1+ | chỉ lấy nguyên lý; dùng `shapely.buffer(join_style='mitre')` thay vì mã FreeCAD | walls |
| Tách bước nhận dạng khỏi bước ghi; phần tử mang `claim_state`, `assumption`, `source_refs`, `confidence` | [alvin528/CAD2BIM](https://github.com/alvin528/CAD2BIM) | Apache-2.0 | học thiết kế; nếu lấy mã phải giữ NOTICE | elements |
| Pset nguồn gốc (`SourceLayer`, `SourceEntity`…), báo cáo entity bị bỏ qua, test tự sinh DXF | [Kevinscsatoshi/ifcbim](https://github.com/Kevinscsatoshi/ifcbim) | **không có giấy phép** | **chỉ ý tưởng, không chép**; tránh các lỗi của nó (regex không neo, `unitless`=mm, INSERT thành hộp, bỏ bulge) | elements, tests |
| Suy phòng từ tường, IoU phòng, đo nhất quán, `run.json` tái lập | [Show2Instruct/ifc-floorplan](https://github.com/Show2Instruct/ifc-floorplan) | **không có giấy phép** | chỉ ý tưởng cho bộ đánh giá | eval |
| Chuỗi 5 bước đọc → dựng tường → lỗ mở → IFC → chấm điểm so với DXF | [vylint-22/SaN-architect-ai](https://github.com/vylint-22/SaN-architect-ai) | **không có giấy phép** (chỉ đọc README) | chỉ ý tưởng | khung |
| Cung/INSERT/đơn vị: `make_path`, `virtual_entities`, `ocs().to_wcs`, `units.conversion_factor` | [mozman/ezdxf](https://github.com/mozman/ezdxf) | MIT | dùng API; **đã thử** (bulge, INSERT lật gương) | read |
| Noding/mitre/hợp nhất: `unary_union`, `linemerge`, `buffer` | shapely | BSD-3 | dùng API; **đã thử** | segments, walls |
| `feature.add_feature/add_filling`, `add_wall_representation`, Pset/vật liệu/phân loại | [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) | LGPL-3.0 | dùng API (task sau); **đã thử** voids/fills trên 0.9.0.post1 | M3 |
| Dữ liệu đánh giá | Innerscene (CC0), [Matleyx78/dxf-test-file](https://github.com/Matleyx78/dxf-test-file) (CC0) | CC0 | dùng được, ghi `samples/corpus/README.md` | eval |

**Không được chép mã**: `dxf2ifc.py` của Bonsai (GPL-3.0), ifcbim, ifc-floorplan, VecFloorSeg, A-Scan2BIM, SaN-architect-ai (không giấy phép). Hướng AI nhận dạng (VecFloorSeg, FloorplanTransformation, FloorPlanToIFC) để sau, chỉ khi luật + hình học không đủ.

## Đầu vào (inputs)
- Thiết kế và khảo sát: `research/06-cad-to-bim/cad2bim-framework-design.md`, `github-survey-cad-to-ifc.md`, `github-group3-code-review.md`, `cad2bim-and-ifcbim-code-review.md`, `wall-corner-joins-and-ezdxf-details.md`, `freecad-ifcopenshell-dxf-to-ifc-and-enrichment.md`
- Mã hiện tại: `src/cad2bim/__init__.py`, `src/model.py`, `src/pipeline.py`, `config/layer_mapping.yaml`, `config/tag_mapping.yaml`
- Dữ liệu: `samples/*.dxf` (có đáp án), `samples/corpus/` (README, MANIFEST, PROFILE.csv; không có đáp án)
- Công cụ đã có: `samples/profile_corpus.py`, `samples/fetch_innerscene_corpus.py`, `tests/eval/run_baseline.py`, `research/06-cad-to-bim/poc/wall_corner_join_trial.py`, `poc/ifc_opening_test.py`

## Đầu ra mong đợi (expected_outputs)
- **M0 (đánh giá)**: `tests/eval/` có runner chạy khâu hiện tại/mới trên một thư mục DXF, ghi JSON chỉ số, và `compare` hai kết quả; sinh được DXF tổng hợp có đáp án (xem tiêu chí). `out/eval/baseline-m0-pre-refactor.json` giữ làm mốc so.
- **M1 (tách tầng, không đổi hành vi cũ)**: `src/cad2bim/{rules,read,spaces,elements}.py`; `__init__.py` còn là mặt tiền; luật theo layer + tên khối + bí danh; `config/layer_mapping.yaml` mở rộng có tương thích ngược.
- **M2 (hình học)**: `src/cad2bim/{segments,walls}.py`; tường được tạo từ LINE/LWPOLYLINE hở (hiện bị bỏ) thành `BimElement` kind `wall` và, qua adapter, thành `Obj` để `normalize` dùng được.
- Cập nhật `research/06-cad-to-bim/cad2bim-framework-design.md` theo những gì thực tế khác thiết kế; dòng nguồn mới (nếu có) vào `research/sources.md`.
- Báo cáo ngắn kết quả so với đường cơ sở ở mục Tiến độ.

## Tiêu chí hoàn thành (acceptance)
**M0**
- [x] Corpus công khai có giấy phép rõ ràng, có MANIFEST (nguồn, sha256, thời điểm tải, giấy phép) và README; bộ tải tuân thủ `robots.txt` và Crawl-delay
- [x] Đường cơ sở chạy trên toàn corpus: 80 file, 0 lỗi, 0/78 nhận dạng được (`out/eval/baseline-m0-pre-refactor.json`)
- [ ] `tests/eval/compare.py`: so hai JSON, in chỉ số tốt lên/xấu đi theo file
- [ ] Bộ sinh DXF tổng hợp có đáp án (`tests/eval/synth.py`): góc L/T/chữ thập, tường hở 0,08–0,30 m, hai nét song song độ dày khác nhau, LWPOLYLINE có bulge, INSERT lật gương, `$INSUNITS` mm/m/0, layer lạ; mỗi ca có kết quả mong đợi (số tường, tổng chiều dài tim, số phòng)
- [ ] Chỉ số tối thiểu trong runner: độ phủ phân loại, số đối tượng theo loại, bảo toàn tổng chiều dài tim, số đầu rời còn lại, số phòng, thời gian, lỗi
**M1**
- [x] 102 test hiện có vẫn qua (`.venv/bin/python -m pytest -q`): hiện 162 passed (102 cũ + 60 mới)
- [x] `read`: mở khối INSERT, giữ bulge, OCS→WCS cho cung/tròn, có test từ ca tổng hợp (`tests/test_v2_read_classify.py`) (cung nửa đường tròn R=2 cho độ dài ≈ 9,283 m trong ví dụ đã thử; tâm cung lật gương đúng ở WCS)
- [ ] `rules`: luật theo tên khối, bí danh layer, mặc định/Pset gắn `assumed`; layer lạ vẫn ghi `unmatched_layers.csv`
- [ ] Số file corpus có ít nhất 1 thực thể nhận dạng **> 0/78** (mục tiêu đề xuất: ≥ 15/78; ghi con số thực tế và lý do nếu thấp hơn)
**M2**
- [x] `segments`: kéo dài đầu rời + noding + ghép chuỗi (`src/cad2bim/segments.py`, `tests/test_v2_geometry.py`); trên ca tổng hợp "vách hở" khôi phục đúng số phòng (đã thử bằng POC: 3 → 13 phòng)
- [x] `walls`: nối góc và hợp nhất bằng `shapely`; ghép nét song song cho ca độ dày khác nhau; độ dày không ghép được ghi `assumed` (`src/cad2bim/walls.py`)
- [ ] Tổng chiều dài tim được bảo toàn qua noding (kiểm tự động); không tạo phòng/tường giả khi `tol` lớn (có ca "lối đi cố ý để hở")
- [x] Mỗi lỗi sửa trong task có một ca tái hiện trong `tests/` trước khi sửa (đã áp dụng cho: `linemerge` một đoạn; `$INSUNITS` sai; đoán đơn vị khi ít điểm)
- [ ] Chỉ số corpus được ghi trước và sau mỗi mốc; không có hồi quy ở các ca có đáp án

## Phạm vi từng bên
- **claude-mobile**: toàn bộ M0–M2 (`src/cad2bim/`, `config/layer_mapping.yaml` mở rộng tương thích ngược, `tests/`, `tests/eval/`, `research/06-cad-to-bim/` để cập nhật thiết kế). Không sửa `docs/` (chỉ `synthesizer`), `PRIMARY_OBJECTIVE.md`, `CLAUDE.md`.

## Ngoài phạm vi (tách task sau khi M2 xong)
- M3: `openings` (gán tường chủ, lỗ voids/fills) và `ifc_writer.py` tối thiểu (tường, cửa có lỗ, phòng); kiểm bằng GUI (FreeCAD/Bonsai) giao claude-laptop.
- M4: `enrich` (bảng Pset/vật liệu/phân loại, kiểm tên thuộc tính bằng `util.pset.get_template`), `validate_ifc` (IoU phòng, kiểm chéo GPKG).
- M5: MEP (phần tử tuyến và điểm; hồ sơ layer riêng; bản vẽ MEP thật có thể chỉ có DWG).
- Nhận DWG (cần ODA File Converter hoặc LibreDWG), hướng AI nhận dạng, georeference mở rộng.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | in_progress | 2026-11-09T12:17:00+07:00 | v2 2D chạy 91/91 file (31 có phần tử); thêm bộ đọc 3D `read3d/analyze3d/ifc3d` (177 test đạt). Còn: compare + synth (M0), tường tô đặc, phòng từ tường, host cửa, ACIS 3DSOLID, đáp án kiểm. Đã chốt hướng luồng AI agent (xem thiết kế mục 8), chưa cài đặt |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-08 23:10 | todo | Tạo task theo yêu cầu của người dùng sau khi hoàn tất khảo sát (TASK-017). Công việc đã làm trước khi mở task: tải corpus CC0 (`samples/fetch_innerscene_corpus.py`, `samples/corpus/`), `samples/profile_corpus.py`, `tests/eval/run_baseline.py`, đường cơ sở 0/78, thiết kế `cad2bim-framework-design.md`. Test hiện có 102 passed. Chưa sửa `src/`. Chưa commit (chờ người dùng) |
| 2026-11-09 06:00 | todo | Theo yêu cầu người dùng: **đã xóa `samples/corpus/`** (129 DXF + 66 DWG mẫu thư viện, ~22 MB, chưa vào git) vì không phải bản vẽ dự án thật. Giữ lại các script (`samples/fetch_innerscene_corpus.py`, `samples/profile_corpus.py`, `tests/eval/run_baseline.py`), 3 file mẫu `samples/sample-floor-*.dxf` và kết quả `out/eval/baseline-m0-*.json`. Các chỉ số `0/78`, `0/127` trong task/thiết kế là của corpus đã xóa, chỉ còn giá trị tham khảo. Cần dữ liệu thật hoặc bộ có đáp án (cắt mặt bằng từ IFC mở) thay thế |
| 2026-11-09 06:20 | todo | Theo yêu cầu người dùng: cài ODA File Converter 27.10.0.0 (AppImage, `~/apps/ODAFileConverter/`), thử đổi 4 DWG (R2018 và R10) sang DXF, đọc lại bằng `ezdxf` đều ổn; ghi `dwg-to-dxf-oda-converter.md`. Chưa tích hợp vào `src/` |
| 2026-11-09 11:00 | in_progress | Theo yêu cầu người dùng ('code lại một lượt dựa trên khung'): viết `src/cad2bim/{read,classify,segments,walls,elements,analyze}.py` + `config/classify.yaml`; mã cũ `build` giữ nguyên. Test: 162 passed (60 mới). Đánh giá trên kho bản vẽ thật (61 DXF, `out/eval/v2-real-3.json`): 61/61 chạy không lỗi; **26/61 file ra ≥1 phần tử** (tường 10693, cột 4066, cửa 1393, phòng 825, ống gió 5066, ống nước 2609, thiết bị 569, báo cháy 3172); đơn vị: 6 file `$INSUNITS` khai báo sai được sửa (insunits_conflict), 12 file đoán; thời gian trung vị 0,2 s, tối đa 16,4 s. 35 file 0 phần tử: 25 gần như rỗng (tờ Smith House), 10 có layer nhận ra nhưng cửa/cửa sổ vẽ bằng nét rời nên chưa nhận. Chưa có đáp án để kiểm đúng/sai; số phần tử chưa được xác minh (có thể thừa do hatch/nét họa tiết trên layer tường). Chưa nối pipeline GPKG, chưa ghi IFC, chưa làm `compare.py`/`synth.py` |
| 2026-11-09 09:47 | in_progress | Theo yêu cầu người dùng: viết `reports/report-2026-11-09-0947.md`. Ghép DXF đã chuyển (ODA) về cùng thư mục DWG gốc trong `samples/corpus_real/raw/` (91 DXF; `dxf/` giữ nguyên 61) và cập nhật `MANIFEST.csv` (93 → 153 dòng). `HVAC_DRAWING_LIST.dwg` ODA không chuyển được (AcDbProxyObject không ép sang AcDbMLeaderStyle; thử ACAD2007/2018, audit 0/1), người dùng bảo bỏ qua. Đánh giá `out/eval/v2-real-5.json` trên 91 file: 91/91 không lỗi, 31 file có ≥1 phần tử; số phần tử đếm trùng vì các bản `dwg_DU_*`/`dxf_DU_*` của Smith House giống nhau. Ví dụ 0 phần tử: `5-star-hotel.dxf` (201 533 thực thể, nét tường nằm trên layer `5`/`Layer2`, bị bỏ vì layer lạ) |
| 2026-11-09 10:30 | in_progress | Viết `research/06-cad-to-bim/dxf-ifc-symbol-concordance.md` (bản quy ước đối chiếu mã nhóm/mẫu cấu trúc DXF ↔ IFC; thêm 2 dòng `sources.md`). Mới đối chiếu bằng `ezdxf` 1.4.5 và IfcOpenShell 0.9.0 cục bộ, **chưa** đối chiếu tài liệu gốc Autodesk/buildingSMART (đánh dấu trong tệp). Đọc mã từng hàm của `analyze.py`/`read.py`/`classify.py`/`segments.py`/`walls.py`; ghi nhận điểm yếu: nhận dạng chỉ theo tên layer; `INTERIOR-*` bị phân loại thành tường (đã chạy thử); `beam`/`stair`/`furniture` phân loại nhưng không tạo phần tử; cửa sổ chỉ từ INSERT; tường ghép cặp không nối góc ở cấp phần tử; không dựng phòng từ tường; lỗi hình học bị nuốt (`except Exception`) |
| 2026-11-09 10:50 | in_progress | Cầu nối thử `research/06-cad-to-bim/poc/v2_walls_to_ifc.py` (v2 `analyze()` → IfcWall + IfcDoor + IfcSpace) chạy trên `Apartment-413201.dxf`: 121 IfcWall (89 tường v2 tách theo đoạn), 16 IfcDoor (gán tường gần nhất, hướng suy đoán), 6 IfcSpace (suy từ lỗ kín của tường đệm + đóng khe 0,5 m; thô, thiếu phòng). **Lỗi đã phát hiện và sửa:** `unit.assign_unit` mặc định đặt đơn vị dài `.MILLI.` trong khi toạ độ là mét → toà nhà nhỏ đi 1000 lần; trước đó tôi đã báo sai '27,6 m' vì đo không áp dụng đơn vị. Đã sửa trong `v2_walls_to_ifc.py`; **`dxf_walls_to_ifc.py`, `ifc_opening_test.py` và `out/poc/sample-floor-1-walls.ifc` vẫn còn lỗi này (chưa sửa)**. Bonsai (chạy nền) nạp file mới được |
| 2026-11-09 11:40 | in_progress | Bản vẽ `3-bedroom-double-garage-two-storey-house-plan.dwg` là DWG vector hoá từ PDF (layer `PDF_Geometry`, `PDF_Solid Fills`; 3 mặt bằng + mặt đứng + mặt cắt cùng một modelspace). v2 ra 0 phần tử. Ghép cặp nét song song theo hình học (`poc/geom_only_walls_to_ifc.py`) **sai**: chỉ bắt đường gạch hatch (vạch chéo dài), 289 'tường' lộn xộn — bỏ. Tường thật là `SOLID` tô đặc → `poc/solid_fill_walls_to_ifc.py` (hợp SOLID, bỏ mảnh mỏng và dấu định vị 0,5 m): Plan-1 15 khối, Plan-2 16, Plan-3 0; vẽ chồng lên bản vẽ gốc thì khớp bằng mắt (ảnh dựng bằng matplotlib, chưa lưu vào repo). Khung mặt bằng khoanh tay bằng toạ độ. Xác nhận hai quy tắc phổ thông còn thiếu: tường tô đặc và nhiều bản vẽ trong một file |
| 2026-11-09 12:10 | in_progress | 3D: `Amsterdam arena` (DWG R2010 → DXF bằng ODA): toàn bộ là POLYLINE polyface (mỗi cái một tam giác, đỉnh không dùng chung) + LINE + 543 khối, layer tiếng Hà Lan; `$INSUNITS=1` (inch) nhưng kích thước hợp lý cho mét. Bản thử đầu mở khối tối đa 3 tầng nên **thiếu ~7 300 mặt (~16%) và ~8 000 LINE** — đã sửa bằng 8 tầng. Đính chính một con số tôi đã nói: thống kê `other_types` của v2 chỉ đếm thực thể trên layer đã nhận ra, nên '~700 thực thể 3D trong kho' là đếm thiếu; riêng `3d-site.dxf` có 2 885 `3DSOLID` (ACIS nhị phân, `ezdxf` chỉ trả byte thô). Kiểm so khớp diện tích bề mặt DXF với IFC: lệch 0,0% (trên cùng tập đã duyệt) |
| 2026-11-09 12:17 | in_progress | Đưa bộ đọc 3D vào `src/cad2bim/`: `read3d.py` (polyface, polygon mesh, 3DFACE, MESH, LINE, ARC/CIRCLE giữ chính xác, polyline làm phẳng, `thickness` → lăng trụ, mở khối 8 tầng, không bỏ layer lạ), `analyze3d.py` (`analyze3d()` → `Model3D`, đơn vị qua `resolve_units`, cảnh báo nếu kích thước < 10 m), `ifc3d.py` (`write_ifc3d()`: proxy theo layer, khung dây `Curve3D`, cung bằng `IfcIndexedPolyCurve`+`IfcArcIndex`), `config/classify.yaml` thêm `max_block_depth_3d`, `max_items_3d`. Test mới `tests/test_v3_read3d.py` (11); **toàn bộ 177 passed**. Trên arena: 17 438 polyface, 45 526 mặt, 52 423 đường (51 933 LINE, 245 polyline 3D), 245 cung chính xác (216 ARC + 29 CIRCLE), `errors=0`, 7,3 s; Bonsai nạp `out/poc/amsterdam-arena/arena-v3.ifc` được. **Chưa làm:** `3DSOLID`/`BODY`/`REGION` (ACIS), phân loại ngữ nghĩa, giữ màu/vật liệu/cấu trúc khối, kiểm từng toạ độ độc lập. **Hạn chế đã biết:** đơn vị của arena vẫn bị hiểu là inch (bbox ±7,5 m; kiểm 'nhỏ bất thường' ngưỡng 10 m không bắt được vì rộng 15 m). Chưa commit (chờ người dùng) |
| 2026-11-09 15:20 | in_progress | Theo chỉ đạo của mentor (đầu vào chỉ là CAD 2D chi tiết; chuyển IFC ít mất thông tin nhất, rồi làm giàu và vẽ thêm) và thảo luận với chủ dự án: bổ sung **luồng AI agent** vào `research/06-cad-to-bim/cad2bim-framework-design.md` mục 8 và viết `reports/report-2026-11-09-1520.md`. Chốt: (1) AI đọc ảnh vẽ từ DXF có nhãn handle để lấy ngữ cảnh, hình học và ghi IFC vẫn là mã xác định; (2) thêm lớp nguồn 2D lossless (Pset `CAD_Source`) và vòng critic; (3) mô hình diễn giải trung gian mở rộng `BimElement` thay cho CSDL đồ thị riêng; (4) Cost/Asset là module phụ sau IFC, đơn giá/thuộc tính ở tệp cấu hình. **Chưa viết mã** cho luồng này; thứ tự: `ifc2d.py` lossless + kiểm bảo toàn, rồi POC render + agent đọc. Ghi 5 nguồn mới vào `sources.md` (đọc từ kết quả tìm kiếm, chưa kiểm). Chưa commit (chờ người dùng) |

## Blocker / câu hỏi mở
- **(2026-11-09) Luồng AI agent**: chưa đo được mức AI hiểu ngữ cảnh từ ảnh vẽ DXF (cần POC); cần hỏi mentor: loại bản vẽ "chi tiết" (kiến trúc/kết cấu/MEP), mức làm giàu mong muốn, có bản vẽ thật không; có cần truy vấn nhiều dự án (khi đó mới cân nhắc CSDL đồ thị).
- **(2026-11-09) Quy tắc phổ thông còn thiếu ở v2 2D** (đã xác nhận trên dữ liệu thật): tường vẽ bằng `SOLID`/hatch tô đặc; nhiều bản vẽ (mặt bằng/đứng/cắt) trong một modelspace; dựng phòng từ tường; host + lỗ mở cho cửa; nhận diện không phụ thuộc tên layer; `beam`/`stair`/`furniture` chưa tạo phần tử; `INTERIOR-*` bị coi là tường.
- **(2026-11-09) 3D**: `3DSOLID`/`BODY`/`REGION` là ACIS nhúng, cần bộ đọc ACIS hoặc đổi định dạng trước; đơn vị khi `$INSUNITS` sai mà kích thước vẫn hợp lý không phát hiện được (arena).
- **(2026-11-09) Lỗi đơn vị `.MILLI.` còn ở** `poc/dxf_walls_to_ifc.py`, `poc/ifc_opening_test.py`, `out/poc/sample-floor-1-walls.ifc` (chưa sửa).
- **Chưa có dữ liệu đánh giá phù hợp** (corpus mẫu đã bị xóa 2026-11-09 theo yêu cầu người dùng). Cần: (1) vài bản vẽ DXF/DWG dự án thật do người dùng cung cấp, và/hoặc (2) bộ mặt bằng cắt từ mô hình IFC mở có đáp án (giấy phép từng bộ chưa kiểm). M0 còn thiếu bước này trước khi đo M1/M2 một cách đáng tin.
- **DWG**: đã giải quyết một phần (2026-11-09): ODA File Converter 27.10.0.0 cài ở `~/apps/ODAFileConverter/`, đổi DWG R10 và R2018 sang DXF R2018 (xem `research/06-cad-to-bim/dwg-to-dxf-oda-converter.md`). Còn lại: phần mềm đóng nguồn, **không đóng gói/phân phối**; chưa đọc điều khoản đầy đủ; chưa kiểm độ trung thực với khối động/đối tượng riêng.
- **Corpus nghiêng về nhà ở/phòng khám cỡ nhỏ**: chỉ số chủ yếu đo độ bền/độ phủ; cần bản vẽ thật của dự án để hiệu chỉnh luật và dung sai.
- **`Obj` hay `BimElement`**: đề xuất giữ hai lớp bằng adapter để không phá đường GPKG/IMDF; cần xác nhận trước M1.
- **Mục tiêu "≥ 15/78" ở M1** là con số đề xuất, chưa có cơ sở thống kê; điều chỉnh sau khi lập danh sách bí danh layer thực tế từ PROFILE.csv.
