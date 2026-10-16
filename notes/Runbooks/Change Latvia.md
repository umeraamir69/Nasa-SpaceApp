---
tags:
  - ops
---

# Runbook: Latvia flood change

## When to use

After the two `080_D_059` GCOV `.h5` files are in `data/latvia/gcov/`. Produces HH log-ratio PNG, lake mask, and km² GeoJSON. Snyder products are not touched.

## Steps

1. `source venv/bin/activate`
2. `python scripts/download_latvia.py` — skip if the two `080_D_059` files are already there
3. `python scripts/change_latvia.py`
4. Open `outputs/latvia/summary.json` — expect ~6.5 km² new water, ~34 km² lakes
5. Restart uvicorn; click **Latvia flood** on http://127.0.0.1:5173

## If it fails

- Empty crop / 0 km² — you grabbed `071_A_030`. Delete those `.h5` files and download `080_D_059` only.
- `need 2 080_D_059` — `python scripts/download_latvia.py`
- `Not logged in` — [[Runbooks/Earthdata login]]

## Related

- [[docs/Task 2]]
- [[research/Flood candidates]]
- [[Runbooks]]
