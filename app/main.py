#!/usr/bin/env python3
"""EchoLens API — serves the Snyder case GeoJSON and map layers. No live Earthdata."""

from __future__ import annotations

import json
import math
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "snyder": ROOT / "outputs" / "snyder",
    "latvia": ROOT / "outputs" / "latvia",
    "nepal": ROOT / "outputs" / "nepal",
    "thunderbay": ROOT / "outputs" / "thunderbay",
    "crete": ROOT / "outputs" / "crete",
    "isaias": ROOT / "outputs" / "isaias",
    "coleman": ROOT / "outputs" / "coleman",
    "secondflat": ROOT / "outputs" / "secondflat",
    "spokane": ROOT / "outputs" / "spokane",
}
OUT = CASES["snyder"]
WEB_DIST = ROOT / "web" / "dist"
LABELS = {"snyder": "Snyder Fire", "latvia": "Latvia flood", "nepal": "Nepal GLOF",
          "thunderbay": "Thunder Bay 36", "crete": "Crete flood", "isaias": "Isaias surge",
          "coleman": "Coleman Creek", "secondflat": "Second Flat", "spokane": "Autumn Lane"}
MEDIA = {"snyder": "/media", "latvia": "/media-latvia", "nepal": "/media-nepal",
         "thunderbay": "/media-thunderbay", "crete": "/media-crete", "isaias": "/media-isaias",
         "coleman": "/media-coleman", "secondflat": "/media-secondflat", "spokane": "/media-spokane"}

app = FastAPI(title="EchoLens", version="0.5.0")
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
    return MEDIA[name]


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
    data["has_ir"] = (folder / "ir_nirops.geojson").exists()
    data["has_lakes"] = (folder / "lakes.geojson").exists()
    data["has_emsr"] = (folder / "emsr927.geojson").exists() or (
        folder / "emsr933.geojson"
    ).exists()
    data["has_flood_extent"] = (folder / "flood_extent.geojson").exists()
    data["has_rivers"] = (folder / "rivers.geojson").exists()
    return data


OVERLAYS = {
    "ir": ["ir_nirops.geojson"],
    "lakes": ["lakes.geojson"],
    "emsr": ["emsr933.geojson", "emsr927.geojson"],
    "flood": ["flood_extent.geojson"],
    "rivers": ["rivers.geojson"],
}


def _overlay_file(folder: Path, layer: str) -> Path:
    for name in OVERLAYS[layer]:
        if (folder / name).exists():
            return folder / name
    return folder / OVERLAYS[layer][0]


def _ring_area_km2(ring) -> float:
    """Equirectangular shoelace area of a lon/lat ring, in km² (~1% error)."""
    if len(ring) < 4:
        return 0.0
    mean_lat = sum(p[1] for p in ring) / len(ring)
    kx = 111.32 * math.cos(math.radians(mean_lat))
    ky = 111.32
    area = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        area += (x2 - x1) * (y2 + y1) / 2.0
    return abs(area) * kx * ky


def _explode_change(fc: dict) -> dict:
    """Split a single union-MultiPolygon change feature into per-fragment
    Polygon features with part numbers and areas, for the map inspector."""
    feats = []
    for feat in fc.get("features") or []:
        geom = feat.get("geometry") or {}
        if geom.get("type") == "MultiPolygon":
            polys = geom["coordinates"]
        elif geom.get("type") == "Polygon":
            polys = [geom["coordinates"]]
        else:
            feats.append(feat)
            continue
        n = len(polys)
        for i, poly in enumerate(polys, 1):
            outer = poly[0] if poly else []
            holes = poly[1:] if len(poly) > 1 else []
            area = _ring_area_km2(outer) - sum(_ring_area_km2(h) for h in holes)
            props = dict(feat.get("properties") or {})
            props.update({"part": f"{i}/{n}", "area_km2": round(max(area, 0.0), 3)})
            feats.append({"type": "Feature", "properties": props,
                          "geometry": {"type": "Polygon", "coordinates": poly}})
    out = dict(fc)
    out["features"] = feats
    return out


@app.get("/api/geojson/change")
def geojson_change(name: str = "snyder", explode: bool = True):
    fc = json.loads(_need(_case_dir(name) / "change.geojson").read_text())
    if explode:
        fc = _explode_change(fc)
    return JSONResponse(fc)


@app.get("/api/geojson/perimeter")
def geojson_perimeter(name: str = "snyder"):
    path = _case_dir(name) / "perimeter_nifc.geojson"
    if not path.exists():
        return {"type": "FeatureCollection", "features": []}
    return FileResponse(path, media_type="application/geo+json")


@app.get("/api/geojson/overlay")
def geojson_overlay(name: str = "snyder", layer: str = "ir"):
    if layer not in OVERLAYS:
        raise HTTPException(404, f"unknown overlay {layer}")
    path = _overlay_file(_case_dir(name), layer)
    if not path.exists():
        return {"type": "FeatureCollection", "features": []}
    return FileResponse(path, media_type="application/geo+json")


OUT.mkdir(parents=True, exist_ok=True)
CASES["latvia"].mkdir(parents=True, exist_ok=True)
CASES["nepal"].mkdir(parents=True, exist_ok=True)
CASES["thunderbay"].mkdir(parents=True, exist_ok=True)
CASES["crete"].mkdir(parents=True, exist_ok=True)
CASES["isaias"].mkdir(parents=True, exist_ok=True)
app.mount("/media-latvia", StaticFiles(directory=CASES["latvia"]), name="latvia")
app.mount("/media-nepal", StaticFiles(directory=CASES["nepal"]), name="nepal")
app.mount("/media-thunderbay", StaticFiles(directory=CASES["thunderbay"]), name="thunderbay")
app.mount("/media-crete", StaticFiles(directory=CASES["crete"]), name="crete")
app.mount("/media-isaias", StaticFiles(directory=CASES["isaias"]), name="isaias")
app.mount("/media-coleman", StaticFiles(directory=CASES["coleman"]), name="coleman")
app.mount("/media-secondflat", StaticFiles(directory=CASES["secondflat"]), name="secondflat")
app.mount("/media-spokane", StaticFiles(directory=CASES["spokane"]), name="spokane")
app.mount("/media", StaticFiles(directory=OUT), name="media")

if WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="ui")
