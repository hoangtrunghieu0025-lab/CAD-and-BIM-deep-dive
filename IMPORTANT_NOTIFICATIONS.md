# ⚠️ IMPORTANT NOTIFICATIONS — THÔNG BÁO QUAN TRỌNG CHO MỌI AGENT

> Agent nào cũng phải đọc file này ngay sau Bước 0 trong `AGENTS.md`.

## CÁCH GHI THÔNG BÁO (BẮT BUỘC)

1. **Thêm thông báo mới lên ĐẦU danh sách** (ngay dưới dòng `---` đầu tiên bên dưới). **Không sửa, không xoá** thông báo cũ; muốn đính chính thì viết thông báo mới và dẫn chiếu thông báo cũ theo tiêu đề.
2. **Dòng tiêu đề** theo đúng mẫu, có **ngày + giờ + phút theo giờ Việt Nam (múi giờ Asia/Ho_Chi_Minh, UTC+7)**:
   ```
   ## [YYYY-MM-DD HH:MM GMT+7] <biểu tượng mức độ> TIÊU ĐỀ VIẾT HOA NGẮN GỌN
   ```
   Lấy giờ bằng lệnh `TZ=Asia/Ho_Chi_Minh date +"%Y-%m-%d %H:%M"` (đừng đoán giờ; máy cloud chạy giờ UTC nên không dùng `date` trần). Ví dụ: `## [2026-11-06 10:19 GMT+7] 🔴 MẠNG CỦA CLOUD SESSION BỊ GIỚI HẠN`
3. **Mức độ**: 🔴 CAO (ảnh hưởng độ tin cậy/việc đang làm của agent khác, phải đọc trước khi làm tiếp) · 🟡 TRUNG BÌNH (nên biết) · 🟢 THÔNG TIN (tham khảo).
4. **Thân thông báo** có các mục sau, theo thứ tự:
   - `- **Người gửi**:` `claude-mobile` hoặc `claude-laptop`
   - `- **Gửi lúc**:` ngày giờ giờ Việt Nam đầy đủ, ví dụ `2026-11-06 10:19 GMT+7`
   - `- **Gửi cho**:` `tất cả` / `claude-mobile` / `claude-laptop`
   - `- **Mức độ**:` như mục 3, kèm lý do ngắn
   - `### ĐÃ XẢY RA GÌ` · `### ĐÃ XỬ LÝ GÌ` · `### YÊU CẦU ĐỐI VỚI TỪNG AGENT` · `### KHI NÀO THÔNG BÁO NÀY HẾT HIỆU LỰC`
5. **Không ghi** email, mật khẩu, token hay thông tin cá nhân.
6. Sau khi ghi: `git pull --rebase origin main`, commit (message bắt đầu bằng `notify:`), rồi `git push origin main`.
7. **Đọc**: xử lý mọi thông báo 🔴 và 🟡 chưa hết hiệu lực trước khi làm task.

---

## [2026-11-06 10:19 GMT+7] 🔴 MẠNG CỦA CLOUD SESSION BỊ GIỚI HẠN — NGHIÊN CỨU CHƯA ĐƯỢC XÁC MINH VỚI NGUỒN GỐC

- **Người gửi**: claude-mobile
- **Gửi lúc**: 2026-11-06 10:19 GMT+7
- **Gửi cho**: tất cả (đặc biệt claude-laptop)
- **Mức độ**: 🔴 CAO (ảnh hưởng độ tin cậy của toàn bộ `research/`)

### ĐÃ XẢY RA GÌ
1. Môi trường cloud của `claude-mobile` (environment "Default") chạy ở chế độ **Limited network**: chỉ cho phép package registry (PyPI, npm…) và host của MCP server như GitHub; danh sách Allowed domains ban đầu **trống**.
2. Vì vậy 4 researcher (TASK-002 → TASK-005) **không đọc được** các trang tài liệu gốc (lỗi DNS `ENOTFOUND`): OSM wiki, Apple IMDF, OGC GeoPackage, GDAL, QGIS docs, buildingSMART, IfcOpenShell docs, ezdxf docs. Chúng chỉ dùng được đoạn trích từ WebSearch và vài trang GitHub.
3. Hệ quả: các ghi chú trong `research/01-cad/`, `02-bim/`, `03-bim-pipeline-3d-7d/`, `04-osm-imdf-tagging/` có nhiều chỗ ghi **"chưa xác minh"**. `research/04-osm-imdf-tagging/imdf-feature-types.md` (cột bắt buộc, danh sách category) viết theo trí nhớ, và `qgis-import-notes.md` có độ tin cậy thấp.

### ĐÃ XỬ LÝ GÌ
- Đã thêm 10 host vào Allowed domains của environment "Default" của claude-mobile (đã kiểm tra truy cập được): `wiki.openstreetmap.org`, `register.apple.com`, `docs.ogc.org`, `www.geopackage.org`, `gdal.org`, `docs.qgis.org`, `standards.buildingsmart.org` (trả 403 do chặn bot — dùng `ifc43-docs.standards.buildingsmart.org` thay thế), `ifc43-docs.standards.buildingsmart.org`, `docs.ifcopenshell.org`, `ezdxf.readthedocs.io`.
- **CHƯA** chạy lại việc xác minh. Trạng thái các task 002–005: `in_review` (chưa `done`).

### ⚠️ ĐIỀU NÀY KHÔNG TỰ ÁP DỤNG CHO claude-laptop
`claude-laptop` dùng **tài khoản khác** nên có environment và chính sách mạng **riêng**; thay đổi trên là cấu hình tài khoản của claude-mobile và **không** chuyển sang laptop. Nếu laptop chạy trên máy local thì thường không bị giới hạn này, nhưng nếu laptop cũng chạy trong cloud session thì phải tự kiểm tra và tự cấu hình Allowed domains của tài khoản mình.

### YÊU CẦU ĐỐI VỚI TỪNG AGENT
**claude-laptop**
- **KHÔNG tin** các khẳng định kỹ thuật trong `research/` là đã kiểm chứng; chỗ ghi "chưa xác minh" phải được kiểm tra trước khi đưa vào code/config.
- Khi làm TASK-007/008/010, kiểm chứng bằng thực nghiệm trên máy mình (tên hàm `ifcopenshell`/`ezdxf`, `ogrinfo`, mở trong QGIS) và ghi kết quả vào nhật ký task.
- Đã biết bảng trong `PRIMARY_OBJECTIVE.md` mục 3.3 (bước 4) có sai/thiếu so với nguồn thứ cấp: cửa nội bộ thiếu `indoor=door`; cầu thang theo Simple Indoor Tagging là `stairs=yes` + `indoor=room|area` (không phải `highway=steps`); tường trong IMDF nhiều khả năng là `unit` với category vật liệu chứ không mặc định `fixture`; IMDF 1.0.0 có 16 feature type (thiếu `geofence`, `kiosk`, `relationship`, `section`, `manifest.json`); RTree của GeoPackage là extension (tự tạo khi dùng GDAL). **Chưa xác minh với spec gốc.** Đừng cứng hoá bảng cũ vào code.

**claude-mobile** (tôi)
- Chạy lại xác minh với nguồn gốc rồi cập nhật `research/`; sau đó mới đánh dấu 002–005 `done` và làm TASK-006, 007, 009.
- Chưa sửa `PRIMARY_OBJECTIVE.md` (chưa được chủ dự án cho phép).

### KHI NÀO THÔNG BÁO NÀY HẾT HIỆU LỰC
Khi claude-mobile thêm một thông báo mới phía trên ghi rõ "ĐÃ XÁC MINH" cho 4 thư mục research.
