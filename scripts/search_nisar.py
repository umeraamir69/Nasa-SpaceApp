#!/usr/bin/env python3
"""Search NISAR L2 granules for EchoLens candidate events. Does not download."""

from __future__ import annotations

import argparse
import sys
from datetime import date

import earthaccess
from earthaccess.exceptions import LoginStrategyUnavailable

# lon_min, lat_min, lon_max, lat_max
EVENTS = {
    "snyder": {
        "title": "Snyder Fire (CO–UT border)",
        "bbox": (-109.45, 38.85, -108.55, 39.50),
        "before": ("2026-06-17", "2026-06-26"),
        "after": ("2026-07-18", "2026-07-26"),
        "notes": "Ignited 27 Jun, contained 17 Jul. After-window stops before the 27 Jul–10 Aug NISAR gap.",
    },
    "thunder-bay": {
        "title": "Thunder Bay 36 / Wabakimi (ON)",
        "bbox": (-90.40, 50.10, -88.70, 51.20),
        "before": ("2026-06-17", "2026-07-11"),
        "after": ("2026-08-11", "2026-09-15"),
        "notes": "Started 12 Jul. After-window starts after the 27 Jul–10 Aug NISAR gap.",
    },
}

PRODUCTS = (
    "NISAR_L2_GCOV_PROVISIONAL_V1",
    "NISAR_L2_GUNW_PROVISIONAL_V1",
)


def search(short_name: str, bbox: tuple[float, float, float, float], start: str, end: str):
    return earthaccess.search_data(
        short_name=short_name,
        bounding_box=bbox,
        temporal=(start, end),
        count=20,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", choices=sorted(EVENTS), required=True)
    args = parser.parse_args()
    event = EVENTS[args.event]

    print(f"# {event['title']}")
    print(event["notes"])
    print(f"bbox={event['bbox']}")
    print()

    auth = None
    for strategy in ("netrc", "environment"):
        try:
            auth = earthaccess.login(strategy=strategy)
        except LoginStrategyUnavailable:
            continue
        if getattr(auth, "authenticated", False):
            break
    if not getattr(auth, "authenticated", False):
        print(
            "Not logged in. Create https://urs.earthdata.nasa.gov/ then run:\n"
            "  python -c \"import earthaccess; earthaccess.login()\"",
            file=sys.stderr,
        )
        return 1

    for short_name in PRODUCTS:
        print(f"## {short_name}")
        for label in ("before", "after"):
            start, end = event[label]
            hits = search(short_name, event["bbox"], start, end)
            print(f"  {label:6} {start} → {end}: {len(hits)} granules")
            for item in hits[:3]:
                granule = item.get("umm", {}).get("GranuleUR") or item
                print(f"         - {granule}")
        print()

    print(f"searched {date.today().isoformat()} — no files downloaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
