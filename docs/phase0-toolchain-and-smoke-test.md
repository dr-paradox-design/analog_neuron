# Phase 0 — Toolchain and smoke test (2026-10-11)

## Toolchain

| Tool | Version | Source | Check |
|---|---|---|---|
| Magic | 8.3.683 | built from source (`/usr/local/bin`) | loads `sky130A.magicrc`, DRC styles fast/full/routing |
| netgen (LVS) | 1.5.324 | built from source → `~/.local` | `netgen -batch quit` |
| ngspice | 47 (KLU, OpenMP) | built from source → `~/.local` | `ngspice -v` |
| xschem | 3.4.8RC | built from source | `xschem --version` |
| ciel | 2.6.1 | pip | sees sky130 `1689ac3f2dc763876eaf967227c7dfe831b031ae` |

Environment (`~/.zshrc` and `~/.bashrc`): `PDK_ROOT=$HOME/.ciel`, `PDK=sky130A`.
`~/.spiceinit` is the PDK's `libs.tech/ngspice/spinit` (hsa compatibility, KLU, fast lib loading).

## Smoke test: CMOS inverter (PMOS W=2/L=0.15, NMOS W=1/L=0.15)

| Step | Result | Evidence |
|---|---|---|
| ngspice, 45 PVT points | 45/45 clean; VM 0.64–1.12 V | `scripts/sim.py spice/smoke/inv_tb.cir --pvt` |
| Magic layout | 4.50 × 9.65 µm | `mag/smoke/inv_layout.tcl` |
| Magic DRC, `drc(full)` | 0 violations | `verif/drc/smoke_inv_drc.log` |
| netgen LVS | Circuits match uniquely, no property errors | `verif/lvs/smoke_inv.log`, `verif/lvs/smoke_inv_comp.out` |

The schematic → simulation → layout → DRC → LVS loop works end to end.

## Things learned (apply to the real design)

- **Corner naming:** in this PDK's ngspice library, `sf` behaves as fast NMOS / slow PMOS and
  `fs` as slow NMOS / fast PMOS (inverter VM drops in `sf`, tpHL falls and tpLH rises).
  Read corner results by device behaviour, not by the conventional letter order.
- **Magic in batch mode** must run with stdin from `/dev/null` and a timeout
  (`scripts/magic_batch.sh`); otherwise a script error leaves Magic waiting for input.
- **`magic::gencell`** takes flat `key value` parameters, and must create instances in a fresh
  cell — if an instance of the same name already exists it takes a GUI-dialog code path and fails.
- **Generated transistor geometry** (internal units of 0.005 µm): drain metal1 strip on the left,
  source on the right, gate contacts top and bottom, guard ring on li (`viagr 100` adds metal1
  on the right side of the ring). Unused gate-contact pads fail met1.6 (min area 0.083 µm²)
  and must be extended or removed.
- The `m=xx on .subckt line` ngspice warning comes from the PDK model files and is harmless.
