#!/usr/bin/env python3
"""Download the official Snyder Fire perimeter from NIFC WFIGS and write GeoJSON.

Source of the polygon: National Interagency Fire Center, Wildland Fire
Interagency Geospatial Services (WFIGS) year-to-date perimeters.
Incident: UniqueFireIdentifier 2026-UTDRD-005113 (UT-DRD-005113).

InciWeb (incident page, may be thin after closeout):
  https://inciweb.wildfire.gov/incident-information/utdrd-snyder
Official ops / IR maps:
  https://ftp.wildfire.gov/public/incident_specific_maps/rocky_mtn/2026/2026_Snyder/
FIRMS is hotspots (points), not this polygon — overlay those separately if
FIRMS_MAP_KEY is set.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ref" / "snyder" / "nifc_wfigs_snyder.geojson"

WFIGS = (
    "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/"
    "WFIGS_Interagency_Perimeters_YearToDate/FeatureServer/0/query"
)
FIRE_ID = "2026-UTDRD-005113"
FIRE_BBOX = (-109.22, 38.98, -108.80, 39.20)  # W,S,E,N — same as crop_snyder.py


def fetch_wfigs() -> dict:
    params = {
        "where": f"attr_UniqueFireIdentifier='{FIRE_ID}'",
        "outFields": ",".join(
            [
                "poly_IncidentName",
                "poly_GISAcres",
                "poly_DateCurrent",
                "attr_UniqueFireIdentifier",
                "attr_POOState",
                "attr_POOCounty",
                "attr_FireDiscoveryDateTime",
                "attr_IncidentName",
                "attr_CalculatedAcres",
                "attr_IncidentTypeCategory",
                "attr_PercentContained",
                "attr_ContainmentDateTime",
                "attr_InitialLatitude",
                "attr_InitialLongitude",
            ]
        ),
        "f": "geojson",
    }
    url = WFIGS + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = json.load(resp)
    if not data.get("features"):
        raise SystemExit(f"WFIGS returned no feature for {FIRE_ID}")
    return data


def fetch_firms_hotspots() -> dict | None:
    """Optional VIIRS archive points. Needs a free FIRMS map key in the env."""
    key = os.environ.get("FIRMS_MAP_KEY")
    if not key:
        return None
    west, south, east, north = FIRE_BBOX
    # Standard processing (archive) for the first 10 days after ignition.
    path = (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/"
        f"VIIRS_SNPP_SP/{west},{south},{east},{north}/10/2026-06-27"
    )
    with urllib.request.urlopen(path, timeout=60) as resp:
        text = resp.read().decode()
    lines = [ln for ln in text.strip().splitlines() if ln]
    if len(lines) < 2:
        print("FIRMS: no hotspots in window", file=sys.stderr)
        return {"type": "FeatureCollection", "features": []}
    header = lines[0].split(",")
    feats = []
    for ln in lines[1:]:
        row = dict(zip(header, ln.split(",")))
        try:
            lon = float(row["longitude"])
            lat = float(row["latitude"])
        except (KeyError, ValueError):
            continue
        feats.append(
            {
                "type": "Feature",
                "properties": {k: row.get(k) for k in ("acq_date", "confidence", "bright_ti4", "satellite")},
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        )
    out = ROOT / "ref" / "snyder" / "firms_viirs_snyder.geojson"
    gj = {
        "type": "FeatureCollection",
        "features": feats,
        "metadata": {
            "source": "NASA FIRMS VIIRS_SNPP_SP area API",
            "url": "https://firms.modaps.eosdis.nasa.gov/",
            "window": "2026-06-27 plus 10 days",
            "bbox": FIRE_BBOX,
        },
    }
    out.write_text(json.dumps(gj))
    print(f"FIRMS hotspots {len(feats)} → {out}")
    return gj


def main() -> int:
    data = fetch_wfigs()
    feat = data["features"][0]
    props = feat.get("properties") or {}
    props["source"] = "NIFC WFIGS Interagency Perimeters Year-to-Date"
    props["source_url"] = WFIGS.split("/query")[0]
    props["retrieved_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    props["inciweb"] = "https://inciweb.wildfire.gov/incident-information/utdrd-snyder"
    props["ops_maps"] = "https://ftp.wildfire.gov/public/incident_specific_maps/rocky_mtn/2026/2026_Snyder/"
    feat["properties"] = props
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data))
    acres = props.get("poly_GISAcres")
    print(f"wrote {OUT}")
    print(f"  {props.get('poly_IncidentName')}  {FIRE_ID}  GIS acres={acres}")
    fetch_firms_hotspots()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
