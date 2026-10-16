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
CASES = {
    "snyder": ROOT / "outputs" / "snyder",
    "latvia": ROOT / "outputs" / "latvia",
}
OUT = CASES["snyder"]
WEB_DIST = ROOT / "web" / "dist"
LABELS = {"snyder": "Snyder Fire", "latvia": "Latvia flood"}

app = FastAPI(title="EchoLens", version="0.4.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _need(path: Path) -> Path:
    if not path.exists():
        raise HTTPException(404, f"missing {path.relative_to(ROOT)}")
    return path


def _case_dir(name: str) -> Path:
    if name not in CASES:
        raise HTTPException(404, f"unknown case {name}")
    return CASES[name]


def _media_prefix(name: str) -> str:
    return "/media" if name == "snyder" else "/media-latvia"


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "cases": {
            cid: {
                "ready": (path / "summary.json").exists(),
                "has_layers": (path / "layers" / "bounds.json").exists(),
            }
            for cid, path in CASES.items()
        },
    }


@app.get("/api/cases")
def list_cases():
    return {
        "default": "snyder",
        "cases": [
            {
                "id": cid,
                "label": LABELS[cid],
                "ready": (path / "summary.json").exists(),
            }
            for cid, path in CASES.items()
        ],
    }


@app.get("/api/case")
def case(name: str = "snyder"):
    folder = _case_dir(name)
    data = json.loads(_need(folder / "summary.json").read_text())
    data["case_id"] = name
    data["label"] = LABELS[name]
    prefix = _media_prefix(name)
    bounds_path = folder / "layers" / "bounds.json"
    data["bounds"] = json.loads(bounds_path.read_text()) if bounds_path.exists() else None
    data["layers"] = [
        {"id": "before", "label": "Before", "url": f"{prefix}/layers/before.png"},
        {"id": "after", "label": "After", "url": f"{prefix}/layers/after.png"},
        {"id": "change", "label": "Change · log-ratio", "url": f"{prefix}/layers/change.png"},
        {"id": "confidence", "label": "Confidence", "url": f"{prefix}/layers/confidence.png"},
    ]
    optical = folder / "layers" / "optical.png"
    if optical.exists():
        opt_meta = {}
        meta_path = folder / "layers" / "optical.json"
        if meta_path.exists():
            opt_meta = json.loads(meta_path.read_text())
        data["layers"].append(
            {
                "id": "optical",
                "label": "Optical",
                "url": f"{prefix}/layers/optical.png",
            }
        )
        data["optical"] = opt_meta
        data["has_optical"] = True
    else:
        data["has_optical"] = False
    data["has_perimeter"] = (folder / "perimeter_nifc.geojson").exists()
    return data


@app.get("/api/geojson/change")
def geojson_change(name: str = "snyder"):
    return FileResponse(_need(_case_dir(name) / "change.geojson"), media_type="application/geo+json")


@app.get("/api/geojson/perimeter")
def geojson_perimeter(name: str = "snyder"):
    path = _case_dir(name) / "perimeter_nifc.geojson"
    if not path.exists():
        return {"type": "FeatureCollection", "features": []}
    return FileResponse(path, media_type="application/geo+json")


OUT.mkdir(parents=True, exist_ok=True)
CASES["latvia"].mkdir(parents=True, exist_ok=True)
app.mount("/media-latvia", StaticFiles(directory=CASES["latvia"]), name="latvia")
app.mount("/media", StaticFiles(directory=OUT), name="media")

if WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="ui")
