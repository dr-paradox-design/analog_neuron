# ADR-001: Neuron circuit architecture for Silicluster v3

**Status:** Proposed
**Date:** 2026-10-10
**Deciders:** dr-paradox-design (project owner)

## Context

We must tape out a single-input analog neuron, y = f(w·x + b), on SKY130 for the
Silicluster v3 shuttle. The constraints that shape the architecture:

| Constraint | Value | Architectural pressure |
|---|---|---|
| Devices | nfet_01v8 / pfet_01v8 only | No thick-oxide or native devices; ~0.4–0.6 V thresholds eat headroom |
| Supply | 1.8 V nominal, ±10% (1.62 V worst) | Little room for stacked/cascode devices |
| I/O | 1 analog in, 1 analog out, VDD, VSS; no digital, no clock | w and b are **fixed in silicon**; no trimming, no calibration |
| Input range | 0.3–1.2 V | Front end must accept a 0.9 V swing near both rails at 1.62 V |
| Linearity | ≤ 5% MAC error across input range | Must be observable at the single output pin |
| PVT | TT/FF/SS/SF/FS, −40…125 °C, VDD ±10% | Absolute R and I shift ±20–30%; gain must not |
| Mismatch | Weight σ < 2–3% (Monte Carlo) | Large, long-channel mirror devices; common-centroid layout |
| Power | < 100 µW (≈ 50 µA at 1.98 V) | Low-µA biasing; buffer is the dominant consumer |
| Area | 180 × 115 µm incl. grid + guard rings | Resistors and compensation caps must stay compact |
| Schedule | Submit 2026-10-28 (18 days) | Favour fewest blocks and simplest layout |
| Output load | **Unknown** (pending Silicluster reply) | Buffer cannot be finalised yet |

## Decision

Build a **ratiometric, current-mode neuron with a ReLU activation**:

```
                 ┌──────────── Bias reference (beta-multiplier + start-up) ────────────┐
                 ▼                    ▼                      ▼                      ▼
 x ─► [V→I: OTA + R_in] ─I_x─► [mirror ×w] ─► Σ ◄─ I_b ─► [ReLU] ─► [I→V: R_out] ─► [buffer] ─► y
```

- I_x = (x − V_ref) / R_in, with the OTA holding the R_in node at a fixed V_ref ≈ 0.25–0.3 V
- I_sum = w·I_x + I_b (KCL at the summing node)
- I_out = max(0, I_sum) (diode-connected device conducts only positive current)
- y = R_out · I_out (R_out same resistor type as R_in), followed by an OTA buffer

Overall: **y = (R_out/R_in) · max(0, w·(x − V_ref) + I_b·R_in)**

Gain depends only on a resistor ratio and a transistor ratio, which track across PVT.

## Options Considered

### Option A: Ratiometric current-mode + ReLU (chosen)

| Dimension | Assessment |
|---|---|
| Complexity | Low–Med: 2 OTAs (V→I, buffer), mirrors, 1 reference |
| Area | Low: ReLU is one diode-connected device; resistors ≈ 100 □ each in xhigh_po (≈ 2 kΩ/□) |
| Power | ≈ 35–45 µA total estimate (≈ 65–80 µW), buffer-dominated |
| PVT robustness | High for gain (ratios); medium for bias term I_b·R_in |
| Linearity | High: active region is a straight line; V→I OTA input CM is fixed |
| Testability | MAC linearity directly measurable at y above the ReLU threshold |
| Schedule risk | Lowest of the three |

**Pros:** matches the current-mode design in CLAUDE.md; the V→I OTA sees a fixed common
mode, so no rail-to-rail input stage is needed at 1.62 V; gain is set by matched ratios;
fewest blocks to lay out.
**Cons:** resistive input (≈ 100–250 kΩ to V_ref); bias term I_b·R_in drifts with PVT;
mirror accuracy degrades near zero current (just above the ReLU knee).

### Option B: Voltage-mode (non-inverting amplifier + precision-rectifier ReLU)

| Dimension | Assessment |
|---|---|
| Complexity | Med: 2–3 op-amps, one inside a precision rectifier |
| Area | Med: more compensation capacitance |
| Power | Higher: each op-amp ≈ 10–20 µA |
| PVT robustness | High for gain (resistor ratio) |
| Linearity | Good in the amplifier; poor near the rectifier knee (offset, slewing) |
| Testability | Good |
| Schedule risk | Medium |

**Pros:** conceptually familiar; high input impedance comes naturally.
**Cons:** the amplifier input must follow x across 0.3–1.2 V, which needs a rail-to-rail input
pair at 1.62 V (hard, large, offset jumps at the crossover); more op-amps means more power
and area; departs from the current-mode architecture specified in CLAUDE.md.

### Option C: Current-mode + differential-pair sigmoid (tanh)

| Dimension | Assessment |
|---|---|
| Complexity | Med–High: extra I→V stage plus a diff pair before the output stage |
| Area | Med |
| Power | Med |
| PVT robustness | Low for activation shape: diff-pair slope scales with 1/T (weak inversion) or √(I·µCox) (strong inversion) |
| Linearity | MAC linearity **not observable**: the single output passes through a compressive tanh |
| Testability | Poor for the ≤ 5% MAC spec |
| Schedule risk | Highest |

**Pros:** smooth, bounded, biologically familiar activation.
**Cons:** activation shape moves strongly across corners; with only one output pin the MAC
linearity spec cannot be verified on silicon; more blocks to design and lay out.

### Sub-decision: V→I converter topology

| Option | Verdict |
|---|---|
| OTA + R_in, R_in node held at fixed V_ref | **Chosen**: OTA input CM fixed, highly linear, small |
| Source-degenerated transistor | Rejected: ≈ 10%+ nonlinearity over a 0.9 V span |
| Source-follower OTA (x on OTA input) | Rejected: needs rail-to-rail input at 1.62 V |
| High-Z input buffer + chosen V→I | Fallback, if Silicluster requires high input impedance (+1 OTA, ≈ +10 µA) |

## Trade-off Analysis

The deciding forces are the **1.62 V worst-case supply**, the **single output pin** and the
**18-day schedule**.

- At 1.62 V, any stage whose input must follow 0.3–1.2 V needs a rail-to-rail input pair.
  Option A avoids this by holding the OTA inputs at V_ref and letting x drive a resistor
  instead. Options B and the source-follower V→I do not.
- With one output pin, the only way to verify MAC linearity on silicon is an activation that
  is linear in its active region. ReLU satisfies this; tanh does not.
- Option A has the fewest analog blocks, which directly reduces layout time, the
  highest-risk phase of the schedule.

We accept two costs: a resistive input impedance (to be confirmed acceptable) and a bias term
that moves with PVT (to be measured; fixed by switching to an R-tracking reference if needed).

## Consequences

- **Easier:** gain accuracy across corners; MAC linearity measurement; layout (few blocks,
  mostly mirrors and two resistors); power budget.
- **Harder:** accuracy just above the ReLU knee, where mirrored currents are small; matching
  R_in to R_out needs interdigitated resistor layout; mirror Vds matching at 1.62 V.
- **To revisit:**
  - Output buffer topology, once Silicluster confirms the output load (fallback load chosen at Gate A, 2026-10-17)
  - Bias reference type, if the I_b·R_in spread across PVT is too large
  - Input buffer, if high input impedance is required
  - Concrete w and b values (fixed in silicon; owner to confirm)

## Action Items

**Phase 0: Environment (2026-10-11)**
1. [x] Build netgen (LVS) from source into `~/.local`; the `netgen` on PATH is the NETGEN 6.2 mesh generator
2. [x] Build ngspice ≥ 44 from source (apt version is ngspice-36) — ngspice-47 built
3. [x] Set `PDK_ROOT=$HOME/.ciel`, `PDK=sky130A` in `~/.zshrc` and `~/.bashrc`
4. [x] Smoke tests on an inverter: corner sim, Magic DRC, netgen LVS — see `docs/phase0-toolchain-and-smoke-test.md`

**Phase 1: Block design (10-11 → 10-15)**
5. [x] gm/Id characterisation of nfet_01v8 / pfet_01v8 (`spice/char/devchar_tb.cir`)
6. [ ] Bias reference + start-up → V→I → weight mirror → Σ/ReLU → I→V, each with its own testbench

**Phase 2: Full-neuron verification (10-15 → 10-17)**
7. [ ] 45-point PVT sweep: linearity, bias, power, OTA phase margin, start-up (fast/slow VDD ramp)
8. [ ] Monte Carlo ≥ 200 runs: weight σ, offset
9. [ ] Floorplan and area check against 180 × 115 µm
10. [ ] 🚦 **Gate A**: schematic sign-off; output-load fallback chosen if no reply

**Phase 3: Layout (10-17 → 10-23)**
11. [ ] Magic Tcl-scripted layout, bias block first end-to-end to calibrate pace
12. [ ] Common-centroid mirrors with dummies, interdigitated R_in/R_out, guard rings, M4/M5 grid

**Phase 4: Physical verification (10-23 → 10-25)**
13. [ ] DRC (Magic), LVS (netgen + sky130A_setup.tcl), PEX, post-layout corner sims
14. [ ] 🚦 **Gate B**: DRC/LVS clean with logs in `verif/`

**Phase 5: Package (10-25 → 10-28)**
15. [ ] GDS export, bounding-box and pin checks, `docs/` writeup, `submit/` package, submit 2026-10-28

## Findings from implementation (2026-10-11)

These were measured in simulation and change assumptions above.

1. **pfet_01v8 needs |Vgs| ≈ 1.0–1.35 V at 1 µA** (W = 2 µm, L = 0.5–8 µm, TT 27 °C) versus
   0.62–0.72 V for nfet_01v8, and more at −40 °C / SS. At VDD = 1.62 V a PMOS diode leaves
   only ≈ 0.3–0.4 V for anything stacked beneath it.
   *Consequence:* no PMOS cascodes; PMOS used only as wide, simple mirrors; precision
   (weight mirror, summing) on the NMOS side; never stack a PMOS diode on an NMOS diode.
2. **xhigh_po resistor:** 2 kΩ/□, TC1 = −1.47e-3/K (R falls ≈ 20 % from −40 to 125 °C).
   The PDK R/C corner files (`_ll`, `_hh`, …) **do not vary xhigh_po**, so its sheet-resistance
   spread is covered manually with ±20 % R in every bias testbench.
3. **Corner naming:** in this PDK's ngspice library `sf` behaves as fast NMOS / slow PMOS and
   `fs` as slow NMOS / fast PMOS. Results are interpreted by device behaviour.
4. **Bias reference** runs M1/M2 in weak–moderate inversion, where I ≈ n·UT·ln K / R: the
   current is PTAT/R (≈ 2.2× over −40…125 °C) instead of ≈ 3.5× in strong inversion.
   Result: 1.13–3.89 µA over 45 PVT points and R ±20 % (target 1–5 µA).
5. **Start-up false state:** at −40 °C / 1.62 V the PMOS gate line falls below the NMOS gate
   line, so a start-up device connected between them conducts backwards and holds the loop
   at ≈ 0.3 µA. The kick device now injects from VDD into the NMOS gate line.
6. **Bias term drift (open):** the reference makes I·R ∝ n·UT·ln K, i.e. PTAT (≈ 1.7× over
   temperature). Any neuron threshold built from I_ref·R inherits this. Options are listed as
   question 5 below.

## Open questions for the owner

1. Values of **w** and **b** (fixed in silicon, no control pins)
2. **ReLU** (recommended) vs sigmoid
3. Is a **≈ 100–250 kΩ input impedance** acceptable?
4. ~~Approval to build netgen and ngspice from source~~ — done, no sudo needed
5. **Threshold/bias accuracy over temperature:** keep thresholds tied to I_ref·R (PTAT, simplest),
   tie them to VDD with a resistor divider (temperature-flat, tracks the ±10 % supply), or add a
   CMOS temperature-compensated voltage reference (flattest, more area and design time)?
