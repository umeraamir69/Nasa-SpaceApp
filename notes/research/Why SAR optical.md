---
tags:
  - research
  - data
date: 2026-10-13
---

# Why-SAR — cloudy Sentinel-2 over Snyder

Stretch: put a **cloudy optical** scene next to the NISAR pair so judges see why radar exists.

## Scene

| Field | Value |
|---|---|
| Sensor | Sentinel-2 L2A true color (TCI) |
| ID | `S2C_12SXJ_20260707_1_L2A` |
| Time | 7 Jul 2026 18:13 UTC (during the fire; contained 17 Jul) |
| Cloud cover | 34.4% (thick white over the west/south of our box) |
| Catalog | [Element84 Earth Search](https://earth-search.aws.element84.com/v1/search) / AWS `sentinel-cogs` |
| File | `outputs/snyder/layers/optical.png` |

NASA GIBS Worldview snapshots returned `Data-Present: false` for VIIRS/MODIS true-color on these dates. Sentinel-2 COG window-read worked.

## How to refresh

```text
python scripts/change_snyder.py   # writes layer bounds
python scripts/fetch_optical.py
```

Or the unattended path: `python scripts/pipeline_snyder.py`

On the map, click **Optical**. Same geographic box as Before/After/Change.

## Latvia (flood)

`python scripts/fetch_optical.py --case latvia` — Sentinel-2 `S2A_34VEJ_20260821_1_L2A`, **21 Aug 2026**, **84% cloud**, over the EMSR926 box. Tile nodata is transparent.

Related: [[research/Change detection]] [[docs/Pitch]] [[docs/Score upgrades]] [[docs/Task 2]]
