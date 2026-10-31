# EchoLens A to Z — the complete guide, in plain language

*What we built, how it works, what the numbers mean, and how it compares with
the rest of the world. No background needed — every term is explained where it
first appears, and there is an [A–Z glossary](#a-z-glossary) at the end.*

**One-line version:** EchoLens turns two radar pictures from the NISAR
satellite into a one-page incident briefing — what changed on the ground, how
many square kilometres, and why you should believe the outline.

---

## 0. The 30-second version (explain it like I'm five)

Imagine you take a photo of your garden, then a storm floods it, then you take
a second photo. If you could subtract the first photo from the second, the
flood would light up — everything that didn't change cancels out.

EchoLens does exactly that, but with **radar** instead of a camera, from
**space**. Radar has a superpower cameras don't: it sees through cloud, smoke,
and darkness. So when a wildfire burns under a smoke plume, or a flood spreads
under monsoon cloud, the radar still sees the ground.

We compare a "before" radar image with an "after" radar image, keep only the
pixels that changed a lot, check them against official maps (fire perimeters,
flood polygons), and publish the result as an interactive map with honest
numbers — including the cases where the honest answer is "no, we can't see a
flood here."

---

## 1. What is this project?

- **Name:** EchoLens. **Event:** NASA Space Apps 2026, Toronto — challenge
  *"Dancing with the SARs"* (SAR = Synthetic Aperture Radar, explained below).
- **Demo:** a local web app — a map with 6 incident cases (2 wildfires,
  4 floods/storms), each with before/after/change layers, official overlays,
  and a written briefing with precision/recall numbers.
- **Status:** all 6 cases processed from real NISAR satellite data, all tests
  passing (104 live checks + 9 unit tests, 30 Oct 2026).

### The 6 cases at a glance

| # | Case | Type | Before → after | Verdict | Headline number |
|---|------|------|---------------|---------|-----------------|
| 1 | Snyder Fire (Colorado–Utah) | Wildfire | 17 Jun → 23 Jul 2026 | **Detected** | 40.9 km², precision 1.00 |
| 2 | Thunder Bay 36 (Ontario) | Wildfire | 11 Jul → 16 Aug 2026 | **Detected** | 235 km² severe core |
| 3 | Nepal Rasuwa GLOF | Glacier flood | 19 → 31 Aug 2026 | **Detected** | 2.4 km², precision 0.99 |
| 4 | Latvia–Lithuania flood | Flood | 18 → 30 Aug 2026 | **Negative** | dry-down, not flood |
| 5 | Crete flood | Flash flood | 27 Sep → 9 Oct 2026 | **Negative** | water drained before pass |
| 6 | Hurricane Isaias (Florida) | Surge | 30 Sep → 12 Oct 2026 | **Marginal** | 0.5 km² fringe, unvalidated |

A **verdict** is our bottom line per case. *Detected* means we mapped real
change and checked it against an official source. *Negative* means we looked
carefully and the honest answer is "no flood visible" — and we can prove why
(wrong timing: the water came and went between satellite passes). *Marginal*
means a faint signal that might be real but has no independent confirmation
yet. Publishing negatives is unusual for a demo, and deliberate: a tool that
only ever says "yes" can't be trusted when it matters.

---

## 2. Key ideas in plain language

### Radar, SAR, and NISAR

- **Radar** shouts radio waves at the ground and listens for the echo. Bright
  echo = rough or wet surfaces (forest canopy, buildings, soaked soil). Dark
  echo = smooth surfaces that bounce the signal away from the satellite
  (calm water, flat mud, ash-covered burn scars).
- **SAR (Synthetic Aperture Radar)** is a trick that turns a small antenna on
  a moving satellite into a very large virtual antenna, giving sharp images
  (tens of metres) from 750 km up.
- **NISAR** (NASA-ISRO SAR) is the satellite: the first with two radar
  wavelengths (**L-band**, ~24 cm, from NASA; **S-band**, ~10 cm, from ISRO),
  launched 30 Jul 2025, mapping all land every 12 days. L-band is the long
  wave — it passes through cloud, smoke, and even leafy canopies to feel the
  ground. Everything we do uses L-band.
- **Backscatter** is the technical word for "how loud the echo is." We work
  with calibrated backscatter called **gamma-0**, measured in **dB
  (decibels)** — the same unit as sound levels. A change of −2 dB means the
  echo got roughly 37% quieter.

### Polarisation: HH, HV, VV

Radio waves wiggle in a direction. NISAR transmits waves wiggling horizontally
(H) or vertically (V) and listens in H or V. That gives channels:

- **HH** — sent H, received H. Best for water: a flooded field goes dark.
- **HV** — sent H, received V. Best for fire: a burned forest loses the
  jumbled branches that scramble the signal, so the echo drops.
- Fires in this project use **HV**; floods use **HH**. (Think: **H**V = **H**eat
  damage, **H**H = **H**ydro.)

### Change detection

Subtract "after" from "before" (in dB). Big negative number = got much darker
= candidate fire scar or new water. One threshold decides: fires ≥ 1.5 dB
darker, floods ≥ 2 dB darker. Simple enough to explain in one sentence —
that simplicity is a feature, not a limitation (see §7, how we compare).

### Precision, recall, IoU — the three honesty numbers

Suppose the official fire map covers 100 squares and we flag 40:

- **Precision** = "of what we flagged, how much was really fire?" 40/40 = 1.00.
  High precision = we never cry wolf.
- **Recall** = "of the real fire, how much did we find?" 40/100 = 0.40.
  High recall = we find everything.
- **IoU** (Intersection over Union) = overlap ÷ combined area — one number
  that punishes both kinds of error.

We deliberately trade recall for precision: **we under-map on purpose.** A
briefing that says "at least this much burned, and all of it is real" is more
useful than one that guesses the full extent and gets half of it wrong.

---

## 3. How radar sees fire, flood — and wet soil

### Wildfire

A living forest canopy is a chaos of leaves and branches that scatters radar
in all directions, including back to the satellite (loud echo). Fire removes
the canopy and leaves char and ash — smoother, quieter. So a burn scar shows
up as a **dark patch in HV** that wasn't there before. Published L-band
research says boreal burns drop 2–3 dB (HH) and 3–6 dB (HV); our arid Snyder
site dropped a median −1.24 dB (HV) — smaller, exactly as expected for sparse
desert vegetation, and still well above the ~1.2 dB noise floor.

### Flood

Calm water is a mirror: the radar pulse bounces away from the satellite, so
new water shows up as a **dark patch in HH**. The catch is timing — water must
still be there when the satellite passes. Our Latvia pair came 8+ days after
peak rain (dry-down), and Crete's water drained within days. Both are honest
negatives, and the data proves it (scene got *brighter*, +0.2 dB).

### Wet soil (soil moisture) — cross-checked, not retrieved

Wet ground changes the echo too: damp soil is "brighter" to radar than dry
soil (up to a point), while standing water goes mirror-dark. We don't run our
own soil-moisture retrieval — that job belongs to NISAR's official **L3 SME2
soil-moisture map** (200 m, three retrieval algorithms DSG/PMI/TSR, beta
released 2026, accuracy goal 0.06 m³/m³; India's NRSC published the first maps
in Feb 2026). Instead we **cross-check our scenes against SME2**
(`scripts/xcheck_sme2.py`, recorded in each summary under
`soil_moisture_check`):

- **Isaias:** all three SME2 algorithms agree the soil got wetter after the
  hurricane (30 Sep → 12 Oct: DSG +0.018, PMI +0.047, TSR +0.052 m³/m³),
  matching our +0.5 dB scene brightening. A pre-landfall pass (8 Oct eve)
  sits in between. Caveat: beta algorithms disagree on absolutes and
  "clear"-flag coverage is sparse — deltas only.
- **Snyder:** SME2/DSG (87% clear flags) shows the **east half wetter than
  the west on both dates** (0.19 vs 0.12 in June, 0.20 vs 0.14 in July) —
  independent backing for our "vegetation/moisture change, correctly not
  flagged" read of the eastern bright patch.

Our flood rule (flag only *darkening* that ends *water-dark*) is naturally
immune to wet-soil brightening — moisture can only push pixels *away* from
the flood gate, never into it. That's a design choice, not luck.

**Bottom line for judges:** we retrieve *change*, SME2 retrieves *moisture*,
and the two agree where they overlap.

---

## 4. Our method, step by step

Every case runs the same pipeline (numbers are the shipped defaults):

1. **Pick a same-mode pair.** Two passes over the same place, same flight
   track, same radar settings (beam + polarisation mode). A guard script
   *refuses* mismatched pairs — an early Nepal mistake (mixed modes) produced
   a fake scene-wide gradient, so the guard now makes that failure impossible.
2. **Cut out the event box.** The raw satellite files are huge (~1–7 GB each);
   we read just the rectangle around the event.
3. **Calm the speckles.** Radar images are grainy (called *speckle*). A 3×3
   median filter smooths each pixel with its neighbours — like squinting to
   see the big shapes.
4. **Subtract.** After-minus-before in dB, per pixel. This is the change map:
   blue = darker, red = brighter.
5. **Threshold.** Keep pixels darker by ≥1.5 dB (fire, HV) or ≥2 dB (flood,
   HH). Floods add a second gate: the "after" pixel must itself look like
   water (very dark), and permanent lakes/rivers (dark on *both* dates) are
   masked out — a lake is not a flood.
6. **Clean up.** Drop isolated specks (minimum blob size); floods get a DEM
   land mask so choppy/quieter sea can't fake a flood.
7. **Draw outlines.** Convert kept pixels to polygons (GeoJSON), measure area
   in km², and score against official truth (precision/recall/IoU).
8. **Audit.** Slope check (are flags on flat ground or radar-shadowed cliffs?),
   threshold sweep (is the cutoff at the knee of the curve, not a round
   number?), null test (do flags sit nearer rivers than random points?).

No machine learning anywhere. Every number on the map can be traced to one
threshold and explained in a sentence.

---

## 5. The six cases, one by one

### 5.1 Snyder Fire — the hero (Detected)

Late-June 2026 wildfire on the Colorado–Utah line. Pair: 17 Jun → 23 Jul,
same track, HV channel. Result: **40.9 km²** of darkening, **every pixel
inside** the official NIFC perimeter (precision **1.00**, recall 0.335, IoU
0.335). A second, independent check against NIROPS aircraft heat maps agrees
(precision 1.00, recall 0.335; half the scattered heat sits in our core). The
red "brighter" patch east of the fire is vegetation/moisture change — flagged
by nothing, because we only flag darkening. A GUNW coherence second vote was
tested and honestly dropped (0.73 vs 0.76 — no split on arid ground).

### 5.2 Thunder Bay 36 — the giant (Detected)

Ontario's largest fire ever (~314,000 ha), started 12 Jul 2026; our "before"
pass is 11 Jul — one day pre-ignition. Same HV 1.5 dB method as Snyder for a
like-for-like comparison. Result: **235 km²** severe core (~7% of the reported
complex, which includes unburned interior and merged fires). Ontario publishes
no 2026 perimeter yet, so the pending check is NASA FIRMS satellite hotspots
(needs a free API key — the one input we're still waiting on).

### 5.3 Nepal Rasuwa GLOF — the gorge (Detected)

On 26 Aug 2026 a glacier lake burst in Rasuwa district; the flood ran down the
Bhote Koshi gorge. Pair: 19 → 31 Aug, same mode, HH. Result: **2.4 km²** of
wet-channel darkening at **0.99 precision / 0.18 recall** vs the official HOT
flood polygon — five days after the peak, the wettest channel still shows.
Special tuning preserved rivers only 1–2 pixels wide, and the slope audit
confirms flags sit on valley floors (8° vs 33° background). Fun context: ISRO
later found the same site creeping in *deformation* data weeks before the
burst — a different method, same valley, complementary story.

### 5.4 Latvia flood — the honest negative (Negative)

Peak rain 21–22 Aug; our pair is 18 → 30 Aug — over a week late. The scene
median **brightened** (+0.2 dB): dry-down, not flood. 40 fragments, sitting a
median 1.1 km from mapped rivers vs 1.0 km for random points — no association.
We then ran a 7-rule experiment on the raw data (looser gates, HV-only,
HH−HV ratio, dual-pol agreement): HV found **zero** pixels, loosening only
added fragments. The negative survived every method we threw at it.

### 5.5 Crete flood — the drained flash flood (Negative)

440 mm of rain in 48 h (2–4 Oct, EMSR933); our "after" pass is 9 Oct — five
days later. With a DEM land mask (which killed 58 km² of sea-state false
alarms), the result is 27 pixels / 0.17 km², precision 0.33 / recall 0.01 vs
748 Copernicus polygons — and the truth pixels themselves read −9 dB with
*zero* darkening. The water was simply gone. A mid-event pair exists but its
valid swath misses the flooded area. Lesson, stated on the map: *timing is
everything.*

### 5.6 Hurricane Isaias — the maybe (Marginal)

Cat 2 landfall near Destin, Florida, 9 Oct 2026. The ideal 9-hours-after pass
turned out to be a frame-edge sliver (unusable — rejected, documented); the
usable pair is 3 days post-landfall. Result: **0.52 km²** of dark bay fringe
in a rain-soaked (+0.9 dB) landscape — plausible residual surge water, shown
with caveats, **unvalidated** (no USGS high-water event published yet).

---

## 6. How we prove we're right

| Check | What it does | Where it passed |
|-------|--------------|-----------------|
| Official-overlap scores | precision / recall / IoU vs NIFC, NIROPS, HOT, Copernicus | Snyder 1.00, Nepal 0.99 |
| Second independent truth | a *different* sensor agrees (aircraft IR vs satellite) | Snyder NIROPS |
| Null test | flags must beat random points (else: noise) | Latvia failed honestly → negative |
| Slope audit | flags must sit on plausible terrain, not radar shadows | all 6 clean |
| Threshold sweep | cutoff picked at the curve's knee, not a round number | Nepal 2.0 dB |
| Same-mode guard | cross-settings pairs are refused automatically | all 6 pass; 2 bad pairs rejected pre-download |
| Method experiment | 7 detection rules compared head-to-head | Latvia: none rescue it |
| Software tests | 9 unit tests + 104 live end-to-end checks | all green, 30 Oct 2026 |
| GUNW coherence vote | flood flags must sit on decorrelated pixels | Nepal 0.11 vs 0.59 — strong confirm; Latvia 0.19 vs 0.39 — real change, not river water |
| SME2 cross-check | scene wetness vs official soil-moisture product | Isaias + Snyder agree (deltas) |
| Pair search | a nearer-peak pair must not exist unexamined | Latvia: none exists on any track |

---

## 7. How we compare with the rest of the world

We are a threshold method (one cutoff, explainable). Here's the honest
scoreboard against published numbers:

| Benchmark / product | Their number | Us | Reading |
|---------------------|--------------|----|---------|
| Sen1Floods11 flood IoU: simple threshold | ~0.35 | Snyder IoU 0.335 (fire) | **in-family** for a fixed threshold |
| Sen1Floods11 flood IoU: deep nets | 0.38–0.42 | — | DL gains ~0.05 IoU at the cost of explainability — we skip it deliberately |
| OPERA DSWx-S1 open water (C-band) | 93% overall, IoU ~0.75 | different task (static water vs our *change*) | institutional product; ours is the change lens |
| OPERA DSWx-NI (NISAR water, validated Oct 2026) | ≥80% open-water requirement | our negatives are *timing* negatives, consistent | the product to co-display next |
| Riverine flood F1 (Nat. Comms. 2026) | 0.69 | Nepal P 0.99 / R 0.18 | our conservative point on the same curve |
| Flood under trees/buildings | IoU ~0.04 (**everyone fails**) | we under-map rather than guess | same wall, honest posture |
| NISAR soil moisture (SME2, 200 m) | goal 0.06 error; NRSC maps Feb 2026 | not retrieved (out of scope) | gap documented + proposal in §10 |
| Boreal HV burn drop (literature) | 3–6 dB | Thunder Bay mapped at ≥1.5 dB | Snyder arid −1.24 dB also consistent |

Takeaway: our numbers sit where the literature says a threshold method should
sit, our negatives match the field's known hard cases (timing, canopy), and
the one real gap — quantitative soil moisture — belongs to a dedicated product
we name and propose to cross-check.

---

## 8. The technology (what runs where)

You don't need to know any of this to use the demo — this is for the curious.

**Data flow (left to right):**

```text
NISAR satellite → NASA Earthdata (raw .h5 files, GBs)
      → Python scripts (download → cut box → despeckle → subtract
        → threshold → polygons → scores) → outputs/*.json/*.png/*.geojson
      → FastAPI server :8000 (serves numbers + map tiles)
      → React + Leaflet website :5173 (the map you click)
```

- **Processing:** Python (numpy, h5py, rasterio, shapely). Runs in a pinned
  folder `.conda/env` (Python 3.12) because the system Python is an odd alpha
  that can't build packages — one of many small war stories in §11.
- **Server:** FastAPI (`app/main.py`) — endpoints like `/api/cases`,
  `/api/case?name=nepal`, `/api/geojson/change`. Tiny, fast, boring on purpose.
- **Website:** React + Vite + Leaflet (`web/`). Dark "briefing console" design,
  case tabs with verdict dots, floating layer dock, before/after swipe slider,
  click-any-fragment inspector, and an 8-step guided Pitch mode (arrow keys work).
- **Truth sources:** NIFC fire perimeters, NIROPS aircraft IR, Copernicus
  Emergency Mapping (EMSR926/927/933), HOT OpenStreetMap flood polygons,
  Sentinel-2 optical (the "why radar" cloud comparison), Copernicus DEM slopes.

---

## 9. How to run it yourself

**Just look (2 minutes):** two terminals, repo root:

```text
venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
cd web && npm run dev -- --host 127.0.0.1 --port 5173
```

Open **http://127.0.0.1:5173**. Click the case tabs, flip layers, drag the
Swipe slider, click any red fragment, press **Pitch** for the guided tour.

**Reproduce from NASA (hours, ~15–35 GB disk, free Earthdata account):** each
case has a download + change script pair, e.g.
`scripts/download_latvia.py` → `scripts/change_latvia.py`. Never put your
password in a file — use environment variables. (And rotate the password after
hackathon season if you ever pasted it in chat. Ask us how we know.)

**Verify:** `venv/bin/python -m unittest discover -s tests` (9 tests, <1 s),
`cd web && npm run build`, and the 104-check live probe in `/tmp` on request.

---

## 10. Honest limitations & what's next

1. **Timing beats method.** Three cases are negative/marginal because the
   12-day revisit missed the water. Fix: check the event date against the
   pass calendar *before* downloading (we do now).
2. **Recall is low by design** (0.18–0.34). We map severe cores, not full
   extents. For a briefing tool that's the right trade; say it out loud.
3. **Soil moisture is cross-checked, not retrieved** (SME2 deltas agree on
   Isaias + Snyder). Still open: SMAP comparison, per-pixel wetness covariate.
4. **Thunder Bay truth pending** (FIRMS key), **Isaias truth pending** (USGS).
5. **No coherence second vote on fires** (tested, no split on arid ground),
   **no ML** (benchmark gain ~0.05 IoU — not worth it for a demo).
6. **Demo-day hardening:** offline tile pack, one-command start, USB backup of
   `outputs/` + the built site.

---

## 11. War stories (what broke, what we learned)

- **The Nepal gradient.** Our first Nepal pair mixed two radar modes and
  painted a fake scene-wide gradient. Fix: a same-mode guard that refuses bad
  pairs — now covered by tests, can never silently recur.
- **The 58 km² ocean.** Crete's first flood map was mostly sea. Fix: a DEM
  land mask (downloaded tile-by-tile from the cloud, with timeouts after it
  hung on missing ocean tiles).
- **The Python that couldn't.** The laptop's default Python is a 3.16 alpha
  that can't build common packages. Fix: a self-contained Python 3.12
  environment inside the project folder.
- **The sliver.** Isaias's perfect-timing pass covered only a frame-edge strip
  of the city. Fix: check KML footprints *before* downloading gigabytes.
- **The sign flip.** Thunder Bay's auto-threshold picked "brighter" because of
  one bright blob. Fix: explicit decrease-only default for fires.

---

## A–Z glossary

- **After / before** — the two satellite passes being compared.
- **Backscatter** — loudness of the radar echo; our raw material.
- **Change detection** — mapping what differs between two images.
- **Coherence (GUNW)** — a second NISAR product measuring phase stability;
  tested, dropped for arid fires.
- **dB (decibel)** — log unit for echo strength; our thresholds live here.
- **DEM** — elevation map; used for land masks and slope audits.
- **DSWx** — NASA OPERA's surface-water product family (S1 = Sentinel-1
  radar, HLS = optical, NI = NISAR). Our institutional reference.
- **EMSR** — Copernicus Emergency Mapping activation code (926 Latvia,
  927 Nepal, 933 Crete).
- **FIRMS** — NASA's fire-hotspot feed; pending truth for Thunder Bay.
- **GCOV** — our NISAR product: geocoded polarimetric covariance
  (calibrated backscatter on a map grid).
- **GeoJSON** — the text format of our map outlines.
- **GLOF** — glacial lake outburst flood (Nepal).
- **GUNW** — NISAR interferogram product (see Coherence).
- **HH / HV** — radar channels: transmit-H receive-H (water), transmit-H
  receive-V (fire).
- **HOT** — Humanitarian OpenStreetMap Team; flood polygons for Nepal.
- **IoU** — overlap ÷ union; the single strictest map score.
- **L-band** — NISAR's long radar wave (~24 cm); sees through cloud/smoke.
- **NIFC / NIROPS** — US fire perimeter authority / aircraft IR mappers.
- **Null test** — "do our flags beat random dots?" Anti-self-deception check.
- **OPERA** — NASA JPL project turning SAR into ready products (DSWx, DISP).
- **Precision / recall** — "how much of ours is real" / "how much of real is ours."
- **Sen1Floods11** — the standard SAR-flood benchmark (C-band); our calibrator.
- **SMAP / SME2** — NASA's soil-moisture satellite (9 km) / NISAR's 200 m
  soil-moisture product.
- **Speckle** — radar grain; tamed with a median filter.
- **Threshold** — the dB cutoff; ours are swept, cited, and fixed.
- **USGS STN** — high-water-mark network; pending truth for Isaias.
- **Verdict** — our bottom line per case: detected / negative / marginal.

---

*Sources: NIFC WFIGS; NIROPS; Copernicus EMS (EMSR926/927/933); HOTOSM;
NASA ASF DAAC / Earthdata; OPERA DSWx validation (93% S1, ≥80% NI);
Sen1Floods11 (Bonafilia et al. 2020 + follow-ups); NISAR soil-moisture
multi-scale algorithm (RSE, ubRMSE 0.027–0.036 vs 0.06 goal); NRSC Feb-2026
maps; Nat. Comms. 2026 flood-limits paper; ENVI SARscape NISAR notes.*

*Generated 30 Oct 2026 from the shipped code, outputs, and test logs. Numbers
in this doc are the committed `outputs/*/summary.json` values.*
