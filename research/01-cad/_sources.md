# Nguồn thêm vào ở vòng 2 (2026-11-06) — research/01-cad

Ghi chú: không sửa `research/sources.md` theo chỉ đạo; điều phối viên gộp nếu cần. Host `ezdxf.readthedocs.io` vẫn không phân giải DNS trong phiên này; dùng nguồn gốc cùng tác giả trên GitHub (nhánh `master`, có thể lệch bản phát hành). Ngày truy cập tất cả: 2026-11-06.

| Nguồn | URL | Dùng cho |
|---|---|---|
| ezdxf docs recover | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/drawing/recover.rst | recover.readfile, ngoại lệ, chỉ ASCII |
| ezdxf docs disassemble | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/disassemble.rst | hàm, entity không hỗ trợ |
| ezdxf src disassemble | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/disassemble.py | chữ ký, XCLIP, MINSERT |
| ezdxf src insert | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/insert.py | virtual_entities, explode, attribs |
| ezdxf docs insert (blocks) | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/blocks/insert.rst | attribs |
| ezdxf docs concepts/blocks | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/concepts/blocks.rst | dynamic block |
| ezdxf src block | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/block.py | cờ xref, is_xref |
| ezdxf src layer | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/layer.py | is_off/is_frozen/is_locked, ký tự cấm |
| ezdxf src xref | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/xref.py | attach/embed/detach, ConflictPolicy |
| ezdxf docs xref | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/xref.rst | mô tả hàm xref |
| ezdxf src mline | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/mline.py | MLINE virtual_entities/explode |
| ezdxf docs mline | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/dxfentities/mline.rst | MLINE R2000, WCS |
| ezdxf src mtext | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/mtext.py | plain_text |
| ezdxf src path | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/path/path.py | Path.flattening |
| ezdxf tutorial getting_data | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/tutorials/getting_data.rst | cú pháp query |
| ezdxf docs flatten_entities | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/tasks/flatten_entities.rst | chỉ TODO |
| ezdxf docs units | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/concepts/units.rst | $INSUNITS, $MEASUREMENT |
| ezdxf src units | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/units.py | enum, conversion_factor |
| ezdxf docs coordinates | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/concepts/coordinates.rst | WCS/OCS/UCS |
| ezdxf docs ocs | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/concepts/ocs.rst | elevation |
| ezdxf src dxfgfx | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/entities/dxfgfx.py | ocs() |
| ezdxf src math/ucs | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/math/ucs.py | OCS.to_wcs |
| ezdxf docs/src upright | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/upright.py ; https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/upright.rst | upright, upright_all |
| ezdxf docs geodata | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/dxfobjects/geodata.rst | GEODATA |
| ezdxf src layouts/layout | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/layouts/layout.py | get_geodata/new_geodata |
| ezdxf docs layouts | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/layouts/layouts.rst | modelspace "real world units" |
| ezdxf dxfversion.inc | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/dxfversion.inc | bảng phiên bản DXF |
| ezdxf introduction | https://raw.githubusercontent.com/mozman/ezdxf/master/docs/source/introduction.rst | đọc cũ lưu R12 |
| ezdxf odafc docs | https://github.com/mozman/ezdxf/blob/master/docs/source/addons/odafc.rst | config, xvfb, cảnh báo bảo mật |
| ezdxf src odafc | https://raw.githubusercontent.com/mozman/ezdxf/master/src/ezdxf/addons/odafc.py | ngoại lệ, chữ ký, VALID_VERSIONS |
| LibreDWG README | https://raw.githubusercontent.com/LibreDWG/libredwg/master/README | GPLv3+, phiên bản đọc/ghi |
| Web search: ezdxf dynamic block *U | (kết quả: https://ezdxf.readthedocs.io/en/stable/concepts/blocks.html ; https://github.com/haplokuon/netDxf/issues/324 ; https://blog.draftsperson.net/anonymous-blocks-in-autocad/) | `*U` (nguồn thứ cấp, không mở trực tiếp) |

## Host vẫn bị chặn (không xác minh được)
ezdxf.readthedocs.io, www.nationalcadstandard.org, nationalcadstandard.org, blog.draftsperson.net, en.wikipedia.org, help.graphisoft.com.
