---
tags:
  - ops
---

# Runbook: Snyder change image

## When to use

After the two GCOV `.h5` files are in `data/snyder/gcov/`. Produces the log-ratio PNG, confidence PNG, and km² GeoJSON.

## Steps

1. `source venv/bin/activate`
2. `python scripts/fetch_snyder_perimeter.py` — only if `ref/snyder/nifc_wfigs_snyder.geojson` is missing
3. `python scripts/change_snyder.py`
4. Open `outputs/snyder/change.png` and `outputs/snyder/summary.json`
5. Optional second vote: `python scripts/download_gunw.py` then re-run step 3

## If it fails

- Missing `.h5` → [[docs/Get the data]]
- Missing perimeter → fetch script or copy from `ref/snyder/`
- `Not logged in` on GUNW download → [[Runbooks/Earthdata login]]

## Related

- [[research/Change detection]]
- [[research/Snyder perimeter]]
- [[docs/Processing pipeline]]
- [[Runbooks]]
