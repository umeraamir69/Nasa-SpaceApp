#!/usr/bin/env python3
"""Download Snyder same-track GUNW granules into data/snyder/gunw/.

GCOV change must already work. GUNW is the coherence second vote, not the
primary change image. Official GUNW is nearest-neighbor (~12-day) HH/VV.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import earthaccess
from earthaccess.exceptions import LoginStrategyUnavailable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "snyder" / "gunw"

NEEDLE = "048_A_021"
BBOX = (-109.45, 38.85, -108.55, 39.50)
# Cover pre-fire through contained: 12-day pairs that see the burn.
TEMPORAL = ("2026-06-17", "2026-07-26")
SHORT_NAME = "NISAR_L2_GUNW_PROVISIONAL_V1"


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

    hits = earthaccess.search_data(
        short_name=SHORT_NAME,
        bounding_box=BBOX,
        temporal=TEMPORAL,
        count=40,
    )
    date_re = re.compile(r"_(\d{8})T")

    def in_window(item) -> bool:
        ur = granule_id(item)
        if NEEDLE not in ur:
            return False
        dates = sorted(set(date_re.findall(ur)))
        if len(dates) < 2:
            return False
        # Keep 12-day pairs whose later date is still in the GCOV after-window
        # (skip 23 Jul → 16 Aug, which is post-containment).
        return dates[0] >= "20260617" and dates[-1] <= "20260726"

    match = [g for g in hits if in_window(g)]
    print(f"{SHORT_NAME} {TEMPORAL[0]} → {TEMPORAL[1]}: {len(hits)} hits, {len(match)} fire-window {NEEDLE}")
    for g in match:
        size = getattr(g, "size", "?")
        print(f"  {granule_id(g)}  ~{size} MB")
    if not match:
        print(f"No {NEEDLE} GUNW granule in window", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    print(f"\nDownloading {len(match)} granules → {OUT}")
    paths = earthaccess.download(match, local_path=str(OUT), threads=2, show_progress=True)
    for path in paths:
        p = Path(path)
        mb = p.stat().st_size / 1_000_000 if p.exists() else 0
        print(f"  saved {p} ({mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
