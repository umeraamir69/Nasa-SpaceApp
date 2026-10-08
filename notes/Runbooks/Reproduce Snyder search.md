---
tags:
  - ops
---

# Runbook: Reproduce the Snyder GCOV pair on the websites

Same two files we already have in `data/snyder/gcov/`. Use **either** site. Sign in with Earthdata first.

## Copy these values

| Field | Value |
|---|---|
| Collection / short name | `NISAR_L2_GCOV_PROVISIONAL_V1` |
| Product | GCOV (Geocoded Polarimetric Covariance) |
| Maturity | **Provisional** — not Beta |
| Place | Snyder Fire, CO–UT border (Westwater / Mesa County) |
| Bounding box (W, S, E, N) | `-109.45, 38.85, -108.55, 39.50` |
| Track / frame | `048` ascending, frame `021` — look for `048_A_021` in the name |
| Before window | **2026-06-17** → **2026-06-26** |
| After window | **2026-07-18** → **2026-07-26** |

Exact granules (search for these strings if the site has a filename filter):

```text
NISAR_L2_PR_GCOV_023_048_A_021_4005_DHDH_A_20260617T122757_20260617T122831_P05023_N_F_J_001
NISAR_L2_PR_GCOV_026_048_A_021_4005_DHDH_A_20260723T122754_20260723T122829_P05023_N_F_J_001
```

Each `.h5` is about **7 GB**. Do not pick BETA products. Do not pick a different track.

---

## A. ASF Vertex (easier)

1. Open [search.asf.alaska.edu](https://search.asf.alaska.edu/).
2. Click **Sign in** → Earthdata Login.
3. If asked to authorize **ASF DAAC** / accept a EULA, accept it.
4. Top-left **Dataset**: choose **NISAR**.
5. **Filters** (left or Filters button):
   - **Science Product**: `GCOV (Geocoded Polarimetric Covariance)`
   - **Data Maturity**: `Provisional`
   - **Direction**: `Ascending` (optional but helps)
6. **Area**: click the box tool on the map. Draw a box over the Utah–Colorado line, west of Grand Junction, around Westwater Canyon. Or use Area → Bounding Box and paste:
   - West `-109.45`  South `38.85`  East `-108.55`  North `39.50`
7. **Start date** `2026-06-17`  **End date** `2026-06-26`. Search.
8. In the results list, find the file whose name contains **`048_A_021`** and **`20260617`**. That is the before granule. Download the `.h5`.
9. Change dates only: Start `2026-07-18`  End `2026-07-26`. Search again.
10. Find **`048_A_021`** and **`20260723`**. Download that `.h5`.
11. Put both files in `/Users/muhamamd/Documents/nasa/data/snyder/gcov/`.

You will see other GCOV scenes in the box. Ignore anything that is not `048_A_021`.

---

## B. NASA Earthdata Search

1. Open [search.earthdata.nasa.gov](https://search.earthdata.nasa.gov/).
2. Sign in (same Earthdata account).
3. In the search bar type exactly: `NISAR_L2_GCOV_PROVISIONAL_V1` and press Enter.
4. Click that **one** collection (Provisional GCOV). Do not open the BETA collection.
5. Left panel → **Spatial**: Bounding Rectangle  
   `-109.45, 38.85, -108.55, 39.50`
6. **Temporal**: `2026-06-17` to `2026-06-26`.
7. Open **Granules**. Find `...048_A_021...20260617...`. Add to project / download the `.h5`.
8. Change temporal to `2026-07-18` to `2026-07-26`.
9. Find `...048_A_021...20260723...`. Download.
10. Same folder: `data/snyder/gcov/`.

If the granule list is long, paste `048_A_021` into the granule search/filter box.

Direct collection search:  
https://search.earthdata.nasa.gov/search?q=NISAR_L2_GCOV_PROVISIONAL_V1

---

## C. Same search from our script

```text
cd /Users/muhamamd/Documents/nasa
source venv/bin/activate
python scripts/search_nisar.py --event snyder
python scripts/download_nisar.py
```

That uses the same bbox, dates, and short name. It will skip files that already exist.

Related: [[Runbooks/Download NISAR]] [[research/NISAR data access]] [[decisions/ADR-002 Primary event Snyder Fire]]
