v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {sky130_fd_pr/pfet3_01v8.sym} 100 300 0 0 {name=XM1 W=10 L=1 nf=1 mult=1 body=T model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 300 300 0 1 {name=XM2 W=10 L=1 nf=1 mult=1 body=T model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 180 190 0 0 {name=XMT W=16 L=2 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 140 420 0 1 {name=XM3 W=2 L=2 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 260 420 0 0 {name=XM4 W=2 L=2 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
N 120 270 120 240 {}
N 120 240 200 240 {}
N 280 270 280 240 {}
N 280 240 200 240 {}
N 200 220 200 240 {}
N 120 330 120 360 {}
N 120 360 120 390 {}
N 120 360 180 360 {}
N 180 360 180 420 {}
N 160 420 180 420 {}
N 180 420 240 420 {}
N 280 330 280 360 {}
N 280 360 280 390 {}
N 280 360 360 360 {}
N 120 450 120 480 {}
N 120 480 280 480 {}
N 280 450 280 480 {}
N 40 480 120 480 {}
N 200 160 200 130 {}
N 200 130 40 130 {}
N 40 300 80 300 {}
N 320 300 380 300 {}
N 100 190 160 190 {}
C {ipin.sym} 40 300 0 0 {name=l6 lab=INP}
C {ipin.sym} 380 300 0 1 {name=l7 lab=INN}
C {ipin.sym} 100 190 0 0 {name=l8 lab=VP}
C {opin.sym} 360 360 0 0 {name=l9 lab=OUT}
C {iopin.sym} 40 130 0 1 {name=l10 lab=VDD}
C {iopin.sym} 40 480 0 1 {name=l11 lab=VSS}
C {lab_wire.sym} 200 240 0 0 {name=l12 lab=T}
C {lab_wire.sym} 180 360 0 0 {name=l13 lab=D1}
