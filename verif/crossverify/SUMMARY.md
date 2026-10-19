# Cross-verification of the submitted GDS (2026-10-20)

Independent checks on `gds/analog_neuron.gds` (SHA-256 prefix 61d321cc11f4516e), in addition to the
Magic DRC / netgen LVS of the .mag cells in `verif/drc/` and `verif/lvs/`.

| Check | Tool / deck | Result | File |
|---|---|---|---|
| Manufacturing rules, FEOL + BEOL + off-grid | KLayout, PDK `sky130A_mr.drc` | 0 violations | `klayout_sky130A_mr.lyrdb` |
| Pin/label shapes over drawn metal | KLayout, PDK `pin_label_purposes_overlapping_drawing.rb.drc` | 0 | `klayout_pin_label.lyrdb` |
| Zero-area shapes | KLayout, PDK `zeroarea.rb.drc` | 0 | `klayout_zeroarea.lyrdb` |
| DRC of the GDS read back into Magic | Magic `drc(full)` after `gds read` | 0 violations | `magic_drc_from_gds.log` |
| LVS of the GDS (Magic extraction of the GDS vs reference) | netgen + `sky130A_setup.tcl` | match uniquely, 0 property errors | `lvs_from_gds_comp.out` |
| Antenna rules | Magic `antennacheck` | no violations | `magic_antenna.log` |
| GDS vs .mag correspondence | GDS regenerated from the .mag cells, layer-by-layer XOR | identical | — |
| Pins in the GDS | KLayout text objects | X, Y metal3 at (179.40, 81.27 / 82.07); VDD, VSS metal5 | — |
| Power grid orientation | KLayout geometry | metal5: 2 horizontal rails; metal4: 18 vertical straps (+ capacitor plates/tabs) | — |
| Bounding box | KLayout | (0, 0) – (180, 115) µm | — |

Finding fixed during this check: three metal3 port labels extended 0.1 µm past the end of their track
(pin shapes not over drawing). Labels are now placed inside the track; an XOR against the previous GDS
showed only the metal3 pin layer (70/16) changed - all fabricated layers are identical.
