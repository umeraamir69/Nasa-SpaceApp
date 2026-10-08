---
tags:
  - research
  - data
---

# What GCOV is

Not photos. Not JPEG/PNG. The Snyder file is an **HDF5 container** of radar backscatter **images** already on a map grid.

Inspected file: `data/snyder/gcov/NISAR_L2_PR_GCOV_023_048_A_021_..._20260617....h5` (17 Jun 2026, track 48 frame 21, ascending).

## The layers we will use

| Layer | Path | What it is |
|---|---|---|
| HHHH | `/science/LSAR/GCOV/grids/frequencyA/HHHH` | HH backscatter power (how bright the ground is to horizontal radar) |
| HVHV | same folder, `HVHV` | HV backscatter (cross-pol; vegetation often brighter) |
| mask | `mask` | which pixels are valid |

Frequency A is **10 m** pixels, shape **35064 × 35568**. Frequency B is the same scene at **80 m** (smaller, faster to preview).

NISAR L-band. Dual-pol HH/HV. Terrain-corrected gamma-0. Official product note: [ASF GCOV](https://nisar-docs.asf.alaska.edu/gcov/).

A burn scar usually looks **darker** on HHHH after the fire (less canopy to bounce the pulse). We turn those two arrays into a visible PNG later; the `.h5` is the source.

Related: [[research/NISAR data access]] [[Runbooks/Download NISAR]]
