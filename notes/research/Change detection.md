---
tags:
  - research
  - data
date: 2026-10-13
---

# Snyder GCOV change detection (offline POC)

Ran `python scripts/change_snyder.py` on 13 Oct 2026. No sklearn. No app.

## Method

1. Frequency B **80 m** HHHH + HVHV + `mask` from the locked `048_A_021` pair (17 Jun / 23 Jul).
2. Valid pixels: GCOV mask not `0` (partially focused) and not `255` (fill).
3. `10 * log10(power)`, then **3×3 median** despeckle.
4. Log-ratio: July dB − June dB.
5. Overlay [[research/Snyder perimeter]] (NIFC WFIGS `2026-UTDRD-005113`).
6. Sign comes from the median HVHV Δ **inside** that perimeter (it is a **drop**). Flag pixels with HVHV drop ≥ 1.5 dB; drop speckle islands smaller than 8 pixels (~5 ha).
7. Vectorize → GeoJSON. Area = pixel count × 80 m × 80 m.

GUNW coherence is a **second vote** when `data/snyder/gunw/*.h5` exists (`python scripts/download_gunw.py`). Co-event pair used: **29 Jun – 11 Jul** (during the fire). There is no 17–29 Jun pre-fire GUNW on this track.

## Result

| Metric | Value |
|---|---|
| HVHV Δ inside NIFC (median) | **−1.24 dB** |
| HVHV Δ outside NIFC (median) | +0.40 dB |
| HHHH Δ inside (median) | −0.26 dB |
| Detected change | **40.9 km²** (6,396 pixels) |
| NIFC polygon | 122.2 km² (30,202.5 GIS acres) |
| Precision vs NIFC | **1.00** (no flagged pixels outside the official perimeter) |
| Recall vs NIFC | 0.34 |
| IoU | 0.34 |

The whole-box mean in [[research/Scar check]] looked mixed because a **bright red patch east of the fire** sits outside the perimeter. Inside the yellow WFIGS outline the scar is a coherent HV **darkening**. Keep Snyder.

GUNW HH coherence on the 29 Jun–11 Jul pair does **not** split the scar: mean 0.73 inside NIFC vs 0.76 outside. Only 0.4% of change pixels fall below 0.40. L-band stays fairly coherent on this arid mesa; **GCOV HV log-ratio is the detection**, GUNW is context. That is worth saying in the pitch (honesty > a fake second layer).

Outputs (small enough for git): `outputs/snyder/change.png`, `confidence.png`, `coherence.png`, `change.geojson`, `summary.json`.

## How to run

```text
python scripts/fetch_snyder_perimeter.py   # if ref/snyder/ is missing
python scripts/change_snyder.py
python scripts/download_gunw.py            # ~2.3 GB × fire-window pairs, then re-run change
```

Related: [[docs/Processing pipeline]] [[research/Snyder perimeter]] [[research/Scar check]] [[research/Why SAR optical]]
