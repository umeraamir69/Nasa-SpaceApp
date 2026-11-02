# EchoLens expansion findings — new events, new features, new approaches

*Researched and partly built 31 Oct 2026. Nothing here is processed yet
except the Otsu micro-test — event downloads await a go/no-go (each is
GBs + hours). Vetting tool: `scripts/vet_event.py` (stdlib, CMR, no auth).*

---

## 1. New events vetted (6, all with same-mode pairs)

All pairs below are same track/beam/mode (guard-compatible), found by CMR
search over event boxes. Ranked by story × timing × truth.

| # | Event | Type | Best pair | Timing vs event | Truth | Rank |
|---|-------|------|-----------|-----------------|-------|------|
| 1 | **Valencia/Alicante flood** (Storm Adam, 18–20 Oct 2026) | Flood | 167_D_068/069 2005 DHDH, 11 → 23 Oct | before −7 d, after +3 d — near-perfect | HDX `esp-flood-emsr935` confirmed | **TOP PICK** |
| 2 | **Coleman Creek fire** (Harney Co. OR, ~313k acres, late Jul) | Fire | 143_D_066/067 4005 DHDH, 6 Jul → 11 Aug (9 pairs exist) | brackets late-Jul ignition | NIFC WFIGS (will exist at this size) | High |
| 3 | **Spokane fires** (WA, early Aug, 833 homes, $1B+) | WUI fire | 042_D_064/065 4005 DHDH, 23 Jul → 16 Aug | brackets early-Aug disaster | NIFC + damage reports | High (different story: homes, not hectares) |
| 4 | **Sicily flood** (SE Sicily, 18 Oct, 20.6 km² delineated) | Flood | 144_A_020 2005 DHDH, 10 → 22 Oct | before −8 d, after +4 d | Copernicus vectors (EMSR # TBD) | Medium (truth TBD) |
| 5 | **Sinlahekin fire** (Okanogan WA, ~152k acres, mid-Aug) | Fire | 172_D_063/064 4005 DHDH, 20 Jul → 25 Aug | brackets mid-Aug | NIFC | Medium (too similar to Thunder Bay) |
| 6 | **Tuscany flash flood** (9 Sep) | Flood | 072_A_023 2005 DHDH, 30 Aug → 11 Sep | after +2 d — excellent | Copernicus vectors (EMSR # TBD) | Medium (truth TBD, box TBD) |

Notes:

- ~~Valencia is the standout~~ **Valencia is a documented dead end (2 Nov).**
  Pair 167_D_069 11→23 Oct downloads and passes the guard, but the EMSR935
  truth (1507 px) sits ~99% on *invalid* product-mask pixels — the flood
  coast lies just past the frame's valid swath edge (mask-0 pixels read
  exactly 0.0 power = fill, so the mask convention is correct). Exhausted:
  no 167_D_070 frame exists; 058_A_021 and 066_D_069 have pre-storm befores
  but their 28 Oct afters are missing from the catalog entirely. Valid
  pixels show zero darkening (scene +0.39 dB). Same dead-end class as
  Crete-065/Lasithi and Isaias-148/sliver. Lesson, again: check valid-swath
  overlap with truth *before* treating a pair as processable — CMR
  intersection ≠ valid data. Otsu/KI confirmation must come from another
  scene (Sicily/Tuscany candidates, same coastal risk).
- EMSR935 rapidmapping-backend zip URLs 404 (naming differs from EMSR933 or
  still in production ~10 days post-activation); HDX `esp-flood-emsr935`
  exists instead — use the Nepal/HDX fetch pattern, not the Crete/backend one.
- Fire perimeters: query NIFC WFIGS by incident name at processing time
  (same pattern as `scripts/fetch_snyder_perimeter.py`).
- Skipped: Big Grass Fire OR (578k acres but grass — weak L-band structure
  signal), TS Arthur/Edouard (weaker storm stories than Isaias).

**Recommended next step (updated 2 Nov):** Valencia dead → process Coleman
Creek (fire #3, 308k acres + NIFC) and Spokane/Autumn Lane (WUI story) instead.
Flood-method confirmation (Otsu/KI) still needs a second detection scene.

---

## 2. Website upgrades shipped (31 Oct)

- **Overview mode** (`Overview` button): all 6 cases side by side — verdict,
  area, dates, event marker, key metric — plus totals (3 detected · 2
  negative · 1 marginal · km²) and a 4-step method strip. Click any card to
  open the case. Renders as an overlay so the map stays mounted.
- **Event timeline** in every briefing: before pass → event → after pass
  (e.g. "Landfall · 9 Oct"), with hover hint.
- **NISAR pair row** in stats: track · mode parsed from filenames
  (e.g. `048_A_021 · DHDH both dates`), verified for all 6 cases.
- **Print briefing** button + print stylesheet: one-page light-theme handout
  (briefing only, map/chrome hidden).
- Hover hints everywhere (shipped earlier): stat rows, layers, toggles,
  pitch controls, map-fragment tooltips.

---

## 3. Approaches research: ML, OpenCV, and what else could work

### 3.1 Otsu micro-test — the headline finding (ran on real data)

`scripts/experiment_otsu.py` (numpy Otsu, no new deps — cv2 is NOT installed):

| Rule (Nepal, official confinement, min 3 px) | px | P | R | IoU |
|---|---|---|---|---|
| Shipped fixed −2.0 dB (reproduced exactly) | 377 | 0.987 | 0.176 | 0.175 |
| Unsupervised Otsu +0.04 dB | 1374 | 0.961 | 0.625 | **0.609** |

Reading: Otsu finds "everything that darkened at all" and, *inside the
official corridor*, that is mostly wet channel — recall triples with
precision intact. BUT: (a) without confinement Otsu flags half the Himalaya
(P 0.011) — the win is conditional on the supervised corridor; (b) single
scene, no held-out test. Decision: **fixed cut stays shipped** (explainable
baseline, consistent across cases); Otsu is recorded
(`otsu_experiment` in Nepal summary) and Valencia is the confirmation scene.

### 3.1b KI + split-KI micro-test — ran 2 Nov (OpenCV installed)

`scripts/experiment_ki.py` (cv2 Otsu cross-check + cv2 connected components):

| Rule (Nepal, official confinement, min 3 px) | px | P | R | IoU |
|---|---|---|---|---|
| Shipped fixed −2.0 dB | 388 | 0.985 | 0.181 | 0.180 |
| cv2 Otsu +0.04 (= numpy Otsu ✓) | 1412 | 0.961 | 0.642 | 0.625 |
| KI global +2.20 | 2162 | 0.960 | 0.982 | **0.943** |
| Split-KI median +2.06 (16/16 tiles) | 2148 | 0.960 | 0.975 | 0.938 |

Reading: adaptive cuts trace the *full extent* (IoU 0.94) while the fixed cut
maps the *severe core* (IoU 0.18, P 0.99) — different products, both honest.
But the adaptive wins ride entirely on the official-corridor confinement
(KI +2.2 ≈ "everything not-brightened inside the hand-drawn corridor"), and
with Valencia dead there is no second scene to confirm generality. Recorded
(`ki_experiment` in Nepal summary). Fixed cut stays shipped.

### 3.2 Adaptive thresholds (literature)

- Otsu is the most-used SAR auto-threshold, but studies (ALOS-2 Japan floods)
  find most auto-methods **over-extract**; **Kittler–Illingworth
  minimum-error** usually beats Otsu on SAR histograms.
- Operational standard is **split-based KI**: tile the scene, threshold each
  tile (Copernicus GFM-style). Recommended next experiment after Otsu:
  split-KI on Nepal + Valencia.
- Our scenes are unimodal (flood ≪ 1% of pixels) — global Otsu splits noise
  (+0.04 dB here). Tiling or corridor-confinement is required, not optional.

### 3.3 What OpenCV would (and wouldn't) add

- **Yes:** `cv2.threshold` + `THRESH_OTSU` (one-line Otsu),
  morphology (`morphologyEx`), `connectedComponentsWithStats` (blob filter +
  area stats in one call), `findContours` (polygonize alternative). Drop-in
  upgrades for our scipy/skimage steps, faster in C.
- **No:** OpenCV has **no SAR Lee/Frost despeckle** — those live in SNAP,
  OTB, or hand-rolled code. Our 3×3 median is fine; refined-Lee is a ±5%
  project for later.
- Verdict: install `opencv-python-headless` in `.conda/env` when we want
  Otsu/KI + connected components; no science blocked without it.

### 3.4 Polarimetry — the unused half of GCOV

- We use only backscatter intensities (HH/HV). GCOV is a *covariance* product
  — its off-diagonals carry polarimetric phase info we never touch.
- Reference: L-band + **Freeman–Durden decomposition + Random Forest** hit
  **87% overall** on Hurricane Florence inundation (open water *and*
  flooded forest via double-bounce). This is THE approach for "flood under
  trees" — the case our threshold method cannot see.
- Catch: full Freeman–Durden / H-A-α needs **quad-pol**; all our pairs are
  dual-pol DHDH (HH+HV). Dual-pol proxies exist (H-α for dual-pol,
  HH–HV correlation) but are weaker. Realistic path: dual-pol descriptors
  as extra features, or hunt one quad-pol pair for a showcase scene.

### 3.5 Deep learning (calibrated, not hyped)

- Known numbers: Sen1Floods11 flood IoU 0.38–0.42 (SegFormer-b2 0.418) vs
  ~0.35 threshold; Prithvi-EO foundation models reach 0.82+ *water* IoU
  (easier task than flood-change).
- Cost: GPU training, labeled chips, and — critically — the demo loses its
  one-sentence explainability. Our Otsu result (IoU 0.61, unsupervised)
  already beats published DL flood numbers *on this scene*, which weakens
  the ML case further.
- Verdict stands: **no ML classifier for the demo**. The honest ML story for
  judges: "an unsupervised histogram cut beats the literature's DL numbers
  here — the bottleneck is timing and truth, not model capacity."

### 3.6 Other approaches considered

- **Coherence (done):** GUNW second vote shipped for Nepal (confirm) and
  Latvia (real-change-not-water). Coherence confirms *change*, not water.
- **InSAR deformation:** the Nepal precursor story (ISRO found pre-burst
  creep in deformation time series). Different product, different pipeline —
  a 7th-case candidate ("the flood we saw coming"), not a method upgrade.
- **Optical+SAR fusion:** rejected for detection (cloud), kept for the
  why-SAR layer. OPERA DSWx-HLS is the institutional fusion reference.
- **Time-series / frequency:** flood-frequency maps from stacks (needs
  5+ passes/case — download-heavy, demo-light). Skip.

---

## 4. Decisions for the human

1. ~~**Process Valencia?**~~ Done 2 Nov: **dead end** (truth outside valid
   swath). No UI case; findings above.
2. **Coleman Creek / Spokane?** In progress 2 Nov (fires; NIFC truth saved).
3. **Adopt Otsu/KI?** Blocked: no confirmation scene (Valencia dead).
   Fixed cut stays shipped; experiments recorded in Nepal summary.
4. **Install OpenCV + try split-KI?** Done 2 Nov: cv2 5.0 in `.conda/env`,
   KI IoU 0.94 recorded with caveats above.

*Full context: [a-to-z.md](a-to-z.md) §§3/6/7/10. Vetting:
`scripts/vet_event.py`. Otsu: `scripts/experiment_otsu.py`.*

---

## 5. Processing results (2 Nov) — what got built

### Second Flat fire (SHIPPED, detected)

Pair 005_A_024 8 Jul → 13 Aug (shared granules with Coleman), HV 1.5 dB.
**68.9 km² at P 0.968 / R 0.155 / IoU 0.154** vs the 431 km² NIFC perimeter
(2026-ORBUD-002693, 105,854 acres sage+pine, ignited 24 Jul). Pine canopy
loss darkens exactly as the literature predicts. Slope audit + optical +
UI wiring done; pitch step added.

### Coleman Creek fire (SHIPPED, fuel-type negative)

Same pair, HV 1.5 dB. **31.3 km² at P 0.48 / R 0.013** vs 1,307 km² NIFC.
Inside median **HV −0.10 dB / HH −0.03 dB** — both bands silent; only 4.5%
of fire pixels cross the cut vs 1.2% background noise. Range/grass holds no
L-band structure to lose. Not a timing problem (pair brackets ignition well)
and not a threshold problem (HH confirms). The Coleman/Second Flat pair —
same satellite, same week, 60 km apart — is a controlled fuel experiment:
pine P 0.97, grass R 0.01. Shipped with `verdict` + `fuel_check` in summary
and a pitch step.

### Spokane / Autumn Lane fire (SHIPPED, fuel-context negative)

Pair 042_D_065 23 Jul → 16 Aug, HV 1.5 dB. **9 px, P/R 0.0** vs 23 km² NIFC
(2026-WANES-001857, 5,764 acres, ignited 1 Aug). Inside median **HV +0.13 dB**
(HH +0.35) — the burn brightened slightly; buildings scatter loudly standing
or burned, and the grass matrix behaves as at Coleman. Download footnote:
earthaccess stalled at 98% for 25 min; killed and resumed via `curl -C -`
with a URS bearer token (HTTP 206) — verified HDF5-valid before rename.
Shipped as the WUI negative with `verdict` + `fuel_check`.

### Scoreboard after expansion: 9 cases

4 detected (Snyder, Thunder Bay, Nepal, Second Flat) · 4 negative (Latvia,
Crete, Coleman, Spokane) · 1 marginal (Isaias). Every negative carries a
distinct proven mechanism: timing ×2, fuel ×2. Tests: 9/9 unit, 154/154
live probe. Test fix along the way: UTM-grid rotation puts legitimate edge
pixels up to 0.006° outside corner-derived layer bounds — the bounds test
now carries a documented 0.01° epsilon instead of a wrong strict expectation.
