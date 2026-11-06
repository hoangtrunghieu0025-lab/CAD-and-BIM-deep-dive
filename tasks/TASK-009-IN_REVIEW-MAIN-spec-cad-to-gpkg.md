---
id: TASK-009
title: "[IN_REVIEW][MAIN] Viết spec thiết kế pipeline CAD → BIM → GPKG"
category: MAIN
assignees: [claude-mobile]
created_by: claude-mobile
created_at: 2026-11-06T09:37:46+07:00
updated_at: 2026-11-06T12:16:49+07:00
status: in_review
priority: high
depends_on: [TASK-005, TASK-007]
---

# [IN_REVIEW][MAIN] TASK-009 — Viết spec thiết kế pipeline CAD → BIM → GPKG

## Mô tả
Viết đặc tả để laptop cài đặt: module, hàm, input/output từng bước, schema bảng GPKG theo IMDF, quy tắc georeference, kiểm tra hợp lệ.

## Bổ sung phạm vi theo chủ dự án (2026-11-06) — mô-đun xuất gói IMDF
*(do claude-laptop ghi hộ theo yêu cầu của chủ dự án; claude-mobile là assignee xem lại và điều chỉnh nếu cần.)*

Kết quả TASK-014 (`research/05-market-tools/comparison-and-recommendation.md`): các công cụ trên thị trường tiêu thụ và sinh **gói IMDF** (ZIP gồm `manifest.json` + `*.geojson`) để nộp Apple Indoor Maps / Microsoft Places, không phải GPKG. GPKG của dự án là dạng lưu trữ/xem trong QGIS. Vì vậy spec phải có thêm **mô-đun xuất gói IMDF từ các bảng GPKG** (`export/imdf_package`), dự kiến cài đặt trong TASK-010 hoặc giai đoạn kế tiếp.

Spec mô-đun này phải nêu:
- **Đầu vào**: file `.gpkg` do pipeline tạo (mỗi IMDF feature type một bảng; feature không geometry nằm ở bảng `attributes`).
- **Đầu ra**: `<tên>.imdf.zip` chứa `manifest.json` (**bắt buộc**), `address.geojson` (**bắt buộc**), `venue.geojson` (**bắt buộc**, đúng một Venue) và các `*.geojson` tuỳ chọn (`building`, `footprint`, `level`, `unit`, `opening`, `fixture`, `detail`, `amenity`, `anchor`, `occupant`, `kiosk`, `relationship`, `section`, `geofence`); xem `research/04-osm-imdf-tagging/imdf-relations-and-constraints.md`.
- **Chuyển đổi**: cột JSON text → object/mảng; `name` dạng LABELS; geometry null cho `building`/`occupant`/`address`; `id` là UUID; `display_point`; bỏ cột không thuộc IMDF hoặc khai báo extension (`imdf:extension:<provider>:<name>#<version>`).
- **Manifest**: các khoá `version`, `created`, `language`, `generated_by`, `extensions` (chỉ có ví dụ trong spec, chưa có định nghĩa đầy đủ — ghi rõ là suy từ ví dụ).
- **Kiểm tra trước khi đóng gói**: thuộc tính bắt buộc/nullable theo từng feature (`research/04-osm-imdf-tagging/imdf-feature-types.md`), khoá ngoại tồn tại, unit ⊂ level và phủ kín level, opening được phủ bởi unit, mỗi level có opening (trừ ngoại lệ), `venue` chứa mọi feature.
- **Tham chiếu để đối chiếu**: gói IMDF do Archilogic sinh từ DXF mẫu (TASK-013 phần B), nếu có; validator cộng đồng `adap-c6-fingerprint/IMDFrnt` (chưa đánh giá).
- **Danh sách test** cho mô-đun: cấu trúc ZIP, schema từng file, các ràng buộc ở trên; thêm vào danh sách test mà TASK-010 phải qua.

## Đầu vào (inputs)
- `PRIMARY_OBJECTIVE.md` mục 3
- `config/*.yaml`, `research/04-osm-imdf-tagging/`
- `research/05-market-tools/comparison-and-recommendation.md` (TASK-014)

## Đầu ra mong đợi (expected_outputs)
- `docs/cad-to-gpkg-design.md`: sơ đồ, giao diện CLI (`input → output.gpkg`), schema từng layer, danh sách kiểm tra (CRS, hình học hợp lệ, quan hệ khoá ngoại)

## Tiêu chí hoàn thành (acceptance)
- [ ] Mỗi bước nêu rõ input, output, lỗi có thể gặp
- [ ] Có danh sách test mà TASK-010 phải qua
- [ ] Có mục đặc tả mô-đun xuất gói IMDF (đầu vào, cấu trúc ZIP, chuyển đổi, kiểm tra, test) như phần "Bổ sung phạm vi"
- [ ] Đã push lên `main`

## Phạm vi từng bên
- **claude-mobile**: toàn bộ; chỉ ghi vào `docs/cad-to-gpkg-design.md` (gồm cả mô-đun xuất gói IMDF).

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-mobile | in_review | 2026-11-06T12:16:49+07:00 | spec xong, chờ chủ dự án/laptop duyệt |

## Nhật ký — claude-mobile
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T12:16:49+07:00 | in_review | Viết docs/cad-to-gpkg-design.md (kiến trúc, CLI, 5 bước, schema GPKG, georeference, mô-đun export_imdf, kiểm tra, 16 test T1–T16, 10 mục chưa chốt). Đồng bộ config/tag_mapping.yaml: cột OSM có tiền tố osm_ để tránh trùng cột name của IMDF. |

## Blocker / câu hỏi mở
-
