#!/usr/bin/env python3
"""Download official Crete flood proof polygons (Copernicus EMSR933).

Writes outputs/crete/emsr933.geojson (observedEvent flood water +
maximumFloodExtent). No Earthdata. No NISAR granules.
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
OUT = ROOT / "outputs" / "crete"

UA = {"User-Agent": "EchoLens/1.0 (NASA Space Apps)"}

# Latest DELINEATION/MONITOR vector zips, verified 30 Oct 2026 (302 → S3).
COPERNICUS = (
    ("AOI01", "https://rapidmapping.emergency.copernicus.eu/backend/EMSR933/AOI01/DEL_MONIT01/EMSR933_AOI01_DEL_MONIT01_v2.zip?type=vectors"),
    ("AOI03", "https://rapidmapping.emergency.copernicus.eu/backend/EMSR933/AOI03/DEL_MONIT02/EMSR933_AOI03_DEL_MONIT02_v1.zip?type=vectors"),
    ("AOI04", "https://rapidmapping.emergency.copernicus.eu/backend/EMSR933/AOI04/DEL_MONIT01/EMSR933_AOI04_DEL_MONIT01_v2.zip?type=vectors"),
)

CITE = {
    "event": "Copernicus EMS Rapid Mapping EMSR933 — Flood in Crete, Greece (2–4 Oct 2026)",
    "url": "https://mapping.emergency.copernicus.eu/activations/EMSR933/",
    "note": "ObservedEvent is mapped flood water; maximumFloodExtent is the modelled outer extent. Lasithi Plateau lake, Ierapetra coast, Mylopotamos.",
}


def fetch(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_layers(blob: bytes, aoi: str) -> list[dict]:
    feats = []
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        for name in zf.namelist():
            if not name.endswith(".json"):
                continue
            if "observedEventA" in name:
                kind = "flood_water"
            elif "maximumFloodExtentA" in name:
                kind = "flood_extent"
            else:
                continue
            data = json.loads(zf.read(name))
            for feat in data.get("features") or []:
                props = dict(feat.get("properties") or {})
                props["aoi"] = aoi
                props["source"] = "copernicus_emsr933"
                props["kind"] = kind
                props["layer"] = Path(name).name
                feats.append({"type": "Feature", "properties": props,
                              "geometry": feat.get("geometry")})
    return feats


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    all_feats = []
    for aoi, url in COPERNICUS:
        print(f"Copernicus {aoi} …")
        try:
            blob = fetch(url)
        except Exception as exc:
            print(f"  fail {exc}", file=sys.stderr)
            continue
        got = load_layers(blob, aoi)
        print(f"  {len(got)} features ({len(blob)} bytes)")
        all_feats.extend(got)
    if not all_feats:
        print("no Copernicus features", file=sys.stderr)
        return 1
    emsr = {"type": "FeatureCollection", "name": "emsr933_flood",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "properties": {"citation": CITE,
                           "when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                           "n_features": len(all_feats)},
            "features": all_feats}
    (OUT / "emsr933.geojson").write_text(json.dumps(emsr))
    print("wrote", OUT / "emsr933.geojson", len(all_feats), "features")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
