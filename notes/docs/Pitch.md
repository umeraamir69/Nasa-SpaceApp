---
tags:
  - docs
  - pitch
date: 2026-10-13
---

# 3-minute pitch

Say this next to the live map at http://127.0.0.1:5173. Target **~450 spoken words**. Do not discover Snyder for the judges — they already know there was a fire. Sell the **method**.

Demo weekend: 14–15 Nov. Challenge: Dancing with the SARs. [[docs/Product vision]] [[docs/Why a past fire]]

## 30-second version (if cut short)

EchoLens turns two NISAR radar passes into an incident briefing: what changed, how many square kilometres, and why we trust it. We locked the Snyder Fire, June 17 to July 23, same track. Inside the official NIFC perimeter the radar goes darker by 1.2 dB. We map **40.9 km²**. Nothing we flag sits outside that line. Smoke does not matter. Cloud does not matter. Same steps on the next fire.

## 3-minute script

Times are a stopwatch, not a suggestion. Clicks assume **Change** is on and **NIFC perimeter** is on at the start.

### 0:00 – 0:25 · Hook

Smoke hides a fire from every optical satellite in the sky. NISAR does not look with light. It looks with L-band radar. EchoLens is the last mile: two real NISAR passes in, a briefing a human can read in under a minute.

We are not exploring the globe. We are answering one question: **what burned, where, and why should you believe the outline.**

### 0:25 – 0:50 · The exam with an answer key

If we pointed the code at a random forest and it drew a blob, we would not know if the blob was real. So we picked a fire with an answer key: the **Snyder Fire**, Colorado–Utah, late June 2026. Official NIFC perimeter. Same NISAR track, June 17 before, July 23 after.

Snyder is the exam. EchoLens is the method you reuse on the next fire.

### 0:50 – 1:40 · Demo *(talk while you click)*

*[Map is already on Snyder. Change layer + yellow NIFC outline.]*

This is not a photograph. Blue is darker after the fire. That dark patch is the scar. The yellow line is not ours — that is the official NIFC perimeter. Our change sits **inside** it.

*[Click **Before**.]* June 17. Radar brightness, same grid.

*[Click **After**.]* July 23. Same look angle, same track.

*[Click **Change**.]* July minus June, in decibels. The bright patch to the east is **outside** the fire. We do not call it burn.

*[Click **Confidence**.]* Grey is valid radar. Colour is change we are willing to ship.

*[Click **Optical**.]* Sentinel-2, 7 July, same box. White is cloud. That is why we do not wait for a clear photo.

**40.9 square kilometres.** NIFC mapped about 122. We are conservative on purpose: precision against that official line is **1.0**. We under-map. We do not cry wolf.

### 1:40 – 2:25 · Why we trust it

The algorithm is short on purpose. No neural net. Gamma-0 power to dB, a 3-by-3 median so speckle is not a fire, then a log-ratio. Cross-pol HV is the layer that actually drops inside the burn, about **minus 1.2 dB**.

We also pulled GUNW coherence for a second vote. On this arid mesa, L-band barely notices — 0.73 inside the fire, 0.76 outside. So we **do not fake a coherence mask**. Detection stays on backscatter. Honesty is the trust layer.

### 2:25 – 2:50 · Who it is for

The user is not “anyone with a globe.” It is an incident briefing: dates, square kilometres, a cited perimeter, and a sentence for why the outline is real. Next fire: last pass before, next pass after, same script.

### 2:50 – 3:00 · Close

EchoLens: two NISAR passes, one briefing, checked against a fire we can name. Open the map. Ask us why the east side is red. We already know.

## Click path (memorize)

Open the tab **before** you start talking. Reload takes ~15 s. Do not hook on “Loading Snyder case…”.

1. Load the app. **Change** + **NIFC perimeter** on. Point at yellow vs blue.
2. **Before** → **After** → **Change** → **Confidence** → **Optical**. Polygons hide automatically except on Change.
3. Toggle **NIFC perimeter** off and on once.
4. Click **Change**. Leave **NIFC** on for questions.

## Rehearsal — 13 Oct 2026

Timed against the live map at http://127.0.0.1:5173.

| Beat | Budget | First-pass words | @150 wpm | After cut |
|---|---|---|---|---|
| Hook | 0:00–0:25 | 63 | 0:25 | same |
| Exam | 0:25–0:50 | 70 | 0:28 | drop incident ID (it is on the card) |
| Demo clicks | 0:50–1:40 | 147 | 0:59 | cut filler; clicks themselves are ~20 s |
| Trust | 1:40–2:25 | 101 | 0:40 | drop Optical repeat |
| Who | 2:25–2:50 | 74 | 0:30 | drop Thunder Bay (FAQ only) |
| Close | 2:50–3:00 | 27 | 0:11 | same |
| **Total** | **3:00** | **482 → ~3:13** | | **403 words → 2:41 @150 / 2:53 @140** |

**What broke on the map**

- Before/After with EchoLens polygons on looks like a pink blob. The app now hides polygons unless **Change** is selected.
- Optical already hid polygons. Keep that.
- First paint after reload is slow. Pre-load.

**Human still to do:** read it out loud once with a phone stopwatch. This pass timed the clicks and the word count, not a mouth.

If the laptop dies: `outputs/snyder/change.png` on a USB stick. Same story, no map.

## Weekend click path (14–15 Nov)

1. `./demo.sh` (or two terminals — [[Runbooks/Run the app]]). Pre-load Snyder **before** you talk.
2. **Pitch** button for the guided tour, or manual: Change + NIFC → Before → After → Change → Confidence → Optical.
3. Optional 10 s: Overview (nine verdicts) or Nepal (0.99 precision) or Coleman (grass negative).
4. USB fallback: `outputs/snyder/change.png`.

Submission paste + 30 s shot list + 7 slides: `docs/submission.md`.

## If they ask

| Question | Answer |
|---|---|
| Why only 41 km² of 122? | We threshold at 1.5 dB HV drop after despeckle. Mixed burn, river, and unburned mesa stay out. Precision 1.0 is the point. |
| Why not train a model? | Two dates, one event. A log-ratio we can explain in a sentence beats a black box we cannot. SI tools helped us code; they do not draw the scar. |
| Why not live Earthdata? | Demo weekend has no network budget. Granules are already on disk. |
| Why Snyder, not Canada? | Snyder had a contained, dated pair **before** the July 27–August 10 NISAR gap. Thunder Bay is on the same map (235 km² core). |
| Latvia / Coleman found nothing? | Feature, not bug. Flood wave gone; grass barely darkens at L-band. Same week pine at Second Flat hits P 0.97. |
| Is GUNW useless? | No. It did not split **this** scar. We still show it. We do not invent a drop. |
| What is GCOV? | Geocoded polarimetric covariance. Calibrated backscatter on a map grid. Not a JPEG. |
| Why the Optical chip? | Sentinel-2, 7 Jul, 34% cloud over this box. That is the why-SAR beat, not a second scar map. |

## Speaking split (if not solo)

- **A (0:00–0:50)** hook + Snyder as the answer key
- **B (0:50–1:40)** demo clicks
- **C (1:40–3:00)** method, honesty, user, close

Solo: read it in one voice. Do not add a fourth person pointing at the legend.

Related: [[research/Change detection]] [[research/Snyder perimeter]] [[research/Why SAR optical]] [[Runbooks/Run the app]] [[docs/Score upgrades]]
