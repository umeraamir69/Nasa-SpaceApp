#!/usr/bin/env python3
"""Cross-check SME2 soil moisture against our GCOV scene medians (conda env).

Reads NISAR L3 SME2 granules (EASE-Grid 2.0, 200 m) over a case box and
reports per-algorithm soil-moisture medians. Compares the before→after SM
delta with our committed GCOV scene-median dB shift. Beta caveat: the three
candidate algorithms (DSG/PMI/TSR) can disagree on absolutes, so deltas are
the robust quantity.

Example:
  xcheck_sme2.py --case isaias --before data/isaias/sme2/*0930*.h5 \\
      --after data/isaias/sme2/*1012*.h5 --mid data/isaias/sme2/*1009*.h5
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import h5py
import numpy as np
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
ALGOS = ("DSG", "PMI", "TSR")


def window_stats(path: str, lon_min, lat_min, lon_max, lat_max) -> dict:
    f = h5py.File(path, "r")
    grids = f["science/LSAR/SME2/grids"]
    have = [a for a in ALGOS if a in grids["algorithmCandidates"]]
    if not have:
        f.close()
        return {"error": "no algorithm candidates"}
    ref = grids[f"algorithmCandidates/{have[0]}"]
    xs = ref["xCoordinates"][:]
    ys = ref["yCoordinates"][:]
    tr = Transformer.from_crs("EPSG:4326", "EPSG:6933", always_xy=True)
    x0, y0 = tr.transform(lon_min, lat_min)
    x1, y1 = tr.transform(lon_max, lat_max)
    # xs ascending, ys descending
    c0, c1 = np.searchsorted(xs, [min(x0, x1), max(x0, x1)])
    y_lo, y_hi = min(y0, y1), max(y0, y1)
    r0 = int(np.searchsorted(-ys, -y_hi))
    r1 = int(np.searchsorted(-ys, -y_lo, side="right"))
    r0, r1 = max(r0, 0), min(r1, len(ys))
    c0, c1 = max(c0, 0), min(c1, len(xs))
    wbf = grids["ancillaryData/waterbodyFraction"][r0:r1, c0:c1]
    land = (wbf < 0.25) & np.isfinite(wbf)
    out = {"rows": [int(r0), int(r1)], "cols": [int(c0), int(c1)],
           "land_frac": round(float(np.mean(land)), 3),
           "algorithms": have}
    halves = {"west": (0, (c1 - c0) // 2), "east": ((c1 - c0) // 2, c1 - c0)}
    for algo in have:
        g = grids[f"algorithmCandidates/{algo}"]
        sm = g["soilMoisture"][r0:r1, c0:c1].astype(np.float64)
        q = g["retrievalQualityFlag"][r0:r1, c0:c1]
        ok = land & np.isfinite(sm) & (sm >= 0) & (sm <= 0.6)
        med = float(np.median(sm[ok])) if ok.sum() else None
        entry = {
            "median_m3m3": round(med, 4) if med is not None else None,
            "n_px": int(ok.sum()),
            "flag0_frac": round(float(np.mean((q == 0)[land])), 4) if land.sum() else 0.0,
        }
        for hname, (ha, hb) in halves.items():
            hok = ok[:, ha:hb]
            hm = float(np.median(sm[:, ha:hb][hok])) if hok.sum() else None
            entry[f"{hname}_median"] = round(hm, 4) if hm is not None else None
            entry[f"{hname}_n"] = int(hok.sum())
        out[algo] = entry
    f.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="SME2 vs GCOV cross-check.")
    ap.add_argument("--case", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--mid", default=None)
    ap.add_argument("--patch-summary", action="store_true")
    args = ap.parse_args()

    bounds = json.load(open(ROOT / f"outputs/{args.case}/layers/bounds.json"))
    box = (bounds["west"], bounds["south"], bounds["east"], bounds["north"])
    summ = json.load(open(ROOT / f"outputs/{args.case}/summary.json"))

    def one(pat):
        files = sorted(glob.glob(pat))
        if not files:
            raise SystemExit(f"no file matches {pat}")
        return files[0]

    res = {
        "product": "NISAR_L3_SME2_PROVISIONAL_V1 (beta)",
        "box": [round(v, 3) for v in box],
        "before": {"file": Path(one(args.before)).name,
                   **window_stats(one(args.before), *box)},
        "after": {"file": Path(one(args.after)).name,
                  **window_stats(one(args.after), *box)},
    }
    if args.mid:
        res["mid"] = {"file": Path(one(args.mid)).name,
                      **window_stats(one(args.mid), *box)}
    res["gcov_scene_median_db"] = summ.get("hh_median_diff_db",
                                           summ.get("hv_median_diff_db"))
    for algo in ALGOS:
        b = res["before"].get(algo, {}).get("median_m3m3")
        a = res["after"].get(algo, {}).get("median_m3m3")
        res[f"delta_{algo}"] = round(a - b, 4) if a is not None and b is not None else None
    print(json.dumps(res, indent=1))

    if args.patch_summary:
        summ["soil_moisture_check"] = res
        json.dump(summ, open(ROOT / f"outputs/{args.case}/summary.json", "w"), indent=1)
        print(f"patched outputs/{args.case}/summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
