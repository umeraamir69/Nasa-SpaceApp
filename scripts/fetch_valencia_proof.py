#!/usr/bin/env python3
"""Download official Valencia flood proof polygons (Copernicus EMSR935).

Writes outputs/valencia/emsr935.geojson (observedEvent flood water).
Prints the AOI bounds for the change-script crop box.
No Earthdata. No NISAR granules.
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
OUT = ROOT / "outputs" / "valencia"

UA = {"User-Agent": "EchoLens/1.0 (NASA Space Apps)"}

COPERNICUS = (
    ("AOI01", "https://rapidmapping.emergency.copernicus.eu/backend/EMSR935/AOI01/DEL_PRODUCT/EMSR935_AOI01_DEL_PRODUCT_v1.zip?type=vectors"),
)

CITE = {
    "event": "Copernicus EMS Rapid Mapping EMSR935 — Flood in Alicante-Valencia Regions, Spain (18–20 Oct 2026, Storm Adam)",
    "url": "https://mapping.emergency.copernicus.eu/activations/EMSR935/",
    "hdx": "https://data.humdata.org/dataset/esp-flood-emsr935",
    "note": "ObservedEvent is mapped flood water (delineation). La Safor / Marina Alta coastal districts.",
}


def fetch(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_layers(blob: bytes, aoi: str) -> tuple[list[dict], list | None]:
    feats, aoi_bounds = [], None
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        for name in zf.namelist():
            if not name.endswith(".json"):
                continue
            data = json.loads(zf.read(name))
            if "observedEventA" in name:
                for feat in data.get("features") or []:
                    props = dict(feat.get("properties") or {})
                    props["aoi"] = aoi
                    props["source"] = "copernicus_emsr935"
                    props["kind"] = "flood_water"
                    props["layer"] = Path(name).name
                    feats.append({"type": "Feature", "properties": props,
                                  "geometry": feat.get("geometry")})
            elif "areaOfInterestA" in name:
                xs, ys = [], []
                for feat in data.get("features") or []:
                    g = feat.get("geometry") or {}
                    coords = g.get("coordinates") or []
                    flat = json.dumps(coords).replace("[", " ").replace("]", " ").replace(",", " ").split()
                    nums = [float(v) for v in flat]
                    xs += nums[0::2]
                    ys += nums[1::2]
                if xs:
                    aoi_bounds = [min(xs), min(ys), max(xs), max(ys)]
    return feats, aoi_bounds


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
        got, bounds = load_layers(blob, aoi)
        print(f"  {len(got)} features ({len(blob)} bytes)")
        if bounds:
            print(f"  AOI bounds (w,s,e,n): {[round(v, 4) for v in bounds]}")
        all_feats.extend(got)
    if not all_feats:
        print("no Copernicus features", file=sys.stderr)
        return 1
    emsr = {"type": "FeatureCollection", "name": "emsr935_flood",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "properties": {"citation": CITE,
                           "when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                           "n_features": len(all_feats)},
            "features": all_feats}
    (OUT / "emsr935.geojson").write_text(json.dumps(emsr))
    print("wrote", OUT / "emsr935.geojson", len(all_feats), "features")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
