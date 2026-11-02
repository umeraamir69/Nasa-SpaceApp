#!/usr/bin/env python3
"""Autumn Lane wildfire GCOV change (Spokane WA, Jul–Aug 2026).

Same HV log-ratio method as Snyder: despeckle, one-sided darkening test,
blob filter, polygonize. Wildland-urban interface (timber + homes); Snyder-parity 1.5 dB default
threshold. Scored against the NIFC perimeter.

Run:  .conda/env/bin/python scripts/change_spokane.py [--threshold 1.5] --truth outputs/spokane/perimeter_nifc.geojson
Needs data/spokane/gcov/042_D_065 23 Jul + 16 Aug .h5 (P05023).
"""

from __future__ import annotations

import argparse
import json
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

import granule_modes

ROOT = Path(__file__).resolve().parents[1]
GCOV = ROOT / "data" / "spokane" / "gcov"
OUT_PUB = ROOT / "outputs" / "spokane"

# Wabakimi / Armstrong. Scar touches the west and south edges of a tight box,
# so this carries margin; frame f063 spans lon -92.1..-86.7, lat 48.6..52.0.
FIRE_BBOX = (-117.75, 47.70, -117.40, 47.88)
GRID = "science/LSAR/GCOV/grids/frequencyB"
THRESH_DB = 1.5
MEDIAN_SIZE = 3
MIN_PIXELS = 8
NEEDLE = "042_D_065"


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


def crop_window(x, y, west, south, east, north):
    col = np.where((x >= west) & (x <= east))[0]
    row = np.where((y >= south) & (y <= north))[0]
    if col.size == 0 or row.size == 0:
        raise SystemExit("fire box is outside the raster")
    return slice(row.min(), row.max() + 1), slice(col.min(), col.max() + 1)


def load_gcov():
    files = sorted(p for p in GCOV.glob("*.h5") if NEEDLE in p.name and "P05023" in p.name)
    if len(files) < 2:
        files = sorted(p for p in GCOV.glob("*.h5") if NEEDLE in p.name)
    if len(files) < 2:
        raise SystemExit(f"need 2 {NEEDLE} .h5 in {GCOV}")
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

    def read(path: Path):
        with h5py.File(path, "r") as f:
            g = f[GRID]
            return {"HHHH": g["HHHH"][rows, cols], "HVHV": g["HVHV"][rows, cols],
                    "mask": g["mask"][rows, cols]}

    return {"epsg": epsg, "x": x[cols], "y": y[rows], "dx": dx, "dy": dy,
            "before_date": before_date, "after_date": after_date,
            "before": read(before_path), "after": read(after_path),
            "before_path": before_path.name, "after_path": after_path.name}


def affine_for(x, y, dx, dy) -> Affine:
    return Affine(dx, 0.0, float(x[0]) - dx / 2.0, 0.0, dy, float(y[0]) - dy / 2.0)


def raster_in_poly(geom_utm, shape_hw, transform: Affine) -> np.ndarray:
    if geom_utm is None or geom_utm.is_empty:
        return np.zeros(shape_hw, dtype=bool)
    return rasterize([(geom_utm, 1)], out_shape=shape_hw, transform=transform,
                     fill=0, dtype=np.uint8).astype(bool)


def polygonize(mask: np.ndarray, transform: Affine, epsg: int):
    polys = [shape(geom) for geom, val in shapes(mask.astype(np.uint8), mask=mask,
                                                 transform=transform) if val == 1]
    if not polys:
        from shapely.geometry import GeometryCollection
        return GeometryCollection(), GeometryCollection()
    union = unary_union(polys)
    to_ll = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)

    def _t(coords):
        lon, lat = to_ll.transform(coords[:, 0], coords[:, 1])
        out = np.empty_like(coords)
        out[:, 0], out[:, 1] = lon, lat
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


def layer_bounds(x, y, dx, dy, epsg: int) -> dict:
    to_ll = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    west, east = float(x[0] - dx / 2.0), float(x[-1] + dx / 2.0)
    north, south = float(y[0] - dy / 2.0), float(y[-1] + dy / 2.0)
    w1, n1 = to_ll.transform(west, north)
    e1, s1 = to_ll.transform(east, south)
    return {"south": s1, "west": w1, "north": n1, "east": e1, "epsg": epsg,
            "pixel_m": abs(dx), "width": int(x.size), "height": int(y.size)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Autumn Lane HV log-ratio change.")
    ap.add_argument("--threshold", type=float, default=THRESH_DB)
    ap.add_argument("--truth", default=None, help="optional truth-polygon GeoJSON")
    ap.add_argument("--sign", choices=("auto", "decrease", "increase"), default="decrease",
                    help="fire darkens HV: 'decrease' unless you have a reason")
    args = ap.parse_args()

    src = load_gcov()
    granule_modes.require_compatible(src["before_path"], src["after_path"])
    x, y, dx, dy = src["x"], src["y"], src["dx"], src["dy"]
    transform = affine_for(x, y, dx, dy)

    truth_utm = None
    truth_name = None
    if args.truth:
        gj = json.loads(Path(args.truth).read_text())
        geoms = [shape(f["geometry"]) for f in gj.get("features") or [] if f.get("geometry")]
        truth_ll = unary_union(geoms)
        to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{src['epsg']}", always_xy=True)

        def _t(coords):
            lon, lat = to_utm.transform(coords[:, 0], coords[:, 1])
            out = np.empty_like(coords)
            out[:, 0], out[:, 1] = lon, lat
            return out

        truth_utm = shp_xy(truth_ll, _t)
        truth_name = Path(args.truth).name
    in_fire = raster_in_poly(truth_utm, src["before"]["HHHH"].shape, transform)

    valid = (product_valid(src["before"]["mask"]) & product_valid(src["after"]["mask"])
             & np.isfinite(src["before"]["HHHH"]) & np.isfinite(src["after"]["HHHH"])
             & np.isfinite(src["before"]["HVHV"]) & np.isfinite(src["after"]["HVHV"])
             & (src["before"]["HHHH"] > 0) & (src["after"]["HHHH"] > 0)
             & (src["before"]["HVHV"] > 0) & (src["after"]["HVHV"] > 0))

    diffs, dbs = {}, {}
    for pol in ("HHHH", "HVHV"):
        before = despeckle(to_db(src["before"][pol]))
        after = despeckle(to_db(src["after"][pol]))
        before[~valid] = np.nan
        after[~valid] = np.nan
        diff = after - before
        diff[~valid] = np.nan
        diffs[pol], dbs[pol] = diff, (before, after)

    hv, hh = diffs["HVHV"], diffs["HHHH"]
    if args.sign == "auto":
        # Median of central half (no perimeter yet). Fragile when the scar
        # sits off-centre — prefer the default 'decrease' for fires.
        h, w = hv.shape
        core = np.zeros_like(valid)
        core[h // 4:3 * h // 4, w // 4:3 * w // 4] = valid[h // 4:3 * h // 4, w // 4:3 * w // 4]
        hv_core = hv[core]
        sign = float(np.sign(np.nanmedian(hv_core))) if hv_core.size else -1.0
        if sign == 0:
            sign = -1.0
    else:
        sign = 1.0 if args.sign == "increase" else -1.0
    change = valid & np.isfinite(hv) & (sign * hv >= args.threshold)
    change = binary_opening(change, structure=np.ones((3, 3), dtype=bool))
    labeled, nlab = label(change)
    keep = np.zeros_like(change)
    for i in range(1, nlab + 1):
        blob = labeled == i
        if int(blob.sum()) >= MIN_PIXELS:
            keep |= blob
    change = keep

    both_pol = (valid & np.isfinite(hh) & (np.sign(hh) == np.sign(hv))
                & (np.abs(hh) >= args.threshold) & (np.abs(hv) >= args.threshold))

    conf = np.zeros(change.shape, dtype=np.uint8)
    conf[valid] = 1
    conf[change] = 2
    conf[change & both_pol] = 3

    pixel_km2 = abs(dx * dy) / 1e6
    area_km2 = float(change.sum() * pixel_km2)
    union_utm, union_ll = polygonize(change, transform, src["epsg"])
    shapely_km2 = 0.0 if union_utm.is_empty else float(union_utm.area / 1e6)

    metrics = {}
    if truth_utm is not None and not truth_utm.is_empty:
        truth_km2 = float(truth_utm.area / 1e6)
        tp = float((change & in_fire).sum())
        fp = float((change & ~in_fire).sum())
        fn = float((~change & in_fire & valid).sum())
        metrics = {"truth": truth_name, "truth_km2": round(truth_km2, 3),
                   "precision_vs_truth": round(tp / (tp + fp), 3) if (tp + fp) else 0.0,
                   "recall_vs_truth": round(tp / (tp + fn), 3) if (tp + fn) else 0.0,
                   "iou_vs_truth": round(tp / (tp + fp + fn), 3) if (tp + fp + fn) else 0.0}

    OUT_PUB.mkdir(parents=True, exist_ok=True)
    save_panel(OUT_PUB / "change.png", hv,
               f"Autumn Lane HVHV log-ratio (dB)  {src['before_date']} → {src['after_date']}",
               "RdBu_r", -6, 6)
    conf_cmap = ListedColormap(["#111111", "#4a4a4a", "#ee964b", "#c1121f"])
    save_panel(OUT_PUB / "confidence.png", conf.astype(np.float32),
               "0 none · 1 valid · 2 change · 3 both-pol", conf_cmap, 0, 3, cbar="level")

    citation = {
        "event": "Autumn Lane fire, Spokane WA — 5,764 acres, 833 homes lost",
        "unique_fire_identifier": "2026-WANES-001857",
        "start": "2026-08-01",
        "polygon": "NIFC WFIGS Interagency Perimeters Year-to-Date",
        "wfigs_layer": "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Interagency_Perimeters_YearToDate/FeatureServer/0",
        "note": "Scored against the NIFC perimeter via --truth.",
    }
    change_fc = {"type": "FeatureCollection", "name": "echolens_spokane_gcov_change",
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                 "properties": {"area_km2": round(area_km2, 3),
                                "polygon_area_km2": round(shapely_km2, 3),
                                "pixel_m": abs(dx), "threshold_db": args.threshold,
                                "primary_pol": "HVHV",
                                "sign": "increase" if sign > 0 else "decrease",
                                "before": src["before_date"], "after": src["after_date"],
                                **metrics, "citation": citation},
                 "features": [{"type": "Feature",
                               "properties": {"name": "EchoLens GCOV log-ratio change",
                                              "area_km2": round(shapely_km2, 3)},
                               "geometry": None if union_ll.is_empty else mapping(union_ll)}]}
    (OUT_PUB / "change.geojson").write_text(json.dumps(change_fc))

    layer_dir = OUT_PUB / "layers"
    hv_before, hv_after = dbs["HVHV"]
    finite = hv_before[np.isfinite(hv_before)]
    lo, hi = (float(np.percentile(finite, 2)), float(np.percentile(finite, 98))) if finite.size else (-20.0, 0.0)
    save_raw_layer(layer_dir / "before.png", hv_before, "gray", lo, hi)
    save_raw_layer(layer_dir / "after.png", hv_after, "gray", lo, hi)
    save_raw_layer(layer_dir / "change.png", hv, "RdBu_r", -6, 6)
    conf_layer = conf.astype(np.float32)
    conf_layer[conf == 0] = np.nan
    save_raw_layer(layer_dir / "confidence.png", conf_layer, conf_cmap, 0, 3)
    bounds = layer_bounds(x, y, dx, dy, src["epsg"])
    (layer_dir / "bounds.json").write_text(json.dumps(bounds, indent=2))

    summary = {"when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "case": "spokane", "event": "Autumn Lane wildfire, Washington",
               "before": src["before_date"], "after": src["after_date"],
               "before_file": src["before_path"], "after_file": src["after_path"],
               "grid": GRID, "pixel_m": abs(dx), "threshold_db": args.threshold,
               "despeckle": f"median {MEDIAN_SIZE}x{MEDIAN_SIZE}", "primary_pol": "HVHV",
               "sign_used": "increase" if sign > 0 else "decrease",
               "change_pixels": int(change.sum()), "area_km2": round(area_km2, 3),
               **metrics, "citation": citation}
    (OUT_PUB / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
