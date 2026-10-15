# EchoLens

NASA Space Apps Toronto 2026 — **Dancing with the SARs**. Track surface change with NISAR radar.

Working notes: `notes/` (Obsidian). Start at `notes/00 Home.md`. **Full teammate data guide:** `notes/docs/Get the data.md`.

Do not put Earthdata passwords or `.h5` granules in git.

## Get the Snyder data

Needs Python 3.11+, ~16 GB disk, a free [Earthdata](https://urs.earthdata.nasa.gov/) account. Authorize **ASF DAAC** in Earthdata Applications if asked.

```text
git clone https://github.com/umeraamir69/Nasa-SpaceApp.git
cd Nasa-SpaceApp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python -c "import earthaccess; earthaccess.login(persist=True)"

python scripts/search_nisar.py --event snyder
python scripts/download_nisar.py
python scripts/inspect_h5.py
python scripts/preview_gcov.py
python scripts/crop_snyder.py
python scripts/pipeline_snyder.py
```

Or, after the two `.h5` files are already on disk: `python scripts/pipeline_snyder.py` (perimeter + change + cloudy Sentinel-2). Files land in `data/snyder/gcov/` (~7 GB × 2). `data/` is gitignored. Panoply cannot open these HDF5 files; use the preview PNGs. Change image and GeoJSON: `outputs/snyder/`.

| Script | Role |
|---|---|
| `scripts/search_nisar.py` | Search only |
| `scripts/download_nisar.py` | Snyder GCOV pair |
| `scripts/inspect_h5.py` | HDF5 tree / identity |
| `scripts/preview_gcov.py` | 80 m PNGs |
| `scripts/crop_snyder.py` | Crop to Snyder fire box |
| `scripts/fetch_snyder_perimeter.py` | NIFC WFIGS Snyder polygon |
| `scripts/change_snyder.py` | Log-ratio + confidence + GeoJSON |
| `scripts/fetch_optical.py` | Cloudy Sentinel-2 TCI (why-SAR) |
| `scripts/pipeline_snyder.py` | Perimeter + change + optical (no download) |
| `scripts/download_gunw.py` | GUNW coherence (second vote) |

Locked pair: track `048_A_021`, 17 Jun 2026 and 23 Jul 2026, collection `NISAR_L2_GCOV_PROVISIONAL_V1`.

## Run the map

```text
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```text
cd web
npm install --cache ../.npm-cache
npm run dev
```

Open http://127.0.0.1:5173. API: http://127.0.0.1:8000/api/case. Pitch script: `notes/docs/Pitch.md`. Team-page paste: `notes/docs/Team page.md`. Weekend kit: `notes/Runbooks/Weekend kit.md`.

## Layout

| Path | What |
|---|---|
| `notes/` | Project brain |
| `scripts/` | Search, download, change |
| `data/` | Local granules (gitignored) |
| `ref/snyder/` | NIFC WFIGS perimeter (cited) |
| `outputs/snyder/` | Change PNG, confidence, GeoJSON, map layers |
| `app/` | FastAPI |
| `web/` | Vite + React + Leaflet |
