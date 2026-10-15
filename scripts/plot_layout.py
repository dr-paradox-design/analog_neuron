#!/usr/bin/env python3
"""Draw docs/img/layout.png from build/render/polys.json (scripts/render_layout.py) with the
functional blocks of neuron_core outlined and labelled."""
import json
import pathlib
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import FancyBboxPatch

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE_AT = (6.0, 4.0)
BG = "#0d1117"
# layer: (face colour, alpha), drawn in this order
STYLE = [("nwell", "#1f6f78", 0.25), ("diff", "#3fb950", 0.55), ("tap", "#2ea043", 0.35),
         ("poly", "#f85149", 0.55), ("rpoly", "#ff7b72", 0.75), ("li1", "#a371f7", 0.35),
         ("met1", "#58a6ff", 0.35), ("met2", "#db61a2", 0.45), ("met3", "#e3b341", 0.55),
         ("capm", "#c9d1d9", 0.30), ("met4", "#79c0ff", 0.30), ("met5", "#8b949e", 0.35)]
GROUPS = {
    "BIAS REFERENCE": ["BIAS"],
    "OTA  ×2": ["OTA_S", "OTA_K"],
    "WEIGHT MIRROR  ×2": ["WK1", "WS1", "MS", "MK", "WS2", "WK2"],
    "I₀": ["I0_S"], "I₀ ": ["I0_K"],
    "Rz": ["RZ"],
    "RESISTOR ARRAY  37 × 43 kΩ": ["RARR"],
    "Cc": ["CC_S"], "Cc ": ["CC_K"],
    "PMOS KNEE FLIP + ReLU": ["PR1A", "PR2A", "PK1A", "PK2A", "PK2B", "PK1B", "PR2B", "PR1B"],
}


def instance_boxes():
    boxes, cur, tf = {}, None, None
    for line in (ROOT / "mag/neuron/neuron_core.mag").read_text().splitlines():
        f = line.split()
        if not f:
            continue
        if f[0] == "use":
            cur = f[2]
        elif f[0] == "transform":
            tf = [int(v) for v in f[1:7]]
        elif f[0] == "box" and cur and tf:
            a, b, c, d, e, g = tf
            x1, y1, x2, y2 = (int(v) for v in f[1:5])
            xs = [(a * x + b * y + c) / 200 + CORE_AT[0] for x, y in ((x1, y1), (x2, y2))]
            ys = [(d * x + e * y + g) / 200 + CORE_AT[1] for x, y in ((x1, y1), (x2, y2))]
            boxes[cur] = (min(xs), min(ys), max(xs), max(ys))
            cur, tf = None, None
    return boxes


def main():
    polys = json.loads((ROOT / "build/render/polys.json").read_text())
    fig, ax = plt.subplots(figsize=(12, 7.67), dpi=150)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    for name, col, alpha in STYLE:
        if name in polys:
            ax.add_collection(PolyCollection(polys[name], facecolor=col, edgecolor=col,
                                             linewidth=0.15, alpha=alpha))
    # boundary
    ax.add_patch(plt.Rectangle((0, 0), 180, 115, fill=False, ec="#30363d", lw=1.2))
    boxes = instance_boxes()
    for label, insts in GROUPS.items():
        bs = [boxes[i] for i in insts if i in boxes]
        if not bs:
            continue
        x1, y1 = min(b[0] for b in bs) - 0.8, min(b[1] for b in bs) - 0.8
        x2, y2 = max(b[2] for b in bs) + 0.8, max(b[3] for b in bs) + 0.8
        ax.add_patch(FancyBboxPatch((x1, y1), x2 - x1, y2 - y1, boxstyle="round,pad=0,rounding_size=1.2",
                                    fill=False, ec="#f0f6fc", lw=0.9, ls=(0, (4, 3)), alpha=0.85))
        ax.text(x1 + 0.6, y2 + 0.9, label.strip(), color="#f0f6fc", fontsize=8.5, fontweight="bold",
                family="DejaVu Sans", va="bottom", ha="left",
                bbox=dict(boxstyle="round,pad=0.25", fc=BG, ec="none", alpha=0.85))
    ax.text(179, 113.6 + 1.6, "VDD  (metal5)", color="#8b949e", fontsize=7.5, ha="right", va="bottom")
    ax.text(179, -1.2, "VSS  (metal5)", color="#8b949e", fontsize=7.5, ha="right", va="top")
    ax.text(180.8, 81.67, "X  Y", color="#f0f6fc", fontsize=7.5, ha="left", va="center", fontweight="bold")
    ax.set_xlim(-2, 186)
    ax.set_ylim(-4, 119)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0, 117.5, "analog_neuron  ·  SKY130  ·  180 × 115 µm", color="#c9d1d9",
            fontsize=10, fontweight="bold", va="bottom")
    out = ROOT / "docs/img/layout.png"
    fig.savefig(out, facecolor=BG, bbox_inches="tight", pad_inches=0.15)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
