# EchoLens

NASA Space Apps Toronto 2026 — **Dancing with the SARs**. Two NISAR radar passes in, an incident briefing out.

**Teammates start here: [Task 1 — Snyder: reproduce and see](notes/docs/Task%201.md).**

Working notes (Obsidian): `notes/` → `notes/00 Home.md`. Do not put Earthdata passwords or `.h5` granules in git.

## Task 1 — two tracks

The Snyder map products (`outputs/snyder/`, ~4 MB) **are in this repo**. You can **see** the demo without NASA login. Rebuilding from radar needs ~16 GB and Earthdata.

### A — See it (~15 min)

Needs Python 3.11+ and Node 18+.

```text
git clone https://github.com/umeraamir69/Nasa-SpaceApp.git
cd Nasa-SpaceApp
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Terminal 1:

```text
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```text
cd web
npm install --cache ../.npm-cache
npm run dev -- --host 127.0.0.1 --port 5173
```

Open http://127.0.0.1:5173

You should see Snyder Fire, **40.9 km²** EchoLens change, **122.2 km²** NIFC, precision **1.00**, Optical cloud **34%**. Click Change → Before → After → Confidence → Optical. If Vite is down you get `ERR_CONNECTION_REFUSED` — start terminal 2 again.

No servers? Open `outputs/snyder/change.png`.

### B — Reproduce from NASA (optional)

Earthdata account + **~16 GB** free. Authorize **ASF DAAC** in Earthdata Applications.

```text
python -c "import earthaccess; earthaccess.login(persist=True)"
python scripts/search_nisar.py --event snyder
python scripts/download_nisar.py
python scripts/inspect_h5.py
python scripts/pipeline_snyder.py
```

Then run Track A servers again. Granules land in `data/snyder/gcov/` (gitignored, ~7 GB × 2). Panoply cannot open these `.h5` files — use the map or the PNGs.

Locked pair: track `048_A_021`, 17 Jun 2026 and 23 Jul 2026, `NISAR_L2_GCOV_PROVISIONAL_V1`.

Task 2 flood (after Snyder products are in git; granules are optional):

```text
python scripts/search_nisar.py --event latvia-flood
python scripts/download_latvia.py
python scripts/change_latvia.py
```

Nepal GLOF (after Latvia **granules** are off this disk; Latvia products stay):

```text
python scripts/search_nisar.py --event nepal-glof
python scripts/fetch_nepal_proof.py
python scripts/crop_nepal.py
python scripts/change_nepal.py
```

Do not download Thunder Bay on the same disk. Full tables: `notes/docs/Task 1.md`. Task 2: `notes/docs/Task 2.md`. Task 3: `notes/docs/Task 3.md`. Pitch: `notes/docs/Pitch.md`.

## Scripts

| Script | Role |
|---|---|
| `scripts/search_nisar.py` | Search only |
| `scripts/download_nisar.py` | Snyder GCOV pair |
| `scripts/inspect_h5.py` | HDF5 tree / identity |
| `scripts/preview_gcov.py` | 80 m PNGs |
| `scripts/crop_snyder.py` | Crop to Snyder fire box |
| `scripts/fetch_snyder_perimeter.py` | NIFC WFIGS Snyder polygon |
| `scripts/change_snyder.py` | Log-ratio + confidence + GeoJSON |
| `scripts/fetch_optical.py` | Cloudy Sentinel-2 TCI (why-SAR; `--case latvia` for flood) |
| `scripts/fetch_snyder_ir.py` | NIROPS airborne IR (30 Jun + 7 Jul) |
| `scripts/pipeline_snyder.py` | Perimeter + change + optical (no download) |
| `scripts/download_gunw.py` | GUNW coherence (second vote) |
| `scripts/download_latvia.py` | Latvia flood GCOV pair `080_D_059` |
| `scripts/change_latvia.py` | HH flood log-ratio + lake mask |
| `scripts/download_nepal.py` | Nepal GLOF full granules (~7 GB × 2) — skip on a small disk |
| `scripts/crop_nepal.py` | Nepal GLOF Rasuwa crop via HTTPS range-read |
| `scripts/fetch_nepal_proof.py` | Copernicus EMSR927 + HOT 27 Aug flood |
| `scripts/change_nepal.py` | HH GLOF log-ratio + official corridor |

## Layout

| Path | What |
|---|---|
| `notes/` | Project brain (Obsidian) |
| `notes/docs/Task 1.md` | **Teammate onboarding** |
| `scripts/` | Search, download, change |
| `data/` | Local granules (gitignored) |
| `ref/snyder/` | NIFC WFIGS perimeter (cited) |
| `outputs/snyder/` | Snyder change PNG, GeoJSON, map layers (in git) |
| `outputs/latvia/` | Latvia flood products (in git once committed) |
| `outputs/nepal/` | Nepal GLOF products + EMSR927 / flood GeoJSON |
| `app/` | FastAPI |
| `web/` | Vite + React + Leaflet |
