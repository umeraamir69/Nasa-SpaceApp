---
tags:
  - adr
status: accepted
date: 2026-10-15
---

# ADR: Stretch second case is flood (Latvia EMSR926)

## Context

Snyder wildfire is proven. The challenge allows any surface-change type. We were asked for a second event and specifically flood. We will not replace the MVP or download ~14 GB on a nearly full disk.

Three 2026 floods have NISAR L2 granules (searched 15 Oct): Latvia EMSR926, Nepal GLOF EMSR927, Ottawa 1 Jul storms.

## Decision

- **Primary remains Snyder Fire.** Pitch still opens on wildfire.
- **Stretch case 2 is flood**, preferred event **Latvia–Lithuania EMSR926** (21–22 Aug 2026), GCOV track `080_D_059` 18 Aug → 30 Aug (western Latvia). `071_A_030` is the wrong swath.
- Nepal EMSR927 is the backup if we need a published flood polygon first. **Added as a third chip on 20 Oct** (Latvia products kept; Latvia granules deleted so `048_D_074` fits). See [[docs/Task 3]].
- Ottawa / Niagara are not processed (urban flash; Niagara sits in the NISAR gap).
- **Download** only after Snyder **granules** are off this disk (products in `outputs/snyder/` stay). Done 15 Oct: Snyder `.h5` deleted, Latvia `080_D_059` downloaded.

## Consequences

- Search script grows `--event latvia-flood|nepal-glof|ottawa-flood`.
- Flood math is the same log-ratio **plus** a permanent-water mask.
- Map case switcher is live when `outputs/latvia/summary.json` exists. Default chip is still Snyder.
- We are not covering all four change types. One fire + one flood.

## Related

- [[Decisions]]
- [[research/Flood candidates]]
- [[decisions/ADR-001 Change type wildfire]]
- [[decisions/ADR-002 Primary event Snyder Fire]]
