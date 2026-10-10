# Silicluster v3 — Analog Neuron Project

## Submission constraints (fixed, do not violate)
- Process: SKY130 (sky130A), 1v8 devices only (nfet_01v8 / pfet_01v8)
- Supply: 1.8 V nominal
- I/O: 1 analog input, 1 analog output, plus VDD/VSS. No digital pins, no clock.
- Area: 180 µm × 115 µm max, including power grid and guard rings
- Power grid: M4 vertical, M5 horizontal
- Deadline: submit by Oct 28, 2026 (buffer before Oct 31 11:59pm Mexico City / slot limit)

## Design: single-input current-mode neuron
y = f(w·x + b)
Blocks: self-biased current reference (beta-multiplier + start-up) →
V-to-I converter (x) → current mirror (weight w) → summing node (+ bias b) →
activation stage (ReLU or diff-pair sigmoid-like) → output buffer (TBD pending
Silicluster's reply on output load).

## Target specs
- Input range: ~0.3–1.2 V
- Unit bias current: 1–5 µA
- Total power: < 100 µW
- MAC linearity: ≤ 5% error across input range
- Corners: TT/FF/SS/SF/FS, −40 to 125 °C, VDD ±10%
- Mismatch: Monte Carlo, weight accuracy σ < 2–3%

## Toolchain (native Ubuntu, no Docker/WSL)
- Magic (built from source — apt version too old for SKY130)
- netgen (built from source)
- ngspice (apt on 24.04+, else build from source)
- xschem (built from source)
- SKY130 PDK via `ciel` — env vars: PDK_ROOT=$HOME/.ciel, PDK=sky130A
- Model include: $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice (tt/ff/ss/sf/fs)
- LVS setup: $PDK_ROOT/sky130A/libs.tech/netgen/sky130A_setup.tcl
- Magic tech file: $PDK_ROOT/sky130A/libs.tech/magic/sky130A.magicrc

## Rules for Claude Code in this project
- Never report DRC or LVS as passing without pasting the actual log output.
- Run ngspice in batch mode (`ngspice -b <file>.cir`) and parse results from
  the output, not from assumed behavior.
- All schematics/netlists go in spice/, layout in mag/, DRC/LVS logs in
  verif/drc/ and verif/lvs/, final GDS in gds/, writeup in docs/.
- Before any layout work, confirm the schematic passes all corner sims.
- Flag immediately if area budget (180×115 µm) is at risk — don't discover
  this after layout is done.
- Do not finalize the output buffer until output-load spec is confirmed
  (pending email to silicluster@gmail.com).

## Project structure
```
silicluster/
  CLAUDE.md
  xschem/
  spice/
  mag/
  gds/
  verif/drc/
  verif/lvs/
  docs/
  submit/
```
