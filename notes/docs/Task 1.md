---
tags:
  - docs
  - ops
  - onboarding
date: 2026-10-15
---

# Task 1 — Snyder: reproduce and see

This is the **first EchoLens deliverable**. Everyone on the team should be able to open the Snyder map and, if they have disk, rebuild it from NASA.

Repo: https://github.com/umeraamir69/Nasa-SpaceApp  
Challenge: Dancing with the SARs. Primary event: Snyder Fire (CO–UT), 17 Jun → 23 Jul 2026, NISAR track `048_A_021`.

**Do not** put Earthdata passwords, tokens, or `.h5` files in git, chat, or this vault.

There are **two tracks**. Most teammates only need Track A.

| Track | Time | Disk | What you get |
|---|---|---|---|
| **A — See it** | ~15 min | ~200 MB (`venv` + `node_modules`) | Live map at http://127.0.0.1:5173 |
| **B — Reproduce it** | ~30 min + download | **~16 GB** | Same map, rebuilt from the two GCOV granules |

Flood is **Task 2** ([[docs/Task 2]]). Thunder Bay is not started.

On 15 Oct this machine **deleted the Snyder `.h5` granules** (~16 GB) so the Latvia pair could fit. `outputs/snyder/` is still in git — **Track A still works**. Track B on this laptop must run `python scripts/download_nisar.py` again before `pipeline_snyder.py`.

---

## Track A — See the map (no NASA download)

`outputs/snyder/` is **in git** (~4 MB). You do **not** need Earthdata for this.

Needs: git, **Python 3.11+**, **Node 18+**.

```text
git clone https://github.com/umeraamir69/Nasa-SpaceApp.git
cd Nasa-SpaceApp
git pull

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Terminal 1 (repo root):

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

Open **http://127.0.0.1:5173**

Leave it loading until the briefing shows numbers (first paint ~15 s). Then:

1. **Change** + **NIFC perimeter** on — yellow official outline, blue scar inside it.
2. Before → After → Change → Confidence → **Optical**.
3. Optical: white is cloud (Sentinel-2 7 Jul).
4. Toggle NIFC off/on once. End on **Change**.

If the page is `ERR_CONNECTION_REFUSED`, Vite is not running. Restart terminal 2. [[Runbooks/Run the app]]

### You are done with Task 1-see when

The briefing shows **all** of these (from `outputs/snyder/summary.json`):

| Field | Must show |
|---|---|
| Before / after | 2026-06-17 → 2026-07-23 |
| EchoLens change | **40.9 km²** |
| NIFC GIS area | **122.2 km²** |
| Precision vs NIFC | **1.00** (no pixels outside the official line) |
| HVHV inside perimeter | **−1.24 dB** |
| Optical cloud cover | **34% · Sentinel-2 7 Jul** |

Also: InciWeb / NIFC WFIGS / Ops maps links under Source. Legend: *Blue: darker after the fire · red: brighter (not burn)*.

No map? Open `outputs/snyder/change.png` in any image app. Same scar, no server.

Quick API check:

```text
curl -s http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1:8000/api/case | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['area_km2'], d['has_optical'])"
```

Expect `40.934` and `True`.

---

## Track B — Reproduce from NASA (optional)

Only if you want to **rebuild** `outputs/snyder/` from the radar files. Track A is enough to demo.

Needs: Earthdata account, **~16 GB free**, ASF DAAC authorized.

### B1. Login (once per laptop)

1. https://urs.earthdata.nasa.gov/ — free account.
2. Earthdata → Applications → authorize **ASF DAAC** (401 until you do).
3. Type the password yourself. Never paste it in Discord or notes.

```text
source venv/bin/activate
python -c "import earthaccess; earthaccess.login(persist=True)"
```

Writes `~/.netrc` (mode 600). [[Runbooks/Earthdata login]]

### B2. Search, then download the locked pair

```text
python scripts/search_nisar.py --event snyder
python scripts/download_nisar.py
python scripts/inspect_h5.py
```

Search must list GCOV granules. Download writes `data/snyder/gcov/` (~7 GB × 2). `data/` is gitignored.

Locked files (names must contain):

```text
048_A_021 ... 20260617 ...   # before, ~6.9 GB
048_A_021 ... 20260723 ...   # after,  ~7.1 GB
```

`inspect_h5.py` should print `trackNumber: 48` and June or July `zeroDopplerStartTime`. Collection: `NISAR_L2_GCOV_PROVISIONAL_V1` — **not** Beta.

Panoply **cannot** open these `.h5` files. That is expected. [[Runbooks/Open H5 files]]

Optional look (no app):

```text
python scripts/preview_gcov.py
python scripts/crop_snyder.py
```

PNGs: `data/snyder/preview/` and `data/snyder/preview/crop/`.

### B3. Rebuild products + optical

```text
python scripts/pipeline_snyder.py
```

That runs NIFC perimeter → log-ratio change → cloudy Sentinel-2. Writes `outputs/snyder/` (overwrites). Then go back to Track A and start the two servers.

GUNW (coherence, second vote, extra ~2.3 GB) is **optional**:

```text
python scripts/download_gunw.py
python scripts/change_snyder.py
```

On Snyder, GUNW barely splits the scar (0.73 vs 0.76). Detection stays on GCOV HV. [[research/Change detection]]

Full download notes: [[docs/Get the data]] [[Runbooks/Download NISAR]] [[Runbooks/Snyder pipeline]]

---

## Folder map (after Task 1)

```text
Nasa-SpaceApp/
  app/main.py                 FastAPI
  web/                        Vite + React + Leaflet
  scripts/download_nisar.py   Track B
  scripts/pipeline_snyder.py  Track B rebuild
  outputs/snyder/             IN GIT — map + PNGs + GeoJSON
    summary.json
    change.geojson
    change.png
    layers/{before,after,change,confidence,optical}.png
  ref/snyder/                 NIFC WFIGS polygon (cited)
  data/snyder/gcov/           NOT IN GIT — only after Track B
  notes/docs/Task 1.md        this file
  notes/docs/Pitch.md         3-minute script
```

---

## If it fails

| What you see | What to do |
|---|---|
| `ERR_CONNECTION_REFUSED` on :5173 | Terminal 2 / Vite is down. `npm run dev` again |
| Briefing: `API: 404` / missing layers | `outputs/snyder/` missing — `git pull` or run Track B |
| No **Optical** chip | `outputs/snyder/layers/optical.png` missing — `python scripts/fetch_optical.py` (small, no Earthdata) |
| `Not logged in` on download | `earthaccess.login(persist=True)` |
| 401 on download | Earthdata → Applications → ASF DAAC |
| Empty search | Wrong product. Must be `NISAR_L2_GCOV_PROVISIONAL_V1` |
| `partial_*` in `data/snyder/gcov/` | Download interrupted. Re-run `download_nisar.py` |
| npm `EACCES` | `npm install --cache ../.npm-cache` — do not sudo |
| Panoply dimscale error | Ignore Panoply. Use the PNGs / the map |
| Want flood | [[docs/Task 2]] — `python scripts/download_latvia.py` then `change_latvia.py`. Do not download Thunder Bay on this disk |

---

## Pitch while you look

Script: [[docs/Pitch]]. Click path is Track A steps 1–4. Do not discover Snyder for judges — sell the method.

Related: [[docs/Get the data]] [[Runbooks/Run the app]] [[docs/Processing pipeline]] [[research/Snyder perimeter]] [[docs/Team page]]
