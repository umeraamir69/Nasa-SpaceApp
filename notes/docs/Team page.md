---
tags:
  - docs
  - pitch
date: 2026-10-15
---

# Team page + project copy

Paste this on [spaceappschallenge.org](https://www.spaceappschallenge.org/). You still have to create the team in the browser — this is the text.

Challenge: **Dancing with the SARs**. Local event: **Toronto** (Centennial College, 14–15 Nov).

## Team

| Field | Paste |
|---|---|
| Team name | EchoLens |
| Challenge | Dancing with the SARs |
| One line | Two NISAR radar passes in, an incident briefing out: what burned, how many km², and why the outline is real. |

## About the team (short)

EchoLens is a NASA Space Apps Toronto 2026 project. We turn a before/after NISAR L2 pair into a map a human can brief in under a minute. Primary case: Snyder Fire (CO–UT), June–July 2026, checked against the official NIFC perimeter.

## Project summary (for the team page or later project submission)

EchoLens maps wildfire scar from **NISAR L-band GCOV** (geocoded polarimetric covariance), not from photographs. We locked the same-track pair `048_A_021` — 17 Jun 2026 before, 23 Jul 2026 after — around the Snyder Fire. After a 3×3 median despeckle, HVHV log-ratio flags pixels that went ≥ 1.5 dB darker. That outline is **40.9 km²**. Every flagged pixel sits inside NIFC WFIGS incident `2026-UTDRD-005113` (precision 1.0 vs the official line; we under-map on purpose). A cloudy Sentinel-2 scene from 7 Jul (34% cloud) is the why-SAR beat: optical is white, radar still returns a scar. GUNW coherence did not split this arid mesa, so we do not fake a second layer.

## NASA / partner data we actually use

- NISAR L2 GCOV Provisional (`NISAR_L2_GCOV_PROVISIONAL_V1`) — detection
- NISAR L2 GUNW Provisional — coherence as a second vote (not a discriminator here)
- NIFC WFIGS interagency perimeters — ground truth
- Sentinel-2 L2A (ESA Copernicus, Element84/AWS) — cloudy optical overlay

## Seeking members (optional)

Need one more person who can (a) speak 90 seconds of the pitch, or (b) stand at the laptop and click Before → After → Change → Optical while someone else talks. SAR math is already done.

**Discord / WhatsApp blast:**

> EchoLens — NASA Space Apps Toronto, Dancing with the SARs. We already have a live map of the Snyder Fire from real NISAR L2 (40.9 km², checked against NIFC). Looking for a teammate to split the 3-minute pitch or run the laptop. GitHub: umeraamir69/Nasa-SpaceApp

## Do not paste

Earthdata passwords, tokens, or granule filenames that imply a secret. The pair is public PROVISIONAL; the login is not.

Related: [[docs/Pitch]] [[docs/Product vision]] [[Tasks]] [[docs/Task 1]] [[docs/Get the data]]
