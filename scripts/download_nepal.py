#!/usr/bin/env python3
"""Download the Nepal Rasuwa GLOF same-track GCOV pair (EMSR927) into data/nepal/gcov/.

Locked: track 048_D_074, 16 Aug 2026 before (DHDH), 28 Aug 2026 after (QPDH).
Does not download Snyder or Latvia. These Himalaya frames are ~7 GB each (~14 GB pair).
On a small disk use `python scripts/crop_nepal.py` instead (HTTPS range-read of the Rasuwa crop).
"""

from __future__ import annotations

import sys
from pathlib import Path

import earthaccess
from earthaccess.exceptions import LoginStrategyUnavailable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "nepal" / "gcov"

NEEDLE = "048_D_074"
BBOX = (85.10, 27.90, 85.55, 28.35)
WINDOWS = (
    ("before", "2026-08-14", "2026-08-18"),
    ("after", "2026-08-27", "2026-08-30"),
)
SHORT_NAME = "NISAR_L2_GCOV_PROVISIONAL_V1"


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

    chosen = []
    for label, start, end in WINDOWS:
        hits = earthaccess.search_data(
            short_name=SHORT_NAME,
            bounding_box=BBOX,
            temporal=(start, end),
            count=20,
        )
        match = [g for g in hits if NEEDLE in granule_id(g) and "GCOV" in granule_id(g)]
        print(f"{label} {start} → {end}: {len(hits)} hits, {len(match)} match {NEEDLE}")
        for g in match:
            print(f"  {granule_id(g)}  ~{getattr(g, 'size', '?')} MB")
        if not match:
            print(f"No {NEEDLE} granule in {label} window", file=sys.stderr)
            return 1
        chosen.append(match[0])

    OUT.mkdir(parents=True, exist_ok=True)
    print(f"\nDownloading {len(chosen)} granules → {OUT}")
    paths = earthaccess.download(chosen, local_path=str(OUT), threads=2, show_progress=True)
    for path in paths:
        p = Path(path)
        mb = p.stat().st_size / 1_000_000 if p.exists() else 0
        print(f"  saved {p} ({mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
