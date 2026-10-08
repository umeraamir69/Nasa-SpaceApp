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

- [ ] Submit team page (challenge: Dancing with the SARs)
- [ ] Recruit against gaps: SAR/data, backend, frontend, pitch
- [ ] Stand up shared GitHub repo
- [ ] Stand up team channel (Discord/WhatsApp)

## Later

### Weeks 2–3 — Sep 30 – Oct 13

- [x] Download two real passes (before/after) — Snyder GCOV `048_A_021` in `data/snyder/gcov/`
- [ ] Confirm visible change in the data; switch event if not
- [ ] Document the download process in [[research/NISAR data access]]
- [ ] Offline Python POC: GCOV log-ratio + GUNW coherence (no sklearn)
- [ ] Produce one proof-of-concept change image **and** a confidence mask
- [ ] Overlay a ground-truth perimeter (FIRMS / agency / news) and cite it
- [ ] Oct 28: revisit scope when the full challenge statement lands (parked until then)

### Weeks 4–6 — Oct 14 – Nov 3

- [ ] App skeleton: React + FastAPI/Flask + empty map
- [ ] Backend serves mock GeoJSON
- [ ] Wire Week 3 algorithm output as real GeoJSON
- [ ] Before / after / change / **confidence** toggle + plain-language briefing (dates, km², why we trust it)
- [ ] Draft the 3-minute pitch script (do not leave this for Week 7)
- [ ] Cross-check Oct 28 challenge statement
- [ ] Stretch: cloudy optical next to the SAR pair (why-SAR)
- [ ] Stretch: second region/event only if the first pair is proven

### Week 7 — Nov 4–13

- [ ] Full pipeline runs unattended once
- [ ] Case study data + processed output saved locally and backed up
- [ ] Rehearse the Week 5 pitch; assign speaking sections
- [ ] Confirm weekend roles
- [ ] Offline copies of data/code; deps pre-installed

## Done

- [x] Stand up the Obsidian vault in `notes/`
- [x] Ingest EchoLens start plan into the vault
