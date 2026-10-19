#!/usr/bin/env python3
"""Assemble submit/analog_neuron_silicluster_v3.zip (Silicluster v3 call, section 10).

The package mirrors the repository layout, so the commands in its README run unchanged inside the
unzipped folder. Run scripts/validation_report.py first if the results changed.
"""
import pathlib
import shutil
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAME = "analog_neuron_silicluster_v3"
STAGE = ROOT / "build" / "submission" / NAME
ZIP = ROOT / "submit" / f"{NAME}.zip"

FILES = {
    "analog_neuron.gds": "gds/analog_neuron.gds",
    "analog_neuron.v": "submit/analog_neuron.v",
    "analog_neuron_validation.pdf": "submit/analog_neuron_validation.pdf",
    "README.md": "submit/README.md",
    "spice/lvs/analog_neuron_ref.spice": "spice/lvs/analog_neuron_ref.spice",
    "build/pex/neuron_core_pex.spice": "build/pex/neuron_core_pex.spice",
    "build/pex/neuron_core_pex_mb.spice": "build/pex/neuron_core_pex_mb.spice",
}
for f in ("bias_ref.spice", "bias_tb.cir", "bias_startup_tb.cir", "bias_dcramp_tb.cir"):
    FILES[f"spice/bias/{f}"] = f"spice/bias/{f}"
for f in ("ota5p.spice", "vi_conv.spice", "neuron_core.spice", "neuron_tb.cir", "neuron_pex_tb.cir",
          "neuron_pex_mb_tb.cir"):
    FILES[f"spice/neuron/{f}"] = f"spice/neuron/{f}"
for f in ("sim.py", "magic_batch.sh", "drc.tcl", "extract_lvs.tcl", "lvs.sh"):
    FILES[f"scripts/{f}"] = f"scripts/{f}"
for cell in ("analog_neuron", "neuron_core", "bias_ref", "ota5p"):
    FILES[f"verification/drc/{cell}_drc.log"] = f"verif/drc/{cell}_drc.log"
    FILES[f"verification/lvs/{cell}.log"] = f"verif/lvs/{cell}.log"
    FILES[f"verification/lvs/{cell}_comp.out"] = f"verif/lvs/{cell}_comp.out"
for p in sorted((ROOT / "verif" / "crossverify").glob("*")):
    FILES[f"verification/crossverify/{p.name}"] = str(p.relative_to(ROOT))
for sub in ("gate-A", "post-layout"):
    for p in sorted((ROOT / "verif" / "sim" / sub).glob("*.txt")):
        FILES[f"verification/sim/{sub}/{p.name}"] = str(p.relative_to(ROOT))


def used_cells(top="analog_neuron"):
    d = ROOT / "mag" / "neuron"
    used, todo = set(), [top]
    while todo:
        c = todo.pop()
        if c not in used:
            used.add(c)
            todo += [l.split()[1] for l in (d / f"{c}.mag").read_text().splitlines() if l.startswith("use ")]
    return sorted(used)


def main():
    shutil.rmtree(STAGE, ignore_errors=True)
    for dst, src in FILES.items():
        out = STAGE / dst
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / src, out)
    cells = used_cells()
    for c in cells:
        (STAGE / "mag").mkdir(exist_ok=True)
        shutil.copy2(ROOT / "mag" / "neuron" / f"{c}.mag", STAGE / "mag" / f"{c}.mag")
    ZIP.unlink(missing_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(STAGE.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(STAGE.parent))
    print(f"wrote {ZIP} ({ZIP.stat().st_size / 1e6:.2f} MB): {len(FILES)} files + {len(cells)} .mag cells")


if __name__ == "__main__":
    main()
