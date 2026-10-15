# Parasitic (C) extraction of cell $env(CELL) to a flat simulation netlist at $env(OUT).
# Capacitance to substrate and coupling between nets are included (cthresh 0); wire
# resistance is not (microamp currents: IR drops are negligible here).
load $env(CELL) -silent
select top cell
extract do local
extract do capacitance
extract do coupling
extract all
ext2spice hierarchy off
ext2spice format ngspice
ext2spice cthresh 0
ext2spice scale off
ext2spice subcircuit top on
ext2spice -o $env(OUT)
quit -noprompt
