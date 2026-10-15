# Write cell $env(CELL) (and its hierarchy) to GDS at $env(OUT).
load $env(CELL) -silent
select top cell
gds write $env(OUT)
quit -noprompt
