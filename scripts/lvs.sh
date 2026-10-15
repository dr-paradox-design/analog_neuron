#!/usr/bin/env bash
# Extract a Magic cell and compare it against a reference SPICE subcircuit.
#   usage: scripts/lvs.sh <cell> <magdir> <reference.spice> <logname>
# Writes verif/lvs/<logname>.log (netgen stdout) and verif/lvs/<logname>_comp.out
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cell=$1; magdir=$(realpath "$2"); ref=$(realpath "$3"); name=$4
mkdir -p "$root/build/lvs" "$root/verif/lvs"
ext="$root/build/lvs/${cell}_extracted.spice"
CELL=$cell OUT=$ext "$root/scripts/magic_batch.sh" "$root/scripts/extract_lvs.tcl" "$magdir" \
    > "$root/build/lvs/${cell}_extract.log" 2>&1
netgen -batch lvs "$ext $cell" "$ref $cell" \
    "$PDK_ROOT/${PDK:-sky130A}/libs.tech/netgen/${PDK:-sky130A}_setup.tcl" \
    "$root/verif/lvs/${name}_comp.out" > "$root/verif/lvs/${name}.log" 2>&1
# Verdict: netgen's "Final result" line says "match uniquely" even when device sizes differ,
# so require both a unique match and no property errors.
comp="$root/verif/lvs/${name}_comp.out"
if grep -q "Circuits match uniquely" "$comp" && ! grep -q "Property errors were found" "$comp"; then
    verdict="LVS_VERDICT PASS (topology and device properties match)"
else
    verdict="LVS_VERDICT FAIL (see $comp)"
fi
echo "$verdict" | tee -a "$root/verif/lvs/${name}.log"
