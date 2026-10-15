#!/usr/bin/env python3
"""Break the two V->I loops inside the extracted neuron_core netlist for an AC stability test.

In build/pex/neuron_core_pex.spice, the gate of each OTA's + input device (pfet with gate XS and
bulk OTA_S/T; gate XK and bulk OTA_K/T) is moved to XS_BRK / XK_BRK. Inside the subcircuit a 1 GH
inductor closes the loop at DC and a 1 F capacitor couples the AC injection, brought out as new
ports NACS / NACK. Same method as spice/neuron/vi_stab_tb.cir; all extracted parasitics on XS / XK
stay on the loop side.
"""
import pathlib
import re

SRC = pathlib.Path(__file__).resolve().parents[1] / "build" / "pex" / "neuron_core_pex.spice"
DST = SRC.with_name("neuron_core_pex_brk.spice")
t = SRC.read_text()
for x, ota in (("XS", "OTA_S"), ("XK", "OTA_K")):
    pat = re.compile(rf"^(X\d+ {ota}/T ){x}( \S+ {ota}/T sky130_fd_pr__pfet_01v8 .*)$", re.M)
    hits = pat.findall(t)
    if len(hits) != 1:
        raise SystemExit(f"{x}: expected exactly one OTA input device, found {len(hits)}")
    t = pat.sub(rf"\g<1>{x}_BRK\g<2>", t)
t = t.replace(".subckt neuron_core X Y VDD VSS", ".subckt neuron_core X Y VDD VSS NACS NACK", 1)
t = t.replace(".ends", "LBRKS XS XS_BRK 1G\nCBRKS XS_BRK NACS 1\nLBRKK XK XK_BRK 1G\nCBRKK XK_BRK NACK 1\n.ends", 1)
DST.write_text(t)
print(f"wrote {DST}")
