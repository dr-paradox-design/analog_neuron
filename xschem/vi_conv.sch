v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {sky130_fd_pr/pfet3_01v8.sym} 400 120 0 0 {name=XI0 W=16 L=4 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 400 330 0 0 {name=XMF W=16 L=4 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 130 200 3 0 {name=XR L=103.53 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {sky130_fd_pr/cap_mim_m3_1.sym} 250 230 2 1 {name=XCC model=cap_mim_m3_1 W=20 L=20 MF=1 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 250 300 2 1 {name=XRZ L=25 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {ota5p.sym} 150 330 0 0 {name=XA}
N 40 60 420 60 {}
N 420 90 420 60 {}
N 40 200 100 200 {}
N 160 200 180 200 {}
N 180 200 250 200 {}
N 250 200 420 200 {}
N 420 150 420 200 {}
N 420 200 420 300 {}
N 250 260 250 270 {}
N 210 330 250 330 {}
N 250 330 380 330 {}
N 250 330 250 380 {}
N 180 200 180 240 {}
N 180 240 70 240 {}
N 70 240 70 310 {}
N 70 310 90 310 {}
N 40 350 90 350 {}
N 230 120 380 120 {}
N 420 360 420 420 {}
N 420 420 160 420 {}
N 160 420 40 420 {}
N 160 390 160 420 {}
C {lab_pin.sym} 150 270 0 0 {name=l7 lab=VDD}
C {lab_pin.sym} 130 390 0 0 {name=l8 lab=VP}
C {lab_pin.sym} 130 220 0 0 {name=l9 lab=VSS}
C {lab_pin.sym} 230 300 0 0 {name=l10 lab=VSS}
C {ipin.sym} 40 200 0 0 {name=l11 lab=IN}
C {ipin.sym} 40 350 0 0 {name=l12 lab=VREF}
C {ipin.sym} 230 120 0 0 {name=l13 lab=VP}
C {opin.sym} 250 380 0 0 {name=l14 lab=G}
C {iopin.sym} 40 60 0 1 {name=l15 lab=VDD}
C {iopin.sym} 40 420 0 1 {name=l16 lab=VSS}
C {lab_wire.sym} 420 200 0 0 {name=l17 lab=X}
