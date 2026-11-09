"""THỬ NGHIỆM: gộp các polyface nhỏ của một DXF 3D thành ít polyface lớn (mỗi layer vài khối <= 30000 đỉnh) để
FreeCAD/LibreCAD nạp nhanh. Mở INSERT (<= 3 tầng). Dùng: .venv/bin/python -I mesh3d_merge_dxf.py <in.dxf> <out.dxf> [layer_bỏ,...]
Giới hạn 30000 đỉnh/polyface vì chỉ số đỉnh của polyface trong DXF là số nguyên 16 bit (chưa xác minh với tài liệu gốc)."""
import sys, collections, ezdxf
from ezdxf.render import MeshBuilder
src, dst = sys.argv[1], sys.argv[2]
skip = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else set()
doc = ezdxf.readfile(src)
acc = collections.defaultdict(lambda: ([], []))
def walk(ents, pl, depth):
    for e in ents:
        layer = e.dxf.layer if not (e.dxf.layer == "0" and pl) else pl
        t = e.dxftype()
        if t == "POLYLINE" and e.is_poly_face_mesh:
            mb = MeshBuilder.from_polyface(e); v, f = acc[layer]; b = len(v)
            v.extend((p.x, p.y, p.z) for p in mb.vertices); f.extend([tuple(b + i for i in fc) for fc in mb.faces if len(fc) >= 3])
        elif t == "INSERT" and depth < 3:
            try: walk(list(e.virtual_entities()), layer, depth + 1)
            except Exception: pass
walk(doc.modelspace(), None, 0)
new = ezdxf.new("R2000"); msp = new.modelspace(); n = 0
for layer, (v, f) in acc.items():
    if layer in skip or not f: continue
    if layer not in new.layers: new.layers.add(layer)
    chunk, cv, cf = {}, [], []
    def flush():
        global n
        if cf:
            pf = msp.add_polyface(dxfattribs={"layer": layer}); pf.append_faces([[cv[i] for i in fc] for fc in cf]); n += 1
    for fc in f:
        if len(cv) + len(fc) > 30000: flush(); cv, cf = [], []
        cf.append(tuple(range(len(cv), len(cv) + len(fc)))); cv.extend(v[i] for i in fc)
    flush()
new.saveas(dst); print("polyface lớn:", n, "->", dst)
