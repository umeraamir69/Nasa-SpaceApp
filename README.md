# EchoLens

NASA Space Apps Toronto 2026 — **Dancing with the SARs**. Two NISAR radar passes in, an incident briefing out.

**New here? Read [docs/a-to-z.md](docs/a-to-z.md)** — the complete plain-language guide (what we did, how, the numbers, how we compare). Working notes (Obsidian): `notes/` → `notes/00 Home.md`. Do not put Earthdata passwords or `.h5` granules in git.

## The 6 cases

| Case | Type | Pair | Verdict | Headline |
|---|---|---|---|---|
| Snyder Fire | Wildfire | 17 Jun → 23 Jul 2026, HV | Detected | 40.9 km², precision 1.00 vs NIFC + NIROPS |
| Thunder Bay 36 | Wildfire | 11 Jul → 16 Aug 2026, HV | Detected | 235 km² severe core (~7% of complex) |
| Nepal Rasuwa GLOF | Glacier flood | 19 → 31 Aug 2026, HH | Detected | 2.4 km², precision 0.99 vs HOT flood |
| Latvia flood | Flood | 18 → 30 Aug 2026, HH | Negative | post-peak dry-down, proven over 7 methods |
| Crete flood | Flash flood | 27 Sep → 9 Oct 2026, HH | Negative | drained before Oct 9 (truth itself: no darkening) |
| Isaias surge | Hurricane | 30 Sep → 12 Oct 2026, HH | Marginal | 0.5 km² bay fringe, unvalidated |

All pairs are same-track / same-mode, verified by `scripts/granule_modes.py`.

## Run it (~2 min)

Needs Python 3.11+ and Node 18+. Map products (`outputs/`, ~30 MB) are in this repo — no NASA login needed to view.

```text
git clone https://github.com/umeraamir69/Nasa-SpaceApp.git
cd Nasa-SpaceApp
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Terminal 1 (API):

```text
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2 (web):

```text
cd web
npm install --cache ../.npm-cache
npm run dev -- --host 127.0.0.1 --port 5173
```

Open http://127.0.0.1:5173 — case tabs, layer dock, swipe slider, fragment inspector, guided **Pitch** mode (arrow keys work).

No servers? Open any `outputs/*/layers/change.png`.

## Reproduce from NASA (optional)

Earthdata account + ~15–35 GB free. Authorize **ASF DAAC** in Earthdata Applications. Credentials via env vars only (`EARTHDATA_USERNAME` / `EARTHDATA_PASSWORD`) — never in files.

```text
python scripts/search_nisar.py --event snyder        # find the pair
python scripts/download_nisar.py                     # ~14 GB to data/snyder/gcov/
python scripts/change_snyder.py                      # → outputs/snyder/
```

Per-case pairs (`download_*.py` → `change_*.py`): latvia (`080_D_059`), nepal (`098_A_016` + `fetch_nepal_proof.py`), thunderbay (`041_D_063`), crete (`137_D_071` + `fetch_crete_proof.py`), isaias (`004_A_017`). Validation: `validate_slopes.py`, `threshold_sweep.py`, `experiment_latvia.py`.

Processing (h5py/rasterio/shapely) needs the pinned env: `.conda/env/bin/python` (Python 3.12; the default venv is a 3.16 alpha that cannot build numpy/Pillow). App/tests run on `venv/bin/python`.

## Verify

```text
venv/bin/python -m unittest discover -s tests   # 9 tests, <1 s
cd web && npm run build
```

Live end-to-end probe (104 checks over all cases/layers/GeoJSON): `/tmp/check_all_cases.py` against running servers.

## Scripts

| Script | Role |
|---|---|
| `scripts/search_nisar.py` | Find same-track pairs per event (CMR) |
| `scripts/granule_modes.py` | Same-mode guard — refuses cross-mode pairs |
| `scripts/download_nisar.py` / `download_latvia.py` / `download_nepal.py` | Fetch GCOV pairs (generic flags on nepal's) |
| `scripts/change_snyder.py` / `change_thunderbay.py` | HV fire log-ratio + confidence + GeoJSON |
| `scripts/change_latvia.py` / `change_nepal.py` / `change_crete.py` / `change_isaias.py` | HH flood log-ratio + masks + GeoJSON |
| `scripts/download_aux.py` | Generic SME2/GUNW granule downloader |
| `scripts/xcheck_sme2.py` | Soil-moisture cross-check vs SME2 beta (deltas) |
| `scripts/xcheck_gunw.py` | GUNW coherence second vote for flood cases |
| `scripts/experiment_latvia.py` | 7-rule water-index comparison (raw granules) |
| `scripts/threshold_sweep.py` | precision/recall/IoU vs truth at many dB cuts |
| `scripts/validate_slopes.py` | DEM slope audit per case |
| `scripts/validate_snyder.py` / `validate_latvia.py` | Overlap scores vs NIFC/NIROPS, rivers null test |
| `scripts/fetch_optical.py --case X` | Cloudy Sentinel-2 TCI (the why-SAR layer) |
| `scripts/fetch_snyder_ir.py` / `fetch_snyder_perimeter.py` / `fetch_nepal_proof.py` / `fetch_crete_proof.py` | Truth polygons |
| `scripts/crop_nepal.py` / `crop_snyder.py` / `preview_gcov.py` / `inspect_h5.py` | Crops, previews, HDF5 inspection |
| `scripts/fix_layer_frames.py` | Idempotent layer-frame registration fixes |
| `scripts/pipeline_snyder.py` / `download_gunw.py` | Unattended Snyder run / coherence second vote |

## Layout

| Path | What |
|---|---|
| `docs/a-to-z.md` | Complete plain-language guide |
| `notes/` | Project brain (Obsidian) |
| `scripts/` | Search, download, change, validate |
| `data/` | Local granules (gitignored, ~35 GB) |
| `outputs/<case>/` | `summary.json`, `change.geojson`, `layers/*.png` (in git) |
| `app/` | FastAPI (`/api/cases`, `/api/case`, `/api/geojson/*`) |
| `web/` | Vite + React + Leaflet briefing console |
| `tests/` | Asset + API contract tests |
