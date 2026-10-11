# Extract cell $env(CELL) to an LVS netlist at $env(OUT).
load $env(CELL) -silent
select top cell
extract do local
extract all
ext2spice lvs
ext2spice -o $env(OUT)
quit -noprompt
