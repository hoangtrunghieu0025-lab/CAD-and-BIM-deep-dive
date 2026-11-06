# OSM Simple Indoor Tagging (SIT) — đối chiếu bảng tag trong PRIMARY_OBJECTIVE

- **Câu hỏi nghiên cứu**: Các tag OSM ở bảng mục 3.3 bước 4a có đúng với Simple Indoor Tagging không? Thiếu gì?
- **Kết luận ngắn**: Hầu hết tag trong bảng tồn tại. Sai/thiếu chính: cửa phải có `indoor=door` + `door=*` (bảng chỉ ghi `door=*`, `entrance=*`); cầu thang theo SIT là `stairs=yes` + `indoor=room|area`, còn `highway=steps` là tag OSM chung (chưa thấy trong SIT); thang máy là `highway=elevator` (kèm `indoor=room`/`area`); thiếu `room=*`, `min_level`/`max_level`.
- **Độ tin cậy**: trung bình-thấp — wiki OSM không fetch được (DNS bị chặn); chỉ có đoạn trích từ WebSearch. Mục "chưa xác minh" cần kiểm lại khi mở được `wiki.openstreetmap.org`.

## Chi tiết — đối chiếu từng dòng

| Dòng bảng PRIMARY_OBJECTIVE | Kết quả | Ghi chú |
|---|---|---|
| Tầng: `level=*`, `level:ref=*`, `repeat_on=*` | Đúng, có thật | `level=*` số (có thể thập phân, danh sách `0;1`, khoảng `0-1`); `level:ref=*` là nhãn in trên bảng chỉ dẫn/nút thang máy (vd K, E, 3), có thể khác `level`; `repeat_on=*` cho đối tượng lặp qua nhiều tầng (thang máy, thang cuốn) — **tầng khởi đầu không nằm trong danh sách** (vd `level=0`, `repeat_on=1;3` → xuất hiện ở tầng 0,1,3). Khoảng với số âm/thập phân có thể mơ hồ (theo trang Talk/proposal; chưa xác minh chi tiết). |
| Phòng: `indoor=room`, `ref`, `name` | Đúng | `indoor=room` = không gian kín có tường bao; mục đích đặt bằng `room=*` (bảng thiếu `room=*`). |
| Hành lang: `indoor=corridor` | Đúng | Wiki hiện coi là loại đặc biệt của `indoor=area` (các trang dịch cũ định nghĩa khác — định nghĩa đã đổi theo thời gian). |
| Tường: `indoor=wall` | Đúng | Tường không đi qua được, thường là way theo đường tim tường; chỉ dùng khi `indoor=room` chưa định nghĩa tường. |
| Cửa: `door=*`, `entrance=*` | **Thiếu** | Cửa nội bộ: node `indoor=door` + `door=*`. Lối vào/ra toà nhà: `entrance=*` (vẫn có thể có `door=*`) thay cho `indoor=door`. Cửa của thang máy: node `indoor=door`/`entrance=*` riêng + `repeat_on=*` (theo trang highway=elevator). |
| Cầu thang: `highway=steps` | **Chưa khớp SIT** | Theo SIT: khu vực cầu thang `stairs=yes` + `indoor=room` (hoặc `indoor=area` nếu không tường), nhiều tầng dùng `level=0;1` / `level=0-1`. `highway=steps` là tag OSM chung cho way bậc thang (dùng cho routing), không thấy trong đoạn trích SIT — chưa xác minh. |
| Thang máy: `highway=elevator` | Đúng | Area `highway=elevator` + `indoor=room` (hoặc `indoor=area`). |
| Khu vực: `indoor=area` | Đúng | Không gian không kín hoàn toàn; tường chỉ có khi có `indoor=wall` hoặc phòng kề. |
| Toà nhà: `building=*`, `building:levels=*` | Đúng nhưng nằm ngoài SIT | Là tag building chuẩn của OSM, không phải phần của `indoor=*`. `building:levels` chưa đối chiếu trực tiếp trong phiên này (chưa xác minh). |

Tag có thể cần thêm (chưa xác minh đầy đủ): `indoor=level` (trang Tag:indoor=level tồn tại — vai trò chính xác chưa đọc được), `indoor=yes` cho node, `min_level`/`max_level`/`building:min_level`, `access=*`, `wheelchair=*`, `conveying=*` (thang cuốn), `door=hinged|sliding|…`.

Lưu ý: trang SIT từng được ghi là "proposal/schema" và được cập nhật gần đây (~102 ngày trước theo đoạn trích) → cần kiểm phiên bản hiện hành.

## Liên quan đến pipeline CAD → BIM → GPKG
- Mapping IfcSpace → `indoor=room` (kín) hay `indoor=area`; IfcDoor → `indoor=door`+`door=*`; IfcBuildingStorey → giá trị `level=*`; IfcStair/IfcTransportElement(ELEVATOR) → `stairs=yes` / `highway=elevator`.
- Giá trị `level` trong OSM là số đã mã hoá tầng nhìn thấy (có thể khác IMDF `ordinal`); nên lưu cả `level` và `level:ref` làm cột riêng trong GPKG.
- Trong GPKG lưu tag OSM thành cột riêng (`indoor`, `level`, `ref`, `name`, `door`…) cộng cột `tags` JSON text cho phần còn lại.

## Nguồn
- [OSM Wiki — Simple Indoor Tagging](https://wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging) — truy cập 2026-11-06 (chỉ đoạn trích tìm kiếm)
- [Tag:highway=elevator](https://wiki.openstreetmap.org/wiki/Tag:highway=elevator) — truy cập 2026-11-06 (đoạn trích)
- [Tag:indoor=level](https://wiki.openstreetmap.org/wiki/Tag:indoor=level) — truy cập 2026-11-06 (đoạn trích)
- [Indoor](https://wiki.openstreetmap.org/wiki/Indoor) — truy cập 2026-11-06 (đoạn trích)

## Câu hỏi còn mở
- Tag chính xác và giá trị `door=*` hợp lệ; vai trò `indoor=level`; xác nhận `highway=steps` trong ngữ cảnh indoor.
- Cách SIT biểu diễn tầng bằng relationship (`type=level`) so với tag `level` trên từng đối tượng — chưa đọc.
