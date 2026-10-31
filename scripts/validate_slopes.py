#!/usr/bin/env python3
"""DEM slope audit: are flagged pixels sitting on layover-prone slopes? (conda env)

Reads Copernicus 30 m DEM straight from AWS Open Data (no auth) over each
case box, compares the slope distribution of EchoLens change polygons against
the box background, and patches slope_check into each summary.json.

Run:  .conda/env/bin/python scripts/validate_slopes.py [--case snyder|latvia|nepal]
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[1]
CASES = ("snyder", "latvia", "nepal", "thunderbay", "crete", "isaias")


def dem_url(lat: float, lon: float) -> str:
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return (f"/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/"
            f"Copernicus_DSM_COG_10_{ns}{abs(math.floor(lat)):02d}_00_"
            f"{ew}{abs(math.floor(lon)):03d}_00_DEM/"
            f"Copernicus_DSM_COG_10_{ns}{abs(math.floor(lat)):02d}_00_"
            f"{ew}{abs(math.floor(lon)):03d}_00_DEM.tif")


def slope_deg(dem: np.ndarray, res_m: float) -> np.ndarray:
    gy, gx = np.gradient(dem.astype(np.float64), res_m)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def audit(case: str) -> dict:
    bounds = json.loads((ROOT / "outputs" / case / "layers" / "bounds.json").read_text())
    west, south, east, north = (bounds["west"], bounds["south"], bounds["east"], bounds["north"])
    gj = json.loads((ROOT / "outputs" / case / "change.geojson").read_text())
    geoms = [shape(f["geometry"]) for f in gj["features"] if f.get("geometry")]

    # Cover the box with 1° DEM tiles (boxes are ≤1.3° wide; keep it simple).
    tiles = []
    for lat in range(math.floor(south), math.floor(north) + 1):
        for lon in range(math.floor(west), math.floor(east) + 1):
            tiles.append((lat, lon))

    os.environ["AWS_NO_SIGN_REQUEST"] = "YES"
    slopes_flag, slopes_bg = [], []
    with rasterio.Env(AWS_NO_SIGN_REQUEST="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        for lat, lon in tiles:
            url = dem_url(lat + 0.5, lon + 0.5)
            try:
                src = rasterio.open(url)
            except Exception as exc:
                print(f"  {case}: cannot open DEM tile {lat}/{lon}: {exc}")
                continue
            with src:
                tw, ts, te, tn = transform_bounds("EPSG:4326", src.crs, west, south, east, north,
                                                  densify_pts=21)
                win = from_bounds(tw, ts, te, tn, transform=src.transform)
                win = win.round_lengths().round_offsets()
                arr = src.read(1, window=win, boundless=True, fill_value=np.nan)
                aff = src.window_transform(win)
            arr = np.where(arr > 30000, np.nan, arr).astype(np.float32)
            res_deg = abs(aff.a)
            res_m = res_deg * 111320.0 * math.cos(math.radians((south + north) / 2))
            sl = slope_deg(np.where(np.isfinite(arr), arr, np.nanmedian(arr)), res_m)
            sl[~np.isfinite(arr)] = np.nan
            shapes = [(g, 1) for g in geoms]
            mask = rasterize(shapes, out_shape=arr.shape, transform=aff, fill=0,
                             dtype=np.uint8).astype(bool) if shapes else np.zeros_like(arr, bool)
            ok = np.isfinite(sl)
            slopes_bg.extend(sl[ok & ~mask].ravel().tolist())
            slopes_flag.extend(sl[ok & mask].ravel().tolist())
    slopes_bg = np.array(slopes_bg, dtype=np.float64)
    slopes_flag = np.array(slopes_flag, dtype=np.float64)

    def frac(a, t):
        return round(float((a > t).mean()), 3) if a.size else 0.0

    stats = {
        "dem": "Copernicus DSM 30 m (AWS Open Data)",
        "flagged_pixels": int(slopes_flag.size),
        "flagged_median_slope_deg": round(float(np.median(slopes_flag)), 1) if slopes_flag.size else None,
        "background_median_slope_deg": round(float(np.median(slopes_bg)), 1) if slopes_bg.size else None,
        "flagged_frac_over_10deg": frac(slopes_flag, 10),
        "background_frac_over_10deg": frac(slopes_bg, 10),
        "flagged_frac_over_20deg": frac(slopes_flag, 20),
        "background_frac_over_20deg": frac(slopes_bg, 20),
    }
    print(f"{case}: {json.dumps(stats)}")
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", choices=CASES, default=None)
    args = ap.parse_args()
    for case in [args.case] if args.case else CASES:
        stats = audit(case)
        spath = ROOT / "outputs" / case / "summary.json"
        summary = json.loads(spath.read_text())
        summary["slope_check"] = stats
        spath.write_text(json.dumps(summary, indent=2))
        print(f"patched {spath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
