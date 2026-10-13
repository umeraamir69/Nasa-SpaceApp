#!/usr/bin/env python3
"""Offline Snyder GCOV change: despeckle, log-ratio, product mask, NIFC overlay.

Writes a change PNG, a confidence PNG, and GeoJSON with km².
If a GUNW coherence file is in data/snyder/gunw/, it is a second vote.
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
GCOV = ROOT / "data" / "snyder" / "gcov"
GUNW = ROOT / "data" / "snyder" / "gunw"
PERIM = ROOT / "ref" / "snyder" / "nifc_wfigs_snyder.geojson"
OUT_DATA = ROOT / "data" / "snyder" / "change"
OUT_PUB = ROOT / "outputs" / "snyder"

# Westwater / Snyder Mesa / Glade Park. Same box as crop_snyder.py.
FIRE_BBOX = (-109.22, 38.98, -108.80, 39.20)
GRID = "science/LSAR/GCOV/grids/frequencyB"
THRESH_DB = 1.5
MEDIAN_SIZE = 3
MIN_PIXELS = 8  # 8 × 80 m × 80 m ≈ 5 ha
GUNW_COH_LOW = 0.40  # co-event HH coherence below this is a second vote


def to_db(power: np.ndarray) -> np.ndarray:
    valid = np.isfinite(power) & (power > 0)
    out = np.full(power.shape, np.nan, dtype=np.float32)
    out[valid] = (10.0 * np.log10(power[valid])).astype(np.float32)
    return out


def product_valid(mask: np.ndarray) -> np.ndarray:
    """GCOV mask: 255 fill, 0 = not fully focused, else subswath number."""
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
        raise SystemExit("fire box is outside the raster")
    return slice(row.min(), row.max() + 1), slice(col.min(), col.max() + 1)


def load_gcov():
    files = sorted(GCOV.glob("*.h5"))
    if len(files) < 2:
        raise SystemExit(f"need 2 .h5 in {GCOV}")
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
    west, south = to_utm.transform(FIRE_BBOX[0], FIRE_BBOX[1])
    east, north = to_utm.transform(FIRE_BBOX[2], FIRE_BBOX[3])
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


def load_perimeter(epsg: int):
    if not PERIM.exists():
        raise SystemExit(f"missing {PERIM} — run python scripts/fetch_snyder_perimeter.py")
    gj = json.loads(PERIM.read_text())
    geoms = [shape(ft["geometry"]) for ft in gj["features"]]
    geom_ll = unary_union(geoms)
    to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)

    def _t(coords):
        lon, lat = to_utm.transform(coords[:, 0], coords[:, 1])
        out = np.empty_like(coords)
        out[:, 0] = lon
        out[:, 1] = lat
        if coords.shape[1] > 2:
            out[:, 2:] = coords[:, 2:]
        return out

    geom_utm = shp_xy(geom_ll, _t)
    props = gj["features"][0].get("properties") or {}
    return geom_ll, geom_utm, props, gj


def affine_for(x: np.ndarray, y: np.ndarray, dx: float, dy: float) -> Affine:
    return Affine(dx, 0.0, float(x[0]) - dx / 2.0, 0.0, dy, float(y[0]) - dy / 2.0)


def raster_in_poly(geom_utm, shape_hw, transform: Affine) -> np.ndarray:
    return rasterize(
        [(geom_utm, 1)],
        out_shape=shape_hw,
        transform=transform,
        fill=0,
        dtype=np.uint8,
    ).astype(bool)


def polygonize(mask: np.ndarray, transform: Affine, epsg: int):
    polys = [shape(geom) for geom, val in shapes(mask.astype(np.uint8), mask=mask, transform=transform) if val == 1]
    if not polys:
        from shapely.geometry import GeometryCollection

        union = GeometryCollection()
    else:
        union = unary_union(polys)
    to_ll = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)

    def _t(coords):
        lon, lat = to_ll.transform(coords[:, 0], coords[:, 1])
        out = np.empty_like(coords)
        out[:, 0] = lon
        out[:, 1] = lat
        if coords.shape[1] > 2:
            out[:, 2:] = coords[:, 2:]
        return out

    return union, (union if union.is_empty else shp_xy(union, _t))


def load_gunw_coherence(x: np.ndarray, y: np.ndarray):
    """Crop 80 m GUNW HH coherence onto the GCOV frequencyB crop if a file exists."""
    files = sorted(GUNW.glob("*.h5"))
    if not files:
        return None, None
    # Prefer the 29 Jun–11 Jul pair (active burn). Partial_* files are not .h5.
    ranked = sorted(
        files,
        key=lambda p: ("20260629" in p.name and "20260711" in p.name, p.name),
        reverse=True,
    )
    path = ranked[0]
    layer = "science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude"
    x_key = "science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/xCoordinates"
    y_key = "science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/yCoordinates"
    with h5py.File(path, "r") as f:
        if layer not in f:
            print(f"GUNW {path.name}: no {layer}", file=sys.stderr)
            return None, path.name
        gx = f[x_key][:]
        gy = f[y_key][:]
        coh = f[layer][:]
    col0 = int(np.argmin(np.abs(gx - x[0])))
    row0 = int(np.argmin(np.abs(gy - y[0])))
    sampled = coh[row0 : row0 + y.size, col0 : col0 + x.size].astype(np.float32)
    if sampled.shape != (y.size, x.size):
        print(f"GUNW crop shape {sampled.shape} != {(y.size, x.size)}", file=sys.stderr)
        return None, path.name
    return sampled, path.name


def pixel_to_plot(geom_utm, x, y, dx, dy):
    def add(ax, poly, **kw):
        ext = np.asarray(poly.exterior.coords)
        cols = (ext[:, 0] - x[0]) / dx
        rows = (ext[:, 1] - y[0]) / dy
        ax.plot(cols, rows, **kw)

    def overlay(ax, **kw):
        gt = geom_utm.geom_type
        if gt == "Polygon":
            add(ax, geom_utm, **kw)
        elif gt == "MultiPolygon":
            for p in geom_utm.geoms:
                add(ax, p, **kw)

    return overlay


def save_raw_layer(path: Path, arr, cmap, vmin, vmax) -> None:
    """PNG with no axes — for Leaflet ImageOverlay. origin=upper = north at top."""
    h, w = arr.shape
    fig = plt.figure(figsize=(w / 100.0, h / 100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    cm = plt.get_cmap(cmap).copy() if isinstance(cmap, str) else cmap
    cm.set_bad("#0b0d10")
    ax.imshow(arr, cmap=cm, vmin=vmin, vmax=vmax, origin="upper", interpolation="nearest")
    ax.set_axis_off()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100, pad_inches=0)
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


def save_panel(path: Path, arr, title, cmap, vmin, vmax, overlay_fn=None, cbar="dB"):
    fig, ax = plt.subplots(figsize=(7.2, 6.2), dpi=140)
    im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax, origin="upper")
    if overlay_fn:
        overlay_fn(ax)
    ax.set_title(title)
    ax.set_axis_off()
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label=cbar)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def main() -> int:
    src = load_gcov()
    geom_ll, geom_utm, perim_props, perim_gj = load_perimeter(src["epsg"])
    x, y, dx, dy = src["x"], src["y"], src["dx"], src["dy"]
    transform = affine_for(x, y, dx, dy)
    in_fire = raster_in_poly(geom_utm, src["before"]["HHHH"].shape, transform)

    valid = (
        product_valid(src["before"]["mask"])
        & product_valid(src["after"]["mask"])
        & np.isfinite(src["before"]["HHHH"])
        & np.isfinite(src["after"]["HHHH"])
        & np.isfinite(src["before"]["HVHV"])
        & np.isfinite(src["after"]["HVHV"])
        & (src["before"]["HHHH"] > 0)
        & (src["after"]["HHHH"] > 0)
        & (src["before"]["HVHV"] > 0)
        & (src["after"]["HVHV"] > 0)
    )

    diffs = {}
    dbs = {}
    for pol in ("HHHH", "HVHV"):
        before = despeckle(to_db(src["before"][pol]))
        after = despeckle(to_db(src["after"][pol]))
        before[~valid] = np.nan
        after[~valid] = np.nan
        diff = after - before
        diff[~valid] = np.nan
        diffs[pol] = diff
        dbs[pol] = (before, after)

    hv = diffs["HVHV"]
    hh = diffs["HHHH"]
    inside = in_fire & valid
    outside = (~in_fire) & valid
    hv_in = hv[inside]
    sign = float(np.sign(np.nanmedian(hv_in))) if hv_in.size else 1.0
    if sign == 0:
        sign = 1.0
    signed = sign * hv
    change = valid & np.isfinite(hv) & (signed >= THRESH_DB)
    # drop 1-pixel speckle islands
    change = binary_opening(change, structure=np.ones((3, 3), dtype=bool))
    labeled, nlab = label(change)
    keep = np.zeros_like(change)
    for i in range(1, nlab + 1):
        blob = labeled == i
        if int(blob.sum()) >= MIN_PIXELS:
            keep |= blob
    change = keep

    both_pol = valid & np.isfinite(hh) & (np.sign(hh) == np.sign(hv)) & (np.abs(hh) >= THRESH_DB) & (np.abs(hv) >= THRESH_DB)

    gunw_coh, gunw_name = load_gunw_coherence(x, y)
    gunw_low = None
    gunw_stats = {}
    if gunw_coh is not None:
        # Co-event pair: burned canopy should already be incoherent.
        gunw_low = np.isfinite(gunw_coh) & (gunw_coh >= 0) & (gunw_coh < GUNW_COH_LOW)
        gunw_stats = {
            "inside_mean": float(np.nanmean(gunw_coh[inside])) if inside.any() else None,
            "outside_mean": float(np.nanmean(gunw_coh[outside])) if outside.any() else None,
            "change_mean": float(np.nanmean(gunw_coh[change])) if change.any() else None,
            "low_threshold": GUNW_COH_LOW,
            "change_low_frac": float(np.mean(gunw_low[change])) if change.any() else None,
        }

    # Confidence 0–4 (byte), also stretched 0–1 for the PNG.
    conf = np.zeros(change.shape, dtype=np.uint8)
    conf[valid] = 1
    conf[change] = 2
    conf[change & both_pol] = 3
    conf[change & in_fire] = np.maximum(conf[change & in_fire], 3)
    conf[change & both_pol & in_fire] = 4
    if gunw_low is not None:
        conf[change & gunw_low] = np.maximum(conf[change & gunw_low], np.uint8(4))

    pixel_km2 = abs(dx * dy) / 1e6
    area_km2 = float(change.sum() * pixel_km2)
    nifc_km2 = float(geom_utm.area / 1e6)
    tp = float((change & in_fire).sum())
    fp = float((change & ~in_fire).sum())
    fn = float((~change & in_fire & valid).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    iou = tp / (tp + fp + fn) if (tp + fp + fn) else 0.0

    union_utm, union_ll = polygonize(change, transform, src["epsg"])
    shapely_km2 = 0.0 if union_utm.is_empty else float(union_utm.area / 1e6)

    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_PUB.mkdir(parents=True, exist_ok=True)

    overlay = pixel_to_plot(geom_utm, x, y, dx, dy)
    yellow = dict(color="yellow", lw=1.15, solid_capstyle="round")

    save_panel(
        OUT_PUB / "change.png",
        hv,
        f"Snyder HVHV log-ratio (dB)  {src['before_date']} → {src['after_date']}\n"
        "yellow outline: NIFC WFIGS perimeter 2026-UTDRD-005113",
        "RdBu_r",
        -4,
        4,
        overlay_fn=lambda ax: overlay(ax, **yellow),
    )
    conf_cmap = ListedColormap(["#111111", "#4a4a4a", "#f4d35e", "#ee964b", "#c1121f"])
    save_panel(
        OUT_PUB / "confidence.png",
        conf.astype(np.float32),
        "Confidence 0–4  (white = NIFC perimeter)",
        conf_cmap,
        0,
        4,
        overlay_fn=lambda ax: overlay(ax, color="white", lw=1.0),
        cbar="level",
    )
    if gunw_coh is not None:
        save_panel(
            OUT_PUB / "coherence.png",
            gunw_coh,
            "GUNW HH coherence  29 Jun–11 Jul 2026 (co-event)\n"
            "yellow = NIFC perimeter; low coherence inside the scar is the second vote",
            "viridis",
            0,
            1,
            overlay_fn=lambda ax: overlay(ax, **yellow),
            cbar="coherence",
        )
    save_panel(
        OUT_DATA / "change_mask.png",
        np.where(valid, change.astype(np.float32), np.nan),
        f"Detected change  {area_km2:.1f} km²  IoU vs NIFC={iou:.2f}",
        "autumn",
        0,
        1,
        overlay_fn=lambda ax: overlay(ax, **yellow),
        cbar="change",
    )

    citation = {
        "polygon": "NIFC WFIGS Interagency Perimeters Year-to-Date",
        "unique_fire_identifier": "2026-UTDRD-005113",
        "incident_name": perim_props.get("poly_IncidentName") or "Snyder",
        "gis_acres": perim_props.get("poly_GISAcres"),
        "percent_contained": perim_props.get("attr_PercentContained"),
        "wfigs_layer": "https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-interagency-fire-perimeters-to-date",
        "wfigs_query": "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Interagency_Perimeters_YearToDate/FeatureServer/0",
        "inciweb": "https://inciweb.wildfire.gov/incident-information/utdrd-snyder",
        "ops_maps": "https://ftp.wildfire.gov/public/incident_specific_maps/rocky_mtn/2026/2026_Snyder/",
        "firms": "https://firms.modaps.eosdis.nasa.gov/ (hotspots, not this polygon)",
        "note": "WFIGS GIS acres are 30,202.5. NIFC situation reports later listed 28,264 acres contained. Overlay uses the WFIGS polygon.",
    }

    change_fc = {
        "type": "FeatureCollection",
        "name": "echolens_snyder_gcov_change",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "properties": {
            "area_km2": round(area_km2, 3),
            "polygon_area_km2": round(shapely_km2, 3),
            "nifc_km2": round(nifc_km2, 3),
            "pixel_m": abs(dx),
            "threshold_db": THRESH_DB,
            "primary_pol": "HVHV",
            "sign": "increase" if sign > 0 else "decrease",
            "before": src["before_date"],
            "after": src["after_date"],
            "precision_vs_nifc": round(precision, 3),
            "recall_vs_nifc": round(recall, 3),
            "iou_vs_nifc": round(iou, 3),
            "gunw_file": gunw_name,
            "citation": citation,
        },
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "EchoLens GCOV log-ratio change",
                    "area_km2": round(shapely_km2, 3),
                    "pixel_area_km2": round(area_km2, 3),
                },
                "geometry": None if union_ll.is_empty else mapping(union_ll),
            }
        ],
    }
    (OUT_PUB / "change.geojson").write_text(json.dumps(change_fc))
    (OUT_PUB / "perimeter_nifc.geojson").write_text(json.dumps(perim_gj))

    layer_dir = OUT_PUB / "layers"
    hv_before, hv_after = dbs["HVHV"]
    finite = hv_before[np.isfinite(hv_before)]
    lo, hi = (float(np.percentile(finite, 2)), float(np.percentile(finite, 98))) if finite.size else (-20.0, 0.0)
    conf_cmap = ListedColormap(["#111111", "#4a4a4a", "#f4d35e", "#ee964b", "#c1121f"])
    save_raw_layer(layer_dir / "before.png", hv_before, "gray", lo, hi)
    save_raw_layer(layer_dir / "after.png", hv_after, "gray", lo, hi)
    save_raw_layer(layer_dir / "change.png", hv, "RdBu_r", -4, 4)
    save_raw_layer(layer_dir / "confidence.png", conf.astype(np.float32), conf_cmap, 0, 4)
    bounds = layer_bounds(x, y, dx, dy, src["epsg"])
    (layer_dir / "bounds.json").write_text(json.dumps(bounds, indent=2))
    print("layer bounds", bounds)

    summary = {
        "when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "before": src["before_date"],
        "after": src["after_date"],
        "before_file": src["before_path"],
        "after_file": src["after_path"],
        "grid": GRID,
        "pixel_m": abs(dx),
        "threshold_db": THRESH_DB,
        "despeckle": f"median {MEDIAN_SIZE}x{MEDIAN_SIZE}",
        "primary_pol": "HVHV",
        "inside_hv_mean_db": float(np.nanmean(hv_in)) if hv_in.size else None,
        "inside_hv_median_db": float(np.nanmedian(hv_in)) if hv_in.size else None,
        "outside_hv_median_db": float(np.nanmedian(hv[outside])) if outside.any() else None,
        "inside_hh_median_db": float(np.nanmedian(hh[inside])) if inside.any() else None,
        "sign_used": "increase" if sign > 0 else "decrease",
        "change_pixels": int(change.sum()),
        "area_km2": round(area_km2, 3),
        "nifc_km2": round(nifc_km2, 3),
        "precision_vs_nifc": round(precision, 3),
        "recall_vs_nifc": round(recall, 3),
        "iou_vs_nifc": round(iou, 3),
        "gunw": gunw_name,
        "gunw_coherence": gunw_stats,
        "citation": citation,
    }
    (OUT_PUB / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print("GeoJSON", OUT_PUB / "change.geojson")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
