# klayout -zz -r scripts/render_layout.py
# Exports the flattened polygons of selected layers of gds/analog_neuron.gds to
# build/render/polys.json; scripts/plot_layout.py draws them.
import json
import os
import pya

LAYERS = {"nwell": (64, 20), "diff": (65, 20), "tap": (65, 44), "poly": (66, 20), "li1": (67, 20),
          "met1": (68, 20), "met2": (69, 20), "met3": (70, 20), "met4": (71, 20), "met5": (72, 20),
          "capm": (89, 44), "rpoly": (66, 13)}
ly = pya.Layout()
ly.read("gds/analog_neuron.gds")
top = ly.top_cell()
out = {}
for name, (l, d) in LAYERS.items():
    li = ly.find_layer(l, d)
    if li is None:
        continue
    reg = pya.Region(top.begin_shapes_rec(li)).merged()
    polys = []
    for p in reg.each():
        polys.append([[pt.x * ly.dbu, pt.y * ly.dbu] for pt in p.to_simple_polygon().each_point()])
    out[name] = polys
os.makedirs("build/render", exist_ok=True)
json.dump(out, open("build/render/polys.json", "w"))
print({k: len(v) for k, v in out.items()})
