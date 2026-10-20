---
tags:
  - research
  - data
date: 2026-10-15
---

# Flood stretch — candidates

Snyder stays the **primary** demo. Flood is a **second case**, not a second MVP. Same NISAR L2 GCOV log-ratio idea: new open water is darker after the event. Permanent lakes stay dark on both dates — those pixels are not change.

Searched **15 Oct 2026**. Pair **downloaded and processed** the same day after Snyder `.h5` granules were deleted (map products kept).

```text
python scripts/search_nisar.py --event latvia-flood
python scripts/search_nisar.py --event nepal-glof
python scripts/search_nisar.py --event ottawa-flood
```

## Verdict

**Preferred flood: Latvia–Lithuania, Copernicus EMSR926**, ~21–22 Aug 2026.

Same-track GCOV pair exists, **event sits between the two dates**, plains (not Himalayan layover), after the 27 Jul–10 Aug NISAR gap.

| Role | Track | Date |
|---|---|---|
| Before | `080_D_059` (descending; covers western Latvia / EMSR926) | **18 Aug 2026** |
| After | same track | **30 Aug 2026** |

`071_A_030` also exists but its valid pixels start ~24°E — east of the EMSR926 centre. Do not use it for this event.

GUNW `080_D_059` 18 Aug–30 Aug spans the flood — coherence drop over new water is a real second vote here (unlike arid Snyder). Not downloaded yet.

Ground truth: Copernicus EMSR926. Vector products were still not on HDX as of 19 Oct (S3 prefix empty). Map cites the activation URL, overlays **permanent lakes** from the HH pair, and a cloudy Sentinel-2 21 Aug scene.

Processed result (`python scripts/change_latvia.py`): **6.5 km²** HH darkening that also looks like water on 30 Aug, **34.0 km²** permanent lakes masked. Box-wide HH median **+0.20 dB** — after pass is 8 days after the 21–22 Aug crest, so this is leftover water, not the peak.

## Also searched

| Event | Dates | Granules | Why not first |
|---|---|---|---|
| **Nepal Rasuwa GLOF** EMSR927 | 26 Aug 2026 | Yes. Same-track `048_D_074` **16 Aug → 28 Aug**. Copernicus GRA landslides + HOT 27 Aug flood polygon on the map. UNOSAT mudflow / barrier-lake FileGDBs exist. | Added **20 Oct** as the third chip (not a Latvia replacement). Himalaya layover: flag HH darkening only inside official polygons. After is `QPDH` vs before `DHDH` — change uses HHHH. Granules are ~7 GB × 2 — use `crop_nepal.py` on this disk. |
| **Ottawa 1 Jul 2026** | Canada Day storms, 118 mm, 4,500 basements | Yes. `098_D_065` **18 Jun → 3 Jul**. | Urban flash / sewers. 80 m L-band will not see basements. Local-impact story, weak scar. Do not process. |
| Niagara Jul 27–Aug 2 | St. Catharines emergency | Not searched | Peak sits **inside** the 27 Jul–10 Aug NISAR gap. Water gone by 11 Aug. |

Thunder Bay 36 remains the second **wildfire**, not the flood.

## How flood differs from Snyder

- Sign can still be “darker after” (specular water).
- Mask **water on both dates** or you will flag every lake.
- Ground truth is a **flood extent**, not NIFC.
- Pitch beat: same script, different surface. Snyder stays the 3-minute. Latvia is the “also floods” chip.

## Download (after Snyder granules were cleared)

Snyder **products** (`outputs/snyder/`) stay. Snyder **`.h5` files** were removed 15 Oct on this machine to free ~16 GB. Re-download Snyder only if you need to rebuild the fire case.

```text
python scripts/download_latvia.py   # track 080_D_059 only, ~1.6 GB × 2
python scripts/change_latvia.py
```

Map: Snyder is still the default chip. Latvia appears when `outputs/latvia/summary.json` exists. [[docs/Task 2]]

## Nepal GLOF (third chip, 20 Oct)

Latvia still has no EMSR926 vectors. Nepal does. Same disk cannot hold both granule pairs (~3 GB each). **Latvia `.h5` deleted 20 Oct; `outputs/latvia/` kept.**

```text
python scripts/fetch_nepal_proof.py
python scripts/crop_nepal.py       # range-read Rasuwa crop; granules are ~7 GB × 2
python scripts/change_nepal.py
```

Proof layers: `outputs/nepal/emsr927.geojson` (Copernicus observedEvent, landslides) and `outputs/nepal/flood_extent.geojson` (HOT, 27 Aug, 31.7 km² full Bhote Koshi / Trishuli). Change is HH darkening **inside** those polygons — mixed 80 m gorge pixels are not specular water.

[[docs/Task 3]]

Related: [[research/Candidate events]] [[research/Change types]] [[research/NISAR data access]] [[decisions/ADR-003 Stretch flood Latvia]]
