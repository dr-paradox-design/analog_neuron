#!/usr/bin/env python3
"""Draw docs/img/transfer.png: post-layout y(x) at TT, 1.8 V, -40/27/125 C, vs the ideal
y = 2 max(0, x - V_k). Data: build/plots/curve_<T>.txt (wrdata from neuron_pex_tb.cir)."""
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
BG, FG, MUTED, GRID = "#0d1117", "#e6edf3", "#8b949e", "#21262d"
TEMPS = [(-40, "#58a6ff"), (27, "#3fb950"), (125, "#f85149")]
VK = 0.326 * 1.8


def main():
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=170)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    x_id = np.linspace(0.3, 1.2, 200)
    ax.plot(x_id, 2 * np.maximum(0, x_id - VK), color=MUTED, lw=1.4, ls=(0, (5, 4)),
            label="ideal  2·max(0, x − V$_k$)", zorder=1)
    for t, col in TEMPS:
        d = np.loadtxt(ROOT / f"build/plots/curve_{t}.txt")
        keep = (d[:, 0] > 55e-6) & (d[:, 1] >= 0.3) & (d[:, 1] <= 1.2)
        ax.plot(d[keep, 1], d[keep, 3], color=col, lw=2.0, label=f"post-layout  {t:+d} °C", zorder=2)
    ax.axvline(VK, color=GRID, lw=1.0, zorder=0)
    ax.annotate("knee  V$_k$ = 0.326·VDD", xy=(VK, 0.0), xytext=(VK + 0.04, 0.55), color=FG, fontsize=9,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8))
    ax.text(0.31, 0.07, "across 45 PVT corners:  slope 1.90 – 2.00  ·  INL ≤ 0.70 %", color=MUTED, fontsize=8.5)
    ax.set_xlim(0.3, 1.2)
    ax.set_ylim(-0.05, 1.25)
    ax.set_xlabel("input  x  (V)", color=FG, fontsize=10)
    ax.set_ylabel("output  y  (V)", color=FG, fontsize=10)
    ax.set_title("Transfer function — extracted layout, TT, VDD = 1.8 V", color=FG, fontsize=11,
                 loc="left", fontweight="bold")
    ax.tick_params(colors=MUTED, labelsize=9)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.grid(color=GRID, lw=0.7)
    leg = ax.legend(loc="upper left", frameon=False, fontsize=8.5)
    for txt in leg.get_texts():
        txt.set_color(FG)
    out = ROOT / "docs/img/transfer.png"
    fig.savefig(out, facecolor=BG, bbox_inches="tight", pad_inches=0.15)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
