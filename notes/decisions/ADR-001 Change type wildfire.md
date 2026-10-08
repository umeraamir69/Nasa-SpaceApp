---
tags:
  - adr
status: accepted
date: 2026-09-23
---

# ADR: MVP change type is wildfire

## Context

The challenge allows any surface-change type. We need one primary type so data pull, demo, and pitch stay aligned. Flood and others stay available if we have time after a proven wildfire pair.

## Decision

MVP is **wildfire burn scars**. Flood (and other types) only after a working wildfire case study.

Candidate events to search first: Snyder Fire (CO–UT) and Thunder Bay 36 (Ontario). The specific event is not locked until granules exist. [[research/Candidate events]]

## Consequences

- Demo story is a dated fire with a before/after radar pair
- Ground truth should be a fire perimeter (FIRMS / agency), not a flood extent
- Pitch language is disaster-response / burn scar, not inundation

## Related

- [[Decisions]]
- [[research/Change types]]
- [[docs/Product vision]]
