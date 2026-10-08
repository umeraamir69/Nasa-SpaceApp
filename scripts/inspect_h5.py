#!/usr/bin/env python3
"""Print the HDF5 tree and key GCOV layers. Does not load the full 10 m images."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "data" / "snyder" / "gcov"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help=".h5 path (default: first Snyder GCOV)")
    args = parser.parse_args()
    path = Path(args.file) if args.file else next(DEFAULT.glob("*.h5"), None)
    if path is None or not path.exists():
        print("No .h5 found. Pass a path.", file=sys.stderr)
        return 1

    print(f"file  {path}")
    print(f"size  {path.stat().st_size / 1e9:.2f} GB\n")

    with h5py.File(path, "r") as f:
        print("## layers we care about")
        for key in (
            "science/LSAR/GCOV/grids/frequencyA/HHHH",
            "science/LSAR/GCOV/grids/frequencyA/HVHV",
            "science/LSAR/GCOV/grids/frequencyA/mask",
            "science/LSAR/GCOV/grids/frequencyB/HHHH",
        ):
            if key in f:
                d = f[key]
                print(f"  {key}\n    shape={d.shape} dtype={d.dtype}")

        print("\n## frequencyB/HHHH sample stats (80 m, small enough to read)")
        arr = f["science/LSAR/GCOV/grids/frequencyB/HHHH"][:]
        valid = arr[np.isfinite(arr) & (arr > 0)]
        if valid.size:
            print(f"  pixels={arr.size:,}  valid={valid.size:,}")
            print(f"  min={valid.min():.4g}  median={np.median(valid):.4g}  max={valid.max():.4g}")
        ident = f["science/LSAR/identification"]
        print("\n## identity")
        for name in (
            "granuleId",
            "zeroDopplerStartTime",
            "trackNumber",
            "frameNumber",
            "orbitPassDirection",
        ):
            v = ident[name][()]
            if isinstance(v, bytes):
                v = v.decode()
            print(f"  {name}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
