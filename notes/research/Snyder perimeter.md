---
tags:
  - research
  - data
date: 2026-10-13
---

# Snyder Fire — official perimeter (cite this)

The polygon we overlay is **NIFC WFIGS**, not a hand-drawn box. FIRMS is hotspots (points). InciWeb is the incident page.

## Polygon we use

| Field | Value |
|---|---|
| Source | NIFC Wildland Fire Interagency Geospatial Services (WFIGS) — Interagency Perimeters Year-to-Date |
| Incident name | Snyder |
| UniqueFireIdentifier | **2026-UTDRD-005113** (IRWIN / UT-DRD-005113) |
| GIS acres | 30,202.5 |
| Contained | 100% |
| Discovery | 27 Jun 2026 05:10 UTC |
| POO | Grand County, Utah (38.998°N, 109.249°W) |
| Layer | [WFIGS FeatureServer](https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Interagency_Perimeters_YearToDate/FeatureServer/0) |
| Open data | [NIFC Open Data](https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-interagency-fire-perimeters-to-date) |
| File in repo | `ref/snyder/nifc_wfigs_snyder.geojson` |

NIFC situation reports later listed **28,264 acres** contained (17–18 Jul). The overlay uses the **WFIGS GIS polygon** (30,202.5 acres / 122.2 km²), which is what is actually in the national perimeter feed.

Refresh:

```text
python scripts/fetch_snyder_perimeter.py
```

## InciWeb / ops maps

- InciWeb: https://inciweb.wildfire.gov/incident-information/utdrd-snyder (thin after closeout)
- Official IR and ops PDFs: https://ftp.wildfire.gov/public/incident_specific_maps/rocky_mtn/2026/2026_Snyder/

## FIRMS

NASA FIRMS VIIRS/MODIS are **thermal hotspots**, not a burn perimeter. Do not treat them as the Snyder outline. Optional: set `FIRMS_MAP_KEY` and re-run the fetch script to pull a 10-day VIIRS point file. Product page: https://firms.modaps.eosdis.nasa.gov/

Related: [[research/Change detection]] [[research/Candidate events]] [[decisions/ADR-002 Primary event Snyder Fire]]
