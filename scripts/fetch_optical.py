#!/usr/bin/env python3
"""Crop a cloudy Sentinel-2 scene over Snyder for the why-SAR overlay.

GIBS true-color snapshots had no data for these dates. We window-read a public
Sentinel-2 L2A Cloud-Optimized GeoTIFF (Element84 / AWS). Default scene is
2026-07-07 (34% cloud) during the fire.
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "snyder" / "layers"
BOUNDS = OUT / "bounds.json"
SCENE_ID = "S2C_12SXJ_20260707_1_L2A"
STAC = "https://earth-search.aws.element84.com/v1/search"


def stac_scene(scene_id: str) -> dict:
    body = json.dumps({"collections": ["sentinel-2-l2a"], "ids": [scene_id]}).encode()
    req = urllib.request.Request(STAC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        feats = json.load(resp).get("features") or []
    if not feats:
        raise SystemExit(f"no STAC feature for {scene_id}")
    return feats[0]


def main() -> int:
    if not BOUNDS.exists():
        raise SystemExit(f"missing {BOUNDS} — run python scripts/change_snyder.py first")
    bounds = json.loads(BOUNDS.read_text())
    feat = stac_scene(SCENE_ID)
    visual = feat["assets"]["visual"]["href"]
    props = feat.get("properties") or {}
    west, south, east, north = bounds["west"], bounds["south"], bounds["east"], bounds["north"]

    os.environ["AWS_NO_SIGN_REQUEST"] = "YES"
    with rasterio.Env(AWS_NO_SIGN_REQUEST="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(visual) as src:
            ubox = transform_bounds("EPSG:4326", src.crs, west, south, east, north, densify_pts=21)
            win = from_bounds(*ubox, transform=src.transform).round_lengths().round_offsets()
            scale = max(float(win.width) / 896.0, 1.0)
            out_w = max(1, int(round(win.width / scale)))
            out_h = max(1, int(round(win.height / scale)))
            rgb = src.read(
                indexes=[1, 2, 3],
                window=win,
                out_shape=(3, out_h, out_w),
                resampling=Resampling.bilinear,
                boundless=True,
                fill_value=0,
            )

    arr = np.transpose(rgb, (1, 2, 0))
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / "optical.png"
    plt.imsave(png, arr)
    meta = {
        "id": SCENE_ID,
        "datetime": props.get("datetime"),
        "cloud_cover_pct": props.get("eo:cloud_cover"),
        "collection": "sentinel-2-l2a",
        "visual": visual,
        "stac": STAC,
        "citation": "Sentinel-2 L2A true-color (TCI) via Element84 Earth Search / AWS sentinel-cogs. ESA Copernicus.",
        "why": "Cloudy scene on 7 Jul 2026, during the Snyder Fire, same box as the NISAR pair.",
    }
    (OUT / "optical.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {png}  ({png.stat().st_size} bytes)")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
