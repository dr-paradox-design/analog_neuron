# CMOS inverter layout — Phase 0 smoke test.
# Run with: scripts/magic_batch.sh mag/smoke/inv_layout.tcl mag/smoke
# Coordinates are Magic internal units (snap internal): 1 unit = 0.005 um.
#
#   VDD rail ─────────────────────────────
#             PMOS W=2 L=0.15 (centre 0,Yp)   S → guard ring (right) → VDD
#   Y ──┐     D ◄──────────────┘ gate ▲
#       │                             │ A (metal1 strip between gates)
#   Y ──┘     D ◄──────────────┐ gate ▼
#             NMOS W=1 L=0.15 (centre 0,0)    S → guard ring (right) → VSS
#   VSS rail ─────────────────────────────

# gencell must create fresh instances, so start from an empty cell
foreach f [concat [glob -nocomplain inv.mag] [glob -nocomplain sky130_fd_pr__*.mag]] {
    file delete $f
}

snap internal
load inv -silent

proc rect {layer x1 y1 x2 y2} {
    box $x1 $y1 $x2 $y2
    paint $layer
}

proc pin {name x y index use} {
    box $x $y $x $y
    label $name c metal1
    port make $index
    port use $use
    port class bidirectional
}

set Yp 830

# Devices: gencell puts the cell's lower-left corner at the box, so offset
# by half the generated FIXED_BBOX to centre each device.
box -158 -257 -158 -257
magic::gencell sky130::sky130_fd_pr__nfet_01v8 xn w 1 l 0.15 nf 1 guard 1 viagr 100
box -158 [expr {$Yp - 366}] -158 [expr {$Yp - 366}]
magic::gencell sky130::sky130_fd_pr__pfet_01v8 xp w 2 l 0.15 nf 1 guard 1 viagr 100
select clear

# A: NMOS top gate contact to PMOS bottom gate contact
rect metal1 -29 132 29 [expr {$Yp - 241}]

# The outer gate contacts (NMOS bottom, PMOS top) are unused; their 0.29 x 0.23 um
# metal1 pads alone fail met1.6 (min area 0.083 um^2), so stretch them outward.
rect metal1 -29 -230 29 -132
rect metal1 -29 [expr {$Yp + 241}] 29 [expr {$Yp + 339}]

# Y: both drains (left strips) joined around the left side
rect metal1 -400 -23 -21 23
rect metal1 -400 -23 -354 [expr {$Yp + 23}]
rect metal1 -400 [expr {$Yp - 23}] -21 [expr {$Yp + 23}]

# VSS: NMOS source to its guard ring, guard ring down to the rail
rect metal1 21 -23 181 23
rect metal1 135 -400 181 -240
rect metal1 -450 -500 450 -400

# VDD: PMOS source to its guard ring, guard ring up to the rail
rect metal1 21 [expr {$Yp - 23}] 181 [expr {$Yp + 23}]
rect metal1 135 [expr {$Yp + 349}] 181 [expr {$Yp + 500}]
rect metal1 -450 [expr {$Yp + 500}] 450 [expr {$Yp + 600}]

pin A      0 360               1 signal
pin Y   -377 400               2 signal
pin VDD    0 [expr {$Yp + 550}] 3 power
pin VSS    0 -450              4 ground

select top cell
puts "BBOX_UM [box size]"
writeall force
gds write ../../build/smoke/inv.gds
quit -noprompt
