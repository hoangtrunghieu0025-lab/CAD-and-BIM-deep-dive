# Quy ước đặt tên layer phổ biến

- **Câu hỏi nghiên cứu**: Các chuẩn đặt tên layer nào phổ biến và nên ánh xạ layer → loại đối tượng thế nào cho bản vẽ không theo chuẩn?
- **Kết luận ngắn** (2–4 dòng): Chuẩn quốc tế/US/UK (ISO 13567, NCS/AIA, AEC UK/BS 1192) đều cấu trúc theo trường: discipline/agent – nhóm đối tượng – phần mô tả/presentation. Thực tế nhiều bản vẽ (đặc biệt Việt Nam) không theo chuẩn nào ⇒ mapping phải là file cấu hình theo dự án, hỗ trợ regex/glob và fallback.
- **Độ tin cậy**: trung bình — chi tiết chuẩn lấy từ kết quả tìm kiếm/tài liệu Autodesk và trường đại học; văn bản chuẩn đầy đủ thường trả phí (chưa kiểm tra trực tiếp). Quy ước ở Việt Nam: chưa xác minh.

## Chi tiết

### US National CAD Standard (NCS) / AIA CAD Layer Guidelines
- Tên layer gồm các trường cách nhau bằng dấu gạch: **discipline designator** (A architectural, S structural…) – **major group** (WALL, DOOR, GLAZ…) – **minor group** (FULL, IDEN…) – **status** (tuỳ chọn). Ví dụ: `A-WALL`, `A-WALL-FULL`, `A-DOOR`, `A-DOOR-FULL` (cửa full-height và swing), `A-DOOR-IDEN` (số cửa, hardware group).
- Quy tắc: major group có thể ghép với mọi discipline nếu giữ nguyên định nghĩa; các nguồn mâu thuẫn về việc minor group tự định nghĩa (một nguồn cho phép, nguồn khác không cho major group tự định nghĩa).
- Các layer hay gặp khác (theo NCS/AIA, cần đối chiếu bảng chính thức — chưa xác minh từng tên): `A-AREA` (khu vực/diện tích), `A-FLOR`, `A-GLAZ`, `A-COLS`, `A-ANNO-TEXT`, `A-ANNO-DIMS`. Trong `PRIMARY_OBJECTIVE.md` ví dụ `A-AREA` → IfcSpace chỉ là gợi ý, không phải quy định chuẩn.

### ISO 13567
- Tên layer là chuỗi các trường độ dài cố định, có trường bắt buộc: **agent** (2 ký tự, ví dụ A- kiến trúc, E- điện, S- kết cấu), **element**, **presentation** (2 ký tự, ví dụ E- element graphics, T text, H hatching, D dimensions). Tình trạng các Part của chuẩn: kiểm tra phiên bản hiện hành trước khi dùng.

### AEC (UK) / BS 1192
- Năm trường cách nhau bằng dấu gạch, ví dụ `A-G251-G-WallExtl-Fwd` (agent kiến trúc, element tường ngoài theo Uniclass, presentation graphic, user definition, view). Autodesk AutoCAD Architecture có sẵn layer standard "BS1192" và "AIA" với các trường định nghĩa.

### Thực tế không theo chuẩn
- Tên theo ngôn ngữ địa phương, ví dụ `TUONG`, `CUA`, `COT`, `PHONG` (chưa xác minh — đề xuất từ kinh nghiệm chung, cần xác nhận bằng mẫu thật), hoặc dạng `0`, `Defpoints`, `Layer1`. `Defpoints` là layer mặc định của AutoCAD cho điểm định nghĩa dimension (không in) và nên loại bỏ.
- Tên layer có thể kèm tiền tố xref `XREF|A-WALL`; cần chuẩn hoá bằng cách lấy phần sau `|`.

### Chiến lược mapping đề xuất
1. Chuẩn hoá: upper-case, bỏ tiền tố `xref|`, bỏ khoảng trắng thừa.
2. Quy tắc theo thứ tự ưu tiên: khớp chính xác → glob/regex (ví dụ `^A-WALL(-.*)?$`) → theo tên block → theo màu/linetype (yếu) → fallback `unknown`.
3. Mỗi quy tắc: `layer_pattern`, `object_type` (wall/door/window/space/stair/column/annotation/ignore), `ifc_class` tuỳ chọn.
4. Báo cáo layer không khớp để người dùng bổ sung quy tắc.

Ví dụ cấu hình (minh hoạ, không phải chuẩn):
```yaml
layers:
  - pattern: '^A-WALL(-.*)?$'
    type: wall
    ifc: IfcWall
  - pattern: '^A-DOOR(-.*)?$'
    type: door
    ifc: IfcDoor
  - pattern: '^A-AREA(-.*)?$'
    type: space
    ifc: IfcSpace
ignore: ['^DEFPOINTS$', '.*-DIMS$', '.*-TEXT$']
```

## Liên quan đến pipeline CAD → BIM → GPKG
- Đây là nền cho `config/layer_mapping.yaml`: cần regex, ignore list, và profile theo dự án (NCS, ISO 13567, tuỳ chỉnh).
- Từ `type`/`ifc` đi tiếp sang OSM tag (`indoor=room/corridor/wall`, `door=*`) và IMDF category qua `tag_mapping.yaml`.
- Nên sinh báo cáo "layer thống kê" (số entity theo layer) để hỗ trợ viết mapping nhanh.

## Nguồn
- [AIA CAD layer format — Draftsperson.net](https://blog.draftsperson.net/the-aia-cad-layer-format) — truy cập 2026-11-06 (qua kết quả tìm kiếm)
- [University of Calgary — Layer Naming Convention (dựa trên NCS)](https://live-ucalgary.ucalgary.ca/sites/default/files/teams/223/Design%20Standards/8.4.2%20Layer%20Naming%20Convention.pdf) — truy cập 2026-11-06
- [Autodesk — AIA Long Format layer standard](https://help.autodesk.com/cloudhelp/2024/CHT/AutoCAD-Architecture/files/GUID-FE0C3A9D-838C-4584-9FDB-5195773ECFA6.htm) — truy cập 2026-11-06
- [Autodesk — BS1192 descriptive layer standard](https://help.autodesk.com/cloudhelp/2024/CHT/AutoCAD-Architecture/files/GUID-80C5FD0A-9824-42F5-A5E4-CCDD34C3ACE3.htm) — truy cập 2026-11-06
- [Wikipedia — ISO 13567](https://en.wikipedia.org/wiki/ISO_13567) — truy cập 2026-11-06
- [Arkance — Setting Layer Standards in AutoCAD Part 2 (AEC UK)](https://ukcommunity.arkance.world/hc/en-us/articles/21550671880338-Setting-Layer-Standards-in-AutoCAD-Part-2) — truy cập 2026-11-06

## Kiểm chứng vòng 2 (2026-11-06)
- Vẫn **không** truy cập được (DNS bị chặn): `www.nationalcadstandard.org`, `nationalcadstandard.org`, `blog.draftsperson.net`, `en.wikipedia.org`, `help.graphisoft.com`. Do đó toàn bộ nội dung NCS/AIA, ISO 13567, BS 1192 và quy ước `xref|layer` ở trên giữ nguyên nhãn "qua kết quả tìm kiếm / chưa xác minh từ trang gốc". Tên layer cụ thể (`A-AREA`, `A-FLOR`, `A-GLAZ`, `A-COLS`, `A-ANNO-TEXT`, `A-ANNO-DIMS`) vẫn chưa xác minh. Cần allow thêm các host trên để đóng mục này.
- Mã nguồn ezdxf (`xref.py`) xác nhận tên `DEFPOINTS` được ezdxf coi là tên layer/tài nguyên đặc biệt luôn được giữ nguyên khi nạp (cùng `0`, `STANDARD`, `CONTINUOUS`, `BYLAYER`/`BYBLOCK`) — hỗ trợ gián tiếp việc `Defpoints` là layer mặc định; mô tả "không in" vẫn chưa xác minh.

## Câu hỏi còn mở
- Không truy cập được nationalcadstandard.org (mạng bị chặn, kiểm lại vòng 2): danh sách major group chính thức chưa đối chiếu.
- Quy ước layer thực tế ở Việt Nam / TCVN liên quan (chưa xác minh, cần mẫu thật).
- Có nên dùng đặc trưng phụ (màu, linetype, lineweight) để suy loại khi layer vô nghĩa không.
