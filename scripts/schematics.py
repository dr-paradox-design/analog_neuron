#!/usr/bin/env python3
"""xschem schematics of the design, generated from the same sizing as the SPICE netlists.

Writes xschem/{ota5p,bias_ref,vi_conv,neuron_core}.sch and their .sym symbols. The SPICE netlists in
spice/ stay the design source; these schematics are the readable view of them, and --check proves they
are the same circuit (xschem netlist vs spice/lvs/<cell>_ref.spice, netgen).

  python3 scripts/schematics.py             write the .sch / .sym files
  python3 scripts/schematics.py --check     ... then netlist each with xschem and LVS it (verif/lvs/schematic/)
  python3 scripts/schematics.py --export    ... then export SVGs and restyle them into docs/img/sch_<cell>.svg
"""
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
XS = ROOT / "xschem"
CELLS = ("ota5p", "bias_ref", "vi_conv", "neuron_core")
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

    def cap(self, name, x, y, w, l, rot=0):
        return self.place(SYM["cap"], "cap", x, y, f"name={name} model=cap_mim_m3_1 W={w} L={l} MF=1 spiceprefix=X",
                          rot)

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
               [("+", -36, -30, 0, 0.3), ("-", -35, 10, 0, 0.3), ("@name", 25, -45, 0, 0.2)])
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
    ms3 = s.fet("nfet", "XMS3", 100, 200, 1, 1, "VSS")
    # rails
    s.wire((40, 140), (120, 140), (180, 140), (360, 140), (520, 140))
    s.wire((40, 470), (180, 470), (360, 470), (520, 470))
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
    s.wire(ms3["S"], (120, 265), (180, 265))
    s.wire((120, 265), (60, 265))
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
    s.label(60, 265, "VN", "opin", flip=1)
    s.label(40, 140, "VDD", "iopin", flip=1)
    s.label(40, 470, "VSS", "iopin", flip=1)
    s.text("start-up", 470, 420, 0.25, layer=8)
    s.write(XS / "bias_ref.sch")


def vi_conv():
    s = Sch()
    i0 = s.fet("pfet", "XI0", 260, 120, 16, 4, "VDD")
    mf = s.fet("nfet", "XMF", 260, 330, 16, 4, "VSS")
    r = s.res("XR", 130, 200, 103.53, rot=3)
    cc = s.cap("XCC", 225, 230, 20, 20, rot=2)
    rz = s.res("XRZ", 225, 300, 25, rot=2, flip=1)
    a = s.inst("ota5p", "XA", 150, 330, OTA_PINS)
    s.wire((40, 60), (280, 60))
    s.wire(i0["S"], (280, 60))
    s.wire((40, 200), r["P"])
    s.wire(r["M"], (180, 200), (225, 200), (280, 200))
    s.wire(i0["D"], (280, 200), mf["D"])
    s.wire(cc["c0"], rz["M"])
    s.wire(a["OUT"], (225, 330), mf["G"])
    s.wire((225, 330), (225, 380))
    s.wire((180, 200), (180, 240), (70, 240), (70, 310), a["INP"])
    s.wire((40, 350), a["INN"])
    s.wire((180, 120), i0["G"])
    s.wire(mf["S"], (280, 420), (160, 420), (40, 420))
    s.wire(a["VSS"], (160, 420))
    s.label(*a["VDD"], "VDD")
    s.label(*a["VP"], "VP")
    s.label(*r["B"], "VSS")
    s.label(*rz["B"], "VSS")
    s.label(40, 200, "IN", "ipin")
    s.label(40, 350, "VREF", "ipin")
    s.label(180, 120, "VP", "ipin")
    s.label(225, 380, "G", "opin")
    s.label(40, 60, "VDD", "iopin", flip=1)
    s.label(40, 420, "VSS", "iopin", flip=1)
    s.label(280, 200, "X", "lab_wire")
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
    xs = (620, 760, 880, 1020)
    s.wire((560, 60), *[(x, 60) for x in xs])
    s.wire((560, 560), *[(x, 560) for x in (620, 760, 1020)])
    s.label(560, 60, "VDD", "iopin", flip=1)
    s.label(560, 560, "VSS", "iopin", flip=1)
    pk1 = s.fet("pfet", "XPK1", 640, 130, 32, 4, "VDD", flip=1)
    pk2 = s.fet("pfet", "XPK2", 740, 130, 32, 4, "VDD")
    wk = s.fet("nfet", "XWK", 600, 480, 16, 4, "VSS", m=2)
    ws = s.fet("nfet", "XWS", 740, 480, 16, 4, "VSS", m=2)
    pr1 = s.fet("pfet", "XPR1", 900, 130, 32, 8, "VDD", flip=1)
    pr2 = s.fet("pfet", "XPR2", 1000, 130, 32, 8, "VDD")
    ro = s.res("XRO", 1020, 400, 103.53)
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
    s.wire((760, 300), (820, 300), (880, 300))
    # ReLU diode and output copy
    s.wire(pr1["G"], (950, 130), pr2["G"])
    s.wire((950, 130), (950, 220), (880, 220))
    s.wire(pr1["D"], (880, 220), (880, 300))
    s.wire(pr2["D"], (1020, 300), ro["P"])
    s.wire((1020, 300), (1080, 300))
    s.label(1080, 300, "Y", "opin")
    s.label(*ro["B"], "VSS")
    s.label(*wk["G"], "GK")
    s.label(*ws["G"], "GS")
    s.label(820, 300, "S", "lab_wire")
    s.label(620, 190, "DK", "lab_wire")
    for t, x, y in (("divider 9:4:3", 170, 262), ("signal V->I", 250, 215), ("knee V->I", 262, 475),
                    ("knee flip", 655, 70), ("x2 weight mirrors", 630, 580),
                    ("ReLU", 860, 70), ("R_out", 1040, 440)):
        s.text(t, x, y, 0.25, layer=8)
    s.write(XS / "neuron_core.sch")


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


# design tokens shared with the README images (docs/img/neuron.gif)
BG, TEXT, MUTED, FAINT = "#0d1117", "#e6edf3", "#8b949e", "#30363d"
WIRE, SYMB, PORT, SIZE, NOTE = "#58a6ff", "#c9d1d9", "#3fb950", "#e3b341", "#8b949e"


def restyle(src, dst):
    svg = src.read_text()
    lw = float(re.search(r"stroke-width:\s*([\d.]+)", svg).group(1))
    body = svg.split("</style>", 1)[1]
    keep, xs, ys = [], [], []
    for line in body.splitlines():
        m = re.match(r'<path class="l(\d+)" d="([^"]+)"/>', line)
        if m:
            layer, d = int(m.group(1)), m.group(2)
            nums = list(map(float, re.findall(r"-?[\d.]+", d)))
            pts = list(zip(nums[0::2], nums[1::2]))
            if layer == 5 and d.endswith("z") and len(pts) == 5:      # pin squares
                continue
            if layer not in (1, 4, 5):
                continue
            xs += [p[0] for p in pts]
            ys += [p[1] for p in pts]
            keep.append(line)
            continue
        m = re.match(r'<circle class="l(\d+)" cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)"', line)
        if m and m.group(1) in ("1", "4"):
            cx, cy, r = float(m.group(2)), float(m.group(3)), float(m.group(4))
            if m.group(1) == "1":
                keep.append(f'<circle cx="{cx}" cy="{cy}" r="{0.75 * r:.2f}" fill="{WIRE}"/>')
            else:
                keep.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{SYMB}" '
                            f'stroke-width="{1.6 * lw:.2f}"/>')
            continue
        m = re.match(r'<text fill="(#[0-9a-f]+)".*font-size="([\d.]+)" transform="translate\(([-\d.]+), ([-\d.]+)\)" >(.*)</text>', line)
        if m:
            fill, size, x, y, s = m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5)
            if fill in ("#ff0000", "#ff7777", "#00ffcc") or s.startswith("nf=") or s.endswith("_01v8") \
                    or s.startswith("sky130") or s.startswith("res_") or s.startswith("cap_") \
                    or s.startswith("mult=") or s.strip() in ("", "@spice_get_voltage"):
                continue
            color = {"#cccccc": TEXT, "#aaaa00": SIZE, "#00ddff": WIRE, "#ffff00": NOTE}.get(fill, MUTED)
            if fill == "#00ddff":                       # net labels: smaller, bold
                size *= 0.62
                line = line.replace(m.group(2), f"{size:.2f}", 1)
                line = line.replace(f'fill="{fill}"', f'fill="{color}" font-weight="600"')
            else:
                line = line.replace(f'fill="{fill}"', f'fill="{color}"')
            keep.append(line)
            xs += [x, x + 0.6 * size * len(s)]
            ys += [y - size, y + 0.3 * size]
    pad = 4 * lw
    x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
    w, h = x1 - x0, y1 - y0
    style = f"""<style>
text {{ font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; }}
.l1 {{ fill: none; stroke: {WIRE}; stroke-width: {2.2 * lw:.3f}; stroke-linecap: round; stroke-linejoin: round; }}
.l4 {{ fill: {SYMB}; stroke: {SYMB}; stroke-width: {1.6 * lw:.3f}; stroke-linecap: round; stroke-linejoin: round; }}
.l5 {{ fill: {PORT}; fill-opacity: 0.25; stroke: {PORT}; stroke-width: {1.6 * lw:.3f}; stroke-linejoin: round; }}
</style>"""
    out = keep
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" '
           f'width="{w:.0f}" height="{h:.0f}">\n{style}\n'
           f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{3 * lw:.1f}" fill="{BG}"/>\n'
           + "\n".join(out) + "\n</svg>\n")
    dst.write_text(svg)


def export():
    out = ROOT / "build" / "xschem"
    out.mkdir(parents=True, exist_ok=True)
    for cell in CELLS:
        raw = out / f"{cell}_raw.svg"
        raw.unlink(missing_ok=True)
        xschem(cell, f"xschem zoom_full\nxschem print svg {raw} 2400 1400", out)
        restyle(raw, ROOT / "docs" / "img" / f"sch_{cell}.svg")
        print("wrote", f"docs/img/sch_{cell}.svg")


if __name__ == "__main__":
    write_all()
    if "--check" in sys.argv and not check():
        sys.exit(1)
    if "--export" in sys.argv:
        export()
