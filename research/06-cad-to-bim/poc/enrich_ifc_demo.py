import sys, ifcopenshell, ifcopenshell.api, ifcopenshell.util.pset as up, ifcopenshell.util.element as ue
import ifcopenshell.util.selector as sel
f = ifcopenshell.open(sys.argv[1])
t = up.get_template("IFC4")
print("Pset_WallCommon props:", [p.Name for p in t.get_by_name("Pset_WallCommon").HasPropertyTemplates][:12])
walls = sel.filter_elements(f, "IfcWall")
print("walls:", len(walls))
mat = ifcopenshell.api.run("material.add_material", f, name="Concrete", category="concrete")
cls = ifcopenshell.api.run("classification.add_classification", f, classification="Demo-Classification")
for w in walls:
    ps = ifcopenshell.api.run("pset.add_pset", f, product=w, name="Pset_WallCommon")
    ifcopenshell.api.run("pset.edit_pset", f, pset=ps, properties={"IsExternal": False, "LoadBearing": False, "Reference": "W-" + str(w.id())})
    ps2 = ifcopenshell.api.run("pset.add_pset", f, product=w, name="Pset_ProjectCustom")  # Pset tự đặt
    ifcopenshell.api.run("pset.edit_pset", f, pset=ps2, properties={"SourceLayer": "A-WALL", "AssumedHeight_m": 3.0})
    ifcopenshell.api.run("material.assign_material", f, products=[w], material=mat)
    ref = ifcopenshell.api.run("classification.add_reference", f, products=[w], identification="XX.01", name="Wall (demo)", classification=cls)
w = list(walls)[0]
print(ue.get_psets(w))
print("material:", ue.get_material(w).Name)
f.write(sys.argv[2]); print("wrote", sys.argv[2])
