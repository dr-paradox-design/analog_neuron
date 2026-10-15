# Neuron core — knee-replica ReLU neuron

Netlists: `spice/neuron/neuron_core.spice`, `vi_conv.spice`, `ota5p.spice`, plus
`spice/bias/bias_ref.spice` · Testbenches: `spice/neuron/neuron_tb.cir` (transfer, linearity,
power, Monte Carlo), `vi_conv_tb.cir` (V→I linearity), `vi_stab_tb.cir` (loop stability),
`ota5p_tb.cir` (OTA open loop)

## Function

**y = 2 · (R_out / R_in) · max(0, x − V_k)**, with R_out = R_in → **y = 2 · max(0, x − V_k)**

- Weight **w = 2** (×2 NMOS weight mirrors), knee **V_k ≈ 0.331 · VDD ≈ 0.596 V** (ReLU turns on
  there), input range 0.3–1.2 V → y from 0 to ≈ 1.2 V.
- In the y = f(w·x + b) form: w = 2, b = −2·V_k ≈ −1.19 V (output referred).

## Circuit

```
 VDD ─ Ra(9u) ─┬─ VK ─ Rb(4u) ─┬─ VREF ─ Rc(3u) ─ VSS      u = xhigh_po unit, 0.69 × 14.79 µm (≈ 41 kΩ)
               │                │
 x  ── R_in(7u) ─ XVS: OTA + MF holds its node at VREF, MF sinks I_x + I0
 VK ── R_k (7u) ─ XVK: same, MF sinks I_k + I0
       XWS = 2 × MF(XVS)  sinks 2(I_x + I0) from node S
       XWK = 2 × MF(XVK)  sinks 2(I_k + I0) from DK → PMOS flip XPK1/XPK2 sources it into S
 S:    PMOS diode XPR1 supplies only the excess 2(I_x − I_k) > 0      → ReLU
       XPR2 copies it into R_out (7u) → y
```

- **VREF and I0 cancel** between the signal and knee paths; what remains is device mismatch.
- **Thresholds are VDD ratios** (owner decision): VREF = 0.142·VDD, VK = 0.331·VDD — flat over
  temperature and process, ±10 % with the supply. R_k's current returns to VSS through MF_k (not
  into VREF), so VK = VREF·(1 + Rb/Rc) and the divider ratios include that load.
- **Why a PMOS-input OTA:** its inputs sit at VREF ≈ 0.25 V; an NMOS pair needs ≥ 0.75 V.
- **Why I0:** a PMOS copy of the bias (≈ I_ref/2) keeps MF out of deep subthreshold at small x,
  where the loop gain and bandwidth would otherwise collapse.
- **Compensation:** Miller Cc 0.80 pF (MIM 20 × 20 µm) with nulling resistor Rz ≈ 72 kΩ.

## Sizing (2026-10-15)

| Device | W / L (µm) | m | Note |
|---|---|---|---|
| MF (both converters), XWS, XWK | 16 / 4 | 1, 2, 2 | weight mirror; 4× the original area |
| XPK1, XPK2 (knee flip) | 32 / 4 | 1 | |
| I0 (both converters) | 16 / 4 | 1 | ≈ I_ref / 2 |
| XPR1, XPR2 (ReLU diode, output copy) | 32 / 8 | 1 | |
| OTA: tail / input pair / load | 16/2 · 10/1 · 2/2 | 1 | |
| Cc / Rz | 0.80 pF (20 × 20 MIM) / 0.69 × 25 µm | — | |
| Resistor unit | xhigh_po 0.69 × 14.79 µm | — | divider 9:4:3, R_in = R_k = R_out = 7 units |

Chosen from a 100-run Monte Carlo per variant (tt_mm, 27 °C, 1.8 V):

| Variant | Slope σ | Knee σ |
|---|---|---|
| Original (mirror 8/2) | 2.81 % | 49.7 mV |
| Mirror 16/4 | 1.33 % | 31.4 mV |
| **+ flip 32/4, I0 16/4 (chosen)** | **1.36 %** | **23.7 mV** |
| + 4× OTA devices | 1.36 % | 22.6 mV |

## Verified results — final sizing

| Check | Result | Spec |
|---|---|---|
| 45 PVT points (5 corners × −40/27/125 °C × 1.62/1.8/1.98 V) | 45/45 clean | all corners |
| Slope (w) over PVT | 1.903 – 1.995 | w = 2 |
| Knee over PVT | 0.526 – 0.645 V = 0.326·VDD (flat over T and process) | VDD ratio |
| MAC linearity (INL, knee + 0.1 V to 1.2 V) | ≤ 0.71 % | ≤ 5 % ✅ |
| Output below the knee | ≤ 26 µV | — |
| R −20 % / +20 % (all xhigh_po), 45 PVT each | slope 1.902 – 1.996, knee unchanged, INL ≤ 0.76 % | ✅ |
| Monte Carlo, 200 runs: slope σ | **1.47 %** (1.887 – 2.037) | σ < 2–3 % ✅ |
| Monte Carlo: knee σ / INL worst | 22.3 mV / 0.81 % | — |
| V→I loop phase margin, 45 PVT × 3 inputs | ≥ 71.7° (crossover 2.0 – 5.2 MHz) | ≥ 60° ✅ |
| Peak power, R nominal | 37.8 – 78.3 µW | < 100 µW ✅ |
| **Peak power, R −20 %** | **47.3 – 98.1 µW** | < 100 µW ⚠️ no room for a buffer |

SkyWater documents xhigh_po electrical specs as "still TBD", so ±20 % sheet-resistance spread is
an assumption, deliberately conservative.

Systematic slope is 1–5 % below 2: the output copy XPR2 has less drain voltage than the diode
XPR1 when y is high, most at low VDD and cold.

### Supply-current breakdown at the worst power corner (ff, 125 °C, 1.98 V, R −20 %, x = 1.2 V)

| Branch | Current | Share |
|---|---|---|
| Knee flip XPK1 + XPK2 (each 2·(I_k + I0)) | 14.6 µA | 30 % |
| ReLU diode + output copy XPR1 + XPR2 | 10.5 µA | 21 % |
| Bias reference branches | 7.7 µA | 16 % |
| OTA tails | 7.6 µA | 16 % |
| Divider (incl. knee-converter input current) | ≈ 4.9 µA | 10 % |
| I0 sources | 3.5 µA | 7 % |
| Total | 48.9 µA (≈ 97 µW) | |

### Output loading (raw output, no buffer; output impedance ≈ R_out ≈ 300 kΩ)

| Load on y | Slope | Gain change | INL |
|---|---|---|---|
| none | 1.958 | — | 0.48 % |
| 10 MΩ ‖ 10 pF | 1.903 | −2.8 % | 0.47 % |
| 1 MΩ ‖ 10 pF | 1.520 | −22 % | 0.38 % |

Loading costs gain, not linearity.

### V→I converter

- Endpoint INL ≤ 0.054 % over 0.3–1.2 V at all 5 corners (original sizing); held node within
  0.6 mV of VREF.

### Area (Magic-generated devices, guard rings included)

≈ 4,850 µm² of devices at the original sizing (≈ 6,200 µm² with the larger mirrors and Cc) →
≈ 12–14k µm² with routing, against the 20,700 µm² budget. R_in/R_out/divider resistors must be
folded unit segments (a single R_in would be 109 µm long). The MIM capacitors (metal 3–4) need
gaps in the M4 power grid.

## Simulation notes

- The PDK **xhigh_po** model has negative voltage coefficients, so R crosses zero near |V| ≈ 1 kV;
  Newton can lock onto spurious kV solutions (≈ 3 % of mismatch seeds). `neuron_tb.cir` starts
  from a power-up, checks 13 internal nodes and the supply current, and re-runs the same seed
  from a nodeset operating point if anything is non-physical. Both start methods give identical
  results when both are valid.
- x is swept as a 2 ms ramp, not a DC sweep (the DC sweep needs repeated gmin rescues).

## Open

- **Output stage** — depends on the output-load spec (pending Silicluster). The raw output is a
  ≈ 300 kΩ source; it needs ≥ 10 MΩ loads for < 3 % gain error.
- **Power margin** — at R −20 %, 125 °C, 1.98 V the core alone takes 98 µW. Any buffer needs the
  core power reduced first (knee flip carries I0 twice; bias branches can run at lower current).
