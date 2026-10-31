#!/usr/bin/env python3
"""Latvia method experiment: compare flood-detection rules (conda env).

The shipped HH-darkening rule found only unvalidated fragments on the
post-peak 18→30 Aug pair. This script loads the same crop and compares
candidate rules side by side WITHOUT overwriting outputs/latvia/.

Run:  .conda/env/bin/python scripts/experiment_latvia.py [--needle 080_D_059]

Needs data/latvia/crop/{before,after}.npz (crop_nepal.py --out ...) or
2 local .h5 granules in data/latvia/gcov/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_opening, label

sys.path.insert(0, str(Path(__file__).resolve().parent))

import change_latvia as CL  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CROP = ROOT / "data" / "latvia" / "crop"


def load_npz_pair():
    before_p, after_p = CROP / "before.npz", CROP / "after.npz"
    if not (before_p.exists() and after_p.exists()):
        return None
    before = np.load(before_p, allow_pickle=False)
    after = np.load(after_p, allow_pickle=False)
    pols = [p for p in ("HHHH", "HVHV") if p in before and p in after]

    def pack(z):
        out = {"mask": z["mask"]}
        for pol in pols:
            out[pol] = z[pol]
        return out

    return {"before": pack(before), "after": pack(after), "pols": pols,
            "dx": float(before["dx"]), "dy": float(before["dy"])}


def blobs(mask: np.ndarray, min_pixels: int = 8) -> np.ndarray:
    opened = binary_opening(mask, structure=np.ones((3, 3), dtype=bool))
    labeled, nlab = label(opened)
    keep = np.zeros_like(mask)
    for i in range(1, nlab + 1):
        blob = labeled == i
        if int(blob.sum()) >= min_pixels:
            keep |= blob
    return keep


def report(name: str, mask: np.ndarray, pixel_km2: float) -> None:
    kept = blobs(mask)
    labeled, nlab = label(kept)
    print(f"{name:34s} raw={mask.sum():7d}  kept={kept.sum():7d}  "
          f"blobs={nlab:4d}  area={kept.sum() * pixel_km2:7.2f} km²")


def main() -> int:
    needle = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--needle" else "080_D_059"
    src = load_npz_pair()
    if src is None:
        print("no npz crop; loading local .h5 (needs full granules)")
        full = CL.load_gcov()
        src = {"before": full["before"], "after": full["after"],
               "pols": ["HHHH", "HVHV"], "dx": full["dx"], "dy": full["dy"]}
    pols = src["pols"]
    print(f"pols: {pols}")

    valid = CL.product_valid(src["before"]["mask"]) & CL.product_valid(src["after"]["mask"])
    db = {}
    for pol in pols:
        b = CL.despeckle(CL.to_db(src["before"][pol]))
        a = CL.despeckle(CL.to_db(src["after"][pol]))
        b[~valid] = np.nan
        a[~valid] = np.nan
        valid &= np.isfinite(src["before"][pol]) & np.isfinite(src["after"][pol])
        valid &= (src["before"][pol] > 0) & (src["after"][pol] > 0)
        db[pol] = (b, a)
    print(f"valid frac: {valid.mean():.3f}")

    hh_b, hh_a = db["HHHH"]
    diff = hh_a - hh_b
    pixel_km2 = abs(src["dx"] * src["dy"]) / 1e6
    print(f"HH diff median: {np.nanmedian(diff[valid]):+.2f} dB  "
          f"p5/p95: {np.nanpercentile(diff[valid], 5):+.1f}/{np.nanpercentile(diff[valid], 95):+.1f}")

    print("\n--- rule comparison (all with 3x3 opening + min 8 px) ---")
    permanent = valid & (hh_b <= -14.0) & (hh_a <= -14.0)
    # 1. shipped rule
    report("shipped: dHH<=-2dB & after<=-12dB & !perm",
           valid & ~permanent & (diff <= -2.0) & (hh_a <= -12.0), pixel_km2)
    # 2. looser after-water gate
    report("loose: dHH<=-2dB & after<=-10dB & !perm",
           valid & ~permanent & (diff <= -2.0) & (hh_a <= -10.0), pixel_km2)
    # 3. no after gate at all
    report("nogate: dHH<=-2dB & !perm",
           valid & ~permanent & (diff <= -2.0), pixel_km2)
    # 4. stricter darkening
    report("strict: dHH<=-3dB & after<=-12dB & !perm",
           valid & ~permanent & (diff <= -3.0) & (hh_a <= -12.0), pixel_km2)
    if "HVHV" in db:
        hv_b, hv_a = db["HVHV"]
        hv_diff = hv_a - hv_b
        # 5. cross-pol darkening (canopy/roughness loss under water)
        report("hv: dHV<=-2dB & afterHV<=-18dB & !perm",
               valid & ~permanent & (hv_diff <= -2.0) & (hv_a <= -18.0), pixel_km2)
        # 6. dual-pol water index: HH/HV ratio collapse + dark after
        ratio_b, ratio_a = hh_b - hv_b, hh_a - hv_b
        d_ratio = ratio_a - ratio_b
        report("ratio: d(HH-HV)<=-2 & after<=-12dB & !perm",
               valid & ~permanent & (d_ratio <= -2.0) & (hh_a <= -12.0), pixel_km2)
        # 7. both-pol agreement
        report("both: dHH<=-2 & dHV<=-2 & after<=-12 & !perm",
               valid & ~permanent & (diff <= -2.0) & (hv_diff <= -2.0) & (hh_a <= -12.0),
               pixel_km2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
