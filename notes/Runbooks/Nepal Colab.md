---
tags:
  - ops
---

# Runbook: Nepal GLOF on Google Colab

## When to use

Laptop disk cannot hold the `048_D_074` pair (~7 GB × 2). Colab machines have ~80 GB. Use this to **download the granules in the cloud**, then pull back only the small Rasuwa crop.

The map on the laptop already runs from `outputs/nepal/` (and `data/nepal/crop/*.npz` if present). You do not need the 14 GB files to demo.

## Steps

1. Open `notebooks/nepal_glof_colab.ipynb` in [Google Colab](https://colab.research.google.com/).
2. Runtime → default CPU is enough (disk matters, not GPU).
3. Run the install cell, then the Earthdata login cell. Use **your** account. Do not paste a password into a cell.
4. Run the download cell. Expect ~15–40 min for both `.h5` files under `/content/nepal/gcov/`.
5. Run the crop cell. Download `before.npz` / `after.npz` (~1.3 MB each).
6. On the laptop: put them in `data/nepal/crop/` and run `python scripts/change_nepal.py`.

Optional Drive copy is commented out — only if Drive has ~14 GB free.

## If it fails

- Login loop — authorize ASF DAAC on https://urs.earthdata.nasa.gov/ under Applications.
- Colab disk full — you started extra datasets. Runtime → Disconnect and delete runtime, then only this notebook.
- `no 048_D_074` — Earthdata search glitch; re-run the search cell.

## Related

- [[docs/Task 3]]
- [[Runbooks/Change Nepal]]
- [[Runbooks]]
