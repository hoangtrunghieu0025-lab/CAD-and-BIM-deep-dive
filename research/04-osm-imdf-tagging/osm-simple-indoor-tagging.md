# OSM Simple Indoor Tagging (SIT) — đối chiếu bảng tag trong PRIMARY_OBJECTIVE

- **Câu hỏi nghiên cứu**: Các tag OSM ở bảng mục 3.3 bước 4a có đúng với Simple Indoor Tagging không? Thiếu gì?
- **Kết luận ngắn**: Hầu hết tag trong bảng tồn tại. Điểm sai/thiếu đã xác minh: (1) cửa nội bộ là node `indoor=door` + `door=*` (bảng chỉ ghi `door=*`, `entrance=*`); (2) khu vực cầu thang là `stairs=yes` + `indoor=room|area`, còn `highway=steps` **có trong SIT** nhưng chỉ cho từng *flight of steps* (way), không cho cả khu cầu thang; (3) `level=*` là **bắt buộc** trên mọi phần tử indoor; (4) thiếu `room=*`, `min_level`/`max_level` trên toà nhà, `indoor=level`.
- **Độ tin cậy**: **cao** — đọc wikitext gốc của trang `Simple_Indoor_Tagging`, `Tag:highway=elevator`, `Tag:highway=steps` (`action=raw`, 2026-11-06 ~11:05 GMT+7).
- **Trạng thái xác minh**: ĐÃ XÁC MINH (TASK-012, claude-laptop). Thay bản cũ chỉ dựa vào đoạn trích tìm kiếm.

## Chi tiết — đối chiếu từng dòng

| Dòng bảng PRIMARY_OBJECTIVE | Kết quả | Căn cứ (trang SIT trừ khi ghi khác) |
|---|---|---|
| Tầng: `level=*`, `level:ref=*`, `repeat_on=*` | **Đúng** | `level` = *"the physical level number"* (0 = mặt đất, −1 = tầng hầm đầu); `level:ref` = số/mã tầng như hiển thị trong toà nhà (K, E, 3, B1, LG), có thể khác `level`; `repeat_on` chỉ dùng cho **node**, "starting level is not included" (vd `level=0` thì `repeat_on=1;3`), ví dụ giá trị `1;3`, `0-6`. |
| Phòng: `indoor=room`, `ref`, `name` | **Đúng** | `indoor=room`: "Conventional room with walls". Mục đích đặt bằng `room=*`; `ref`, `name`, `height` là tag tuỳ chọn. `level=*` là **MANDATORY**. |
| Hành lang: `indoor=corridor` | **Đúng** | "Enclosed walkway area that connects rooms. Like `indoor=area`, not necessarily surrounded by walls." |
| Tường: `indoor=wall` | **Đúng** | Phần tử tường không đi qua được, **ưu tiên way theo đường tim tường**; có thể là area (`indoor=wall` + `area=yes`) cho tường bất quy tắc. Chỉ cần khi tường chưa được xác định bởi `indoor=room`; room mặc định có tường bao. |
| Cửa: `door=*`, `entrance=*` | **Thiếu `indoor=door`** | Cửa = **node** có cả `indoor=door` và `door=*`; cửa là lối vào/ra toà nhà dùng `entrance=*` thay `indoor=door` nhưng vẫn có `door=*`. `door=yes` (loại chưa rõ), `door=no` (lỗ mở không có cánh), `door=<loại>` (xem `Key:door`). Node cửa được chia sẻ giữa các room nối và way tường. Cửa không đặt được trên tường dạng area. |
| Cầu thang: `highway=steps` | **Chưa đúng** cho khu cầu thang | Khu cầu thang = area `stairs=yes` + `indoor=room` (hoặc `indoor=area` nếu không tường); thêm `conveying=yes` cho thang cuốn dạng cầu thang. **Từng đợt bậc** có thể vẽ thêm bằng way `highway=steps` + `level` (+ `conveying=yes` cho thang cuốn); trang `Tag:highway=steps` ghi onWay=yes, onArea=no, onNode=no (area dùng `area:highway=steps`). Nhiều tầng: `level=0;1` hoặc `level=0-1`. |
| Thang máy: `highway=elevator` | **Đúng** | Area `highway=elevator` + `indoor=room` (hoặc `indoor=area` khi không tường). Theo `Tag:highway=elevator`: area cần thêm `area=yes`; cửa thang máy là node riêng `indoor=door` (hoặc `entrance=*`) + `repeat_on=*`, node **thuộc về** area thang máy; nên thêm `door`, `automatic_door`. Thang nghiêng: way `highway=elevator`. Status trang: "de facto". |
| Khu vực: `indoor=area` | **Đúng** | "Area which is not (entirely) surrounded by walls." |
| Toà nhà: `building=*`, `building:levels=*` | Nằm ngoài SIT | Trang SIT **không** nhắc `building:levels`; SIT khuyến nghị `min_level`, `max_level` (và tuỳ chọn `non_existent_levels`) trên building outline hoặc relation, tương thích Simple 3D Buildings. |

### Tag SIT khác đã xác minh
- `indoor=level` (tuỳ chọn): outline của một tầng; key khuyến nghị: `name`, `level:ref`, `height`, `level`. Trang `Tag:indoor=level` chuyển hướng (redirect) về trang SIT.
- `level` nhiều tầng: danh sách `1;2` hoặc khoảng `-1-5`, `-4--2` (trang có ví dụ cho số âm).
- `window=*` (node, có `repeat_on`), `height=*` (m).
- POI đơn giản: node có `level` / `level:ref`; toà nhà có `min_level`/`max_level` để dễ tìm.

### Chưa tìm thấy trong trang SIT
`indoor=yes` cho node, `access=*`, `wheelchair=*`, `building:min_level` — không có trong trang; bản cũ liệt kê chúng là "có thể cần thêm": giữ nhãn **chưa xác minh** cho các tag này (chúng có thể tồn tại ở trang khác của OSM wiki).
Cách SIT biểu diễn tầng bằng relationship `type=level`: trang hiện tại **không** mô tả relationship, chỉ dùng tag `level` trên từng phần tử (ghi chú cũ nghi ngờ có relationship: không có trong bản trang đọc ngày 2026-11-06).

## Liên quan đến pipeline CAD → BIM → GPKG
- IfcSpace → `indoor=room` (kín) hay `indoor=area`/`corridor`; IfcDoor → node `indoor=door` + `door=*` (lối vào toà nhà → `entrance=*`); IfcBuildingStorey → giá trị `level=*`; IfcStair → area `stairs=yes` + `indoor=room|area`; thang máy → area `highway=elevator` + `indoor=room`.
- Mọi phần tử indoor **phải** có `level`. Lưu cả `level` (số vật lý) và `level:ref` (nhãn) thành cột riêng.
- Giá trị `level` OSM (số vật lý) khác `ordinal` IMDF về nguồn gốc; nên map riêng, không ép bằng nhau.
- Trong GPKG: cột riêng cho tag hay dùng (`indoor`, `level`, `level:ref`, `name`, `ref`, `door`, `room`) và cột JSON text cho phần còn lại (đề xuất thiết kế, cột `:` trong tên có thể gây rắc rối SQL → cân nhắc tên `level_ref`).

## Nguồn
- [Simple Indoor Tagging (wikitext)](https://wiki.openstreetmap.org/w/index.php?title=Simple_Indoor_Tagging&action=raw) — truy cập 2026-11-06
- [Tag:highway=elevator (wikitext)](https://wiki.openstreetmap.org/w/index.php?title=Tag:highway%3Delevator&action=raw) — 2026-11-06
- [Tag:highway=steps (wikitext)](https://wiki.openstreetmap.org/w/index.php?title=Tag:highway%3Dsteps&action=raw) — 2026-11-06
- Tag:indoor=level → chuyển hướng tới Simple Indoor Tagging; Indoor → chuyển hướng `Key:indoor` — 2026-11-06

## Chưa xác minh / câu hỏi mở
- Danh sách giá trị hợp lệ của `door=*` (trang `Key:door` chưa đọc).
- `Key:indoor`, `Key:room` (giá trị `room=*`) chưa đọc.
- Tính ổn định của trang SIT (trang ghi đã cập nhật theo workshop 2026); khi cứng hoá vào config, ghi ngày truy cập.
