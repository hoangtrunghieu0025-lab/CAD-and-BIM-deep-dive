# Báo cáo tổng hợp ngày 09/11/2026 (GMT+7)

Gộp và tóm tắt từ ba báo cáo cùng ngày, đã bỏ phần trùng. Chi tiết kỹ thuật nằm ở các tệp được dẫn chiếu.

Ba báo cáo gốc:
- [09:47](report-2026-11-09-0947.md): tiến độ nghiên cứu (TASK-017) và xây dựng `cad2bim` v2 (TASK-018), số liệu đánh giá trên bản vẽ thật.
- [15:20](report-2026-11-09-1520.md): luồng AI đọc ảnh vẽ từ DXF, công nghệ và dữ liệu mẫu theo từng công đoạn. Viết cho bài toán dựng IFC từ đầu, trước chỉ đạo lần 2 của mentor.
- [18:18](report-2026-11-09-1818.md): công việc trong ngày, hai lần chỉ đạo của mentor, vấn đề mở và việc tiếp theo.

1. **Bối cảnh và trạng thái task.** Mục tiêu chính là chuyển CAD/BIM sang GeoPackage chuẩn OSM Simple Indoor Tagging và IMDF, mở được trong QGIS. Các task liên quan:
   - TASK-010 (pipeline DXF/IFC sang GPKG): xong.
   - TASK-011 (kiểm GPKG trong QGIS): đang chờ duyệt, còn thiếu 3 ảnh chụp giao diện.
   - TASK-017 (nghiên cứu cách chuyển CAD sang BIM): đang chờ duyệt.
   - TASK-018 (khung `cad2bim` v2: đọc DXF, phân loại layer, làm sạch hình học, dựng tường, bộ đánh giá): đang làm.

2. **Kết quả trong ngày.**
   - Viết lại khung `cad2bim` v2 trong `src/cad2bim/` và thêm bộ đọc 3D. Chạy trên 91 bản vẽ DXF thật: 91/91 không lỗi, 31 file có phần tử nhận dạng được. Số phần tử chưa được kiểm đúng sai vì chưa có đáp án. Test: 177 đạt.
   - Cài ODA File Converter để đổi DWG sang DXF (đóng nguồn, không đóng gói vào repo). Một file không chuyển được, đã bỏ qua.
   - Xóa kho mẫu công khai theo yêu cầu, nên các chỉ số cũ như 0/78 chỉ còn giá trị tham khảo.
   - Cầu nối thử DXF sang IFC cho ra tường, cửa, phòng nhưng phòng còn thô. Phát hiện lỗi đơn vị `.MILLI.`, mới sửa ở một tệp.

3. **Chỉ đạo của mentor.** Lần 1: đầu vào chỉ là CAD 2D chi tiết, cần chuyển sang IFC ít mất thông tin nhất rồi làm giàu. Từ đó đề xuất luồng AI đọc ảnh vẽ, phương án rule-based khi không dùng được LLM vì bảo mật, và thư viện pattern. Lần 2 (đổi phạm vi): bên bạn **đã có BIM**, nhưng thiếu `IfcSpace` và `IfcRelSpaceBoundary`; việc cần làm là suy các thông tin này từ CAD và BIM hiện có, sau đó xuất geodata. Khung rule rút còn khoảng 4 nhóm: căn chỉnh CAD với BIM, ghép phần tử, dựng phòng, quan hệ giữa các phòng. Georeference không suy được từ hai nguồn này, cần `IfcMapConversion` hoặc điểm điều khiển.

4. **Tài liệu đã tạo.** Thiết kế mục 8 trong `research/06-cad-to-bim/cad2bim-framework-design.md`, nhật ký TASK-018, 5 nguồn mới trong `research/sources.md`, hai trang artifact riêng tư (báo cáo luồng AI và POC mô phỏng). Các tài liệu viết trước chỉ đạo lần 2 là cho bài toán dựng IFC từ đầu, nên cần điều chỉnh.

5. **Vấn đề mở.**
   - Chưa có cặp IFC và DXF thật của cùng một công trình, nên chưa đo được căn chỉnh và độ đúng của phòng.
   - Lỗi đơn vị `.MILLI.` còn ở 3 tệp thử.

6. **Việc tiếp theo.** Hỏi mentor các câu trên và lấy cặp IFC với DXF thật; cập nhật thiết kế và TASK-018 theo phạm vi mới; thử nguyên mẫu căn chỉnh và dựng `IfcSpace` trên dữ liệu mẫu; sửa lỗi đơn vị; hoàn tất `compare.py` và `synth.py`.
