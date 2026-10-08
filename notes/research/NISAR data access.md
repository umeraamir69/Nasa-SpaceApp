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

Script: `python scripts/search_nisar.py --event snyder|thunder-bay`

## Log

| Date | What | Result |
|---|---|---|
| 2026-09-23 | Earthdata login | Authenticated |
| 2026-09-23 | Snyder Fire GCOV | Before 17–26 Jun: **8**. After 18–26 Jul: **3** |
| 2026-09-23 | Snyder Fire GUNW | Before: **2**. After: **9** |
| 2026-09-23 | Thunder Bay 36 GCOV | Before 17 Jun–11 Jul: **20+**. After 11 Aug–15 Sep: **20+** |
| 2026-09-23 | Thunder Bay 36 GUNW | Before: **16**. After: **20+** |

## Best Snyder pair (same track)

GCOV track `048_A_021`:

- Before: `NISAR_L2_PR_GCOV_023_048_A_021_..._20260617T122757`
- After: `NISAR_L2_PR_GCOV_026_048_A_021_..._20260723T122754`

Descending `056_D_068` / `056_D_069` also have Jun 18 / Jul 24 pairs.

Both Snyder GCOV granules are on disk (2026-09-23):

- `data/snyder/gcov/NISAR_L2_PR_GCOV_023_048_A_021_..._20260617....h5` (6.9 GB, before)
- `data/snyder/gcov/NISAR_L2_PR_GCOV_026_048_A_021_..._20260723....h5` (7.1 GB, after)

Related: [[research/Candidate events]] [[decisions/ADR-001 Change type wildfire]] [[decisions/ADR-002 Primary event Snyder Fire]]
