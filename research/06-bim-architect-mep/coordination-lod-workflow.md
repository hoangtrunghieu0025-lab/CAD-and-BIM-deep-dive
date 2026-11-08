# Điều phối Kiến trúc ↔ MEP, clash detection và LOD

- **Câu hỏi nghiên cứu**: Kiến trúc và MEP phối hợp thế nào; LOD nào phù hợp để điều phối?
- **Kết luận ngắn**: Mỗi bộ môn dựng model riêng, link/federate để điều phối. Kiến trúc cung cấp phòng, tường, trần; MEP đặt Space, thiết bị, tuyến ống/cáp trong các không gian đó. Clash detection (thường Navisworks) chạy trên model liên kết. BIMForum đặt LOD 350 cho điều phối trade.
- **Độ tin cậy**: trung bình — nguồn là bài báo BD+C, blog vendor; chưa đọc bản gốc BIMForum LOD Specification.

## Chi tiết
### LOD (theo BIMForum, qua bài BD+C)
- AIA E202 (2008) đưa LOD 100–500; AIA G202-2013 làm rõ 100/200/300/400; BIMForum thêm **350** cho điều phối trade và hoãn 500.
- 100: ký hiệu/placeholder. 200: đối tượng generic, kích thước/vị trí gần đúng. 350: hệ thống cụ thể + giao diện với hệ khác. 400: thêm chi tiết chế tạo/lắp đặt. 500: hoàn công (mô tả AIA). Bản gốc 300 chưa trích được.
- Spec tổ chức theo CSI Uniformat 2010 (mở rộng đến cấp 4).
- Lưu ý `PRIMARY_OBJECTIVE.md`: ISO 7817-1 dùng LOIN; "LOD" ở đây là Level of Development (BIMForum/AIA) — khác nhau.
- Thực hành (blog vendor, độ tin cậy thấp): LOD 200 cho xung đột hệ thống lớn sớm, 300–350 cho điều phối chi tiết; trên 350 thường giải quyết tại công trường.

### Quy trình điều phối
1. Link model kiến trúc vào MEP (Revit link native, không cần IFC).
2. MEP đặt Space theo Room kiến trúc; tính tải; dựng hệ thống.
3. BIM manager chạy clash (Navisworks) giữa kiến trúc, kết cấu, MEP, PCCC; phát hành issue (BCF — xem `PRIMARY_OBJECTIVE.md`).
4. Lặp đến khi federated model sạch; xuất bản vẽ.
5. Deliverable điển hình: model từng bộ môn, model điều phối, báo cáo clash, as-built.

## Liên quan đến pipeline CAD → BIM → GPKG
- Dự án chỉ cần LOD thấp–vừa (hình học 2D + ngữ nghĩa phòng/cửa); không cần LOD 350+.
- Điều phối giữa bộ môn gợi ý: dùng `GlobalId` làm khoá liên kết (xem `research/03-bim-pipeline-3d-7d/guid-linking.md`).

## Nguồn
- [BD+C – Level of Development: Will a new standard bring clarity](https://www.bdcnetwork.com/home/article/55144799/level-of-development-will-a-new-standard-bring-clarity-to-bim-model-detail) — truy cập 2026-11-08 (qua tóm tắt tìm kiếm)
- [ArchGyan – BIM for MEP Engineers](https://archgyan.com/bim-mep-engineers-coordinating-models/) — truy cập 2026-11-08 (blog, tin cậy thấp)
- [United-BIM case study](https://www.united-bim.com/?p=40007) — truy cập 2026-11-08 (vendor, tin cậy thấp)

## Câu hỏi còn mở
- Đọc bản gốc BIMForum LOD Specification (bimforum.org/lod) để xác minh định nghĩa LOD 300 và bảng theo hạng mục MEP.
- ISO 19650 / IDS cho yêu cầu thông tin MEP: chưa tra.
