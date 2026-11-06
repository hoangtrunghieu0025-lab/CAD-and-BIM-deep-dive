# Tổng quan các chiều BIM 3D → 7D

- **Câu hỏi nghiên cứu**: Mỗi chiều BIM thêm dữ liệu gì, dùng chuẩn/class IFC và công cụ nào; định nghĩa có thống nhất không?
- **Kết luận ngắn**: 3D (hình học + thuộc tính), 4D (tiến độ) và 5D (chi phí) khá thống nhất. 6D và 7D KHÔNG thống nhất: 6D vừa được dùng cho "bền vững/năng lượng" vừa cho "FM/vận hành"; 7D có chỗ dùng cho FM, có chỗ cho dữ liệu cảm biến/phân tích. Với dự án này, ta cố định cách dùng (6D = bền vững, 7D = FM, theo `PRIMARY_OBJECTIVE.md`) và ghi rõ đó là quy ước.
- **Độ tin cậy**: trung bình — định nghĩa lấy từ khảo sát/wiki/blog vendor, không có chuẩn ISO định nghĩa "nD"; chi tiết class IFC chưa đọc toàn văn spec (WebFetch bị chặn, chỉ dùng kết quả tìm kiếm).

## Chi tiết

### Điểm không thống nhất về định nghĩa
- Khảo sát Charef, Alaka, Emmitt (2018): 86% chuyên gia đang dùng 6D xếp 6D = Sustainability; 85% chuyên gia dùng 7D xếp 7D = Facility Management; tài liệu học thuật về 6D/7D rất ít (52 bài về 4D, 15 về 5D, 6 về 6D, 2 về 7D). Chỉ là một khảo sát nên mang tính chỉ thị.
- Wiki Designing Buildings liệt kê 6D = thông tin quản lý cơ sở vật chất, kèm lưu ý "có sự mơ hồ, đôi khi dùng mô tả khác". Richard Saxon (được trích ở đó) đề xuất 6D = thông tin vận hành & bảo trì, 7D = thông tin từ cảm biến/phân tích để vận hành tài sản.
- Một số vendor nói trên 5D (hoặc 7D) "không có đồng thuận" về quy trình BIM tương ứng.
- Hệ quả: khi ghi tài liệu/đặt tên bảng, nên gọi theo nội dung (schedule, cost, sustainability, FM) chứ không chỉ theo số.

### Bảng chiều → dữ liệu thêm → chuẩn/class IFC → công cụ
| Chiều | Dữ liệu thêm | Chuẩn / class IFC liên quan | Công cụ ví dụ | Mức xác minh |
|---|---|---|---|---|
| 2D | Hình học phẳng, layer | DWG/DXF (không phải IFC) | AutoCAD, ezdxf | từ PRIMARY_OBJECTIVE |
| 3D | Hình học 3D, vật liệu, Pset, phân loại, quan hệ không gian | IFC (ISO 16739): IfcProject/IfcSite/IfcBuilding/IfcBuildingStorey/IfcSpace, IfcElement; `IfcRoot.GlobalId` | Revit, ArchiCAD, IfcOpenShell, Bonsai | khái niệm chuẩn, xem `guid-linking.md` |
| 4D | Task, thời lượng, ngày bắt đầu/kết thúc, quan hệ task–cấu kiện | `IfcWorkSchedule`, `IfcTask` (+`IfcTaskTime`), `IfcRelAssignsToProcess` | Navisworks TimeLiner, Synchro, MS Project, Primavera P6, IfcOpenShell Ifc4D | xem `4d-schedule.md` |
| 5D | Khối lượng (quantity), đơn giá, tổng chi phí | `IfcCostSchedule`, `IfcCostItem`, `IfcRelAssignsToControl`, `IfcElementQuantity`/`Qto_*BaseQuantities` | Revit schedules, CostX (chưa xác minh), IfcOpenShell Ifc5D, Bonsai | xem `5d-cost-quantities.md` |
| 6D (bền vững — quy ước ở đây) | Thông số nhiệt, vật liệu, năng lượng, carbon | gbXML (ngoài IFC), `IfcRelSpaceBoundary`, `IfcMaterial*`; Pset nhiệt chưa xác minh | EnergyPlus, DesignBuilder, Tally, One Click LCA, EC3 | xem `6d-sustainability.md` |
| 7D (FM — quy ước ở đây) | Thông tin tài sản, bảo hành, tuổi thọ, bảo trì, sensor | COBie (MVD của IFC), `Pset_Warranty`, `Pset_ServiceLife`, `Pset_ManufacturerTypeInformation`; ISO 19650-3 (AIM) | CAFM/CMMS, Autodesk Tandem, Azure Digital Twins | xem `7d-facility-management-cobie.md` |

### Hình học vs phi hình học và cách lưu (câu hỏi PRIMARY_OBJECTIVE §2)
- Hình học: lưu trong IFC (representation của từng IfcProduct); dùng cho 3D, và là đầu vào để trích footprint cho GIS.
- Phi hình học: Pset/Qto (thuộc tính, khối lượng), quan hệ (`IfcRel*`), process/cost/control (4D, 5D). Có thể giữ trong IFC hoặc tách ra DB quan hệ/graph (RDF/Turtle) và nối bằng GUID — một nguồn tin thứ cấp (Pulse, 2026) mô tả dự án neo tài sản bằng IFC GUID và mô tả quan hệ bằng RDF (chưa xác minh với nguồn gốc).
- COBie: dạng bảng (19 bảng theo slide ĐH Charlotte) hoặc IFC; thích hợp nạp vào CMMS.

## Liên quan đến pipeline CAD → BIM → GPKG
- Phần được đưa sang GIS thực tế nhất: hình học 3D→2D footprint theo tầng (`IfcBuildingStorey`, `IfcSpace`), georeference (`IfcMapConversion`/`IfcProjectedCRS`), và thuộc tính 7D (mã tài sản, loại phòng) làm cột thuộc tính trong GPKG/IMDF `unit`/`occupant`/`amenity`.
- 4D/5D/6D ít có ý nghĩa với indoor mapping; có thể giữ dạng bảng không-hình-học trong GPKG (bảng thuộc tính nối bằng GUID) — đề xuất thiết kế, chưa kiểm chứng.

## Nguồn
- [Charef et al. — Beyond the third dimension of BIM](https://www.research.lancs.ac.uk/portal/en/publications/beyond-the-third-dimension-of-bim(acfb063d-97af-470c-9068-8ed47b124116)/export.html) — truy cập 2026-11-06
- [Designing Buildings — BIM dimensions](https://www.designingbuildings.co.uk/wiki/BIM_dimensions) — truy cập 2026-11-06
- [Revizto — BIM dimensions](https://revizto.com/en/2d-3d-4d-5d-6d-bim-dimensions/) — truy cập 2026-11-06
- [UNC Charlotte — COBie slides](https://bim.charlotte.edu/wp-content/uploads/sites/1263/2025/08/COBie_Slides.pdf) — truy cập 2026-11-06
- Các nguồn khác xem từng ghi chú và `_sources.md`.

## Câu hỏi còn mở
- Có tài liệu chuẩn (ISO/buildingSMART) nào chính thức hoá "nD" không? Chưa tìm thấy.
- Nên chọn 6D = bền vững hay FM cho tài liệu cuối (`docs/`)? Đề xuất: giữ quy ước PRIMARY_OBJECTIVE và ghi chú mơ hồ.
