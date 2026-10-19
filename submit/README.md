# analog_neuron — Silicluster v3 analog project

Single-input analog ReLU neuron, SKY130A, 1.8 V:

**Y = 2 · max(0, X − V<sub>k</sub>)**, V<sub>k</sub> = 0.326 · VDD (0.586 V at 1.8 V)

| | |
|---|---|
| Top cell | `analog_neuron`, 180.000 µm × 115.000 µm |
| Analog I/O | 1 input (`X`), 1 output (`Y`); the call allows up to 2 + 2 |
| Supply | 1.8 V (verified 1.62 – 1.98 V) |
| Power grid | metal4 vertical straps, metal5 horizontal rails |

## Files (call §10)

| Required item | File(s) |
|---|---|
| GDS of the final layout | `analog_neuron.gds` |
| Magic .mag files | `mag/` — top cell `analog_neuron.mag` and the 17 cells it uses |
| Verilog file with the external interface | `analog_neuron.v` |
| Testbench and files to reproduce the simulation | `spice/`, `scripts/sim.py`, `build/pex/` (extracted netlists for the post-layout testbenches) |
| Simulation and validation document | `analog_neuron_validation.pdf` |
| DRC evidence | `verification/drc/` — `analog_neuron_drc.log`: `No errors found`, `DRC_COUNT 0` |
| LVS evidence | `verification/lvs/` — `analog_neuron.log`: `Circuits match uniquely`, `LVS_VERDICT PASS` |

Also included: `spice/lvs/analog_neuron_ref.spice` (LVS reference netlist) and `verification/sim/` (result
tables of the schematic and post-layout runs summarised in the PDF).

## Pins (origin at the lower-left corner of the cell)

| Pin | Type | Layer / location | Electrical |
|---|---|---|---|
| `X` | analog input | metal3, right edge, x = 179.4 µm, y = 81.27 µm | 0.3 – 1.2 V; ≈ 300 kΩ to an internal ≈ 0.26 V node |
| `Y` | analog output | metal3, right edge, x = 179.4 µm, y = 82.07 µm | 0 – ≈ 1.2 V; **unbuffered, ≈ 300 kΩ source** |
| `VDD` | supply | metal5 rail, y = 111.5 – 114.5 µm | 1.8 V |
| `VSS` | ground | metal5 rail, y = 0.5 – 3.5 µm | 0 V |

`Y` should be read by a high-impedance input: a 10 MΩ load lowers the gain by ≈ 2.8 %, a 1 MΩ load by ≈ 22 %
(linearity is unaffected).

## Verification summary

| | Result | Target |
|---|---|---|
| DRC (Magic, sky130A `drc(full)`) | 0 violations | clean |
| LVS (netgen, `sky130A_setup.tcl`) | unique match, no property errors | match |
| MAC linearity, post-layout, 45 PVT points | INL ≤ 0.70 % | ≤ 5 % |
| Weight mismatch (200-run Monte Carlo) | σ = 1.47 % | < 2–3 % |
| Loop phase margin, post-layout, 45 PVT | ≥ 62.5° | ≥ 60° |
| Peak power, 45 PVT | 38 – 78 µW | — |

PVT = tt/ff/ss/sf/fs × −40 / 27 / 125 °C × 1.62 / 1.8 / 1.98 V. Details and figures: `analog_neuron_validation.pdf`.

## Reproduce

Requires ngspice (≥ 44), Magic, netgen and the SKY130A PDK.

```bash
export PDK_ROOT=$HOME/.ciel PDK=sky130A        # adjust to your PDK installation
python3 scripts/sim.py spice/neuron/neuron_tb.cir --pvt --jobs 8        # schematic, 45 PVT
python3 scripts/sim.py spice/neuron/neuron_pex_tb.cir --pvt --jobs 8    # post-layout transfer
python3 scripts/sim.py spice/neuron/neuron_pex_mb_tb.cir --pvt --jobs 8 # post-layout stability
python3 scripts/sim.py spice/neuron/neuron_tb.cir --mc 200 --corner tt_mm --jobs 8
CELL=analog_neuron scripts/magic_batch.sh scripts/drc.tcl mag | grep DRC_COUNT
scripts/lvs.sh analog_neuron mag spice/lvs/analog_neuron_ref.spice analog_neuron
```

Results are written to `build/sim/<testbench>/` (one log and netlist per PVT point plus `results.json`).
