# samples/ — file mẫu để phát triển và test pipeline

Trạng thái: **DONE** (TASK-008, claude-laptop, 2026-11-06). Tất cả file do dự án tự sinh bằng `generate_samples.py`, không dùng dữ liệu bên thứ ba.

## Nguồn và giấy phép

Dữ liệu là toà nhà giả định, không đại diện công trình thật. Tác giả: chủ repo (Hoang Trung Hieu), sinh bằng script trong thư mục này. Chưa có file `LICENSE` ở gốc repo, nên các file mẫu chưa gắn giấy phép chính thức; chủ repo cần chọn giấy phép (gợi ý: CC0 cho dữ liệu mẫu). Không có thành phần nào sao chép từ nguồn có bản quyền.

## Danh sách file

| File | Nội dung |
|---|---|
| `sample-floor-1.dxf` | Mặt bằng tầng 1 (DXF R2010) |
| `sample-floor-2.dxf` | Mặt bằng tầng 2, cùng hình học, đánh số phòng P2xx |
| `sample-building.ifc` | Mô hình IFC4, 2 `IfcBuildingStorey`, cùng bố cục |
| `generate_samples.py` | Script tái tạo toàn bộ file trên |

Tái tạo: `.venv/bin/python samples/generate_samples.py`

## Bố cục (chung cho DXF và IFC)
- Mặt bằng 24 m x 12 m, gốc (0,0) ở góc tây-nam. Mỗi tầng cao 3,0 m (tầng 2 ở cao độ 3,0 m).
- 12 phòng/tầng (mỗi phòng 4 x 5 m): 6 phòng phía nam, 6 phía bắc, hành lang rộng 2 m ở giữa. Tổng 24 phòng + 2 hành lang.
- Tầng 1: phòng P101–P112; tầng 2: P201–P212. P101–P106 phía nam, P107–P112 phía bắc (tương tự tầng 2).
- Mỗi phòng có 1 cửa (rộng 0,9 m, cao 2,1 m) mở ra hành lang.

## DXF
- Đơn vị: mét (`$INSUNITS = 6`). CRS: **không có**, toạ độ cục bộ.
- Layer: `A-WALL` (tường: 1 polyline kín ngoài + các đường ngăn), `A-AREA` (đường bao phòng/hành lang, polyline kín), `A-AREA-IDEN` (TEXT tên phòng), `A-DOOR` (INSERT block `DOOR`).
- Mỗi file: 13 LWPOLYLINE `A-AREA`, 13 TEXT, 12 LINE + 1 LWPOLYLINE `A-WALL`, 12 INSERT. Tên layer chỉ gần giống quy ước AIA, chưa đối chiếu chuẩn (chưa xác minh).

## IFC
- Schema IFC4, đơn vị mét, tạo bằng `ifcopenshell.api`.
- Cây: `IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey (x2)`.
- Mỗi tầng: 13 `IfcSpace` (12 phòng + hành lang, `Name` = mã phòng, `LongName` = tên, có `Pset_SpaceCommon`), 4 `IfcWall` ngoài, 12 `IfcDoor`. Tổng: 26 IfcSpace, 8 IfcWall, 24 IfcDoor.
- `IfcSpace` và `IfcWall` có hình học extrude; `IfcDoor` chỉ có vị trí và kích thước, không có hình học.
- CRS: **không có** `IfcMapConversion` / `IfcProjectedCRS`; toạ độ cục bộ. Pipeline phải gán georeference riêng.
- Chưa kiểm tra bằng viewer GUI (Bonsai/FreeCAD chưa cài).

## Kiểm chứng đã chạy
- `ezdxf.readfile` + `audit()`: 0 lỗi, cả 2 DXF.
- `ifcopenshell.open` đọc được; `ifcopenshell.geom.create_shape` thành công 34/34 phần tử có hình học.
- `ogrinfo -so -al samples/sample-floor-1.dxf` đọc được, 51 feature.


## Mẫu bổ sung (TASK-015)
Sinh bằng `.venv/bin/python samples/generate_samples_extended.py` (tự dựng, không dùng dữ liệu bên thứ ba). Mặt bằng 1 tầng 24 × 12 m, **tường dày 0,2 m** đặt trên trục lưới (nên giữa các phòng có khe 0,2 m), toạ độ cục bộ mét, không CRS.

| File | Nội dung |
|---|---|
| `sample-building-extended.ifc` | IFC4: 10 phòng + hành lang (`IfcSpace`), 16 `IfcWall` có hình học, `IfcStair`, `IfcTransportElement` (ELEVATOR), `IfcColumn`, 3 `IfcFurniture`, 2 `IfcWindow`, 10 `IfcDoor` (có `OperationType`; `Pset_DoorCommon`: `IsExternal`, `FireExit`, `HasDrive`; một cửa lấp `IfcOpeningElement`, tám cửa có thân, một cửa chỉ có placement) |
| `sample-building-ifc2x3.ifc` | IFC2X3 tối thiểu: 2 phòng, hành lang, 2 cửa; không có `IfcMapConversion` |
| `sample-floor-extended.dxf` | DXF: tường dày (polygon kín trên `A-WALL`), phòng `A-AREA`/`A-AREA-IDEN`, cầu thang `A-STRS`, cột `A-COLS`, cửa sổ `A-GLAZ` (LINE), nội thất `A-FURN`, nét chi tiết `A-DETL`, 10 cửa là INSERT (4 cái có ATTRIB `TYPE`/`AUTOMATIC`/`MATERIAL`). Ô thang máy là phòng thường (DXF chưa có quy tắc thang máy) |
| `project-ext-ifc.yaml`, `project-ext-dxf.yaml`, `project-ifc2x3.yaml` | dự án chạy các mẫu trên; hai dự án đầu dùng `options.wall_mode: structure` |

Kết quả mẫu: `samples/out/sample-ext-ifc.gpkg`, `samples/out/sample-ext-dxf.gpkg`. Với `wall_mode: simplified` pipeline cảnh báo khe 33,52 m² (phần tường); với `structure` khe bằng 0.
