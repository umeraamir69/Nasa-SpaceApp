---
tags:
  - research
  - data
date: 2026-10-29
---

# Accuracy review: is the log-ratio approach right, and how do we prove it

Question: are our maps accurate, can we test that with numbers, and what would
do better? Short answer: the method is the published standard for its class,
our Snyder numbers sit where the literature says they should, and the honest
gaps are (a) no threshold-sensitivity analysis yet, (b) no terrain audit yet,
(c) floods lack ground truth. This note records the calibration and the fixes.

## 1. Our method in one paragraph

80 m NISAR GCOV backscatter, 3×3 median despeckle, per-pixel log-ratio
(after − before in dB), one-sided threshold (fires: HV darkening ≥1.5 dB;
floods: HH darkening ≥2 dB + after looks like water), permanent-water masking
for floods, blob-size filter, polygonize. No ML. Deterministic and explainable.

## 2. Literature calibration (all numbers external)

- **L-band boreal burn drops 2–3 dB (HH) and 3–6 dB (HV).**
  Classic ALOS result for boreal forest. Snyder is arid mesa, not boreal, so
  our inside-median of −1.24 dB (HV) being smaller is *consistent*, not weak.
  Prediction: Thunder Bay 36 (boreal) should show multi-dB HV drops. Test it.
- **L-band noise floor ≈ 1.2 dB.** An independent 2026 NISAR/Sentinel-1 fire
  test (Frijoles) measured +0.17 dB over burn against a 1.22 dB floor. Our
  1.5 dB fire threshold sits just above the floor — the right place.
- **Threshold flood mapping scores IoU ≈ 0.35; deep models 0.38–0.42.**
  Sen1Floods11 benchmark (Sentinel-1 C-band). Our Snyder IoU 0.335 vs NIFC is
  in-family for a fixed-threshold method, and we publish precision/recall
  instead of hiding behind one number.
- **A second Space Apps team cites −6.8 dB HV for boreal fire** (Team Zenith,
  Dancing with SARs). Same sign, same band, same order as the literature.

## 3. Scorecard per case (committed numbers)

| Case | Metric | Value | Verdict |
|---|---|---|---|
| Snyder | precision vs NIFC | 1.00 | no false positives in crop |
| Snyder | recall vs NIFC | 0.335 | under-maps: severe core only |
| Snyder | IoU vs NIFC | 0.335 | in-family for threshold SAR |
| Snyder | precision/recall vs NIROPS heat perimeter | 1.00 / 0.335 | independent corroboration |
| Snyder | scattered-heat recall | 0.51 | active fire sits in our core |
| Latvia | waterways proximity | 1.1 km vs 1.0 km random | no river association → negative |
| Latvia | scene median | +0.2 dB | dry-down, not flood |
| Nepal | precision / recall vs HOT flood | 0.99 / 0.18 | same-mode 098_A_016 19→31 Aug, --no-open |
| Nepal | slope audit | 8° flagged vs 33° bg | valley floors, gating works |

## 4. What we added to test harder (29 Oct)

1. **DEM slope audit** — `scripts/validate_slopes.py`. Copernicus 30 m DEM
   (AWS open data, no auth), slope per flagged pixel vs box background.
   Separates layover artifacts from real change, especially Nepal.
   Patches `slope_check` into each summary.
2. **Threshold sweep** — `scripts/threshold_sweep.py`. Sweeps the dB cut on any
   npz crop against any truth polygon, prints precision/recall/IoU per cut.
   Run it on Nepal the moment the same-mode pair lands; pick the knee, not a
   round number.
3. **Null-model discipline** — every future case reports detection-vs-random
   (the Latvia waterways check is the template), not just raw km².
4. **Granule guard** — `scripts/granule_modes.py` refuses cross-mode pairs.
   The Nepal failure cannot silently recur. Covered by unit tests.

## 5. What would do better (ranked, honest costs)

1. **Coherence second vote (GUNW)** where a co-event pair exists. Floods:
   open water decorrelates hard — the Latvia note already flags this as the
   real upgrade. Fires on arid ground: proven weak (0.73 vs 0.76), skip.
2. **Dual-pol agreement** (HH *and* HV must move). Kills speckle false
   positives; costs some recall. The Latvia experiment script compares it.
3. **DEM slope/layover mask in the pipeline**, not just audit. Free DEM,
   small code, real false-positive cut in mountains.
4. **Adaptive threshold** (Otsu/Kittler on the diff histogram) instead of a
   fixed dB cut. Standard upgrade; keep the fixed cut as the explainable
   baseline for the pitch.
5. **Texture filter comparison** (median vs Lee/refined-Lee). Probably ±5%,
   not the bottleneck. Do last.
6. **ML classifier**: the scorecard says no, and the benchmark agrees the gain
   over thresholds is ~0.05 IoU. Not worth the explainability loss for a demo.

## 6. Thunder Bay / Crete / Isaias pair verification (29 Oct, CMR)

| Event | Pair (same track/beam/mode) | Timing |
|---|---|---|
| Thunder Bay 36 | 041D f062/f063, 4005 DHDH, 11 Jul → 16 Aug | before 1 day pre-ignition |
| Thunder Bay 36 (alt) | 018A f027/f028, 11 Jul equiv → 14 Aug | tighter after |
| Crete flood | 137D f070/f071, 2005 DHDH, 27 Sep → 9 Oct | −5 d / +5 d around 2–4 Oct |
| Crete (alt) | 158A f019/f020, 29 Sep → 11 Oct | −3 d / +7 d |
| Isaias | 148A f017, 4005 DHDH, 28 Sep → 10 Oct | after ≈ 9 h post-landfall |
| Isaias (alt) | 004A f016/f017, 30 Sep → 12 Oct | −9 d / +3 d |

Traps found: Crete 057A 22 Sep is SHSH (single-pol) — cross-mode vs DHDH,
the guard catches it. Isaias 127D 9 Oct 00:29 UTC is *before* landfall
(01:30 UTC 10 Oct) — not an after. Ontario LIO perimeters stop at 2025, so
Thunder Bay truth = FIRMS VIIRS hotspots (free key) ± GWIS burned area.

Related: [[research/Change detection]] [[research/NISAR data access]]
[[docs/Score upgrades]] [[research/Candidate events]]
