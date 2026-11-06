# CONTRACT giữa claude-mobile và claude-laptop

Hai agent làm việc trên cùng repo GitHub, giao tiếp **chỉ qua file** trong `mailbox/`.

## 1. Vai trò

| | **claude-mobile** | **claude-laptop** |
|---|---|---|
| Chạy ở đâu | Cloud (không có GUI, ổ đĩa giới hạn, mạng theo allowlist) | Máy local của người dùng (Ubuntu, 16GB RAM, không GPU rời) |
| Nhận việc | Ít code: nghiên cứu, tài liệu, thiết kế mapping/config, viết spec, review, script nhỏ | Nhiều code & việc cần máy thật: cài QGIS/FreeCAD/Bonsai, chạy pipeline với file thật, kiểm tra `.gpkg` trong QGIS, chụp ảnh, tải file/công cụ bị chặn mạng ở cloud |
| Không làm | Mở GUI (QGIS…), xử lý file CAD/IFC lớn | — (nên nhận việc nặng; việc nghiên cứu thuần giao lại cho mobile nếu quá tải) |

## 2. Mailbox

```
mailbox/
├── claude-mobile/    # thư MOBILE GỬI ĐI (chỉ mobile được ghi)
└── claude-laptop/    # thư LAPTOP GỬI ĐI (chỉ laptop được ghi)
```

- **Mỗi agent chỉ ghi vào thư mục của mình**; muốn gửi thư cho bên kia thì tạo file mới trong thư mục của mình. Bên kia đọc thư mục đó. Nhờ vậy không bao giờ xung đột git.
- **Không sửa, không xoá thư đã gửi** (append-only). Cần đính chính thì gửi thư mới, đặt `reply_to`.
- **Đánh dấu đã đọc**: mỗi agent ghi con trỏ vào file `mailbox/<tên-mình>/_cursor.md` (xem mục 5), không sửa thư của bên kia.

### Tên file
```
email-<YYYYMMDD>T<HHMMSS>Z-<tieu-de-ngan>.md
```
- Thời điểm theo **UTC** (`date -u +%Y%m%dT%H%M%SZ`).
- Tiêu đề ngắn: chữ thường không dấu, gạch ngang, tối đa ~5 từ. Ví dụ: `email-20261106T010042Z-kickoff-setup.md`.

### Nội dung thư (bắt buộc có frontmatter)
```markdown
---
from: claude-mobile
to: claude-laptop
sent_at: 2026-11-06T01:00:42Z
subject: Tiêu đề đầy đủ
type: request | response | info | question
reply_to: <tên file thư đang trả lời, hoặc bỏ trống>
priority: low | normal | high
---

## Bối cảnh
## Yêu cầu / Nội dung
## Đầu vào (inputs)
## Đầu ra mong đợi (expected_outputs)
## Tiêu chí hoàn thành (acceptance)
## Hạn / ghi chú
```
Với `type: response`: nêu **kết quả**, đường dẫn file đầu ra, lệnh đã chạy, lỗi nếu có, và ghi rõ `DONE` / `PARTIAL` / `BLOCKED` kèm lý do.

## 3. Contract đầu vào – đầu ra giữa hai agent

1. **Mọi yêu cầu phải tự đủ**: người nhận không phải đoán. Nêu rõ đường dẫn file đầu vào (tương đối từ gốc repo), lệnh/thao tác mong muốn, và đường dẫn đầu ra.
2. **Đầu ra đặt đúng chỗ** (người gửi chỉ định, mặc định như dưới):

| Loại | Thư mục |
|---|---|
| Ghi chú nghiên cứu | `research/NN-<chủ đề>/` |
| Tài liệu tổng hợp | `docs/` |
| Cấu hình mapping | `config/` |
| Code | `src/`, test ở `tests/` |
| File mẫu đầu vào | `samples/` |
| Kết quả chạy (`.gpkg`, ảnh) | `out/` (git-ignore; chỉ commit file nhỏ có chủ đích, đặt vào `samples/` hoặc `docs/assets/`) |

3. **Tiêu chí hoàn thành kiểm chứng được** (ví dụ: "`ogrinfo -so out/x.gpkg` liệt kê đủ các layer `unit`, `level`, `building`; CRS = EPSG:4326").
4. **Phản hồi trong thư `response`**: `DONE|PARTIAL|BLOCKED`, danh sách file đã tạo, lệnh đã chạy, kết quả kiểm tra, vấn đề còn mở.
5. **Không bịa**: kết quả chưa chạy thật thì ghi "chưa kiểm chứng". Các quy tắc độ tin cậy khác theo `CLAUDE.md`.
6. **Tách việc không chồng chéo**: mỗi thư yêu cầu nêu rõ file nào bên nhận được phép ghi để không đụng việc của bên kia.

## 4. Quy trình git
- Làm việc trên nhánh đã được giao; **pull/rebase trước khi bắt đầu** và **commit + push ngay sau khi gửi thư hoặc hoàn thành việc**, để bên kia thấy được.
- Commit message nêu rõ thư/nhiệm vụ, ví dụ: `mailbox(mobile): kickoff setup request`.
- Hai agent có thể ở hai nhánh khác nhau; khi đó bên nhận `git fetch` và đọc `mailbox/<bên-kia>/` từ nhánh của bên gửi, hoặc hai bên thống nhất nhánh chung trong thư đầu tiên.
- Không push lên nhánh của bên kia nếu không được yêu cầu.

## 5. Con trỏ đã đọc (`_cursor.md`)
Mỗi agent giữ file `mailbox/<tên-mình>/_cursor.md` (chỉ mình ghi):
```
last_read_from_<tên-bên-kia>: email-20261106T010042Z-kickoff-setup.md
updated_at: 2026-11-06T01:30:00Z
```
Khi bắt đầu phiên làm việc: đọc mọi thư trong thư mục bên kia có tên **lớn hơn** con trỏ (tên file sắp xếp theo thời gian), xử lý theo thứ tự, rồi cập nhật con trỏ.
