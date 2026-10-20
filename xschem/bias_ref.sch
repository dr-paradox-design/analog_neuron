v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {sky130_fd_pr/pfet3_01v8.sym} 200 200 0 1 {name=XM3 W=16 L=2 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 340 200 0 0 {name=XM4 W=16 L=2 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 200 330 0 1 {name=XM1 W=20 L=2 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 340 330 0 0 {name=XM2 W=20 L=2 nf=1 mult=4 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_1p41.sym} 360 410 0 0 {name=XR1 L=17 model=res_xhigh_po_1p41 spiceprefix=X mult=1}
C {sky130_fd_pr/pfet3_01v8.sym} 500 200 0 0 {name=XMS1A W=0.42 L=40 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 500 290 0 0 {name=XMS1B W=0.42 L=40 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 500 380 0 0 {name=XMS2 W=16 L=0.5 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 100 200 0 0 {name=XMS3 W=1 L=1 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
N 40 140 120 140 {}
N 120 140 180 140 {}
N 180 140 360 140 {}
N 360 140 520 140 {}
N 40 470 180 470 {}
N 180 470 360 470 {}
N 360 470 520 470 {}
N 120 170 120 140 {}
N 180 170 180 140 {}
N 360 170 360 140 {}
N 520 170 520 140 {}
N 180 360 180 470 {}
N 360 440 360 470 {}
N 520 410 520 470 {}
N 220 200 290 200 {}
N 290 200 320 200 {}
N 360 230 360 260 {}
N 360 260 360 300 {}
N 360 260 290 260 {}
N 290 260 290 200 {}
N 360 260 420 260 {}
N 180 230 180 265 {}
N 180 265 180 300 {}
N 180 265 240 265 {}
N 240 265 240 330 {}
N 220 330 240 330 {}
N 240 330 320 330 {}
N 360 360 360 380 {}
N 120 230 120 265 {}
N 120 265 180 265 {}
N 120 265 60 265 {}
N 520 230 520 260 {}
N 520 320 520 335 {}
N 520 335 520 350 {}
N 520 335 570 335 {}
C {lab_pin.sym} 340 410 0 0 {name=l10 lab=VSS}
C {lab_pin.sym} 480 200 0 0 {name=l11 lab=VSS}
C {lab_pin.sym} 480 290 0 0 {name=l12 lab=VSS}
C {lab_pin.sym} 480 380 0 0 {name=l13 lab=VN}
C {lab_pin.sym} 80 200 0 0 {name=l14 lab=ST}
C {lab_pin.sym} 570 335 0 1 {name=l15 lab=ST}
C {opin.sym} 420 260 0 0 {name=l16 lab=VP}
C {opin.sym} 60 265 0 1 {name=l17 lab=VN}
C {iopin.sym} 40 140 0 1 {name=l18 lab=VDD}
C {iopin.sym} 40 470 0 1 {name=l19 lab=VSS}
T {start-up} 470 420 0 0 0.25 0.25 {layer=8}
