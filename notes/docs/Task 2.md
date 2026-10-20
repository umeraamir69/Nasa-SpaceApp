---
tags:
  - docs
  - ops
  - onboarding
date: 2026-10-15
---

# Task 2 — Latvia flood (stretch)

Second case. **Snyder stays the pitch.** Same method, different surface: new open water is darker HH after the storm.

Event: Latvia–Lithuania floods ~21–22 Aug 2026, Copernicus **EMSR926**. Pair: NISAR GCOV track `080_D_059`, **18 Aug → 30 Aug 2026**.

Snyder **map products** stay in git (`outputs/snyder/`). Snyder **granules** were deleted on this machine on 15 Oct to free disk. Latvia **granules** were deleted on 20 Oct so Nepal GLOF could fit; Latvia **map products** stay. Track A of [[docs/Task 1]] still works. Nepal: [[docs/Task 3]].

## See it

After `outputs/latvia/summary.json` exists, the map grows a **Latvia flood** chip next to Snyder.

```text
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```text
cd web && npm run dev -- --host 127.0.0.1 --port 5173
```

Open http://127.0.0.1:5173 — default is still Snyder. Click **Latvia flood**.

## Reproduce it

Needs Earthdata (same as Task 1) and ~5 GB free (these frames are ~2 GB each, not 7 GB).

```text
python scripts/search_nisar.py --event latvia-flood
python scripts/download_latvia.py
python scripts/change_latvia.py
```

Writes `data/latvia/gcov/` (gitignored) and `outputs/latvia/`. Then restart the API and use the Latvia chip.

Do **not** download `071_A_030` / `071_A_031` (wrong swath — valid HH starts ~24°E) or Thunder Bay on the same disk.

## What you should see

Processed **15 Oct 2026** on this machine:

| | |
|---|---|
| Pair | `080_D_059` 18 Aug → 30 Aug 2026 |
| Polarization | HHHH, Frequency B, 80 m |
| EchoLens new water | **6.5 km²** |
| Permanent lakes masked | **34.0 km²** |
| Box median HH | +0.20 dB (slightly brighter after) |

Peak flood was ~21–22 Aug. The after pass is **8 days later**, so this is residual new water, not the crest. The box median going slightly *brighter* is consistent with water receding. Copernicus EMSR926 vectors were still not on HDX as of 19 Oct — no official flood polygon. The map instead overlays **permanent lakes** (HH dark on both dates) and a cloudy Sentinel-2 scene from **21 Aug** (84% cloud).

Open `outputs/latvia/change.png` if the servers are down.

## How it differs from Snyder

| | Snyder | Latvia |
|---|---|---|
| Polarization | HVHV (burn) | HHHH (open water) |
| Threshold | 1.5 dB darker | 2 dB darker **and** after looks like water |
| Extra mask | NIFC + NIROPS IR | Permanent lakes (dark on **both** dates) |
| Optical | Sentinel-2 7 Jul (34% cloud) | Sentinel-2 21 Aug (84% cloud) |
| Answer key | NIFC WFIGS polygon | EMSR926 (vectors still not in HDX) |

Related: [[research/Flood candidates]] [[docs/Task 1]] [[decisions/ADR-003 Stretch flood Latvia]]
