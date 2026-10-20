---
tags:
  - research
  - data
---

# NISAR data access

Account works locally (`earthaccess` + user `~/.netrc`). Credentials are **not** in this repo.

Products that exist and return granules:

- `NISAR_L2_GCOV_PROVISIONAL_V1` (backscatter)
- `NISAR_L2_GUNW_PROVISIONAL_V1` (unwrapped interferogram / coherence)

Script: `python scripts/search_nisar.py --event snyder|thunder-bay|latvia-flood|nepal-glof|ottawa-flood`

## Log

| Date | What | Result |
|---|---|---|
| 2026-09-23 | Earthdata login | Authenticated |
| 2026-09-23 | Snyder Fire GCOV | Before 17–26 Jun: **8**. After 18–26 Jul: **3** |
| 2026-09-23 | Snyder Fire GUNW | Before: **2**. After: **9** |
| 2026-09-23 | Thunder Bay 36 GCOV | Before 17 Jun–11 Jul: **20+**. After 11 Aug–15 Sep: **20+** |
| 2026-09-23 | Thunder Bay 36 GUNW | Before: **16**. After: **20+** |
| 2026-10-15 | Latvia flood EMSR926 GCOV | Before 11–20 Aug: **6** (incl. `071_A_030` 18 Aug). After 23 Aug–20 Sep: **12** (same track 30 Aug) |
| 2026-10-15 | Nepal GLOF EMSR927 GCOV | Before 11–25 Aug: **6**. After 27 Aug–20 Sep: **11** (`048_D_074` 16 Aug → 28 Aug; after is `QPDH`) |
| 2026-10-15 | Ottawa 1 Jul GCOV | Before 17–30 Jun: **6**. After 2–26 Jul: **11** (`098_D_065` 18 Jun → 3 Jul) |
| 2026-10-15 | Snyder GCOV + GUNW `.h5` deleted | Map products kept. Freed ~16 GB |
| 2026-10-15 | Latvia EMSR926 GCOV download | `080_D_059` 18 Aug + 30 Aug on disk (~1.6 GB × 2). `071_A_030` downloaded then removed (empty crop) |
| 2026-10-20 | Nepal GLOF EMSR927 GCOV search | Confirmed `048_D_074` 16 Aug DHDH → 28 Aug QPDH |
| 2026-10-20 | Latvia GCOV `.h5` deleted | Map products kept. Freed ~3.1 GB for Nepal |
| 2026-10-20 | Nepal EMSR927 GCOV download | Full pair is **~7 GB × 2**. Aborted. Range-read crop via `crop_nepal.py` into `data/nepal/crop/*.npz` (~1.3 MB × 2) |

## Best Snyder pair (same track)

GCOV track `048_A_021`:

- Before: `NISAR_L2_PR_GCOV_023_048_A_021_..._20260617T122757`
- After: `NISAR_L2_PR_GCOV_026_048_A_021_..._20260723T122754`

Descending `056_D_068` / `056_D_069` also have Jun 18 / Jul 24 pairs.

Snyder GCOV was on disk from 23 Sep, **deleted 15 Oct** to free space for Latvia. Map products in `outputs/snyder/` were kept.

- `data/snyder/gcov/NISAR_L2_PR_GCOV_023_048_A_021_..._20260617....h5` (6.9 GB, before) — **removed**
- `data/snyder/gcov/NISAR_L2_PR_GCOV_026_048_A_021_..._20260723....h5` (7.1 GB, after) — **removed**

GUNW (2026-10-13), same track — **removed 15 Oct**:

- `...GUNW_024_048_A_021_025..._20260629..._20260711...` (~2.3 GB, **co-event**)

Latvia GCOV was on disk 15–20 Oct, **deleted 20 Oct** so Nepal would fit. Map products in `outputs/latvia/` were kept.

Nepal GCOV **crop** on disk (2026-10-20), `python scripts/crop_nepal.py` (do not store the 14 GB pair here):

- `data/nepal/crop/before.npz` — 16 Aug DHDH HHHH/HVHV, Rasuwa box, 1.3 MB
- `data/nepal/crop/after.npz` — 28 Aug QPDH HHHH/HVHV, same box, 1.4 MB

The 11–23 Jul pair was downloaded then removed — disk was full. No 17–29 Jun pre-fire GUNW on `048_A_021`. Coherence barely drops inside the scar — see [[research/Change detection]].

Related: [[research/Candidate events]] [[decisions/ADR-001 Change type wildfire]] [[decisions/ADR-002 Primary event Snyder Fire]]
