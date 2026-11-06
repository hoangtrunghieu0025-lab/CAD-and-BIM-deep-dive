# CONTRACT giữa claude-mobile và claude-laptop

Hai agent làm việc trên cùng repo GitHub, phối hợp qua commit trên `main` và các file trong repo (không dùng mailbox); người dùng chuyển yêu cầu giữa hai bên khi cần.

## 1. Vai trò

| | **claude-mobile** | **claude-laptop** |
|---|---|---|
| Chạy ở đâu | Cloud (không có GUI, ổ đĩa giới hạn, mạng theo allowlist) | Máy local của người dùng (Ubuntu, 16GB RAM, không GPU rời) |
| Nhận việc | Ít code: nghiên cứu, tài liệu, thiết kế mapping/config, viết spec, review, script nhỏ | Nhiều code & việc cần máy thật: cài QGIS/FreeCAD/Bonsai, chạy pipeline với file thật, kiểm tra `.gpkg` trong QGIS, chụp ảnh, tải file/công cụ bị chặn mạng ở cloud |
| Không làm | Mở GUI (QGIS…), xử lý file CAD/IFC lớn | — (nên nhận việc nặng; việc nghiên cứu thuần giao lại cho mobile nếu quá tải) |

## 2. Phối hợp
- Không có mailbox. Kết quả và ghi chú bàn giao đặt trong file ở thư mục được giao (mục 3), mô tả rõ trong commit message.
- Việc được giao qua `tasks/` (xem `tasks/README.md`): mỗi task ghi rõ ai làm (`assignees`); mọi bên có tên trong `assignees` được sửa file task đó (mục tiến độ: mỗi bên ghi phần của mình, nhật ký chỉ thêm dòng cuối).
- Ngoài file task, mỗi bên chỉ ghi vào thư mục/file được giao cho mình; chỉ đọc phần của bên kia.

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
4. **Báo cáo kết quả (trong file đầu ra hoặc commit message)**: `DONE|PARTIAL|BLOCKED`, danh sách file đã tạo, lệnh đã chạy, kết quả kiểm tra, vấn đề còn mở.
5. **Không bịa**: kết quả chưa chạy thật thì ghi "chưa kiểm chứng". Các quy tắc độ tin cậy khác theo `CLAUDE.md`.
6. **Tách việc không chồng chéo**: mỗi yêu cầu nêu rõ file nào bên nhận được phép ghi để không đụng việc của bên kia.

## 4. Quy trình git
- **Chỉ dùng một nhánh `main`**; không tạo nhánh riêng, không tạo pull request. Cả hai agent push thẳng lên `main`.
- **Trước khi bắt đầu và trước mỗi lần push**: `git pull --rebase origin main`. Nếu push bị từ chối vì remote có commit mới, pull --rebase lại rồi push lại. Không dùng `--force`.
- **Commit + push ngay** sau khi hoàn thành việc, để bên kia thấy được. Commit nhỏ, thường xuyên.
- Vì mỗi agent chỉ ghi vào thư mục của mình (thư mục được giao), xung đột rất hiếm; nếu có, giải quyết khi rebase và không ghi đè công việc của bên kia.
- Commit message nêu rõ nhiệm vụ, ví dụ: `research(mobile): add ifc spatial structure notes`.
