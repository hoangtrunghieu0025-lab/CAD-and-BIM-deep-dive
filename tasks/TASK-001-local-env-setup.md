---
id: TASK-001
title: Kiểm tra và cài môi trường local (Ubuntu)
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T09:31:35+07:00
updated_at: 2026-11-06T09:55:00+07:00
status: in_review
priority: high
---

## Mô tả
Kiểm tra máy local (Ubuntu, 16GB RAM, không GPU rời) và cài môi trường tối thiểu để chạy pipeline CAD → BIM → GPKG và mở `.gpkg` trong QGIS.

## Đầu vào (inputs)
- `PRIMARY_OBJECTIVE.md` (mục 3.5 công nghệ đề xuất)

## Đầu ra mong đợi (expected_outputs)
- `docs/local-env-report.md`: bảng phiên bản/trạng thái của Python, `qgis`, `gdal-bin` (`ogrinfo`), `freecad`, Blender + Bonsai, `librecad`; dung lượng ổ đĩa trống.
- `requirements.txt` ở gốc repo với phiên bản đã kiểm chứng chạy được.

## Tiêu chí hoàn thành (acceptance)
- [x] `python -c "import ezdxf, ifcopenshell, shapely, geopandas"` chạy không lỗi trong `.venv`
- [x] `ogrinfo --version` và `qgis --version` in được phiên bản
- [ ] Hai file đầu ra đã commit và push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; được ghi `docs/local-env-report.md`, `requirements.txt`.
- **claude-mobile**: không ghi hai file này.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | in_review | 2026-11-06T09:55:00+07:00 | PARTIAL: phần bắt buộc xong; chưa cài FreeCAD/Blender+Bonsai/LibreCAD |

## Nhật ký — claude-laptop
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-06T09:55:00+07:00 | in_review | Tạo `.venv`, cài ezdxf/ifcopenshell/shapely/geopandas...; import OK; `ogrinfo` GDAL 3.8.4, `qgis` 3.44.7. Ghi `docs/local-env-report.md`, `requirements.txt`. FreeCAD, Blender+Bonsai, LibreCAD chưa cài (cần sudo). |

## Blocker / câu hỏi mở
- Có muốn cài FreeCAD, Blender+Bonsai, LibreCAD không (cần sudo)? Hiện chưa cài.
