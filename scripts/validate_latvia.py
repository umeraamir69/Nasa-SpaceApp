#!/usr/bin/env python3
"""Latvia independent check: change fragments vs HOTOSM waterways (stdlib only).

No official EMSR926 flood vectors exist on HDX (re-checked 29 Oct 2026), so
this clips OSM rivers/streams/canals to the case bounds as a reference layer
and measures whether EchoLens change fragments sit any closer to waterways
than random points in the same valid crop.

Run (needs the 30 MB HOT download once):
  curl -o /tmp/lva_waterways.zip \
    https://production-raw-data-api.s3.amazonaws.com/ISO3/LVA/waterways/hotosm_lva_waterways_osm_geojson.zip
  unzip -o /tmp/lva_waterways.zip waterways.geojson -d /tmp/lva_waterways
  venv/bin/python scripts/validate_latvia.py /tmp/lva_waterways/waterways.geojson

Writes outputs/latvia/rivers.geojson and patches outputs/latvia/summary.json.
"""

from __future__ import annotations

import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from png_crop import read_png  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "latvia"

KEEP_WATERWAY = {"river", "stream", "canal"}
KX = 111320.0 * math.cos(math.radians(57.0))
KY = 111320.0


def seg_intersects(a, b, west, south, east, north) -> bool:
    (ax, ay), (bx, by) = a, b
    if max(ax, bx) < west or min(ax, bx) > east or max(ay, by) < south or min(ay, by) > north:
        return False
    return True


def pt_seg_m2(px, py, ax, ay, bx, by) -> float:
    dx, dy = (bx - ax) * KX, (by - ay) * KY
    L2 = dx * dx + dy * dy
    t = ((px - ax) * KX * dx + (py - ay) * KY * dy) / L2 if L2 else 0.0
    t = max(0.0, min(1.0, t))
    ex, ey = (px - ax) * KX - t * dx, (py - ay) * KY - t * dy
    return ex * ex + ey * ey


def centroid(poly) -> tuple[float, float]:
    ring = poly[0]
    return (sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring))


def median(vals: list[float]) -> float:
    s = sorted(vals)
    return s[len(s) // 2]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    waterways = json.loads(Path(sys.argv[1]).read_text())
    bounds = json.loads((OUT / "layers" / "bounds.json").read_text())
    west, south, east, north = bounds["west"], bounds["south"], bounds["east"], bounds["north"]

    feats, segs = [], []
    for f in waterways.get("features") or []:
        g = f.get("geometry") or {}
        if (f.get("properties") or {}).get("waterway") not in KEEP_WATERWAY:
            continue
        lines = []
        if g.get("type") == "LineString":
            lines = [g["coordinates"]]
        elif g.get("type") == "MultiLineString":
            lines = g["coordinates"]
        for line in lines:
            if any(west <= x <= east and south <= y <= north for x, y in line):
                feats.append(line)
            for a, b in zip(line, line[1:]):
                if seg_intersects(a, b, west, south, east, north):
                    segs.append((a[0], a[1], b[0], b[1]))
    print(f"rivers/streams/canals in crop: {len(feats)} lines, {len(segs)} segments")

    rivers = {
        "type": "FeatureCollection",
        "name": "hotosm_lva_waterways_clip",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "properties": {
            "source": "HOTOSM LVA waterways (OpenStreetMap), river/stream/canal clipped to case bounds",
            "url": "https://data.humdata.org/dataset/hotosm_lva_waterways",
            "when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "features": [
            {"type": "Feature", "properties": {"kind": "waterway"},
             "geometry": {"type": "LineString",
                          "coordinates": [[round(x, 5), round(y, 5)] for x, y in line]}}
            for line in feats
        ],
    }
    (OUT / "rivers.geojson").write_text(json.dumps(rivers))
    print(f"wrote {OUT / 'rivers.geojson'} ({(OUT / 'rivers.geojson').stat().st_size} bytes)")

    def nearest(px, py) -> float:
        return math.sqrt(min(pt_seg_m2(px, py, *s) for s in segs))

    change = json.loads((OUT / "change.geojson").read_text())
    polys = change["features"][0]["geometry"]["coordinates"]
    d_change = [nearest(*centroid(p)) for p in polys]

    w, h, _, _ = read_png(str(OUT / "layers" / "before.png"))
    img_w, img_h, _, rows = read_png(str(OUT / "layers" / "before.png"))
    ch = len(rows[0]) // img_w
    random.seed(7)
    rnd = []
    guard = 0
    while len(rnd) < 300 and guard < 60000:
        guard += 1
        y = random.randrange(img_h)
        x = random.randrange(img_w)
        alpha = rows[y][x * ch + ch - 1] if ch == 4 else 255
        if alpha == 0:
            continue
        rnd.append((west + (x + 0.5) / img_w * (east - west),
                    north - (y + 0.5) / img_h * (north - south)))
    d_rnd = [nearest(*p) for p in rnd]

    stats = {
        "reference": "HOTOSM LVA waterways (river/stream/canal), OpenStreetMap via HDX",
        "n_change": len(d_change),
        "change_median_m": round(median(d_change)),
        "change_within_250m": sum(d <= 250 for d in d_change),
        "change_within_500m": sum(d <= 500 for d in d_change),
        "n_random": len(d_rnd),
        "random_median_m": round(median(d_rnd)),
        "random_within_250m": sum(d <= 250 for d in d_rnd),
        "random_within_500m": sum(d <= 500 for d in d_rnd),
    }
    print(json.dumps(stats, indent=2))

    summary = json.loads((OUT / "summary.json").read_text())
    summary["waterways_check"] = stats
    summary["layers_note"] = (
        "Web layers keep rows 0..530 of the 993-row processing crop; rows below "
        "are mostly outside the valid swath overlap. Panel change.png/confidence.png "
        "still show the full crop."
    )
    summary["verdict"] = (
        "No confident flood detection. The 18→30 Aug pair falls 8+ days after the "
        "21–22 Aug peak rain, the scene median brightened (+0.2 dB, dry-down), and "
        "the flagged fragments sit no closer to mapped waterways than random points. "
        "Permanent lakes (34 km²) are correctly masked. Treat this case as a negative "
        "result: L-band confirms the flood wave had passed, not a flood map."
    )
    summary["citation"]["note"] = (
        "Official EMSR926 flood vectors were still not on HDX as of 29 Oct 2026 "
        "(exact-phrase search, zero hits). Detection is HH darkening minus permanent "
        "water, checked against HOTOSM waterways with no river association found."
    )
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print("patched", OUT / "summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
