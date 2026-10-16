#!/usr/bin/env python3
"""Latvia flood GCOV change: despeckle, HH log-ratio, permanent-water mask.

Snyder map products are not touched. Writes outputs/latvia/.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from pyproj import Transformer
from rasterio.features import shapes
from rasterio.transform import Affine
from scipy.ndimage import binary_opening, label, median_filter
from shapely import transform as shp_xy
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
GCOV = ROOT / "data" / "latvia" / "gcov"
OUT_PUB = ROOT / "outputs" / "latvia"

# Western Latvia / Lithuania border around EMSR926 centre 22.21E, 56.87N.
FLOOD_BBOX = (21.70, 56.55, 23.00, 57.25)
GRID = "science/LSAR/GCOV/grids/frequencyB"
THRESH_DB = 2.0
WATER_DB = -14.0
AFTER_WATER_DB = -12.0
MEDIAN_SIZE = 3
MIN_PIXELS = 8


def to_db(power: np.ndarray) -> np.ndarray:
    valid = np.isfinite(power) & (power > 0)
    out = np.full(power.shape, np.nan, dtype=np.float32)
    out[valid] = (10.0 * np.log10(power[valid])).astype(np.float32)
    return out


def product_valid(mask: np.ndarray) -> np.ndarray:
    return (mask != 0) & (mask != 255)


def despeckle(db: np.ndarray, size: int = MEDIAN_SIZE) -> np.ndarray:
    fill = np.nanmedian(db)
    work = np.where(np.isfinite(db), db, fill).astype(np.float32)
    out = median_filter(work, size=size)
    out[~np.isfinite(db)] = np.nan
    return out.astype(np.float32)


def crop_window(x: np.ndarray, y: np.ndarray, west: float, south: float, east: float, north: float):
    col = np.where((x >= west) & (x <= east))[0]
    row = np.where((y >= south) & (y <= north))[0]
    if col.size == 0 or row.size == 0:
        raise SystemExit("flood box is outside the raster")
    return slice(row.min(), row.max() + 1), slice(col.min(), col.max() + 1)


def load_gcov():
    files = sorted(p for p in GCOV.glob("*.h5") if "080_D_059" in p.name)
    if len(files) < 2:
        raise SystemExit(f"need 2 080_D_059 .h5 in {GCOV} — run python scripts/download_latvia.py")
    dated = []
    for path in files:
        with h5py.File(path, "r") as f:
            start = f["science/LSAR/identification/zeroDopplerStartTime"][()]
            if isinstance(start, bytes):
                start = start.decode()
            dated.append((start[:10], path))
    dated.sort()
    before_date, before_path = dated[0]
    after_date, after_path = dated[-1]

    with h5py.File(before_path, "r") as f:
        g = f[GRID]
        epsg = int(g["projection"][()])
        x = g["xCoordinates"][:]
        y = g["yCoordinates"][:]
        dx = float(g["xCoordinateSpacing"][()])
        dy = float(g["yCoordinateSpacing"][()])

    to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    west, south = to_utm.transform(FLOOD_BBOX[0], FLOOD_BBOX[1])
    east, north = to_utm.transform(FLOOD_BBOX[2], FLOOD_BBOX[3])
    rows, cols = crop_window(x, y, west, south, east, north)
    x = x[cols]
    y = y[rows]

    def read(path: Path):
        with h5py.File(path, "r") as f:
            g = f[GRID]
            return {
                "HHHH": g["HHHH"][rows, cols],
                "HVHV": g["HVHV"][rows, cols],
                "mask": g["mask"][rows, cols],
            }

    return {
        "epsg": epsg,
        "x": x,
        "y": y,
        "dx": dx,
        "dy": dy,
        "before_date": before_date,
        "after_date": after_date,
        "before": read(before_path),
        "after": read(after_path),
        "before_path": before_path.name,
        "after_path": after_path.name,
    }


def affine_for(x: np.ndarray, y: np.ndarray, dx: float, dy: float) -> Affine:
    return Affine(dx, 0.0, float(x[0]) - dx / 2.0, 0.0, dy, float(y[0]) - dy / 2.0)


def polygonize(mask: np.ndarray, transform: Affine, epsg: int):
    polys = [shape(geom) for geom, val in shapes(mask.astype(np.uint8), mask=mask, transform=transform) if val == 1]
    union = unary_union(polys) if polys else None
    if union is None:
        from shapely.geometry import GeometryCollection

        return GeometryCollection(), GeometryCollection()
    to_ll = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)

    def _t(coords):
        lon, lat = to_ll.transform(coords[:, 0], coords[:, 1])
        out = np.empty_like(coords)
        out[:, 0] = lon
        out[:, 1] = lat
        if coords.shape[1] > 2:
            out[:, 2:] = coords[:, 2:]
        return out

    return union, shp_xy(union, _t)


def save_raw_layer(path: Path, arr, cmap, vmin, vmax) -> None:
    h, w = arr.shape
    fig = plt.figure(figsize=(w / 100.0, h / 100.0), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor((0, 0, 0, 0))
    cm = plt.get_cmap(cmap).copy() if isinstance(cmap, str) else cmap
    cm.set_bad((0, 0, 0, 0))
    ax.imshow(arr, cmap=cm, vmin=vmin, vmax=vmax, origin="upper", interpolation="nearest")
    ax.set_axis_off()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100, pad_inches=0, transparent=True)
    plt.close(fig)
    print("wrote", path)


def save_panel(path: Path, arr, title, cmap, vmin, vmax, cbar="dB"):
    fig, ax = plt.subplots(figsize=(7.2, 6.2), dpi=140)
    im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax, origin="upper")
    ax.set_title(title)
    ax.set_axis_off()
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label=cbar)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def layer_bounds(x: np.ndarray, y: np.ndarray, dx: float, dy: float, epsg: int) -> dict:
    to_ll = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    west = float(x[0] - dx / 2.0)
    east = float(x[-1] + dx / 2.0)
    north = float(y[0] - dy / 2.0)
    south = float(y[-1] + dy / 2.0)
    w1, n1 = to_ll.transform(west, north)
    e1, s1 = to_ll.transform(east, south)
    return {
        "south": s1,
        "west": w1,
        "north": n1,
        "east": e1,
        "epsg": epsg,
        "pixel_m": abs(dx),
        "width": int(x.size),
        "height": int(y.size),
    }


def main() -> int:
    src = load_gcov()
    x, y, dx, dy = src["x"], src["y"], src["dx"], src["dy"]
    transform = affine_for(x, y, dx, dy)

    valid = (
        product_valid(src["before"]["mask"])
        & product_valid(src["after"]["mask"])
        & np.isfinite(src["before"]["HHHH"])
        & np.isfinite(src["after"]["HHHH"])
        & (src["before"]["HHHH"] > 0)
        & (src["after"]["HHHH"] > 0)
    )

    hh_before = despeckle(to_db(src["before"]["HHHH"]))
    hh_after = despeckle(to_db(src["after"]["HHHH"]))
    hh_before[~valid] = np.nan
    hh_after[~valid] = np.nan
    diff = hh_after - hh_before
    diff[~valid] = np.nan

    # Permanent lakes: dark on both dates. New flood: darker after, and after looks like water.
    permanent = valid & (hh_before <= WATER_DB) & (hh_after <= WATER_DB)
    change = (
        valid
        & ~permanent
        & np.isfinite(diff)
        & (diff <= -THRESH_DB)
        & (hh_after <= AFTER_WATER_DB)
    )
    change = binary_opening(change, structure=np.ones((3, 3), dtype=bool))
    labeled, nlab = label(change)
    keep = np.zeros_like(change)
    for i in range(1, nlab + 1):
        blob = labeled == i
        if int(blob.sum()) >= MIN_PIXELS:
            keep |= blob
    change = keep

    conf = np.zeros(change.shape, dtype=np.uint8)
    conf[valid] = 1
    conf[permanent] = 2
    conf[change] = 3

    pixel_km2 = abs(dx * dy) / 1e6
    area_km2 = float(change.sum() * pixel_km2)
    perm_km2 = float(permanent.sum() * pixel_km2)
    union_utm, union_ll = polygonize(change, transform, src["epsg"])
    shapely_km2 = 0.0 if union_utm is None or union_utm.is_empty else float(union_utm.area / 1e6)

    OUT_PUB.mkdir(parents=True, exist_ok=True)
    save_panel(
        OUT_PUB / "change.png",
        diff,
        f"Latvia EMSR926  HH log-ratio (dB)  {src['before_date']} → {src['after_date']}\n"
        "blue = darker after (new water) · permanent lakes masked",
        "RdBu_r",
        -6,
        6,
    )
    conf_cmap = ListedColormap(["#111111", "#4a4a4a", "#3d5a80", "#00b4d8"])
    save_panel(
        OUT_PUB / "confidence.png",
        conf.astype(np.float32),
        "0 none · 1 valid · 2 permanent water · 3 new water",
        conf_cmap,
        0,
        3,
        cbar="level",
    )

    change_fc = {
        "type": "FeatureCollection",
        "name": "echolens_latvia_gcov_flood",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "properties": {
            "area_km2": round(area_km2, 3),
            "polygon_area_km2": round(shapely_km2, 3),
            "permanent_water_km2": round(perm_km2, 3),
            "pixel_m": abs(dx),
            "threshold_db": THRESH_DB,
            "primary_pol": "HHHH",
            "event": "Latvia–Lithuania flood EMSR926",
            "before": src["before_date"],
            "after": src["after_date"],
            "citation": {
                "event": "Copernicus EMS Rapid Mapping EMSR926",
                "url": "https://mapping.emergency.copernicus.eu/activations/EMSR926/",
                "note": "Official flood vectors were not in HDX on 15 Oct 2026. Detection is HH darkening minus permanent water.",
            },
        },
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "EchoLens new water", "area_km2": round(shapely_km2, 3)},
                "geometry": None if union_ll is None or union_ll.is_empty else mapping(union_ll),
            }
        ],
    }
    (OUT_PUB / "change.geojson").write_text(json.dumps(change_fc))

    layer_dir = OUT_PUB / "layers"
    finite = hh_before[np.isfinite(hh_before)]
    lo, hi = (float(np.percentile(finite, 2)), float(np.percentile(finite, 98))) if finite.size else (-25.0, 0.0)
    save_raw_layer(layer_dir / "before.png", hh_before, "gray", lo, hi)
    save_raw_layer(layer_dir / "after.png", hh_after, "gray", lo, hi)
    save_raw_layer(layer_dir / "change.png", diff, "RdBu_r", -6, 6)
    conf_layer = conf.astype(np.float32)
    conf_layer[conf == 0] = np.nan
    save_raw_layer(layer_dir / "confidence.png", conf_layer, conf_cmap, 0, 3)
    bounds = layer_bounds(x, y, dx, dy, src["epsg"])
    (layer_dir / "bounds.json").write_text(json.dumps(bounds, indent=2))

    summary = {
        "when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "case": "latvia",
        "event": "Latvia–Lithuania flood EMSR926",
        "before": src["before_date"],
        "after": src["after_date"],
        "before_file": src["before_path"],
        "after_file": src["after_path"],
        "grid": GRID,
        "pixel_m": abs(dx),
        "threshold_db": THRESH_DB,
        "water_db": WATER_DB,
        "after_water_db": AFTER_WATER_DB,
        "despeckle": f"median {MEDIAN_SIZE}x{MEDIAN_SIZE}",
        "primary_pol": "HHHH",
        "hh_median_diff_db": float(np.nanmedian(diff[valid])) if valid.any() else None,
        "change_pixels": int(change.sum()),
        "area_km2": round(area_km2, 3),
        "permanent_water_km2": round(perm_km2, 3),
        "citation": change_fc["properties"]["citation"],
    }
    (OUT_PUB / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
