---
tags:
  - index
---

# EchoLens

NASA Space Apps Toronto 2026 — **Dancing with the SARs**. Track and visualize surface change with **NISAR** (NASA-ISRO SAR) radar, anywhere on Earth. Demo weekend is **Nov 14–15** at Centennial College. ~7 weeks of runway from Sep 23.

Obsidian is the project brain. The vault is this `notes/` folder. Cursor reads and writes these same files.

## Start here

- [[docs/Task 1]] — **teammates: see the Snyder map, then optionally rebuild it**
- [[docs/Task 2]] — Latvia flood stretch (chip on the same map)
- [[docs/Task 3]] — Nepal GLOF EMSR927 (official flood polygons)
- [[Tasks]] — **the checklist. This week first.**
- [[docs/Complete plan]] — today → demo day
- [[docs/Get the data]] — Track B download appendix
- [[Runbooks/Run the app]] — **Week 4 map** (http://127.0.0.1:5173)
- [[docs/Pitch]] — **3-minute script**
- [[docs/Team page]] — **paste this on the Space Apps team page**
- [[research/Why SAR optical]] — cloudy Sentinel-2 over Snyder
- [[docs/What I need]] — blockers to start
- [[docs/Score upgrades]] — what raises the score
- [[docs/Product vision]]
- [[research/NISAR data access]] — first technical risk
- [[research/Change types]] — pick one, don't cover all
- [[research/Candidate events]] — Snyder vs Thunder Bay 36

## Map

### Docs
- [[docs/Index]]
- [[docs/Product vision]]
- [[docs/Complete plan]]
- [[docs/Tech stack]]
- [[docs/Risk log]]

### Work
- [[Tasks]]
- [[Inbox]]
- [[sessions/2026-09-23]]
- [[sessions/2026-10-20]]
- [[sessions/2026-10-26]] — chat backup (Nepal GLOF / Colab)

### Research
- [[Research]]
- [[research/NISAR data access]]
- [[research/Change types]]

### Decisions
- [[Decisions]]

### Ops
- [[Runbooks]]
- [[Runbooks/Earthdata login]]

## Current status

**30 Oct 2026** — Six cases live: Snyder, Thunder Bay 36, Nepal (same-mode reprocessed), Latvia (proven negative), Crete (negative), Isaias (marginal). Inspector + swipe + pitch mode + redesign shipped. Full guide: `docs/a-to-z.md` (repo root). Still open: FIRMS key (Thunder Bay truth), Earthdata password rotation, demo-day hardening. Demo **14–15 Nov**.

**2 Nov 2026** — Nine cases: + Second Flat (detected, P 0.97), Coleman Creek (fuel negative), Spokane (WUI negative). Valencia attempted → dead end (truth off valid swath). Otsu/KI tested (IoU 0.61/0.94, recorded, not shipped). Overview mode + print briefing + timelines shipped. Log: `docs/expansion.md`.

## How we use this vault

1. Capture in [[Inbox]] or a Daily Note under `sessions/`.
2. Promote into `docs/`, `decisions/`, `research/`, or runbooks.
3. Link with `[[wikilinks]]`.
4. Never store real secrets here (no Earthdata passwords).
