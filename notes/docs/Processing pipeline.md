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

4. **Change image.** Log-ratio: `after_dB - before_dB`. A burn scar is a **drop** in backscatter (negative). Threshold that drop. That is the algorithm. No sklearn.

5. **Trust mask.** Drop pixels the product `mask` says are invalid. Later: GUNW coherence drop as a second vote. This is the “why we trust it” layer.

6. **Check against a fire perimeter.** Overlay FIRMS / InciWeb / news polygon. If our blob sits inside the Snyder perimeter, the method is real. If not, we say so or pick another pair.

7. **Vectorize.** Changed pixels → polygons → **GeoJSON** + a km² number.

8. **App.** FastAPI serves that GeoJSON. React + Leaflet: before / after / change / confidence + a briefing card.

## What we are not doing

- Training a neural net on fire
- Live Earthdata in the demo
- Treating the `.h5` as a photo to “detect objects” with OpenCV

Related: [[research/What GCOV is]] [[docs/Tech stack]] [[docs/Score upgrades]]
