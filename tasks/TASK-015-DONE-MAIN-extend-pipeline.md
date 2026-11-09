---
id: TASK-015
title: "[DONE][MAIN] Mở rộng pipeline: đối tượng chưa cài đặt và mẫu bổ sung"
category: MAIN
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T15:08:50+07:00
updated_at: 2026-11-09T07:00:37+07:00
status: done
priority: normal
depends_on: [TASK-010]
---

# [DONE][MAIN] TASK-015 — Mở rộng pipeline: đối tượng chưa cài đặt và mẫu bổ sung

## Mô tả
Điểm 7–8 trong mục Blocker của TASK-010: các phần spec chưa cài đặt vì thiếu mẫu hoặc ngoài T1–T20. Task này nhóm lại để làm sau khi TASK-010/011 xong, theo thứ tự ưu tiên của chủ dự án. Không chặn TASK-011.

## Đầu vào (inputs)
- `docs/cad-to-gpkg-design.md` (mục 4, 5, 6, 11), `config/tag_mapping.yaml`
- Mục Blocker của TASK-010

## Đầu ra mong đợi (expected_outputs)
- Mẫu bổ sung trong `samples/` (tường dày, `IfcStair`, thang máy, `IfcColumn`, `IfcWindow`, `Pset_DoorCommon`, IFC2X3, ATTRIB trên INSERT) kèm cập nhật `samples/README.md`
- Cài đặt, theo mức ưu tiên: (a) cầu thang/thang máy/cột → `unit`; (b) mode tường `structure`; (c) `opening.door` (type/material/automatic) và `display_point`; (d) `fixture`/`detail`; (e) control points (spec 6.3); (f) kiểm khe giữa unit bằng đường bao độc lập (`A-WALL`/`IfcWall`)
- Test mới cho từng mục, ghi vào nhật ký

## Tiêu chí hoàn thành (acceptance)
- [x] Mỗi mục (a)–(f) hoặc đã cài đặt có test, hoặc ghi lý do hoãn trong nhật ký
- [x] `pytest` qua toàn bộ, `check` 0 lỗi trên mẫu cũ và mẫu mới
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; ghi `src/`, `tests/`, `samples/`.
- **claude-mobile**: cập nhật spec/config khi laptop báo thiếu.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | done | 2026-11-09T07:00:37+07:00 | (a)–(f) có test, 102 test qua (nay 162 cùng test mới); đóng theo yêu cầu chủ dự án; chưa push (chủ dự án tự commit) |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T17:24:59+07:00 | in_progress | Nhận task (TASK-010 DONE, TASK-011 IN_REVIEW không chặn). Kế hoạch: (a) cầu thang/thang máy/cột → unit, trừ vùng đè khỏi unit phòng; (b) tường `structure`; (c) `opening.door` + `display_point`; (d) fixture/detail; (e) control points; (f) cảnh báo khe so với đường bao độc lập; mẫu bổ sung và test cho từng mục. |
| 2026-11-06T17:35:59+07:00 | in_review | **Cài đặt xong (a)–(f), 102 test qua (39 test mới), `check` 0 lỗi/0 cảnh báo trên 4 mẫu GPKG.** (a) cầu thang (`IfcStair`, DXF `A-STRS`), thang máy (`IfcTransportElement` ELEVATOR), cột (`IfcColumn`, `A-COLS`) → `unit` `stairs`/`elevator`/`column` với tag OSM theo `tag_mapping.yaml`; phần đè bị trừ khỏi unit ưu tiên thấp hơn (cột trừ khỏi hành lang → lỗ). (b) `options.wall_mode: structure` → một unit `structure` cho mạng tường mỗi tầng (`indoor=wall` + `area=yes` trong `osm_tags`), lấp khe 0,2 m giữa các phòng; mặc định vẫn `simplified`. (c) object `door` (`type`, `automatic`, `material`) từ `IfcDoor.OperationType` + `Pset_DoorCommon.HasDrive` và từ ATTRIB `TYPE`/`AUTOMATIC`/`MATERIAL` của block DXF, kiểm theo từ vựng IMDF (đọc từ spec); `display_point` cho unit/level/fixture. (d) bảng `fixture` (`IfcFurnishingElement`, `A-FURN`) và `detail` (`A-DETL`), xuất cả vào gói IMDF. (e) `georeference.control_points` (≥ 2 cặp, khớp bình phương tối thiểu, báo sai số; cảnh báo nếu > 0,1 m). (f) cảnh báo khe so với đường bao tường độc lập (DXF: polygon lớn trên layer tường; IFC: vành ngoài của hợp thân tường): wall_mode simplified cảnh báo 33,52 m², structure bằng 0, mẫu cũ không cảnh báo. Thêm: cửa dày tường được dịch lên ranh giới unit gần nhất (≤ 0,5 m) để qua kiểm B-open; IFC2X3 chạy được; ba nguồn tâm cửa IFC (opening, thân, placement) đều được test. Mẫu: `sample-building-extended.ifc`, `sample-building-ifc2x3.ifc`, `sample-floor-extended.dxf` + 3 project yaml (`samples/README.md`). Đã tự sửa `config/layer_mapping.yaml` (thêm `A-FURN`, `A-DETL`) và `config/tag_mapping.yaml` (thêm `fixture`, `detail`) — xem Blocker.
| 2026-11-09 07:00 | done | Đóng task theo yêu cầu của chủ dự án (ghi bởi claude-mobile). Tiêu chí 'Đã push lên main' để trống có chủ ý: chủ dự án tự commit/push. |

## Blocker / câu hỏi mở
Không có blocker. **Quyết định thiết kế do laptop tự đặt (mobile rà, đổi nếu không đồng ý) và việc cần cập nhật spec:**
1. **Config đã sửa trực tiếp** (chỉ thêm, không đổi mục cũ): `layer_mapping.yaml` thêm rule `fixture` (`A-FURN`) và `detail` (`A-DETL`); `tag_mapping.yaml` thêm `object_types.fixture` (`IfcFurniture`→ fixture `furniture`) và `detail`. Tên layer chỉ là gợi ý NCS/AIA, chưa đối chiếu.
2. **Khoá mới trong `project.yaml`**: `options.wall_mode` (`simplified` | `structure`, ghi đè `tag_mapping.object_types.wall.imdf.mode`) và `georeference.control_points: [{local: [x, y], world: [E, N]}, ...]` kèm `crs` (không cần `origin`).
3. **Ưu tiên khi unit chồng nhau**: cột > thang máy = cầu thang > tường > phòng; phần đè bị trừ khỏi unit ưu tiên thấp (spec cần ghi: IMDF yêu cầu unit không chồng).
4. **Tường**: polygon kín trên layer tường có bề ngang nhỏ nhất ≤ 1,0 m là thân tường; lớn hơn là đường bao toà nhà (`WALL_MAX_THICKNESS` trong `cad2bim`). Tường DXF vẽ bằng LINE (không dày) chỉ được đếm. Đường bao cho kiểm khe: DXF = polygon lớn nhất trên layer tường, nếu không có thì vành ngoài của hợp thân tường; IFC = vành ngoài của hợp `IfcWall`.
5. **Cửa dịch lên ranh giới unit** (tối đa 0,5 m, bỏ qua unit `structure`) để tường dày không làm cửa nằm lơ lửng giữa tường; `check` B-open vẫn kiểm cửa nằm trên ranh giới.
6. **Ánh xạ `door.type` từ IFC**: `*SWING*`→swinging, `SLIDING*`→sliding, `REVOLVING`→revolving, `ROLLINGUP`→shutter; `FOLDING*` và còn lại → null (chưa có ánh xạ chắc chắn). `automatic` từ `Pset_DoorCommon.HasDrive` (true/false, thiếu → null). `material` chỉ lấy từ ATTRIB DXF (IFC không có nguồn rõ ràng). Từ vựng IMDF: `type` 9 giá trị, `material` 4 giá trị (wood, glass, metal, gate), đã đọc từ spec; ghi chú research cũ ghi `door`/`unspecified` là sai, đã sửa.
7. **IFC**: nội thất lấy qua `IfcFurnishingElement` (có cả IFC2X3), thang máy chỉ khi `PredefinedType`/`OperationType` = ELEVATOR (thang cuốn bị bỏ kèm cảnh báo), `IfcWindow` chỉ đếm (IMDF không có feature cửa sổ).
8. **Chưa làm**: thang máy từ DXF (chưa có quy tắc layer), cột/cầu thang vẽ bằng INSERT (chỉ nhận polygon kín/HATCH), thang cuốn, GPKG nhiều toà nhà, kiểm khe cho GPKG ngoài (cần đường bao độc lập), `restroom` và `emergencyexit` vẫn `unverified`. Mẫu vẫn tự sinh, chưa có bản vẽ/IFC thật.
9. **Spec cần cập nhật** (`docs/cad-to-gpkg-design.md`, của mobile): mục 4 (carve, snap cửa, tường structure, fixture/detail), mục 6.3 (control points đã cài đặt), mục 5 (bảng `fixture`, `detail`, cột `door`, `display_point`), mục 10 (thêm test), mục 11 (xoá các dòng đã xong).
