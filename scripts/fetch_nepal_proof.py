#!/usr/bin/env python3
"""Download official Nepal GLOF proof polygons (Copernicus EMSR927 + HOT flood).

Writes outputs/nepal/emsr927.geojson and outputs/nepal/flood_extent.geojson.
No Earthdata. Does not download NISAR granules.
"""

from __future__ import annotations

import json
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "nepal"

UA = {"User-Agent": "EchoLens/1.0 (NASA Space Apps)"}

# Latest GRA / GRA_MONIT01 vector zips from HDX npl-flood-emsr927.
COPERNICUS = (
    (
        "AOI01",
        "https://rapidmapping.emergency.copernicus.eu/backend/EMSR927/AOI01/GRA_PRODUCT/EMSR927_AOI01_GRA_PRODUCT_v1.zip?type=vectors",
    ),
    (
        "AOI02",
        "https://rapidmapping.emergency.copernicus.eu/backend/EMSR927/AOI02/GRA_PRODUCT/EMSR927_AOI02_GRA_PRODUCT_v2.zip?type=vectors",
    ),
    (
        "AOI03",
        "https://rapidmapping.emergency.copernicus.eu/backend/EMSR927/AOI03/GRA_MONIT01/EMSR927_AOI03_GRA_MONIT01_v1.zip?type=vectors",
    ),
    (
        "AOI05",
        "https://rapidmapping.emergency.copernicus.eu/backend/EMSR927/AOI05/GRA_MONIT01/EMSR927_AOI05_GRA_MONIT01_v2.zip?type=vectors",
    ),
)

HOT_FLOOD = "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL/combined/hot_flood_npl_flood_extent.geojson"

CITE = {
    "event": "Copernicus EMS Rapid Mapping EMSR927 + HOT flood extent 27 Aug 2026",
    "url": "https://mapping.emergency.copernicus.eu/activations/EMSR927/",
    "hdx": "https://data.humdata.org/dataset/npl-flood-emsr927",
    "hot_flood": HOT_FLOOD,
    "unosat_mudflow": "https://data.humdata.org/dataset/mudflow-rockflow-extent-as-of-26-27-august-2026-in-rasuwa-district-bagmati-province-nepal",
    "unosat_barrier_lakes": "https://data.humdata.org/dataset/newly-formed-barrier-lakes-following-an-ice-rock-avalanche-in-rasuwa-district-nepal-as-of-",
    "note": "Copernicus GRA observedEvent is mapped landslides along the GLOF path. Standing water is the HOT 27 Aug flood polygon (Bhote Koshi / Trishuli). UNOSAT published mudflow and barrier-lake FileGDBs for the same dates.",
}


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_observed_from_zip(blob: bytes, aoi: str) -> list[dict]:
    feats = []
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        names = [n for n in zf.namelist() if n.endswith(".json") and "observedEvent" in n]
        if not names:
            return feats
        data = json.loads(zf.read(names[0]))
        for feat in data.get("features") or []:
            props = dict(feat.get("properties") or {})
            props["aoi"] = aoi
            props["source"] = "copernicus_emsr927"
            props["kind"] = "landslide"
            props["layer"] = Path(names[0]).name
            feats.append({"type": "Feature", "properties": props, "geometry": feat.get("geometry")})
    return feats


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    emsr_feats = []
    for aoi, url in COPERNICUS:
        print(f"Copernicus {aoi} …")
        try:
            blob = fetch(url)
        except Exception as exc:
            print(f"  fail {exc}", file=sys.stderr)
            continue
        got = load_observed_from_zip(blob, aoi)
        print(f"  {len(got)} observedEvent features ({len(blob)} bytes)")
        emsr_feats.extend(got)

    if not emsr_feats:
        print("no Copernicus observedEvent features", file=sys.stderr)
        return 1

    emsr = {
        "type": "FeatureCollection",
        "name": "emsr927_observed_event",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "properties": {
            "citation": CITE,
            "when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "n_features": len(emsr_feats),
        },
        "features": emsr_feats,
    }
    (OUT / "emsr927.geojson").write_text(json.dumps(emsr))
    print("wrote", OUT / "emsr927.geojson", len(emsr_feats), "features")

    print("HOT flood extent …")
    hot = json.loads(fetch(HOT_FLOOD).decode())
    feats = []
    for feat in hot.get("features") or []:
        props = dict(feat.get("properties") or {})
        props["source"] = "hot_flood_extent"
        props["kind"] = "flood"
        props["observed"] = "2026-08-27"
        feats.append({"type": "Feature", "properties": props, "geometry": feat.get("geometry")})
    flood = {
        "type": "FeatureCollection",
        "name": "hot_npl_flood_extent_20260827",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "properties": {
            "citation": CITE,
            "when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "n_features": len(feats),
        },
        "features": feats,
    }
    (OUT / "flood_extent.geojson").write_text(json.dumps(flood))
    print("wrote", OUT / "flood_extent.geojson", len(feats), "features")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
