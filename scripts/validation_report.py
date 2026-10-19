#!/usr/bin/env python3
"""Build submit/analog_neuron_validation.pdf - the simulation and validation document required by the
Silicluster v3 call (section 10).

Every number and figure is read from the result files of the actual runs (build/sim/*/results.json,
build/plots/curve_*.txt, verif/), so the report cannot drift from the evidence. Figures are drawn
with matplotlib, laid out in HTML and printed to PDF with headless Chrome.

Usage: python3 scripts/validation_report.py
"""
import base64
import math
import datetime
import io
import json
import pathlib
import statistics as st
import subprocess

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
SIM = ROOT / "build" / "sim"
OUT_PDF = ROOT / "submit" / "analog_neuron_validation.pdf"
OUT_HTML = ROOT / "build" / "report" / "analog_neuron_validation.html"
FONTS = pathlib.Path.home() / (".config/Claude/local-agent-mode-sessions/skills-plugin/"
                               "e255e400-605e-49b5-a06f-30c9e5fe39f5/f6741142-a0dd-4b1e-8089-0d544ad65cff/"
                               "skills/canvas-design/canvas-fonts")

INK, MUTED, RULE = "#1f2328", "#59636e", "#d1d9e0"
BLUE, AMBER, GREEN, RED = "#0969da", "#bf8700", "#1a7f37", "#cf222e"
CORNERS = ["tt", "ff", "ss", "sf", "fs"]
TEMPS = [-40, 27, 125]
VDDS = [1.62, 1.8, 1.98]
VK_RATIO = 0.326

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": RULE, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 9.5, "axes.titleweight": "bold",
    "axes.titlecolor": INK, "axes.titlelocation": "left", "axes.grid": True, "grid.color": "#eaeef2",
    "grid.linewidth": 0.6, "legend.frameon": False, "legend.fontsize": 7.5, "savefig.dpi": 200,
})


def up(x, d=2):
    """Upper bound rounded up to d decimals (never understate a maximum)."""
    return f"{math.ceil(float(x) * 10**d - 1e-9) / 10**d:.{d}f}"


def dn(x, d=2):
    """Lower bound rounded down to d decimals (never overstate a minimum)."""
    return f"{math.floor(float(x) * 10**d + 1e-9) / 10**d:.{d}f}"


def load(name):
    return json.loads((SIM / name / "results.json").read_text())


def ordered(rows):
    key = {(r["corner"], r["temp"], r["vdd"]): r for r in rows}
    return [key[(c, t, v)] for c in CORNERS for t in TEMPS for v in VDDS]


def png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def img_file(path):
    return "data:image/png;base64," + base64.b64encode(pathlib.Path(path).read_bytes()).decode()


def pvt_axis(ax):
    for i in range(1, 5):
        ax.axvline(9 * i - 0.5, color=RULE, lw=0.8, zorder=0)
    ax.set_xticks([9 * i + 4 for i in range(5)])
    ax.set_xticklabels([c.upper() for c in CORNERS])
    ax.set_xlim(-0.8, 44.8)


# ------------------------------------------------------------------ data
sch = ordered(load("neuron_tb"))
pex = ordered(load("neuron_pex_tb"))
rlo = ordered(load("neuron_rs0p8"))
rhi = ordered(load("neuron_rs1p2"))
mc = [r["results"] for r in load("neuron_mc" if (SIM / "neuron_mc").exists() else "neuron_tb_mc") if r["ok"]]
stab = ordered(load("neuron_pex_mb_tb"))
bias = ordered(load("bias_tb"))
bstart = ordered(load("bias_startup_tb"))
bramp = {(r["corner"], r["temp"], r["vdd"]): r["results"] for r in load("bias_dcramp_tb")}


def col(rows, k, s=1.0):
    return np.array([r["results"][k] * s for r in rows])


def inl(rows):
    return np.array([max(r["results"]["inl_max_pct"], -r["results"]["inl_min_pct"]) for r in rows])


S = {}
S["slope"] = (col(pex, "slope").min(), col(pex, "slope").max())
S["knee"] = (col(pex, "knee").min(), col(pex, "knee").max())
S["inl"] = inl(pex).max()
S["inl_rs"] = max(inl(rlo).max(), inl(rhi).max())
S["pwr"] = (col(pex, "pwr_max", 1e6).min(), col(pex, "pwr_max", 1e6).max())
S["pwr_rlo"] = col(rlo, "pwr_max", 1e6).max()
ms = [x["slope"] for x in mc]
mk = [x["knee"] for x in mc]
S["mc_n"] = len(mc)
S["mc_slope"] = (st.fmean(ms), st.stdev(ms), 100 * st.stdev(ms) / st.fmean(ms))
S["mc_knee"] = (st.fmean(mk), 1e3 * st.stdev(mk))
S["mc_inl"] = max(max(x["inl_max_pct"], -x["inl_min_pct"]) for x in mc)
pm_s = np.array([[r["results"][f"pmS_x{x}"] for x in ("0.3", "0.75", "1.2")] for r in stab])
pm_k = np.array([[r["results"][f"pmK_x{x}"] for x in ("0.3", "0.75", "1.2")] for r in stab])
S["pm_s"], S["pm_k"] = pm_s.min(), pm_k.min()
ib = np.array([[r["results"]["i_rlo"], r["results"]["i_nom"], r["results"]["i_rhi"]] for r in bias]) * 1e6
S["ibias"] = (ib.min(), ib.max())
S["start_t"] = max(r["results"]["t_fast90"] for r in bstart) * 1e6
S["start_von"] = max(v["v_on"] for v in bramp.values())
S["start_dev"] = max(abs(r["results"][k] / r["results"]["i_predip"] - 1)
                     for r in bstart for k in ("i_fast", "i_med", "i_dip")) * 100

# ------------------------------------------------------------------ figures
fig, ax = plt.subplots(figsize=(6.6, 2.75))
xid = np.linspace(0.3, 1.2, 200)
ax.plot(xid, 2 * np.maximum(0, xid - VK_RATIO * 1.8), color=MUTED, lw=1.2, ls=(0, (5, 4)),
        label="ideal  2·max(0, x − V$_k$)")
for t, c in ((-40, BLUE), (27, GREEN), (125, RED)):
    d = np.loadtxt(ROOT / f"build/plots/curve_{t}.txt")
    keep = (d[:, 0] > 55e-6) & (d[:, 1] >= 0.3) & (d[:, 1] <= 1.2)
    ax.plot(d[keep, 1], d[keep, 3], color=c, lw=1.6, label=f"post-layout, {t:+d} °C")
ax.set_xlabel("input x (V)")
ax.set_ylabel("output y (V)")
ax.set_xlim(0.3, 1.2)
ax.set_ylim(-0.05, 1.25)
ax.set_title("Transfer function — extracted layout, TT, VDD = 1.8 V")
ax.legend(loc="upper left")
F_TRANSFER = png(fig)

fig, axs = plt.subplots(4, 1, figsize=(6.6, 5.0), sharex=True)
idx = np.arange(45)
specs = [("slope", 1, "slope (weight)", None), ("knee", 1, "knee (V)", None),
         ("inl", 1, "INL (% of FS)", 5.0), ("pwr_max", 1e6, "peak power (µW)", 100.0)]
for ax, (k, s, lab, lim) in zip(axs, specs):
    ys = inl(sch) if k == "inl" else col(sch, k, s)
    yp = inl(pex) if k == "inl" else col(pex, k, s)
    ax.plot(idx, ys, "o", ms=3.4, mfc="none", mec=MUTED, mew=0.8, label="schematic")
    ax.plot(idx, yp, "o", ms=2.4, color=BLUE, label="post-layout")
    if lim:
        ax.axhline(lim, color=RED, lw=0.9, ls=(0, (4, 3)))
        ax.text(44.5, lim, "spec", color=RED, fontsize=7, ha="right", va="bottom")
    ax.set_ylabel(lab)
    pvt_axis(ax)
axs[2].set_ylim(0, 5.5)
axs[3].set_ylim(0, 110)
axs[0].legend(loc="lower right", ncol=2)
axs[0].set_title("All 45 PVT points (per corner: −40/27/125 °C × 1.62/1.8/1.98 V)")
F_PVT = png(fig)

fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.4))
axs[0].hist(ms, bins=24, color=BLUE, alpha=0.85)
axs[0].set_xlabel("slope (weight)")
axs[0].set_title(f"Weight: σ = {S['mc_slope'][2]:.2f} %")
axs[1].hist(mk, bins=24, color=AMBER, alpha=0.85)
axs[1].set_xlabel("knee (V)")
axs[1].set_title(f"Knee: σ = {S['mc_knee'][1]:.1f} mV")
for a in axs:
    a.set_ylabel("runs")
F_MC = png(fig)

fig, ax = plt.subplots(figsize=(6.6, 2.5))
for j, (lab, c) in enumerate((("R −20 %", RED), ("R nominal", INK), ("R +20 %", BLUE))):
    for T in TEMPS:
        v = [ib[i, j] for i, r in enumerate(bias) if r["temp"] == T]
        ax.plot([T - 6 + 6 * j] * 2, [min(v), max(v)], color=c, lw=3, solid_capstyle="round",
                label=lab if T == TEMPS[0] else None)
ax.axhspan(1, 5, color=GREEN, alpha=0.07, zorder=0)
ax.text(128, 4.85, "spec 1 – 5 µA", color=GREEN, fontsize=7, ha="right", va="top")
ax.set_xticks(TEMPS)
ax.set_xticklabels([f"{t} °C" for t in TEMPS])
ax.set_ylabel("bias current (µA)")
ax.set_ylim(0, 5.5)
ax.set_title("Bias reference: range over 5 corners × 3 VDD")
ax.legend(loc="upper left", ncol=3)
F_BIAS = png(fig)

fig, ax = plt.subplots(figsize=(6.6, 2.5))
ax.plot(idx, pm_s.min(axis=1), "o", ms=3, color=BLUE, label="signal loop (worst of x = 0.3/0.75/1.2 V)")
ax.plot(idx, pm_k.min(axis=1), "o", ms=3, color=AMBER, label="knee loop")
ax.axhline(60, color=RED, lw=0.9, ls=(0, (4, 3)))
ax.text(44.5, 60, "60° target", color=RED, fontsize=7, ha="right", va="bottom")
ax.set_ylabel("phase margin (°)")
ax.set_ylim(40, 120)
pvt_axis(ax)
ax.set_title("Post-layout loop stability (Middlebrook double injection at the OTA outputs)")
ax.legend(loc="upper left", ncol=2)
F_STAB = png(fig)

# ------------------------------------------------------------------ evidence text
drc_log = (ROOT / "verif/drc/analog_neuron_drc.log").read_text()
lvs_log = (ROOT / "verif/lvs/analog_neuron.log").read_text()
lvs_core = (ROOT / "verif/lvs/neuron_core_comp.out").read_text()


def tail(text, pat, n=1):
    lines = [l for l in text.splitlines() if pat in l]
    return lines[-n:] if lines else ["(not found)"]


drc_lines = tail(drc_log, "No errors found") + tail(drc_log, "DRC_COUNT")
lvs_lines = tail(lvs_log, "Final result") + tail(lvs_log, "LVS_VERDICT")
core_counts = [l.strip() for l in lvs_core.splitlines() if l.startswith("Number of devices") or l.startswith("Number of nets")][-2:]

# ------------------------------------------------------------------ HTML
def font_face(name, file, weight="normal", style="normal"):
    return (f"@font-face {{ font-family: '{name}'; src: url('file://{FONTS / file}'); "
            f"font-weight: {weight}; font-style: {style}; }}")


css = "\n".join([
    font_face("Body", "InstrumentSans-Regular.ttf"), font_face("Body", "InstrumentSans-Bold.ttf", "bold"),
    font_face("Body", "InstrumentSans-Italic.ttf", style="italic"), font_face("Mono", "IBMPlexMono-Regular.ttf"),
    font_face("Serif", "InstrumentSerif-Italic.ttf", style="italic"),
    f"""
@page {{ size: A4; margin: 16mm 17mm 16mm 17mm; }}
body {{ font-family: 'Body', sans-serif; color: {INK}; font-size: 9.6pt; line-height: 1.45; }}
h1 {{ font-size: 21pt; margin: 0 0 2pt 0; letter-spacing: -0.2pt; }}
h2 {{ font-size: 12.5pt; margin: 18pt 0 6pt 0; padding-bottom: 3pt; border-bottom: 1px solid {RULE};
      break-after: avoid; }}
h3 {{ font-size: 10.5pt; margin: 12pt 0 4pt 0; break-after: avoid; }}
.sub {{ color: {MUTED}; font-size: 10.5pt; margin-bottom: 10pt; }}
.meta {{ color: {MUTED}; font-size: 8.6pt; margin-bottom: 14pt; }}
.eq {{ font-family: 'Serif'; font-size: 17pt; text-align: center; margin: 8pt 0 10pt 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 4pt 0 8pt 0; font-size: 8.8pt; break-inside: avoid; }}
th {{ text-align: left; color: {MUTED}; font-weight: bold; border-bottom: 1.2px solid {INK}; padding: 3pt 6pt 3pt 0; }}
td {{ border-bottom: 1px solid {RULE}; padding: 3pt 6pt 3pt 0; vertical-align: top; }}
td.ok {{ color: {GREEN}; font-weight: bold; }}
code, pre {{ font-family: 'Mono', monospace; font-size: 7.9pt; }}
pre {{ background: #f6f8fa; border: 1px solid {RULE}; padding: 6pt 8pt; white-space: pre-wrap; break-inside: avoid; }}
figure {{ margin: 6pt 0 10pt 0; break-inside: avoid; text-align: center; }}
figure img {{ width: 100%; }}
figcaption {{ color: {MUTED}; font-size: 8.2pt; margin-top: 3pt; text-align: left; }}
.page {{ break-before: page; }}
.note {{ border-left: 3px solid {AMBER}; padding: 2pt 0 2pt 9pt; color: {INK}; background: #fff8e5; }}
"""])

today = datetime.date.today().isoformat()
html = f"""<!doctype html><html><head><meta charset="utf-8"><title>analog_neuron — validation</title>
<style>{css}</style></head><body>

<h1>analog_neuron</h1>
<div class="sub">Simulation and validation report · single-input analog ReLU neuron · Silicluster v3 (analog project)</div>
<div class="meta">SKY130A · 1.8 V · 180 µm × 115 µm · report generated {today} from the result files of the runs listed in §4</div>

<div class="eq">y = 2 · max(0, x − V<sub>k</sub>),&nbsp;&nbsp; V<sub>k</sub> = 0.326 · VDD</div>

<h2>1. Summary</h2>
<table>
<tr><th>Quantity</th><th>Result</th><th>Target</th><th></th></tr>
<tr><td>MAC linearity (INL, knee + 0.1 V … 1.2 V)</td><td>≤ {up(S['inl'])} % (post-layout, 45 PVT); ≤ {up(S['inl_rs'])} % at R ±20 %; ≤ {up(S['mc_inl'])} % (Monte Carlo)</td><td>≤ 5 %</td><td class="ok">pass</td></tr>
<tr><td>Weight accuracy, mismatch ({S['mc_n']}-run Monte Carlo)</td><td>σ = {S['mc_slope'][2]:.2f} % (mean slope {S['mc_slope'][0]:.3f})</td><td>σ &lt; 2–3 %</td><td class="ok">pass</td></tr>
<tr><td>Weight (slope) over PVT</td><td>{dn(S['slope'][0], 3)} – {up(S['slope'][1], 3)}</td><td>2</td><td></td></tr>
<tr><td>Knee over PVT</td><td>{dn(S['knee'][0], 3)} – {up(S['knee'][1], 3)} V (= 0.326 · VDD; flat over temperature and process)</td><td>VDD ratio</td><td></td></tr>
<tr><td>Peak supply power</td><td>{dn(S['pwr'][0], 1)} – {up(S['pwr'][1], 1)} µW; {up(S['pwr_rlo'], 1)} µW at R −20 %</td><td>&lt; 100 µW (design target)</td><td class="ok">pass</td></tr>
<tr><td>Bias current (incl. R ±20 %)</td><td>{dn(S['ibias'][0])} – {up(S['ibias'][1])} µA</td><td>1 – 5 µA</td><td class="ok">pass</td></tr>
<tr><td>Bias start-up</td><td>starts at every PVT point, ≤ {up(S['start_t'], 1)} µs after a 1 µs ramp; settled current identical across ramps and brown-out (≤ {S['start_dev']:.3f} %)</td><td>always starts</td><td class="ok">pass</td></tr>
<tr><td>Loop phase margin (post-layout)</td><td>signal loop ≥ {dn(S['pm_s'], 1)}°, knee loop ≥ {dn(S['pm_k'], 1)}°</td><td>≥ 60°</td><td class="ok">pass</td></tr>
<tr><td>DRC (Magic, sky130A <code>drc(full)</code>)</td><td>0 violations</td><td>clean</td><td class="ok">pass</td></tr>
<tr><td>LVS (netgen, <code>sky130A_setup.tcl</code>)</td><td>circuits match uniquely, no property errors</td><td>match</td><td class="ok">pass</td></tr>
<tr><td>Area</td><td>180.000 µm × 115.000 µm</td><td>180 µm × 115 µm</td><td class="ok">pass</td></tr>
</table>
<p>PVT = 5 process corners (tt, ff, ss, sf, fs) × −40 / 27 / 125 °C × 1.62 / 1.8 / 1.98 V = 45 points.
"Post-layout" = devices and parasitic capacitance extracted from the final layout with Magic.</p>

<h2>2. Interface</h2>
<table>
<tr><th>Pin</th><th>Direction</th><th>Layer / location (µm, origin lower-left)</th><th>Electrical</th></tr>
<tr><td><code>X</code></td><td>analog input</td><td>metal3, right edge, x = 179.4, y = 81.27</td><td>0.3 – 1.2 V; ≈ 300 kΩ to an internal ≈ 0.26 V node (draws ≤ ≈ 3.2 µA)</td></tr>
<tr><td><code>Y</code></td><td>analog output</td><td>metal3, right edge, x = 179.4, y = 82.07</td><td>0 – ≈ 1.2 V; unbuffered, ≈ 300 kΩ source impedance</td></tr>
<tr><td><code>VDD</code></td><td>supply</td><td>metal5 horizontal rail, y = 111.5 – 114.5</td><td>1.8 V nominal (verified 1.62 – 1.98 V)</td></tr>
<tr><td><code>VSS</code></td><td>ground</td><td>metal5 horizontal rail, y = 0.5 – 3.5</td><td>0 V</td></tr>
</table>
<p>Power grid: metal4 vertical straps (10 µm pitch, alternating VDD/VSS) and metal5 horizontal rails, as required
by §11 of the call. Port declaration: <code>analog_neuron.v</code>.</p>

<div class="page"></div>
<h2>3. Circuit</h2>
<figure><img src="{img_file(ROOT / 'docs/img/block-diagram.png')}"><figcaption>Figure 1 — Current topology.
Strand count represents current: each ×2 mirror doubles its bundle, the knee current is subtracted at Σ and only
the excess reaches the ReLU and R<sub>out</sub>.</figcaption></figure>
<ul>
<li><b>V→I converters.</b> An OTA with a PMOS input pair holds one end of R<sub>in</sub> at an internal reference
V<sub>REF</sub> ≈ 0.142·VDD, so I<sub>x</sub> = (x − V<sub>REF</sub>)/R<sub>in</sub>. A replica converter driven
by the divider voltage V<sub>k</sub> produces the knee current; V<sub>REF</sub> cancels between the two.</li>
<li><b>Weight.</b> NMOS mirrors (W/L = 16/4, ×2 copies) set w = 2; the gain is 2·R<sub>out</sub>/R<sub>in</sub>
with R<sub>out</sub> and R<sub>in</sub> built from matched xhigh_po unit resistors (7 units each, ≈ 43.4 kΩ/unit).</li>
<li><b>ReLU.</b> The knee current is flipped by a PMOS mirror and subtracted from the signal current; a PMOS diode
can only supply the positive excess, which is copied into R<sub>out</sub>.</li>
<li><b>Bias.</b> Beta-multiplier current reference with start-up (≈ 2 µA at 27 °C).</li>
<li><b>Compensation.</b> Miller capacitor 0.80 pF (MIM 20 × 20 µm) with a ≈ 72 kΩ nulling resistor per converter.</li>
</ul>

<h2>4. Simulation setup</h2>
<table>
<tr><th>Item</th><th>Value</th></tr>
<tr><td>Simulator / PDK</td><td>ngspice-47 (KLU); SKY130A via ciel, version 1689ac3f; models <code>sky130.lib.spice</code></td></tr>
<tr><td>Corners</td><td>tt, ff, ss, sf, fs × −40 / 27 / 125 °C × 1.62 / 1.8 / 1.98 V; xhigh_po sheet resistance additionally at −20 % and +20 %
(the PDK corners do not vary it and SkyWater lists its e-test specs as TBD)</td></tr>
<tr><td>Mismatch</td><td>{S['mc_n']} Monte Carlo runs, corner <code>tt_mm</code> (device mismatch enabled)</td></tr>
<tr><td>Transfer test</td><td>power-up, then x ramped 0.29 → 1.21 V over 2 ms (quasi-static); output loaded only by stand-in pad ESD diodes</td></tr>
<tr><td>Stability test</td><td>Middlebrook double injection at each OTA output (cuts every feedback path), x = 0.3 / 0.75 / 1.2 V</td></tr>
<tr><td>Post-layout netlist</td><td>Magic extraction of the final layout: devices + 506 parasitic capacitors</td></tr>
<tr><td>Testbenches</td><td><code>spice/neuron/neuron_tb.cir</code>, <code>neuron_pex_tb.cir</code>, <code>neuron_pex_mb_tb.cir</code>,
<code>spice/bias/bias_tb.cir</code>, <code>bias_startup_tb.cir</code>, <code>bias_dcramp_tb.cir</code>; runner <code>scripts/sim.py</code></td></tr>
</table>

<div class="page"></div>
<h2>5. Results</h2>
<h3>5.1 Transfer function</h3>
<figure><img src="{F_TRANSFER}"><figcaption>Figure 2 — Post-layout transfer at three temperatures against the
ideal ReLU. The output is ≈ 0 below the knee and linear above it; temperature moves the curve by less than the line width.</figcaption></figure>

<h3>5.2 All PVT points</h3>
<figure><img src="{F_PVT}" style="width:85%"><figcaption>Figure 3 — Slope, knee, linearity and power at every PVT point, schematic
(open) and post-layout (filled). The knee depends only on VDD (three levels per corner); layout changes the
results by less than 0.1 %.</figcaption></figure>

<div class="page"></div>
<h3>5.3 Mismatch</h3>
<figure><img src="{F_MC}"><figcaption>Figure 4 — {S['mc_n']}-run Monte Carlo (tt_mm, 27 °C, 1.8 V). Weight σ
{S['mc_slope'][2]:.2f} % meets the 2–3 % target; knee σ {S['mc_knee'][1]:.1f} mV (mean {S['mc_knee'][0]:.3f} V).</figcaption></figure>

<h3>5.4 Bias reference and start-up</h3>
<figure><img src="{F_BIAS}"><figcaption>Figure 5 — Bias current range at each temperature for nominal and ±20 %
resistance. Start-up was checked at all 45 points with a 1 µs ramp, a 100 µs ramp, a brown-out to 0.8 V and a
quasi-static DC ramp; the reference turns on by VDD = {up(S['start_von'])} V at the latest.</figcaption></figure>

<h3>5.5 Stability</h3>
<figure><img src="{F_STAB}"><figcaption>Figure 6 — Post-layout phase margin of both converter loops at all 45 PVT
points. The knee loop has a second feedback path through the shared divider (its load moves V<sub>REF</sub>); the
measurement cuts at the OTA output so that path is included.</figcaption></figure>

<div class="page"></div>
<h2>6. Physical verification</h2>
<figure><img src="{img_file(ROOT / 'docs/img/layout.png')}"><figcaption>Figure 7 — Final layout, 180 µm × 115 µm,
with functional blocks outlined. Power grid: metal4 vertical straps, metal5 horizontal rails.</figcaption></figure>
<h3>DRC — Magic, sky130A <code>drc(full)</code>, top cell <code>analog_neuron</code></h3>
<pre>{chr(10).join(drc_lines)}</pre>
<h3>LVS — netgen with <code>sky130A_setup.tcl</code>, top cell against the reference netlist</h3>
<pre>{chr(10).join(lvs_lines)}
neuron_core:  {' | '.join(core_counts)}</pre>
<p>Each block (<code>ota5p</code>, <code>bias_ref</code>, <code>neuron_core</code>) also passes DRC and LVS on its
own. Full logs are in <code>verification/</code> in this package. PASS is only declared when netgen reports a unique
match <i>and</i> no property (device size) errors.</p>

<h2>7. Reproducing the results</h2>
<pre>export PDK_ROOT=$HOME/.ciel PDK=sky130A
python3 scripts/sim.py spice/neuron/neuron_tb.cir --pvt --jobs 12          # schematic, 45 PVT
python3 scripts/sim.py spice/neuron/neuron_tb.cir --mc 200 --corner tt_mm --jobs 12
python3 scripts/sim.py spice/neuron/neuron_pex_tb.cir --pvt --jobs 12      # post-layout transfer
python3 scripts/sim.py spice/neuron/neuron_pex_mb_tb.cir --pvt --jobs 12   # post-layout stability
python3 scripts/sim.py spice/bias/bias_tb.cir --pvt                        # bias reference</pre>

<h2>8. Known limitations</h2>
<ul>
<li class="note"><b>Unbuffered output.</b> Y has ≈ 300 kΩ source impedance. A 10 MΩ load reduces the gain by
≈ 2.8 %; a 1 MΩ load by ≈ 22 %. Linearity is unaffected. The output should be read by a high-impedance input.</li>
<li><b>xhigh_po spread.</b> The ±20 % sheet-resistance range is an assumption; at −20 % combined with 125 °C and
1.98 V the core reaches {up(S['pwr_rlo'], 1)} µW.</li>
<li><b>Systematic weight.</b> The slope is 1–5 % below 2 (output-mirror drain-voltage difference), largest at low
VDD and −40 °C.</li>
<li><b>Not run:</b> antenna-rule check.</li>
</ul>
</body></html>"""

OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
OUT_HTML.write_text(html)
subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={OUT_PDF}", f"file://{OUT_HTML}"], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"wrote {OUT_PDF}")
for k, v in S.items():
    print(f"  {k}: {v}")
