#!/usr/bin/env python3
"""Layout of bias_ref (spice/bias/bias_ref.spice): beta-multiplier current reference + start-up.

  ch2 (top)    : M3/M4 gates and sources, MS1A
  PMOS row     : M3 M4 | MS1A (upper) / MS1B (lower), long L=40 pull-ups, all wells = VDD
  ch1          : VN VP NS ST ST1 VDD VSS
  NMOS row     : M2a M2b M1 M2c M2d (M1 at the centroid of the 4x device) | MS2 MS3 | R1
  ch0 (bottom) : VSS
Spines at the left edge join nets present in several channels. Ports (metal3, left edge):
VDD VSS VP VN.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import maglib as M
from router import Router

FET = dict(nf=1, guard=1, topc=1, botc=0, viagl=100)
GAP = 0.5            # bbox gap between devices sharing a well / substrate
SPINES = {"VSS": 0.8, "VDD": 1.6, "VP": 2.4, "ST1": 3.2, "VN": 4.0}
X0 = 5.2             # first device column (spines and ports to the left)


def build():
    d = M.generate([
        ("nfet", dict(w=20, l=2, **FET)),        # M1, M2
        ("nfet", dict(w=16, l=0.5, nf=1, guard=1, topc=1, botc=0, viagr=100)),  # MS2
        ("nfet", dict(w=1, l=1, **FET)),         # MS3
        ("pfet", dict(w=16, l=2, **FET)),        # M3, M4
        ("pfet", dict(w=0.42, l=40, **FET)),     # MS1A, MS1B
        ("rxh141", dict(l=17, guard=1, viagl=100)),
    ])
    n20, ms2_d, ms3_d, p16, ms1_d, r1_d = d.values()

    c = M.Cell("bias_ref")
    r = Router(c)

    # vertical plan
    ch0_y = 1.4
    nrow_y = 2.6
    nrow_h = max(n20.bbox.h, ms2_d.bbox.h, r1_d.bbox.h)
    ch1_y0 = nrow_y + nrow_h + 1.4
    ch1_n = 8
    prow_y = ch1_y0 + (ch1_n - 1) * M.TRACK_PITCH + 1.4
    prow_top = prow_y + p16.bbox.h
    ch2_y0 = prow_top + 1.4

    # NMOS row: M2a M2b M1 M2c M2d | MS2 MS3 | R1   (bottoms aligned)
    x = X0
    row = {}
    for name, dev, orient in (("M2a", n20, "N"), ("M2b", n20, "N"), ("M1", n20, "N"),
                              ("M2c", n20, "N"), ("M2d", n20, "N"), ("MS2", ms2_d, "FS"),
                              ("MS3", ms3_d, "N")):
        row[name] = c.place(dev, name, x, nrow_y, orient)
        x += dev.bbox.w + GAP
    x += 0.5
    r1 = c.place(r1_d, "R1", x, nrow_y)
    nrow_right = r1.box.x2

    # PMOS row: M3 M4 | MS1A over MS1B
    x = X0
    m3 = c.place(p16, "M3", x, prow_y)
    x += p16.bbox.w + GAP
    m4 = c.place(p16, "M4", x, prow_y)
    x += p16.bbox.w + GAP
    ms1b = c.place(ms1_d, "MS1B", x, prow_y)
    ms1a = c.place(ms1_d, "MS1A", x, prow_top - ms1_d.bbox.h)
    right = max(nrow_right, ms1a.box.x2) + 1.0

    r.channel("ch0", ch0_y, 2, down=True)
    r.channel("ch1", ch1_y0, ch1_n)
    r.channel("ch2", ch2_y0, 4)

    # NMOS row
    for k in ("M2a", "M2b", "M2c", "M2d"):
        m = row[k]
        r.hook(m, "G", "ch1", "VN")
        r.hook(m, "D", "ch1", "VP")
        r.hook(m, "S", "ch1", "NS")
        r.hook(m, "ringL", "ch0", "VSS")
    m1 = row["M1"]
    r.hook(m1, "G", "ch1", "VN")
    r.hook(m1, "D", "ch1", "VN")
    r.hook(m1, "S", "ch0", "VSS")
    r.hook(m1, "ringL", "ch0", "VSS")
    # MS2 (L=0.5): drain, gate and source strips are only 0.395 um apart, too close for risers
    # to different tracks on one side. Flipped (gate at the bottom -> ch0), source strapped to its
    # own VSS guard ring in metal1, drain alone up to ch1.
    ms2 = row["MS2"]
    r.hook(ms2, "G", "ch0", "VN")
    r.hook(ms2, "D", "ch1", "ST")
    r.hook(ms2, "ringR", "ch0", "VSS")
    s, ring = ms2.pin("S"), ms2.pin("ringR")
    c.rect("metal1", M.Rect(s.x1, s.cy - 0.15, ring.x2, s.cy + 0.15))
    ms3 = row["MS3"]
    r.hook(ms3, "G", "ch1", "ST")
    r.hook(ms3, "D", "ch1", "VDD")
    r.hook(ms3, "S", "ch1", "VN")
    r.hook(ms3, "ringL", "ch0", "VSS")
    r.hook(r1, "R1", "ch1", "NS")
    r.hook(r1, "R2", "ch0", "VSS")
    r.hook(r1, "ringL", "ch0", "VSS")

    # PMOS row
    r.hook(m3, "D", "ch1", "VN")
    r.hook(m4, "D", "ch1", "VP")
    for m in (m3, m4):
        r.hook(m, "G", "ch2", "VP")
        r.hook(m, "S", "ch2", "VDD")
        r.hook(m, "ringL", "ch2", "VDD")
    r.hook(ms1b, "D", "ch1", "ST")
    r.hook(ms1b, "S", "ch1", "ST1")
    r.hook(ms1b, "G", "ch1", "VSS")
    r.hook(ms1b, "ringL", "ch1", "VDD")
    r.hook(ms1a, "D", "ch2", "ST1")
    r.hook(ms1a, "S", "ch2", "VDD")
    r.hook(ms1a, "G", "ch2", "VSS")
    r.hook(ms1a, "ringL", "ch2", "VDD")

    # spines and ports
    r.spine("VSS", SPINES["VSS"], ["ch0", "ch1", "ch2"])
    r.spine("VDD", SPINES["VDD"], ["ch1", "ch2"])
    r.spine("VP", SPINES["VP"], ["ch1", "ch2"])
    r.spine("ST1", SPINES["ST1"], ["ch1", "ch2"])
    r.spine("VN", SPINES["VN"], ["ch0", "ch1"])
    r.port("ch2", "VDD", 0.25, 1, "power")
    r.port("ch0", "VSS", 0.25, 2, "ground")
    r.port("ch2", "VP", 0.25, 3)
    r.port("ch1", "VN", 0.25, 4)
    r.extend("ch0", "VSS", right)
    r.extend("ch2", "VDD", right)
    r.finalize()
    path = c.write()
    print(f"wrote {path}  extent {c.extent()}")
    for name, ch in r.channels.items():
        print(f"  {name}: {sorted(ch.track.items(), key=lambda t: t[1])}")
    return c


if __name__ == "__main__":
    build()
