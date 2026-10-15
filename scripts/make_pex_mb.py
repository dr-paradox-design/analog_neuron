#!/usr/bin/env python3
"""Prepare the extracted neuron_core for Middlebrook double-injection loop analysis.

Each V->I loop is cut at its OTA output: the two OTA devices whose drain is GS (OTA_S M2, M4) are
moved to a new net GSA (likewise GK -> GKA in OTA_K). GSA/GS and GKA/GK become ports so the
testbench can insert a series voltage source (between GSA and GS) and a shunt current source (into
GS). Every feedback path - including the knee loop's second path through the shared divider
(VREF) - passes through the OTA, so this cut opens all of them.
"""
import pathlib
import re

SRC = pathlib.Path(__file__).resolve().parents[1] / "build" / "pex" / "neuron_core_pex.spice"
DST = SRC.with_name("neuron_core_pex_mb.spice")
t = SRC.read_text()
for g, ota in (("GS", "OTA_S"), ("GK", "OTA_K")):
    # pfet M2: <ota>/T INN <g> <ota>/T ; nfet M4: VSS <ota>/D1 <g> VSS
    pats = [re.compile(rf"^(X\d+ {ota}/T \S+ ){g}( {ota}/T sky130_fd_pr__pfet_01v8 .*)$", re.M),
            re.compile(rf"^(X\d+ VSS {ota}/D1 ){g}( VSS sky130_fd_pr__nfet_01v8 .*)$", re.M)]
    for pat in pats:
        n = len(pat.findall(t))
        if n != 1:
            raise SystemExit(f"{ota}: expected one output device for {pat.pattern}, found {n}")
        t = pat.sub(rf"\g<1>{g}A\g<2>", t)
t = t.replace(".subckt neuron_core X Y VDD VSS", ".subckt neuron_core X Y VDD VSS GSA GS GKA GK", 1)
DST.write_text(t)
print(f"wrote {DST}")
