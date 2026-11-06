# 4D — Tiến độ thi công

- **Câu hỏi nghiên cứu**: Tiến độ được gắn vào cấu kiện 3D thế nào trong IFC và công cụ nào làm việc đó?
- **Kết luận ngắn**: Mẫu chuẩn IFC là `IfcWorkSchedule` → `IfcTask` (thời gian qua `TaskTime`) → `IfcRelAssignsToProcess` → sản phẩm (IfcProduct). Công cụ: Navisworks TimeLiner, Synchro, MS Project/Primavera P6, IfcOpenShell Ifc4D/Bonsai. Cách nối ở công cụ độc quyền thường bằng selection set/tên, không phải GUID.
- **Độ tin cậy**: trung bình — cấu trúc entity xác nhận từ trang schema qua kết quả tìm kiếm; mẫu đầy đủ chưa đối chiếu ví dụ chính thức.

## Chi tiết

### Dữ liệu thêm ở 4D
Task (tên, trạng thái, mốc), thời lượng/ngày bắt đầu–kết thúc, lịch làm việc, quan hệ task–cấu kiện (cấu kiện nào được lắp/phá/tạm trong task nào), nhóm WBS.

### Class IFC
- `IfcTask` là subtype của `IfcProcess`; có các thuộc tính như Status, WorkMethod, IsMilestone, Priority, TaskTime. Thời lượng (ScheduleDuration) nằm trong TaskTime.
- `IfcWorkSchedule`: lịch của một work plan, có StartTime, FinishTime (tuỳ chọn); điều khiển tập task/resource qua `IfcRelAssignsToControl`.
- `IfcRelAssignsToProcess`: gán một hay nhiều đối tượng (RelatedObjects) vào quá trình (RelatingProcess), có QuantityInProcess tuỳ chọn. Task có inverse `OperatesOn`.
- Cảnh báo phiên bản: một trang IFC4_2 ghi thuộc tính RelatingProcess "deprecated, gán NIL", trong khi bản IFC4/IFC4.3 khác vẫn hiển thị là dùng bình thường — chưa xác minh; cần kiểm tra theo phiên bản schema đích trước khi viết exporter.
- Mẫu nối "sản phẩm ↔ task" kiểu Navisworks/Synchro không phải IFC thuần.

### Công cụ
- Navisworks TimeLiner: đọc MS Project (MPX); Primavera cần P6 cài tại máy hoặc P6 Web Services (tài liệu bản 2021, bản mới có thể khác). Nối task với model bằng selection set; một diễn đàn 2009 nói tự động gắn khi tên selection set trùng tên task (nguồn cũ, cộng đồng).
- Synchro 4D: nền tảng chuyên 4D/logistics (nguồn so sánh blog, mức xác minh thấp).
- IfcOpenShell `Ifc4D`: tiện ích chuyển đổi giữa IFC và MS Project / PowerProject / Oracle P6; commit gần đây cho thấy importer MS Project và P6 dùng chung một generator (calendars, status, task times, resources). Bonsai có giao diện 4D (chi tiết chưa xác minh).

### Quy trình dữ liệu
Input: mô hình 3D (IFC với GlobalId) + tiến độ (MPP/XER/MPX) → xử lý: tạo IfcTask + TaskTime, gán sản phẩm → output: IFC có schedule hoặc bảng task–GUID để animate.

## Liên quan đến pipeline CAD → BIM → GPKG
- Có thể xuất bảng `task_assignment(task_id, start, finish, global_id)` cạnh các layer GPKG; QGIS Temporal Controller có thể hiển thị theo thời gian nếu feature có trường thời gian. Đề xuất, chưa kiểm chứng. Không cần cho phạm vi indoor mapping tối thiểu.

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
