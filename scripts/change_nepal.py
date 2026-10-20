#!/usr/bin/env python3
"""Nepal Rasuwa GLOF GCOV change: HH log-ratio, layover corridor, EMSR927 overlay.

Snyder and Latvia map products are not touched. Writes outputs/nepal/.
Needs data/nepal/gcov/ 048_D_074 pair and python scripts/fetch_nepal_proof.py.
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
from rasterio.features import rasterize, shapes
from rasterio.transform import Affine
from scipy.ndimage import binary_opening, label, median_filter
from shapely import transform as shp_xy
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
GCOV = ROOT / "data" / "nepal" / "gcov"
CROP = ROOT / "data" / "nepal" / "crop"
OUT_PUB = ROOT / "outputs" / "nepal"
EMSR_PATH = OUT_PUB / "emsr927.geojson"
FLOOD_PATH = OUT_PUB / "flood_extent.geojson"

# Rasuwa / Bhote Koshi upper valley (AOI01–03). Tight on purpose — Himalayan layover.
GLOF_BBOX = (85.08, 27.90, 85.42, 28.30)
GRID = "science/LSAR/GCOV/grids/frequencyB"
THRESH_DB = 2.0
WATER_DB = -14.0
MEDIAN_SIZE = 3
MIN_PIXELS = 8
POL_CANDIDATES = ("HHHH", "HVHV")


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
        raise SystemExit("GLOF box is outside the raster")
    return slice(row.min(), row.max() + 1), slice(col.min(), col.max() + 1)


def load_npz_pair():
    before_p = CROP / "before.npz"
    after_p = CROP / "after.npz"
    if not (before_p.exists() and after_p.exists()):
        return None
    before = np.load(before_p, allow_pickle=False)
    after = np.load(after_p, allow_pickle=False)
    b_pols = [str(p) for p in before["pols"].tolist()]
    a_pols = [str(p) for p in after["pols"].tolist()]
    pols = [p for p in POL_CANDIDATES if p in b_pols and p in a_pols]
    if not pols:
        raise SystemExit(f"no common polarisation in crop npz: {b_pols} vs {a_pols}")

    def pack(z):
        out = {"mask": z["mask"]}
        for pol in pols:
            out[pol] = z[pol]
        return out

    return {
        "epsg": int(before["epsg"]),
        "x": before["x"],
        "y": before["y"],
        "dx": float(before["dx"]),
        "dy": float(before["dy"]),
        "pols": pols,
        "primary_pol": "HHHH" if "HHHH" in pols else pols[0],
        "before_date": str(before["date"]),
        "after_date": str(after["date"]),
        "before": pack(before),
        "after": pack(after),
        "before_path": str(before["granule"]),
        "after_path": str(after["granule"]),
    }


def load_gcov():
    cropped = load_npz_pair()
    if cropped is not None:
        return cropped

    files = sorted(p for p in GCOV.glob("*.h5") if "048_D_074" in p.name)
    if len(files) < 2:
        raise SystemExit(
            f"need data/nepal/crop/{{before,after}}.npz or 2 048_D_074 .h5 in {GCOV} — "
            "run python scripts/crop_nepal.py (small disk) or download_nepal.py"
        )
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
        before_keys = list(g.keys())
    with h5py.File(after_path, "r") as f:
        after_keys = list(f[GRID].keys())
    pols = [p for p in POL_CANDIDATES if p in before_keys and p in after_keys]
    if not pols:
        raise SystemExit(
            f"no common polarisation in {POL_CANDIDATES}; before={before_keys} after={after_keys}"
        )

    to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    west, south = to_utm.transform(GLOF_BBOX[0], GLOF_BBOX[1])
    east, north = to_utm.transform(GLOF_BBOX[2], GLOF_BBOX[3])
    rows, cols = crop_window(x, y, west, south, east, north)
    x = x[cols]
    y = y[rows]

    def read(path: Path):
        with h5py.File(path, "r") as f:
            g = f[GRID]
            out = {"mask": g["mask"][rows, cols]}
            for pol in pols:
                out[pol] = g[pol][rows, cols]
            return out

    return {
        "epsg": epsg,
        "x": x,
        "y": y,
        "dx": dx,
        "dy": dy,
        "pols": pols,
        "primary_pol": "HHHH" if "HHHH" in pols else pols[0],
        "before_date": before_date,
        "after_date": after_date,
        "before": read(before_path),
        "after": read(after_path),
        "before_path": before_path.name,
        "after_path": after_path.name,
    }


def load_ll_union(path: Path):
    if not path.exists():
        return None
    gj = json.loads(path.read_text())
    geoms = [shape(ft["geometry"]) for ft in gj.get("features") or [] if ft.get("geometry")]
    if not geoms:
        return None
    return unary_union(geoms)


def to_utm_geom(geom_ll, epsg: int):
    to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)

    def _t(coords):
        lon, lat = to_utm.transform(coords[:, 0], coords[:, 1])
        out = np.empty_like(coords)
        out[:, 0] = lon
        out[:, 1] = lat
        if coords.shape[1] > 2:
            out[:, 2:] = coords[:, 2:]
        return out

    return shp_xy(geom_ll, _t)


def affine_for(x: np.ndarray, y: np.ndarray, dx: float, dy: float) -> Affine:
    return Affine(dx, 0.0, float(x[0]) - dx / 2.0, 0.0, dy, float(y[0]) - dy / 2.0)


def raster_in_poly(geom_utm, shape_hw, transform: Affine) -> np.ndarray:
    if geom_utm is None or geom_utm.is_empty:
        return np.zeros(shape_hw, dtype=bool)
    return rasterize(
        [(geom_utm, 1)],
        out_shape=shape_hw,
        transform=transform,
        fill=0,
        dtype=np.uint8,
    ).astype(bool)


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
    if not EMSR_PATH.exists() or not FLOOD_PATH.exists():
        raise SystemExit("missing proof polygons — run python scripts/fetch_nepal_proof.py")

    src = load_gcov()
    pol = src["primary_pol"]
    x, y, dx, dy = src["x"], src["y"], src["dx"], src["dy"]
    transform = affine_for(x, y, dx, dy)
    hw = (y.size, x.size)

    flood_ll = load_ll_union(FLOOD_PATH)
    emsr_ll = load_ll_union(EMSR_PATH)
    flood_utm = to_utm_geom(flood_ll, src["epsg"]) if flood_ll is not None else None
    emsr_utm = to_utm_geom(emsr_ll, src["epsg"]) if emsr_ll is not None else None

    in_flood = raster_in_poly(flood_utm, hw, transform)
    in_emsr = raster_in_poly(emsr_utm, hw, transform)
    in_official = in_flood | in_emsr
    if not in_official.any():
        raise SystemExit("official EMSR927 / flood polygons miss this crop")

    valid = (
        product_valid(src["before"]["mask"])
        & product_valid(src["after"]["mask"])
        & np.isfinite(src["before"][pol])
        & np.isfinite(src["after"][pol])
        & (src["before"][pol] > 0)
        & (src["after"][pol] > 0)
    )

    db_before = despeckle(to_db(src["before"][pol]))
    db_after = despeckle(to_db(src["after"][pol]))
    db_before[~valid] = np.nan
    db_after[~valid] = np.nan
    diff = db_after - db_before
    diff[~valid] = np.nan

    # Gorge mixed pixels are not specular Latvia lakes (~-12 dB). Keep the
    # log-ratio, but require the pixel to sit inside Copernicus/HOT — layover
    # on the adjacent slopes would otherwise dominate.
    permanent = valid & (db_before <= WATER_DB) & (db_after <= WATER_DB)
    change = (
        valid
        & in_official
        & ~permanent
        & np.isfinite(diff)
        & (diff <= -THRESH_DB)
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
    conf[in_official & valid] = np.maximum(conf[in_official & valid], 1)
    conf[change] = 3

    pixel_km2 = abs(dx * dy) / 1e6
    area_km2 = float(change.sum() * pixel_km2)
    perm_km2 = float(permanent.sum() * pixel_km2)
    flood_km2 = float(in_flood.sum() * pixel_km2)
    tp = float((change & in_flood).sum())
    fp = float((change & ~in_flood).sum())
    fn = float((~change & in_flood & valid).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    union_utm, union_ll = polygonize(change, transform, src["epsg"])
    shapely_km2 = 0.0 if union_utm is None or union_utm.is_empty else float(union_utm.area / 1e6)

    cite = json.loads(EMSR_PATH.read_text()).get("properties", {}).get("citation") or {
        "event": "Copernicus EMS Rapid Mapping EMSR927",
        "url": "https://mapping.emergency.copernicus.eu/activations/EMSR927/",
    }

    OUT_PUB.mkdir(parents=True, exist_ok=True)
    save_panel(
        OUT_PUB / "change.png",
        diff,
        f"Nepal EMSR927  {pol} log-ratio (dB)  {src['before_date']} → {src['after_date']}\n"
        "blue = darker after · flagged pixels sit inside Copernicus/HOT polygons",
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
        "name": "echolens_nepal_gcov_glof",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "properties": {
            "area_km2": round(area_km2, 3),
            "polygon_area_km2": round(shapely_km2, 3),
            "permanent_water_km2": round(perm_km2, 3),
            "official_flood_km2_in_crop": round(flood_km2, 3),
            "precision_vs_flood": round(precision, 3),
            "recall_vs_flood": round(recall, 3),
            "pixel_m": abs(dx),
            "threshold_db": THRESH_DB,
            "primary_pol": pol,
            "event": "Nepal Rasuwa GLOF EMSR927",
            "before": src["before_date"],
            "after": src["after_date"],
            "citation": cite,
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
    finite = db_before[np.isfinite(db_before)]
    lo, hi = (float(np.percentile(finite, 2)), float(np.percentile(finite, 98))) if finite.size else (-25.0, 0.0)
    save_raw_layer(layer_dir / "before.png", db_before, "gray", lo, hi)
    save_raw_layer(layer_dir / "after.png", db_after, "gray", lo, hi)
    save_raw_layer(layer_dir / "change.png", diff, "RdBu_r", -6, 6)
    conf_layer = conf.astype(np.float32)
    conf_layer[conf == 0] = np.nan
    save_raw_layer(layer_dir / "confidence.png", conf_layer, conf_cmap, 0, 3)
    bounds = layer_bounds(x, y, dx, dy, src["epsg"])
    (layer_dir / "bounds.json").write_text(json.dumps(bounds, indent=2))

    summary = {
        "when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "case": "nepal",
        "event": "Nepal Rasuwa GLOF EMSR927",
        "before": src["before_date"],
        "after": src["after_date"],
        "before_file": src["before_path"],
        "after_file": src["after_path"],
        "grid": GRID,
        "pixel_m": abs(dx),
        "threshold_db": THRESH_DB,
        "water_db": WATER_DB,
        "despeckle": f"median {MEDIAN_SIZE}x{MEDIAN_SIZE}",
        "primary_pol": pol,
        "pols": src["pols"],
        "mask": "official EMSR927 + HOT flood (layover)",
        "hh_median_diff_db": float(np.nanmedian(diff[valid])) if valid.any() else None,
        "change_pixels": int(change.sum()),
        "area_km2": round(area_km2, 3),
        "permanent_water_km2": round(perm_km2, 3),
        "official_flood_km2_in_crop": round(flood_km2, 3),
        "emsr_pixels": int(in_emsr.sum()),
        "precision_vs_flood": round(precision, 3),
        "recall_vs_flood": round(recall, 3),
        "citation": cite,
    }
    (OUT_PUB / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
