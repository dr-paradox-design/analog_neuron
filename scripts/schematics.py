#!/usr/bin/env python3
"""xschem schematics of the design, generated from the same sizing as the SPICE netlists.

Writes xschem/{ota5p,bias_ref,vi_conv,neuron_core}.sch and their .sym symbols, plus analog_neuron.sch: the
whole neuron flat on one sheet, every device drawn. The SPICE netlists in
spice/ stay the design source; these schematics are the readable view of them, and --check proves they
are the same circuit (xschem netlist vs spice/lvs/<cell>_ref.spice, netgen).

  python3 scripts/schematics.py             write the .sch / .sym files
  python3 scripts/schematics.py --check     ... then netlist each with xschem and LVS it (verif/lvs/schematic/)
  python3 scripts/schematics.py --export    ... then screenshot the full sheet with xschem (docs/img/xschem_analog_neuron.png)
"""
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
XS = ROOT / "xschem"
CELLS = ("ota5p", "bias_ref", "vi_conv", "neuron_core", "analog_neuron")
HEADER = "v {xschem version=3.4.8 file_version=1.2}\n"

# pin positions of the symbols used (symbol coordinates, y down)
PINS = {
    "nfet": {"D": (20, -30), "G": (-20, 0), "S": (20, 30)},
    "pfet": {"S": (20, -30), "G": (-20, 0), "D": (20, 30)},
    "res": {"P": (0, -30), "M": (0, 30), "B": (-20, 0)},
    "cap": {"c0": (0, -30), "c1": (0, 30)},
    "lab": {"p": (0, 0)},
}
SYM = {
    "nfet": "sky130_fd_pr/nfet3_01v8.sym", "pfet": "sky130_fd_pr/pfet3_01v8.sym",
    "res": "sky130_fd_pr/res_xhigh_po_0p69.sym", "res1p41": "sky130_fd_pr/res_xhigh_po_1p41.sym",
    "cap": "sky130_fd_pr/cap_mim_m3_1.sym",
}


def xform(p, rot, flip):
    x, y = p
    if flip:
        x = -x
    return [(x, y), (-y, x), (-x, -y), (y, -x)][rot]


class Sch:
    def __init__(self):
        self.items = []

    def wire(self, *pts):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            self.items.append(f"N {x1} {y1} {x2} {y2} {{}}")

    def place(self, sym, kind, x, y, attrs, rot=0, flip=0):
        self.items.append(f"C {{{sym}}} {x} {y} {rot} {flip} {{{attrs}}}")
        return {k: (x + dx, y + dy) for k, (dx, dy) in
                ((k, xform(v, rot, flip)) for k, v in PINS[kind].items())}

    def fet(self, kind, name, x, y, w, l, body, m=1, flip=0):
        model = "nfet_01v8" if kind == "nfet" else "pfet_01v8"
        return self.place(SYM[kind], kind, x, y,
                          f"name={name} W={w} L={l} nf=1 mult={m} body={body} model={model} spiceprefix=X",
                          flip=flip)

    def res(self, name, x, y, l, rot=0, flip=0, wide=False):
        model = "res_xhigh_po_1p41" if wide else "res_xhigh_po_0p69"
        return self.place(SYM["res1p41" if wide else "res"], "res", x, y,
                          f"name={name} L={l} model={model} spiceprefix=X mult=1", rot, flip)

    def cap(self, name, x, y, w, l, rot=0, flip=0):
        return self.place(SYM["cap"], "cap", x, y, f"name={name} model=cap_mim_m3_1 W={w} L={l} MF=1 spiceprefix=X",
                          rot, flip)

    def label(self, x, y, net, kind="lab_pin", flip=0, rot=0):
        n = sum(1 for i in self.items if i.startswith("C {")) + 1
        self.items.append(f"C {{{kind}.sym}} {x} {y} {rot} {flip} {{name=l{n} lab={net}}}")

    def inst(self, cell, name, x, y, pins):
        self.items.append(f"C {{{cell}.sym}} {x} {y} 0 0 {{name={name}}}")
        return {k: (x + dx, y + dy) for k, (dx, dy) in pins.items()}

    def text(self, s, x, y, size=0.3, layer=None):
        a = f"layer={layer}" if layer is not None else ""
        self.items.append(f"T {{{s}}} {x} {y} 0 0 {size} {size} {{{a}}}")

    def write(self, path):
        path.write_text(HEADER + "G {}\nK {}\nV {}\nS {}\nE {}\n" + "\n".join(self.items) + "\n")


# ---------------------------------------------------------------------------------------- symbols
def box_symbol(path, pins, body_lines, texts):
    """pins: list of (name, dir, x, y, stub_end) in netlist port order."""
    out = [HEADER.rstrip(), "G {}", 'K {type=subcircuit\nformat="@name @pinlist @symname"\ntemplate="name=x1"\n}',
           "V {}", "S {}", "E {}"]
    out += [f"L 4 {a} {b} {c} {d} {{}}" for a, b, c, d in body_lines]
    for name, d, x, y, (sx, sy) in pins:
        out.append(f"L 4 {x} {y} {sx} {sy} {{}}")
    for name, d, x, y, _ in pins:
        out.append(f"B 5 {x - 2.5} {y - 2.5} {x + 2.5} {y + 2.5} {{name={name} dir={d}}}")
    out += [f"T {{{s}}} {x} {y} 0 {f} {sz} {sz} {{}}" for s, x, y, f, sz in texts]
    path.write_text("\n".join(out) + "\n")


OTA_PINS = {"INP": (-60, -20), "INN": (-60, 20), "OUT": (60, 0), "VDD": (0, -60), "VP": (-20, 60), "VSS": (10, 60)}
VI_PINS = {"IN": (-80, -20), "VREF": (-80, 20), "G": (80, 0), "VP": (-20, -80), "VDD": (20, -80), "VSS": (0, 80)}
BIAS_PINS = {"VDD": (0, -70), "VSS": (0, 70), "VP": (80, -20), "VN": (80, 20)}
CORE_PINS = {"X": (-80, 0), "Y": (80, 0), "VDD": (0, -70), "VSS": (0, 70)}


def symbols():
    box_symbol(XS / "ota5p.sym",
               [("INP", "in", -60, -20, (-40, -20)), ("INN", "in", -60, 20, (-40, 20)),
                ("OUT", "out", 60, 0, (40, 0)), ("VP", "in", -20, 60, (-20, 30)),
                ("VDD", "inout", 0, -60, (0, -20)), ("VSS", "inout", 10, 60, (10, 15))],
               [(-40, -40, -40, 40), (-40, -40, 40, 0), (-40, 40, 40, 0)],
               [("+", -36, -30, 0, 0.3), ("-", -35, 10, 0, 0.3), ("@name", 20, 30, 0, 0.2)])
    box_symbol(XS / "vi_conv.sym",
               [("IN", "in", -80, -20, (-60, -20)), ("VREF", "in", -80, 20, (-60, 20)),
                ("G", "out", 80, 0, (60, 0)), ("VP", "in", -20, -80, (-20, -60)),
                ("VDD", "inout", 20, -80, (20, -60)), ("VSS", "inout", 0, 80, (0, 60))],
               [(-60, -60, 60, -60), (60, -60, 60, 60), (60, 60, -60, 60), (-60, 60, -60, -60)],
               [("V->I", -24, -12, 0, 0.35), ("@name", -58, -78, 1, 0.2),
                ("IN", -55, -30, 0, 0.18), ("VREF", -55, 10, 0, 0.18), ("G", 45, -10, 0, 0.18)])
    box_symbol(XS / "bias_ref.sym",
               [("VDD", "inout", 0, -70, (0, -50)), ("VSS", "inout", 0, 70, (0, 50)),
                ("VP", "out", 80, -20, (60, -20)), ("VN", "out", 80, 20, (60, 20))],
               [(-60, -50, 60, -50), (60, -50, 60, 50), (60, 50, -60, 50), (-60, 50, -60, -50)],
               [("bias", -30, -22, 0, 0.3), ("@name", -58, -68, 1, 0.2),
                ("VP", 35, -30, 0, 0.18), ("VN", 35, 10, 0, 0.18)])
    box_symbol(XS / "neuron_core.sym",
               [("X", "in", -80, 0, (-60, 0)), ("Y", "out", 80, 0, (60, 0)),
                ("VDD", "inout", 0, -70, (0, -50)), ("VSS", "inout", 0, 70, (0, 50))],
               [(-60, -50, 60, -50), (60, -50, 60, 50), (60, 50, -60, 50), (-60, 50, -60, -50)],
               [("neuron", -42, -22, 0, 0.3), ("@name", -58, -68, 1, 0.2)])


# ------------------------------------------------------------------------------------- schematics
def ota5p():
    s = Sch()
    m1 = s.fet("pfet", "XM1", 100, 300, 10, 1, "T")
    m2 = s.fet("pfet", "XM2", 300, 300, 10, 1, "T", flip=1)
    mt = s.fet("pfet", "XMT", 180, 190, 16, 2, "VDD")
    m3 = s.fet("nfet", "XM3", 140, 420, 2, 2, "VSS", flip=1)
    m4 = s.fet("nfet", "XM4", 260, 420, 2, 2, "VSS")
    s.wire(m1["S"], (120, 240), (200, 240))
    s.wire(m2["S"], (280, 240), (200, 240))
    s.wire(mt["D"], (200, 240))
    s.wire(m1["D"], (120, 360), m3["D"])
    s.wire((120, 360), (180, 360), (180, 420))
    s.wire(m3["G"], (180, 420), m4["G"])
    s.wire(m2["D"], (280, 360), m4["D"])
    s.wire((280, 360), (360, 360))
    s.wire(m3["S"], (120, 480), (280, 480))
    s.wire(m4["S"], (280, 480))
    s.wire((40, 480), (120, 480))
    s.wire(mt["S"], (200, 130), (40, 130))
    s.wire((40, 300), m1["G"])
    s.wire(m2["G"], (380, 300))
    s.wire((100, 190), mt["G"])
    s.label(40, 300, "INP", "ipin")
    s.label(380, 300, "INN", "ipin", flip=1)
    s.label(100, 190, "VP", "ipin")
    s.label(360, 360, "OUT", "opin")
    s.label(40, 130, "VDD", "iopin", flip=1)
    s.label(40, 480, "VSS", "iopin", flip=1)
    s.label(200, 240, "T", "lab_wire")
    s.label(180, 360, "D1", "lab_wire")
    s.write(XS / "ota5p.sch")


def bias_ref():
    s = Sch()
    m3 = s.fet("pfet", "XM3", 200, 200, 16, 2, "VDD", flip=1)
    m4 = s.fet("pfet", "XM4", 340, 200, 16, 2, "VDD")
    m1 = s.fet("nfet", "XM1", 200, 330, 20, 2, "VSS", flip=1)
    m2 = s.fet("nfet", "XM2", 340, 330, 20, 2, "VSS", m=4)
    r1 = s.res("XR1", 360, 410, 17, wide=True)
    ms1a = s.fet("pfet", "XMS1A", 500, 200, 0.42, 40, "VDD")
    ms1b = s.fet("pfet", "XMS1B", 500, 290, 0.42, 40, "VDD")
    ms2 = s.fet("nfet", "XMS2", 500, 380, 16, 0.5, "VSS")
    ms3 = s.fet("nfet", "XMS3", -20, 200, 1, 1, "VSS")
    # rails
    s.wire((-100, 140), (0, 140), (180, 140), (360, 140), (520, 140))
    s.wire((-100, 470), (180, 470), (360, 470), (520, 470))
    for p in (ms3["D"], m3["S"], m4["S"], ms1a["S"]):
        s.wire(p, (p[0], 140))
    for p in (m1["S"], r1["M"], ms2["S"]):
        s.wire(p, (p[0], 470))
    # PMOS mirror, VP diode
    s.wire(m3["G"], (290, 200), m4["G"])
    s.wire(m4["D"], (360, 260), m2["D"])
    s.wire((360, 260), (290, 260), (290, 200))
    s.wire((360, 260), (420, 260))
    # NMOS pair, VN diode
    s.wire(m3["D"], (180, 265), m1["D"])
    s.wire((180, 265), (240, 265), (240, 330))
    s.wire(m1["G"], (240, 330), m2["G"])
    s.wire(m2["S"], r1["P"])
    s.wire(ms3["S"], (0, 265), (180, 265))
    s.wire((0, 265), (-80, 265))
    # start-up
    s.wire(ms1a["D"], ms1b["S"])
    s.wire(ms1b["D"], (520, 335), ms2["D"])
    s.wire((520, 335), (570, 335))
    s.label(*r1["B"], "VSS")
    s.label(*ms1a["G"], "VSS")
    s.label(*ms1b["G"], "VSS")
    s.label(*ms2["G"], "VN")
    s.label(*ms3["G"], "ST")
    s.label(570, 335, "ST", flip=1)
    s.label(420, 260, "VP", "opin")
    s.label(-80, 265, "VN", "opin", flip=1)
    s.label(-100, 140, "VDD", "iopin", flip=1)
    s.label(-100, 470, "VSS", "iopin", flip=1)
    s.text("start-up", 532, 405, 0.25, layer=8)
    s.write(XS / "bias_ref.sch")


def vi_conv():
    s = Sch()
    i0 = s.fet("pfet", "XI0", 400, 120, 16, 4, "VDD")
    mf = s.fet("nfet", "XMF", 400, 330, 16, 4, "VSS")
    r = s.res("XR", 130, 200, 103.53, rot=3)
    cc = s.cap("XCC", 250, 230, 20, 20, rot=2, flip=1)
    rz = s.res("XRZ", 250, 300, 25, rot=2, flip=1)
    a = s.inst("ota5p", "XA", 150, 330, OTA_PINS)
    s.wire((40, 60), (420, 60))
    s.wire(i0["S"], (420, 60))
    s.wire((40, 200), r["P"])
    s.wire(r["M"], (180, 200), (250, 200), (420, 200))
    s.wire(i0["D"], (420, 200), mf["D"])
    s.wire(cc["c0"], rz["M"])
    s.wire(a["OUT"], (250, 330), mf["G"])
    s.wire((250, 330), (250, 380))
    s.wire((180, 200), (180, 240), (70, 240), (70, 310), a["INP"])
    s.wire((40, 350), a["INN"])
    s.wire((230, 120), i0["G"])
    s.wire(mf["S"], (420, 420), (160, 420), (40, 420))
    s.wire(a["VSS"], (160, 420))
    s.label(*a["VDD"], "VDD")
    s.label(*a["VP"], "VP")
    s.label(*r["B"], "VSS")
    s.label(*rz["B"], "VSS")
    s.label(40, 200, "IN", "ipin")
    s.label(40, 350, "VREF", "ipin")
    s.label(230, 120, "VP", "ipin")
    s.label(250, 380, "G", "opin")
    s.label(40, 60, "VDD", "iopin", flip=1)
    s.label(40, 420, "VSS", "iopin", flip=1)
    s.label(420, 200, "X", "lab_wire")
    s.write(XS / "vi_conv.sch")


def neuron_core():
    s = Sch()
    # bias and ratiometric divider
    b = s.inst("bias_ref", "XBIAS", 140, 150, BIAS_PINS)
    s.label(*b["VDD"], "VDD")
    s.label(*b["VSS"], "VSS")
    s.label(*b["VP"], "VP", flip=1)
    s.label(*b["VN"], "VN", flip=1)
    ra = s.res("XRA", 140, 330, 133.11)
    rb = s.res("XRB", 140, 430, 59.16)
    rc = s.res("XRC", 140, 530, 44.37)
    s.label(*ra["P"], "VDD")
    s.wire(ra["M"], (140, 370), rb["P"])
    s.wire(rb["M"], (140, 480), rc["P"])
    s.wire((140, 370), (200, 370))
    s.wire((140, 480), (200, 480))
    s.label(200, 370, "VK", flip=1)
    s.label(200, 480, "VREF", flip=1)
    s.label(*rc["M"], "VSS")
    for r in (ra, rb, rc):
        s.label(*r["B"], "VSS")
    # V->I converters
    for name, y, inp, g in (("XVS", 170, None, "GS"), ("XVK", 430, "VK", "GK")):
        v = s.inst("vi_conv", name, 400, y, VI_PINS)
        if inp:
            s.label(*v["IN"], inp)
        else:
            s.wire((280, v["IN"][1]), v["IN"])
            s.label(280, v["IN"][1], "X", "ipin")
        s.label(*v["VREF"], "VREF")
        s.label(*v["VP"], "VP")
        s.label(*v["VDD"], "VDD", flip=1)
        s.label(*v["VSS"], "VSS")
        s.wire(v["G"], (500, y))
        s.label(500, y, g, flip=1)
    # current-mode core: rails
    xs = (620, 760, 960, 1100)
    s.wire((560, 60), *[(x, 60) for x in xs])
    s.wire((560, 560), *[(x, 560) for x in (620, 760, 1100)])
    s.label(560, 60, "VDD", "iopin", flip=1)
    s.label(560, 560, "VSS", "iopin", flip=1)
    pk1 = s.fet("pfet", "XPK1", 640, 130, 32, 4, "VDD", flip=1)
    pk2 = s.fet("pfet", "XPK2", 740, 130, 32, 4, "VDD")
    wk = s.fet("nfet", "XWK", 600, 480, 16, 4, "VSS", m=2)
    ws = s.fet("nfet", "XWS", 740, 480, 16, 4, "VSS", m=2)
    pr1 = s.fet("pfet", "XPR1", 980, 130, 32, 8, "VDD", flip=1)
    pr2 = s.fet("pfet", "XPR2", 1080, 130, 32, 8, "VDD")
    ro = s.res("XRO", 1100, 400, 103.53)
    for p in (pk1, pk2, pr1, pr2):
        s.wire(p["S"], (p["S"][0], 60))
    for p in (wk["S"], ws["S"], ro["M"]):
        s.wire(p, (p[0], 560))
    # knee flip
    s.wire(pk1["G"], (690, 130), pk2["G"])
    s.wire((690, 130), (690, 190), (620, 190))
    s.wire(pk1["D"], (620, 190), wk["D"])
    # summing node S
    s.wire(pk2["D"], (760, 300), ws["D"])
    s.wire((760, 300), (860, 300), (960, 300))
    # ReLU diode and output copy
    s.wire(pr1["G"], (1030, 130), pr2["G"])
    s.wire((1030, 130), (1030, 220), (960, 220))
    s.wire(pr1["D"], (960, 220), (960, 300))
    s.wire(pr2["D"], (1100, 300), ro["P"])
    s.wire((1100, 300), (1160, 300))
    s.label(1160, 300, "Y", "opin")
    s.label(*ro["B"], "VSS")
    s.label(*wk["G"], "GK")
    s.label(*ws["G"], "GS")
    s.label(860, 300, "S", "lab_wire")
    s.label(620, 190, "DK", "lab_wire")
    for t, x, y in (("divider 9:4:3", 170, 262), ("signal V->I", 250, 215), ("knee V->I", 262, 475),
                    ("knee flip", 655, 70), ("x2 weight mirrors", 630, 580),
                    ("ReLU", 1000, 70), ("R_out", 1120, 440)):
        s.text(t, x, y, 0.25, layer=8)
    s.write(XS / "neuron_core.sch")


# ------------------------------------------------------------------- flat transistor-level top cell
def flat_converter(s, ox, oy, tag, inp, g, title, tap):
    """One V->I converter at transistor level (R_in, 5-T OTA, MF, I0, Cc, Rz); rails at oy and oy + 350."""
    P = lambda x, y: (ox + x, oy + y)
    n = lambda base: f"{base}_{tag}"
    t = "T" + tag
    r = s.res(n("XR"), *P(-20, 170), 103.53, rot=3)
    i0 = s.fet("pfet", n("XI0"), *P(80, 60), 16, 4, "VDD")
    mf = s.fet("nfet", n("XMF"), *P(80, 290), 16, 4, "VSS")
    cc = s.cap(n("XCC"), *P(240, 200), 20, 20, rot=2, flip=1)
    rz = s.res(n("XRZ"), *P(240, 270), 25, rot=2, flip=1)
    mt = s.fet("pfet", n("XMT"), *P(500, 60), 16, 2, "VDD")
    m1 = s.fet("pfet", n("XM1"), *P(420, 170), 10, 1, t)
    m2 = s.fet("pfet", n("XM2"), *P(620, 170), 10, 1, t, flip=1)
    m3 = s.fet("nfet", n("XM3"), *P(460, 290), 2, 2, "VSS", flip=1)
    m4 = s.fet("nfet", n("XM4"), *P(580, 290), 2, 2, "VSS")
    for d in (i0["S"], mt["S"]):
        tap(d, oy)
    for d in (mf["S"], m3["S"], m4["S"]):
        tap(d, oy + 350)
    s.wire(P(-90, 170), r["P"])
    s.wire(r["M"], P(100, 170), P(240, 170), m1["G"])
    s.wire(i0["D"], P(100, 170), mf["D"])
    s.wire(cc["c0"], rz["M"])
    s.wire(rz["P"], P(240, 320))
    s.wire(m1["S"], P(440, 110), P(520, 110))
    s.wire(m2["S"], P(600, 110), P(520, 110))
    s.wire(mt["D"], P(520, 110))
    s.wire(m1["D"], P(440, 230), m3["D"])
    s.wire(P(440, 230), P(500, 230), P(500, 290))
    s.wire(m3["G"], P(500, 290), m4["G"])
    s.wire(m2["D"], P(600, 230), m4["D"])
    s.wire(P(600, 230), P(680, 230))
    s.wire(m2["G"], P(680, 170))
    if inp == "X":
        s.label(*P(-90, 170), "X", "ipin")
    else:
        s.label(*P(-90, 170), inp)
    s.label(*r["B"], "VSS")
    s.label(*rz["B"], "VSS")
    s.label(*i0["G"], "VP")
    s.label(*mt["G"], "VP")
    s.label(*mf["G"], g)
    s.label(*P(240, 320), g)
    s.label(*P(680, 230), g, flip=1)
    s.label(*P(680, 170), "VREF", flip=1)
    s.label(*P(520, 110), t, "lab_wire")
    s.label(*P(100, 170), "X" + tag, "lab_wire")
    s.text(title, *P(-60, -60), 0.3, layer=8)
    s.text("OTA", *P(500, -60), 0.3, layer=8)


def analog_neuron():
    """The whole neuron on one sheet: every transistor, resistor and capacitor of the design."""
    s = Sch()
    taps = {}

    def tap(p, y):
        s.wire(p, (p[0], y))
        taps.setdefault(y, set()).add(p[0])

    # ---- row 1: bias reference, divider, signal converter (VDD at y=0, VSS at y=350)
    P = lambda x, y: (x + 140, y - 140)
    ms3 = s.fet("nfet", "XMS3", *P(-20, 200), 1, 1, "VSS")
    m3 = s.fet("pfet", "XMB3", *P(200, 200), 16, 2, "VDD", flip=1)
    m4 = s.fet("pfet", "XMB4", *P(340, 200), 16, 2, "VDD")
    m1 = s.fet("nfet", "XMB1", *P(200, 330), 20, 2, "VSS", flip=1)
    m2 = s.fet("nfet", "XMB2", *P(340, 330), 20, 2, "VSS", m=4)
    r1 = s.res("XR1", *P(360, 410), 17, wide=True)
    ms1a = s.fet("pfet", "XMS1A", *P(500, 200), 0.42, 40, "VDD")
    ms1b = s.fet("pfet", "XMS1B", *P(500, 290), 0.42, 40, "VDD")
    ms2 = s.fet("nfet", "XMS2", *P(500, 380), 16, 0.5, "VSS")
    for d in (ms3["D"], m3["S"], m4["S"], ms1a["S"]):
        tap(d, 0)
    for d in (m1["S"], r1["M"], ms2["S"]):
        tap(d, 350)
    s.wire(m3["G"], P(290, 200), m4["G"])
    s.wire(m4["D"], P(360, 260), m2["D"])
    s.wire(P(360, 260), P(290, 260), P(290, 200))
    s.wire(P(360, 260), P(420, 260))
    s.wire(m3["D"], P(180, 265), m1["D"])
    s.wire(P(180, 265), P(240, 265), P(240, 330))
    s.wire(m1["G"], P(240, 330), m2["G"])
    s.wire(m2["S"], r1["P"])
    s.wire(ms3["S"], P(0, 265), P(180, 265))
    s.wire(P(0, 265), P(-80, 265))
    s.wire(ms1a["D"], ms1b["S"])
    s.wire(ms1b["D"], P(520, 335), ms2["D"])
    s.wire(P(520, 335), P(570, 335))
    for pin, net, f in ((r1["B"], "VSS", 0), (ms1a["G"], "VSS", 0), (ms1b["G"], "VSS", 0), (ms2["G"], "VN", 0),
                        (ms3["G"], "ST", 0), (P(570, 335), "ST", 1), (P(420, 260), "VP", 1), (P(-80, 265), "VN", 0)):
        s.label(*pin, net, flip=f)
    # ratiometric divider
    dx = 840
    ra = s.res("XRA", dx, 60, 133.11)
    rb = s.res("XRB", dx, 170, 59.16)
    rc = s.res("XRC", dx, 280, 44.37)
    tap(ra["P"], 0)
    tap(rc["M"], 350)
    s.wire(ra["M"], (dx, 115), rb["P"])
    s.wire(rb["M"], (dx, 225), rc["P"])
    s.wire((dx, 115), (dx + 50, 115))
    s.wire((dx, 225), (dx + 50, 225))
    s.label(dx + 50, 115, "VK", flip=1)
    s.label(dx + 50, 225, "VREF", flip=1)
    for r in (ra, rb, rc):
        s.label(*r["B"], "VSS")
    flat_converter(s, 1080, 0, "S", "X", "GS", "signal V->I converter", tap)

    # ---- row 2: knee converter and the current-mode core (VDD at y=520, VSS at y=870)
    flat_converter(s, 140, 520, "K", "VK", "GK", "knee V->I converter", tap)
    C = lambda x, y: (x + 900, y + 520)
    pk1 = s.fet("pfet", "XPK1", *C(80, 60), 32, 4, "VDD", flip=1)
    pk2 = s.fet("pfet", "XPK2", *C(220, 60), 32, 4, "VDD")
    wk = s.fet("nfet", "XWK", *C(40, 290), 16, 4, "VSS", m=2)
    ws = s.fet("nfet", "XWS", *C(220, 290), 16, 4, "VSS", m=2)
    pr1 = s.fet("pfet", "XPR1", *C(460, 60), 32, 8, "VDD", flip=1)
    pr2 = s.fet("pfet", "XPR2", *C(580, 60), 32, 8, "VDD")
    ro = s.res("XRO", *C(600, 240), 103.53)
    for d in (pk1["S"], pk2["S"], pr1["S"], pr2["S"]):
        tap(d, 520)
    for d in (wk["S"], ws["S"], ro["M"]):
        tap(d, 870)
    s.wire(pk1["G"], C(150, 60), pk2["G"])
    s.wire(C(150, 60), C(150, 120), C(60, 120))
    s.wire(pk1["D"], C(60, 120), wk["D"])
    s.wire(pk2["D"], C(240, 180), ws["D"])
    s.wire(C(240, 180), C(340, 180), C(440, 180))
    s.wire(pr1["G"], C(520, 60), pr2["G"])
    s.wire(C(520, 60), C(520, 120), C(440, 120))
    s.wire(pr1["D"], C(440, 120), C(440, 180))
    s.wire(pr2["D"], C(600, 180), ro["P"])
    s.wire(C(600, 180), C(660, 180))
    s.label(*C(660, 180), "Y", "opin")
    s.label(*ro["B"], "VSS")
    s.label(*wk["G"], "GK")
    s.label(*ws["G"], "GS")
    s.label(*C(340, 180), "S", "lab_wire")
    s.label(*C(60, 120), "DK", "lab_wire")

    # ---- rails and supply pins
    for y, net, port in ((0, "VDD", True), (350, "VSS", True), (520, "VDD", False), (870, "VSS", False)):
        xs = sorted(taps[y] | {20})
        s.wire(*[(x, y) for x in xs])
        if port:
            s.label(20, y, net, "iopin", flip=1)
        else:
            s.label(20, y, net)
    for t, x, y in (("bias reference (beta multiplier)", 120, -60), ("start-up", 600, -60),
                    ("divider 9:4:3", 790, -60), ("knee flip", 970, 460), ("ReLU + output copy", 1320, 460),
                    ("x2 weight mirrors", 940, 890), ("R_out", 1520, 800)):
        s.text(t, x, y, 0.3, layer=8)
    s.write(XS / "analog_neuron.sch")


def write_all():
    XS.mkdir(exist_ok=True)
    (XS / "xschemrc").write_text(
        "# open with:  cd xschem && xschem neuron_core.sch   (PDK_ROOT must point at the ciel install)\n"
        "source $env(PDK_ROOT)/sky130A/libs.tech/xschem/xschemrc\n"
        "append XSCHEM_LIBRARY_PATH :[file dirname [file normalize [info script]]]\n")
    symbols()
    ota5p()
    bias_ref()
    vi_conv()
    neuron_core()
    analog_neuron()
    print("wrote", ", ".join(f"xschem/{c}.sch" for c in CELLS))


# ------------------------------------------------------------------------------------ check / export
def xschem(cell, commands, out):
    """Run Tcl commands on one schematic, headless; errors land in <out>/<cell>.err."""
    env = dict(os.environ, PDK_ROOT=os.environ.get("PDK_ROOT", str(pathlib.Path.home() / ".ciel")), PDK="sky130A")
    err = out / f"{cell}.err"
    tcl = out / f"{cell}.tcl"
    tcl.write_text(f"if {{[catch {{\n{commands}\n}} e]}} {{set f [open {err} w]; puts $f $e; close $f}}\n"
                   "xschem exit closewindow force\n")
    err.unlink(missing_ok=True)
    subprocess.run(["timeout", "60", "xschem", "-x", "--rcfile", str(XS / "xschemrc"), "--netlist_path", str(out),
                    "--script", str(tcl), str(XS / f"{cell}.sch")],
                   cwd=XS, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if err.exists():
        sys.exit(f"xschem failed on {cell}: {err.read_text().strip()}")


def check():
    out = ROOT / "build" / "xschem"
    log = ROOT / "verif" / "lvs" / "schematic"
    out.mkdir(parents=True, exist_ok=True)
    log.mkdir(parents=True, exist_ok=True)
    setup = pathlib.Path(os.environ.get("PDK_ROOT", pathlib.Path.home() / ".ciel")) / "sky130A/libs.tech/netgen/sky130A_setup.tcl"
    ok = True
    for cell in CELLS:
        net = out / f"{cell}.spice"
        net.unlink(missing_ok=True)
        xschem(cell, f"set lvs_netlist 1\nset top_is_subckt 1\nxschem netlist {cell}.spice", out)
        ref = ROOT / "spice" / "lvs" / f"{cell}_ref.spice"
        if cell == "vi_conv":       # no standalone reference: compare against the hierarchy inside neuron_core's
            ref = ROOT / "spice" / "lvs" / "neuron_core_ref.spice"
        comp = log / f"{cell}_comp.out"
        r = subprocess.run(["netgen", "-batch", "lvs", f"{net} {cell}", f"{ref} {cell}", str(setup), str(comp)],
                           capture_output=True, text=True)
        (log / f"{cell}.log").write_text(r.stdout + r.stderr)
        text = comp.read_text() if comp.exists() else ""
        good = "Circuits match uniquely" in text and "Property errors were found" not in text
        ok &= good
        verdict = "PASS" if good else "FAIL"
        line = f"SCHEMATIC_LVS {cell}: {verdict}"
        with open(log / f"{cell}.log", "a") as f:
            f.write(line + "\n")
        print(line, f"({net.relative_to(ROOT)} vs {ref.relative_to(ROOT)})")
    return ok


# screenshot size (pixels); xschem zooms the whole sheet to fit, the margins are cropped afterwards
SHOT = {"analog_neuron": (3000, 1900)}


def export():
    """Screenshot from xschem itself (its own renderer and colours). xschem needs a window for PNG output,
    so this briefly opens one. The simulation back-annotation layers (15, 17: id, gm, vgs, vds)
    are hidden because they only show '-' without a simulation."""
    from PIL import Image, ImageOps
    out = ROOT / "build" / "xschem"
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PDK_ROOT=os.environ.get("PDK_ROOT", str(pathlib.Path.home() / ".ciel")), PDK="sky130A")
    for cell in SHOT:
        raw = out / f"{cell}_raw.png"
        raw.unlink(missing_ok=True)
        w, h = SHOT[cell]
        tcl = out / f"{cell}_png.tcl"
        tcl.write_text("foreach l {15 17} { set enable_layer($l) 0 }\nxschem enable_layers\nxschem zoom_full\n"
                       f"xschem print png {raw} {w} {h}\nxschem exit closewindow force\n")
        subprocess.run(["timeout", "60", "xschem", "--rcfile", str(XS / "xschemrc"), "--script", str(tcl),
                        str(XS / f"{cell}.sch")], cwd=XS, env=env, stdin=subprocess.DEVNULL, capture_output=True)
        im = Image.open(raw).convert("RGB")
        im = ImageOps.expand(im.crop(im.getbbox()), border=40, fill=(0, 0, 0))
        dst = ROOT / "docs" / "img" / f"xschem_{cell}.png"
        im.save(dst, optimize=True)
        print("wrote", dst.relative_to(ROOT), im.size)


if __name__ == "__main__":
    write_all()
    if "--check" in sys.argv and not check():
        sys.exit(1)
    if "--export" in sys.argv:
        export()
