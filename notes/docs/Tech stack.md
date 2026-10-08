---
tags:
  - docs
  - architecture
---

# Tech stack

One language per layer. Python owns SAR/geospatial; JavaScript owns the browser.

| Layer | Language | Tools | Why |
|---|---|---|---|
| Data access | Python | `earthaccess`, `requests` | Official Earthdata client: auth, search, download |
| SAR processing | Python | `rasterio`, `GDAL`, `numpy`, `scipy` | Raster I/O + despeckle / change-detection math |
| Optional ML | Python | `scikit-learn` | Classify change types — stretch, not MVP |
| Backend | Python | FastAPI (or Flask) | Fast to stand up, serves GeoJSON |
| Frontend | JS / TS | React, Leaflet or Mapbox GL JS | Before/after toggle + summary panel. Leaflet is free; Mapbox is polish |
| Styling | CSS | Tailwind optional | Skip if hand-written CSS is faster |
| Python → JS | — | GeoJSON | Native to rasterio's world and every JS map lib |
| VCS | — | Git + GitHub | Required for submission; Week 1, not weekend |
| Hosting | — | Vercel/Netlify + Render/Railway | Live link for judges |

## Week 1 setup (when we start code)

```text
python3 -m venv venv && source venv/bin/activate
pip install earthaccess rasterio numpy scipy fastapi uvicorn

npx create-react-app echolens-frontend
cd echolens-frontend && npm install leaflet react-leaflet
```

If nobody has used `rasterio` / GDAL, budget Week 2 just to learn reading/writing rasters. Do not learn that at hour 8 of the hackathon.

Related: [[docs/Complete plan]] [[docs/Product vision]]
