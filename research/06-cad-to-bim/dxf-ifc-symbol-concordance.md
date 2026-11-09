# Bản quy ước đối chiếu ký hiệu DXF ↔ IFC

- **Câu hỏi nghiên cứu**: Các mẫu ký hiệu thường gặp trong file DXF (cặp mã-giá trị, thực thể, layer, khối) có nghĩa gì bằng ngôn ngữ tự nhiên, và cách diễn đạt tương đương trong IFC (STEP) là gì?
- **Kết luận ngắn**: DXF là danh sách phẳng các cặp `(mã nhóm, giá trị)`; mỗi thực thể chỉ chứa hình học, layer, màu và mã định danh, không chứa quan hệ hay ngữ nghĩa. IFC là đồ thị các đối tượng `#id=LỚP(thuộc tính…)` trỏ tới nhau; hình học chỉ là một nhánh, còn loại đối tượng, vị trí, quan hệ (thuộc tầng nào, đục lỗ ở đâu) và thuộc tính là các nhánh khác. Phần lớn các cặp DXF có thể đối chiếu được; phần ngữ nghĩa (tường, cửa, phòng) thì không có sẵn trong DXF, phải suy ra từ tên layer, tên khối hoặc hình học.
- **Độ tin cậy**: trung bình. Mã nhóm, thuộc tính của thực thể DXF và thứ tự thuộc tính IFC4 đã đối chiếu với thư viện cài cục bộ (`ezdxf` 1.4.5, IfcOpenShell 0.9.0.post1) và với file mẫu trong `samples/`. Chưa đối chiếu với tài liệu gốc của Autodesk (DXF Reference) và buildingSMART (IFC4 docs) trong phiên này. Các chỗ như vậy được đánh dấu **[chưa xác minh với tài liệu gốc]**.

## Chi tiết

### 1. Hai cách tổ chức dữ liệu

| | DXF | IFC (STEP, đuôi `.ifc`) |
|---|---|---|
| Đơn vị lưu | một **cặp hai dòng**: dòng 1 = mã nhóm (group code), dòng 2 = giá trị | một **dòng**: `#số=TÊNLỚP(ô1,ô2,…);` |
| "Mã" cho biết điều gì | mã nhóm cho biết **dòng giá trị ngay sau là loại dữ liệu gì** (vd `8` = tên layer, `10` = x) | **thứ tự ô** trong ngoặc cho biết loại dữ liệu (vd ô thứ 3 của `IfcWall` là `Name`); tên ô nằm trong đặc tả, không nằm trong file |
| Giá trị rỗng | không ghi cặp đó | `$` |
| Tham chiếu | handle (mã `5`) và handle chủ (mã `330`), dạng hex | `#số` trỏ tới dòng khác |
| Số nguyên "nhãn" của lớp | `0` + tên thực thể (`LINE`, `INSERT`…) | tên lớp viết hoa ngay sau dấu `=` (`IFCWALL`) |
| Quan hệ giữa các đối tượng | **không có** (mỗi thực thể đứng riêng) | **là thành phần chính**: các lớp `IfcRel…` |

Ví dụ thật, cùng một ý "một đối tượng":

```
DXF  (sample-floor-1.dxf)                IFC  (sample-building.ifc, dòng 117)
  0 / LINE                               #135=IFCDOOR('3kS_m5FQP3d8IG_fSmD_mP',$,'Cua P101',$,$,#145,$,$,2.1,0.9,$,$,$);
  8 / A-WALL
 10 / 0.0   20 / 5.0   30 / 0.0
 11 / 24.0  21 / 5.0   31 / 0.0
```

Thứ tự ô của lớp IFC4 (đã lấy từ schema IfcOpenShell cục bộ):
- `IfcWall`: GlobalId, OwnerHistory, Name, Description, ObjectType, ObjectPlacement, Representation, Tag, PredefinedType.
- `IfcDoor`: như trên nhưng thêm OverallHeight, OverallWidth, PredefinedType, OperationType, UserDefinedOperationType (sau Tag).
- `IfcSpace`: GlobalId, OwnerHistory, Name, Description, ObjectType, ObjectPlacement, Representation, LongName, CompositionType, PredefinedType, ElevationWithFlooring.

### 2. Bố cục tổng thể của file

| Phần trong DXF | Nghĩa tự nhiên | Tương đương trong IFC |
|---|---|---|
| `HEADER` (`$INSUNITS`, `$EXTMIN`…) | thông tin chung của bản vẽ, trong đó **đơn vị** | `HEADER;` của file STEP (tên file, schema) và **`IfcProject` → `IfcUnitAssignment` → `IfcSIUnit`** cho đơn vị |
| `TABLES` → bảng `LAYER`, `LTYPE`, `STYLE` | danh sách layer, kiểu nét, kiểu chữ được định nghĩa | không có bảng tương đương một-một. Layer có thể ghi bằng `IfcPresentationLayerAssignment`; kiểu nét/màu bằng `IfcStyledItem`, `IfcCurveStyle`, `IfcSurfaceStyle` |
| `BLOCKS` | thư viện khối (ký hiệu dùng lại) | `IfcRepresentationMap` (khuôn hình học dùng lại) và `IfcTypeObject` (như `IfcDoorType`, kiểu đối tượng); mỗi lần đặt dùng `IfcMappedItem` hoặc `IfcRelDefinesByType` |
| `ENTITIES` | các thực thể trong modelspace | các thể hiện `IfcProduct` (`IfcWall`, `IfcDoor`, `IfcSpace`…) trong phần `DATA;` |
| `OBJECTS` | từ điển, layout, vật liệu… | các lớp "định nghĩa" như `IfcPropertySet`, `IfcMaterial` |

Trong hai file mẫu `sample-floor-extended.dxf` và `sample-floor-1.dxf`, bảng đếm thực thể cho thấy `LWPOLYLINE` 35/16, `LINE` 6/13, `INSERT` 10/12, `TEXT` 12/13, `ATTRIB` 12/0, `ARC` 1/1 (cung nằm trong khối cửa).

### 3. Bảng mã nhóm thường gặp (group code)

Kiểm bằng bảng thuộc tính của `ezdxf` 1.4.5 và bằng file mẫu. Thuộc tính trong ngoặc là tên `ezdxf`.

| Mã | Giá trị thường là | Diễn đạt tự nhiên | Tương đương trong IFC |
|---|---|---|---|
| `0` | tên thực thể (`LINE`, `INSERT`, `TEXT`…) | "bắt đầu một thực thể loại này" | tên lớp sau dấu `=` (nhưng DXF chỉ cho loại hình, IFC cho loại **ngữ nghĩa**) |
| `5` (handle) | chuỗi hex, ví dụ `94` | số hiệu duy nhất của thực thể trong file | `#số` (chỉ có nghĩa trong file này) **và** `GlobalId` (22 ký tự, bền vững qua các lần xuất file). Hai thứ này không đồng nhất với handle: handle DXF thường đổi khi lưu lại, `GlobalId` thì phải giữ nguyên |
| `330` (owner) | handle của đối tượng chủ | "thực thể này thuộc về đối tượng nào" (ví dụ thuộc modelspace hoặc một khối) | không có một ô thống nhất; quan hệ chứa nằm trong `IfcRelAggregates` và `IfcRelContainedInSpatialStructure` **[chưa xác minh: đối tượng chủ của `17` trong mẫu có đúng là modelspace]** |
| `100` | tên lớp con, `AcDbEntity`, `AcDbLine`… | nhãn nội bộ phân đoạn dữ liệu của AutoCAD | không có |
| `8` (layer) | tên layer | "thực thể này nằm trên layer tên X" | **không có ô tương đương**. Layer chỉ là chuỗi; muốn giữ phải dùng `IfcPresentationLayerAssignment` hoặc ghi vào Pset. Loại đối tượng (tường, cửa) là **lớp IFC** (`IfcWall`) |
| `62` (color) | số 0–256 | màu theo chỉ số AutoCAD (`256` = theo layer, `0` = theo khối) | `IfcStyledItem` → `IfcSurfaceStyle` / `IfcCurveStyle` (màu RGB) |
| `6` (linetype) | tên kiểu nét | nét liền, nét đứt… | `IfcCurveStyle` (kiểu nét) |
| `370` (lineweight) | số, vd `-3` | độ dày nét vẽ | `IfcCurveStyle` (độ rộng) |
| `210`/`220`/`230` (extrusion) | vector | hướng pháp tuyến của mặt phẳng vẽ (OCS). Khác `(0,0,1)` thì toạ độ phải đổi (hay gặp khi lật gương) | `IfcAxis2Placement3D` (`Axis` = hướng Z, `RefDirection` = hướng X) |
| `10`,`20`,`30` | số thực | x, y, z của điểm thứ nhất (đầu, tâm, điểm chèn… tuỳ thực thể) | `IfcCartesianPoint((x,y,z))` |
| `11`,`21`,`31` | số thực | x, y, z của điểm thứ hai (điểm cuối của LINE; điểm căn chỉnh của TEXT) | một `IfcCartesianPoint` khác trong `IfcPolyline` |
| `40` | số thực | **bán kính** (CIRCLE, ARC) hoặc **chiều cao chữ** (TEXT, ATTRIB) | `Radius` của `IfcCircle`; chiều cao chữ nằm trong `IfcTextStyle…` hoặc `Extent` của `IfcTextLiteralWithExtent` |
| `41`/`42`/`43` | số thực | với INSERT: **hệ số phóng x/y/z**; với LWPOLYLINE: `41` = bề rộng cuối, `42` = **bulge** (độ cong của đoạn đó), `43` = bề rộng cố định | hệ số phóng: `Scale` của `IfcCartesianTransformationOperator`; bulge: cung trong `IfcIndexedPolyCurve` (`IfcArcIndex`) |
| `50` | số thực (độ) | **góc xoay** (INSERT, TEXT), hoặc góc đầu của ARC | `RefDirection` trong `IfcAxis2Placement3D` (IFC lưu hướng, không lưu góc) |
| `51` | số thực (độ) | góc cuối của ARC | tham số cắt `Trim2` của `IfcTrimmedCurve` |
| `2` | chuỗi | **tên khối** (INSERT, BLOCK) hoặc **tên thẻ** (ATTRIB) | tên khuôn: `Name` của `IfcRepresentationMap`/`IfcTypeObject`; tên thuộc tính: `Name` của `IfcPropertySingleValue` |
| `1` | chuỗi | **nội dung chữ** (TEXT, ATTRIB) | `NominalValue` của `IfcPropertySingleValue` hoặc `Literal` của `IfcTextLiteralWithExtent` |
| `66` | số nguyên | cờ "sau INSERT này có ATTRIB đi kèm" | không có (IFC không cần cờ) |
| `70` | số nguyên (bit cờ) | trong LWPOLYLINE: `1` = **đường khép kín**; trong ATTRIB: cờ thuộc tính; trong LAYER: trạng thái layer | đường khép kín: `IfcArbitraryClosedProfileDef` (hoặc điểm đầu = điểm cuối trong `IfcPolyline`) |
| `90` | số nguyên | số đỉnh của LWPOLYLINE | độ dài danh sách điểm |
| `$INSUNITS` (mã `70` trong header) | số, vd `6` = mét | đơn vị của toàn bản vẽ | `IfcSIUnit(.LENGTHUNIT.,$,.METRE.)` (`.MILLI.` nếu mm) |

Quy luật chung (suy ra từ mẫu; **[chưa xác minh với tài liệu gốc]** cho toàn bộ dải số): mã `10–59` là số thực, mã `0–9` là chuỗi, mã `330` là handle.

### 4. Các mẫu cấu trúc thường gặp trong DXF và cách diễn đạt trong IFC

#### 4.1. Một đường thẳng (`LINE`)
- **DXF**: `0/LINE`, `8/<layer>`, điểm đầu `10-20-30`, điểm cuối `11-21-31`.
- **Nghĩa tự nhiên**: nối hai điểm, thuộc layer X. Không nói gì về việc nó là tường, mép tường hay đường trục.
- **IFC**: không có "đường rời". Hình học nằm **bên trong** một đối tượng: `IfcPolyline(Points)` hoặc một cạnh của `IfcIndexedPolyCurve`, bọc trong `IfcShapeRepresentation` của một sản phẩm. Đường trục tường dùng `RepresentationIdentifier='Axis'` **[chưa xác minh với tài liệu gốc]**.

#### 4.2. Đường gấp khúc (`LWPOLYLINE`), hở hoặc khép kín
Mẫu thật trong `sample-floor-extended.dxf`:
```
0:LWPOLYLINE | 5:9B | 330:17 | 100:AcDbEntity | 8:A-WALL | 100:AcDbPolyline
| 90:4 | 70:1 | 10:-0.1 | 20:-0.1 | 10:24.1 | 20:-0.1 | 10:24.1 | 20:0.1 | 10:-0.1 | 20:0.1
```
- **Nghĩa tự nhiên**: một đường qua **4 đỉnh** (`90:4`), **khép kín** (`70:1`): hình chữ nhật từ x = −0,1 tới 24,1 và y = −0,1 tới 0,1, trên layer `A-WALL`. Mỗi cặp `10`/`20` là một đỉnh (chỉ có x, y; độ cao nằm ở `38`/elevation).
- **Đặc điểm**: không có mã `30` cho từng đỉnh; chỉ có x, y.
- **Tương đương IFC (thật trong mẫu `sample-building-extended.ifc`)**: chính hình chữ nhật này được viết thành

```
#273=IFCCARTESIANPOINTLIST2D(((-0.1,-0.1),(24.1,-0.1),(24.1,0.1),(-0.1,0.1),(-0.1,-0.1)));
#274=IFCINDEXEDPOLYCURVE(#273,$,$);
#276=IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#274);
#277=IFCEXTRUDEDAREASOLID(#276,$,#275,3.);        # đùn lên 3,0
#278=IFCSHAPEREPRESENTATION(#11,'Body','SweptSolid',(#277));
#279=IFCPRODUCTDEFINITIONSHAPE($,$,(#278));
#272=IFCWALL('1LPr7y8l5Div$9EX6hzWuZ',$,'Tuong 1',$,$,#290,#279,$,$);
```
  Đọc từ dưới lên: `IfcWall` có ô `Representation` = `#279`, đi xuống `#278`… tới `#273` là danh sách điểm. Lưu ý IFC **đóng đường bằng cách lặp lại điểm đầu** ở cuối (5 điểm cho 4 đỉnh), còn DXF dùng cờ `70:1`.
- **Điểm mất mát chính**: DXF không nói chiều cao tường (3,0); số 3,0 là **thông tin mới** mà đoạn IFC thêm vào, và pipeline hiện coi là giả định (`assumed`).

#### 4.3. Đoạn cong trong polyline (bulge, mã `42`)
- **DXF**: mỗi đỉnh có thể có mã `42`. `bulge = tan(góc cung/4)` **[chưa xác minh với tài liệu gốc]**; `0` là đoạn thẳng; dấu cho biết hướng cong.
- **Nghĩa tự nhiên**: đoạn nối đỉnh này với đỉnh kế tiếp là một cung chứ không phải đoạn thẳng.
- **IFC**: `IfcIndexedPolyCurve` với danh sách `Segments` gồm `IfcLineIndex` và `IfcArcIndex` (cung đi qua ba điểm chỉ số). Pipeline của chúng ta (`read.py`) làm phẳng cung thành các đoạn thẳng ngắn thay vì giữ cung.

#### 4.4. Cung (`ARC`) và vòng tròn (`CIRCLE`)
Mẫu thật (cung cánh cửa, nằm trong khối `DOOR`): `0:ARC | 8:0 | 10:-0.45 | 20:0.0 | 30:0.0 | 40:0.9 | 50:0.0 | 51:90.0`
- **Nghĩa tự nhiên**: cung tròn tâm (−0,45; 0), bán kính 0,9, đi từ góc 0° tới 90° (theo chiều ngược kim đồng hồ, theo quy ước thường gặp của DXF **[chưa xác minh với tài liệu gốc]**). Đây là **vết quét của cánh cửa**, tức bản vẽ mô tả cách cửa mở, không phải hình cánh cửa.
- **Bẫy**: `8:0` nghĩa là cung nằm trên layer `0`, tức sẽ **kế thừa layer của INSERT** (mục 4.6).
- **IFC**: `IfcCircle(Position, Radius)` kết hợp `IfcTrimmedCurve(BasisCurve, Trim1, Trim2, SenseAgreement)` để cắt thành cung. Trong IFC, bề rộng cửa là **số riêng** `OverallWidth`; vết quét không bắt buộc phải có.

#### 4.5. Chữ (`TEXT`, `MTEXT`)
Mẫu thật: `0:TEXT | 8:A-AREA-IDEN | 10:2.0 | 20:2.5 | 30:0.0 | 40:0.4 | 1:P101 | 72:1 | 11:2.0 | 21:2.5 | 31:0.0`
- **Nghĩa tự nhiên**: dòng chữ "P101", cao 0,4, đặt ở (2,0; 2,5), trên layer `A-AREA-IDEN` (tên gợi ý: nhãn khu vực). Mã `72`/`11` là căn chỉnh (**[chưa xác minh với tài liệu gốc]**).
- **IFC**: chữ để hiển thị là `IfcAnnotation` với `IfcTextLiteralWithExtent`. Nhưng thường người ta dùng chữ này để **đặt tên phòng**, tức ô `Name`/`LongName` của `IfcSpace` (như `'P101'`, `'Phong P101'` trong mẫu). Quan hệ "chữ nằm trong vùng khép kín nào" là suy luận hình học của pipeline (`analyze.py`: `pg.contains(Point(t.pts[0]))`), không có trong DXF.

#### 4.6. Khối và INSERT, layer `0` kế thừa
Mẫu thật:
```
0:INSERT | 5:C5 | 330:17 | 8:A-DOOR | 100:AcDbBlockReference | 66:1 | 2:DOOR | 10:2.0 | 20:5.0 | 30:0.0
  0:ATTRIB | 2:TYPE     | 1:swinging
  0:ATTRIB | 2:AUTOMATIC| 1:NO
  0:ATTRIB | 2:MATERIAL | 1:wood
  0:SEQEND
```
- **Nghĩa tự nhiên**: "đặt khối tên `DOOR` tại (2,0; 5,0) trên layer `A-DOOR`; kèm ba thuộc tính: loại *swinging*, tự động *NO*, vật liệu *wood*". Mã `66:1` báo trước rằng có ATTRIB theo sau, kết thúc bằng `SEQEND`.
- **Quy tắc layer `0`**: nét trong khối vẽ trên layer `0` sẽ lấy layer của INSERT (ở đây `A-DOOR`). Nên cung `8:0` ở mục 4.4 thực ra thuộc `A-DOOR`.
- **Tương đương IFC**:
  - khối (`BLOCK`) ↔ khuôn hình học `IfcRepresentationMap` hoặc kiểu `IfcDoorType`;
  - INSERT ↔ **một thể hiện** `IfcDoor` (có `ObjectPlacement`) và có thể dùng `IfcMappedItem` để dùng lại khuôn;
  - điểm chèn `10/20/30` + góc `50` ↔ `IfcLocalPlacement` → `IfcAxis2Placement3D(vị trí, trục Z, trục X)`;
  - ATTRIB ↔ thuộc tính: hoặc ô chuẩn (`OperationType`, v.v.), hoặc `IfcPropertySingleValue` trong `IfcPropertySet` (như `Pset_DoorCommon`/`IsExternal` trong mẫu). **Việc gán `TYPE`/`AUTOMATIC`/`MATERIAL` vào ô nào là quyết định thiết kế của ta** (xem `config/tag_mapping.yaml`), DXF không quy định.
- **Cần nhớ**: INSERT chỉ ghi vị trí và tên khối. Muốn biết hình, phải mở khối (`virtual_entities()`), và vì khối có thể lồng khối nên phải đệ quy (`read.py`, `max_depth=3`).

#### 4.7. Vùng tô (`HATCH`) và hình đặc (`SOLID`)
- **DXF**: `HATCH` = vùng khép kín tô mẫu (ranh giới gồm nhiều đường); `SOLID` = tam giác/tứ giác tô đặc (mẫu thật: bốn điểm `10/11/12/13`).
- **Nghĩa tự nhiên**: chỉ là hình để **trình bày** (gạch tường, tô đen). Không phải phần tử toà nhà.
- **IFC**: `IfcAnnotationFillArea` + `IfcFillAreaStyle` cho phần tô; hoặc bỏ qua. Pipeline v2 xem layer hatch là chú thích và bỏ.

#### 4.8. Tên layer có quy ước
- **DXF**: chỉ là chuỗi `8/A-WALL`. Quy ước đặt tên (ví dụ NCS: `A-WALL` tường, `A-DOOR` cửa, `A-AREA` vùng, `A-GLAZ` kính, `A-COLS` cột, `A-STRS` thang) là thoả thuận của người vẽ, **không được bảo đảm**.
- **IFC**: loại đối tượng là lớp (`IfcWall`, `IfcDoor`, `IfcSpace`, `IfcWindow`, `IfcColumn`, `IfcStair`). Bảng gợi ý của pipeline: xem `config/classify.yaml` (`wall → IfcWall`, `door → IfcDoor`, …).
- **Hệ quả**: layer lạ (`5`, `Layer2`) ⇒ không suy được lớp IFC ⇒ pipeline bỏ hình học. Layer đặt nhầm (`INTERIOR-FURNITURE`) ⇒ suy ra **sai** lớp (`wall`).

#### 4.9. Đơn vị
- **DXF**: số trong file **không mang đơn vị**; đơn vị chung nằm ở `$INSUNITS` trong HEADER (mẫu: `6` = mét), hay ghi sai.
- **IFC**: số cũng không mang đơn vị, nhưng đơn vị được ghi **trong chính file**: `IfcProject` → `IfcUnitAssignment` → `IfcSIUnit(.LENGTHUNIT.,…,.METRE.)`. Nếu dòng này sai thì mọi kích thước sai theo hệ số (đã gặp: ghi `.MILLI.` làm toà nhà 27,6 m thành 27,6 mm).

### 5. Những thứ IFC có mà DXF không có (nên phải suy ra hoặc giả định)

| Trong IFC | Trong DXF | Pipeline làm gì |
|---|---|---|
| Lớp ngữ nghĩa (`IfcWall`) | chỉ có tên layer | đoán từ tên layer/tên khối (`classify.py`) |
| Chiều cao, độ dày tường | không có (tường chỉ là nét) | độ dày suy từ khoảng cách hai nét song song (`derived`); chiều cao theo cấu hình (`assumed`) |
| Quan hệ `IfcRelContainedInSpatialStructure` (thuộc tầng nào) | mỗi file DXF thường là một tầng, không ghi | người dùng khai báo tầng |
| Quan hệ `IfcRelVoidsElement` + `IfcRelFillsElement` (cửa đục vào tường nào) | không có | chưa làm (cửa chưa có tường chủ) |
| Phòng (`IfcSpace`) với ranh giới | chỉ có polyline kín trên layer phòng (nếu có) | lấy polyline kín trên layer phòng; không dựng từ tường |
| `GlobalId` bền vững | handle thay đổi khi lưu lại | `stable_id` băm từ nguồn |
| Thuộc tính (Pset) | chỉ ATTRIB nếu người vẽ nhập | đọc ATTRIB, ghi vào `props`; phần còn lại thiếu |
| Vật liệu, phân loại | không có | không có |

### 6. Tương ứng nhanh với mã nguồn của dự án

| Ở đâu | DXF | IFC |
|---|---|---|
| `Prim.etype` (`read.py`) | mã `0` | — |
| `Prim.layer` | mã `8` (có kế thừa layer `0`) | — |
| `Prim.handle`, `Prim.top` | mã `5`, handle INSERT trên cùng | — |
| `Prim.pts` | `10/20(/30)`, `11/21/31`, các đỉnh đã làm phẳng | `IfcCartesianPoint` |
| `Prim.ins` | `10/20`, `50`, `41`, `42` của INSERT | `IfcLocalPlacement` + `IfcCartesianTransformationOperator` |
| `Prim.attribs` | ATTRIB: mã `2` → mã `1` | `IfcPropertySingleValue` (Name → NominalValue) |
| `BimElement.ifc_class` | — | tên lớp IFC |
| `BimElement.prov.claims` | — | không có tương đương trong IFC chuẩn (ta ghi vào Pset riêng `Pset_Cad2Bim_Provenance`) |

## Liên quan đến pipeline CAD → BIM → GPKG
- Giải thích vì sao bước phân loại theo tên layer là điểm yếu: DXF không có ô "loại đối tượng".
- Gợi ý các việc cho M3 (ghi IFC): cần quyết định tường vẽ thành `IfcWall` với `IfcExtrudedAreaSolid` (như mẫu), cửa là `IfcDoor` với `IfcOpeningElement`/`IfcRelVoidsElement`/`IfcRelFillsElement` (mẫu `sample-building-extended.ifc` đã có đủ ba), phòng là `IfcSpace`.
- Nhắc kiểm đơn vị ngay khi ghi IFC (xem mục 4.9).

## Nguồn
- File mẫu của dự án: `samples/sample-floor-1.dxf`, `samples/sample-floor-extended.dxf`, `samples/sample-building.ifc`, `samples/sample-building-extended.ifc` (tự sinh bởi dự án) — đọc 2026-11-09
- `ezdxf` 1.4.5 cài cục bộ (`DXFATTRIBS` của `Line`, `Arc`, `Circle`, `Insert`, `Text`, `Attrib`, `LWPolyline`) — https://github.com/mozman/ezdxf — kiểm 2026-11-09
- IfcOpenShell 0.9.0.post1 cài cục bộ (schema IFC4: thứ tự thuộc tính các lớp) — https://github.com/IfcOpenShell/IfcOpenShell — kiểm 2026-11-09

## Câu hỏi còn mở
- Đối chiếu từng dòng trong mục 3 với **DXF Reference của Autodesk** và với **IFC4 docs của buildingSMART** (chưa tải trang gốc trong phiên này).
- Công thức bulge, quy ước chiều quay của ARC, bảng dải kiểu giá trị theo mã nhóm: chưa xác minh.
- Mã `330` trong thực thể ENTITIES: đối tượng chủ có đúng là bản ghi của modelspace không?
- IFC4.3 có đổi tên hoặc thêm lớp nào ảnh hưởng bảng tương ứng không: chưa kiểm (mới kiểm IFC4).
