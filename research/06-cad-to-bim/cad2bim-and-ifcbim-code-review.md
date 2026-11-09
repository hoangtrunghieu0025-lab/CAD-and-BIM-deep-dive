# Đọc mã hai repo: alvin528/CAD2BIM và Kevinscsatoshi/ifcbim

- **Câu hỏi nghiên cứu**: Hai repo người dùng gửi thêm có phần mã nào ta tận dụng được cho converter DXF → IFC của dự án?
- **Kết luận ngắn**: Cả hai đều dựng hình học dạng **mesh** (không phải `IfcExtrudedAreaSolid`) và không có nối góc tường. **ifcbim** là DXF → IFC theo layer đúng kiểu ta cần, nhưng **không có giấy phép** nên chỉ học ý tưởng. **alvin528/CAD2BIM** (Apache-2.0) không đọc DXF; nó nhận một `model-spec.json` do LLM/người viết rồi xuất IFC, nhưng có sẵn phần ta chưa có: lỗ mở cửa (`voids`/`fills`), Pset truy vết nguồn, kiểm tra đa giác. Kiến trúc "tách nhận dạng ngữ nghĩa khỏi ghi file" của nó khớp khoảng trống Geometry → Semantic.
- **Độ tin cậy**: trung bình đến cao cho nội dung mã (đã clone, đọc README và các file chính, 2026-11-08). **Chưa chạy mã của hai repo** (mã ngoài, không chạy). Một lệnh đọc dữ liệu repo đã bị hệ thống chặn nên tôi chỉ dùng công cụ đọc file. Khẳng định "không có nối góc/lỗ mở" là từ đọc mã, chưa kiểm bằng chạy.

## Chi tiết

### 1. Kevinscsatoshi/ifcbim ("CAD2BIM Studio")
- **Là gì**: ứng dụng web FastAPI, tải DXF lên → IFC4 + bản xem 3D. 27 commit, commit đầu 2026-03-17 và cuối 2026-03-17 theo `git log` (clone nông, 50 commit). **Không có file LICENSE**, README không nêu giấy phép → mặc định bản quyền thuộc tác giả, **không sao chép mã**.
- **Phụ thuộc**: `ezdxf==1.4.2`, `ifcopenshell==0.8.4.post1`. Chỉ nhận DXF (DWG bị tắt).
- **Quy trình**: `modules/dxf_parser.py` (253 dòng) → `modules/layer_mapper.py` (150) → `app/services/ifc_builder.py` (445).

| Phần | Làm gì | Đánh giá cho ta |
|---|---|---|
| `dxf_parser` | Đọc LINE, LWPOLYLINE, POLYLINE, CIRCLE, ARC, INSERT (kèm `ATTRIB`), TEXT/MTEXT bằng `ezdxf` vào dataclass `CadEntity`; đọc `$INSUNITS`, layer (tắt/đóng băng), block | Cấu trúc dữ liệu gọn, ta đã có tương đương trong `src/ingest/dxf.py`. **Bỏ qua bulge** của polyline cong, **không áp phép biến đổi block** khi đọc entity trong block |
| `layer_mapper` | Bảng regex tên layer → `IFCClassMapping` (class, cao, dày, vật liệu, Pset mặc định); có nhiều ngôn ngữ (Anh, Đức, Pháp, Tây Ban Nha, Trung); xuất/nạp cấu hình JSON; layer không khớp → `IfcBuildingElementProxy` | Ý tưởng khớp `config/layer_mapping.yaml` của ta. **Regex không neo** nên dễ khớp nhầm (ví dụ `col` khớp "color", `floor` thành `IfcSlab`); ta nên giữ cách neo `^A-WALL(-.*)?$` hiện có |
| `ifc_builder` | Mỗi entity thành **một** phần tử IFC; hình học là mesh (`add_mesh_representation`) từ lăng trụ đoạn thẳng, footprint, trụ; dùng `ABSTRACT_CLASS_FALLBACKS` (`IfcDistributionElement` là lớp trừu tượng → đổi sang `IfcFlowSegment`); gán vật liệu (có bộ nhớ đệm); mỗi phần tử có Pset `CAD2BIM_Metadata` (`SourceLayer`, `SourceEntity`, `GeometryStrategy`, `MaterialGuess`, kích thước mặc định…); đếm entity bị bỏ qua | **Điểm hay**: Pset truy vết nguồn và báo cáo entity bỏ qua. **Điểm yếu**: INSERT và TEXT chỉ thành hộp đánh dấu 0,25 m (cửa không có hình cửa, không có lỗ mở); mỗi đoạn tường là một mesh riêng, không nối góc; chữ trên layer cửa cũng thành "cửa"; `unitless` được coi là mm |
| Kiểm thử | `tests/test_pipeline.py` tạo DXF bằng `ezdxf` rồi chạy toàn bộ pipeline, đọc lại IFC | Cách kiểm thử tự đóng gói này ta nên làm theo |

### 2. alvin528/CAD2BIM
- **Là gì**: "Agent Skill" cho trợ lý lập trình có thị giác (Codex, Claude Code…) cùng bộ xuất tất định. LLM/VLM đọc bản vẽ (DXF/PDF/ảnh), tự viết `model-spec.json`; bộ xuất chỉ biên dịch spec thành IFC/GLB/OBJ/STL, **không quyết định ngữ nghĩa**. README nói rõ "no OCR, no CV detector, no rule-based semantic recognizer, no fixed CAD-layer mapping". Apache-2.0. 6 commit, ghi "v0.1 concept preview" (2026-07-27). Trang demo là bản phát lại có kịch bản, không chuyển đổi thật; mẫu là căn hộ tổng hợp ~76 m² (23 tường, 4 cửa, 6 cửa sổ, 7 phòng). Không có số liệu độ chính xác; chưa có thử nghiệm trên bản vẽ thật.
- **Phụ thuộc**: `ifcopenshell>=0.8.4,<0.9` — **không khớp** bản `0.9.0.post1` của ta; tương thích chưa kiểm.
- **Phần đáng học trong `exporter.py` (1268 dòng)**:

| Phần | Nội dung | Dùng cho ta |
|---|---|---|
| Hợp đồng spec | `model-spec.json` với `levels`, `elements` (id, `ifc_class`, `level_id`, `geometry.kind` = `wall`/`extrusion`/`box`), mỗi phần tử kèm `claim_state`, `confidence`, `source_refs`, `assumption` | Mẫu cho **mô hình trung gian có truy vết và đánh dấu giả định**; khớp nhu cầu ghi rõ cao độ/độ dày là giả định |
| Lỗ mở | `add_feature` (IfcRelVoidsElement) và `add_filling` (IfcRelFillsElement) nối `IfcOpeningElement` với tường và cửa | **Phần ta còn thiếu** (POC chưa làm lỗ mở). Dùng đúng `ifcopenshell.api.feature` |
| Kiểm tra hình học | `_validate_simple_polygon`, `_segments_intersect`, `_triangulate_polygon` (kiểm đa giác đơn, không tự cắt, tam giác hoá) | Ý tưởng cho kiểm footprint phòng/sàn; ta đã có `shapely` nên có thể dùng `is_valid` |
| Truy vết | Pset `Pset_CAD2BIMTraceability` (`ElementId`, `SourceRefs`, `ClaimState`, `Confidence`, `Assumption`); GUID ổn định từ hạt giống (`_stable_ifc_guid`) | Ý tưởng cho Pset nguồn gốc và IFC tái lặp được (so sánh giữa các lần chạy) |
| Hình học | Tường = chính xác **2 điểm**, độ dày cố định; mesh `IfcPolygonalFaceSet`, không phải solid tham số; chỉ 13 class IFC cho phép | Không tận dụng; POC của ta dùng `create_2pt_wall` cho solid tham số |

### 3. Link arXiv
`arxiv.org/search/?query=CAD2BIM&searchtype=all` trả về **0 kết quả** ("produced no results"). Không có bài nào theo từ khoá này; các bài liên quan ở các note khác (ISARC 2021, arXiv 2306.01642, Cloud2BIM).

## Liên quan đến pipeline CAD → BIM → GPKG
- **Học ý tưởng, không chép mã**: ifcbim (không giấy phép). Từ alvin528/CAD2BIM (Apache-2.0) có thể tham khảo mã, nhưng nếu lấy nguyên đoạn phải giữ thông báo bản quyền và ghi nguồn; hiện **chưa cần**, vì phần cần là vài lệnh API công khai của IfcOpenShell.
- **Việc nên làm cho `ifc_writer.py`**:
  1. Mô hình trung gian có `source_refs`, `claim_state`, `assumption` cho mỗi phần tử (theo alvin528); nối vào `src/model.py`.
  2. Pset nguồn gốc (`SourceLayer`, `SourceEntity`, `Assumption`) như ifcbim, thêm vào bước enrich.
  3. Lỗ mở cửa bằng `feature.add_feature` + `add_filling`, kiểm trên mẫu `A-DOOR`.
  4. Báo cáo entity bị bỏ qua theo layer (ta đã có `out/unmatched_layers.csv`).
  5. Bài học tránh: regex không neo, `unitless` mặc định mm, INSERT thành hộp, cửa không có lỗ.
  6. Viết kiểm thử tự sinh DXF bằng `ezdxf`.
- Kiểm tương thích `ifcopenshell` 0.9 với `api.feature.add_feature`/`add_filling` trước khi dùng (bản ghi trong repo kia ghim `<0.9`).

## Nguồn
- [GitHub — Kevinscsatoshi/ifcbim](https://github.com/Kevinscsatoshi/ifcbim) — truy cập 2026-11-08 (clone và đọc `README.md`, `modules/`, `app/services/ifc_builder.py`, `tests/`)
- [GitHub — alvin528/CAD2BIM](https://github.com/alvin528/CAD2BIM) — truy cập 2026-11-08 (clone và đọc `README.md`, `pyproject.toml`, `exporter.py`, `references/model-spec-contract.md`)
- [CAD2BIM demo (GitHub Pages)](https://alvin528.github.io/CAD2BIM/) — truy cập 2026-11-08 (tóm tắt trang)
- [arXiv — tìm "CAD2BIM"](https://arxiv.org/search/?query=CAD2BIM&searchtype=all) — truy cập 2026-11-08 (0 kết quả)

## Câu hỏi còn mở
- Chạy thật hai repo trong môi trường cách ly để xác nhận hành vi (cửa, lỗ mở, nối góc): chưa làm.
- `add_feature`/`add_filling` có hoạt động đúng trên `ifcopenshell 0.9.0.post1` với tường từ `create_2pt_wall`: chưa kiểm.
- Ngày commit cuối thật của hai repo: `git log` chỉ cho thấy trong 50 commit đầu của clone nông.
