---
tags:
  - ops
---

# Runbook: Download NISAR (manual)

The data is **not in the cloud folder we search**. Search only returns granule IDs. Files land on disk under:

`data/snyder/gcov/` (under the repo root; gitignored)

That folder is gitignored. Each Snyder GCOV granule is about **7 GB**. The pair is ~14.5 GB.

## What to download (Snyder, track 048_A_021)

| When | Granule |
|---|---|
| Before (17 Jun 2026) | `NISAR_L2_PR_GCOV_023_048_A_021_4005_DHDH_A_20260617T122757_20260617T122831_P05023_N_F_J_001` |
| After (23 Jul 2026) | `NISAR_L2_PR_GCOV_026_048_A_021_4005_DHDH_A_20260723T122754_20260723T122829_P05023_N_F_J_001` |

Product: `NISAR_L2_GCOV_PROVISIONAL_V1`

## Manual — ASF Vertex (easiest)

1. Open https://search.asf.alaska.edu/
2. Sign in with **your** Earthdata account.
3. Dataset: **NISAR** → collection **GCOV Provisional**.
4. Draw a box on the CO–UT border (Westwater / Mesa County) or paste bbox `-109.45,38.85,-108.55,39.50`.
5. Date filters: `2026-06-17` to `2026-06-26`, then again `2026-07-18` to `2026-07-26`.
6. Find the two granule names above (look for `048_A_021`).
7. Click the download icon. If ASF asks you to authorize the application / accept a EULA, do that once.
8. Move the `.h5` files into `data/snyder/gcov/`.

## Manual — Earthdata Search

1. Open https://search.earthdata.nasa.gov/
2. Search collection `NISAR_L2_GCOV_PROVISIONAL_V1`.
3. Spatial: same bbox. Temporal: the two windows above.
4. Add the two granules to the project → Download.
5. Same destination: `data/snyder/gcov/`.

## Script (already running or repeat later)

```text
cd <repo root>
source venv/bin/activate
python scripts/download_nisar.py
```

Needs `~/.netrc` from the Earthdata login. Does not re-download files that already finished.

## If download fails

- Authorize **ASF DAAC** / **Earthdata Search** under Earthdata → Applications / EULAs.
- Do not mix BETA and PROVISIONAL in one pair.
- Do not download Thunder Bay until the Snyder pair is on disk.

Related: [[research/NISAR data access]] [[Runbooks/Earthdata login]]
