# Full-rule DRC on cell $env(CELL), loaded from the working directory.
# Prints DRC_COUNT <n> and one line per violation type.
load $env(CELL) -silent
select top cell
expand
drc style drc(full)
drc check
drc catchup
set total 0
foreach {why boxes} [drc listall why] {
    set n [llength $boxes]
    incr total $n
    puts "DRC_VIOLATION ($n) $why"
    foreach b $boxes {
        puts "    at (um) [lmap v $b {format %.3f [expr {$v * [cif scale out]}]}]"
    }
}
puts "DRC_COUNT $total"
quit -noprompt
