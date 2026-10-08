#!/usr/bin/env python3
"""Render 80 m GCOV HHHH previews. Panoply cannot open these NISAR files."""

from __future__ import annotations

from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "snyder" / "gcov"
OUT = ROOT / "data" / "snyder" / "preview"
LAYER = "science/LSAR/GCOV/grids/frequencyB/HHHH"


def to_db(arr: np.ndarray) -> np.ndarray:
    valid = np.isfinite(arr) & (arr > 0)
    out = np.full(arr.shape, np.nan, dtype=np.float32)
    out[valid] = (10.0 * np.log10(arr[valid])).astype(np.float32)
    return out


def stretch(arr: np.ndarray) -> tuple[float, float]:
    finite = arr[np.isfinite(arr)]
    lo, hi = np.percentile(finite, (2, 98))
    return float(lo), float(hi)


def save_gray(path: Path, arr: np.ndarray, title: str) -> None:
    lo, hi = stretch(arr)
    fig, ax = plt.subplots(figsize=(8, 8), dpi=120)
    ax.imshow(arr, cmap="gray", vmin=lo, vmax=hi, origin="upper")
    ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def main() -> None:
    files = sorted(SRC.glob("*.h5"))
    if len(files) < 2:
        raise SystemExit(f"need 2 .h5 files in {SRC}")
    OUT.mkdir(parents=True, exist_ok=True)

    dbs = []
    labels = []
    for path in files:
        with h5py.File(path, "r") as f:
            power = f[LAYER][:]
            start = f["science/LSAR/identification/zeroDopplerStartTime"][()]
            if isinstance(start, bytes):
                start = start.decode()
        date = start[:10]
        db = to_db(power)
        dbs.append(db)
        labels.append(date)
        save_gray(OUT / f"hhhh_{date}.png", db, f"GCOV HHHH 80 m  {date}  (dB)")

    before, after = dbs
    diff = after - before
    save_gray(OUT / "hhhh_diff_jul_minus_jun.png", diff, "July − June  (dB, 80 m)")
    print("done", OUT)


if __name__ == "__main__":
    main()
