#!/usr/bin/env bash
# Run a Magic Tcl script headless with the SKY130 tech file.
# Magic never waits for input (stdin is /dev/null) and is killed after
# MAGIC_TIMEOUT seconds, so a script error can't leave it hanging.
#   usage: scripts/magic_batch.sh <script.tcl> <workdir>
set -euo pipefail
script=$(realpath "$1")
workdir=$2
: "${PDK_ROOT:?PDK_ROOT is not set}"
PDK=${PDK:-sky130A}
cd "$workdir"
exec timeout -k 5 "${MAGIC_TIMEOUT:-300}" magic -dnull -noconsole \
    -rcfile "$PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc" "$script" </dev/null
