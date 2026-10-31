#!/usr/bin/env python3
"""Download the Latvia flood same-track GCOV pair (EMSR926) into data/latvia/gcov/.

Locked: track 080_D_059, 18 Aug 2026 before, 30 Aug 2026 after.
Does not download Snyder. Does not download 071_A_030 (wrong swath).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import earthaccess
from earthaccess.exceptions import LoginStrategyUnavailable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "latvia" / "gcov"

NEEDLE = "080_D_059"
BBOX = (21.40, 56.40, 23.10, 57.40)
WINDOWS = (
    ("before", "2026-08-11", "2026-08-20"),
    ("after", "2026-08-28", "2026-09-02"),
)
SHORT_NAME = "NISAR_L2_GCOV_PROVISIONAL_V1"
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Download a same-track GCOV before/after pair.")
    parser.add_argument("--needle", default=NEEDLE, help="track substring, e.g. 080_D_059")
    parser.add_argument("--bbox", default=",".join(map(str, BBOX)),
                        help="lon_min,lat_min,lon_max,lat_max CMR search box")
    parser.add_argument("--before", default=",".join(WINDOWS[0][1:]), help="start,end before window")
    parser.add_argument("--after", default=",".join(WINDOWS[1][1:]), help="start,end after window")
    parser.add_argument("--out", default=str(OUT), help="download directory")
    parser.add_argument("--prefer", default=PREFER_VERSION, help="product version substring")
    parser.add_argument("--threads", type=int, default=4, help="download threads per file")
    args = parser.parse_args()
    search_bbox = tuple(map(float, args.bbox.split(",")))
    windows = (("before", *args.before.split(",")), ("after", *args.after.split(",")))
    out = Path(args.out)

    if login() is None:
        print("Not logged in. Need ~/.netrc or EARTHDATA_* env vars.", file=sys.stderr)
        return 1

    chosen = []
    for label, start, end in windows:
        hits = earthaccess.search_data(
            short_name=SHORT_NAME,
            bounding_box=search_bbox,
            temporal=(start, end),
            count=20,
        )
        match = [g for g in hits if args.needle in granule_id(g) and "GCOV" in granule_id(g)]
        print(f"{label} {start} → {end}: {len(hits)} hits, {len(match)} match {args.needle}")
        for g in match:
            print(f"  {granule_id(g)}  ~{getattr(g, 'size', '?')} MB")
        if not match:
            print(f"No {args.needle} granule in {label} window", file=sys.stderr)
            return 1
        same = [g for g in match if args.prefer in granule_id(g)]
        chosen.append(sorted(same or match, key=granule_id)[0])

    out.mkdir(parents=True, exist_ok=True)
    print(f"\nDownloading {len(chosen)} granules → {out}")
    paths = earthaccess.download(chosen, local_path=str(out), threads=args.threads,
                                 show_progress=True)
    for path in paths:
        p = Path(path)
        mb = p.stat().st_size / 1_000_000 if p.exists() else 0
        print(f"  saved {p} ({mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
