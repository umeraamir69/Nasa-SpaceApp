#!/usr/bin/env python3
"""GUNW coherence second vote for flood cases (conda env).

Samples co-event GUNW HH coherence onto the shipped GCOV crop and compares
mean coherence inside the shipped change flags (and truth polygons, if any)
vs background. Open water decorrelates hard (~0), so a real flood should
show lower coherence inside flags; a negative should show no split.

  xcheck_gunw.py --case nepal    # needs data/nepal/gunw/*.h5 (098_A_016 co-event)
  xcheck_gunw.py --case latvia   # needs data/latvia/gunw/*.h5 (080_D_059 co-event)

Reuses each change script's load_gcov() for the exact shipped crop geometry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import h5py
import numpy as np
from affine import Affine
from pyproj import Transformer
from rasterio.features import rasterize
from shapely.geometry import shape
from shapely.ops import transform as shp_transform
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

COH = "science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude"
GX = "science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/xCoordinates"
GY = "science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/yCoordinates"

CASES = {
    "nepal": {"needle": "098_A_016", "truth": ["flood_extent.geojson", "emsr927.geojson"]},
    "latvia": {"needle": None, "truth": []},
}


def load_crop(case: str):
    if case == "nepal":
        import change_nepal as C
        return C.load_gcov(needle=CASES[case]["needle"]), C
    import change_latvia as C
    return C.load_gcov(), C


def rasterize_geojson(path: Path, epsg: int, transform: Affine, shape_hw) -> np.ndarray:
    if not path.exists():
        return np.zeros(shape_hw, bool)
    gj = json.load(open(path))
    to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True).transform
    geoms = []
    for feat in gj.get("features", []):
        g = feat.get("geometry")
        if g:
            geoms.append(shp_transform(to_utm, shape(g)))
    if not geoms:
        return np.zeros(shape_hw, bool)
    return rasterize([(g, 1) for g in geoms], out_shape=shape_hw,
                     transform=transform, fill=0).astype(bool)


def main() -> int:
    ap = argparse.ArgumentParser(description="GUNW coherence second vote.")
    ap.add_argument("--case", choices=("nepal", "latvia"), required=True)
    ap.add_argument("--patch-summary", action="store_true")
    args = ap.parse_args()

    gunw_files = sorted((ROOT / f"data/{args.case}/gunw").glob("*.h5"))
    if not gunw_files:
        raise SystemExit(f"no data/{args.case}/gunw/*.h5 — run download_aux.py")
    gpath = gunw_files[0]
    print(f"GUNW: {gpath.name}")

    full, C = load_crop(args.case)
    x, y = np.asarray(full["x"]), np.asarray(full["y"])
    dx, dy = float(full["dx"]), float(full["dy"])
    H, W = y.size, x.size
    aff = Affine(dx, 0.0, x[0] - dx / 2, 0.0, dy, y[0] - dy / 2)

    with h5py.File(gpath, "r") as f:
        if COH not in f:
            raise SystemExit(f"{gpath.name}: no {COH}")
        gx, gy = f[GX][:], f[GY][:]
        print(f"GUNW grid: {f[COH].shape}, dx~{gx[1]-gx[0]:.1f}")
        cols = np.searchsorted(gx, x).clip(0, gx.size - 1)
        rows = np.searchsorted(-gy, -y).clip(0, gy.size - 1)
        band = f[COH][rows[0]:rows[-1] + 1, :].astype(np.float32)
        coh = band[rows - rows[0]][:, cols]
    coh[(coh < 0) | (coh > 1)] = np.nan

    outdir = ROOT / f"outputs/{args.case}"
    flags = rasterize_geojson(outdir / "change.geojson", full["epsg"], aff, (H, W))
    valid = np.isfinite(coh)
    bg = valid & ~flags

    def stats(mask, name):
        m = mask & valid
        return {"region": name, "n_px": int(m.sum()),
                "mean": round(float(np.nanmean(coh[m])), 4) if m.sum() else None,
                "low_frac": round(float(np.mean(coh[m] < 0.4)), 4) if m.sum() else None}

    res = {"gunw_file": gpath.name,
           "regions": [stats(flags, "shipped_change_flags"), stats(bg, "background")]}
    for t in CASES[args.case]["truth"]:
        tm = rasterize_geojson(outdir / t, full["epsg"], aff, (H, W))
        res["regions"].append(stats(tm, f"truth:{t}"))
    split = (res["regions"][0]["mean"] is not None
             and res["regions"][1]["mean"] is not None
             and res["regions"][0]["mean"] < res["regions"][1]["mean"] - 0.05)
    res["verdict"] = ("flags decorrelated vs background — confirms real surface "
                      "change; water needs the rivers/truth test"
                      if split else "no coherence split")
    print(json.dumps(res, indent=1))

    if args.patch_summary:
        sp = outdir / "summary.json"
        summ = json.load(open(sp))
        summ["gunw_check"] = res
        json.dump(summ, open(sp, "w"), indent=1)
        print(f"patched {sp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
