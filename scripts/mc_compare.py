#!/usr/bin/env python3
"""Compare Monte Carlo result sets produced by scripts/sim.py --mc.

Usage:
  scripts/mc_compare.py build/sim/mc_A_base_mc build/sim/mc_B_weight_mc ...

For each directory, reads results.json and prints, over the clean runs:
slope mean/sigma, knee mean/sigma, INL worst case, peak power, and the
number of runs that needed the numerical retry (method 2).
"""
import json
import pathlib
import statistics as st
import sys


def summary(d):
    rows = json.loads((pathlib.Path(d) / "results.json").read_text())
    good = [r["results"] for r in rows if r["ok"]]

    def col(k):
        return [x[k] for x in good if x.get(k) is not None]

    slope, knee = col("slope"), col("knee")
    inl = col("inl_max_pct") + [-v for v in col("inl_min_pct")]
    return {
        "name": pathlib.Path(d).name.removesuffix("_mc"),
        "clean": f"{len(good)}/{len(rows)}",
        "retried": sum(1 for x in good if x.get("method") == 2),
        "slope_mean": st.fmean(slope), "slope_sig_pct": 100 * st.stdev(slope) / st.fmean(slope),
        "slope_min": min(slope), "slope_max": max(slope),
        "knee_mean": st.fmean(knee), "knee_sig_mv": 1e3 * st.stdev(knee),
        "knee_min": min(knee), "knee_max": max(knee),
        "inl_worst": max(inl), "pwr_max_uw": 1e6 * max(col("pwr_max")),
    }


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rows = [summary(d) for d in sys.argv[1:]]
    print(f"{'variant':12} {'clean':>7} {'retry':>5} | {'slope mean':>10} {'sigma':>7} {'min':>6} {'max':>6} | "
          f"{'knee mean':>9} {'sigma':>8} {'min':>6} {'max':>6} | {'INL worst':>9} {'P max':>8}")
    for r in rows:
        print(f"{r['name']:12} {r['clean']:>7} {r['retried']:>5} | {r['slope_mean']:10.4f} {r['slope_sig_pct']:6.2f}% "
              f"{r['slope_min']:6.3f} {r['slope_max']:6.3f} | {r['knee_mean']:8.4f}V {r['knee_sig_mv']:6.1f}mV "
              f"{r['knee_min']:6.3f} {r['knee_max']:6.3f} | {r['inl_worst']:8.3f}% {r['pwr_max_uw']:6.1f}uW")


if __name__ == "__main__":
    main()
