# Chuyển DWG → DXF bằng ODA File Converter

- **Câu hỏi nghiên cứu**: Có cách chạy được trên máy này để đổi DWG sang DXF cho pipeline `ezdxf` không, dùng thế nào, và có ràng buộc gì?
- **Kết luận ngắn**: Có. ODA File Converter 27.10.0.0 (AppImage, không cần sudo) đã cài ở `~/apps/ODAFileConverter/` và đổi được cả DWG R2018 lẫn DWG R10 (AC1006, 1989) sang DXF R2018, giữ layer và khối. Ràng buộc chính: đây là phần mềm **đóng nguồn**, điều khoản của ODA không cho đóng gói/phân phối cùng phần mềm khác nếu chưa có văn bản đồng ý, nên ta chỉ gọi nó như công cụ ngoài, **không đưa vào repo**.
- **Độ tin cậy**: cao cho khả năng chuyển đổi (đã chạy 4 file, đọc lại bằng `ezdxf`); thấp cho độ trung thực toàn diện (chưa so từng thực thể với bản gốc) và cho điều khoản pháp lý (chỉ thấy một câu trong file thực thi, **chưa đọc bản điều khoản đầy đủ**).

## Chi tiết
**Cài đặt (đã làm, 2026-11-09)**
- Tải từ liên kết chính thức của trang ODA (`https://www.opendesign.com/guestfiles/oda_file_converter` → `guestfiles/get?filename=ODAFileConverter_QT6_lnxX64_11dll.AppImage`, chuyển hướng sang URL ký sẵn trên AWS S3, hết hạn sau 60 giây, **không cần đăng nhập**). Phiên bản 27.10.0.0, 81 062 392 byte, sha256 `a73eea1dfc873cd46b94bfa07760dcff0082c4300dd33c5401e8a526cfab787b` (ODA không công bố checksum để đối chiếu).
- Đặt tại `~/apps/ODAFileConverter/ODAFileConverter_QT6_lnxX64_11dll_27.10.AppImage` (đã `chmod +x`). Máy có `/dev/fuse`, glibc 2.39; không cần cài thêm gói.

**Cách dùng** (cú pháp theo trang ODA; đã kiểm bằng chạy thật)
```
DISPLAY=:0 ~/apps/ODAFileConverter/ODAFileConverter_QT6_lnxX64_11dll_27.10.AppImage \
    <thư_mục_vào> <thư_mục_ra> ACAD2018 DXF 0 1
#   tham số: thư mục nguồn · thư mục đích · phiên bản đầu ra · DXF|DWG · đệ quy 0/1 · audit 0/1 · [bộ lọc, mặc định *.dwg;*.dxf]
```
- Cần một màn hình X: plugin Qt đóng gói chỉ có `xcb` (không có `offscreen`); `DISPLAY=:0` (XWayland của phiên) chạy được, in cảnh báo `Could not find the Qt platform plugin "wayland"` nhưng vẫn chạy. Máy chưa có `Xvfb` (chỉ có `Xephyr`), nếu cần chạy không màn hình thì phải cài `xvfb`.
- Thư mục vào/ra phải khác nhau; chuyển cả thư mục, không chuyển từng file.

**Kết quả thử** (đọc lại bằng `ezdxf.readfile`, tất cả đọc được, đầu ra AC1032)
| Đầu vào | Định dạng gốc | Thực thể sau chuyển | Layer | Ghi chú |
|---|---|---|---|---|
| `positio.dwg`, `Kotelo.dwg`, `hoyrystin-1.dwg` (từ `Mcrauli/dwg2ifc`, MIT) | AutoCAD 2018 | 4 / 16 / 15 | 1 (`0`) | giữ `3DSOLID`, `3DFACE`, `MESH`, `ATTDEF` |
| kế hoạch điện nhà ở USFS E0084000 (Innerscene, CC0) | **AutoCAD R10 (AC1006)** | **1479** (954 LINE, 219 ARC, 206 TEXT, 57 CIRCLE, 25 INSERT) | 5: `0`, `HIP`, `LIGHTING`, `POWER`, `TEXT` | 7 khối; **`$INSUNITS = 0`** (mất thông tin đơn vị, phải dùng `fallback_unit`) |

## Liên quan đến pipeline CAD → BIM → GPKG
- Bước "đưa về DXF" trong `TASK-018` có thể gọi lệnh trên; vì ODA đóng nguồn nên đặt đường dẫn công cụ trong cấu hình/biến môi trường (ví dụ `ODA_FILE_CONVERTER`), không mã cứng và không đóng gói.
- Chuyển đổi lưu thành DXF **R2018 (AC1032)**; `ezdxf` 1.4.5 đọc được. Thực thể ACIS (`3DSOLID`) vẫn là dữ liệu SAB mà `ezdxf` không phân tích hình học (theo ghi chú của dwg2ifc); nếu cần hình học 3D phải xử lý riêng.
- Bản vẽ điện R10 sau chuyển là một mặt bằng MEP nhà ở có layer rõ (`POWER`, `LIGHTING`): đáng thử luật nhận dạng MEP trên đó khi làm M5.

## Nguồn
- [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) — truy cập 2026-11-09 (trang tải; không nêu điều khoản, không nêu cú pháp đầy đủ)
- Chạy thật tại máy, 2026-11-09: phiên bản 27.10.0.0; dòng bản quyền lấy từ chuỗi trong file thực thi ("This software may not be licensed, sold, distributed or included with other software products without the written consent of Open Design Alliance")
- `Mcrauli/dwg2ifc` (MIT), Innerscene (CC0): xem `research/sources.md`

## Câu hỏi còn mở
- Điều khoản đầy đủ của ODA File Converter (dùng thương mại, dùng nội bộ công ty): chưa đọc.
- Độ trung thực: khối động, annotative scale, đối tượng riêng của AutoCAD Architecture/MEP sau chuyển: chưa kiểm.
- Chạy không màn hình (`xvfb`) và chạy hàng loạt trong CI: chưa thử.
