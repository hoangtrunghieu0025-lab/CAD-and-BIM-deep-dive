# Định dạng CAD: DXF, DWG và các định dạng liên quan

- **Câu hỏi nghiên cứu**: DXF/DWG khác nhau thế nào, phiên bản nào được hỗ trợ, và đọc DWG vào Python bằng cách nào?
- **Kết luận ngắn** (2–4 dòng): DXF là định dạng trao đổi (ASCII, có biến thể binary) được `ezdxf` đọc/ghi trực tiếp (R12 → R2018). DWG là nhị phân độc quyền; `ezdxf` không đọc DWG trực tiếp, phải đi qua ODA File Converter (`ezdxf.addons.odafc`) hoặc LibreDWG (`dwg2dxf`, GPLv3+). Với pipeline: chuẩn hoá mọi đầu vào về DXF rồi dùng `ezdxf`.
- **Độ tin cậy**: trung bình — các điểm về ezdxf/odafc/LibreDWG lấy từ kết quả tìm kiếm của tài liệu chính thức (trang readthedocs không fetch trực tiếp được do giới hạn mạng); điểm nào không có nguồn ghi "chưa xác minh".

## Chi tiết

### Bảng định dạng
| Định dạng | Bản chất | Ghi chú |
|---|---|---|
| DXF | Trao đổi của Autodesk, chủ yếu ASCII (tag-based: cặp group code + value) | Có thể mở bằng nhiều phần mềm; `ezdxf` đọc/ghi |
| DWG | Nhị phân độc quyền Autodesk | Không có thư viện Python thuần đọc được; cần ODA/LibreDWG/AutoCAD |
| DGN | MicroStation (Bentley) | Ngoài phạm vi ghi chú này (chưa xác minh chi tiết) |
| SVG/PDF | Vector xuất ra | Mất layer/ngữ nghĩa, không phù hợp làm nguồn |

### Phiên bản DXF mà ezdxf hỗ trợ
Theo tài liệu ezdxf: đọc/ghi/tạo mới DXF R12 (AC1009), R2000 (AC1015), R2004 (AC1018), R2007 (AC1021), R2010 (AC1024), R2013 (AC1027), R2018 (AC1032). R13 (AC1012) và R14 (AC1014) chỉ đọc và được nâng lên R2000; các file cũ hơn R12 chỉ đọc và lưu thành R12. Ma trận chính xác phụ thuộc phiên bản ezdxf cài đặt.

### Đường đọc DWG
1. **ODA File Converter + `ezdxf.addons.odafc`**: `odafc.readfile('my.dwg')` chuyển DWG sang DXF tạm rồi nạp bằng ezdxf. Lỗi: `ODAFCNotInstalledError`, `UnsupportedFileFormat`. Windows có đường dẫn mặc định; Linux/macOS tìm bằng `shutil.which()` hoặc khoá cấu hình `linux_exec_path` (từ ezdxf 1.0). Linux headless có thể cần `xvfb`. Tài liệu cảnh báo chạy ứng dụng ngoài là rủi ro bảo mật nếu đường dẫn có thể bị thay đổi.
2. **LibreDWG (`dwg2dxf`)**: GPLv3+; đọc DWG r1.2–r2018 (độ phủ ~99% theo manual 0.13.4); một số đối tượng R2010+ rất nâng cao bị bỏ qua. Ghi DWG chỉ ổn đến r2004. Lưu ý giấy phép GPL khi tích hợp.
3. Phần mềm thương mại (AutoCAD, BricsCAD) — ngoài phạm vi, chỉ dùng để sửa file hỏng.

### Rủi ro khi chuyển đổi
- Chuyển DWG→DXF có thể làm mất/ biến đổi đối tượng độc quyền (proxy object, ACIS, ACAD_TABLE) — chưa xác minh mức độ cụ thể theo từng phiên bản.
- Nên pin phiên bản DXF đầu ra (ví dụ ASCII DXF 2018) để hành vi ổn định.

## Liên quan đến pipeline CAD → BIM → GPKG
- Bước Ingest: `ingest/` nhận `.dxf` trực tiếp; `.dwg` → gọi `odafc` (cấu hình đường dẫn qua biến môi trường/config), fallback `dwg2dxf`. Cần ghi log phiên bản converter vào metadata đầu ra để tái lập.
- Test CI nên dùng DXF mẫu nhỏ (không phụ thuộc ODA); DWG chỉ test tích hợp có điều kiện (skip nếu thiếu converter).
- Giấy phép: ODA File Converter là phần mềm miễn phí nhưng không mã nguồn mở (điều khoản chưa xác minh); LibreDWG là GPLv3+.

## Nguồn
- [ezdxf — Introduction (phiên bản DXF)](https://ezdxf.readthedocs.io/en/stable/introduction.html) — truy cập 2026-11-06 (qua kết quả tìm kiếm)
- [ezdxf — ODA File Converter Support](https://ezdxf.readthedocs.io/en/stable/addons/odafc.html) — truy cập 2026-11-06 (qua kết quả tìm kiếm)
- [GNU LibreDWG manual](https://www.gnu.org/software/libredwg/manual/html_node/Overview.html) — truy cập 2026-11-06 (qua kết quả tìm kiếm)
- [dwg2dxf(1) openSUSE manpage](https://manpages.opensuse.org/Tumbleweed/libredwg-tools/dwg2dxf.1.en.html) — truy cập 2026-11-06
- [LibreDWG GitHub](https://github.com/LibreDWG/libredwg) — truy cập 2026-11-06

## Câu hỏi còn mở
- Giấy phép/điều khoản phân phối lại ODA File Converter (chưa xác minh).
- Mức mất mát thực tế khi DWG→DXF với proxy entity (chưa xác minh).
- DGN: có cần hỗ trợ không (ODA converter có thể đọc DGN? chưa xác minh).
