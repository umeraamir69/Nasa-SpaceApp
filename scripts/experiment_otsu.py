#!/usr/bin/env python3
"""Otsu vs fixed threshold on the Nepal HH diff (conda env, numpy Otsu).

Loads the shipped same-mode pair, computes Otsu's automatic cut on the
despeckled HH log-ratio, and scores {fixed 2.0 dB, Otsu} against the HOT
flood polygon. Answers: would an adaptive threshold beat our fixed cut?

Literature says Otsu is the most-used SAR auto-threshold but often
over-extracts; Kittler-Illingworth usually wins. This tests Otsu only.

Prints a comparison table. No files are written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

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
import change_nepal as CN  # noqa: E402


def otsu_cut(values: np.ndarray, bins: int = 256) -> float:
    v = values[np.isfinite(values)]
    lo, hi = np.percentile(v, [0.5, 99.5])
    hist, edges = np.histogram(v, bins=bins, range=(lo, hi))
    centers = (edges[:-1] + edges[1:]) / 2
    w = hist / hist.sum()
    csum = np.cumsum(w)
    msum = np.cumsum(w * centers)
    total = msum[-1]
    denom = csum * (1 - csum)
    with np.errstate(invalid="ignore", divide="ignore"):
        between = (total * csum - msum) ** 2 / np.where(denom == 0, np.nan, denom)
    return float(centers[int(np.nanargmax(between))])


def main() -> int:
    full = CN.load_gcov(needle="098_A_016")
    x, y = np.asarray(full["x"]), np.asarray(full["y"])
    dx, dy = float(full["dx"]), float(full["dy"])
    valid = CN.product_valid(full["before"]["mask"]) & CN.product_valid(full["after"]["mask"])
    b = CN.despeckle(CN.to_db(full["before"]["HHHH"]))
    a = CN.despeckle(CN.to_db(full["after"]["HHHH"]))
    valid &= np.isfinite(b) & np.isfinite(a) & (full["before"]["HHHH"] > 0) & (full["after"]["HHHH"] > 0)
    diff = np.where(valid, a - b, np.nan)

    cut = otsu_cut(diff[valid])
    print(f"Otsu cut on HH diff: {cut:+.2f} dB  (fixed shipped cut: -2.00 dB)")

    from scipy.ndimage import label as nd_label

    aff = Affine(dx, 0.0, x[0] - dx / 2, 0.0, dy, y[0] - dy / 2)
    to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{full['epsg']}", always_xy=True).transform

    def raster(path):
        gj = json.load(open(path))
        geoms = [shp_transform(to_utm, shape(f["geometry"]))
                 for f in gj["features"] if f.get("geometry")]
        return rasterize([(g, 1) for g in geoms], out_shape=diff.shape,
                         transform=aff, fill=0).astype(bool)

    truth = raster(ROOT / "outputs/nepal/flood_extent.geojson")
    in_official = truth | raster(ROOT / "outputs/nepal/emsr927.geojson")
    perm = valid & (b <= CN.WATER_DB) & (a <= CN.WATER_DB)

    def blobs(mask):
        labeled, nlab = nd_label(mask)
        keep = np.zeros_like(mask)
        for i in range(1, nlab + 1):
            blob = labeled == i
            if int(blob.sum()) >= 3:
                keep |= blob
        return keep

    print(f"\n{'rule':44s} {'px':>6s} {'P':>6s} {'R':>6s} {'IoU':>6s}")
    for name, thr in [
        ("shipped: dHH<=-2.0, official, min3px", -2.0),
        ("Otsu cut, official, min3px", cut),
    ]:
        m = blobs(valid & in_official & ~perm & np.isfinite(diff) & (diff <= thr))
        tp = int((m & truth).sum())
        fp = int((m & ~truth).sum())
        fn = int((~m & truth & valid).sum())
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        iou = tp / (tp + fp + fn) if tp + fp + fn else 0.0
        print(f"{name:44s} {m.sum():6d} {p:6.3f} {r:6.3f} {iou:6.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
