# Báo cáo môi trường local (TASK-001)

- Máy: Ubuntu (Linux 7.0.0-42-generic), 16GB RAM (~15GiB), không GPU rời
- Kiểm tra lúc: 2026-11-06T02:53Z, bởi claude-laptop
- Trạng thái: **PARTIAL** (phần bắt buộc đã xong; FreeCAD, Blender+Bonsai, LibreCAD chưa cài)

## Công cụ hệ thống

| Công cụ | Trạng thái | Phiên bản | Ghi chú |
|---|---|---|---|
| Python | OK | 3.12.3 | `/usr/bin/python3`; đáp ứng yêu cầu 3.11+ |
| `gdal-bin` (`ogrinfo`) | OK | GDAL 3.8.4 | gói apt `3.8.4+dfsg-3ubuntu3` |
| `qgis` | OK | 3.44.7-Solothurn | gói apt `1:3.44.7+40noble`; còn thư viện `libqgis*3.34.4` cũ cài song song |
| `freecad` / `freecadcmd` | CHƯA CÀI | - | không có trong PATH, dpkg, snap, flatpak |
| Blender + Bonsai | CHƯA CÀI | - | không có trong PATH, dpkg, snap, flatpak; chưa kiểm tra bản portable ngoài PATH |
| `librecad` | CHƯA CÀI | - | không có trong PATH, dpkg, snap, flatpak |

Ba công cụ chưa cài đều là GUI/tuỳ chọn, không chặn pipeline Python. Cài bằng apt/snap cần sudo, chưa thực hiện.

## Python venv (`.venv/`, git-ignore)

Tạo bằng `python3 -m venv .venv`, cài: `ezdxf`, `ifcopenshell`, `shapely`, `pyproj`, `geopandas`, `pyogrio`, `pytest`. Danh sách phiên bản đầy đủ: `requirements.txt`.

| Gói | Phiên bản |
|---|---|
| ezdxf | 1.4.5 |
| ifcopenshell | 0.9.0.post1 |
| shapely | 2.2.0 |
| pyproj | 3.8.0 |
| geopandas | 1.2.0 |
| pyogrio | 0.13.0 |
| pytest | 9.2.0 |
| numpy / pandas | 2.5.4 / 3.1.1 |

Kiểm chứng: `.venv/bin/python -c "import ezdxf, ifcopenshell, shapely, geopandas"` chạy không lỗi.

Lưu ý: `requirements.txt` là bản `pip freeze` trong `.venv` này. Chưa kiểm chứng việc đọc/ghi `.gpkg` bằng pyogrio hay mở file trong GUI QGIS (ngoài phạm vi task này); mới kiểm chứng `qgis --version`.

## Tài nguyên

| Mục | Giá trị |
|---|---|
| Ổ đĩa `/` (nvme0n1p4) | 196G tổng, 20G đã dùng, **167G trống** (11%) |
| RAM | 15GiB tổng, ~10GiB khả dụng lúc đo |

## Tái tạo môi trường

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
