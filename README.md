<div align="center">

# analog_neuron

**A single-input analog ReLU neuron in SkyWater SKY130: schematic to GDS with a fully open-source flow.**

![process](https://img.shields.io/badge/process-SKY130A-1f6feb?style=flat-square)
![area](https://img.shields.io/badge/area-180_×_115_µm-6e7681?style=flat-square)
![DRC](https://img.shields.io/badge/DRC-Magic_+_KLayout_clean-2ea043?style=flat-square)
![LVS](https://img.shields.io/badge/LVS-clean-2ea043?style=flat-square)
![antenna](https://img.shields.io/badge/antenna-clean-2ea043?style=flat-square)
![PVT](https://img.shields.io/badge/post--layout_PVT-45%2F45-2ea043?style=flat-square)
![status](https://img.shields.io/badge/Silicluster_v3-submission_ready-8957e5?style=flat-square)

<img src="docs/img/layout.png" alt="Layout of analog_neuron" width="100%">

<sub>✅ schematic sign-off&nbsp;&nbsp;→&nbsp;&nbsp;✅ layout sign-off&nbsp;&nbsp;→&nbsp;&nbsp;✅ GDS cross-verified&nbsp;&nbsp;→&nbsp;&nbsp;⏳ submission to Silicluster v3 (deadline 31 Oct 2026)</sub>

</div>

## What it computes

<div align="center">

**y = 2 · max(0, x − V<sub>k</sub>)**  with the knee **V<sub>k</sub> = 0.326 · VDD** (0.586 V at 1.8 V)

<img src="docs/img/transfer.png" alt="Post-layout transfer function" width="80%">

</div>

## Theory of operation

<img src="docs/img/block-diagram.png" alt="Current topology of the neuron: signal and knee paths summed at Σ, then ReLU and R_out" width="100%">

The circuit implements one artificial neuron, $y = f(w\,x + b)$ with a ReLU activation $f(u) = \max(0, u)$,
fixed weight $w = 2$ and a bias set by a knee voltage $V_k$:

```math
y \;=\; 2\cdot\max\!\left(0,\; x - V_k\right) \qquad\Longleftrightarrow\qquad w = 2,\quad b = -2V_k
```

Everything is done in the **current domain**: voltages are converted to currents, currents are scaled by
mirrors, added and subtracted by Kirchhoff's current law at a single node, rectified, and converted back to a
voltage by a resistor.

### 1. Ratiometric references

A resistor divider from VDD (xhigh_po unit resistors, ratio $R_a : R_b : R_c = 9:4:3$) produces two
references. The knee converter's input resistor $R_k$ (7 units) also draws current from $V_k$, so solving the
divider with that load:

```math
V_{REF} = \frac{21}{148}\,V_{DD} \approx 0.142\,V_{DD}, \qquad V_k = \frac{49}{148}\,V_{DD} \approx 0.331\,V_{DD}
```

Both are pure resistor ratios: they do not move with temperature or process, only with the supply.
At 1.8 V: $V_{REF} \approx 0.256$ V and $V_k \approx 0.596$ V.

### 2. Voltage-to-current converters

Each converter is an OTA that holds one end of a resistor at $V_{REF}$ (a virtual ground) by driving the
gate of an NMOS transistor $M_F$ that sinks the resistor current. With the input applied to the other end:

```math
I_x = \frac{x - V_{REF}}{R_{in}}, \qquad I_k = \frac{V_k - V_{REF}}{R_{in}} \qquad (R_k = R_{in} \approx 304\ \text{k}\Omega)
```

$M_F$ also carries a small constant current $I_0 \approx I_{ref}/2$ from a PMOS source, so it never drops into
deep subthreshold when $I_x \to 0$ (which would collapse the loop gain). The OTA uses a **PMOS input pair**
because its inputs sit at $V_{REF} \approx 0.26$ V; an NMOS pair would need a common mode above
$V_{GS,n} + V_{DS,sat} \approx 0.75$ V. With 58–67 dB of loop gain the virtual ground stays within 1 mV of $V_{REF}$.

### 3. Weight and summation

Two copies of each $M_F$ (current-mirror ratio **2**) produce $2(I_x + I_0)$ and $2(I_k + I_0)$. The knee
current is turned around by a PMOS mirror so that it is *sourced* into the summing node S, while the signal
current is *sunk* from it. Kirchhoff's current law at S:

```math
I_S = 2\,(I_x + I_0) - 2\,(I_k + I_0) = 2\,(I_x - I_k) = \frac{2\,(x - V_k)}{R_{in}}
```

$V_{REF}$ and $I_0$ appear in both paths and cancel exactly; only device mismatch remains.

### 4. ReLU

The current $I_S$ is supplied by a diode-connected PMOS. A diode can only *source* current, so when the
signal current is smaller than the knee current the diode turns off and the excess is zero:

```math
I_{out} = \max\!\left(0,\; I_S\right)
```

This is the activation function — obtained from the physics of one transistor, with no comparator or
extra bias.

### 5. Current-to-voltage output

A second PMOS copies $I_{out}$ into $R_{out}$ (7 units, the same as $R_{in}$):

```math
y = R_{out}\,I_{out} = 2\,\frac{R_{out}}{R_{in}}\,\max(0,\; x - V_k) = 2\cdot\max(0,\; x - V_k)
```

At $x = 1.2$ V: $I_x \approx 3.1\ \mu$A, $I_k \approx 1.1\ \mu$A, $I_{out} \approx 4.0\ \mu$A, $y \approx 1.2$ V.

### 6. Why it holds across process, temperature and supply

| Quantity | Set by | Cancels |
|---|---|---|
| Weight $w$ | $2 \cdot R_{out}/R_{in}$ | sheet resistance and its temperature coefficient (same material, same units), transistor threshold (ratio of identical mirrors) |
| Knee $V_k$ | $\tfrac{49}{148}V_{DD}$ | sheet resistance, temperature, process |
| $V_{REF}$, $I_0$, bias current | divider, bias reference | appear in both paths, subtracted at S |

The absolute currents do change (roughly 2× from −40 °C to 125 °C), but they never set the transfer
function. Measured over all 45 PVT points: slope 1.90–2.00, knee $0.326\,V_{DD}$ (the small offset from
$0.331\,V_{DD}$ comes from the fitted-line knee definition and the slightly sub-2 slope).

### 7. Bias reference

A **β-multiplier** (constant-$g_m$) reference: transistor $M_2$ is $K = 4$ times wider than $M_1$ and has a
source resistor $R_1$; a PMOS mirror forces equal currents in both branches. In weak/moderate inversion
$V_{GS1} = V_{GS2} + I R_1$ gives

```math
I_{ref} \approx \frac{n\,U_T \ln K}{R_1}, \qquad U_T = \frac{kT}{q}
```

about 2 µA at 27 °C ($n \approx 1.3$, $R_1 \approx 24$ kΩ). The current is PTAT/R, so it rises with
temperature (1.4 → 3.1 µA from −40 to 125 °C) — acceptable because it only biases the OTAs and $I_0$. The
circuit also has a stable zero-current state; a start-up branch injects current into the NMOS gate line until
the loop is running, then switches itself fully off.

### 8. Accuracy

- **Mismatch.** Current-mirror error follows Pelgrom's law,
  $\sigma(\Delta I/I) \approx (g_m/I_D)\cdot A_{VT}/\sqrt{W L}$: quadrupling the mirror gate area (16/4 µm)
  halved the weight spread, $\sigma$ 2.81 % → **1.47 %** (200-run Monte Carlo). Resistors are interdigitated unit
  segments with dummy ends, so $R_{out}/R_{in}$ matches to well under 1 %.
- **Linearity.** INL is the worst deviation from the straight line through $(V_k + 0.1\ \text{V})$ and 1.2 V,
  as a percentage of full scale: **≤ 0.71 %** after layout (target 5 %). Within 0.1 V of the knee the curvature
  belongs to the activation, not to the multiply-accumulate.
- **Systematic slope.** The output PMOS sees less drain voltage than the diode when $y$ is high, so the slope is
  1–5 % below 2 (largest at 1.62 V and −40 °C).

### 9. Stability

Each converter is a two-stage feedback loop (OTA → $M_F$ → resistor node → OTA), compensated by a Miller
capacitor $C_c = 0.8$ pF with a nulling resistor $R_z \approx 72$ kΩ. Choosing $R_z > 1/g_{m,F}$ moves the
right-half-plane zero of plain Miller compensation into the left half-plane, where it adds phase near crossover:

```math
f_z = \frac{1}{2\pi\,C_c\,\left(1/g_{m,F} - R_z\right)}
```

The knee converter has a second, positive feedback path: its current loads the divider, which moves $V_{REF}$
— the OTA's *other* input (about 15 % of the main path). Its stability is therefore measured by Middlebrook
double injection at the OTA output, which opens every path at once. Post-layout phase margin: **≥ 62.5°** (signal
loop) and **≥ 85.7°** (knee loop) at all 45 PVT points.

### 10. Output loading

$Y$ is the unbuffered resistor node, so its source impedance is $\approx R_{out}$. A load $R_L$ divides the output:

```math
y_{\text{loaded}} = y\,\frac{R_L}{R_L + R_{out}}
```

10 MΩ costs ≈ 2.8 % of gain and 1 MΩ ≈ 22 %; linearity is unaffected. Read $Y$ with a high-impedance input.

Full derivations and design decisions: [architecture (ADR-001)](docs/ADR-001-neuron-architecture.md) ·
[neuron core](docs/neuron-core.md) · [bias reference](docs/bias-reference.md).

## Results

Post-layout (extracted devices and parasitic capacitance), 5 process corners × −40 / 27 / 125 °C × 1.62 / 1.8 / 1.98 V.

| | Result | Spec |
|---|---|---|
| MAC linearity (INL) | **≤ 0.71 %** | ≤ 5 % ✅ |
| Weight accuracy σ (200-run Monte Carlo) | **1.47 %** | < 2–3 % ✅ |
| Weight (slope) | 1.90 – 2.00 | 2 |
| Total power | **37.5 – 78.0 µW** | < 100 µW ✅ |
| Loop phase margin (signal / knee loop) | **≥ 62.5° / ≥ 85.7°** | ≥ 60° ✅ |
| Bias current (incl. ±20 % resistor spread) | 1.13 – 3.89 µA | 1 – 5 µA ✅ |
| Area | 180 × 115 µm | 180 × 115 µm ✅ |

Layout parasitics move every result by less than 0.1 % from the schematic.

## Verification

| Check | Tool | Result |
|---|---|---|
| DRC, every cell | Magic, sky130A `drc(full)` | 0 violations |
| DRC of the GDS, manufacturing rules | KLayout, PDK `sky130A_mr.drc` (FEOL + BEOL + off-grid) | 0 violations |
| DRC of the GDS read back | Magic `drc(full)` after `gds read` | 0 violations |
| LVS, every cell and the GDS itself | netgen + `sky130A_setup.tcl` | unique match, 0 property errors |
| Antenna | Magic `antennacheck` | no violations |
| Pin labels / zero-area shapes | KLayout PDK decks | 0 / 0 |
| GDS ↔ .mag | layer-by-layer XOR of a regenerated GDS | identical |

Evidence: [`verif/drc/`](verif/drc) · [`verif/lvs/`](verif/lvs) · [`verif/crossverify/SUMMARY.md`](verif/crossverify/SUMMARY.md) ·
[validation report (PDF)](submit/analog_neuron_validation.pdf)

## Pins

| Pin | Layer | Location (µm) | Notes |
|---|---|---|---|
| `X` | metal3 | right edge, y = 81.27 | input, 0.3 – 1.2 V, ≈ 300 kΩ |
| `Y` | metal3 | right edge, y = 82.07 | output, unbuffered ≈ 300 kΩ: measure with ≥ 10 MΩ |
| `VDD` | metal5 | top rail | 1.8 V |
| `VSS` | metal5 | bottom rail | ground |

Power grid: metal4 vertical straps, metal5 horizontal rails. Interface: [`submit/analog_neuron.v`](submit/analog_neuron.v).

## Submission package

`python3 scripts/make_submission.py` builds `submit/analog_neuron_silicluster_v3.zip` with every item the
Silicluster v3 call (§10) asks for:

| Required | Included |
|---|---|
| GDS of the final layout | `analog_neuron.gds` |
| Magic .mag | top cell + the 17 cells it uses |
| Verilog interface | [`analog_neuron.v`](submit/analog_neuron.v) |
| Testbench and reproduction files | netlists, testbenches, `sim.py`, extracted netlists |
| Simulation and validation document | [`analog_neuron_validation.pdf`](submit/analog_neuron_validation.pdf) |
| DRC / LVS evidence | logs for every cell plus the GDS cross-verification |

## Repository

```
spice/      netlists and testbenches   (bias/ · neuron/ · lvs/ · smoke/ · char/)
scripts/    sim.py (PVT / Monte Carlo runner) · layout/ (layout generator) · DRC / LVS / PEX / GDS ·
            validation_report.py · make_submission.py
mag/        Magic layout, generated by scripts/layout/
gds/        analog_neuron.gds
verif/      DRC and LVS logs, GDS cross-verification, simulation evidence
docs/       design notes, sign-offs, images
submit/     Verilog interface, validation report, submission README
```

## Reproduce

Requires Magic, netgen, ngspice, KLayout and the SKY130A PDK (`PDK_ROOT=$HOME/.ciel`, `PDK=sky130A`).

```bash
# simulate: schematic over 45 PVT corners, 200-run Monte Carlo, then the extracted layout
python3 scripts/sim.py spice/neuron/neuron_tb.cir --pvt --jobs 12
python3 scripts/sim.py spice/neuron/neuron_tb.cir --mc 200 --corner tt_mm --jobs 12
python3 scripts/sim.py spice/neuron/neuron_pex_tb.cir --pvt --jobs 12
python3 scripts/sim.py spice/neuron/neuron_pex_mb_tb.cir --pvt --jobs 12

# generate the layout and the GDS
for b in ota5p bias_ref neuron_core top; do python3 scripts/layout/$b.py; done
CELL=analog_neuron OUT=$PWD/gds/analog_neuron.gds scripts/magic_batch.sh scripts/gds.tcl mag/neuron

# verify
CELL=analog_neuron scripts/magic_batch.sh scripts/drc.tcl mag/neuron
scripts/lvs.sh analog_neuron mag/neuron spice/lvs/analog_neuron_ref.spice analog_neuron
klayout -b -rd input=gds/analog_neuron.gds -rd top_cell=analog_neuron -rd report=build/drc.lyrdb \
        -rd feol=true -rd beol=true -rd offgrid=true -r $PDK_ROOT/sky130A/libs.tech/klayout/drc/sky130A_mr.drc

# report and submission package
python3 scripts/validation_report.py
python3 scripts/make_submission.py
```

<sub>Tools: Magic 8.3.683 · netgen 1.5.324 · ngspice 47 · KLayout 0.30 · SKY130A via ciel.
Details: <a href="docs/ADR-001-neuron-architecture.md">architecture</a> ·
<a href="docs/neuron-core.md">design notes</a> · <a href="docs/layout.md">layout</a> ·
<a href="docs/gate-A.md">schematic sign-off</a> · <a href="docs/gate-B.md">layout sign-off</a> ·
<a href="verif/crossverify/SUMMARY.md">GDS cross-verification</a> ·
<a href="submit/analog_neuron_validation.pdf">validation report</a></sub>
