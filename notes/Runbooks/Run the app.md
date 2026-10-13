---
tags:
  - ops
---

# Runbook: Run the EchoLens app

## When to use

Week 4+ local demo. FastAPI serves Snyder GeoJSON; Vite is the map UI.

## Steps

From the repo root, two terminals:

```text
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```text
cd web
npm install --cache ../.npm-cache
npm run dev
```

Open http://127.0.0.1:5173

Vite proxies `/api` and `/media` to `:8000`. If `outputs/snyder/layers/` is missing, run `python scripts/pipeline_snyder.py` (or `change_snyder.py` then `fetch_optical.py`). Optical needs `optical.png` or the chip stays hidden.

## If it fails

- `/api/case` 404 — change script has not been run
- Map tiles load, no scar — check `/api/geojson/change` and `/media/layers/change.png`
- `EACCES` on npm — use `--cache ../.npm-cache`, do not sudo

## Related

- [[docs/Tech stack]]
- [[research/Change detection]]
- [[Runbooks]]
