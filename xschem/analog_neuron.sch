v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {sky130_fd_pr/nfet3_01v8.sym} 120 60 0 0 {name=XMS3 W=1 L=1 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 340 60 0 1 {name=XMB3 W=16 L=2 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 480 60 0 0 {name=XMB4 W=16 L=2 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 340 190 0 1 {name=XMB1 W=20 L=2 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 480 190 0 0 {name=XMB2 W=20 L=2 nf=1 mult=4 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_1p41.sym} 500 270 0 0 {name=XR1 L=17 model=res_xhigh_po_1p41 spiceprefix=X mult=1}
C {sky130_fd_pr/pfet3_01v8.sym} 640 60 0 0 {name=XMS1A W=0.42 L=40 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 640 150 0 0 {name=XMS1B W=0.42 L=40 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 640 240 0 0 {name=XMS2 W=16 L=0.5 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
N 140 30 140 0 {}
N 320 30 320 0 {}
N 500 30 500 0 {}
N 660 30 660 0 {}
N 320 220 320 350 {}
N 500 300 500 350 {}
N 660 270 660 350 {}
N 360 60 430 60 {}
N 430 60 460 60 {}
N 500 90 500 120 {}
N 500 120 500 160 {}
N 500 120 430 120 {}
N 430 120 430 60 {}
N 500 120 560 120 {}
N 320 90 320 125 {}
N 320 125 320 160 {}
N 320 125 380 125 {}
N 380 125 380 190 {}
N 360 190 380 190 {}
N 380 190 460 190 {}
N 500 220 500 240 {}
N 140 90 140 125 {}
N 140 125 320 125 {}
N 140 125 60 125 {}
N 660 90 660 120 {}
N 660 180 660 195 {}
N 660 195 660 210 {}
N 660 195 710 195 {}
C {lab_pin.sym} 480 270 0 0 {name=l10 lab=VSS}
C {lab_pin.sym} 620 60 0 0 {name=l11 lab=VSS}
C {lab_pin.sym} 620 150 0 0 {name=l12 lab=VSS}
C {lab_pin.sym} 620 240 0 0 {name=l13 lab=VN}
C {lab_pin.sym} 100 60 0 0 {name=l14 lab=ST}
C {lab_pin.sym} 710 195 0 1 {name=l15 lab=ST}
C {lab_pin.sym} 560 120 0 1 {name=l16 lab=VP}
C {lab_pin.sym} 60 125 0 0 {name=l17 lab=VN}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 840 60 0 0 {name=XRA L=133.11 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 840 170 0 0 {name=XRB L=59.16 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 840 280 0 0 {name=XRC L=44.37 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
N 840 30 840 0 {}
N 840 310 840 350 {}
N 840 90 840 115 {}
N 840 115 840 140 {}
N 840 200 840 225 {}
N 840 225 840 250 {}
N 840 115 890 115 {}
N 840 225 890 225 {}
C {lab_pin.sym} 890 115 0 1 {name=l21 lab=VK}
C {lab_pin.sym} 890 225 0 1 {name=l22 lab=VREF}
C {lab_pin.sym} 820 60 0 0 {name=l23 lab=VSS}
C {lab_pin.sym} 820 170 0 0 {name=l24 lab=VSS}
C {lab_pin.sym} 820 280 0 0 {name=l25 lab=VSS}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 1060 170 3 0 {name=XR_S L=103.53 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {sky130_fd_pr/pfet3_01v8.sym} 1160 60 0 0 {name=XI0_S W=16 L=4 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 1160 290 0 0 {name=XMF_S W=16 L=4 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/cap_mim_m3_1.sym} 1320 200 2 1 {name=XCC_S model=cap_mim_m3_1 W=20 L=20 MF=1 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 1320 270 2 1 {name=XRZ_S L=25 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {sky130_fd_pr/pfet3_01v8.sym} 1580 60 0 0 {name=XMT_S W=16 L=2 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 1500 170 0 0 {name=XM1_S W=10 L=1 nf=1 mult=1 body=TS model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 1700 170 0 1 {name=XM2_S W=10 L=1 nf=1 mult=1 body=TS model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 1540 290 0 1 {name=XM3_S W=2 L=2 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 1660 290 0 0 {name=XM4_S W=2 L=2 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
N 1180 30 1180 0 {}
N 1600 30 1600 0 {}
N 1180 320 1180 350 {}
N 1520 320 1520 350 {}
N 1680 320 1680 350 {}
N 990 170 1030 170 {}
N 1090 170 1180 170 {}
N 1180 170 1320 170 {}
N 1320 170 1480 170 {}
N 1180 90 1180 170 {}
N 1180 170 1180 260 {}
N 1320 230 1320 240 {}
N 1320 300 1320 320 {}
N 1520 140 1520 110 {}
N 1520 110 1600 110 {}
N 1680 140 1680 110 {}
N 1680 110 1600 110 {}
N 1600 90 1600 110 {}
N 1520 200 1520 230 {}
N 1520 230 1520 260 {}
N 1520 230 1580 230 {}
N 1580 230 1580 290 {}
N 1560 290 1580 290 {}
N 1580 290 1640 290 {}
N 1680 200 1680 230 {}
N 1680 230 1680 260 {}
N 1680 230 1760 230 {}
N 1720 170 1760 170 {}
C {ipin.sym} 990 170 0 0 {name=l36 lab=X}
C {lab_pin.sym} 1060 190 0 0 {name=l37 lab=VSS}
C {lab_pin.sym} 1300 270 0 0 {name=l38 lab=VSS}
C {lab_pin.sym} 1140 60 0 0 {name=l39 lab=VP}
C {lab_pin.sym} 1560 60 0 0 {name=l40 lab=VP}
C {lab_pin.sym} 1140 290 0 0 {name=l41 lab=GS}
C {lab_pin.sym} 1320 320 0 0 {name=l42 lab=GS}
C {lab_pin.sym} 1760 230 0 1 {name=l43 lab=GS}
C {lab_pin.sym} 1760 170 0 1 {name=l44 lab=VREF}
C {lab_wire.sym} 1600 110 0 0 {name=l45 lab=TS}
C {lab_wire.sym} 1180 170 0 0 {name=l46 lab=XS}
T {signal V->I converter} 1020 -60 0 0 0.3 0.3 {layer=8}
T {OTA} 1580 -60 0 0 0.3 0.3 {layer=8}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 120 690 3 0 {name=XR_K L=103.53 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {sky130_fd_pr/pfet3_01v8.sym} 220 580 0 0 {name=XI0_K W=16 L=4 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 220 810 0 0 {name=XMF_K W=16 L=4 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/cap_mim_m3_1.sym} 380 720 2 1 {name=XCC_K model=cap_mim_m3_1 W=20 L=20 MF=1 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 380 790 2 1 {name=XRZ_K L=25 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
C {sky130_fd_pr/pfet3_01v8.sym} 640 580 0 0 {name=XMT_K W=16 L=2 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 560 690 0 0 {name=XM1_K W=10 L=1 nf=1 mult=1 body=TK model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 760 690 0 1 {name=XM2_K W=10 L=1 nf=1 mult=1 body=TK model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 600 810 0 1 {name=XM3_K W=2 L=2 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 720 810 0 0 {name=XM4_K W=2 L=2 nf=1 mult=1 body=VSS model=nfet_01v8 spiceprefix=X}
N 240 550 240 520 {}
N 660 550 660 520 {}
N 240 840 240 870 {}
N 580 840 580 870 {}
N 740 840 740 870 {}
N 50 690 90 690 {}
N 150 690 240 690 {}
N 240 690 380 690 {}
N 380 690 540 690 {}
N 240 610 240 690 {}
N 240 690 240 780 {}
N 380 750 380 760 {}
N 380 820 380 840 {}
N 580 660 580 630 {}
N 580 630 660 630 {}
N 740 660 740 630 {}
N 740 630 660 630 {}
N 660 610 660 630 {}
N 580 720 580 750 {}
N 580 750 580 780 {}
N 580 750 640 750 {}
N 640 750 640 810 {}
N 620 810 640 810 {}
N 640 810 700 810 {}
N 740 720 740 750 {}
N 740 750 740 780 {}
N 740 750 820 750 {}
N 780 690 820 690 {}
C {lab_pin.sym} 50 690 0 0 {name=l57 lab=VK}
C {lab_pin.sym} 120 710 0 0 {name=l58 lab=VSS}
C {lab_pin.sym} 360 790 0 0 {name=l59 lab=VSS}
C {lab_pin.sym} 200 580 0 0 {name=l60 lab=VP}
C {lab_pin.sym} 620 580 0 0 {name=l61 lab=VP}
C {lab_pin.sym} 200 810 0 0 {name=l62 lab=GK}
C {lab_pin.sym} 380 840 0 0 {name=l63 lab=GK}
C {lab_pin.sym} 820 750 0 1 {name=l64 lab=GK}
C {lab_pin.sym} 820 690 0 1 {name=l65 lab=VREF}
C {lab_wire.sym} 660 630 0 0 {name=l66 lab=TK}
C {lab_wire.sym} 240 690 0 0 {name=l67 lab=XK}
T {knee V->I converter} 80 460 0 0 0.3 0.3 {layer=8}
T {OTA} 640 460 0 0 0.3 0.3 {layer=8}
C {sky130_fd_pr/pfet3_01v8.sym} 980 580 0 1 {name=XPK1 W=32 L=4 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 1120 580 0 0 {name=XPK2 W=32 L=4 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 940 810 0 0 {name=XWK W=16 L=4 nf=1 mult=2 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/nfet3_01v8.sym} 1120 810 0 0 {name=XWS W=16 L=4 nf=1 mult=2 body=VSS model=nfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 1360 580 0 1 {name=XPR1 W=32 L=8 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/pfet3_01v8.sym} 1480 580 0 0 {name=XPR2 W=32 L=8 nf=1 mult=1 body=VDD model=pfet_01v8 spiceprefix=X}
C {sky130_fd_pr/res_xhigh_po_0p69.sym} 1500 760 0 0 {name=XRO L=103.53 model=res_xhigh_po_0p69 spiceprefix=X mult=1}
N 960 550 960 520 {}
N 1140 550 1140 520 {}
N 1340 550 1340 520 {}
N 1500 550 1500 520 {}
N 960 840 960 870 {}
N 1140 840 1140 870 {}
N 1500 790 1500 870 {}
N 1000 580 1050 580 {}
N 1050 580 1100 580 {}
N 1050 580 1050 640 {}
N 1050 640 960 640 {}
N 960 610 960 640 {}
N 960 640 960 780 {}
N 1140 610 1140 700 {}
N 1140 700 1140 780 {}
N 1140 700 1240 700 {}
N 1240 700 1340 700 {}
N 1380 580 1420 580 {}
N 1420 580 1460 580 {}
N 1420 580 1420 640 {}
N 1420 640 1340 640 {}
N 1340 610 1340 640 {}
N 1340 640 1340 700 {}
N 1500 610 1500 700 {}
N 1500 700 1500 730 {}
N 1500 700 1560 700 {}
C {opin.sym} 1560 700 0 0 {name=l75 lab=Y}
C {lab_pin.sym} 1480 760 0 0 {name=l76 lab=VSS}
C {lab_pin.sym} 920 810 0 0 {name=l77 lab=GK}
C {lab_pin.sym} 1100 810 0 0 {name=l78 lab=GS}
C {lab_wire.sym} 1240 700 0 0 {name=l79 lab=S}
C {lab_wire.sym} 960 640 0 0 {name=l80 lab=DK}
N 20 0 140 0 {}
N 140 0 320 0 {}
N 320 0 500 0 {}
N 500 0 660 0 {}
N 660 0 840 0 {}
N 840 0 1180 0 {}
N 1180 0 1600 0 {}
C {iopin.sym} 20 0 0 1 {name=l81 lab=VDD}
N 20 350 320 350 {}
N 320 350 500 350 {}
N 500 350 660 350 {}
N 660 350 840 350 {}
N 840 350 1180 350 {}
N 1180 350 1520 350 {}
N 1520 350 1680 350 {}
C {iopin.sym} 20 350 0 1 {name=l82 lab=VSS}
N 20 520 240 520 {}
N 240 520 660 520 {}
N 660 520 960 520 {}
N 960 520 1140 520 {}
N 1140 520 1340 520 {}
N 1340 520 1500 520 {}
C {lab_pin.sym} 20 520 0 0 {name=l83 lab=VDD}
N 20 870 240 870 {}
N 240 870 580 870 {}
N 580 870 740 870 {}
N 740 870 960 870 {}
N 960 870 1140 870 {}
N 1140 870 1500 870 {}
C {lab_pin.sym} 20 870 0 0 {name=l84 lab=VSS}
T {bias reference (beta multiplier)} 120 -60 0 0 0.3 0.3 {layer=8}
T {start-up} 600 -60 0 0 0.3 0.3 {layer=8}
T {divider 9:4:3} 790 -60 0 0 0.3 0.3 {layer=8}
T {knee flip} 970 460 0 0 0.3 0.3 {layer=8}
T {ReLU + output copy} 1320 460 0 0 0.3 0.3 {layer=8}
T {x2 weight mirrors} 940 890 0 0 0.3 0.3 {layer=8}
T {R_out} 1520 800 0 0 0.3 0.3 {layer=8}
