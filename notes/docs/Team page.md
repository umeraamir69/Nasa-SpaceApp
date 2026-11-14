---
tags:
  - docs
  - pitch
date: 2026-11-14
---

# Team page + project copy

**Full paste package (summary, NASA data, SI disclosure, 30 s shot list, 7 slides, Q&A):** [[../../docs/submission]] → repo file `docs/submission.md`.

Paste the short bits below on [spaceappschallenge.org](https://www.spaceappschallenge.org/). You still create/edit the team in the browser.

Challenge: **Dancing with the SARs**. Local event: **Toronto** (Centennial College, 14–15 Nov).
Final project link: `https://github.com/umeraamir69/Nasa-SpaceApp`

## Team

| Field | Paste |
|---|---|
| Team name | EchoLens |
| Challenge | Dancing with the SARs |
| One line | Two NISAR radar passes in, an incident briefing out: what changed, how many km², and why the outline is real. |

## About the team (short)

EchoLens is a NASA Space Apps Toronto 2026 project. We turn a before/after NISAR L2 pair into a map a human can brief in under a minute. Nine cases live — Snyder Fire as the answer key, plus Thunder Bay, Second Flat, Nepal GLOF, and honest negatives (Latvia, Coleman, Crete, Spokane) where the radar correctly says nothing left.

## Project summary (short)

EchoLens maps surface change from **NISAR L-band GCOV**, not photographs. Same-track pair → despeckle → log-ratio → score vs official truth. Snyder: **40.9 km²** inside NIFC at precision **1.0**. Nepal GLOF: **2.4 km²** at precision **0.99**. We publish negatives too — grass fires and drained floods that L-band should not invent.

## NASA / partner data we actually use

- NISAR L2 GCOV Provisional — detection
- NISAR L2 GUNW Provisional — coherence second vote
- NASA FIRMS VIIRS — Thunder Bay hotspot truth
- NIFC WFIGS — fire perimeters
- Copernicus EMSR / HOT — flood / GLOF truth
- Sentinel-2 L2A — cloudy optical why-SAR chip

## SI / AI disclosure (required)

Coding assistants (Cursor) sped up UI and docs. Detection is classical SAR math, not an SI classifier. Map layers are real satellite / truth data — not AI-generated imagery.

## Seeking members (optional)

Need one more person who can (a) speak 90 seconds of the pitch, or (b) run the laptop clicks while someone else talks.

## Do not paste

Earthdata passwords, tokens, or secrets.

Related: [[docs/Pitch]] [[docs/Product vision]] [[Tasks]]
