#!/usr/bin/env python3
"""Run an ngspice testbench template at one or more PVT points.

The template may use these placeholders:
  @LIB@     path to sky130.lib.spice      @CORNER@  tt/ff/ss/sf/fs (or any .lib section,
                                                    e.g. ss_hh = slow MOS + high R/C)
  @TEMP@    temperature in degC           @VDD@     supply voltage
  @VDDH@    VDD/2                          @DIR@     absolute dir of the template
  @SEED@    random seed (Monte Carlo runs; put ".option seed=@SEED@" in the template)

The testbench reports values by printing lines of the form
  RESULT <name> <value>
from its .control block. Anything else in the ngspice output is kept in the log.

Usage:
  scripts/sim.py spice/smoke/inv_tb.cir                 # tt, 27 C, 1.8 V
  scripts/sim.py spice/smoke/inv_tb.cir --pvt           # 5 corners x 3 temps x 3 VDD
  scripts/sim.py tb.cir --corner ss --temp 125 --vdd 1.62
  scripts/sim.py tb.cir --pvt --corners tt,ss_hh,ff_ll  # custom corner list
  scripts/sim.py tb.cir --mc 200 --corner tt_mm --jobs 12  # mismatch Monte Carlo
"""
import argparse
import concurrent.futures
import statistics
import itertools
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORNERS = ["tt", "ff", "ss", "sf", "fs"]
TEMPS = [-40, 27, 125]
VDDS = [1.62, 1.8, 1.98]
RESULT_RE = re.compile(r"^RESULT\s+(\S+)\s+(\S+)")
ERROR_RE = re.compile(r"^\s*(Error|ERROR)\b|simulation\(s\) aborted|no such vector", re.M)


def render(template, corner, temp, vdd, seed=1, single_thread=False):
    pdk_root = os.environ.get("PDK_ROOT")
    pdk = os.environ.get("PDK", "sky130A")
    if not pdk_root:
        sys.exit("PDK_ROOT is not set (source ~/.bashrc or ~/.zshrc)")
    lib = f"{pdk_root}/{pdk}/libs.tech/ngspice/sky130.lib.spice"
    subs = {
        "@LIB@": lib,
        "@CORNER@": corner,
        "@TEMP@": str(temp),
        "@VDD@": str(vdd),
        "@VDDH@": str(vdd / 2),
        "@DIR@": str(template.parent.resolve()),
        "@SEED@": str(seed),
    }
    text = template.read_text()
    for key, val in subs.items():
        text = text.replace(key, val)
    if single_thread:   # parallel jobs: one OpenMP thread each (~/.spiceinit asks for 8)
        text = text.replace(".control", ".control\nset num_threads=1", 1)
    return text


def run_point(template, corner, temp, vdd, outdir, seed=None, single_thread=False):
    tag = f"{corner}_{temp}C_{vdd}V".replace("-", "m") + (f"_s{seed}" if seed is not None else "")
    netlist = outdir / f"{tag}.cir"
    log = outdir / f"{tag}.log"
    netlist.write_text(render(template, corner, temp, vdd, seed or 1, single_thread))
    proc = subprocess.run(
        ["ngspice", "-b", netlist.name],
        cwd=outdir, capture_output=True, text=True, timeout=1800,
    )
    out = proc.stdout + proc.stderr
    log.write_text(out)
    results = {}
    for line in out.splitlines():
        m = RESULT_RE.match(line.strip())
        if m:
            try:
                results[m.group(1)] = float(m.group(2))
            except ValueError:
                results[m.group(1)] = None   # measurement failed
    errors = ERROR_RE.findall(out)
    ok = proc.returncode == 0 and not errors and bool(results)
    if results.get("sane") == 0:   # testbench's own physical-range check failed
        ok = False
    return {"corner": corner, "temp": temp, "vdd": vdd, "seed": seed, "ok": ok,
            "returncode": proc.returncode, "log": str(log.relative_to(ROOT)),
            "results": results}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("testbench", type=pathlib.Path)
    ap.add_argument("--corner", default="tt")
    ap.add_argument("--temp", type=float, default=27.0)
    ap.add_argument("--vdd", type=float, default=1.8)
    ap.add_argument("--pvt", action="store_true", help="sweep all corners/temps/VDDs")
    ap.add_argument("--corners-only", action="store_true",
                    help="sweep the process corners at 27 C, 1.8 V")
    ap.add_argument("--corners", help="comma-separated corner list for --pvt / --corners-only "
                    "(default: tt,ff,ss,sf,fs)")
    ap.add_argument("--mc", type=int, metavar="N",
                    help="Monte Carlo: N runs at --corner/--temp/--vdd with seeds 1..N "
                         "(use a *_mm corner, e.g. tt_mm, so device mismatch is enabled)")
    ap.add_argument("--jobs", type=int, default=1, help="parallel ngspice processes")
    args = ap.parse_args()

    template = args.testbench.resolve()
    outdir = ROOT / "build" / "sim" / (template.stem + ("_mc" if args.mc else ""))
    outdir.mkdir(parents=True, exist_ok=True)

    corners = args.corners.split(",") if args.corners else CORNERS
    t = int(args.temp) if args.temp.is_integer() else args.temp
    if args.mc:
        points = [(args.corner, t, args.vdd, s) for s in range(1, args.mc + 1)]
    elif args.pvt:
        points = [(c, tt, v, None) for c, tt, v in itertools.product(corners, TEMPS, VDDS)]
    elif args.corners_only:
        points = [(c, 27, 1.8, None) for c in corners]
    else:
        points = [(args.corner, t, args.vdd, None)]

    single = args.jobs > 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        rows = list(pool.map(lambda p: run_point(template, *p[:3], outdir, p[3], single), points))
    (outdir / "results.json").write_text(json.dumps(rows, indent=2))

    names = sorted({k for r in rows for k in r["results"]})
    if args.mc:
        good = [r for r in rows if r["ok"]]
        print(f"Monte Carlo: {len(good)}/{len(rows)} clean runs at {args.corner}, {t} C, {args.vdd} V")
        print(f"{'result':>16} {'mean':>12} {'sigma':>12} {'sigma/mean':>11} {'min':>12} {'max':>12}")
        for n in names:
            v = [r["results"][n] for r in good if r["results"].get(n) is not None]
            if len(v) < 2:
                continue
            m, s = statistics.fmean(v), statistics.stdev(v)
            rel = f"{100 * s / abs(m):10.3f}%" if m else f"{'—':>11}"
            print(f"{n:>16} {m:12.4e} {s:12.4e} {rel} {min(v):12.4e} {max(v):12.4e}")
        print(f"\nlogs in {outdir.relative_to(ROOT)}/")
        sys.exit(0 if len(good) == len(rows) else 1)
    header = f"{'corner':6} {'temp':>5} {'vdd':>5}  " + "  ".join(f"{n:>12}" for n in names) + "  status"
    print(header)
    print("-" * len(header))
    for r in rows:
        vals = "  ".join(
            f"{r['results'].get(n):12.4e}" if r["results"].get(n) is not None else f"{'FAIL':>12}"
            for n in names)
        print(f"{r['corner']:6} {r['temp']:>5} {r['vdd']:>5}  {vals}  {'ok' if r['ok'] else 'ERROR -> ' + r['log']}")
    print(f"\n{sum(r['ok'] for r in rows)}/{len(rows)} runs completed cleanly; "
          f"logs in {outdir.relative_to(ROOT)}/")
    sys.exit(0 if all(r["ok"] for r in rows) else 1)


if __name__ == "__main__":
    main()
