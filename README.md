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
```

Files land in `data/snyder/gcov/` (~7 GB × 2). `data/` is gitignored. Panoply cannot open these HDF5 files; use the preview PNGs in `data/snyder/preview/`.

| Script | Role |
|---|---|
| `scripts/search_nisar.py` | Search only |
| `scripts/download_nisar.py` | Snyder GCOV pair |
| `scripts/inspect_h5.py` | HDF5 tree / identity |
| `scripts/preview_gcov.py` | 80 m PNGs |
| `scripts/crop_snyder.py` | Crop to Snyder fire box |

Locked pair: track `048_A_021`, 17 Jun 2026 and 23 Jul 2026, collection `NISAR_L2_GCOV_PROVISIONAL_V1`.

## Layout

| Path | What |
|---|---|
| `notes/` | Project brain |
| `scripts/` | Search, download, preview |
| `data/` | Local granules (gitignored) |
