---
tags:
  - research
  - data
date: 2026-10-08
---

# Scar check — Snyder 80 m crop

**Decision: keep Snyder. Do not switch events.** A coherent change pattern is visible in the cropped 80 m pair. It is not a simple “everything went dark.”

## What we ran

`python scripts/crop_snyder.py`

Crop: lon/lat `-109.22, 38.98, -108.80, 39.20` (Westwater / Snyder Mesa / Glade Park). Grid: Frequency B, 80 m, EPSG:32612. Size 315×448 pixels.

PNGs: `data/snyder/preview/crop/`

## Numbers (July − June, dB)

| Polarization | Mean ΔdB | Median | Pixels < −1 dB |
|---|---|---|---|
| HHHH | +1.00 | +0.95 | 7.0% |
| HVHV | +0.24 | +0.29 | 15.7% |

The whole-box mean is **up**, not down. That is expected for a mixed box (river + unburned + burn) and for **L-band**: canopy loss often **brightens HH** (more ground return) while some patches **darken HV**.

## What the pictures show

- Grayscale June/July: Colorado River is the winding dark line. Terrain is readable.
- Difference (red = brighter in July, blue = darker): a **non-random** two-part pattern — a blue patch along drainages, a red two-lobed patch to the east. Stronger in **HVHV** than HHHH.
- That is a scar-scale feature, not speckle.

## Caveat

We have not yet laid an official perimeter on the map. Until FIRMS/NIFC/InciWeb is overlaid, we do not know which color is the burn vs river/phenology. Keep Snyder; next step is that overlay, then the real log-ratio + mask script.

Related: [[decisions/ADR-002 Primary event Snyder Fire]] [[research/Candidate events]] [[docs/Processing pipeline]]
