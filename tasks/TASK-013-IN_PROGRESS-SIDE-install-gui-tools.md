---
id: TASK-013
title: "[IN_PROGRESS][SIDE] Cài FreeCAD, Blender + Bonsai, LibreCAD và dùng thử Archilogic"
category: SIDE
assignees: [claude-laptop]
created_by: claude-laptop
created_at: 2026-11-06T10:37:25+07:00
updated_at: 2026-11-06T15:02:03+07:00
status: in_progress
priority: normal
depends_on: [TASK-001]
---

# [IN_PROGRESS][SIDE] TASK-013 — Cài FreeCAD, Blender + Bonsai, LibreCAD và dùng thử Archilogic

## Mô tả
TASK-001 xác nhận ba công cụ GUI sau chưa có trên máy local (Ubuntu 24.04, 16GB RAM, không GPU rời): FreeCAD, Blender + Bonsai (BlenderBIM), LibreCAD. Cài và kiểm chứng để mở được `samples/sample-floor-*.dxf` và `samples/sample-building.ifc` bằng mắt, đối chiếu với kết quả `ezdxf`/`ifcopenshell`. Chưa task nào khác phụ thuộc, nên không chặn pipeline.

Việc cài bằng `apt`/`snap` cần `sudo`; agent không tự cấp quyền. Người dùng chạy lệnh cài (hoặc cấp quyền sudo cho phiên) và agent kiểm chứng kết quả.

### Phần B — Dùng thử Archilogic (bổ sung theo chủ dự án, 2026-11-06)
Từ kết quả TASK-014 (`research/05-market-tools/comparison-and-recommendation.md`): Archilogic nhận DWG/DXF/PDF/ảnh và xuất IMDF; có gói Starter miễn phí (tối đa 5 floor plan, kèm phí $329/floor plan chuyển đổi theo trang giá — chưa rõ điều khoản trừ). Mục đích: lấy **một bộ IMDF do công cụ bên ngoài sinh ra từ chính DXF mẫu** để (1) đối chiếu với thiết kế mapping/IMDF của dự án (TASK-007/009), (2) làm dữ liệu thử cho mô-đun xuất gói IMDF (TASK-009), (3) xem chất lượng nhận diện phòng/cửa của một sản phẩm thương mại.

Lưu ý: Archilogic là **dịch vụ web**, không phải phần mềm tải về; cần tài khoản.
- **Chủ dự án tự đăng ký tài khoản và tự thao tác đăng nhập** (hoặc cấp phép rõ cho agent làm, kèm email dùng); agent **không tự đăng ký**, không dùng email của chủ dự án nếu chưa được phép.
- **Không nhập thông tin thanh toán.** Trước khi bấm chuyển đổi, đọc điều khoản gói Starter; nếu thao tác sẽ phát sinh phí (ví dụ $329/floor plan) thì **dừng và hỏi chủ dự án**.
- **Chỉ tải lên file mẫu của dự án** (`samples/sample-floor-1.dxf`, `samples/sample-floor-2.dxf`; dữ liệu tự sinh, không chứa thông tin thật). Không tải dữ liệu khác.
- Ghi lại điều khoản về quyền dữ liệu/lưu trữ file tải lên (nếu đọc được).

## Đầu vào (inputs)
- `docs/local-env-report.md` (trạng thái "CHƯA CÀI" hiện tại)
- `samples/sample-floor-1.dxf`, `samples/sample-floor-2.dxf`, `samples/sample-building.ifc`

## Đầu ra mong đợi (expected_outputs)
- Cập nhật `docs/local-env-report.md`: thay trạng thái "CHƯA CÀI" bằng phiên bản thực tế, ghi cách cài đã dùng (apt/snap/tarball).
- Ghi nhận kết quả mở file mẫu của từng công cụ trong nhật ký task (ảnh chụp màn hình nếu có, đặt vào `docs/assets/`).
- **Phần B**: `research/05-market-tools/archilogic-trial.md` — quy trình đã làm, gói IMDF tải về (liệt kê file trong ZIP), đối chiếu với đặc tả IMDF đã xác minh (`research/04-osm-imdf-tagging/`), ảnh chụp màn hình (`docs/assets/`), nhận xét về chất lượng nhận diện, giới hạn gói miễn phí, điều khoản dữ liệu. Gói IMDF tải về (nhỏ) đặt vào `samples/external/archilogic/` nếu giấy phép/điều khoản cho phép lưu trong repo, nếu không thì chỉ ghi mô tả.

## Gợi ý cách cài (chưa kiểm chứng, kiểm tra trước khi chạy)
Tên gói và nguồn dưới đây là gợi ý, chưa xác minh trên máy này. Chạy `apt-cache policy <gói>` / `snap info <gói>` để xem có sẵn và phiên bản nào.
- **LibreCAD**: gói apt `librecad`.
- **FreeCAD**: gói apt `freecad` hoặc snap `freecad`; chọn bản có thể nạp module IFC.
- **Blender**: gói snap `blender` (`--classic`), hoặc tarball từ trang chủ Blender; không dùng gói apt nếu quá cũ so với yêu cầu của Bonsai.
- **Bonsai**: add-on của Blender, cài trong Blender qua Extensions; phải khớp phiên bản Blender mà Bonsai hỗ trợ (kiểm tra trong tài liệu Bonsai khi cài).

## Tiêu chí hoàn thành (acceptance)
- [ ] `librecad` mở được `samples/sample-floor-1.dxf`; thấy các layer `A-WALL`, `A-AREA`, `A-AREA-IDEN`, `A-DOOR`
- [ ] `freecad` (hoặc `freecadcmd`) in được phiên bản; mở được `samples/sample-building.ifc`
- [ ] `blender --version` in được phiên bản; Bonsai bật được và mở được `samples/sample-building.ifc`, thấy 2 tầng và các `IfcSpace`
- [ ] `docs/local-env-report.md` cập nhật phiên bản và cách cài của cả ba công cụ
- [ ] Nếu công cụ nào không cài/mở được: ghi lý do vào Blocker, không bỏ trống tiêu chí
- [ ] **(B)** Chủ dự án đã đăng ký/cho phép dùng tài khoản Archilogic; không phát sinh phí ngoài ý muốn
- [ ] **(B)** Đã chuyển đổi ≥1 DXF mẫu và tải về gói IMDF; `research/05-market-tools/archilogic-trial.md` liệt kê các file trong gói, so với danh sách bắt buộc của IMDF (`manifest.json`, `address.geojson`, `venue.geojson`) và các feature type có mặt
- [ ] **(B)** Có bảng so sánh: category/geometry mà Archilogic gán cho phòng, cửa, tường, cầu thang so với mapping của dự án (`config/tag_mapping.yaml`) và ghi chênh lệch
- [ ] **(B)** Ghi rõ giới hạn đã gặp (số floor plan, watermark, phí, định dạng xuất)

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; được ghi `docs/local-env-report.md`, `docs/assets/`, `research/05-market-tools/archilogic-trial.md`, `samples/external/archilogic/` (nếu được phép lưu) và file task này. Lệnh cần `sudo` và thao tác đăng ký/đăng nhập Archilogic do người dùng thực hiện.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | in_progress | 2026-11-06T12:17:25+07:00 | đã kiểm nguồn cài; chờ chủ dự án chạy lệnh sudo (phần A) và đăng ký Archilogic (phần B) |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T12:09:16+07:00 | todo | Theo chủ dự án: gộp phần B — dùng thử Archilogic (kết quả từ TASK-014) vào task này; đổi tiêu đề. Chưa bắt đầu. |
| 2026-11-06T12:17:25+07:00 | in_progress | Nhận task. Kiểm nguồn cài (chưa cài gì): apt có `librecad` 2.2.0.2 và `blender` 4.0.2 (quá cũ cho Bonsai ≥4.2); không có gói apt `freecad` trên máy này; snap `freecad` stable 1.1 (529MB), snap `blender` có kênh 5.0/stable=5.0.1; Bonsai 0.9.0-post1 (py311) trên extensions.blender.org yêu cầu Blender 4.2.0–5.1.0. `sudo` cần mật khẩu nên chờ chủ dự án chạy. |
| 2026-11-06T14:15:23+07:00 | in_progress | Phần A (một phần): **LibreCAD 2.2.0.2** (apt) và **Blender 5.0.1** (snap `5.0/stable`) đã cài. **Bonsai 0.9.0-post1** cài bằng dòng lệnh Blender; Blender chạy nền nạp `sample-building.ifc` OK (IFC4, 2 tầng Elevation 0.0/3.0, 26 IfcSpace, 24 IfcDoor, 8 IfcWall). LibreCAD: `dxf2pdf -a` dựng đúng `sample-floor-1.dxf` (ảnh `docs/assets/librecad-sample-floor-1.png`); chưa nhìn trực tiếp GUI/bảng layer. **FreeCAD chưa cài**: lỗi `network is unreachable` lúc tải snap lần đầu; chờ chủ dự án chạy lại `sudo snap install freecad`. Lưu ý: lần tải Bonsai đầu bị cắt (654 KB, sha256 sai) nên bỏ, tải lại 170 MB và kiểm sha256 trước khi cài. Cập nhật `docs/local-env-report.md`. |
| 2026-11-06T14:47:20+07:00 | in_progress | **Hoãn FreeCAD** theo chủ dự án: snap FreeCAD kéo theo `kf6-core24` 1,74 GB (+ FreeCAD 529 MB), tải qua đường quốc tế chỉ ~0,2–1,2 Mbps (đã tải dở ~179 MB và ~116 MB trong `/var/lib/snapd/snaps/*.partial`). Chạy lại `sudo snap install freecad` khi mạng tốt hơn; Blender+Bonsai đã mở và đọc được `sample-building.ifc` nên phần kiểm IFC bằng GUI đã có. Phần B (Archilogic) vẫn chờ chủ dự án đăng ký tài khoản. |
| 2026-11-06T15:02:03+07:00 | in_progress | Phần B: chủ dự án đã đăng ký tài khoản Archilogic. Phiên này **không có công cụ trình duyệt** (extension Claude in Chrome chưa kết nối) nên laptop không thao tác trên tài khoản; chủ dự án tự làm các bước trên web theo hướng dẫn, laptop phân tích gói tải về. Tìm thấy qua WebSearch: Archilogic gắn xuất IMDF với quy trình **Microsoft Places** (cần floor plan có georeference, có thể cần Place ID), trang Exporting chung chỉ liệt kê SVG, ảnh, DXF, IFC — nên IMDF có thể không xuất được trên gói Starter hoặc cần bước ánh xạ; ghi nhận như một phát hiện. Chưa có file nào được tải lên hoặc tải về. |

## Blocker / câu hỏi mở
- Cần `sudo` để cài; chờ người dùng quyết định cách cài (apt/snap) cho từng công cụ.
- Phần B: cần chủ dự án đăng ký tài khoản Archilogic (hoặc cho phép rõ) và xác nhận không phát sinh phí trước khi chuyển đổi.
