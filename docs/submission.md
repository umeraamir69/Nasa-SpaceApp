# EchoLens — Space Apps submission package

Paste into the Team **Project** tab on [spaceappschallenge.org](https://www.spaceappschallenge.org/).
Submission window: **Sat 14 Nov 9:00 AM → Sun 15 Nov 11:59 PM local**.
Demo for judges: **≤ 30-second video** *or* **≤ 7 slides** (title + close count). English required.
Final project link: `https://github.com/umeraamir69/Nasa-SpaceApp`

Local demo: `./demo.sh` → http://127.0.0.1:5173

---

## Project title

EchoLens

## High-level summary *(short blurb)*

EchoLens turns two NISAR radar passes into an incident briefing: what changed, how many square kilometres, and why we trust the outline. Nine real cases — fires, floods, a glacier outburst — including honest negatives where the radar correctly says “nothing left.”

## Project details *(how it works)*

1. Pull a same-track, same-mode NISAR L2 GCOV pair (before / after).
2. Convert gamma-0 to dB, 3×3 median despeckle, log-ratio.
3. One fixed threshold (fires: HV ≥ 1.5 dB darker; floods: HH brightening with permanent water masked).
4. Score against official truth (NIFC, Copernicus EMSR, HOT, FIRMS) — publish precision/recall and negatives.
5. Serve a React map + FastAPI briefing: before/after/swipe/change/confidence/optical, overlays, pitch tour, printable one-pager.

No neural net. Same script on the next event.

## NASA data used

| Source | Role |
|---|---|
| NISAR L2 GCOV Provisional (`NISAR_L2_GCOV_PROVISIONAL_V1`) | Primary change detection |
| NISAR L2 GUNW Provisional | Coherence second vote (shown; not faked when it does not split) |
| NASA FIRMS VIIRS | Thunder Bay hotspot truth overlay |
| NIFC WFIGS (partner) | Fire perimeter truth |
| Copernicus EMSR / HOT (partner) | Flood / GLOF truth |
| Sentinel-2 L2A (ESA) | Cloudy optical “why SAR” chip |

## Use of Super Intelligence (SI) / AI — disclose

We used coding assistants (Cursor / Composer) to accelerate UI, docs, and scripting. Detection math is classical SAR (log-ratio + mask), not an SI model. No AI-generated imagery is used in the map layers; all rasters are rendered from NISAR / Sentinel-2 / FIRMS / official polygons. If any AI-generated graphic appears in slides or video, it will carry a visible watermark.

## Tools & languages

Python (h5py, numpy, scipy, shapely, rasterio, earthaccess, FastAPI, uvicorn), React + Vite + Leaflet + three.js, GitHub.

## Final project link

https://github.com/umeraamir69/Nasa-SpaceApp

## References

- NISAR L2 products via NASA Earthdata / ASF DAAC
- NIFC WFIGS interagency fire perimeters
- Copernicus Emergency Management Service (EMSR926, EMSR927, EMSR933, …)
- NASA FIRMS (VIIRS)
- Sentinel-2 L2A via Element84/AWS
- Repo docs: `README.md`, `docs/a-to-z.md`, `docs/expansion.md`, `notes/docs/Pitch.md`

---

## Case scoreboard (for judges)

| Case | Type | Result | Headline number |
|---|---|---|---|
| Snyder Fire | Wildfire | Detected | 40.9 km², precision 1.00 vs NIFC |
| Thunder Bay 36 | Wildfire | Detected | 235 km² severe core |
| Second Flat | Wildfire | Detected | 68.9 km², precision 0.97 vs NIFC |
| Coleman Creek | Wildfire | Negative | Grass/range — no L-band darkening |
| Autumn Lane (Spokane) | WUI fire | Negative | Grass + structures — P/R 0.0 |
| Nepal GLOF | Glacier flood | Detected | 2.4 km², precision 0.99 vs flood truth |
| Latvia flood | Flood | Negative | Dry-down; flood wave already gone |
| Crete flood | Flash flood | Negative | Drained before Oct 9 pass |
| Isaias surge | Hurricane | Marginal | 0.5 km² bay fringe, unvalidated |

---

## 30-second video shot list

Record the live map (http://127.0.0.1:5173). Hard cut to 30 s. No music needed.

| Sec | Shot | Voice |
|---|---|---|
| 0–5 | Home → open Snyder, Change + NIFC on | “Smoke hides fires from cameras. NISAR looks with L-band radar.” |
| 5–12 | Before → After → Change | “Two real passes. Subtract. The scar goes dark.” |
| 12–18 | Point at yellow NIFC vs blue change | “40.9 km² — every pixel inside the official NIFC line.” |
| 18–24 | Optical chip (cloud) | “Same week in optical: cloud. Radar still saw it.” |
| 24–30 | Overview or Nepal tab flash | “EchoLens: nine cases, including honest negatives. Two passes, one briefing.” |

Export 1080p, English audio (or English subs). Upload to YouTube/unlisted or Drive; paste the link on the project page.

---

## 7-slide deck outline *(alternative to video)*

1. **Title** — EchoLens · Dancing with the SARs · NASA Space Apps Toronto 2026
2. **Problem** — Smoke and cloud blind optical; responders still need km² and a trusted outline
3. **Method** — Same-mode NISAR pair → despeckle → log-ratio → score vs truth
4. **Snyder proof** — Screenshot: change inside NIFC, 40.9 km², P 1.00; Optical cloud chip
5. **Honesty** — Latvia / Coleman negatives: publishing “no” is part of the product
6. **Product** — Live map: briefing card, swipe, pitch mode, nine cases
7. **Close** — GitHub link · “Two NISAR passes in, an incident briefing out”

---

## Judge Q&A cheat sheet

| Question | Answer |
|---|---|
| Why only 41 of 122 km² at Snyder? | Threshold 1.5 dB HV after despeckle. We under-map on purpose. Precision 1.0 — zero flags outside NIFC. |
| Why no AI model? | Two dates, one event. A log-ratio we can explain beats a black box. SI tools helped us code; they do not draw the scar. |
| Latvia found nothing — failure? | No. Peak rain was 21–22 Aug; our pair is 18→30 Aug. Scene dried. Permanents lakes masked. Honest negative. |
| Why grass fires fail (Coleman)? | L-band sees structure/volume. Range grass barely darkens. Same week, pine at Second Flat hits P 0.97 — fuel physics. |
| Why not live Earthdata on stage? | Demo has no network budget. Granules already processed into `outputs/`. |
| What is GCOV? | Geocoded polarimetric covariance — calibrated backscatter on a map grid. |
| Can this run next fire? | Yes: last pass before, next pass after, same track/mode, same script. |

Full spoken 3-minute script: `notes/docs/Pitch.md`

---

## Human checklist (cannot automate)

- [ ] Paste this page into Space Apps Project tab and **Submit**
- [ ] Record the 30 s video *or* export the 7 slides; upload; paste link
- [ ] Replace placeholder names in `web/src/team.js` if teammates join
- [ ] Out-loud pitch once with a phone stopwatch
- [ ] Rotate Earthdata password (was pasted in an old chat)
- [ ] USB stick: repo + `outputs/` + `venv/` + `web/node_modules/` (see `notes/Runbooks/Weekend kit.md`)
