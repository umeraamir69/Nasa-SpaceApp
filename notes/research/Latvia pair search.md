---
tags:
  - research
  - data
date: 2026-10-30
---

# Latvia nearer-peak pair search: no better pair exists

Question: peak rain was 21–22 Aug 2026; our shipped pair (080_D_059, 18 → 30
Aug) is 8+ days post-peak. Does any same-mode pair bracket the peak better?

## Search (CMR, 30 Oct 2026)

Box (21.4, 56.4, 23.1, 57.4), `NISAR_L2_GCOV_PROVISIONAL_V1`:

- **19 → 29 Aug window: exactly 2 granules** — `100_A_030` and `100_A_031`,
  both **20 Aug** (pre-peak). Same track's after pass falls 1 Sep (12-day
  revisit) — *later* than our shipped 30 Aug after. Net worse, not better.
- **21 → 24 Aug: zero acquisitions on any track.** The 12-day cadence gives
  18 → 30 Aug on both covering tracks (080_D_059, 071_A_030/031). Nothing
  exists near the peak.
- 071_A_030 was tried as an alternative before: empty crop (frame edge miss).
  Same dates anyway, so no timing gain possible.

## Conclusion

080_D_059 18 → 30 Aug is the best-timed same-mode pair that exists. The Latvia
negative stands on timing physics (revisit cadence), not for lack of searching.
Recorded in `outputs/latvia/summary.json` under `pair_search`.

Related: [[research/Accuracy review]] [[research/Flood candidates]]
