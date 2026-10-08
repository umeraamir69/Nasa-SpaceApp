#!/usr/bin/env python3
"""Download the Snyder Fire same-track GCOV pair into data/snyder/gcov/."""

from __future__ import annotations

import sys
from pathlib import Path

import earthaccess
from earthaccess.exceptions import LoginStrategyUnavailable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "snyder" / "gcov"

# Same-track pair locked in notes/research/NISAR data access.md
NEEDLE = "048_A_021"
BBOX = (-109.45, 38.85, -108.55, 39.50)
WINDOWS = (
    ("before", "2026-06-17", "2026-06-26"),
    ("after", "2026-07-18", "2026-07-26"),
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
        match = [g for g in hits if NEEDLE in granule_id(g)]
        print(f"{label} {start} → {end}: {len(hits)} hits, {len(match)} match {NEEDLE}")
        for g in match:
            size = getattr(g, "size", "?")
            print(f"  {granule_id(g)}  ~{size} MB")
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
