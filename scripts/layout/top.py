#!/usr/bin/env python3
"""Top cell analog_neuron: neuron_core inside the 180 x 115 um boundary, plus the power grid.

  metal5 horizontal rails: VSS at the bottom, VDD at the top (VDD/VSS pins)
  metal4 vertical straps : alternating VSS/VDD; via4 onto their own rail, via3 onto every
                           crossing of the core's metal3 track of the same net (C0 VSS, C3 VDD).
                           Straps are split around the MIM capacitors (metal4 top plates).
  X, Y pins              : the core's metal3 X/Y tracks extended to the right boundary.
"""
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import maglib as M
from maglib import Rect

W, H = 180.0, 115.0
CORE_AT = (6.0, 4.0)            # core-local origin in top coordinates
RAIL_W = 3.0                    # metal5 rail width
STRAP_W = 1.6                   # metal4 strap width
VIA4 = 1.18
VIA4_PAD_M4 = 1.60
VIA4_PAD_M5 = 1.42 + 0.1
KEEPOUT = 1.0                   # clearance from capacitor metal4


def core_geometry():
    """Core-local: metal3 power tracks [(net, y, x1, x2)] and metal4 keep-out rects."""
    path = M.MAGDIR / "neuron_core.mag"
    layers, labels, _ = M.parse_mag(path)
    keep = list(layers.get("metal4", []))
    tf = None
    for line in path.read_text().splitlines():
        f = line.split()
        if f and f[0] == "use":
            cur = f[1]
        elif f and f[0] == "transform":
            tf = [int(v) for v in f[1:7]]
        elif f and f[0] == "box" and tf and cur.startswith("mim_"):
            a, b, c0, d, e, f0 = tf
            x1, y1, x2, y2 = (int(v) for v in f[1:5])
            xs = [a * x + b * y + c0 for x, y in ((x1, y1), (x2, y2))]
            ys = [d * x + e * y + f0 for x, y in ((x1, y1), (x2, y2))]
            keep.append(Rect(min(xs) / 200, min(ys) / 200, max(xs) / 200, max(ys) / 200))
            tf = None
    # power tracks: metal3 rects carrying a VDD/VSS label
    m3 = layers.get("metal3", [])
    tracks = []
    for text, layer, x, y in labels:
        if text in ("VDD", "VSS") and layer == "metal3":
            for r in m3:
                if r.contains(x, y) and r.w > 10 * r.h:
                    tracks.append((text, r.cy, r.x1, r.x2))
    vias = [r for r in layers.get("via2", []) + layers.get("via3", [])]
    return tracks, keep, vias


def core_pins():
    m = M.load_macro("neuron_core")
    return {k: v for k, v in m.pins.items()}


def build():
    core = M.load_macro("neuron_core")
    c = M.Cell("analog_neuron")
    ox, oy = CORE_AT
    inst = M.Inst(core, "CORE", "N", ox, oy)
    c.insts.append(inst)
    ext = inst.extent
    if ext.x1 < 0 or ext.y1 < 0 or ext.x2 > W or ext.y2 > H:
        raise SystemExit(f"core extent {ext} outside {W} x {H}")

    tracks, keep, core_vias = core_geometry()
    tracks = [(n, y + oy, x1 + ox, x2 + ox) for n, y, x1, x2 in tracks]
    core_vias = [v.moved(ox, oy) for v in core_vias]
    keep = [k.moved(ox, oy).grown(KEEPOUT) for k in keep]

    # metal5 rails
    vss_y, vdd_y = 2.0, H - 2.0
    c.hwire("metal5", 0.5, W - 0.5, vss_y, RAIL_W)
    c.hwire("metal5", 0.5, W - 0.5, vdd_y, RAIL_W)
    c.label("VSS", "metal5", Rect(1.0, vss_y - 0.5, 2.0, vss_y + 0.5), 4, "ground")
    c.label("VDD", "metal5", Rect(1.0, vdd_y - 0.5, 2.0, vdd_y + 0.5), 3, "power")

    # metal4 straps, alternating nets, every 10 um
    straps = []
    x = 3.0
    k = 0
    while x < W - 2.5:
        straps.append(("VSS" if k % 2 == 0 else "VDD", M.snap(x)))
        x += 10.0
        k += 1
    rail = {"VSS": vss_y, "VDD": vdd_y}
    n_via3 = 0
    for net, sx in straps:
        lo, hi = vss_y - RAIL_W / 2, vdd_y + RAIL_W / 2
        # blocked y-intervals at this x
        blocks = sorted((b.y1, b.y2) for b in keep if b.x1 - STRAP_W / 2 < sx < b.x2 + STRAP_W / 2)
        segs, y0 = [], lo
        for b1, b2 in blocks:
            if b1 > y0:
                segs.append((y0, b1))
            y0 = max(y0, b2)
        if y0 < hi:
            segs.append((y0, hi))
        ry = rail[net]
        for s1, s2 in segs:
            if not (s1 <= ry <= s2):          # a segment not reaching its own rail is useless
                continue
            c.vwire("metal4", sx, s1, s2, STRAP_W)
            c.rect("metal4", Rect(sx - VIA4_PAD_M4 / 2, ry - VIA4_PAD_M4 / 2, sx + VIA4_PAD_M4 / 2, ry + VIA4_PAD_M4 / 2))
            c.rect("metal5", Rect(sx - VIA4_PAD_M5 / 2, ry - VIA4_PAD_M5 / 2, sx + VIA4_PAD_M5 / 2, ry + VIA4_PAD_M5 / 2))
            c.rect("via4", Rect(sx - VIA4 / 2, ry - VIA4 / 2, sx + VIA4 / 2, ry + VIA4 / 2))
            for tn, ty, tx1, tx2 in tracks:
                if tn == net and s1 + 0.5 < ty < s2 - 0.5 and tx1 + 0.3 < sx < tx2 - 0.3:
                    c.via3(sx, ty)
                    n_via3 += 1
                    # a core via pad on the same track close by would leave a metal3 notch < 0.3 um
                    for v in core_vias:
                        if abs(v.cy - ty) < 0.05 and 0 < abs(v.cx - sx) < 1.2:
                            c.rect("metal3", Rect(min(v.cx, sx) - 0.25, ty - 0.25, max(v.cx, sx) + 0.25, ty + 0.25))

    # X / Y pins: extend the core's metal3 tracks to the right boundary
    for net, idx in (("X", 1), ("Y", 2)):
        p = inst.pin(net)
        c.hwire("metal3", p.cx, W - 0.3, p.cy, M.TRACK_W)
        c.label(net, "metal3", Rect(W - 0.8, p.cy - 0.1, W - 0.4, p.cy + 0.1), idx)

    path = c.write()
    # fixed boundary for the 180 x 115 um slot
    t = path.read_text().replace("<< end >>", f"<< properties >>\nstring FIXED_BBOX 0 0 {M.u(W)} {M.u(H)}\n<< end >>")
    path.write_text(t)
    print(f"wrote {path}; core extent {ext}; straps {len(straps)}; via3 to core power tracks: {n_via3}")
    return c


if __name__ == "__main__":
    build()
