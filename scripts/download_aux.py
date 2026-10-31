#!/usr/bin/env python3
"""Download NISAR auxiliary granules (SME2 soil moisture, GUNW coherence, ...).

Generic single-window downloader: pick granules by short name + needle +
bbox + temporal window. Used for the SME2 soil-moisture cross-check and the
GUNW flood second vote. Earthdata via ~/.netrc or EARTHDATA_* env vars.

Examples:
  download_aux.py --short-name NISAR_L3_SME2_PROVISIONAL_V1 --needle 004_A_017 \\
      --bbox=-87.3,30.1,-86.6,31.2 --temporal=2026-09-28,2026-10-14 \\
      --out=data/isaias/sme2 --expect=2
  download_aux.py --short-name NISAR_L2_GUNW_PROVISIONAL_V1 --needle 098_A_016 \\
      --bbox=85.0,27.9,85.5,28.3 --temporal=2026-08-19,2026-08-19 \\
      --out=data/nepal/gunw --expect=1
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import earthaccess
from earthaccess.exceptions import LoginStrategyUnavailable


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
    if login() is None:
        print("Not logged in. Need ~/.netrc or EARTHDATA_* env vars.", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(description="Download NISAR aux granules by filter.")
    parser.add_argument("--short-name", required=True)
    parser.add_argument("--needle", default="", help="substring the GranuleUR must contain")
    parser.add_argument("--bbox", required=True, help="lon_min,lat_min,lon_max,lat_max")
    parser.add_argument("--temporal", required=True, help="start,end (YYYY-MM-DD)")
    parser.add_argument("--out", required=True, help="download directory")
    parser.add_argument("--prefer", default="P05023", help="product version substring")
    parser.add_argument("--expect", type=int, default=0,
                        help="fail unless at least this many match (0 = no check)")
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    bbox = tuple(map(float, args.bbox.split(",")))
    start, end = args.temporal.split(",")

    hits = earthaccess.search_data(
        short_name=args.short_name, bounding_box=bbox,
        temporal=(start, end), count=50,
    )
    match = [g for g in hits if args.needle in granule_id(g)]
    print(f"{start} → {end}: {len(hits)} hits, {len(match)} match '{args.needle}'")
    for g in match:
        print(f"  {granule_id(g)}  ~{getattr(g, 'size', '?')} MB")
    if args.expect and len(match) < args.expect:
        print(f"expected >= {args.expect}, got {len(match)}", file=sys.stderr)
        return 1
    if not match:
        print("no matching granules", file=sys.stderr)
        return 1
    same = [g for g in match if args.prefer in granule_id(g)]
    chosen = sorted(same or match, key=granule_id)

    out = Path(args.out)
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
