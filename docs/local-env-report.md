# Báo cáo môi trường local (TASK-001)

- Máy: Ubuntu (Linux 7.0.0-42-generic), 16GB RAM (~15GiB), không GPU rời
- Kiểm tra lúc: 2026-11-06T09:53+07:00, bởi claude-laptop
- Trạng thái: **PARTIAL** (phần bắt buộc đã xong; LibreCAD, Blender 5.0.1 và Bonsai đã cài và kiểm chứng; FreeCAD 1.1.4 đã cài bằng AppImage (2026-11-08, TASK-016))

## Công cụ hệ thống

| Công cụ | Trạng thái | Phiên bản | Ghi chú |
|---|---|---|---|
| Python | OK | 3.12.3 | `/usr/bin/python3`; đáp ứng yêu cầu 3.11+ |
| `gdal-bin` (`ogrinfo`) | OK | GDAL 3.8.4 | gói apt `3.8.4+dfsg-3ubuntu3` |
| `qgis` | OK | 3.44.7-Solothurn | gói apt `1:3.44.7+40noble`; còn thư viện `libqgis*3.34.4` cũ cài song song |
| `freecad` | **1.1.4** (AppImage) | `~/apps/FreeCAD_1.1.4-Linux-x86_64-py311.AppImage` | Cài 2026-11-08 bằng AppImage (783 MB, không cần `sudo`) thay cho snap vì snap kéo thêm `kf6-core24`. Chạy `~/apps/FreeCAD_...AppImage <file>`. Đã mở `samples/sample-building.ifc`: 2 tầng (0 mm, 3000 mm), 26 IfcSpace (TASK-016). `--version` không in số phiên bản, xem tiêu đề cửa sổ hoặc Help → About. `freecadcmd` chưa kiểm: chạy console với script nhập IFC bị hết thời gian chờ |
| Blender | OK | 5.0.1 (build 2026-02-06) | snap `blender --classic --channel=5.0/stable` (apt chỉ có 4.0.2, quá cũ cho Bonsai ≥ 4.2; kênh mặc định 5.2.x vượt `blender_version_max` = 5.1.0 của Bonsai) |
| Bonsai | OK | 0.9.0-post1 (py311) | extension từ extensions.blender.org, sha256 `c6e486d0…` đã kiểm; cài bằng `blender --command extension install-file -r user_default --enable bonsai.zip`. Kiểm chứng: Blender chạy nền nạp `samples/sample-building.ifc` bằng `bpy.ops.bim.load_project`: schema IFC4, 2 tầng (Elevation 0.0 và 3.0), 26 IfcSpace, 24 IfcDoor, 8 IfcWall |
| `librecad` | OK | 2.2.0.2 | `sudo apt install librecad` (universe). Kiểm chứng: `librecad dxf2pdf -a` xuất `samples/sample-floor-1.dxf` thành PDF; ảnh dựng lại: `docs/assets/librecad-sample-floor-1.png` (12 phòng P101–P112, hành lang, cung cửa, nhãn). Chưa nhìn trực tiếp giao diện/bảng layer của LibreCAD |

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
