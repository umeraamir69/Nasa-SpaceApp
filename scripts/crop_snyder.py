#!/usr/bin/env python3
"""Crop 80 m GCOV to the Snyder Fire box and test if a burn scar is visible."""

from __future__ import annotations

from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "snyder" / "gcov"
OUT = ROOT / "data" / "snyder" / "preview" / "crop"

# Westwater / Snyder Mesa / Glade Park (CO–UT border). ~114 km² fire.
# lon_min, lat_min, lon_max, lat_max
FIRE_BBOX = (-109.22, 38.98, -108.80, 39.20)
LAYERS = ("HHHH", "HVHV")
GRID = "science/LSAR/GCOV/grids/frequencyB"


def to_db(arr: np.ndarray) -> np.ndarray:
    valid = np.isfinite(arr) & (arr > 0)
    out = np.full(arr.shape, np.nan, dtype=np.float32)
    out[valid] = (10.0 * np.log10(arr[valid])).astype(np.float32)
    return out


def crop_window(x: np.ndarray, y: np.ndarray, west: float, south: float, east: float, north: float):
    col = np.where((x >= west) & (x <= east))[0]
    row = np.where((y >= south) & (y <= north))[0]
    if col.size == 0 or row.size == 0:
        raise SystemExit(f"fire box is outside the raster. x={x.min():.0f}-{x.max():.0f} y={y.min():.0f}-{y.max():.0f}")
    return slice(row.min(), row.max() + 1), slice(col.min(), col.max() + 1)


def save(path: Path, arr: np.ndarray, title: str, cmap: str, vmin=None, vmax=None) -> None:
    finite = arr[np.isfinite(arr)]
    if vmin is None or vmax is None:
        vmin, vmax = np.percentile(finite, (2, 98))
    fig, ax = plt.subplots(figsize=(7, 6), dpi=140)
    im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax, origin="upper")
    ax.set_title(title)
    ax.set_axis_off()
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="dB")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def stats(name: str, before: np.ndarray, after: np.ndarray) -> dict:
    diff = after - before
    ok = np.isfinite(diff)
    drop = diff[ok]
    mean = float(np.mean(drop))
    med = float(np.median(drop))
    pct_dark = float(np.mean(drop < -1.0) * 100)
    print(f"{name}: mean ΔdB={mean:.2f}  median={med:.2f}  pct pixels < -1 dB={pct_dark:.1f}%")
    return {"mean": mean, "median": med, "pct_lt_minus1": pct_dark}


def main() -> None:
    files = sorted(SRC.glob("*.h5"))
    if len(files) < 2:
        raise SystemExit(f"need 2 .h5 in {SRC}")
    OUT.mkdir(parents=True, exist_ok=True)

    with h5py.File(files[0], "r") as f:
        g = f[GRID]
        epsg = int(g["projection"][()])
        x = g["xCoordinates"][:]
        y = g["yCoordinates"][:]

    to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    west, south = to_utm.transform(FIRE_BBOX[0], FIRE_BBOX[1])
    east, north = to_utm.transform(FIRE_BBOX[2], FIRE_BBOX[3])
    rows, cols = crop_window(x, y, west, south, east, north)
    print(f"EPSG:{epsg} crop rows={rows} cols={cols} size={(rows.stop-rows.start)}x{(cols.stop-cols.start)}")

    for pol in LAYERS:
        dbs = []
        dates = []
        for path in files:
            with h5py.File(path, "r") as f:
                power = f[f"{GRID}/{pol}"][rows, cols]
                start = f["science/LSAR/identification/zeroDopplerStartTime"][()]
                if isinstance(start, bytes):
                    start = start.decode()
            date = start[:10]
            db = to_db(power)
            dbs.append(db)
            dates.append(date)
            save(OUT / f"{pol}_{date}_crop.png", db, f"{pol} {date} (80 m, Snyder box)", "gray")

        before, after = dbs
        diff = after - before
        save(
            OUT / f"{pol}_diff_crop.png",
            diff,
            f"{pol} July − June (dB)  Snyder box",
            "RdBu_r",
            vmin=-4,
            vmax=4,
        )
        stats(pol, before, after)

    print("bbox lon/lat", FIRE_BBOX)
    print("done", OUT)


if __name__ == "__main__":
    main()
