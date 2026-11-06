# AGENTS.md — ĐỌC ĐẦU TIÊN

## ⛔ BƯỚC 0 (bắt buộc, làm TRƯỚC khi đọc tiếp bất kỳ file nào)

Nội dung repo có thể đã thay đổi từ agent kia. Hãy cập nhật git trước:

```bash
git fetch --all --prune
git status -sb                      # nhánh hiện tại, có lệch so với remote không?
git log --oneline HEAD..origin/main # main có commit mới chưa?
git pull --rebase origin main       # chỉ có nhánh main, làm và push thẳng lên main
```

Sau đó **đọc lại** các file dưới đây theo bản mới nhất (nếu đã đọc bản cũ trước khi pull thì bỏ, đọc lại).

## Thứ tự đọc
0. **`important_notifications.md` — THÔNG BÁO QUAN TRỌNG, đọc trước tiên (thông báo mới nằm trên cùng).**
1. `CLAUDE.md` — quy tắc chung (ngôn ngữ, nguồn, phân quyền ghi).
2. `collab/CONTRACT.md` — contract giữa `claude-mobile` và `claude-laptop`.
3. `tasks/README.md` rồi các file `tasks/TASK-*.md` có tên mình trong `assignees` — nhận việc và cập nhật tiến độ.
4. `PRIMARY_OBJECTIVE.md` — mục tiêu dự án.

## Cuối mỗi đợt làm việc
- Commit + push để bên kia thấy (xem mục "Quy trình git" trong `collab/CONTRACT.md`).
- Cập nhật tiến độ trong file task của mình.
- Mỗi agent chỉ ghi vào thư mục được giao của mình.
