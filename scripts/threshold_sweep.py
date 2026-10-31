#!/usr/bin/env python3
"""Threshold sweep: precision/recall/IoU vs a truth polygon at many dB cuts.

Picks the knee instead of a round number. Operates on an npz crop pair
(crop_nepal.py format) so no 7 GB granules are needed.

Run:  .conda/env/bin/python scripts/threshold_sweep.py data/nepal/crop \\
        outputs/nepal/flood_extent.geojson --pol HHHH --gates -14,-12,-10

Prints one row per (threshold, after-water gate). No files are written.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from rasterio.features import rasterize
from rasterio.transform import Affine

sys.path.insert(0, str(Path(__file__).resolve().parent))

import change_nepal as CN  # noqa: E402


def load_npz_pair(crop: Path):
    before = np.load(crop / "before.npz", allow_pickle=False)
    after = np.load(crop / "after.npz", allow_pickle=False)
    pols = [str(p) for p in before["pols"].tolist()]

    def pack(z):
        out = {"mask": z["mask"]}
        for pol in pols:
            out[pol] = z[pol]
        return out

    return {"epsg": int(before["epsg"]), "x": before["x"], "y": before["y"],
            "dx": float(before["dx"]), "dy": float(before["dy"]),
            "before": pack(before), "after": pack(after)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Sweep dB thresholds vs truth polygons.")
    ap.add_argument("crop", help="dir with before.npz/after.npz")
    ap.add_argument("truth", help="GeoJSON whose polygons are ground truth")
    ap.add_argument("--pol", default="HHHH")
    ap.add_argument("--thresholds", default="1.0,1.5,2.0,2.5,3.0,4.0")
    ap.add_argument("--gates", default="none",
                    help="after-water gates in dB, e.g. -14,-12,-10, or 'none'")
    args = ap.parse_args()

    from shapely.geometry import shape
    from shapely.ops import unary_union

    src = load_npz_pair(Path(args.crop))
    pol = args.pol
    x, y, dx, dy = src["x"], src["y"], src["dx"], src["dy"]
    transform = Affine(dx, 0.0, float(x[0]) - dx / 2.0, 0.0, dy, float(y[0]) - dy / 2.0)
    hw = (y.size, x.size)

    gj = json.loads(Path(args.truth).read_text())
    geoms = [shape(f["geometry"]) for f in gj.get("features") or [] if f.get("geometry")]
    if not geoms:
        raise SystemExit("truth geojson has no geometries")
    truth_ll = unary_union(geoms)
    # Reproject to grid CRS.
    from pyproj import Transformer
    to_crs = Transformer.from_crs("EPSG:4326", f"EPSG:{src['epsg']}", always_xy=True)

    def _t(coords):
        lon, lat = to_crs.transform(coords[:, 0], coords[:, 1])
        out = np.empty_like(coords)
        out[:, 0], out[:, 1] = lon, lat
        if coords.shape[1] > 2:
            out[:, 2:] = coords[:, 2:]
        return out

    from shapely import transform as shp_xy
    truth_grid = shp_xy(truth_ll, _t)
    truth = rasterize([(truth_grid, 1)], out_shape=hw, transform=transform,
                      fill=0, dtype=np.uint8).astype(bool)
    print(f"truth pixels in crop: {truth.sum()} ({truth.mean() * 100:.2f}%)")
    if not truth.any():
        raise SystemExit("truth misses the crop")

    valid = (CN.product_valid(src["before"]["mask"]) & CN.product_valid(src["after"]["mask"])
             & np.isfinite(src["before"][pol]) & np.isfinite(src["after"][pol])
             & (src["before"][pol] > 0) & (src["after"][pol] > 0))
    db_b = CN.despeckle(CN.to_db(src["before"][pol]))
    db_a = CN.despeckle(CN.to_db(src["after"][pol]))
    db_b[~valid] = np.nan
    db_a[~valid] = np.nan
    diff = db_a - db_b
    print(f"valid frac: {valid.mean():.3f}  diff median: {np.nanmedian(diff[valid]):+.2f} dB")

    thresholds = [float(t) for t in args.thresholds.split(",")]
    gates = [None] if args.gates == "none" else [float(g) for g in args.gates.split(",")]
    print(f"\n{'thresh':>7} {'gate':>7} {'prec':>6} {'rec':>6} {'iou':>6} {'f1':>6} {'px':>8}")
    for gate in gates:
        for t in thresholds:
            m = valid & np.isfinite(diff) & (diff <= -t)
            if gate is not None:
                m &= db_a <= gate
            tp = float((m & truth).sum())
            fp = float((m & ~truth).sum())
            fn = float((~m & truth & valid).sum())
            prec = tp / (tp + fp) if (tp + fp) else 0.0
            rec = tp / (tp + fn) if (tp + fn) else 0.0
            iou = tp / (tp + fp + fn) if (tp + fp + fn) else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
            g = "none" if gate is None else f"{gate:g}"
            print(f"{t:7.1f} {g:>7} {prec:6.3f} {rec:6.3f} {iou:6.3f} {f1:6.3f} {int(m.sum()):8d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
