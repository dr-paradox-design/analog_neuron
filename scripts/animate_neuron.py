#!/usr/bin/env python3
"""docs/img/neuron.gif — the neuron in action.

x sweeps 0.3 -> 1.2 -> 0.3 V. Left: the current topology, where the number of flowing strands is the
current (0.5 uA per strand): the signal bundle grows with x, the knee bundle is fixed, and the output
bundle exists only when the signal exceeds the knee (the ReLU). Right: the post-layout transfer curve
(TT, 27 C, 1.8 V; build/plots/curve_27.txt) with the operating point.
"""
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyBboxPatch, Circle

ROOT = pathlib.Path(__file__).resolve().parents[1]
BG, PANEL, LINE, MUTED, TEXT, FAINT = "#0d1117", "#10151c", "#6e7681", "#8b949e", "#e6edf3", "#30363d"
SIG, KNEE, OUT = "#58a6ff", "#e3b341", "#3fb950"
VREF, VK, RIN = 0.2556, 0.5966, 304e3
IK = (VK - VREF) / RIN
UNIT = 0.5e-6                          # current per strand
PITCH = 0.62

d = np.loadtxt(ROOT / "build/plots/curve_27.txt")
keep = (d[:, 0] > 55e-6) & (d[:, 1] >= 0.29) & (d[:, 1] <= 1.21)
cx, cy = d[keep, 1], d[keep, 3]
order = np.argsort(cx)
cx, cy = cx[order], cy[order]

N = 84
xs = np.concatenate([np.linspace(0.3, 1.2, N // 2), np.linspace(1.2, 0.3, N // 2)])

fig = plt.figure(figsize=(10, 4.3), dpi=100)
fig.patch.set_facecolor(BG)
axl = fig.add_axes([0.0, 0.0, 0.62, 1.0])
axr = fig.add_axes([0.68, 0.17, 0.29, 0.66])


def bez(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def bundle(ax, pts, n, color, phase, taper=(1, 1), reverse=False):
    if n <= 0:
        return
    p = np.asarray(pts, float)
    g = np.gradient(p, axis=0)
    g /= np.linalg.norm(g, axis=1, keepdims=True)
    nrm = np.stack([-g[:, 1], g[:, 0]], axis=1)
    s = np.linspace(*taper, len(p))[:, None]
    for k in range(n):
        q = p + nrm * (k - (n - 1) / 2) * PITCH * s
        ax.plot(q[:, 0], q[:, 1], color=color, lw=1.1, alpha=0.95,
                ls=(-phase if reverse else phase, (2.2, 1.6)), solid_capstyle="butt", zorder=3)


def box(ax, x1, x2, y, label, h=7):
    ax.add_patch(FancyBboxPatch((x1, y - h / 2), x2 - x1, h, boxstyle="round,pad=0,rounding_size=1.2",
                                fc=PANEL, ec=LINE, lw=0.8, zorder=4))
    ax.text((x1 + x2) / 2, y, label, color=TEXT, fontsize=8.5, ha="center", va="center", zorder=5)


def draw(i):
    x = xs[i]
    ix = max(0.0, (x - VREF) / RIN)
    iout = 2 * max(0.0, ix - IK)
    y = float(np.interp(x, cx, cy))
    ns, nk = int(round(2 * ix / UNIT)), int(round(2 * IK / UNIT))
    no = max(0, ns - nk)
    phase = (i * 1.3) % 3.8

    ax = axl
    ax.clear()
    ax.set_xlim(0, 100)
    ax.set_ylim(-4.7, 64.7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(BG)
    # lanes
    ys, yk, yo, sx = 44, 16, 30, 66
    ax.plot([7, 12], [ys, ys], color=LINE, lw=0.8)
    ax.plot([7, 12], [yk, yk], color=LINE, lw=0.8)
    bundle(ax, [[24, ys], [31, ys]], max(1, ns // 2) if ix > 0 else 0, SIG, phase)
    bundle(ax, [[24, yk], [31, yk]], max(1, nk // 2), KNEE, phase)
    bundle(ax, np.linspace([41, ys], [52, ys], 20), ns, SIG, phase)
    bundle(ax, bez(np.array([52, ys]), np.array([59, ys]), np.array([58, yo + 2]), np.array([sx - 2.7, yo + 1.2])),
           ns, SIG, phase, taper=(1, 0.3))
    bundle(ax, np.linspace([41, yk], [45, yk], 10), nk, KNEE, phase)
    bundle(ax, np.linspace([53, yk], [55, yk], 6), nk, KNEE, phase)
    bundle(ax, bez(np.array([55, yk]), np.array([60, yk]), np.array([58, yo - 2]), np.array([sx - 2.7, yo - 1.2])),
           nk, KNEE, phase, taper=(1, 0.3))
    bundle(ax, np.linspace([sx + 3, yo], [72, yo], 12), no, OUT, phase)
    bundle(ax, np.linspace([81, yo], [85, yo], 8), no, OUT, phase)
    ax.plot([94, 96.5], [yo, yo], color=LINE, lw=0.8)
    box(ax, 12, 24, ys, "V → I")
    box(ax, 31, 41, ys, "× 2")
    box(ax, 12, 24, yk, "V → I")
    box(ax, 31, 41, yk, "× 2")
    box(ax, 45, 53, yk, "flip")
    box(ax, 72, 81, yo, "ReLU")
    box(ax, 85, 94, yo, "R out")
    ax.add_patch(Circle((sx, yo), 3.0, fc=PANEL, ec=TEXT, lw=1.0, zorder=6))
    ax.text(sx, yo, "Σ", color=TEXT, fontsize=12, ha="center", va="center", zorder=7)
    for xx, yy in ((5.5, ys), (5.5, yk), (97.5, yo)):
        ax.add_patch(Circle((xx, yy), 1.2, fc=BG, ec=TEXT, lw=1.0, zorder=6))
    ax.text(3.6, ys, "x", color=TEXT, fontsize=13, ha="right", va="center", style="italic")
    ax.text(3.6, yk, r"$V_k$", color=TEXT, fontsize=11, ha="right", va="center")
    ax.text(99.2, yo, "y", color=TEXT, fontsize=13, ha="left", va="center", style="italic")
    # readouts
    ax.text(12, 55, f"x = {x:.2f} V", color=SIG, fontsize=11, fontweight="bold", va="center")
    ax.text(12, 51.5, f"signal  2·Iₓ = {2 * ix * 1e6:4.2f} µA", color=SIG, fontsize=8.5, va="center")
    ax.text(12, 6.5, f"knee  2·Iₖ = {2 * IK * 1e6:4.2f} µA  (fixed)", color=KNEE, fontsize=8.5, va="center")
    state = "ReLU on: output = excess" if iout > 0 else "ReLU off: signal < knee"
    ax.text(72, 42, state, color=OUT if iout > 0 else MUTED, fontsize=8.5, va="center")
    ax.text(72, 38.5, f"I_out = {iout * 1e6:4.2f} µA", color=OUT, fontsize=8.5, va="center")
    ax.text(72, 19, f"y = {y:.3f} V", color=TEXT, fontsize=11, fontweight="bold", va="center")
    ax.text(1.5, 1.5, "one strand ≈ 0.5 µA", color=FAINT, fontsize=7.5)

    ax = axr
    ax.clear()
    ax.set_facecolor(BG)
    xi = np.linspace(0.3, 1.2, 100)
    ax.plot(xi, 2 * np.maximum(0, xi - 0.326 * 1.8), color=MUTED, lw=1, ls=(0, (4, 3)), label="ideal")
    ax.plot(cx, cy, color=OUT, lw=1.8, label="post-layout")
    ax.axvline(x, color=FAINT, lw=0.8)
    ax.plot([x], [y], "o", ms=7, color=SIG, mec=TEXT, mew=0.8, zorder=5)
    ax.set_xlim(0.3, 1.2)
    ax.set_ylim(-0.05, 1.25)
    ax.set_xlabel("x (V)", color=MUTED, fontsize=8.5)
    ax.set_ylabel("y (V)", color=MUTED, fontsize=8.5)
    ax.set_title("y = 2·max(0, x − Vₖ)", color=TEXT, fontsize=10, loc="left")
    ax.tick_params(colors=MUTED, labelsize=7.5)
    for s in ax.spines.values():
        s.set_color(FAINT)
    ax.grid(color="#1b222c", lw=0.6)
    leg = ax.legend(loc="upper left", frameon=False, fontsize=7.5)
    for t in leg.get_texts():
        t.set_color(MUTED)


anim = FuncAnimation(fig, draw, frames=N, interval=70)
out = ROOT / "docs/img/neuron.gif"
anim.save(out, writer=PillowWriter(fps=14), savefig_kwargs={"facecolor": BG})
print(f"wrote {out} ({out.stat().st_size / 1e6:.2f} MB, {N} frames)")
