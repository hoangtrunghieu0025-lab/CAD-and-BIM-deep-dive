# ⚠️ IMPORTANT_NOTIFICATIONS — THÔNG BÁO QUAN TRỌNG CHO MỌI AGENT

> Agent nào cũng phải đọc file này ngay sau Bước 0 trong `AGENTS.md`.
> File có 3 phần tách biệt: **PHẦN 1 – Cách ghi** · **PHẦN 2 – Mục lục** · **PHẦN 3 – Các thông báo** (mới nhất ở trên cùng).

---

# PHẦN 1 — CÁCH GHI THÔNG BÁO (BẮT BUỘC)

1. **Vị trí**: thêm thông báo mới vào **đầu PHẦN 3** (ngay dưới dòng `# PHẦN 3`) và thêm 1 dòng vào bảng PHẦN 2. Không sửa nội dung thông báo cũ. Chỉ được đổi dòng `Trạng thái` của thông báo cũ (ví dụ sang "Đã thay thế bởi N-003").
2. **Mã thông báo**: `N-001`, `N-002`, … tăng dần, không dùng lại. Mỗi thông báo có đúng **một** mã, và tiêu đề phải nói rõ việc gì (không đặt hai thông báo có tiêu đề gần giống nhau; thông tin cập nhật thì viết thông báo mới nêu "cập nhật N-xxx").
3. **Dòng tiêu đề**: `## N-<số> · [YYYY-MM-DD HH:MM GMT+7] · <biểu tượng mức độ> TIÊU ĐỀ VIẾT HOA`
4. **Giờ**: giờ Việt Nam. Lấy bằng `TZ=Asia/Ho_Chi_Minh date +"%Y-%m-%d %H:%M"` (máy cloud chạy giờ UTC; đừng đoán giờ).
5. **Mức độ**: 🔴 CAO (phải xử lý trước khi làm tiếp) · 🟡 TRUNG BÌNH (nên biết) · 🟢 THÔNG TIN (tham khảo).
6. **Thân thông báo** gồm đúng các mục sau, theo thứ tự:
   - Dòng thông tin: `Người gửi` · `Gửi lúc` · `Gửi cho` (`tất cả` / `claude-mobile` / `claude-laptop`) · `Mức độ` · `Trạng thái` (`Đang hiệu lực` / `Đã hết hiệu lực` / `Đã thay thế bởi N-xxx`)
   - `### ĐÃ XẢY RA GÌ` · `### ĐÃ XỬ LÝ GÌ` · `### YÊU CẦU ĐỐI VỚI TỪNG AGENT` · `### KHI NÀO HẾT HIỆU LỰC`
7. **Không ghi** email, mật khẩu, token hay thông tin cá nhân.
8. **Sau khi ghi**: `git pull --rebase origin main` → commit (message bắt đầu bằng `notify:`) → `git push origin main`.
9. **Khi đọc**: xử lý mọi thông báo 🔴 và 🟡 có `Trạng thái: Đang hiệu lực` trước khi làm task.

**Mẫu để sao chép** (chỉ là mẫu, KHÔNG phải thông báo thật; các giá trị trong `< >` phải thay):

```markdown
## N-<số> · [<YYYY-MM-DD HH:MM> GMT+7] · <🔴|🟡|🟢> <TIÊU ĐỀ VIẾT HOA>

- **Người gửi**: <claude-mobile|claude-laptop>
- **Gửi lúc**: <YYYY-MM-DD HH:MM> GMT+7
- **Gửi cho**: <tất cả|claude-mobile|claude-laptop>
- **Mức độ**: <🔴|🟡|🟢> <lý do ngắn>
- **Trạng thái**: Đang hiệu lực

### ĐÃ XẢY RA GÌ
### ĐÃ XỬ LÝ GÌ
### YÊU CẦU ĐỐI VỚI TỪNG AGENT
### KHI NÀO HẾT HIỆU LỰC
```

---

# PHẦN 2 — MỤC LỤC

| Mã | Giờ (GMT+7) | Mức | Gửi → nhận | Tiêu đề | Trạng thái |
|---|---|---|---|---|---|
| N-002 | 2026-11-06 10:41 | 🔴 | mobile → laptop | Nhờ claude-laptop làm TASK-012 (xác minh nguồn gốc) | Đang hiệu lực |
| N-001 | 2026-11-06 10:19 | 🔴 | mobile → tất cả | Mạng cloud bị giới hạn, nghiên cứu chưa xác minh | Đang hiệu lực (xem N-002) |

---

# PHẦN 3 — CÁC THÔNG BÁO (mới nhất ở trên cùng)

## N-002 · [2026-11-06 10:41 GMT+7] · 🔴 NHỜ claude-laptop LÀM TASK-012: XÁC MINH NGHIÊN CỨU VỚI NGUỒN GỐC

- **Người gửi**: claude-mobile
- **Gửi lúc**: 2026-11-06 10:41 GMT+7
- **Gửi cho**: claude-laptop
- **Mức độ**: 🔴 CAO (chặn TASK-006, 007, 009 vì nghiên cứu chưa xác minh)
- **Trạng thái**: Đang hiệu lực (cập nhật tiếp theo của N-001)

### ĐÃ XẢY RA GÌ
- Đã chạy vòng xác minh thứ hai cho TASK-002…005. Kết quả:
  - **TASK-002 (CAD)**: XÁC MINH ĐƯỢC phần lớn (~32 khẳng định) nhờ đọc tài liệu + mã nguồn `ezdxf` trên GitHub (`raw.githubusercontent.com/mozman/ezdxf`). Còn ~14 mục chưa xác minh (NCS/ISO 13567/BS 1192, quy ước layer Việt Nam, điều khoản ODA…).
  - **TASK-003 (IFC), TASK-004 (BIM 3D–7D), TASK-005 (OSM/IMDF/GPKG)**: **0 khẳng định được xác minh.** Các agent của claude-mobile chỉ có công cụ `WebFetch`, và công cụ này báo lỗi DNS (`ENOTFOUND`) với mọi host tài liệu dù đã thêm vào Allowed domains. Trong khi đó `curl` từ Bash của claude-mobile tới được `wiki.openstreetmap.org` và `ezdxf.readthedocs.io` (HTTP 200), còn `ifc43-docs.standards.buildingsmart.org` trả 403 (trang chặn bot).
- Quy ước: **không giả User-Agent trình duyệt hay dùng cách nào khác để vượt chặn bot.** Dùng nguồn công khai hợp lệ (GitHub, tải tài liệu/PDF được phép, trình duyệt thật của người dùng trên máy local).

### ĐÃ XỬ LÝ GÌ
- Tạo **TASK-012** (file `tasks/TASK-012-*-verify-research-sources.md`; tên file đổi theo trạng thái, tìm bằng `python3 tasks/list.py`) giao cho claude-laptop (xem file này để biết chi tiết, danh sách khẳng định cần kiểm, tiêu chí hoàn thành). [Đã sửa đường dẫn sau khi đổi quy ước đặt tên file task, được chủ dự án cho phép.]
- Ghi chú vòng 2 và log các URL đã thử nằm ở `research/02-bim/_sources.md`, `research/03-bim-pipeline-3d-7d/_sources.md`, `research/04-osm-imdf-tagging/_sources.md`, `research/04-osm-imdf-tagging/prd-corrections.md`.

### YÊU CẦU ĐỐI VỚI TỪNG AGENT
**claude-laptop**
- Nhận **TASK-012** (ưu tiên cao). Trong phạm vi task này, **claude-laptop ĐƯỢC PHÉP sửa** các file trong `research/02-bim/`, `research/03-bim-pipeline-3d-7d/`, `research/04-osm-imdf-tagging/` và `research/sources.md` (chỉ thêm dòng). Không sửa `PRIMARY_OBJECTIVE.md`.
- Với mỗi khẳng định: đọc nguồn gốc (hoặc chạy thực nghiệm bằng `ifcopenshell`/`ezdxf`/`ogrinfo`/QGIS), rồi sửa ghi chú và gắn **URL cụ thể + ngày truy cập** (GMT+7). Chỗ vẫn không kiểm chứng được thì giữ nhãn "chưa xác minh" và ghi lý do.
- Ghi tiến độ vào nhật ký TASK-012 (giờ GMT+7).

**claude-mobile**
- Không sửa `research/02..04` trong lúc claude-laptop làm TASK-012 (tránh xung đột). Chỉ làm TASK-006 phần CAD (đã xác minh tốt hơn) hoặc chờ.
- Khi TASK-012 `in_review`: rà lại, rồi mới đánh dấu 002–005 `done` và làm TASK-007, 009.

### KHI NÀO HẾT HIỆU LỰC
Khi TASK-012 ở trạng thái `done` và claude-mobile đăng thông báo mới ghi "ĐÃ XÁC MINH".

---

## N-001 · [2026-11-06 10:19 GMT+7] · 🔴 MẠNG CLOUD CỦA claude-mobile BỊ GIỚI HẠN, NGHIÊN CỨU CHƯA XÁC MINH

- **Người gửi**: claude-mobile
- **Gửi lúc**: 2026-11-06 10:19 GMT+7
- **Gửi cho**: tất cả (đặc biệt claude-laptop)
- **Mức độ**: 🔴 CAO (ảnh hưởng độ tin cậy của toàn bộ `research/`)
- **Trạng thái**: Đang hiệu lực (xem N-002 để biết việc xác minh đang giao cho ai)

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

### KHI NÀO HẾT HIỆU LỰC
Khi claude-mobile đăng thông báo mới ghi rõ "ĐÃ XÁC MINH" cho 4 thư mục research (dự kiến sau khi TASK-012 xong).
