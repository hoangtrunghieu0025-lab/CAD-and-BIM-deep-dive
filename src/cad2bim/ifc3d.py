"""Ghi Model3D (analyze3d) ra IFC4: lưới mặt + khung dây, CHƯA có ngữ nghĩa BIM (TASK-018, trước M3).

  * mỗi layer có lưới mặt -> một IfcBuildingElementProxy '<layer>' (IfcPolygonalFaceSet gộp);
  * mỗi layer có khung dây -> một IfcBuildingElementProxy '<layer> (wire)' biểu diễn 'Curve3D':
      LINE/polyline -> IfcPolyline; ARC -> IfcIndexedPolyCurve với IfcArcIndex (cung chính xác, đi qua đầu-giữa-cuối);
      CIRCLE -> IfcIndexedPolyCurve gồm hai IfcArcIndex (bốn điểm cách 90°).
  * ObjectType của phần tử = loại theo layer (kind), vd "unknown"; đơn vị dài ghi tường minh là mét.
"""
from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

import ifcopenshell
import ifcopenshell.api as api

from .analyze3d import Model3D


def write_ifc3d(model: Model3D, dst: str | Path, *, name: str | None = None, exact_arcs: bool = True) -> dict[str, int]:
    f = api.run("project.create_file", version="IFC4")
    proj = api.run("root.create_entity", f, ifc_class="IfcProject", name=name or model.stats.get("file", "model3d"))
    proj.Description = (f"cad2bim 3D; đơn vị {model.stats.get('units')} ({model.stats.get('units_how')}) đã đổi sang mét; "
                        f"$INSUNITS khai báo={model.stats.get('declared_insunits')}; chưa phân loại ngữ nghĩa")
    api.run("unit.assign_unit", f, length={"is_metric": True, "raw": "METRE"})
    ctx = api.run("context.add_context", f, context_type="Model")
    body = api.run("context.add_context", f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)
    site = api.run("root.create_entity", f, ifc_class="IfcSite", name="Site")
    bld = api.run("root.create_entity", f, ifc_class="IfcBuilding", name="Building")
    st = api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="All")
    api.run("aggregate.assign_object", f, products=[site], relating_object=proj)
    api.run("aggregate.assign_object", f, products=[bld], relating_object=site)
    api.run("aggregate.assign_object", f, products=[st], relating_object=bld)

    kinds: dict[str, str] = {}
    mesh_by: dict[str, tuple[list, list]] = defaultdict(lambda: ([], []))
    for m in model.meshes:
        kinds.setdefault(m.layer, m.kind)
        v, fc = mesh_by[m.layer]
        base = len(v)
        v.extend(m.vertices)
        fc.extend([tuple(base + i for i in face) for face in m.faces])
    wire_by: dict[str, list] = defaultdict(list)
    for w in model.wires:
        kinds.setdefault(w.layer, w.kind)
        wire_by[w.layer].append(w)

    n_proxy = n_arc = 0

    def proxy(nm: str, layer: str):
        el = api.run("root.create_entity", f, ifc_class="IfcBuildingElementProxy", name=nm)
        el.ObjectType = kinds.get(layer, "unknown")
        api.run("geometry.edit_object_placement", f, product=el)
        return el

    for layer, (v, fc) in mesh_by.items():
        el = proxy(layer, layer)
        rep = api.run("geometry.add_mesh_representation", f, context=body, vertices=[v], faces=[fc])
        api.run("geometry.assign_representation", f, product=el, representation=rep)
        api.run("spatial.assign_container", f, products=[el], relating_structure=st)
        n_proxy += 1
    for layer, ws in wire_by.items():
        el = proxy(f"{layer} (wire)", layer)
        items = []
        for w in ws:
            if exact_arcs and w.shape == "arc3":
                pl = f.create_entity("IfcCartesianPointList3D", [list(p) for p in w.pts])
                items.append(f.create_entity("IfcIndexedPolyCurve", pl, [f.create_entity("IfcArcIndex", (1, 2, 3))], False))
                n_arc += 1
            elif exact_arcs and w.shape == "circle4":
                pl = f.create_entity("IfcCartesianPointList3D", [list(p) for p in w.pts])
                items.append(f.create_entity("IfcIndexedPolyCurve", pl, [f.create_entity("IfcArcIndex", (1, 2, 3)),
                                                                          f.create_entity("IfcArcIndex", (3, 4, 1))], False))
                n_arc += 1
            else:
                pts = w.pts if w.shape == "polyline" else w.pts + ([w.pts[0]] if w.shape == "circle4" else [])
                items.append(f.createIfcPolyline([f.createIfcCartesianPoint(list(p)) for p in pts]))
        rep = f.createIfcShapeRepresentation(body, "Body", "Curve3D", items)
        api.run("geometry.assign_representation", f, product=el, representation=rep)
        api.run("spatial.assign_container", f, products=[el], relating_structure=st)
        n_proxy += 1
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    f.write(str(dst))
    return {"proxies": n_proxy, "exact_arcs": n_arc, "faces": sum(len(fc) for _, fc in mesh_by.values()),
            "wires": sum(len(v) for v in wire_by.values())}
