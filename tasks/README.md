# tasks/ — nhận việc

Mỗi task là **một file** `tasks/TASK-<NNN>-<tieu-de-ngan>.md` (NNN: 001, 002… tăng dần; chữ thường không dấu, gạch ngang).
Dùng mẫu `tasks/_template.md`.

## Quy tắc
1. **Nhận việc**: đầu phiên làm việc (sau Bước 0 trong `AGENTS.md`), mở `tasks/`, lọc file có tên mình trong `assignees` và `status` chưa `done`/`cancelled`.
2. **Phân công** (`assignees`): `[claude-mobile]`, `[claude-laptop]` hoặc cả hai. Task chia việc cho cả hai thì mỗi bên làm phần trong mục "Phạm vi từng bên".
3. **Quyền sửa**: mọi agent có tên trong `assignees` được sửa file task. Để tránh xung đột git:
   - Phần đầu (frontmatter, mô tả, tiêu chí) chỉ sửa khi cần và nói rõ trong commit.
   - **Tiến độ**: mỗi bên chỉ ghi vào mục **của mình**; nhật ký chỉ **thêm dòng mới ở cuối**, không sửa dòng cũ.
4. **Trạng thái** (`status` tổng, và trạng thái của từng bên): `todo` → `in_progress` → `in_review` → `done`; ngoài ra `blocked` (kèm lý do, bên chặn) và `cancelled`.
5. Cập nhật `updated_at` (giờ GMT+7, ví dụ `2026-11-06T10:30:00+07:00`; lấy bằng `TZ=Asia/Ho_Chi_Minh date +%Y-%m-%dT%H:%M:%S+07:00`) mỗi lần sửa; commit + push ngay (`git pull --rebase origin main` trước).
6. Task `done` thì giữ nguyên file (không xoá) để làm lịch sử.

## Phụ thuộc
- Trường `depends_on` liệt kê task phải `done` trước khi bắt đầu; chưa xong thì đặt `blocked` và ghi lý do, hoặc làm task khác.

## Danh sách task hiện có
Xem `ls tasks/`. Mobile: 002–006, 009 (và soạn 007). Laptop: 001, 008, 010, 011 (và thử 007).
