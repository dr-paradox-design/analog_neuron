v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {bias_ref.sym} 140 150 0 0 {name=XBIAS}
C {lab_pin.sym} 140 80 0 0 {name=l2 lab=VDD}
C {lab_pin.sym} 140 220 0 0 {name=l3 lab=VSS}
C {lab_pin.sym} 220 130 0 1 {name=l4 lab=VP}
C {lab_pin.sym} 220 170 0 1 {name=l5 lab=VN}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 140 330 0 0 {name=XRA L=133.11 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 140 430 0 0 {name=XRB L=59.16 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 140 530 0 0 {name=XRC L=44.37 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {lab_pin.sym} 140 300 0 0 {name=l9 lab=VDD}
N 140 360 140 370 {}
N 140 370 140 400 {}
N 140 460 140 480 {}
N 140 480 140 500 {}
N 140 370 200 370 {}
N 140 480 200 480 {}
C {lab_pin.sym} 200 370 0 1 {name=l10 lab=VK}
C {lab_pin.sym} 200 480 0 1 {name=l11 lab=VREF}
C {lab_pin.sym} 140 560 0 0 {name=l12 lab=VSS}
C {lab_pin.sym} 120 330 0 0 {name=l13 lab=VSS}
C {lab_pin.sym} 120 430 0 0 {name=l14 lab=VSS}
C {lab_pin.sym} 120 530 0 0 {name=l15 lab=VSS}
C {vi_conv.sym} 400 170 0 0 {name=XVS}
N 280 150 320 150 {}
C {ipin.sym} 280 150 0 0 {name=l17 lab=X}
C {lab_pin.sym} 320 190 0 0 {name=l18 lab=VREF}
C {lab_pin.sym} 380 90 0 0 {name=l19 lab=VP}
C {lab_pin.sym} 420 90 0 1 {name=l20 lab=VDD}
C {lab_pin.sym} 400 250 0 0 {name=l21 lab=VSS}
N 480 170 500 170 {}
C {lab_pin.sym} 500 170 0 1 {name=l22 lab=GS}
C {vi_conv.sym} 400 430 0 0 {name=XVK}
C {lab_pin.sym} 320 410 0 0 {name=l24 lab=VK}
C {lab_pin.sym} 320 450 0 0 {name=l25 lab=VREF}
C {lab_pin.sym} 380 350 0 0 {name=l26 lab=VP}
C {lab_pin.sym} 420 350 0 1 {name=l27 lab=VDD}
C {lab_pin.sym} 400 510 0 0 {name=l28 lab=VSS}
N 480 430 500 430 {}
C {lab_pin.sym} 500 430 0 1 {name=l29 lab=GK}
N 560 60 620 60 {}
N 620 60 760 60 {}
N 760 60 960 60 {}
N 960 60 1100 60 {}
N 560 560 620 560 {}
N 620 560 760 560 {}
N 760 560 1100 560 {}
C {iopin.sym} 560 60 0 1 {name=l30 lab=VDD}
C {iopin.sym} 560 560 0 1 {name=l31 lab=VSS}
C {sky130_fd_pr/pfet3_01v8.sym} 640 130 0 1 {name=XPK1 W=32 L=4 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 740 130 0 0 {name=XPK2 W=32 L=4 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 600 480 0 0 {name=XWK W=16 L=4 nf=1 mult=2 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 740 480 0 0 {name=XWS W=16 L=4 nf=1 mult=2 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 980 130 0 1 {name=XPR1 W=32 L=8 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 1080 130 0 0 {name=XPR2 W=32 L=8 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 1100 400 0 0 {name=XRO L=103.53 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
N 620 100 620 60 {}
N 760 100 760 60 {}
N 960 100 960 60 {}
N 1100 100 1100 60 {}
N 620 510 620 560 {}
N 760 510 760 560 {}
N 1100 430 1100 560 {}
N 660 130 690 130 {}
N 690 130 720 130 {}
N 690 130 690 190 {}
N 690 190 620 190 {}
N 620 160 620 190 {}
N 620 190 620 450 {}
N 760 160 760 300 {}
N 760 300 760 450 {}
N 760 300 860 300 {}
N 860 300 960 300 {}
N 1000 130 1030 130 {}
N 1030 130 1060 130 {}
N 1030 130 1030 220 {}
N 1030 220 960 220 {}
N 960 160 960 220 {}
N 960 220 960 300 {}
N 1100 160 1100 300 {}
N 1100 300 1100 370 {}
N 1100 300 1160 300 {}
C {opin.sym} 1160 300 0 0 {name=l39 lab=Y}
C {lab_pin.sym} 1080 400 0 0 {name=l40 lab=VSS}
C {lab_pin.sym} 580 480 0 0 {name=l41 lab=GK}
C {lab_pin.sym} 720 480 0 0 {name=l42 lab=GS}
C {lab_wire.sym} 860 300 0 0 {name=l43 lab=S}
C {lab_wire.sym} 620 190 0 0 {name=l44 lab=DK}
T {divider 9:4:3} 170 262 0 0 0.25 0.25 {layer=8}
T {signal V->I} 250 215 0 0 0.25 0.25 {layer=8}
T {knee V->I} 262 475 0 0 0.25 0.25 {layer=8}
T {knee flip} 655 70 0 0 0.25 0.25 {layer=8}
T {x2 weight mirrors} 630 580 0 0 0.25 0.25 {layer=8}
T {ReLU} 1000 70 0 0 0.25 0.25 {layer=8}
T {R_out} 1120 440 0 0 0.25 0.25 {layer=8}
