#!/usr/bin/env python3
"""Top-level layout of neuron_core (spice/neuron/neuron_core.spice).

Floorplan (y up):
  C3   VDD rail for the PMOS row
  row3 PMOS (flipped, gates down): PR1a PR2a PK1a PK2a PK2b PK1b PR2b PR1b      | (VDD spine)
  C2   resistor-array top links, PMOS gates/drains, X, Y, VK, VREF
  row2 bias_ref (left)  | resistor array (37 units) | spines S DK VREF | Cc_s Cc_k
  C1   everything between the rows
  row1 OTA_s OTA_k (left) | I0_s  WK1 WS1 MS MK WS2 WK2  I0_k | Rz array (4 units)
  C0   VSS, Rz links
Macros (ota5p, bias_ref) connect through metal3 port extensions to private riser columns on
their left. Ports of neuron_core (metal3): X, Y, VDD, VSS.

Run with --place-only to write the placement without routing (spacing check).
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import maglib as M
from maglib import Rect
from router import Router

FET = dict(nf=1, guard=1, topc=1, botc=0, viagl=100)
COL = 0.7                 # pitch of macro port riser columns

# resistor array: unit index -> group; chains are wired in index order within a group
ARRAY = ("A B C A A C B A " + "S K O O K S " * 3 + "S K O " + "A B C A A A B A").split()
# chain ends (top end first): group -> (net at first unit's top pad, net at the other end)
CHAIN = {"S": ("X", "XS"), "K": ("VK", "XK"), "O": ("Y", "VSS"),
         "A": ("VK", "VDD"), "B": ("VK", "VREF"), "C": ("VREF", "VSS")}


def chain_hooks(r, arr, group, top_chan, bot_chan):
    """Series-connect the units of `group` (bottom link first) and hook its two ends."""
    units = [i for i, g in enumerate(ARRAY) if g == group]
    first_net, last_net = CHAIN[group]
    r.hook(arr, f"R1_{units[0]}", top_chan, first_net)
    for k, (a, b) in enumerate(zip(units, units[1:])):
        side = "R2" if k % 2 == 0 else "R1"
        chan = bot_chan if side == "R2" else top_chan
        net = f"{group}_{k}"
        r.hook(arr, f"{side}_{a}", chan, net)
        r.hook(arr, f"{side}_{b}", chan, net)
    n = len(units)
    last_side = ("R1" if n % 2 == 0 else "R2")      # the end not used by the last link
    r.hook(arr, f"{last_side}_{units[-1]}", top_chan if last_side == "R1" else bot_chan, last_net)


def macro_ports(c, r, inst, ports):
    """ports: [(port, net, chan)] nearest column first. Extends each metal3 port left to its
    own column and hooks it to chan with a metal2 riser."""
    x0 = inst.box.x1
    for k, (port, net, chan) in enumerate(ports):
        p = inst.pin(port)
        xcol = M.snap(x0 - COL * (k + 1))
        c.hwire("metal3", xcol, p.cx, p.cy, M.TRACK_W)
        r.hook_m3(xcol, p.cy, chan, net)


def build(place_only=False):
    d = M.generate([
        ("nfet", dict(w=16, l=4, **FET)),
        ("pfet", dict(w=16, l=4, **FET)),
        ("pfet", dict(w=16, l=8, **FET)),
        ("rxh069", dict(l=14.79, nx=37, dummy=1, guard=1, viagl=100)),
        ("rxh069", dict(l=12.5, nx=4, guard=1, viagl=100)),
        ("mim", dict(w=20, l=20)),
    ])
    n16, p16_4, p16_8, rarr_d, rz_d, mim_d = d.values()
    ota = M.load_macro("ota5p")
    bias = M.load_macro("bias_ref")

    c = M.Cell("neuron_core")
    r = Router(c)

    # ---------------- vertical plan
    c0_y = 1.0
    row1_y = 4.6
    row1_top = row1_y + ota.bbox.h
    c1_y0 = row1_top + 1.6
    c1_n = 22
    c1_top = c1_y0 + (c1_n - 1) * M.TRACK_PITCH
    row2_y = c1_top + 3.6                     # room below the caps for their plate tabs
    row2_top = row2_y + max(rarr_d.bbox.h, mim_d.extent.h)
    c2_y0 = row2_top + 1.8                    # >= 1.34 um from the MIM capacitor
    c2_n = 14
    row3_y = c2_y0 + (c2_n - 1) * M.TRACK_PITCH + 1.6
    row3_top = row3_y + p16_8.bbox.h
    c3_y0 = row3_top + 1.4

    # ---------------- left column: macros
    ota_s = c.place(ota, "OTA_S", 8.6, row1_y)
    ota_k = c.place(ota, "OTA_K", ota_s.box.x2 + 0.8 + 6 * COL, row1_y)
    bias_i = c.place(bias, "BIAS", 4.6, row2_y)
    left_end = max(ota_k.box.x2, bias_i.box.x2)

    # ---------------- right region
    xr = left_end + 3.0
    # row 1
    x = xr
    i0_s = c.place(p16_4, "I0_S", x, row1_y)
    x = i0_s.box.x2 + 1.5
    mir = {}
    for name in ("WK1", "WS1", "MS", "MK", "WS2", "WK2"):
        mir[name] = c.place(n16, name, x, row1_y)
        x = mir[name].box.x2 + 0.5
    x += 1.0
    i0_k = c.place(p16_4, "I0_K", x, row1_y)
    rz = c.place(rz_d, "RZ", i0_k.box.x2 + 2.0, row1_y)
    # row 2
    arr = c.place(rarr_d, "RARR", xr, row2_y)
    spine_x = {"S": arr.box.x2 + 1.4, "DK": arr.box.x2 + 2.2, "VREF": arr.box.x2 + 3.0}
    cc_s = c.place(mim_d, "CC_S", arr.box.x2 + 5.0 - (mim_d.extent.x1 - mim_d.bbox.x1), row2_y)
    cc_k = c.place(mim_d, "CC_K", cc_s.extent.x2 + 4.0 - (mim_d.extent.x1 - mim_d.bbox.x1), row2_y)
    # row 3 (flipped: gates face C2)
    x = xr
    pm = {}
    for name, dev in (("PR1A", p16_8), ("PR2A", p16_8), ("PK1A", p16_4), ("PK2A", p16_4),
                      ("PK2B", p16_4), ("PK1B", p16_4), ("PR2B", p16_8), ("PR1B", p16_8)):
        pm[name] = c.place(dev, name, x, row3_y, "FS")
        x = pm[name].box.x2 + 0.5
    right = max(cc_k.extent.x2, x, rz.box.x2) + 1.5
    vdd_spine = right
    right += 1.0

    if place_only:
        path = c.write()
        print(f"placement only: {path}  extent {c.extent()}")
        return c

    r.channel("C0", c0_y, 4)
    r.channel("C1", c1_y0, c1_n)
    r.channel("C2", c2_y0, c2_n)
    r.channel("C3", c3_y0, 1)

    # ---------------- macros
    for o, xn, gn in ((ota_s, "XS", "GS"), (ota_k, "XK", "GK")):
        macro_ports(c, r, o, [("VSS", "VSS", "C0"), ("OUT", gn, "C1"), ("INN", "VREF", "C1"),
                              ("INP", xn, "C1"), ("VP", "VP", "C1"), ("VDD", "VDD", "C1")])
    macro_ports(c, r, bias_i, [("VSS", "VSS", "C1"), ("VDD", "VDD", "C1"), ("VP", "VP", "C1")])

    # ---------------- row 1
    for i0, xn in ((i0_s, "XS"), (i0_k, "XK")):
        r.hook(i0, "G", "C1", "VP")
        r.hook(i0, "D", "C1", xn)
        r.hook(i0, "S", "C1", "VDD")
        r.hook(i0, "ringL", "C1", "VDD")
    for name, g, dn in (("WK1", "GK", "DK"), ("WS1", "GS", "S"), ("MS", "GS", "XS"),
                        ("MK", "GK", "XK"), ("WS2", "GS", "S"), ("WK2", "GK", "DK")):
        m = mir[name]
        r.hook(m, "G", "C1", g)
        r.hook(m, "D", "C1", dn)
        r.hook(m, "S", "C0", "VSS")
        r.hook(m, "ringL", "C0", "VSS")
    # Rz: units 0+1 = Rz_s (GS .. GCS), 2+3 = Rz_k (GK .. GCK), linked at the bottom
    for a, b, gn, gcn, mid in ((0, 1, "GS", "GCS", "RZS_M"), (2, 3, "GK", "GCK", "RZK_M")):
        r.hook(rz, f"R1_{a}", "C1", gn)
        r.hook(rz, f"R1_{b}", "C1", gcn)
        r.hook(rz, f"R2_{a}", "C0", mid)
        r.hook(rz, f"R2_{b}", "C0", mid)
    r.hook(rz, "ringL", "C0", "VSS")

    # ---------------- row 2: resistor array
    for g in "SKOABC":
        chain_hooks(r, arr, g, "C2", "C1")
    r.hook(arr, "ringL", "C1", "VSS")
    for net, x in spine_x.items():
        r.spine(net, x, ["C1", "C2"])
    # capacitors: bottom plate (metal3) = X node, top plate (metal4) = Rz midpoint side
    for cc, xn, gcn in ((cc_s, "XS", "GCS"), (cc_k, "XK", "GCK")):
        mc = cc.extent
        bx = M.snap(mc.x1 + 2.0)                         # bottom-plate tab
        c.rect("metal3", Rect(bx - 0.3, mc.y1 - 1.0, bx + 0.3, mc.y1 + 0.2))
        r.hook_m3(bx, mc.y1 - 0.75, "C1", xn)
        tp = cc.pin("C1")                                # top plate (metal4)
        tx = M.snap(tp.cx - 3.0)
        c.rect("metal4", Rect(tx - 0.3, mc.y1 - 2.3, tx + 0.3, tp.y1 + 0.5))
        c.via3(tx, mc.y1 - 2.05)
        c.rect("metal3", Rect(tx - 0.25, mc.y1 - 2.95, tx + 0.25, mc.y1 - 1.8))
        r.hook_m3(tx, mc.y1 - 2.7, "C1", gcn)

    # ---------------- row 3 (PMOS, flipped)
    pmos = {"PR1A": ("S", "S"), "PR1B": ("S", "S"), "PR2A": ("S", "Y"), "PR2B": ("S", "Y"),
            "PK1A": ("DK", "DK"), "PK1B": ("DK", "DK"), "PK2A": ("DK", "S"), "PK2B": ("DK", "S")}
    for name, (g, dn) in pmos.items():
        m = pm[name]
        r.hook(m, "G", "C2", g)
        r.hook(m, "D", "C2", dn)
        r.hook(m, "S", "C3", "VDD")
        r.hook(m, "ringL", "C3", "VDD")

    # ---------------- power spines and cell ports
    r.spine("VSS", 1.0, ["C0", "C1"])
    r.spine("VDD", vdd_spine, ["C1", "C3"])
    r.port("C2", "X", right, 1)
    r.port("C2", "Y", right, 2)
    r.port("C3", "VDD", right, 3, "power")
    r.port("C0", "VSS", right, 4, "ground")
    r.finalize()
    path = c.write()
    print(f"wrote {path}  extent {c.extent()}")
    for name, ch in r.channels.items():
        used = max(ch.track.values()) + 1
        print(f"  {name}: {used}/{ch.max_tracks} tracks")
    return c


if __name__ == "__main__":
    build(place_only="--place-only" in sys.argv)
