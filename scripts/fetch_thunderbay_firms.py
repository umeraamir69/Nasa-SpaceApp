#!/usr/bin/env python3
"""Fetch NASA FIRMS VIIRS active-fire hotspots for the Thunder Bay 36 window.

Queries VIIRS SNPP + NOAA-20 + NOAA-21 NRT over FIRE_BBOX for
2026-07-11 .. 2026-08-19 (the SAR pair window plus 3 days), merges and
dedupes, then writes:
  outputs/thunderbay/firms_points.csv  raw detections (all attributes)
  outputs/thunderbay/firms.geojson     Point overlay for the web map
  outputs/thunderbay/firms_truth.geojson  187.5 m buffered union, for
      change_thunderbay.py --truth scoring (half a VIIRS I-band pixel).

Needs env FIRMS_MAP_KEY (free key from https://firms.modaps.eosdis.nasa.gov/api/area/).
The key is never written to disk by this script.

Run:  .conda/env/bin/python scripts/fetch_thunderbay_firms.py
"""

from __future__ import annotations

import csv
import io
import json
import os
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import Point, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "thunderbay"

FIRE_BBOX = (-90.5, 49.5, -88.3, 51.1)  # west, south, east, north
START = date(2026, 7, 11)
END = date(2026, 8, 19)  # after-granule (08-16) + 3 days
STEP_DAYS = 5  # FIRMS area day_range max is 5
PRODUCTS = ("VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT")
BUFFER_M = 187.5  # half a VIIRS I-band (375 m) pixel
# Map overlay is grid-thinned so the browser stays fast: one detection
# (strongest FRP) per ~1 km cell. The full record lives in firms_points.csv
# and the scoring union (firms_truth.geojson) always uses ALL detections.
THIN_CELL_DEG = 0.01
API = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"


def window_starts():
    cur = START
    out = []
    while cur <= END:
        out.append(cur)
        cur = cur.fromordinal(cur.toordinal() + STEP_DAYS)
    return out


def fetch_csv(url: str, tries: int = 3) -> str:
    last = None
    for _ in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001 - transient network, retry
            last = e
            time.sleep(3)
    raise SystemExit(f"FIRMS request failed: {url.split('/csv/')[0]}/csv/... : {last}")


def main() -> int:
    key = os.environ.get("FIRMS_MAP_KEY", "").strip()
    if not key:
        raise SystemExit("set FIRMS_MAP_KEY env var (free key, never committed)")
    west, south, east, north = FIRE_BBOX
    rows: dict[tuple, dict] = {}
    per_product: dict[str, int] = {}
    for product in PRODUCTS:
        got = 0
        for start in window_starts():
            url = (f"{API}/{key}/{product}/{west},{south},{east},{north}"
                   f"/{STEP_DAYS}/{start.isoformat()}")
            text = fetch_csv(url)
            reader = csv.DictReader(io.StringIO(text))
            if not reader.fieldnames or "latitude" not in (reader.fieldnames or []):
                print(f"warn: unexpected response for {product} {start}: {text[:120]!r}")
                continue
            for row in reader:
                try:
                    acq = date.fromisoformat(row["acq_date"])
                except ValueError:
                    continue
                if not (START <= acq <= END):
                    continue
                if (row.get("confidence") or "").strip().lower() == "l":
                    continue  # drop low-confidence detections
                dedup = (round(float(row["latitude"]), 5), round(float(row["longitude"]), 5),
                         row["acq_date"], row.get("acq_time"), row.get("satellite"))
                if dedup in rows:
                    continue
                rows[dedup] = row
                got += 1
            time.sleep(1)  # politeness between calls
        per_product[product] = got
        print(f"{product}: {got} in-window detections")

    OUT.mkdir(parents=True, exist_ok=True)
    detections = list(rows.values())
    with (OUT / "firms_points.csv").open("w", newline="") as f:
        fields = ["latitude", "longitude", "bright_ti4", "scan", "track",
                  "acq_date", "acq_time", "satellite", "instrument",
                  "confidence", "version", "bright_ti5", "frp", "daynight"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(detections)

    def _frp(r):
        try:
            return float(r.get("frp") or -1)
        except (TypeError, ValueError):
            return -1.0

    thinned: dict[tuple, dict] = {}
    for r in detections:
        cell = (round(float(r["longitude"]) / THIN_CELL_DEG),
                round(float(r["latitude"]) / THIN_CELL_DEG))
        if cell not in thinned or _frp(r) > _frp(thinned[cell]):
            thinned[cell] = r
    feats = [{"type": "Feature",
              "properties": {"acq_date": r["acq_date"], "acq_time": r.get("acq_time"),
                             "satellite": r.get("satellite"),
                             "confidence": r.get("confidence"),
                             "bright_ti4": r.get("bright_ti4"), "frp": r.get("frp"),
                             "daynight": r.get("daynight")},
              "geometry": {"type": "Point",
                           "coordinates": [float(r["longitude"]), float(r["latitude"])]}} for r in thinned.values()]
    (OUT / "firms.geojson").write_text(json.dumps(
        {"type": "FeatureCollection",
         "properties": {"source": "NASA FIRMS VIIRS NRT", "window": [START.isoformat(), END.isoformat()],
                        "detections_total": len(detections), "thinned_to": len(feats),
                        "thin_cell_deg": THIN_CELL_DEG},
         "features": feats}))
    print(f"overlay thinned: {len(detections)} -> {len(feats)} points")

    to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32616", always_xy=True)
    # resolution=4 (16 pts/disc) keeps the 38 MB vertex storm down to ~6 MB
    # at 1.6% area cost; 5-decimal lon/lat (~1 m) trims JSON further.
    discs = [Point(*to_utm.transform(float(r["longitude"]), float(r["latitude"]))).buffer(BUFFER_M, resolution=4)
             for r in detections]
    union = unary_union(discs) if discs else None
    to_ll = Transformer.from_crs("EPSG:32616", "EPSG:4326", always_xy=True)
    from shapely import transform as shp_xy  # local import: heavy dep, only needed here
    from shapely.validation import make_valid
    import numpy as np

    def _t(coords):
        lon, lat = to_ll.transform(coords[:, 0], coords[:, 1])
        out = np.empty_like(coords)
        out[:, 0], out[:, 1] = np.round(lon, 5), np.round(lat, 5)
        return out

    # 1 m rounding can collapse spikes into self-intersections; repair so
    # downstream unary_union (change --truth scoring) never chokes.
    truth_ll = make_valid(shp_xy(union, _t)) if union is not None and not union.is_empty else None
    (OUT / "firms_truth.geojson").write_text(json.dumps(
        {"type": "FeatureCollection",
         "properties": {"source": "NASA FIRMS VIIRS NRT buffered union",
                        "detections": len(detections), "buffer_m": BUFFER_M,
                        "window": [START.isoformat(), END.isoformat()]},
         "features": [] if truth_ll is None else
         [{"type": "Feature", "properties": {"name": "FIRMS hotspot union"},
           "geometry": mapping(truth_ll)}]}))
    truth_km2 = 0.0 if union is None or union.is_empty else float(union.area / 1e6)
    print(f"detections: {len(detections)}, truth union: {truth_km2:.3f} km2")
    print("wrote firms_points.csv, firms.geojson, firms_truth.geojson")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
