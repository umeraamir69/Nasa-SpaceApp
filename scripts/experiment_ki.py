#!/usr/bin/env python3
"""Kittler-Illingworth + tiled-KI vs Otsu vs fixed on Nepal (conda env).

Literature says KI minimum-error thresholding usually beats Otsu on SAR, and
the operational standard is split-based KI (tile the scene, threshold each
tile). Uses cv2 for Otsu cross-check + connected components.

Prints a comparison table scored vs HOT flood. No files are written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from affine import Affine
from pyproj import Transformer
from rasterio.features import rasterize
from shapely.geometry import shape
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from shapely.ops import transform as shp_transform  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import change_nepal as CN  # noqa: E402


def ki_cut(values: np.ndarray, bins: int = 256) -> float | None:
    """Kittler-Illingworth minimum-error threshold (Sezgin & Sankur)."""
    v = values[np.isfinite(values)]
    if v.size < 100:
        return None
    lo, hi = np.percentile(v, [0.5, 99.5])
    hist, edges = np.histogram(v, bins=bins, range=(lo, hi))
    centers = (edges[:-1] + edges[1:]) / 2
    p = hist / hist.sum()
    P1 = np.cumsum(p)
    P2 = 1.0 - P1
    idx = np.arange(bins)
    m1 = np.cumsum(p * idx) / np.where(P1 == 0, 1, P1)
    m2 = (np.cumsum((p * idx)[::-1]) / np.where(P2[::-1] == 0, 1, P2[::-1]))[::-1]
    v1 = np.cumsum(p * (idx - m1) ** 2) / np.where(P1 == 0, 1, P1)
    v2 = (np.cumsum((p * (idx - m2) ** 2)[::-1]) / np.where(P2[::-1] == 0, 1, P2[::-1]))[::-1]
    ok = (P1 > 0) & (P2 > 0) & (v1 > 0) & (v2 > 0)
    if not ok.any():
        return None
    J = np.full(bins, np.nan)
    J[ok] = (P1[ok] * np.log(v1[ok]) / 2 - P1[ok] * np.log(P1[ok])
             + P2[ok] * np.log(v2[ok]) / 2 - P2[ok] * np.log(P2[ok]))
    return float(centers[int(np.nanargmin(J))])


def blobs_cv2(mask: np.ndarray, min_px: int = 3) -> np.ndarray:
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    keep = np.zeros_like(mask)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= min_px:
            keep |= lab == i
    return keep


def main() -> int:
    full = CN.load_gcov(needle="098_A_016")
    x, y = np.asarray(full["x"]), np.asarray(full["y"])
    dx, dy = float(full["dx"]), float(full["dy"])
    valid = CN.product_valid(full["before"]["mask"]) & CN.product_valid(full["after"]["mask"])
    b = CN.despeckle(CN.to_db(full["before"]["HHHH"]))
    a = CN.despeckle(CN.to_db(full["after"]["HHHH"]))
    valid &= np.isfinite(b) & np.isfinite(a) & (full["before"]["HHHH"] > 0) & (full["after"]["HHHH"] > 0)
    diff = np.where(valid, a - b, np.nan)

    # cv2 Otsu cross-check (diff normalized to uint8)
    vv = diff[valid]
    lo, hi = np.percentile(vv, [0.5, 99.5])
    u8 = np.clip((np.nan_to_num(diff, nan=lo) - lo) / (hi - lo) * 255, 0, 255).astype(np.uint8)
    t_cv, _ = cv2.threshold(u8[valid], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    otsu_cv = lo + (t_cv / 255) * (hi - lo)

    ki_global = ki_cut(vv)
    # split-KI: 4x4 tiles, median of tile cuts with enough valid pixels
    H, W = diff.shape
    tile_cuts = []
    for r in np.array_split(np.arange(H), 4):
        for c in np.array_split(np.arange(W), 4):
            sub = diff[np.ix_(r, c)]
            if np.isfinite(sub).sum() > 2000:
                t = ki_cut(sub.ravel())
                if t is not None:
                    tile_cuts.append(t)
    ki_split = float(np.median(tile_cuts)) if tile_cuts else None
    print(f"cuts: cv2-Otsu {otsu_cv:+.2f} (numpy-Otsu was +0.04) | KI-global {ki_global if ki_global is None else f'{ki_global:+.2f}'} | split-KI {ki_split if ki_split is None else f'{ki_split:+.2f}'} from {len(tile_cuts)} tiles")

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

    print(f"\n{'rule':40s} {'px':>6s} {'P':>6s} {'R':>6s} {'IoU':>6s}")
    rows = [("shipped fixed -2.0", -2.0), ("cv2 Otsu", otsu_cv)]
    if ki_global is not None:
        rows.append(("KI global", ki_global))
    if ki_split is not None:
        rows.append(("split-KI median", ki_split))
    for name, thr in rows:
        m = blobs_cv2(valid & in_official & ~perm & np.isfinite(diff) & (diff <= thr))
        tp = int((m & truth).sum())
        fp = int((m & ~truth).sum())
        fn = int((~m & truth & valid).sum())
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        iou = tp / (tp + fp + fn) if tp + fp + fn else 0.0
        print(f"{name:40s} {m.sum():6d} {p:6.3f} {r:6.3f} {iou:6.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
