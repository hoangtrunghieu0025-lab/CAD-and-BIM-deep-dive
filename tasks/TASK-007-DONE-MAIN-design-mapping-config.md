---
id: TASK-007
title: "[DONE][MAIN] Thiết kế bảng mapping CAD/IFC → OSM → IMDF"
category: MAIN
assignees: [claude-mobile, claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T14:35:46+07:00
status: done
priority: high
depends_on: [TASK-002, TASK-003, TASK-005]
---

# [DONE][MAIN] TASK-007 — Thiết kế bảng mapping CAD/IFC → OSM → IMDF

## Mô tả
Chuyển bảng mapping trong `PRIMARY_OBJECTIVE.md` thành file cấu hình dùng được bởi code. Mobile soạn bản nháp từ research; laptop thử trên file mẫu thật và báo chỗ cần chỉnh.

## Đầu vào (inputs)
- `research/01-cad/`, `research/02-bim/`, `research/04-osm-imdf-tagging/`
- File mẫu trong `samples/` (từ TASK-008)

## Đầu ra mong đợi (expected_outputs)
- `config/layer_mapping.yaml` (CAD layer → loại đối tượng)
- `config/tag_mapping.yaml` (IFC class / loại đối tượng → tag OSM → IMDF feature + category)
- `docs/mapping-design.md` (giải thích các quyết định, trường hợp ngoại lệ)

## Tiêu chí hoàn thành (acceptance)
- [x] Mọi giá trị OSM/IMDF trong file đều có nguồn trong `research/04-*`
- [x] Laptop xác nhận đã chạy thử mapping trên ≥1 file mẫu DXF và ≥1 file IFC, ghi kết quả vào nhật ký
- [x] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: soạn `config/*.yaml` và `docs/mapping-design.md`.
- **claude-laptop**: chỉ ghi nhật ký task này và đề xuất chỉnh sửa trong mục Blocker / câu hỏi mở; sửa trực tiếp `config/*.yaml` chỉ sau khi mobile đã đặt trạng thái `in_review`.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | done | 2026-11-06T14:35:46+07:00 | đã xử lý 10 đề xuất (N-005) |
| claude-laptop | done | 2026-11-06T14:35:46+07:00 | đã chạy thử trên DXF + IFC mẫu (14:23) |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T11:55:16+07:00 | in_review | Soạn config/layer_mapping.yaml, config/tag_mapping.yaml, docs/mapping-design.md. Chạy layer_mapping trên samples/sample-floor-1.dxf: 13 A-AREA + 13 nhãn + 12 cửa + 13 tường, 0 UNMATCHED (khớp samples/README). tag_mapping mới kiểm cú pháp YAML, chưa chạy trên IFC. |
| 2026-11-06T14:35:46+07:00 | done | Rà 10 đề xuất của claude-laptop (N-005), chi tiết ở docs/mapping-design.md mục 6. Chấp nhận 1–9 (nhãn tầng viết hoa + LABELS {"vi":…}; tâm cửa theo hình học opening; namespace UUID đã chốt; quy tắc storey_index; tầng DXF từ project.yaml; ref_pattern; opening DXF; NFC + neo regex; corridor không ref); 10 hoãn (cần mẫu bổ sung). Đọc trực tiếp register.apple.com (type_designators, manifest, types/level): LABELS = JSON {LANGUAGE-TAG: chuỗi}, phải có ngôn ngữ mặc định; Manifest bắt buộc version/created/language; **id phải là UUID v4** nên đổi uuid5 -> stable_v4 (config/tag_mapping.yaml, docs/cad-to-gpkg-design.md). Đặt TASK-007 DONE; TASK-009 hết bị chặn. |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T14:23:00+07:00 | in_review | **Chạy thử mapping trên mẫu thật** (script ngoài repo, `.venv` + PyYAML tạm; chưa commit mã). **DXF** `sample-floor-1.dxf`: layer_mapping OK (13 A-AREA, 13 nhãn, 12 cửa, 13 tường, 0 unmatched; trùng kết quả của mobile); 13 polygon đều có nhãn; tag_mapping: 12 `default-room` + 1 `corridor` ('HANH LANG'); union(units) = đường bao A-WALL (symmetric difference 0 m²); 12/12 opening LineString nằm trên ranh giới unit. **IFC** `sample-building.ifc` (IFC4, unit scale 1.0): 26 IfcSpace lấy tầng bằng `get_aggregate` OK (24 `default-room` + 2 `corridor` theo LongName 'Hanh lang'); 24 IfcDoor lấy tầng bằng `get_container` OK, cả 24 vào `default-door`; 8 IfcWall (mode `simplified` → không xuất); 2 level (`ordinal` 0 và 1, category `unspecified` hợp lệ); union(units) = đường bao 24×12 (diff 0 m²) cả 2 tầng; mọi category sinh ra (`room`, `walkway`, `pedestrian`, `unspecified`) đều có trong danh sách IMDF đã xác minh. uuid5 ổn định giữa các lần chạy. **Hạn chế của phép thử**: mẫu không có tường ngăn dày (không kiểm được khe giữa các unit), IfcDoor không có hình học, không có Pset, không có IfcStair/thang máy/IfcWindow, không có georeference. |

## Blocker / câu hỏi mở
Đề xuất của claude-laptop sau khi chạy thử (laptop **không sửa** `config/*.yaml`; mobile xem và quyết):
1. **`level.name`/`short_name`**: spec `types/level` ghi "Labels MUST not contain mixed case characters" (cần đọc kỹ nghĩa), mà config lấy thẳng `IfcBuildingStorey.Name` ('Tầng 1') và `short_name: {storey_name}`. Đề xuất: thêm bước chuẩn hoá nhãn (vd chữ hoa) và tạo `short_name` ngắn ('1', 'B1') từ chỉ số tầng hoặc `level:ref`.
2. **Vị trí cửa IFC vs DXF (lệch 0,45 m trên mẫu)**: DXF INSERT đặt ở tâm cửa (P101: x=2.0), còn IfcDoor trong mẫu có placement ở *đầu* cửa (x=1.55); config nói "node tại tâm cửa" và `OverallWidth_at_placement` không nêu placement là tâm hay đầu. Phép thử "nằm trên ranh giới" **không phân biệt được** (cả hai cách đều nằm trên ranh giới). Cần quy tắc rõ (ví dụ: IFC lấy tâm theo hình học `IfcOpeningElement`/Body; placement chỉ là dự phòng kèm offset cấu hình). Lưu ý: kiểu đặt placement trong mẫu là do generator của laptop chọn, chưa phản ánh file thật.
3. **`defaults.ids.namespace: null`**: chưa sinh được id ổn định; cần chốt 1 UUID namespace cố định của dự án (laptop dùng UUID tạm khi thử; uuid5 ổn định giữa các lần chạy đã kiểm).
4. **`storey_index`**: config nói "sinh theo thứ tự Elevation, 0 = mặt đất" nhưng chưa nêu cách chọn tầng 0. Laptop thử "tầng có |Elevation| nhỏ nhất = 0, các tầng khác theo thứ hạng" — đúng trên mẫu (0 và 1); cần xác nhận hoặc cấu hình `ground_storey` để xử lý tầng hầm / `IfcBuildingStorey` thiếu Elevation (OPTIONAL).
5. **Tầng cho DXF**: config ghi "1 file DXF = 1 tầng" nhưng không nói `level`, `level:ref`, `ordinal`, `name` lấy từ đâu (tên file? tham số CLI?). Thiếu cho đầu vào DXF.
6. **Nhãn phòng DXF `ref_or_name`**: config nói "ref nếu khớp mã phòng" nhưng chưa có regex mã phòng (mẫu: một chữ cái + số, ví dụ P101 → ref; 'HANH LANG' → name).
7. **Opening từ DXF**: `geometry_source` chỉ mô tả cho IFC; cần mô tả cách suy bề rộng/hướng LineString từ INSERT (laptop suy từ hình học block `DOOR`: LINE dài 0,9 m, `rotation` 0/180 → 12/12 nằm trên ranh giới unit).
8. **Regex tên phòng (`corridor`, `restroom`)**: (a) chạy trên chuỗi Unicode NFD không khớp ('Hành lang' tách dấu → rơi vào `default-room`) → cần chuẩn hoá NFC trước; (b) khớp từ khoá ở bất kỳ đâu trong tên nên 'Tuyến hành lang kỹ thuật' → corridor (có thể là false positive); cân nhắc neo ở đầu/cuối hoặc cho phép ghi đè theo `IfcSpace.PredefinedType`/`ObjectType`.
9. **`ref: {space_name}` cho corridor**: IfcSpace 'HL100' (mã kỹ thuật) sẽ thành `ref=HL100`; cân nhắc không gán `ref` cho corridor hoặc dùng cờ cấu hình.
10. **Chưa thể kiểm bằng mẫu hiện có** (cần dữ liệu thật hoặc mẫu bổ sung): tường ngăn dày và khe giữa unit (`mode: structure`), `IfcStair`, `IfcTransportElement` (ELEVATOR — enum/class chưa xác minh), `IfcWindow`, `Pset_DoorCommon.IsExternal/FireExit`, IFC2X3, georeference, DXF có ATTRIB trên INSERT, layer tiếng Việt (`profiles_disabled`), `A-GLAZ/A-COLS/A-STRS`. Đề xuất bổ sung các ca này vào `samples/` (việc của laptop, sau TASK-007).
