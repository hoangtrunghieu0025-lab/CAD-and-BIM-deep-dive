# Định dạng CAD: DXF, DWG và các định dạng liên quan

- **Câu hỏi nghiên cứu**: DXF/DWG khác nhau thế nào, phiên bản nào được hỗ trợ, và đọc DWG vào Python bằng cách nào?
- **Kết luận ngắn** (2–4 dòng): DXF là định dạng trao đổi (ASCII, có biến thể binary) được `ezdxf` đọc/ghi trực tiếp (R12 → R2018). DWG là nhị phân độc quyền; `ezdxf` không đọc DWG trực tiếp, phải đi qua ODA File Converter (`ezdxf.addons.odafc`) hoặc LibreDWG (`dwg2dxf`, GPLv3+). Với pipeline: chuẩn hoá mọi đầu vào về DXF rồi dùng `ezdxf`.
- **Độ tin cậy**: cao–trung bình — vòng 2 đã đối chiếu docs `.rst` + mã nguồn ezdxf trên GitHub (`ezdxf.readthedocs.io` vẫn không phân giải DNS) và README LibreDWG; điểm nào chưa kiểm chứng ghi "chưa xác minh".

## Chi tiết

### Bảng định dạng
| Định dạng | Bản chất | Ghi chú |
|---|---|---|
| DXF | Trao đổi của Autodesk, chủ yếu ASCII (tag-based: cặp group code + value) | Có thể mở bằng nhiều phần mềm; `ezdxf` đọc/ghi |
| DWG | Nhị phân độc quyền Autodesk | Không có thư viện Python thuần đọc được; cần ODA/LibreDWG/AutoCAD |
| DGN | MicroStation (Bentley) | Ngoài phạm vi ghi chú này (chưa xác minh chi tiết) |
| SVG/PDF | Vector xuất ra | Mất layer/ngữ nghĩa, không phù hợp làm nguồn |

### Phiên bản DXF mà ezdxf hỗ trợ
Đã xác minh (`docs/source/dxfversion.inc`, bảng phiên bản): AC1009 = R12; AC1012 = R13 → R2000; AC1014 = R14 → R2000; AC1015 = R2000; AC1018 = R2004; AC1021 = R2007; AC1024 = R2010; AC1027 = R2013; AC1032 = R2018. Docs `introduction.rst`: "Ezdxf also reads older DXF versions but saves it as DXF R12." Mũi tên "R13 → R2000" nghĩa là file R13/R14 được nâng lên R2000 khi nạp. Chi tiết "đọc/ghi/tạo mới" cho từng phiên bản: bảng chỉ có cột version/release nên phần này chưa xác minh từ nguồn gốc (bản vòng 1 dựa trên kết quả tìm kiếm). DXF nhị phân: `ezdxf.recover` chỉ hỗ trợ ASCII DXF (đã xác minh); `ezdxf.readfile` với binary DXF: chưa xác minh.

### Đường đọc DWG
1. **ODA File Converter + `ezdxf.addons.odafc`** (đã xác minh, docs `addons/odafc.rst` + `addons/odafc.py`): hàm `is_installed`, `readfile`, `export_dwg`, `convert`. Chữ ký: `readfile(filename, version=None, *, audit=False) -> Drawing` — chuyển DWG sang DXF tạm rồi nạp bằng ezdxf. Ngoại lệ (mã nguồn): `ODAFCError` (kế thừa `IOError`) và các lớp con `UnknownODAFCError`, `ODAFCNotInstalledError`, `UnsupportedFileFormat`, `UnsupportedPlatform`, `UnsupportedVersion`. Phiên bản đích hợp lệ: `ACAD9, ACAD10, ACAD12, ACAD13, ACAD14, ACAD2000, ACAD2004, ACAD2007, ACAD2010, ACAD2013, ACAD2018` (có map từ `R2018`, `AC1032`…). Cấu hình (mục `[odafc-addon]`): `win_exec_path` (mặc định `C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe`) và `unix_exec_path` (đường dẫn tuyệt đối, ví dụ AppImage; nếu rỗng thì dùng lệnh `ODAFileConverter` qua `shutil.which`). **Sửa so với vòng 1**: khoá cấu hình Linux/macOS là `unix_exec_path` (mã nguồn); trang docs còn nhắc `linux_exec_path` nhưng tự mâu thuẫn — không dùng tên `linux_exec_path`, và khẳng định "từ ezdxf 1.0" chưa xác minh. Linux headless: docs nói có thể cần cài `xvfb` để ngăn GUI; macOS không có workaround đã biết. Cảnh báo bảo mật (đã xác minh trong docs trên GitHub): "Execution of an external application is a big security issue!", rủi ro lớn khi đường dẫn executable có thể bị thay đổi; docs gợi ý xoá module `ezdxf/addons/odafc.py` nếu không dùng.
2. **LibreDWG (`dwg2dxf`)** (đã xác minh, README GitHub): giấy phép GPL v3 hoặc mới hơn; bộ giải mã đọc mọi phiên bản DWG, nhưng một số đối tượng R2010+ rất nâng cao không đọc được và bị bỏ qua; ghi hỗ trợ mọi phiên bản trừ R2007, và ghi R2010–R2018 còn lỗi CRC (tuỳ chọn build: ghi chỉ ổn đến R2004). Con số "độ phủ ~99% theo manual 0.13.4" và "r1.2–r2018": chưa xác minh lại (vòng 1 qua tìm kiếm). Lưu ý giấy phép GPL khi tích hợp.
3. Phần mềm thương mại (AutoCAD, BricsCAD) — ngoài phạm vi, chỉ dùng để sửa file hỏng.

### Rủi ro khi chuyển đổi
- Chuyển DWG→DXF có thể làm mất/ biến đổi đối tượng độc quyền (proxy object, ACIS, ACAD_TABLE) — chưa xác minh mức độ cụ thể theo từng phiên bản.
- Nên pin phiên bản DXF đầu ra (ví dụ ASCII DXF 2018) để hành vi ổn định.

## Liên quan đến pipeline CAD → BIM → GPKG
- Bước Ingest: `ingest/` nhận `.dxf` trực tiếp; `.dwg` → gọi `odafc` (cấu hình đường dẫn qua biến môi trường/config), fallback `dwg2dxf`. Cần ghi log phiên bản converter vào metadata đầu ra để tái lập.
- Test CI nên dùng DXF mẫu nhỏ (không phụ thuộc ODA); DWG chỉ test tích hợp có điều kiện (skip nếu thiếu converter).
- Giấy phép: ODA File Converter là phần mềm miễn phí nhưng không mã nguồn mở (điều khoản chưa xác minh); LibreDWG là GPLv3+.

## Nguồn
- [ezdxf `docs/source/dxfversion.inc`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/dxfversion.inc) và [`introduction.rst`](https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/introduction.rst) (nguồn của https://ezdxf.readthedocs.io/en/stable/introduction.html) — truy cập 2026-11-06
- [ezdxf `docs/source/addons/odafc.rst`](https://github.com/mozman/ezdxf/blob/master/docs/source/addons/odafc.rst) (nguồn của https://ezdxf.readthedocs.io/en/stable/addons/odafc.html) và [`src/ezdxf/addons/odafc.py`](https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/addons/odafc.py) — truy cập 2026-11-06
- [LibreDWG README (GitHub)](https://raw.githubusercontent.com/LibreDWG/libredwg/master/README) — truy cập 2026-11-06
- [GNU LibreDWG manual](https://www.gnu.org/software/libredwg/manual/html_node/Overview.html) — truy cập 2026-11-06 (vòng 1, qua kết quả tìm kiếm; chưa mở lại)
- [dwg2dxf(1) openSUSE manpage](https://manpages.opensuse.org/Tumbleweed/libredwg-tools/dwg2dxf.1.en.html) — truy cập 2026-11-06
- [LibreDWG GitHub](https://github.com/LibreDWG/libredwg) — truy cập 2026-11-06

## Câu hỏi còn mở
- Giấy phép/điều khoản phân phối lại ODA File Converter (chưa xác minh).
- Mức mất mát thực tế khi DWG→DXF với proxy entity (chưa xác minh).
- DGN: có cần hỗ trợ không (ODA converter có thể đọc DGN? chưa xác minh).
