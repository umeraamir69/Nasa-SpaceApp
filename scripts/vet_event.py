#!/usr/bin/env python3
"""Vet a candidate event: find same-track, same-mode GCOV pairs (stdlib only).

Queries CMR (no auth) for two windows over a bbox, groups by
track/dir/frame/beam/mode, and prints candidate before→after pairs.

  vet_event.py --name coleman --bbox=-119.3,43.3,-118.3,43.9 \\
      --before=2026-07-01,2026-07-25 --after=2026-07-27,2026-08-20
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict

CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
SHORT = "NISAR_L2_GCOV_PROVISIONAL_V1"
RX = re.compile(r"NISAR_L2_PR_GCOV_\d+_(\d+)_([AD])_(\d+)_(\d+)_([A-Z]+)_")


def key(title: str):
    m = RX.search(title or "")
    return m.groups() if m else None  # track, dir, frame, beam, mode


def date_of(title: str) -> str:
    m = re.search(r"_(\d{8})T", title or "")
    return m.group(1) if m else "?"


def query(bbox: str, start: str, end: str):
    qs = urllib.parse.urlencode({
        "short_name": SHORT, "bounding_box": bbox,
        "temporal": f"{start}T00:00:00Z,{end}T23:59:59Z",
        "page_size": 100,
    })
    with urllib.request.urlopen(CMR + "?" + qs, timeout=60) as r:
        d = json.load(r)
    return [e.get("title", "") for e in d.get("feed", {}).get("entry", [])]


def main() -> int:
    ap = argparse.ArgumentParser(description="Vet same-mode pairs for an event.")
    ap.add_argument("--name", required=True)
    ap.add_argument("--bbox", required=True)
    ap.add_argument("--before", required=True, help="start,end")
    ap.add_argument("--after", required=True, help="start,end")
    args = ap.parse_args()

    b0, b1 = args.before.split(",")
    a0, a1 = args.after.split(",")
    before = query(args.bbox, b0, b1)
    after = query(args.bbox, a0, a1)
    print(f"## {args.name}: {len(before)} before-hits, {len(after)} after-hits")

    bg = defaultdict(list)
    for t in before:
        k = key(t)
        if k:
            bg[k].append(t)
    ag = defaultdict(list)
    for t in after:
        k = key(t)
        if k:
            ag[k].append(t)
    pairs = 0
    for k in sorted(set(bg) & set(ag)):
        track, direction, frame, beam, mode = k
        b = sorted(bg[k], key=date_of)[0]
        a = sorted(ag[k], key=date_of)[-1]
        print(f"  PAIR {track}_{direction}_{frame} {beam} {mode}: "
              f"{date_of(b)} -> {date_of(a)}")
        pairs += 1
    if not pairs:
        print("  no same-track/mode pair")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
