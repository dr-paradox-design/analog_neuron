#!/usr/bin/env python3
"""docs/img/block-diagram.png — the neuron's current topology as a technical plate.

Visual language (docs/img/block-diagram-philosophy.md, "Conductive Silence"):
  voltages are single grey hairlines; currents are bundles of identical strands whose COUNT is the
  quantity — the x2 mirror doubles its bundle, the knee bundle is subtracted at the sum, and only
  the excess continues. Resistor forms carry their real unit counts (R_in = R_out = 7, divider 9:4:3).
"""
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, PathPatch, Polygon
from matplotlib.path import Path
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONTS = pathlib.Path.home() / (".config/Claude/local-agent-mode-sessions/skills-plugin/"
                               "e255e400-605e-49b5-a06f-30c9e5fe39f5/f6741142-a0dd-4b1e-8089-0d544ad65cff/"
                               "skills/canvas-design/canvas-fonts")
THIN, MONO, SERIF = FONTS / "Jura-Light.ttf", FONTS / "GeistMono-Regular.ttf", FONTS / "InstrumentSerif-Italic.ttf"

W, H = 1600, 720
BG, PANEL = "#0d1117", "#10151c"
LINE, MUTED, TEXT, FAINT = "#6e7681", "#8b949e", "#e6edf3", "#30363d"
SIG, KNEE, OUT = "#58a6ff", "#e3b341", "#3fb950"
HAIR = 0.55          # pt
PITCH = 3.4          # strand pitch, units

fig = plt.figure(figsize=(16, 7.2), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(BG)

_metrics = {}


def advance(font, ch, size):
    if font not in _metrics:
        f = TTFont(font)
        _metrics[font] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[font]
    return hmtx[cmap[ord(ch)]][0] / upm * size


def text(x, y, s, font=THIN, size=11.0, color=MUTED, track=0.0, ha="left", z=6):
    """Vector text with explicit tracking (em fraction). Returns the drawn width."""
    widths = [advance(font, c, size) for c in s]
    total = sum(widths) + track * size * (len(s) - 1)
    x0 = {"left": x, "center": x - total / 2, "right": x - total}[ha]
    prop = FontProperties(fname=str(font))
    cx = x0
    for c, w in zip(s, widths):
        if c != " ":
            tp = TextPath((cx, y), c, size=size, prop=prop)
            ax.add_patch(PathPatch(tp, facecolor=color, edgecolor="none", lw=0, zorder=z))
        cx += w + track * size
    return total


def label(x, y, s, color=MUTED, size=10.5):
    text(x, y, s.upper(), THIN, size, color, track=0.32, ha="center")


def index(x, y, s):
    text(x, y, s, MONO, 7.2, FAINT if False else "#484f58", track=0.08)


def hline(x1, x2, y, color=LINE, lw=HAIR, z=2, ls="-"):
    ax.plot([x1, x2], [y, y], color=color, lw=lw, solid_capstyle="butt", zorder=z, ls=ls)


def vline(x, y1, y2, color=LINE, lw=HAIR, z=2, ls="-"):
    ax.plot([x, x], [y1, y2], color=color, lw=lw, solid_capstyle="butt", zorder=z, ls=ls)


def block(x1, x2, yc, h=64, z=4):
    ax.add_patch(FancyBboxPatch((x1, yc - h / 2), x2 - x1, h, boxstyle="round,pad=0,rounding_size=7",
                                fc=PANEL, ec=LINE, lw=HAIR, zorder=z))


def ticks(xc, yc, n, color, span=None, h=16):
    gap = 6.0
    xs = xc - (n - 1) * gap / 2 + np.arange(n) * gap
    for x in xs:
        vline(x, yc - h / 2, yc + h / 2, color=color, lw=0.8, z=5)


def bezier(p0, p1, p2, p3, n=220):
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def bundle(points, n, color, taper=(1.0, 1.0), lw=HAIR, z=3, alpha=0.95):
    """n parallel strands along a polyline, offset along its normal; width tapers linearly."""
    p = np.asarray(points, float)
    d = np.gradient(p, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    nrm = np.stack([-d[:, 1], d[:, 0]], axis=1)
    s = np.linspace(taper[0], taper[1], len(p))[:, None]
    for k in range(n):
        off = (k - (n - 1) / 2) * PITCH
        q = p + nrm * off * s
        ax.plot(q[:, 0], q[:, 1], color=color, lw=lw, alpha=alpha, solid_capstyle="butt", zorder=z)


def straight(x1, x2, y, n=120):
    return np.stack([np.linspace(x1, x2, n), np.full(n, y)], axis=1)


def terminal(x, y, r=7.5):
    ax.add_patch(Circle((x, y), r, fc=BG, ec=TEXT, lw=0.9, zorder=6))


def arrow_glyph(x, y, w=12, color=MUTED):
    hline(x, x + w - 3, y, color=color, lw=0.8, z=6)
    ax.add_patch(Polygon([[x + w, y], [x + w - 4.2, y + 2.4], [x + w - 4.2, y - 2.4]], closed=True,
                         fc=color, ec="none", zorder=6))


# ---------------------------------------------------------------- geometry
YS, YK, YO = 520, 280, 400          # signal lane, knee lane, output lane
SX, SR = 1030, 27                   # sum node
VI = (270, 410)                     # V->I converters (both lanes: the knee path is a replica)
MI = (540, 650)                     # x2 mirrors
FL = (720, 810)                     # knee flip
RE = (1112, 1222)                   # ReLU
RO = (1292, 1402)                   # R_out
XIN, XOUT = 120, 1490               # terminals

# ---------------------------------------------------------------- frame marks
for cx, cy, sx, sy in ((40, 40, 1, 1), (W - 40, 40, -1, 1), (40, H - 40, 1, -1), (W - 40, H - 40, -1, -1)):
    hline(cx, cx + 16 * sx, cy, color=FAINT, lw=0.7)
    vline(cx, cy, cy + 16 * sy, color=FAINT, lw=0.7)

text(72, 650, "PLATE 01", MONO, 8.5, MUTED, track=0.16)
text(150, 650, "CURRENT TOPOLOGY OF A SINGLE ANALOG NEURON", THIN, 10.5, TEXT, track=0.30)
text(W - 72, 650, "SKY130 · 1.8 V · 180 × 115 µm", MONO, 8.5, MUTED, track=0.06, ha="right")
hline(72, W - 72, 628, color=FAINT, lw=0.5)

# ---------------------------------------------------------------- signal lane
terminal(XIN, YS)
text(XIN - 24, YS - 6, "x", SERIF, 26, TEXT, ha="right")
hline(XIN + 7.5, VI[0], YS)
bundle(straight(VI[1], MI[0], YS), 6, SIG)
bundle(straight(MI[1], 872, YS), 12, SIG)
bundle(bezier(np.array([872, YS]), np.array([958, YS]), np.array([952, YO + 12]),
              np.array([SX - SR * 0.906, YO + SR * 0.423])), 12, SIG, taper=(1.0, 0.22))

# ---------------------------------------------------------------- knee lane
# divider 9:4:3 from VDD; the 9|4 tap is V_k
UNIT = 6.2
dx = 196
top = YK + 9 * UNIT
vdd_y = top
terminal(XIN, vdd_y)
text(XIN - 24, vdd_y - 6, "VDD", MONO, 9.0, MUTED, ha="right")
hline(XIN + 7.5, dx, vdd_y)
y = top
for k, units in enumerate((9, 4, 3)):
    for u in range(units):
        y1, y2 = y - u * UNIT - 1.0, y - (u + 1) * UNIT + 1.0
        vline(dx, y2, y1, color=KNEE if k == 0 else LINE, lw=1.6, z=5)
    y -= units * UNIT
gnd = y
vline(dx, gnd - 10, gnd, color=LINE)
for i, w in enumerate((14, 9, 4)):
    hline(dx - w / 2, dx + w / 2, gnd - 10 - i * 3.6, color=LINE, lw=0.8)
ax.add_patch(Circle((dx, YK), 2.6, fc=KNEE, ec="none", zorder=6))
hline(dx, VI[0], YK)
text(dx + 9, YK + 7, "V", SERIF, 15, TEXT)
text(dx + 18.5, YK + 3, "k", SERIF, 9.5, TEXT)
bundle(straight(VI[1], MI[0], YK), 6, KNEE)
bundle(straight(MI[1], FL[0], YK), 12, KNEE)
bundle(straight(FL[1], 872, YK), 12, KNEE)
bundle(bezier(np.array([872, YK]), np.array([958, YK]), np.array([952, YO - 12]),
              np.array([SX - SR * 0.906, YO - SR * 0.423])), 12, KNEE, taper=(1.0, 0.22))

# ---------------------------------------------------------------- forms
for yc, tag in ((YS, "A"), (YK, "B")):
    block(*VI, yc)
    ticks(VI[0] + 44, yc, 7, SIG if tag == "A" else KNEE)         # R_in / R_k: 7 units
    tri = [[VI[1] - 52, yc + 13], [VI[1] - 52, yc - 13], [VI[1] - 26, yc]]   # OTA
    ax.add_patch(Polygon(tri, closed=True, fc="none", ec=TEXT, lw=0.8, zorder=5))
    block(*MI, yc)
    text((MI[0] + MI[1]) / 2, yc - 8, "×2", SERIF, 24, TEXT, ha="center")
    index(VI[0], yc + 40, f"{tag}1")
    index(MI[0], yc + 40, f"{tag}2")
# V->I labels with a drawn arrow
for yc in (YS, YK):
    cx = (VI[0] + VI[1]) / 2
    w1 = advance(THIN, "V", 10.5)
    text(cx - 13 - w1, yc - 56, "V", THIN, 10.5, MUTED)
    arrow_glyph(cx - 7, yc - 52.5)
    text(cx + 9, yc - 56, "I", THIN, 10.5, MUTED)
    label((MI[0] + MI[1]) / 2, yc - 56, "mirror")
block(*FL, YK)
# flip glyph: a sink turned into a source (U-turn)
cxf = (FL[0] + FL[1]) / 2
ax.add_patch(PathPatch(Path([(cxf - 14, YK - 10), (cxf - 14, YK + 10), (cxf + 14, YK + 10), (cxf + 14, YK - 10)],
                            [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc="none", ec=TEXT, lw=0.8, zorder=5))
ax.add_patch(Polygon([[cxf + 14, YK - 13], [cxf + 11.2, YK - 7], [cxf + 16.8, YK - 7]], closed=True,
                     fc=TEXT, ec="none", zorder=5))
label(cxf, YK - 56, "flip")
index(FL[0], YK + 40, "B3")
label(dx, gnd - 40, "divider")
index(dx - 12, top + 18, "B0")

# bias: between the lanes, feeding both converters
bx = (VI[0] + VI[1]) / 2
block(VI[0] + 22, VI[1] - 22, YO, h=46)
ax.add_patch(matplotlib.patches.Arc((bx - 22, YO), 22, 22, theta1=40, theta2=330, ec=TEXT, lw=0.8, zorder=5))
ax.add_patch(Polygon([[bx - 22 + 11 * np.cos(np.radians(40)) + 0.5, YO + 11 * np.sin(np.radians(40)) + 4.0],
                      [bx - 22 + 11 * np.cos(np.radians(40)) - 3.8, YO + 11 * np.sin(np.radians(40)) - 1.0],
                      [bx - 22 + 11 * np.cos(np.radians(40)) + 3.4, YO + 11 * np.sin(np.radians(40)) - 2.2]],
                     closed=True, fc=TEXT, ec="none", zorder=5))
text(bx - 4, YO - 5.5, "β", THIN, 15, TEXT)
text(bx + 10, YO - 5.5, "·  ref", THIN, 10, MUTED)
vline(bx, YO + 23, YS - 32, color=MUTED, lw=0.7, ls=(0, (1.2, 2.6)))
vline(bx, YK + 32, YO - 23, color=MUTED, lw=0.7, ls=(0, (1.2, 2.6)))
index(VI[0] + 22, YO + 30, "D1")

# sum node
ax.add_patch(Circle((SX, YO), SR, fc=PANEL, ec=TEXT, lw=0.9, zorder=6))
text(SX, YO - 8.5, "Σ", THIN, 25, TEXT, ha="center", z=7)
index(SX - SR, YO + SR + 14, "C1")

# output: only the excess continues
bundle(straight(SX + SR, RE[0], YO), 4, OUT)
block(*RE, YO)
gx, gy = (RE[0] + RE[1]) / 2 - 22, YO - 12
ax.plot([gx, gx + 20, gx + 44], [gy, gy, gy + 26], color=OUT, lw=1.1, solid_joinstyle="miter", zorder=5)
hline(gx - 4, gx + 48, gy, color=FAINT, lw=0.5, z=4)
label((RE[0] + RE[1]) / 2, YO - 56, "ReLU")
index(RE[0], YO + 40, "C2")
bundle(straight(RE[1], RO[0], YO), 4, OUT)
block(*RO, YO)
ticks((RO[0] + RO[1]) / 2, YO, 7, OUT)                              # R_out: 7 units
label((RO[0] + RO[1]) / 2, YO - 56, "R out")
index(RO[0], YO + 40, "C3")
hline(RO[1], XOUT - 7.5, YO)
terminal(XOUT, YO)
text(XOUT + 22, YO - 6, "y", SERIF, 26, TEXT)

# ---------------------------------------------------------------- legend and anchor
hline(72, W - 72, 140, color=FAINT, lw=0.5)
lx, ly = 72, 96
for name, col, n in (("signal current", SIG, 3), ("knee current", KNEE, 3), ("output current", OUT, 3)):
    bundle(straight(lx, lx + 34, ly), n, col)
    w = text(lx + 46, ly - 4, name.upper(), THIN, 9.0, MUTED, track=0.30)
    lx += 46 + w + 44
vline(lx, ly - 6, ly + 6, color=LINE)                                 # voltage
hline(lx, lx + 34, ly, color=LINE)
w = text(lx + 46, ly - 4, "VOLTAGE", THIN, 9.0, MUTED, track=0.30)
lx += 46 + w + 44
hline(lx, lx + 34, ly, color=MUTED, lw=0.7, ls=(0, (1.2, 2.6)))
text(lx + 46, ly - 4, "BIAS", THIN, 9.0, MUTED, track=0.30)
text(72, 64, "STRAND COUNT IS CURRENT   ·   RESISTOR FORMS SHOW THEIR UNIT COUNT", THIN, 7.8, "#5f6873", track=0.30)

# anchor: y = 2 · max(0, x − V_k), set right-aligned with a true subscript
eq, size, ksize = "y = 2 · max(0, x − V", 30, 17
w_eq = sum(advance(SERIF, c, size) for c in eq)
w_k = advance(SERIF, "k", ksize)
w_close = advance(SERIF, ")", size)
x0 = W - 72 - (w_eq + 1.5 + w_k + 6.0 + w_close)
text(x0, 82, eq, SERIF, size, TEXT)
text(x0 + w_eq + 1.5, 75, "k", SERIF, ksize, TEXT)
text(x0 + w_eq + 1.5 + w_k + 6.0, 82, ")", SERIF, size, TEXT)

out = ROOT / "docs/img/block-diagram.png"
fig.savefig(out, facecolor=BG, dpi=150)
print(f"wrote {out}")
