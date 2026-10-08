---
tags:
  - docs
  - product
---

# Product vision

**EchoLens** visualizes surface change from spaceborne SAR so a judge (or responder) can see *what changed, where, and why we trust the signal* in a few minutes.

## Challenge

**Dancing with the SARs** — NASA Space Apps Toronto 2026, Nov 14–15, Centennial College.

Track and visualize surface change using **NISAR** (NASA-ISRO SAR) radar data, at any location worldwide. Fair game: wetland loss, wildfires, earthquakes, farming activity, glacier movement, and more. We pick one for the MVP.

## What changed

Earlier thinking treated Sentinel-1 as the default source. The confirmed challenge names **NISAR**. Data access must be verified against what NISAR actually publishes — this week, not hour 2 of the hackathon. Sentinel-1 remains the fallback if coverage is thin, pitched as a NISAR-compatible methodology. [[research/NISAR data access]]

## MVP story

1. Two real radar passes around a documented event.
2. A change-detection image that is visibly believable.
3. A map UI: before / after / change / **confidence**, plus a briefing card (dates, km², why we trust it).
4. A ground-truth perimeter on the same map, cited.
5. A 3-minute pitch that a non-scientist can repeat.

Primary change type is **wildfire**. Event is the Snyder Fire. [[research/Change types]] [[decisions/ADR-002 Primary event Snyder Fire]]

## Out of scope for MVP

- Covering every change type
- Live downloads during the event
- ML classification of change types (stretch only)

Related: [[docs/Complete plan]] [[docs/Tech stack]] [[Tasks]]
