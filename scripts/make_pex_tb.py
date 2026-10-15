#!/usr/bin/env python3
"""Derive a post-layout testbench from a schematic one.

Swaps the four design .include lines for the extracted netlist build/pex/neuron_core_pex.spice and
renames internal nodes to their layout names (vi_conv internals are flattened in the layout):
  xn.xvs.x -> xn.xs   xn.xvk.x -> xn.xk   xn.xvs.gc -> xn.gcs   xn.xvk.gc -> xn.gck
The bias-internal node xn.vn (BIAS/VN in the layout) is dropped from checks and nodesets.

Usage: scripts/make_pex_tb.py spice/neuron/neuron_tb.cir spice/neuron/neuron_pex_tb.cir
"""
import pathlib
import sys

INC = """.include @DIR@/../bias/bias_ref.spice
.include @DIR@/ota5p.spice
.include @DIR@/vi_conv.spice
.include @DIR@/neuron_core.spice"""
REN = {"xn.xvs.gc": "xn.gcs", "xn.xvk.gc": "xn.gck", "xn.xvs.x": "xn.xs", "xn.xvk.x": "xn.xk"}

src, dst = sys.argv[1], sys.argv[2]
t = pathlib.Path(src).read_text()
if INC not in t:
    sys.exit(f"{src}: design .include block not found")
t = t.replace(INC, ".include @DIR@/../../build/pex/neuron_core_pex.spice")
for a, b in REN.items():
    t = t.replace(a, b)
t = t.replace(" + (vecmax(abs(v(xn.vn))) > lim)", "").replace(" v(xn.vn)=0.55", "")
if "xn.vn" in t or "xn.xv" in t:
    sys.exit(f"{src}: unmapped schematic-only node left")
first = t.index("\n")
t = (t[:first] + f"\n* POST-LAYOUT version generated from {src} by scripts/make_pex_tb.py; edit the source, not this file."
     + t[first:])
pathlib.Path(dst).write_text(t)
print(f"wrote {dst}")
