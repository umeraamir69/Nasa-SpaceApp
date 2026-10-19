#!/usr/bin/env python3
"""Download NIROPS airborne IR for the Snyder Fire and write GeoJSON.

Source: USDA Forest Service NIROPS, posted on NIFC incident FTP
  https://ftp.wildfire.gov/public/incident_specific_maps/rocky_mtn/2026/2026_Snyder/IR/

30 Jun 2026 = active heat (isolated points + scattered polygons).
7 Jul 2026 = heat perimeter, same day as the Sentinel-2 Optical chip.

This is not FIRMS. FIRMS is satellite hotspots; NIROPS is the aircraft IR map
incident command actually used.
"""

from __future__ import annotations

import json
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "snyder" / "ir_nirops.geojson"
KML_NS = {"k": "http://www.opengis.net/kml/2.2"}

BASE = "https://ftp.wildfire.gov/public/incident_specific_maps/rocky_mtn/2026/2026_Snyder/IR"
SCENES = (
    ("2026-06-30", f"{BASE}/20260630/20260630_Snyder_IR.kmz"),
    ("2026-07-07", f"{BASE}/20260707/20260707_Snyder_IR.kmz"),
)
KEEP = {"heat_perimeter", "scattered_heat", "isolated_heat", "possible_heat"}


def _kind(style_url: str) -> str:
    return (style_url or "").lstrip("#").split("-")[0]


def _coords(text: str) -> list[list[float]]:
    nums: list[float] = []
    for tok in (text or "").replace(",", " ").split():
        try:
            nums.append(float(tok))
        except ValueError:
            continue
    stride = 3 if len(nums) >= 3 and len(nums) % 3 == 0 else 2
    return [[nums[i], nums[i + 1]] for i in range(0, len(nums) - 1, stride)]


def _ring(elem: ET.Element) -> list[list[float]]:
    node = elem.find(".//k:coordinates", KML_NS)
    return _coords(node.text if node is not None else "")


def _geom(pm: ET.Element) -> dict | None:
    points = []
    polys = []
    for pt in pm.findall(".//k:Point", KML_NS):
        ring = _ring(pt)
        if ring:
            points.append(ring[0])
    for poly in pm.findall(".//k:Polygon", KML_NS):
        outer = poly.find(".//k:outerBoundaryIs", KML_NS)
        ring = _ring(outer if outer is not None else poly)
        if len(ring) >= 4:
            polys.append([ring])
    if len(points) == 1 and not polys:
        return {"type": "Point", "coordinates": points[0]}
    if len(points) > 1 and not polys:
        return {"type": "MultiPoint", "coordinates": points}
    if len(polys) == 1 and not points:
        return {"type": "Polygon", "coordinates": polys[0]}
    if len(polys) > 1 and not points:
        return {"type": "MultiPolygon", "coordinates": polys}
    if points or polys:
        geoms = []
        for p in points:
            geoms.append({"type": "Point", "coordinates": p})
        for p in polys:
            geoms.append({"type": "Polygon", "coordinates": p})
        return {"type": "GeometryCollection", "geometries": geoms}
    return None


def parse_kmz(raw: bytes, acq_date: str) -> list[dict]:
    with zipfile.ZipFile(BytesIO(raw)) as zf:
        name = next(n for n in zf.namelist() if n.lower().endswith(".kml"))
        kml = zf.read(name)
    root = ET.fromstring(kml)
    feats = []
    for pm in root.findall(".//k:Placemark", KML_NS):
        kind = _kind(pm.findtext("k:styleUrl", default="", namespaces=KML_NS) or "")
        if kind not in KEEP:
            continue
        geom = _geom(pm)
        if geom is None:
            continue
        feats.append(
            {
                "type": "Feature",
                "properties": {
                    "name": pm.findtext("k:name", default=kind, namespaces=KML_NS),
                    "kind": kind,
                    "acq_date": acq_date,
                    "source": "NIROPS airborne IR",
                },
                "geometry": geom,
            }
        )
    return feats


def main() -> int:
    features: list[dict] = []
    for acq_date, url in SCENES:
        with urlopen(url, timeout=60) as resp:
            raw = resp.read()
        chunk = parse_kmz(raw, acq_date)
        print(f"{acq_date}: {len(chunk)} features from {url.rsplit('/', 1)[-1]}")
        features.extend(chunk)
    if not features:
        raise SystemExit("NIROPS KMZ parsed to zero features")
    gj = {
        "type": "FeatureCollection",
        "name": "snyder_nirops_ir",
        "features": features,
        "metadata": {
            "source": "USDA Forest Service National Infrared Operations (NIROPS)",
            "ftp": BASE,
            "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "note": "30 Jun = active heat. 7 Jul = heat perimeter (same day as Sentinel-2 Optical). Not FIRMS.",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(gj))
    print(f"wrote {OUT}  ({len(features)} features)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
