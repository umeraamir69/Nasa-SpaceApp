---
tags:
  - docs
  - plan
---

# Complete plan

How we get from **Sep 23** to demo day **Nov 14–15**. The hackathon is 48 hours; building starts now so weekend is integration, polish, and maybe a second case study.

Source: [[docs/EchoLens Project Start Plan]]

## Week 1 — Sep 23–29

**Day 1–2 — data access**

- NASA Earthdata Login (free): https://urs.earthdata.nasa.gov/
- Check NISAR on [Earthdata Search](https://search.earthdata.nasa.gov/) and [ASF Vertex](https://search.asf.alaska.edu/)
- NISAR launched in 2025 — confirm what is actually downloadable for candidate regions
- Thin coverage → Sentinel-1 fallback, same SAR principles, framed as NISAR-compatible methodology

**Day 2–4 — one change type + one real event**

- Choose one primary type ([[research/Change types]])
- Find a documented event with known before/after dates
- This decision locks data pull, demo story, and pitch

**Day 4–7 — team**

- Submit team page (Dancing with the SARs)
- Recruit: SAR/data, backend, frontend, pitch
- Shared GitHub repo + team channel now

## Weeks 2–3 — Sep 30 – Oct 13

**Week 2 — pull real sample data**

- Download two actual passes (before/after)
- Confirm visible change before writing app code; switch event if not
- Document the download so anyone on the team can repeat it

**Week 3 — algorithm, offline**

- Standalone Python: despeckle + change detection (log-ratio or coherence difference)
- Goal: one proof-of-concept change image, no app
- Read enough of the methods to back the "why it's trustworthy" pitch beat

**Oct 28:** full challenge statement may add specifics — revisit scope that week.

## Weeks 4–6 — Oct 14 – Nov 3

| Week | Dates | Build |
|---|---|---|
| 4 | Oct 14–20 | React + FastAPI/Flask shell, empty map, mock GeoJSON |
| 5 | Oct 21–27 | Wire Week 3 output as real GeoJSON; before/after toggle + summary panel |
| 6 | Oct 28 – Nov 3 | Cross-check Oct 28 statement; stretch second region/event |

## Week 7 — Nov 4–13

- Pipeline runs end-to-end once, unattended
- Both passes + processed output saved locally and backed up — no live downloads on event weekend
- Draft pitch and speaking sections
- Confirm 48-hour roles
- Chargers, offline data/code, deps pre-installed

## Event weekend — Nov 14–15

Hour-by-hour hackathon plan takes over: pipeline validation, integration, polish, pitch rehearsal, mapped to the 5 judging criteria. Because algorithm + skeleton are already proven, weekend is **integration, polish, and a second case study** — not building from zero.

## First technical step

```text
pip install earthaccess rasterio numpy matplotlib

python3 -c "
import earthaccess
earthaccess.login()
results = earthaccess.search_data(
    short_name='NISAR_L1_...',  # confirm exact product name
    temporal=('2025-01-01', '2026-09-01'),
)
print(len(results), 'granules found')
"
```

If that search is empty for the target region, search Sentinel-1 (`short_name='SENTINEL-1'`) as a placeholder while confirming NISAR coverage.

Do not put Earthdata passwords in this vault. [[Runbooks/Earthdata login]]

Related: [[Tasks]] [[docs/Tech stack]] [[docs/Risk log]]
