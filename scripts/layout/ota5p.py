#!/usr/bin/env python3
"""Layout of ota5p (spice/neuron/ota5p.spice): 5-transistor OTA, PMOS input pair.

  top channel   : VDD VP T INP INN       (metal3 tracks)
  PMOS row      : MT (tail, own well = VDD) | M1 M2 (input pair, shared well = T)
  middle channel: D1 OUT
  NMOS row      :                          M3 M4 (mirror load, under M1 M2)
  bottom channel: VSS
Ports on the left edge, on metal3: INP INN OUT VP VDD VSS.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import maglib as M
from router import Router

COMMON = dict(nf=1, guard=1, topc=1, botc=0, viagl=100)
WELL_GAP = 2.0          # bbox gap between PMOS wells at different potentials (>= 1.27 + 2 x 0.265)
SAME_WELL_GAP = 0.5     # guard-ring diffusion 0.27 apart; wells still overlap and merge
NMOS_GAP = 0.5
EDGE = 1.0              # free margin left of the devices for the port stubs


def build():
    mt_d, in_d, ld_d = M.generate([
        ("pfet", dict(w=16, l=2, **COMMON)),
        ("pfet", dict(w=10, l=1, **COMMON)),
        ("nfet", dict(w=2, l=2, **COMMON)),
    ]).values()

    c = M.Cell("ota5p")
    r = Router(c)

    # --- vertical plan (y), bottom up
    vss_y = 0.5
    nrow_y = 2.0                                   # NMOS row bbox bottom
    nrow_top = nrow_y + ld_d.bbox.h
    mid_y0 = nrow_top + 1.3                        # middle channel track 0
    prow_y = mid_y0 + 0.8 + 1.3                    # input pair bbox bottom
    prow_top = prow_y + in_d.bbox.h
    top_y0 = prow_top + 1.3

    # --- horizontal plan (x)
    x = EDGE
    mt = c.place(mt_d, "MT", x, prow_top - mt_d.bbox.h)        # tops aligned
    x += mt_d.bbox.w + WELL_GAP
    m1 = c.place(in_d, "M1", x, prow_y)
    x += in_d.bbox.w + SAME_WELL_GAP
    m2 = c.place(in_d, "M2", x, prow_y)
    # NMOS load pair centred under the input pair
    pair_cx = (m1.box.x1 + m2.box.x2) / 2
    nx = pair_cx - (2 * ld_d.bbox.w + NMOS_GAP) / 2
    m3 = c.place(ld_d, "M3", nx, nrow_y)
    m4 = c.place(ld_d, "M4", nx + ld_d.bbox.w + NMOS_GAP, nrow_y)
    right = max(m2.box.x2, m4.box.x2) + EDGE

    r.channel("top", top_y0, ["VDD", "VP", "T", "INP", "INN"])
    r.channel("mid", mid_y0, ["D1", "OUT"])
    r.channel("bot", vss_y, ["VSS"])

    # tail
    r.hook(mt, "S", "top", "VDD")
    r.hook(mt, "ringL", "top", "VDD")
    r.hook(mt, "G", "top", "VP")
    r.hook(mt, "D", "top", "T")
    # input pair (bodies tied to T)
    for m, gnet, dnet in ((m1, "INP", "D1"), (m2, "INN", "OUT")):
        r.hook(m, "G", "top", gnet)
        r.hook(m, "S", "top", "T")
        r.hook(m, "ringL", "top", "T")
        r.hook(m, "D", "mid", dnet)
    # mirror load
    for m, dnet in ((m3, "D1"), (m4, "OUT")):
        r.hook(m, "G", "mid", "D1")
        r.hook(m, "D", "mid", dnet)
        r.hook(m, "S", "bot", "VSS")
        r.hook(m, "ringL", "bot", "VSS")

    # ports on the left edge
    for i, (ch, net, use) in enumerate([("top", "INP", "signal"), ("top", "INN", "signal"),
                                        ("mid", "OUT", "signal"), ("top", "VP", "signal"),
                                        ("top", "VDD", "power"), ("bot", "VSS", "ground")], start=1):
        r.port(ch, net, 0.25, i, use)
    for ch, net in (("top", "VDD"), ("bot", "VSS")):     # power tracks span the block
        r.extend(ch, net, right)
    r.draw_tracks()
    path = c.write()
    print(f"wrote {path}  extent {c.extent()}")
    return c


if __name__ == "__main__":
    build()
