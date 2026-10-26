---
tags:
  - docs
  - ops
  - onboarding
---

# Get the data (for teammates)

**Start at [[docs/Task 1]]** if you only need to **see** the Snyder map. `outputs/snyder/` is already in git. This page is **Track B**: clone, log in to NASA, and pull the **same two Snyder GCOV files**. The granules are **not in git** (~14 GB).

Repo: `https://github.com/umeraamir69/Nasa-SpaceApp`

Do **not** put Earthdata passwords, tokens, or `.h5` files in git or in this vault.

## 1. Clone and Python env

Needs Python 3.11+ (3.14 is fine), **~16 GB free** for the GCOV pair, plus **~2.5 GB** if you also pull GUNW, and a NASA Earthdata account.

```text
git clone https://github.com/umeraamir69/Nasa-SpaceApp.git
cd Nasa-SpaceApp
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`data/` is gitignored. After clone it is empty except `.gitkeep`.

## 2. Earthdata login (once per machine)

1. Create a free account: https://urs.earthdata.nasa.gov/
2. In Earthdata → Applications, authorize **ASF DAAC** if it asks. Downloads fail with 401 until you do.
3. On your laptop (interactive — type the password yourself, never paste it in chat or notes):

```text
source venv/bin/activate
python -c "import earthaccess; earthaccess.login(persist=True)"
```

That writes `~/.netrc` (mode 600). The scripts then use `strategy=netrc`. Optional instead of netrc: env vars `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` in your shell only, never in `.env` committed to git.

## 3. Scripts (run from repo root, venv on)

| Script | What it does | Command |
|---|---|---|
| `scripts/search_nisar.py` | Lists granules. **No download.** | `python scripts/search_nisar.py --event snyder` |
| `scripts/download_nisar.py` | Downloads the locked Snyder GCOV pair (~7 GB × 2) | `python scripts/download_nisar.py` |
| `scripts/inspect_h5.py` | Prints layers / date / track. Does not load 10 m. | `python scripts/inspect_h5.py` |
| `scripts/preview_gcov.py` | 80 m June / July / difference PNGs | `python scripts/preview_gcov.py` |
| `scripts/crop_snyder.py` | Crops 80 m to the Snyder fire box | `python scripts/crop_snyder.py` |
| `scripts/fetch_snyder_perimeter.py` | Official NIFC WFIGS Snyder polygon | `python scripts/fetch_snyder_perimeter.py` |
| `scripts/change_snyder.py` | Despeckle + log-ratio + mask + GeoJSON | `python scripts/change_snyder.py` |
| `scripts/fetch_optical.py` | Cloudy Sentinel-2 TCI (Snyder default; Latvia: `--case latvia`) | `python scripts/fetch_optical.py` |
| `scripts/fetch_snyder_ir.py` | NIROPS airborne IR GeoJSON | `python scripts/fetch_snyder_ir.py` |
| `scripts/pipeline_snyder.py` | Perimeter + change + optical (no NISAR download) | `python scripts/pipeline_snyder.py` |
| `scripts/download_gunw.py` | Same-track GUNW (coherence second vote) | `python scripts/download_gunw.py` |
| `scripts/open_panoply.sh` | Panoply on Java 21. **Panoply cannot open these .h5 files.** | skip for data |

Search stretches. Nepal GLOF is Task 3 (`python scripts/download_nepal.py`, ~14 GB). Laptop full → `python scripts/crop_nepal.py` or [[Runbooks/Nepal Colab]]. Thunder Bay still needs ~14 GB — do not grab it here.

```text
python scripts/search_nisar.py --event thunder-bay
python scripts/search_nisar.py --event latvia-flood
python scripts/search_nisar.py --event nepal-glof
```

## 4. What you should have after download

Folder: `data/snyder/gcov/`

| Role | File (name must contain) | Size |
|---|---|---|
| Before | `...048_A_021...20260617....h5` | ~6.9 GB |
| After | `...048_A_021...20260723....h5` | ~7.1 GB |

Exact granule UR:

```text
NISAR_L2_PR_GCOV_023_048_A_021_4005_DHDH_A_20260617T122757_20260617T122831_P05023_N_F_J_001
NISAR_L2_PR_GCOV_026_048_A_021_4005_DHDH_A_20260723T122754_20260723T122829_P05023_N_F_J_001
```

Collection: `NISAR_L2_GCOV_PROVISIONAL_V1` (Provisional, **not** Beta). Same track `048_A_021`.

Check:

```text
ls -lh data/snyder/gcov/
python scripts/inspect_h5.py
```

`inspect` should print `trackNumber: 48` and a June or July `zeroDopplerStartTime`. If a `partial_*` file is sitting there, the download was interrupted — run `download_nisar.py` again (`force` is off, finished files are skipped).

## 5. Look at the radar (do not use Panoply)

These NISAR files break Panoply (`yCoordinates` dimscale mismatch). Use the scripts:

```text
python scripts/preview_gcov.py
python scripts/crop_snyder.py
```

PNGs land in `data/snyder/preview/` and `data/snyder/preview/crop/`. Open those in Preview / any image app. We already confirmed a coherent change pattern in the crop — keep Snyder. [[research/Scar check]]

## 6. Browse the catalog without downloading

Same pair on the websites (look only):

- ASF Vertex: https://search.asf.alaska.edu/ — Dataset **NISAR**, Science Product **GCOV**, Maturity **Provisional**, scene `*048_A_021*`
- Dates: **2026-06-17 → 2026-06-26** (before), **2026-07-18 → 2026-07-26** (after)
- Box (W S E N): `-109.45, 38.85, -108.55, 39.50`
- Earthdata Search: https://search.earthdata.nasa.gov/search?q=NISAR_L2_GCOV_PROVISIONAL_V1

Click-by-click: [[Runbooks/Reproduce Snyder search]]

## 7. Git rules for data

- **Never** `git add data/*.h5`
- **Never** commit `~/.netrc`, `.env`, tokens, or passwords
- `data/**` is already in `.gitignore`
- Do not mix BETA + PROVISIONAL in one pair
- Do not download Thunder Bay until the app serves Snyder GeoJSON ([[research/Change detection]])

## If something fails

| Symptom | Fix |
|---|---|
| `Not logged in` | Re-run `earthaccess.login(persist=True)` |
| 401 / Authorization | Earthdata → Applications → approve ASF DAAC |
| Empty search | You used BETA or the wrong `short_name`. Must be `NISAR_L2_GCOV_PROVISIONAL_V1` |
| `partial_*` files | Re-run download; wait; ~14 GB total |
| Panoply dimscale error | Expected. Use `preview_gcov.py` |

Related: [[Runbooks/Earthdata login]] [[Runbooks/Download NISAR]] [[Runbooks/Snyder pipeline]] [[research/NISAR data access]] [[docs/Processing pipeline]]
