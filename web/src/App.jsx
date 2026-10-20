import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "./App.css";

const RASTERS = [
  { id: "before", label: "Before" },
  { id: "after", label: "After" },
  { id: "change", label: "Change" },
  { id: "confidence", label: "Confidence" },
  { id: "optical", label: "Optical" },
];

function fmtKm2(n) {
  if (n == null) return "—";
  return `${Number(n).toFixed(1)} km²`;
}

function legendFor(raster, caseId) {
  if (caseId === "latvia" || caseId === "nepal") {
    switch (raster) {
      case "before":
      case "after":
        return "HHHH backscatter · dark = water";
      case "change":
        return caseId === "nepal"
          ? "Blue: darker after · red: brighter · flags only inside official Copernicus/HOT polygons"
          : "Blue: darker after (new water) · red: brighter";
      case "confidence":
        return "Grey: valid · steel: lakes · cyan: new water";
      case "optical":
        return "White: cloud · Sentinel-2 around the storm";
      default:
        return "";
    }
  }
  switch (raster) {
    case "before":
    case "after":
      return "HVHV backscatter · brighter = stronger return";
    case "change":
      return "Blue: darker after the fire · red: brighter (not burn)";
    case "confidence":
      return "Grey: valid radar · colour: change we ship";
    case "optical":
      return "White: cloud · Sentinel-2 7 Jul";
    default:
      return "";
  }
}

function layerUrl(cas, rasterId) {
  const hit = cas?.layers?.find((l) => l.id === rasterId);
  return hit?.url || `/media/layers/${rasterId}.png`;
}

function ledeFor(cas) {
  if (cas.case_id === "latvia") {
    return "Two NISAR L-band passes around the Latvia–Lithuania floods (EMSR926). Peak rain was ~21–22 Aug; this pair is 18 Aug → 30 Aug, so the map is leftover new water, not the crest. Permanent lakes are masked.";
  }
  if (cas.case_id === "nepal") {
    return "Two NISAR L-band passes around the Rasuwa glacier-lake outburst (26 Aug, EMSR927). Pair is 16 Aug → 28 Aug. Official Copernicus landslides and the 27 Aug flood polygon sit on the same map. Himalayan layover: we only flag HH darkening inside those official polygons.";
  }
  return "Two NISAR L-band passes around the Snyder Fire. The map is not a photo — it is radar backscatter change, checked against an official perimeter.";
}

function whySarFor(cas) {
  if (cas.case_id === "latvia") {
    return cas.has_optical
      ? "Click Optical: Sentinel-2 around the storm is cloud. L-band still sees new water as a dark HH return. Lakes dark on both dates are not flood."
      : "Cloud and rain hide optical. L-band still sees new water as a dark HH return. Lakes that were dark on both dates are not flood.";
  }
  if (cas.case_id === "nepal") {
    return "Steep Himalaya, monsoon cloud, and a gorge. Two days later the water is not a specular lake at 80 m — mixed pixels sit around −4 dB. Optical is still worse. Official Copernicus and HOT polygons are the proof; we only flag HH darkening inside them so layover slopes stay off the map.";
  }
  return cas.has_optical
    ? "Click Optical: Sentinel-2 on 7 Jul (during the fire) is white cloud over this box. Radar still returns a scar. NIROPS IR is the aircraft heat map from the same week — not FIRMS."
    : "Optical would be smoke and cloud. Radar still returns a scar. Run python scripts/fetch_optical.py to load the 7 Jul Sentinel-2 scene.";
}

function trustFor(cas, cite) {
  if (cas.case_id === "latvia") {
    return "Valid GCOV pixels, 3×3 median despeckle, HH log-ratio ≥ 2 dB darker after, and the after pixel looks like water. Permanent water (dark on both dates) is not flagged. Copernicus EMSR926 is the named event; official flood vectors were not in HDX yet.";
  }
  if (cas.case_id === "nepal") {
    return "Valid GCOV pixels, 3×3 median despeckle, HH log-ratio ≥ 2 dB darker after, and every flagged pixel sits inside Copernicus EMSR927 or the HOT 27 Aug flood polygon (same idea as NIFC on Snyder). 80 m mixed gorge pixels are not Latvia lakes. UNOSAT mapped mudflow and barrier lakes for the same dates.";
  }
  return `Valid GCOV pixels only, 3×3 median despeckle, HVHV log-ratio ≥ 1.5 dB darker after the fire. Every flagged pixel sits inside NIFC WFIGS ${cite.unique_fire_identifier || ""}. GUNW HH coherence barely drops on this arid mesa (0.73 vs 0.76) — so detection stays on GCOV, not a fake second layer.`;
}

function sourceFor(cas, cite) {
  if (cas.case_id === "latvia") {
    return "Copernicus EMS Rapid Mapping EMSR926. Pitch still opens on Snyder.";
  }
  if (cas.case_id === "nepal") {
    return "Copernicus EMSR927 (landslides along the GLOF path) + HOT flood extent 27 Aug (Bhote Koshi / Trishuli). UNOSAT Rasuwa mudflow and barrier-lake maps are the same event. Pitch still opens on Snyder.";
  }
  return `Perimeter: ${cite.polygon || ""}${cite.unique_fire_identifier ? ` · ${cite.unique_fire_identifier}` : ""}. FIRMS is hotspots, not this outline.`;
}

export default function App() {
  const mapEl = useRef(null);
  const mapRef = useRef(null);
  const layersRef = useRef({});
  const [cas, setCas] = useState(null);
  const [err, setErr] = useState(null);
  const [caseId, setCaseId] = useState("snyder");
  const [available, setAvailable] = useState([]);
  const [raster, setRaster] = useState("change");
  const [showChange, setShowChange] = useState(true);
  const [showPerim, setShowPerim] = useState(true);
  const [showIr, setShowIr] = useState(true);
  const [showLakes, setShowLakes] = useState(true);
  const [showEmsr, setShowEmsr] = useState(true);
  const [showFlood, setShowFlood] = useState(true);

  useEffect(() => {
    fetch("/api/cases")
      .then((r) => r.json())
      .then((d) => setAvailable(d.cases || []))
      .catch(() => setAvailable([]));
  }, [cas]);

  useEffect(() => {
    setCas(null);
    setErr(null);
    setRaster("change");
    setShowChange(true);
    setShowPerim(true);
    setShowIr(true);
    setShowLakes(true);
    setShowEmsr(true);
    setShowFlood(true);
    fetch(`/api/case?name=${caseId}`)
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status} from /api/case`);
        return r.json();
      })
      .then(setCas)
      .catch((e) => setErr(e.message));
  }, [caseId]);

  useEffect(() => {
    if (!cas || mapRef.current || !mapEl.current) return;
    const b = cas.bounds;
    const map = L.map(mapEl.current, { zoomControl: true, attributionControl: true }).setView(
      [39.06, -109.0],
      11,
    );
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap",
      maxZoom: 19,
    }).addTo(map);
    map.createPane("rasterPane");
    map.getPane("rasterPane").style.zIndex = 350;
    mapRef.current = map;
    layersRef.current = {};

    const imageBounds =
      b && Number.isFinite(b.south)
        ? [
            [b.south, b.west],
            [b.north, b.east],
          ]
        : null;

    const cid = cas.case_id || "snyder";
    Promise.all([
      fetch(`/api/geojson/change?name=${cid}`).then((r) => r.json()),
      fetch(`/api/geojson/perimeter?name=${cid}`).then((r) => r.json()),
      cas.has_ir
        ? fetch(`/api/geojson/overlay?name=${cid}&layer=ir`).then((r) => r.json())
        : Promise.resolve(null),
      cas.has_lakes
        ? fetch(`/api/geojson/overlay?name=${cid}&layer=lakes`).then((r) => r.json())
        : Promise.resolve(null),
      cas.has_emsr
        ? fetch(`/api/geojson/overlay?name=${cid}&layer=emsr`).then((r) => r.json())
        : Promise.resolve(null),
      cas.has_flood_extent
        ? fetch(`/api/geojson/overlay?name=${cid}&layer=flood`).then((r) => r.json())
        : Promise.resolve(null),
    ]).then(([change, perim, ir, lakes, emsr, flood]) => {
      const changeLayer = L.geoJSON(change, {
        style: {
          color: "#ee964b",
          weight: 1,
          fillColor: "#c1121f",
          fillOpacity: 0.35,
        },
      });
      const perimLayer = L.geoJSON(perim, {
        style: {
          color: "#f4d35e",
          weight: 2,
          fill: false,
        },
      });
      layersRef.current.changePoly = changeLayer;
      layersRef.current.perim = perimLayer;
      if (showPerim) perimLayer.addTo(map);
      if (showChange) changeLayer.addTo(map);
      if (ir) {
        const irLayer = L.geoJSON(ir, {
          style: (feat) => {
            const k = feat?.properties?.kind;
            if (k === "heat_perimeter") return { color: "#ff6b35", weight: 2, fill: false };
            if (k === "scattered_heat") {
              return { color: "#ffd166", weight: 1, fillColor: "#ffd166", fillOpacity: 0.4 };
            }
            return { color: "#ee964b", weight: 1, fill: false };
          },
          pointToLayer: (_feat, latlng) =>
            L.circleMarker(latlng, {
              radius: 3,
              color: "#ff6b35",
              fillColor: "#ff6b35",
              fillOpacity: 0.85,
              weight: 0,
            }),
        });
        layersRef.current.ir = irLayer;
        if (showIr) irLayer.addTo(map);
      }
      if (lakes) {
        const lakeLayer = L.geoJSON(lakes, {
          style: {
            color: "#7eb8da",
            weight: 1,
            fillColor: "#3d5a80",
            fillOpacity: 0.35,
          },
        });
        layersRef.current.lakes = lakeLayer;
        if (showLakes) lakeLayer.addTo(map);
      }
      if (emsr) {
        const emsrLayer = L.geoJSON(emsr, {
          style: {
            color: "#f4d35e",
            weight: 2,
            fillColor: "#f4d35e",
            fillOpacity: 0.18,
          },
        });
        layersRef.current.emsr = emsrLayer;
        if (showEmsr) emsrLayer.addTo(map);
      }
      if (flood) {
        const floodLayer = L.geoJSON(flood, {
          style: {
            color: "#00b4d8",
            weight: 2,
            fillColor: "#0077b6",
            fillOpacity: 0.28,
          },
        });
        layersRef.current.flood = floodLayer;
        if (showFlood) floodLayer.addTo(map);
      }
      const perimBounds = perimLayer.getBounds();
      const emsrBounds = layersRef.current.emsr?.getBounds();
      if (imageBounds) {
        map.fitBounds(imageBounds, { padding: [28, 28] });
      } else if (emsrBounds?.isValid()) {
        map.fitBounds(emsrBounds, { padding: [28, 28] });
      } else if (perimBounds.isValid()) {
        map.fitBounds(perimBounds, { padding: [28, 28] });
      } else {
        const changeBounds = changeLayer.getBounds();
        if (changeBounds.isValid()) map.fitBounds(changeBounds, { padding: [28, 28] });
      }
    });

    if (imageBounds) {
      const img = L.imageOverlay(layerUrl(cas, raster), imageBounds, {
        opacity: 0.88,
        pane: "rasterPane",
      });
      img.addTo(map);
      layersRef.current.raster = img;
    }

    return () => {
      map.remove();
      mapRef.current = null;
    };
    // map is created once when case loads
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cas]);

  useEffect(() => {
    const map = mapRef.current;
    const store = layersRef.current;
    if (!map || !cas?.bounds) return;
    if (store.raster) {
      map.removeLayer(store.raster);
      store.raster = null;
    }
    const b = cas.bounds;
    const img = L.imageOverlay(
      layerUrl(cas, raster),
      [
        [b.south, b.west],
        [b.north, b.east],
      ],
      { opacity: 0.88, pane: "rasterPane" },
    );
    img.addTo(map);
    store.raster = img;
  }, [raster, cas]);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layersRef.current.changePoly;
    if (!map || !layer) return;
    if (showChange) layer.addTo(map);
    else map.removeLayer(layer);
  }, [showChange]);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layersRef.current.perim;
    if (!map || !layer) return;
    if (showPerim) layer.addTo(map);
    else map.removeLayer(layer);
  }, [showPerim]);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layersRef.current.ir;
    if (!map || !layer) return;
    if (showIr) layer.addTo(map);
    else map.removeLayer(layer);
  }, [showIr]);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layersRef.current.lakes;
    if (!map || !layer) return;
    if (showLakes) layer.addTo(map);
    else map.removeLayer(layer);
  }, [showLakes]);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layersRef.current.emsr;
    if (!map || !layer) return;
    if (showEmsr) layer.addTo(map);
    else map.removeLayer(layer);
  }, [showEmsr]);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layersRef.current.flood;
    if (!map || !layer) return;
    if (showFlood) layer.addTo(map);
    else map.removeLayer(layer);
  }, [showFlood]);

  const cite = cas?.citation || {};

  return (
    <div className="shell">
      <header className="top">
        <div>
          <div className="brand">EchoLens</div>
          <div className="sub">NISAR surface change · Dancing with the SARs</div>
        </div>
        <div className="incident">{cas?.label || "Snyder Fire · CO–UT"}</div>
      </header>

      <div className="body">
        <div className="map-wrap">
          <div ref={mapEl} className="map" />
          <div className="map-tools">
            {available.filter((c) => c.ready).length > 1 && (
              <div className="chip-row">
                {available
                  .filter((c) => c.ready)
                  .map((c) => (
                    <button
                      key={c.id}
                      className={caseId === c.id ? "chip on" : "chip"}
                      onClick={() => setCaseId(c.id)}
                      type="button"
                    >
                      {c.label}
                    </button>
                  ))}
              </div>
            )}
            <div className="chip-row">
              {RASTERS.filter((r) => r.id !== "optical" || cas?.has_optical).map((r) => (
                <button
                  key={r.id}
                  className={raster === r.id ? "chip on" : "chip"}
                  onClick={() => {
                    setRaster(r.id);
                    // Polygons hide on Before/After/Optical so the raster is the beat.
                    setShowChange(r.id === "change");
                  }}
                  type="button"
                >
                  {r.label}
                </button>
              ))}
            </div>
            <div className="chip-row">
              <button
                className={showChange ? "chip on" : "chip"}
                onClick={() => setShowChange((v) => !v)}
                type="button"
              >
                EchoLens change
              </button>
              {cas?.has_perimeter && (
                <button
                  className={showPerim ? "chip on" : "chip"}
                  onClick={() => setShowPerim((v) => !v)}
                  type="button"
                >
                  NIFC perimeter
                </button>
              )}
              {cas?.has_ir && (
                <button
                  className={showIr ? "chip on" : "chip"}
                  onClick={() => setShowIr((v) => !v)}
                  type="button"
                >
                  NIROPS IR
                </button>
              )}
              {cas?.has_lakes && (
                <button
                  className={showLakes ? "chip on" : "chip"}
                  onClick={() => setShowLakes((v) => !v)}
                  type="button"
                >
                  Permanent lakes
                </button>
              )}
              {cas?.has_emsr && (
                <button
                  className={showEmsr ? "chip on" : "chip"}
                  onClick={() => setShowEmsr((v) => !v)}
                  type="button"
                >
                  EMSR927
                </button>
              )}
              {cas?.has_flood_extent && (
                <button
                  className={showFlood ? "chip on" : "chip"}
                  onClick={() => setShowFlood((v) => !v)}
                  type="button"
                >
                  Official flood
                </button>
              )}
            </div>
            <div className="legend">
              <div>{legendFor(raster, cas?.case_id)}</div>
              <div className="legend-keys">
                {cas?.has_perimeter && (
                  <span>
                    <i className="swatch nifc" /> NIFC
                  </span>
                )}
                {cas?.has_ir && (
                  <span>
                    <i className="swatch ir" /> NIROPS IR
                  </span>
                )}
                {cas?.has_lakes && (
                  <span>
                    <i className="swatch lakes" /> Lakes
                  </span>
                )}
                {cas?.has_emsr && (
                  <span>
                    <i className="swatch nifc" /> EMSR927
                  </span>
                )}
                {cas?.has_flood_extent && (
                  <span>
                    <i className="swatch flood" /> Official flood
                  </span>
                )}
                <span>
                  <i className="swatch echo" /> EchoLens
                </span>
              </div>
            </div>
          </div>
        </div>

        <aside className="brief">
          {err && <p className="err">API: {err}. Start the backend on :8000.</p>}
          {!cas && !err && <p className="muted">Loading Snyder case…</p>}
          {cas && (
            <>
              <h1>Incident briefing</h1>
              <p className="lede">{ledeFor(cas)}</p>
              <dl>
                <div>
                  <dt>Before / after</dt>
                  <dd>
                    {cas.before} → {cas.after}
                  </dd>
                </div>
                <div>
                  <dt>EchoLens change</dt>
                  <dd>{fmtKm2(cas.area_km2)}</dd>
                </div>
                {cas.case_id === "nepal" ? (
                  <>
                    <div>
                      <dt>Official flood in crop</dt>
                      <dd>{fmtKm2(cas.official_flood_km2_in_crop)}</dd>
                    </div>
                    <div>
                      <dt>Precision vs flood</dt>
                      <dd>
                        {cas.precision_vs_flood == null
                          ? "—"
                          : Number(cas.precision_vs_flood).toFixed(2)}
                      </dd>
                    </div>
                    {cas.recall_vs_flood != null && (
                      <div>
                        <dt>Recall vs flood</dt>
                        <dd>{Number(cas.recall_vs_flood).toFixed(2)}</dd>
                      </div>
                    )}
                  </>
                ) : cas.case_id === "latvia" ? (
                  <div>
                    <dt>Permanent water masked</dt>
                    <dd>{fmtKm2(cas.permanent_water_km2)}</dd>
                  </div>
                ) : (
                  <>
                    <div>
                      <dt>NIFC GIS area</dt>
                      <dd>{fmtKm2(cas.nifc_km2)}</dd>
                    </div>
                    <div>
                      <dt>Precision vs NIFC</dt>
                      <dd>
                        {cas.precision_vs_nifc === 1
                          ? "1.00 — no pixels outside the official line"
                          : cas.precision_vs_nifc}
                      </dd>
                    </div>
                    {cas.recall_vs_nifc != null && (
                      <div>
                        <dt>Recall vs NIFC</dt>
                        <dd>{Number(cas.recall_vs_nifc).toFixed(2)} — we under-map on purpose</dd>
                      </div>
                    )}
                    <div>
                      <dt>HVHV inside perimeter</dt>
                      <dd>{cas.inside_hv_median_db?.toFixed(2)} dB (drop)</dd>
                    </div>
                    {cas.gunw_coherence && (
                      <div>
                        <dt>GUNW coherence</dt>
                        <dd>
                          {Number(cas.gunw_coherence.inside_mean).toFixed(2)} inside vs{" "}
                          {Number(cas.gunw_coherence.outside_mean).toFixed(2)} outside
                        </dd>
                      </div>
                    )}
                  </>
                )}
                {cas.has_optical && cas.optical?.cloud_cover_pct != null && (
                  <div>
                    <dt>Optical cloud cover</dt>
                    <dd>
                      {Number(cas.optical.cloud_cover_pct).toFixed(0)}% · Sentinel-2{" "}
                      {cas.optical.datetime
                        ? String(cas.optical.datetime).slice(0, 10)
                        : cas.case_id === "snyder"
                          ? "7 Jul"
                          : ""}
                    </dd>
                  </div>
                )}
              </dl>
              <h2>Why SAR</h2>
              <p>{whySarFor(cas)}</p>
              <h2>Why we trust it</h2>
              <p>{trustFor(cas, cite)}</p>
              <h2>Source</h2>
              <p>{sourceFor(cas, cite)}</p>
              <p className="source-links">
                {cite.url && (
                  <a href={cite.url} target="_blank" rel="noreferrer">
                    {cite.event || "Event source"}
                  </a>
                )}
                {cite.hdx && (
                  <a href={cite.hdx} target="_blank" rel="noreferrer">
                    HDX EMSR927
                  </a>
                )}
                {cite.unosat_mudflow && (
                  <a href={cite.unosat_mudflow} target="_blank" rel="noreferrer">
                    UNOSAT mudflow
                  </a>
                )}
                {cite.inciweb && (
                  <a href={cite.inciweb} target="_blank" rel="noreferrer">
                    InciWeb
                  </a>
                )}
                {cite.wfigs_layer && (
                  <a href={cite.wfigs_layer} target="_blank" rel="noreferrer">
                    NIFC WFIGS
                  </a>
                )}
                {cite.ops_maps && (
                  <a href={cite.ops_maps} target="_blank" rel="noreferrer">
                    Ops maps
                  </a>
                )}
              </p>
              <p className="muted">
                Offline demo. Granules are not downloaded live.
              </p>
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
