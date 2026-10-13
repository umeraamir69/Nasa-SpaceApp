#!/usr/bin/env python3
"""EchoLens API — serves the Snyder case GeoJSON and map layers. No live Earthdata."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "snyder"
WEB_DIST = ROOT / "web" / "dist"

app = FastAPI(title="EchoLens", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _need(path: Path) -> Path:
    if not path.exists():
        raise HTTPException(404, f"missing {path.relative_to(ROOT)} — run python scripts/change_snyder.py")
    return path


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "case": "snyder",
        "has_geojson": (OUT / "change.geojson").exists(),
        "has_layers": (OUT / "layers" / "bounds.json").exists(),
    }


@app.get("/api/case")
def case():
    data = json.loads(_need(OUT / "summary.json").read_text())
    bounds_path = OUT / "layers" / "bounds.json"
    data["bounds"] = json.loads(bounds_path.read_text()) if bounds_path.exists() else None
    data["layers"] = [
        {"id": "before", "label": "Before · 17 Jun HVHV", "url": "/media/layers/before.png"},
        {"id": "after", "label": "After · 23 Jul HVHV", "url": "/media/layers/after.png"},
        {"id": "change", "label": "Change · log-ratio", "url": "/media/layers/change.png"},
        {"id": "confidence", "label": "Confidence", "url": "/media/layers/confidence.png"},
    ]
    optical = OUT / "layers" / "optical.png"
    if optical.exists():
        opt_meta = {}
        meta_path = OUT / "layers" / "optical.json"
        if meta_path.exists():
            opt_meta = json.loads(meta_path.read_text())
        data["layers"].append(
            {
                "id": "optical",
                "label": "Optical · 7 Jul Sentinel-2 (cloud)",
                "url": "/media/layers/optical.png",
            }
        )
        data["optical"] = opt_meta
        data["has_optical"] = True
    else:
        data["has_optical"] = False
    return data


@app.get("/api/geojson/change")
def geojson_change():
    return FileResponse(_need(OUT / "change.geojson"), media_type="application/geo+json")


@app.get("/api/geojson/perimeter")
def geojson_perimeter():
    return FileResponse(_need(OUT / "perimeter_nifc.geojson"), media_type="application/geo+json")


OUT.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=OUT), name="media")

if WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="ui")
