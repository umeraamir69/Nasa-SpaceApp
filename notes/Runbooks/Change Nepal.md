---
tags:
  - ops
---

# Runbook: Nepal GLOF change

## When to use

After the two `048_D_074` GCOV `.h5` files are in `data/nepal/gcov/` and proof polygons exist. Produces HH log-ratio PNG and km² GeoJSON. Snyder and Latvia products are not touched.

## Steps

1. `python scripts/fetch_nepal_proof.py` — Copernicus EMSR927 + HOT 27 Aug flood
2. `python scripts/crop_nepal.py` — HTTPS range-read of the Rasuwa crop (skip if `data/nepal/crop/*.npz` exists)
3. `python scripts/change_nepal.py`
4. Open `outputs/nepal/summary.json`

## If it fails

- missing crop — `python scripts/crop_nepal.py` (do **not** `download_nepal.py` on a disk with <16 GB free; those frames are ~7 GB each)
- `need 2 048_D_074` — only if you meant to use local `.h5`; otherwise run `crop_nepal.py`
- `missing proof polygons` — `python scripts/fetch_nepal_proof.py`
- `GLOF box is outside the raster` — wrong frame; do not use `048_D_075` as the locked pair
- `no common polarisation` — after pass is QPDH; inspect frequencyB keys with `scripts/inspect_h5.py`

## Related

- [[docs/Task 3]]
- [[research/Flood candidates]]
- [[Runbooks]]
