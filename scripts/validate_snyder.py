#!/usr/bin/env python3
"""Snyder independent check: EchoLens change vs NIROPS airborne IR (conda env).

Run:  .conda/env/bin/python scripts/validate_snyder.py
Patches outputs/snyder/summary.json with per-feature overlap stats.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from pyproj import Transformer
from shapely import transform as shp_xy
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "snyder"

# Equal-area for km² (CONUS Albers).
_to_m = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)


def area_km2(geom) -> float:
    def _project(coords):
        x, y = _to_m.transform(coords[:, 0], coords[:, 1])
        return np.column_stack([x, y])

    return shp_xy(geom, _project).area / 1e6


def main() -> int:
    change = json.loads((OUT / "change.geojson").read_text())
    ir = json.loads((OUT / "ir_nirops.geojson").read_text())
    change_geom = shape(change["features"][0]["geometry"])
    change_km2 = area_km2(change_geom)

    report = []
    for feat in ir["features"]:
        props = feat.get("properties") or {}
        g = shape(feat["geometry"]) if feat.get("geometry") else None
        row = {"kind": props.get("kind"), "acq_date": props.get("acq_date")}
        if g is None or g.is_empty:
            row["note"] = "empty geometry"
        elif g.geom_type == "MultiPoint":
            pts = list(g.geoms)
            inside = sum(1 for p in pts if change_geom.contains(p))
            row.update({"n_points": len(pts), "inside_change": inside,
                        "frac_inside": round(inside / len(pts), 3) if pts else 0.0})
        else:
            inter = change_geom.intersection(g)
            overlap = 0.0 if inter.is_empty else area_km2(inter)
            ir_km2 = area_km2(g)
            row.update({
                "ir_km2": round(ir_km2, 2),
                "overlap_km2": round(overlap, 2),
                "recall_vs_ir": round(overlap / ir_km2, 3) if ir_km2 else 0.0,
                "precision_vs_ir": round(overlap / change_km2, 3) if change_km2 else 0.0,
            })
        report.append(row)
        print(row)

    summary = json.loads((OUT / "summary.json").read_text())
    summary["nirops_check"] = report
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print("patched", OUT / "summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
