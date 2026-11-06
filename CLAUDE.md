# Quy tắc chung cho mọi agent

Mục tiêu dự án: xem `PRIMARY_OBJECTIVE.md`.

## Ngôn ngữ & định dạng
- Viết tiếng Việt; giữ nguyên thuật ngữ kỹ thuật tiếng Anh (IfcSpace, Pset, layer…).
- Mỗi ghi chú research dùng mẫu `research/_templates/finding.md`.

## Độ tin cậy
- Mọi khẳng định kỹ thuật phải có nguồn (URL + ngày truy cập). Thêm nguồn vào `research/sources.md` (chỉ thêm dòng mới, không sửa dòng cũ).
- Không bịa tên chuẩn, class IFC, thuộc tính, tag OSM hay feature IMDF. Không chắc thì ghi rõ "chưa xác minh".

## Phân quyền ghi (tránh xung đột khi chạy song song)
- Mỗi agent research CHỈ ghi vào thư mục `research/NN-<chủ đề>/` của mình; được đọc thư mục khác.
- Chỉ agent `synthesizer` được ghi vào `docs/`.
- Không sửa `PRIMARY_OBJECTIVE.md`, `CLAUDE.md`, `.claude/` nếu không được yêu cầu.

## Đặt tên file
- Theo chủ đề, chữ thường, gạch ngang: `ifc-spatial-structure.md`.

## Cộng tác 2 agent (claude-mobile ↔ claude-laptop)
- Theo `collab/CONTRACT.md`; push thẳng lên `main`, pull --rebase trước khi push. Không dùng mailbox.
- Việc được giao trong `tasks/` (xem `tasks/README.md`); cập nhật tiến độ trong file task của mình.
