---
tags:
  - adr
status: accepted
date: 2026-09-23
---

# ADR: Primary event is the Snyder Fire

## Context

We locked wildfire as the MVP type. Two 2026 events have public NISAR L2 granules. We need one primary story.

## Decision

**Primary case study: Snyder Fire** (Mesa County, CO / Grand County, UT), 27 Jun – 17 Jul 2026, 28,264 acres, contained.

Reason: same-track GCOV pair exists (track `048_A_021`, 17 Jun → 23 Jul), after-window sits before the 27 Jul–10 Aug NISAR gap, and the fire is dated and contained.

**Stretch / second story: Thunder Bay 36** (Wabakimi, Ontario) if the Snyder pair processes cleanly. More granules and a Canadian / Local Impact angle.

Flood stays a later type, not a second event this week.

## Consequences

- Downloads start with the Snyder `048_A_021` GCOV pair
- Ground truth should be a Snyder / Westwater perimeter (InciWeb / NIFC / news), not Ontario
- Pitch lead is a western US burn scar; Thunder Bay is the “and it works in Canada” beat if we get there

## Related

- [[Decisions]]
- [[research/Candidate events]]
- [[research/NISAR data access]]
