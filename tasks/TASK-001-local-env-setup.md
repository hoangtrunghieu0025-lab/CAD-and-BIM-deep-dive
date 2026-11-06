---
id: TASK-001
title: Kiểm tra và cài môi trường local (Ubuntu)
assignees: [claude-laptop]
created_by: claude-mobile
created_at: 2026-11-06T02:31:35Z
updated_at: 2026-11-06T02:31:35Z
status: todo
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
- [ ] `python -c "import ezdxf, ifcopenshell, shapely, geopandas"` chạy không lỗi trong `.venv`
- [ ] `ogrinfo --version` và `qgis --version` in được phiên bản
- [ ] Hai file đầu ra đã commit và push lên `main`

## Phạm vi từng bên
- **claude-laptop**: toàn bộ; được ghi `docs/local-env-report.md`, `requirements.txt`.
- **claude-mobile**: không ghi hai file này.

---

# Tiến độ

## Tổng quan
| Bên | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-laptop | todo | 2026-11-06T02:31:35Z | chưa nhận |

## Nhật ký — claude-laptop
| Thời điểm (UTC) | Trạng thái | Nội dung |
|---|---|---|

## Blocker / câu hỏi mở
-
