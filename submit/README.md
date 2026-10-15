# Silicluster v3 submission — analog_neuron (SKY130A)

Single-input current-mode analog neuron with ReLU activation:

**y = 2 · max(0, x − V_k)**,  V_k = 0.326 · VDD (0.586 V at 1.8 V)

| Item | Value |
|---|---|
| Process / devices | SKY130A, `nfet_01v8`, `pfet_01v8`, `res_xhigh_po`, `cap_mim_m3_1` |
| Supply | 1.8 V nominal (verified 1.62 – 1.98 V) |
| Top cell / size | `analog_neuron`, 180.000 × 115.000 µm |
| Input x | 0.3 – 1.2 V, ≈ 300 kΩ resistive input |
| Output y | 0 – ≈ 1.2 V, ≈ 300 kΩ source, **unbuffered**: measure with ≥ 10 MΩ (≈ 2.8 % gain loss) |
| Power | 38 – 78 µW over corners (52 µW typical) |

## Pins

| Pin | Layer | Location (µm, origin lower-left) |
|---|---|---|
| X | metal3 | x = 179.4, y = 81.27 (right edge) |
| Y | metal3 | x = 179.4, y = 82.07 (right edge) |
| VDD | metal5 | rail y = 111.5 – 114.5, full width |
| VSS | metal5 | rail y = 0.5 – 3.5, full width |

Power grid: metal5 horizontal rails, metal4 vertical straps.

## Files

- `analog_neuron.gds` — layout (top cell `analog_neuron`)
- `analog_neuron.spice` — LVS reference netlist (numeric, hierarchical)

## Verification summary

- DRC (Magic, `drc(full)`): 0 violations on every cell and the top cell.
- LVS (netgen, `sky130A_setup.tcl`): circuits match uniquely, no property errors.
- Post-layout simulation over 5 corners × −40/27/125 °C × 1.62/1.8/1.98 V: slope 1.90 – 2.00,
  MAC linearity error ≤ 0.70 % (spec 5 %), loop phase margin ≥ 62.5°.
- Mismatch (200-run Monte Carlo): weight σ 1.47 % (spec 2 – 3 %).

Details: `docs/gate-A.md` (schematic), `docs/gate-B.md` (layout), `docs/neuron-core.md`.
