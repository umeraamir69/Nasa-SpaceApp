---
tags:
  - tasks
---

# Tasks

From [[docs/Complete plan]]. Capture extras in [[Inbox]].

## Week 1 — Sep 23–29

### Day 1–2 — data access

- [x] Create NASA Earthdata Login: https://urs.earthdata.nasa.gov/
- [x] Search `NISAR_L2_GCOV_PROVISIONAL_V1` and `NISAR_L2_GUNW_PROVISIONAL_V1`
- [x] Confirm granules for Snyder and Thunder Bay 36
- [x] Sentinel-1 fallback not needed — both boxes have NISAR L2
- [ ] Change Earthdata password and revoke the chat-pasted token (secrets were posted in chat)

### Day 2–4 — change type + event

- [x] Pick **one** primary change type — wildfire ([[decisions/ADR-001 Change type wildfire]])
- [x] Find a real documented event — Snyder Fire ([[decisions/ADR-002 Primary event Snyder Fire]])
- [x] Write the decisions in `decisions/`

### Day 4–7 — team

- [ ] Submit team page (challenge: Dancing with the SARs) — copy is ready in [[docs/Team page]]
- [ ] Recruit against gaps: SAR/data, backend, frontend, pitch
- [x] Stand up shared GitHub repo (`umeraamir69/Nasa-SpaceApp`)
- [ ] Stand up team channel (Discord/WhatsApp)

## Later

### Weeks 2–3 — Sep 30 – Oct 13

- [x] Download two real passes (before/after) — Snyder GCOV `048_A_021` in `data/snyder/gcov/`
- [x] Confirm visible change in the data — keep Snyder ([[research/Scar check]]); do not switch
- [x] Document the download process — [[docs/Get the data]] (teammates); granules also logged in [[research/NISAR data access]]
- [x] Task 1 teammate guide (see the map + optional NASA rebuild) — [[docs/Task 1]]
- [x] Offline Python POC: GCOV log-ratio + product mask ([[research/Change detection]]); GUNW is the second vote
- [x] Produce one proof-of-concept change image **and** a confidence mask — `outputs/snyder/`
- [x] Overlay a ground-truth perimeter and cite it — NIFC WFIGS `2026-UTDRD-005113` ([[research/Snyder perimeter]])
- [ ] Oct 28: revisit scope when the full challenge statement lands (parked until then)

### Weeks 4–6 — Oct 14 – Nov 3

- [x] App skeleton: React (Vite) + FastAPI + map ([[Runbooks/Run the app]])
- [x] Backend serves GeoJSON (`/api/geojson/change`, `/api/geojson/perimeter`)
- [x] Wire Week 3 algorithm output as real GeoJSON (`outputs/snyder/`)
- [x] Before / after / change / **confidence** toggle + plain-language briefing (dates, km², why we trust it)
- [x] Draft the 3-minute pitch script — [[docs/Pitch]] (do not leave this for Week 7)
- [ ] Cross-check Oct 28 challenge statement — [[docs/Challenge check]] (13 Oct: summaries only)
- [x] Stretch: cloudy optical next to the SAR pair (why-SAR) — Sentinel-2 7 Jul ([[research/Why SAR optical]])
- [x] Unattended Snyder pipeline script — `python scripts/pipeline_snyder.py` ([[Runbooks/Snyder pipeline]])
- [x] Stretch: search a second change type (flood) — Latvia EMSR926 ([[research/Flood candidates]])
- [x] Stretch: Latvia flood on the map — `080_D_059` 18 Aug → 30 Aug, 6.5 km² leftover water, 34 km² lakes masked ([[docs/Task 2]]). Snyder granules deleted to free disk; Snyder **products** stay.
- [x] Snyder NIROPS IR overlay (30 Jun heat + 7 Jul perimeter) — `python scripts/fetch_snyder_ir.py`
- [x] Latvia permanent-lake overlay + Sentinel-2 21 Aug optical (`fetch_optical.py --case latvia`)
- [x] Stretch: Nepal Rasuwa GLOF EMSR927 on the map — `048_D_074` 16 Aug → 28 Aug, Copernicus + HOT flood polygons ([[docs/Task 3]]). Latvia granules deleted to free disk; Latvia **products** stay.

### Week 7 — Nov 4–13 / demo weekend

- [x] One-command demo — `./demo.sh`
- [x] Submission paste package — `docs/submission.md` (page text, 30 s shot list, 7 slides, Q&A, SI disclosure)
- [x] Team page copy refreshed for nine cases — [[docs/Team page]]
- [ ] Full pipeline runs unattended once (script exists; run it on a machine with free disk) — **not needed for demo**; `outputs/` already ships
- [ ] Case study data + processed output saved locally and backed up — **human:** USB per [[Runbooks/Weekend kit]]
- [x] Rehearse the Week 5 pitch on the live map — first pass 13 Oct ([[docs/Pitch]] rehearsal log). Still need one out-loud stopwatch.
- [ ] Confirm weekend roles — **human**
- [ ] Offline copies of data/code; deps pre-installed — **human:** USB stick
- [ ] Paste + submit on spaceappschallenge.org Project tab — **human** (deadline Sun 15 Nov 11:59 PM local)
- [ ] Record 30 s video or export ≤7 slides — **human** (shot list in `docs/submission.md`)

### Done 29–30 Oct (see `docs/a-to-z.md`)

- [x] Nepal same-mode reprocessing (098_A_016, P 0.99 / R 0.18)
- [x] Thunder Bay 36 (235 km²; FIRMS key still pending)
- [x] Crete EMSR933 (honest negative, DEM land mask)
- [x] Isaias (marginal 0.5 km² fringe; 148 sliver rejected)
- [x] Latvia 7-rule water-index experiment (negative stands)
- [x] Polygon inspector + swipe + pitch mode + site redesign
- [x] Accuracy review + same-mode guard + slope audit + threshold sweep
- [x] 104 live checks + 9 unit tests green; A–Z doc + README refresh
- [ ] Rotate Earthdata password (was pasted in chat)

## Done

- [x] Stand up the Obsidian vault in `notes/`
- [x] Ingest EchoLens start plan into the vault
