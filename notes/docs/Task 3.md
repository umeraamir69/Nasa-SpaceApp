---
tags:
  - docs
  - ops
  - onboarding
date: 2026-10-20
---

# Task 3 — Nepal GLOF (stretch, official proof)

Third case. **Snyder stays the pitch.** Latvia stays on the map. This chip is the flood with a published answer key: Copernicus **EMSR927** + HOT/UNOSAT Rasuwa 26–27 Aug 2026.

Event: glacier-lake outburst, Rasuwa, **26 Aug 2026**. Pair: NISAR GCOV track `048_D_074`, **16 Aug → 28 Aug 2026**. Before is `DHDH`, after is `QPDH` — change uses the common **HHHH** channel.

## See it

After `outputs/nepal/summary.json` exists, the map grows a **Nepal GLOF** chip.

```text
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```text
cd web && npm run dev -- --host 127.0.0.1 --port 5173
```

Open http://127.0.0.1:5173 — default is still Snyder. Click **Nepal GLOF**. Yellow **EMSR927** is Copernicus landslides along the gorge. Cyan **Official flood** is the HOT 27 Aug water polygon.

## Reproduce it

Needs Earthdata. Full granules are **~7 GB × 2** (not the ~3 GB plains frames). On this laptop use the range-read crop instead of `download_nepal.py`. Latvia **`.h5` granules** were deleted 20 Oct; Latvia **map products** in `outputs/latvia/` stay.

```text
python scripts/search_nisar.py --event nepal-glof
python scripts/fetch_nepal_proof.py
python scripts/crop_nepal.py      # Rasuwa box only; do not store 14 GB
python scripts/change_nepal.py
```

Writes `data/nepal/crop/*.npz` (gitignored) and `outputs/nepal/`. Then restart the API.

`python scripts/download_nepal.py` only if you have ~16 GB free. Do not download Thunder Bay.

## What you should see

Processed **20 Oct 2026** on this machine (range-read crop, not the 14 GB pair):

| | |
|---|---|
| Pair | `048_D_074` 16 Aug → 28 Aug 2026 |
| Polarization | HHHH (common to DHDH / QPDH), Frequency B, 80 m |
| EchoLens change | **0.5 km²** HH darkening inside official polygons |
| Official flood in crop | **13.5 km²** (HOT 27 Aug; full valley is 31.7 km²) |
| Precision vs flood | **0.97** |
| Recall vs flood | **0.04** — we under-map; 80 m gorge pixels are not specular water |
| Official proof | Copernicus EMSR927 observedEvent (landslides) + HOT flood extent 27 Aug |
| Layover | Change only inside those official polygons (Snyder-style precision) |

Himalaya: slopes away from the river layover. We do not flag them. UNOSAT published mudflow and barrier-lake FileGDBs for the same dates (not inlined — FileGDB). Cite the HDX pages.

Open `outputs/nepal/change.png` if the servers are down.

Related: [[research/Flood candidates]] [[docs/Task 2]] [[docs/Task 1]]
