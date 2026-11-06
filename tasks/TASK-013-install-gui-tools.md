---
id: TASK-013
title: Cài FreeCAD, Blender + Bonsai, LibreCAD trên máy local
assignees: [claude-laptop]
created_by: claude-laptop
created_at: 2026-11-06T10:37:25+07:00
updated_at: 2026-11-06T10:37:25+07:00
status: todo
priority: normal
depends_on: [TASK-001]
---

## Mô tả
TASK-001 xác nhận ba công cụ GUI sau chưa có trên máy local (Ubuntu 24.04, 16GB RAM, không GPU rời): FreeCAD, Blender + Bonsai (BlenderBIM), LibreCAD. Cài và kiểm chứng để mở được `samples/sample-floor-*.dxf` và `samples/sample-building.ifc` bằng mắt, đối chiếu với kết quả `ezdxf`/`ifcopenshell`. Chưa task nào khác phụ thuộc, nên không chặn pipeline.

Việc cài bằng `apt`/`snap` cần `sudo`; agent không tự cấp quyền. Người dùng chạy lệnh cài (hoặc cấp quyền sudo cho phiên) và agent kiểm chứng kết quả.

## Đầu vào (inputs)
- `docs/local-env-report.md` (trạng thái "CHƯA CÀI" hiện tại)
- `samples/sample-floor-1.dxf`, `samples/sample-floor-2.dxf`, `samples/sample-building.ifc`

## Đầu ra mong đợi (expected_outputs)
- Cập nhật `docs/local-env-report.md`: thay trạng thái "CHƯA CÀI" bằng phiên bản thực tế, ghi cách cài đã dùng (apt/snap/tarball).
- Ghi nhận kết quả mở file mẫu của từng công cụ trong nhật ký task (ảnh chụp màn hình nếu có, đặt vào `docs/assets/`).

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

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; được ghi `docs/local-env-report.md`, `docs/assets/`, file task này. Lệnh cần `sudo` do người dùng chạy.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | todo | 2026-11-06T10:37:25+07:00 | chưa nhận; cần người dùng chạy lệnh cài (sudo) |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|

## Blocker / câu hỏi mở
- Cần `sudo` để cài; chờ người dùng quyết định cách cài (apt/snap) cho từng công cụ.
