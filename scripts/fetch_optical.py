#!/usr/bin/env python3
"""Crop a Sentinel-2 true-color scene into a case box for the why-SAR overlay.

Default is Snyder 7 Jul 2026 (34% cloud). Latvia uses a STAC search around
the 21–22 Aug 2026 storm (prefer a cloudy scene — that is the point).
"""

from __future__ import annotations

import argparse
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
STAC = "https://earth-search.aws.element84.com/v1/search"
SNYDER_SCENE = "S2C_12SXJ_20260707_1_L2A"


def stac_post(body: dict) -> list[dict]:
    req = urllib.request.Request(
        STAC,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp).get("features") or []


def stac_scene(scene_id: str) -> dict:
    feats = stac_post({"collections": ["sentinel-2-l2a"], "ids": [scene_id]})
    if not feats:
        raise SystemExit(f"no STAC feature for {scene_id}")
    return feats[0]


def _overlap(scene_bbox: list[float], bbox: list[float]) -> float:
    w, s, e, n = max(scene_bbox[0], bbox[0]), max(scene_bbox[1], bbox[1]), min(scene_bbox[2], bbox[2]), min(scene_bbox[3], bbox[3])
    if e <= w or n <= s:
        return 0.0
    return ((e - w) * (n - s)) / ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))


def stac_search(bbox: list[float], start: str, end: str) -> dict:
    feats = stac_post(
        {
            "collections": ["sentinel-2-l2a"],
            "bbox": bbox,
            "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z",
            "limit": 20,
        }
    )
    if not feats:
        raise SystemExit(f"no Sentinel-2 L2A in {bbox} {start}→{end}")

    def cloud(f: dict) -> float:
        return float((f.get("properties") or {}).get("eo:cloud_cover") or 0)

    def score(f: dict) -> tuple:
        ov = _overlap(f.get("bbox") or [0, 0, 0, 0], bbox)
        c = cloud(f)
        storm = 1.0 if str((f.get("properties") or {}).get("datetime") or "").startswith("2026-08-21") else 0.0
        cloudy = 1.0 if 20 <= c <= 90 else 0.0
        return (ov * cloudy + 0.15 * storm * ov, ov, c)

    feats.sort(key=score, reverse=True)
    return feats[0]


def write_crop(feat: dict, bounds: dict, out_dir: Path, why: str) -> dict:
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
    alpha = (np.max(arr, axis=2) > 0).astype(np.uint8) * 255
    rgba = np.dstack([arr, alpha])
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / "optical.png"
    plt.imsave(png, rgba)
    meta = {
        "id": feat.get("id"),
        "datetime": props.get("datetime"),
        "cloud_cover_pct": props.get("eo:cloud_cover"),
        "collection": "sentinel-2-l2a",
        "visual": visual,
        "stac": STAC,
        "citation": "Sentinel-2 L2A true-color (TCI) via Element84 Earth Search / AWS sentinel-cogs. ESA Copernicus.",
        "why": why,
    }
    (out_dir / "optical.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {png}  ({png.stat().st_size} bytes)")
    print(json.dumps(meta, indent=2))
    return meta


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=("snyder", "latvia", "thunderbay", "crete",
                                            "isaias", "coleman", "secondflat",
                                            "spokane"),
                        default="snyder")
    args = parser.parse_args()
    out = ROOT / "outputs" / args.case / "layers"
    bounds_path = out / "bounds.json"
    if not bounds_path.exists():
        raise SystemExit(f"missing {bounds_path} — run the change script first")
    bounds = json.loads(bounds_path.read_text())
    if args.case == "snyder":
        feat = stac_scene(SNYDER_SCENE)
        why = "Cloudy scene on 7 Jul 2026, during the Snyder Fire, same box as the NISAR pair."
    elif args.case == "thunderbay":
        bbox = [bounds["west"], bounds["south"], bounds["east"], bounds["north"]]
        feat = stac_search(bbox, "2026-07-12", "2026-08-16")
        why = "Sentinel-2 during the Thunder Bay 36 burn (smoke/cloud is the why-SAR beat)."
    elif args.case == "crete":
        bbox = [bounds["west"], bounds["south"], bounds["east"], bounds["north"]]
        feat = stac_search(bbox, "2026-10-01", "2026-10-06")
        why = "Sentinel-2 during the 2–4 Oct 2026 Crete storm. Cloud is the why-SAR beat."
    elif args.case == "isaias":
        bbox = [bounds["west"], bounds["south"], bounds["east"], bounds["north"]]
        feat = stac_search(bbox, "2026-10-08", "2026-10-12")
        why = "Sentinel-2 around the 9 Oct 2026 Isaias landfall. Cloud is the why-SAR beat."
    elif args.case in ("coleman", "secondflat"):
        bbox = [bounds["west"], bounds["south"], bounds["east"], bounds["north"]]
        feat = stac_search(bbox, "2026-07-24", "2026-08-13")
        why = "Sentinel-2 during the late-July 2026 Oregon burns. Smoke is the why-SAR beat."
    elif args.case == "spokane":
        bbox = [bounds["west"], bounds["south"], bounds["east"], bounds["north"]]
        feat = stac_search(bbox, "2026-08-01", "2026-08-16")
        why = "Sentinel-2 during the early-Aug 2026 Spokane fires. Smoke is the why-SAR beat."
    else:
        bbox = [bounds["west"], bounds["south"], bounds["east"], bounds["north"]]
        feat = stac_search(bbox, "2026-08-20", "2026-08-24")
        why = "Sentinel-2 around the 21–22 Aug 2026 Latvia flood. Cloud is the why-SAR beat."
    write_crop(feat, bounds, out, why)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

