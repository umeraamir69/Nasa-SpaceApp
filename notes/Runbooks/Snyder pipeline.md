---
tags:
  - ops
---

# Runbook: Snyder pipeline (unattended)

## When to use

Re-build `outputs/snyder/` after a code change, or on a teammate machine that already has the two GCOV `.h5` files. Does **not** download NISAR.

## Steps

From the repo root, venv on:

```text
python scripts/pipeline_snyder.py
```

That runs, in order:

1. `fetch_snyder_perimeter.py` — NIFC WFIGS polygon
2. `change_snyder.py` — despeckle, HVHV log-ratio, GeoJSON, map PNGs
3. `fetch_optical.py` — cloudy Sentinel-2 TCI for the Optical chip

Then start the app: [[Runbooks/Run the app]]

## If it fails

- “Need two GCOV .h5 files” — follow [[docs/Get the data]]; this script will not download ~14 GB
- Optical STAC/AWS timeout — change products still work; Optical chip hides until `outputs/snyder/layers/optical.png` exists
- Disk full — do not run Frequency A (10 m) or a Thunder Bay download on a nearly full volume

## Related

- [[Runbooks]]
- [[research/Why SAR optical]]
- [[docs/Processing pipeline]]
