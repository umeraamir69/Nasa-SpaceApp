#!/usr/bin/env python3
"""Range-read the Nepal GLOF crop from Earthdata without saving the 7 GB granules.

048_D_074 is ~6.7 GB (16 Aug) + ~7.6 GB (28 Aug). This laptop cannot store that.
Writes data/nepal/crop/{before,after}.npz (HHHH + mask, Rasuwa box only).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import earthaccess
import h5py
import numpy as np
from earthaccess.exceptions import LoginStrategyUnavailable
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "nepal" / "crop"

NEEDLE = "048_D_074"
BBOX = (85.10, 27.90, 85.55, 28.35)
GLOF_BBOX = (85.08, 27.90, 85.42, 28.30)
WINDOWS = (
    ("before", "2026-08-14", "2026-08-18"),
    ("after", "2026-08-27", "2026-08-30"),
)
SHORT_NAME = "NISAR_L2_GCOV_PROVISIONAL_V1"
GRID = "science/LSAR/GCOV/grids/frequencyB"
POLS = ("HHHH", "HVHV")
# CMR lists P (production) and X product versions of the same acquisition;
# always compare the same version on both dates.
PREFER_VERSION = "P05023"


def login():
    auth = None
    for strategy in ("netrc", "environment"):
        try:
            auth = earthaccess.login(strategy=strategy)
        except LoginStrategyUnavailable:
            continue
        if getattr(auth, "authenticated", False):
            return auth
    return None


def granule_id(item) -> str:
    umm = item.get("umm", {}) if hasattr(item, "get") else {}
    return str(umm.get("GranuleUR") or item)


def crop_window(x: np.ndarray, y: np.ndarray, west: float, south: float, east: float, north: float):
    col = np.where((x >= west) & (x <= east))[0]
    row = np.where((y >= south) & (y <= north))[0]
    if col.size == 0 or row.size == 0:
        raise SystemExit("GLOF box is outside the raster")
    return slice(row.min(), row.max() + 1), slice(col.min(), col.max() + 1)


def extract(handle, out_path: Path, granule: str) -> None:
    with h5py.File(handle, "r") as f:
        g = f[GRID]
        epsg = int(g["projection"][()])
        x = g["xCoordinates"][:]
        y = g["yCoordinates"][:]
        dx = float(g["xCoordinateSpacing"][()])
        dy = float(g["yCoordinateSpacing"][()])
        start = f["science/LSAR/identification/zeroDopplerStartTime"][()]
        if isinstance(start, bytes):
            start = start.decode()
        pols = [p for p in POLS if p in g]
        if not pols:
            raise SystemExit(f"no {POLS} in {list(g.keys())}")

        to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
        west, south = to_utm.transform(GLOF_BBOX[0], GLOF_BBOX[1])
        east, north = to_utm.transform(GLOF_BBOX[2], GLOF_BBOX[3])
        rows, cols = crop_window(x, y, west, south, east, north)
        payload = {
            "epsg": np.int32(epsg),
            "x": x[cols],
            "y": y[rows],
            "dx": np.float64(dx),
            "dy": np.float64(dy),
            "date": np.array(start[:10]),
            "granule": np.array(granule),
            "pols": np.array(pols),
            "mask": g["mask"][rows, cols],
        }
        for pol in pols:
            print(f"  reading {pol} {g[pol].shape} chunks={g[pol].chunks} → crop {(rows.stop-rows.start, cols.stop-cols.start)}")
            payload[pol] = g[pol][rows, cols]
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_path, **payload)
    mb = out_path.stat().st_size / 1_000_000
    print(f"  wrote {out_path} ({mb:.1f} MB) date={payload['date']}")


def pick(match: list, prefer: str):
    """Prefer one product version (P vs X) so both dates compare alike."""
    same = [g for g in match if prefer in granule_id(g)]
    pool = same or match
    pool = sorted(pool, key=granule_id)
    if same and len(match) > len(same):
        print(f"  preferring {prefer} ({len(same)}/{len(match)} matches)")
    return pool[0]


def main() -> int:
    global GLOF_BBOX, OUT
    parser = argparse.ArgumentParser(description="Range-read a GCOV crop without the 7 GB download.")
    parser.add_argument("--needle", default=NEEDLE, help="track substring, e.g. 048_D_074")
    parser.add_argument("--bbox", default=",".join(map(str, BBOX)),
                        help="lon_min,lat_min,lon_max,lat_max CMR search box")
    parser.add_argument("--crop", default=",".join(map(str, GLOF_BBOX)),
                        help="lon_min,lat_min,lon_max,lat_max crop box")
    parser.add_argument("--before", default=",".join(WINDOWS[0][1:]), help="start,end before window")
    parser.add_argument("--after", default=",".join(WINDOWS[1][1:]), help="start,end after window")
    parser.add_argument("--out", default=str(OUT), help="output dir for before.npz/after.npz")
    parser.add_argument("--prefer", default=PREFER_VERSION, help="product version substring")
    args = parser.parse_args()

    GLOF_BBOX = tuple(map(float, args.crop.split(",")))
    search_bbox = tuple(map(float, args.bbox.split(",")))
    windows = (("before", *args.before.split(",")), ("after", *args.after.split(",")))
    out = Path(args.out)
    OUT = out

    if login() is None:
        print("Not logged in. Need ~/.netrc or EARTHDATA_* env vars.", file=sys.stderr)
        return 1

    for label, start, end in windows:
        hits = earthaccess.search_data(
            short_name=SHORT_NAME,
            bounding_box=search_bbox,
            temporal=(start, end),
            count=20,
        )
        match = [g for g in hits if args.needle in granule_id(g) and "GCOV" in granule_id(g)]
        print(f"{label} {start} → {end}: {len(hits)} hits, {len(match)} match {args.needle}")
        if not match:
            print(f"No {args.needle} granule in {label} window", file=sys.stderr)
            return 1
        chosen = pick(match, args.prefer)
        gid = granule_id(chosen)
        print(f"  opening {gid} remotely (no 7 GB download)")
        opened = earthaccess.open([chosen])
        out.mkdir(parents=True, exist_ok=True)
        extract(opened[0], out / f"{label}.npz", gid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
