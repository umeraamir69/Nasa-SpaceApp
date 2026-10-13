---
tags:
  - docs
  - architecture
---

# Processing pipeline

What we do to the two Snyder `.h5` files. Not OpenCV. Not a photo editor.

We already have the data. Next work is **offline math on those rasters**, then a map.

## Stack

| Job | Tool | Why not OpenCV |
|---|---|---|
| Open `.h5` | `h5py` | HDF5, not JPEG |
| Array math | `numpy` / `scipy` | dB, filters, log-ratio |
| Map georeference | `rasterio` | UTM 10 m grid, write GeoTIFF/GeoJSON |
| Show on a map | Leaflet in React | Browser, not a CV window |

OpenCV can blur an image. It does not know UTM, incidence angle, or GeoJSON. We only use it if we want a cheap preview window. The product path is geospatial.

## Steps, in order

1. **Read** `/science/LSAR/GCOV/grids/frequencyA/HHHH` (and `HVHV`, `mask`) from each file. Same track `048_A_021`, so the grids already line up. Use `frequencyB` (80 m) for a fast preview; Frequency A (10 m) for the real product.

2. **To dB.** Values are gamma-0 power. `10 * log10(HHHH)`. Human-readable brightness.

3. **Despeckle.** Radar looks salty. A small Lee / median filter (`scipy.ndimage`) so change is not just speckle.

4. **Change image.** Log-ratio: `after_dB - before_dB`. Inside the NIFC Snyder perimeter, **HVHV drops** (median −1.24 dB). Threshold that drop at 1.5 dB. No sklearn. Script: `python scripts/change_snyder.py`.

5. **Trust mask.** Drop pixels the product `mask` says are invalid (`0` or `255`). Confidence levels: valid → change → both-pol / in-perimeter → GUNW. GUNW HH coherence is downloaded (`python scripts/download_gunw.py`) but on this arid L-band pair it barely drops (0.73 inside vs 0.76 outside). Detection stays on GCOV HV.

6. **Check against a fire perimeter.** Overlay NIFC WFIGS `2026-UTDRD-005113` ([[research/Snyder perimeter]]). The HV darkening sits inside the yellow outline; a bright patch east of the fire is **outside** it. Keep Snyder.

7. **Vectorize.** Changed pixels → polygons → **GeoJSON** + a km² number (`outputs/snyder/change.geojson`, 40.9 km² at the 1.5 dB cut).

8. **Why-SAR optical.** Window-read a cloudy Sentinel-2 TCI (`S2C_12SXJ_20260707_1_L2A`, 34% cloud) into the same box. Script: `python scripts/fetch_optical.py`. [[research/Why SAR optical]]

9. **App.** FastAPI serves that GeoJSON. React + Leaflet: before / after / change / confidence / optical + a briefing card. Run: [[Runbooks/Run the app]].

Unattended (after the two GCOV `.h5` files are on disk): `python scripts/pipeline_snyder.py`. [[Runbooks/Snyder pipeline]]

## What we are not doing

- Training a neural net on fire
- Live Earthdata in the demo
- Treating the `.h5` as a photo to “detect objects” with OpenCV

Related: [[research/What GCOV is]] [[docs/Tech stack]] [[docs/Score upgrades]]
