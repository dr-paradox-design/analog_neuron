# Bias reference — beta-multiplier with start-up

Netlist: `spice/bias/bias_ref.spice` · Testbenches: `spice/bias/bias_tb.cir` (PVT operating point),
`spice/bias/bias_startup_tb.cir` (power-up transients)

## Circuit

```
  VDD ──┬────────────────┬─────────────────┐
       M3 (gate VP)     M4 (diode → VP)   MS1a+MS1b  weak pull-up, gate VSS (2 × 0.42/40)
        │ VN             │ VP               │ ST
       M1 (diode → VN)  M2 (K = 4)         MS2 (gate VN, 16/0.5) pulls ST low once running
        │                │ NS              MS3 (gate ST, 1/1): VDD → VN kick while ST is high
       VSS              R1 (xhigh_po 1.41 µm × 17 µm ≈ 24 kΩ) → VSS
```

| Device | Type | W / L (µm) | m | Role |
|---|---|---|---|---|
| M1 | nfet_01v8 | 20 / 2 | 1 | NMOS diode, sets VN |
| M2 | nfet_01v8 | 20 / 2 | 4 | K = 4 device with source resistor |
| M3, M4 | pfet_01v8 | 16 / 2 | 1 | PMOS mirror (M4 diode) |
| R1 | res_xhigh_po_1p41 | 1.41 / 17 | — | ≈ 24 kΩ at 27 °C |
| MS1a, MS1b | pfet_01v8 | 0.42 / 40 | 1 | always-on pull-up, ≲ 0.1 µA |
| MS2 | nfet_01v8 | 16 / 0.5 | 1 | releases start-up once VN is up |
| MS3 | nfet_01v8 | 1 / 1 | 1 | start-up kick into VN |

Outputs: **VP** (gate line for PMOS mirror copies) and **VN** (gate line for NMOS mirror copies).
A copy with the same W/L as M3 (PMOS) or M1 (NMOS) carries I_ref.

## Design choices

- **Diodes in separate branches.** pfet_01v8 needs |Vgs| ≈ 1.0–1.2 V, so an NMOS diode under a
  PMOS diode (≈ 2 V) would not fit at VDD = 1.62 V. M1 (NMOS diode) shares a branch with M3;
  M4 (PMOS diode) shares a branch with M2 + R1.
- **Weak–moderate inversion.** M1/M2 at W/L = 10, ≈ 2 µA: I ≈ n·UT·ln(K)/R, which varies
  ≈ 2.2× over −40…125 °C (UT rises, xhigh_po R falls) rather than ≈ 3.5× in strong inversion.
- **Start-up.** MS3 injects from VDD into VN. An earlier version kicked from VP into VN; at
  −40 °C / 1.62 V, VP falls below VN and that device conducted backwards, holding the loop in a
  false ≈ 0.3 µA state. MS2 is sized to sink ≫ the pull-up current at every corner so ST < 10 mV
  and MS3 is fully off in normal operation.
- **Resistor spread.** The PDK corners do not vary xhigh_po sheet resistance, so every
  testbench also runs R at −20 % and +20 %.

## Results — operating point, 45 PVT points (5 corners × −40/27/125 °C × 1.62/1.8/1.98 V)

| | −40 °C | 27 °C | 125 °C |
|---|---|---|---|
| I_ref, R nominal | 1.37–1.47 µA | 1.93–2.06 µA | 2.92–3.08 µA |
| I_ref incl. R ±20 % | 1.13–1.86 µA | 1.60–2.59 µA | 2.42–3.89 µA |

- Overall **1.13–3.89 µA** (target 1–5 µA).
- ST ≤ 7 mV and start-up kick current < 1 pA at every point (start-up fully off).
- Minimum M2 saturation margin (Vds − Vdsat): 339 mV.
- Supply sensitivity at TT 27 °C: 1.95 → 2.04 µA for 1.62 → 1.98 V (≈ 12 %/V).
- Supply current of the block: ≈ 2·I_ref + pull-up ≈ 4 µA (≈ 7 µW at 1.8 V).

## Results — power-up transients

See the start-up section below (filled in from `build/sim/bias_startup_tb/results.json`).
