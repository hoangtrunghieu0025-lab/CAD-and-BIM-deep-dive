# tasks/ — nhận việc

Mỗi task là **một file** `tasks/TASK-<NNN>-<STATUS>-<CATEGORY>-<slug>.md` (NNN: 001, 002… tăng dần; slug chữ thường không dấu, gạch ngang). Ví dụ: `TASK-010-BLOCKED-MAIN-implement-pipeline.md`.
Dùng mẫu `tasks/_template.md`. **Xem nhanh toàn bộ task và trạng thái:** `python3 tasks/list.py` (hoặc nhìn tên file).

## 1. Quy ước tên và tiêu đề (BẮT BUỘC)

Trạng thái và category xuất hiện ở **bốn chỗ**, luôn phải khớp nhau:

| Chỗ | Dạng |
|---|---|
| Tên file | `TASK-010-BLOCKED-MAIN-implement-pipeline.md` |
| Trường `title` (frontmatter, có nháy kép) | `title: "[BLOCKED][MAIN] Cài đặt pipeline DXF/IFC → GPKG và test"` |
| Dòng `# ` đầu thân file | `# [BLOCKED][MAIN] TASK-010 — Cài đặt pipeline DXF/IFC → GPKG và test` |
| Trường `status`, `category` (frontmatter) | `status: blocked`, `category: MAIN` — **đây là nguồn sự thật** |

**Cách đổi trạng thái (một lệnh):** sửa `status:` (và `updated_at`, bảng "Tổng quan", nhật ký) trong file, rồi chạy `python3 tasks/list.py --sync`. Lệnh tự cập nhật tên file (bằng `git mv`), `title` và dòng `#`. Không đổi tay ba chỗ kia.

**Dẫn chiếu task bằng ID** (`TASK-010`), không dẫn bằng tên file, vì tên file đổi theo trạng thái.

**Category** (đặt một lần khi tạo task, ghi vào trường `category` trong frontmatter, ít khi đổi):

| Category | Ý nghĩa | Ví dụ |
|---|---|---|
| `MAIN` | Việc nằm trên lộ trình chính để đạt `PRIMARY_OBJECTIVE.md` | nghiên cứu, spec, pipeline, kiểm tra QGIS |
| `FIX` | Sửa sai, xác minh lại, giải quyết vấn đề phát sinh từ task khác. Ghi rõ task gốc trong mục Mô tả | xác minh lại nghiên cứu (TASK-012) |
| `SIDE` | Việc phụ, **không chặn** task `MAIN` nào; làm khi rảnh | cài thêm công cụ GUI (TASK-013) |

**Trạng thái** (viết hoa, phải **khớp đúng** trường `status` ở frontmatter): `TODO` · `IN_PROGRESS` · `IN_REVIEW` · `BLOCKED` · `DONE` · `CANCELLED`.

- `python3 tasks/list.py` (không tham số) kiểm tra tên file, `title`, dòng `#` khớp `status`/`category`, giá trị hợp lệ và không trùng ID; chạy trước khi commit, phải không có cảnh báo.
- Vì tên file đổi theo trạng thái, **chỉ bên làm task (assignee) mới đổi trạng thái**. Task giao cho cả hai bên thì thống nhất ai đổi, và `git pull --rebase` trước khi đổi để tránh xung đột đổi tên.

## 2. Quy tắc làm việc
1. **Nhận việc**: đầu phiên làm việc (sau Bước 0 trong `AGENTS.md`), chạy `python3 tasks/list.py`, lọc task có tên mình trong `assignees` và chưa `DONE`/`CANCELLED`. Task `FIX` ưu tiên hơn `MAIN` khi nó chặn task `MAIN`; `SIDE` làm sau cùng.
2. **Phân công** (`assignees`): `[claude-mobile]`, `[claude-laptop]` hoặc cả hai. Task chia việc cho cả hai thì mỗi bên làm phần trong mục "Phạm vi từng bên".
3. **Quyền sửa**: mọi agent có tên trong `assignees` được sửa file task. Để tránh xung đột git:
   - Phần đầu (frontmatter, mô tả, tiêu chí) chỉ sửa khi cần và nói rõ trong commit.
   - **Tiến độ**: mỗi bên chỉ ghi vào mục **của mình**; nhật ký chỉ **thêm dòng mới ở cuối**, không sửa dòng cũ.
4. **Luồng trạng thái** (`status` tổng, và trạng thái của từng bên): `todo` → `in_progress` → `in_review` → `done`; ngoài ra `blocked` (kèm lý do và bên chặn trong mục Blocker) và `cancelled`.
5. Cập nhật `updated_at` (giờ GMT+7, ví dụ `2026-11-06T10:30:00+07:00`; lấy bằng `TZ=Asia/Ho_Chi_Minh date +%Y-%m-%dT%H:%M:%S+07:00`) mỗi lần sửa; commit + push ngay (`git pull --rebase origin main` trước).
6. Task `done` thì giữ nguyên file (không xoá) để làm lịch sử.

## 3. Tạo task mới
- **Chọn số:** sau `git pull --rebase origin main`, lấy số lớn nhất trong `tasks/` cộng 1. Nếu rebase báo trùng ID với task bên kia vừa đẩy, bên chưa push **đổi sang số kế tiếp** (đổi tên file, trường `id`, rồi chạy `list.py --sync`; sửa mọi chỗ dẫn chiếu trong task của mình). `list.py` báo trùng ID.
- **Chọn category** theo bảng ở mục 1. Task `FIX` ghi task/vấn đề gốc ngay đầu mục Mô tả.
- Copy `_template.md` thành `TASK-NNN-TODO-<CATEGORY>-<slug>.md`, điền frontmatter (có `category`), rồi chạy `python3 tasks/list.py --sync` để `title` và dòng `#` đúng dạng.

## 4. Phụ thuộc
- Trường `depends_on` liệt kê task phải `done` trước khi bắt đầu; chưa xong thì đặt `blocked` và ghi lý do, hoặc làm task khác. `list.py` hiển thị các task còn chờ (cột cuối).
