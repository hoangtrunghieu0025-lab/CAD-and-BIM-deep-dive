# 6D — Bền vững / năng lượng

- **Câu hỏi nghiên cứu**: 6D thêm dữ liệu gì, đi qua chuẩn/công cụ nào, và định nghĩa có thống nhất không?
- **Kết luận ngắn**: Trong tài liệu này 6D = bền vững (năng lượng, carbon, vật liệu), theo PRIMARY_OBJECTIVE; nhưng nhiều nơi dùng 6D = FM (xem `dimensions-overview.md`). Phân tích năng lượng thường đi qua gbXML hoặc IFC (space boundary) vào EnergyPlus; carbon qua quantity + dữ liệu EPD/LCA (Tally, One Click LCA, EC3).
- **Độ tin cậy**: thấp–trung bình — nhiều nguồn là blog/vendor; chưa xác minh được Pset nhiệt cụ thể của IFC.

## Chi tiết

### Dữ liệu thêm
- Năng lượng: hình học bao che, vùng nhiệt (space), thông số nhiệt (hệ số truyền nhiệt, dẫn nhiệt, truyền sáng), lớp tường. Wiki OSArch: mô hình năng lượng nên gọn, chỉ giữ thông tin liên quan.
- Carbon/LCA: quantity vật liệu × dữ liệu môi trường (EPD, CSDL nền).

### Chuẩn và định dạng
- gbXML (ngoài IFC): hướng "trực tiếp" hơn cho phân tích năng lượng; IFC mô tả đầy đủ công trình nhưng schema phức tạp, file lớn (nghiên cứu so sánh).
- IFC: một số phần mềm năng lượng đọc IFC qua `IfcRelSpaceBoundary`; OSArch ghi nhận (2022) còn nhiều thách thức với space boundary.
- Chuỗi công cụ ví dụ: IFC/gbXML → pre-processor (DesignBuilder) → IDF → EnergyPlus.
- Class/Pset IFC cụ thể cho thông số nhiệt (vd. `Pset_WallCommon.ThermalTransmittance`, `Pset_SpaceThermalDesign`): chưa xác minh trong phiên này — không dùng trong mapping trước khi kiểm tra spec.

### Công cụ carbon
- Tally: plug-in Revit, nối quantity phần tử với CSDL vòng đời vật liệu; Tally Climate Action Tool xuất quantity Revit sang EC3 (RMI). Một diễn đàn nhận xét chưa có công cụ nào vừa bóc khối lượng nhanh vừa gán EPD hiện hành chính xác.
- One Click LCA: nhận RVT, IFC, XLSX, CSV, JSON (theo trang tổng hợp bên thứ ba — cần kiểm chứng với tài liệu chính thức).
- Cách `IfcMaterial`/layer set được khớp với EPD: chưa xác minh.

## Liên quan đến pipeline CAD → BIM → GPKG
- Giá trị trực tiếp thấp. Có thể mang sang GPKG: diện tích/thể tích, vật liệu chính, vùng nhiệt (IfcSpace) dưới dạng thuộc tính; footprint toà nhà (building) là đầu vào cho phân tích năng lượng đô thị (hướng mở rộng, chưa nghiên cứu).

## Nguồn
- [OSArch wiki — Building Energy Modeling](https://wiki.osarch.org/building-energy-modeling-bem/) — truy cập 2026-11-06
- [TU Wien — so sánh IFC/gbXML cho EnergyPlus](https://repositum.tuwien.at/handle/20.500.12708/3091) — truy cập 2026-11-06
- [RMI — Embodied carbon tools](https://rmi.org/embodied-carbon-cities-policy-toolkit/tools-and-calculators) — truy cập 2026-11-06
- [Net Zero Compare — Tally LCA](https://netzerocompare.com/software/tally-lca) — truy cập 2026-11-06
- [Charef et al.](https://www.research.lancs.ac.uk/portal/en/publications/beyond-the-third-dimension-of-bim(acfb063d-97af-470c-9068-8ed47b124116)/export.html) — truy cập 2026-11-06

## Câu hỏi còn mở
- Pset/Qto IFC chuẩn cho thông số nhiệt và cho dữ liệu môi trường; buildingSMART có IDM/MVD cho energy analysis không (hướng tìm: "IFC Space Boundary 2nd level", chưa xác minh).
- IfcMaterial → EPD matching trong thực tế.
