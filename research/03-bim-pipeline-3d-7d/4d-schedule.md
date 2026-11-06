# 4D — Tiến độ thi công

- **Câu hỏi nghiên cứu**: Tiến độ được gắn vào cấu kiện 3D thế nào trong IFC và công cụ nào làm việc đó?
- **Kết luận ngắn**: Mẫu chuẩn IFC là `IfcWorkSchedule` → `IfcTask` (thời gian qua `TaskTime`) → `IfcRelAssignsToProcess` → sản phẩm (IfcProduct). Công cụ: Navisworks TimeLiner, Synchro, MS Project/Primavera P6, IfcOpenShell Ifc4D/Bonsai. Cách nối ở công cụ độc quyền thường bằng selection set/tên, không phải GUID.
- **Độ tin cậy**: cao cho cấu trúc entity (kiểm bằng schema bundled của `ifcopenshell 0.9.0.post1`, TASK-012); phần công cụ độc quyền (Navisworks, Synchro, P6) vẫn **chưa xác minh**.

## Chi tiết

### Dữ liệu thêm ở 4D
Task (tên, trạng thái, mốc), thời lượng/ngày bắt đầu–kết thúc, lịch làm việc, quan hệ task–cấu kiện (cấu kiện nào được lắp/phá/tạm trong task nào), nhóm WBS.

### Class IFC
- `IfcTask` ⊂ `IfcProcess`; thuộc tính IFC4/4.3: `Status`, `WorkMethod`, `IsMilestone` (REQUIRED), `Priority`, `TaskTime` (OPTIONAL), `PredefinedType` (**đã xác minh**). `IfcTaskTime` ⊂ `IfcSchedulingTime` gồm `DurationType`, `ScheduleDuration`, `ScheduleStart`, `ScheduleFinish`, `EarlyStart/Finish`, `LateStart/Finish`, `FreeFloat`, `TotalFloat`, `IsCritical`, `StatusTime`, `ActualDuration/Start/Finish`, `RemainingTime`, `Completion` (tất cả OPTIONAL).
- `IfcWorkSchedule` ⊂ `IfcWorkControl`; `IfcWorkControl` có `CreationDate` (REQUIRED), `StartTime` (**REQUIRED**), `FinishTime` (OPTIONAL), `Duration`, `TotalFloat`, `Creators`, `Purpose` (OPTIONAL); `IfcWorkSchedule.PredefinedType` OPTIONAL. Điều khiển tập task/resource qua `IfcRelAssignsToControl` (`RelatingControl` REQUIRED). **Đã xác minh** (IFC4 và 4.3).
- `IfcRelAssignsToProcess`: gán một hay nhiều đối tượng (RelatedObjects) vào quá trình (RelatingProcess), có QuantityInProcess tuỳ chọn. Task có inverse `OperatesOn`.
- Phiên bản: trong schema `IFC4` và `IFC4X3_ADD2` đi kèm ifcopenshell, `IfcRelAssignsToProcess.RelatingProcess` là **REQUIRED** (không deprecated); `QuantityInProcess` OPTIONAL. Nghi vấn "deprecated ở IFC4x2" **chưa xác minh** (schema IFC4x2 không có trong ifcopenshell). Ở IFC2X3 `IfcTask` có `TaskId`, `IsMilestone`, không có `IfcTaskTime` (TaskTime thuộc IFC4+).
- Mẫu nối "sản phẩm ↔ task" kiểu Navisworks/Synchro không phải IFC thuần.

### Công cụ
- Navisworks TimeLiner: đọc MS Project (MPX); Primavera cần P6 cài tại máy hoặc P6 Web Services (tài liệu bản 2021, bản mới có thể khác). Nối task với model bằng selection set; một diễn đàn 2009 nói tự động gắn khi tên selection set trùng tên task (nguồn cũ, cộng đồng).
- Synchro 4D: nền tảng chuyên 4D/logistics (nguồn so sánh blog, mức xác minh thấp).
- IfcOpenShell `Ifc4D`: tiện ích chuyển đổi giữa IFC và MS Project / PowerProject / Oracle P6; commit gần đây cho thấy importer MS Project và P6 dùng chung một generator (calendars, status, task times, resources). Bonsai có giao diện 4D (chi tiết chưa xác minh).

### Quy trình dữ liệu
Input: mô hình 3D (IFC với GlobalId) + tiến độ (MPP/XER/MPX) → xử lý: tạo IfcTask + TaskTime, gán sản phẩm → output: IFC có schedule hoặc bảng task–GUID để animate.

## Liên quan đến pipeline CAD → BIM → GPKG
- Có thể xuất bảng `task_assignment(task_id, start, finish, global_id)` cạnh các layer GPKG; QGIS Temporal Controller có thể hiển thị theo thời gian nếu feature có trường thời gian. Đề xuất, chưa kiểm chứng. Không cần cho phạm vi indoor mapping tối thiểu.

## Kết quả xác minh (TASK-012, claude-laptop, 2026-11-06)
| Khẳng định | Kết quả | Cách kiểm |
|---|---|---|
| Chuỗi `IfcWorkSchedule` → `IfcTask` → `IfcTaskTime` → `IfcRelAssignsToProcess` → `IfcProduct` | ĐÚNG về cấu trúc entity | schema IFC4/IFC4X3_ADD2 |
| `IfcRelAssignsToProcess(RelatingProcess REQ, QuantityInProcess OPT)` | ĐÚNG | schema |
| Module `ifcopenshell.util.sequence`, `ifcopenshell.util.cost`, `ifcopenshell.api.sequence`, `ifcopenshell.api.cost`, `ifcopenshell.util.date` | TỒN TẠI (import được trong 0.9.0.post1). `api.sequence.recalculate_schedule` cần `networkx` (chưa cài) | `importlib` |
| Tên "Ifc4D"/"Ifc5D" như gói riêng | CHƯA XÁC MINH (gói `ifc4d`/`ifc5d` riêng không kiểm; chỉ xác nhận các module `api/util.sequence|cost`) | — |
| Pset cho task: `Pset_TaskCommon`, `Pset_TaskTimeCommon` | **KHÔNG TỒN TẠI** trong template IFC4 lẫn IFC4X3 (mục kiểm tra trong TASK-012); chỉ có `IfcTaskTime` làm thuộc tính | `util.pset.get_template` |
| Navisworks TimeLiner, Synchro, MS Project/P6 | CHƯA XÁC MINH (phần mềm thương mại) | — |

## Nguồn
- [IFC 4.3 — IfcRelAssignsToProcess](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcRelAssignsToProcess.htm) — truy cập 2026-11-06
- [IFC4.1 — IfcWorkSchedule](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_1/FINAL/HTML/schema/ifcprocessextension/lexical/ifcworkschedule.htm) — truy cập 2026-11-06
- [STEP Tools — IfcTask](https://www.steptools.com/stds/ifc/html/t_ifctask.html) — truy cập 2026-11-06
- [IFC 4.2 — IfcRelAssignsToProcess](https://standards.buildingsmart.org/IFC/DEV/IFC4_2/FINAL/HTML/schema/ifckernel/lexical/ifcrelassignstoprocess.htm) — truy cập 2026-11-06
- [Autodesk — Navisworks supported scheduling software (2021)](https://help.autodesk.com/cloudhelp/2021/ENU/Navisworks/files/GUID-1879F810-B3D3-419A-A138-0D2F02A8BFBA.htm) — truy cập 2026-11-06
- [IfcOpenShell mirror — ifc4d MS Project importer commit](https://dev.glassvision.dedyn.io/Glassvision/IfcOpenShell/src/commit/beb0db89e50297504a8870f6f233b26d1d328d1b) — truy cập 2026-11-06

## Câu hỏi còn mở
- Cấu trúc IfcTask/IfcTaskTime đầy đủ và `Pset_TaskCommon` (chưa đọc được trang chính thức).
- Tình trạng deprecated của RelatingProcess ở IFC4.2 so với 4.3.
- Bonsai 4D hỗ trợ tới mức nào; Synchro có export IFC schedule không.
