---
tags:
  - ops
---

# Runbook: Weekend kit

## When to use

The week before 14–15 Nov, and again Friday night of the hackathon. Demo must not depend on Earthdata or this laptop’s wifi.

## On the stick / second drive

Copy these. `data/` is ~16 GB. `outputs/` is ~4 MB and is enough if the map dies.

```text
Nasa-SpaceApp/          # git clone or zip of the repo
  venv/                 # optional: pre-built Python env
  web/node_modules/     # optional: npm already installed
  data/snyder/          # two GCOV .h5 + optional GUNW (gitignored)
  outputs/snyder/       # change.png, GeoJSON, layers/*.png
  ref/snyder/           # NIFC GeoJSON
notes/docs/Pitch.md     # 3-minute script
outputs/snyder/change.png   # USB fallback if the map will not start
```

## Bring

- Laptop + charger
- USB / SD with the copy above
- Phone stopwatch
- Offline: this runbook + [[docs/Pitch]] printed or in Obsidian

## Start (two terminals, repo root)

```text
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```text
cd web
npm run dev -- --host 127.0.0.1 --port 5173
```

Open http://127.0.0.1:5173 **before** the pitch. Reload is ~15 s. Click path: [[docs/Pitch]]

If Vite dies: `ERR_CONNECTION_REFUSED` on :5173 means the process is gone, not a bad URL. Restart the two commands.

If the laptop dies: hold up `outputs/snyder/change.png`. Same story: yellow NIFC is in `outputs/snyder/perimeter_nifc.geojson` / the PNG overlay.

## Do not do on weekend

- Live Earthdata download
- Thunder Bay pull
- Frequency A 10 m
- `pip install` / `npm install` if you already copied `venv/` and `node_modules/`

## Related

- [[Runbooks/Run the app]]
- [[Runbooks/Snyder pipeline]]
- [[docs/Get the data]]
