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
- [ ] Stretch: second region/event only if the first pair is proven (Thunder Bay — skip until more disk)

### Week 7 — Nov 4–13

- [ ] Full pipeline runs unattended once (script exists; run it on a machine with free disk)
- [ ] Case study data + processed output saved locally and backed up
- [x] Rehearse the Week 5 pitch on the live map — first pass 13 Oct ([[docs/Pitch]] rehearsal log). Still need one out-loud stopwatch.
- [ ] Confirm weekend roles
- [ ] Offline copies of data/code; deps pre-installed

## Done

- [x] Stand up the Obsidian vault in `notes/`
- [x] Ingest EchoLens start plan into the vault
