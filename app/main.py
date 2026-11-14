#!/usr/bin/env python3
"""EchoLens API — serves the Snyder case GeoJSON and map layers. No live Earthdata."""

from __future__ import annotations

import json
import math
import struct
import zlib
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
    data["has_firms"] = (folder / "firms.geojson").exists()
    return data


OVERLAYS = {
    "ir": ["ir_nirops.geojson"],
    "lakes": ["lakes.geojson"],
    "emsr": ["emsr933.geojson", "emsr927.geojson"],
    "flood": ["flood_extent.geojson"],
    "rivers": ["rivers.geojson"],
    "firms": ["firms.geojson"],
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


# Confidence PNG buckets, decoded from the committed layers/confidence.png
# (rendered 1:1 through a ListedColormap; transparent bad pixels flatten to
# white figure background = outside the valid swath).
_CONF_NODATA = {(255, 255, 255), (17, 17, 17)}  # no data / invalid
_CONF_VALID = (74, 74, 74)  # valid background
_CONF_FLAG_LABELS = {
    # fire cases: level -> label
    "snyder": {(244, 211, 94): "Change (single-pol)",
               (238, 150, 75): "Change (dual-pol or truth overlap)",
               (193, 18, 31): "Change (dual-pol and truth overlap)"},
    "thunderbay": {(238, 150, 75): "Change (single-pol)",
                   (193, 18, 31): "Change (dual-pol agree)"},
    "coleman": {(238, 150, 75): "Change (single-pol)",
                (193, 18, 31): "Change (dual-pol agree)"},
    "secondflat": {(238, 150, 75): "Change (single-pol)",
                   (193, 18, 31): "Change (dual-pol agree)"},
    "spokane": {(238, 150, 75): "Change (single-pol)",
                (193, 18, 31): "Change (dual-pol agree)"},
    # flood cases: permanent water is masked, bright blue is change
    "latvia": {(61, 90, 128): "Permanent water (masked)",
               (0, 180, 216): "Change"},
    "nepal": {(61, 90, 128): "Permanent water (masked)",
              (0, 180, 216): "Change"},
    "crete": {(61, 90, 128): "Permanent water (masked)",
              (0, 180, 216): "Change"},
    "isaias": {(61, 90, 128): "Permanent water (masked)",
               (0, 180, 216): "Change"},
}


def _decode_png_rgb(path: Path) -> tuple[int, int, bytes]:
    """Minimal 8-bit RGB/RGBA PNG decoder (stdlib only). Returns (w, h, rgb)."""
    d = path.read_bytes()
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        raise HTTPException(500, f"not a PNG: {path.name}")
    pos, w, h, bitdepth, ctype, idat = 8, 0, 0, 0, 0, b""
    while pos < len(d):
        ln = struct.unpack(">I", d[pos:pos + 4])[0]
        typ, data = d[pos + 4:pos + 8], d[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, bitdepth, ctype, _, _, _ = struct.unpack(">IIBBBBB", data)
        elif typ == b"IDAT":
            idat += data
        pos += 12 + ln
    if bitdepth != 8 or ctype not in (2, 6):
        raise HTTPException(500, f"unsupported PNG {path.name}: depth={bitdepth} type={ctype}")
    ch = 3 if ctype == 2 else 4
    raw = zlib.decompress(idat)
    stride = w * ch
    out = bytearray(w * h * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if f == 1:
            for i in range(ch, stride):
                line[i] = (line[i] + line[i - ch]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                b, c = prev[i], prev[i - ch] if i >= ch else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        elif f != 0:
            raise HTTPException(500, f"unsupported PNG filter {f}")
        row = y * w * 3
        for x in range(w):
            o = x * ch
            out[row + x * 3:row + x * 3 + 3] = line[o:o + 3]
        prev = line
    return w, h, bytes(out)


@app.get("/api/confidence")
def confidence(name: str = "snyder"):
    """Pixel stats for the committed layers/confidence.png.

    Buckets: no-data (outside swath), valid background, and per-level
    flagged pixels with km² from the case pixel size."""
    folder = _case_dir(name)
    w, h, px = _decode_png_rgb(_need(folder / "layers" / "confidence.png"))
    try:
        pixel_m = float(json.loads((folder / "summary.json").read_text()).get("pixel_m", 80.0))
    except (OSError, ValueError):
        pixel_m = 80.0
    px_km2 = pixel_m * pixel_m / 1e6
    counts: dict[tuple[int, int, int], int] = {}
    for i in range(0, len(px), 3):
        rgb = (px[i], px[i + 1], px[i + 2])
        counts[rgb] = counts.get(rgb, 0) + 1
    total = w * h
    labels = _CONF_FLAG_LABELS.get(name, {})
    buckets = []
    for rgb, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if rgb in _CONF_NODATA:
            key, label = "nodata", "No data (outside swath)"
        elif rgb == _CONF_VALID:
            key, label = "valid", "Valid background"
        else:
            key, label = "flagged", labels.get(rgb, "Flagged")
        buckets.append({
            "key": key,
            "color": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
            "label": label,
            "pixels": n,
            "km2": round(n * px_km2, 3),
            "share": round(n / total, 4),
        })
    flagged_km2 = round(sum(b["km2"] for b in buckets if b["key"] == "flagged"), 3)
    valid_km2 = round(sum(b["km2"] for b in buckets if b["key"] == "valid"), 3)
    return {"case": name, "width": w, "height": h, "pixel_m": pixel_m,
            "total_km2": round(total * px_km2, 3),
            "valid_km2": valid_km2, "flagged_km2": flagged_km2,
            "buckets": buckets}


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
