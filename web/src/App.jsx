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
  if (caseId === "latvia") {
    switch (raster) {
      case "before":
      case "after":
        return "HHHH backscatter · dark = water";
      case "change":
        return "Blue: darker after (new water) · red: brighter";
      case "confidence":
        return "Grey: valid · steel: lakes · cyan: new water";
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

    Promise.all([
      fetch(`/api/geojson/change?name=${cas.case_id || "snyder"}`).then((r) => r.json()),
      fetch(`/api/geojson/perimeter?name=${cas.case_id || "snyder"}`).then((r) => r.json()),
    ]).then(([change, perim]) => {
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
      const perimBounds = perimLayer.getBounds();
      if (perimBounds.isValid()) {
        map.fitBounds(perimBounds, { padding: [28, 28] });
      } else if (imageBounds) {
        map.fitBounds(imageBounds, { padding: [28, 28] });
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
            </div>
            <div className="legend">
              <div>{legendFor(raster, cas?.case_id)}</div>
              <div className="legend-keys">
                {cas?.has_perimeter && (
                  <span>
                    <i className="swatch nifc" /> NIFC
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
              <p className="lede">
                {cas.case_id === "latvia"
                  ? "Two NISAR L-band passes around the Latvia–Lithuania floods (EMSR926). Peak rain was ~21–22 Aug; this pair is 18 Aug → 30 Aug, so the map is leftover new water, not the crest. Permanent lakes are masked."
                  : "Two NISAR L-band passes around the Snyder Fire. The map is not a photo — it is radar backscatter change, checked against an official perimeter."}
              </p>
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
                {cas.case_id === "latvia" ? (
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
                    <div>
                      <dt>HVHV inside perimeter</dt>
                      <dd>{cas.inside_hv_median_db?.toFixed(2)} dB (drop)</dd>
                    </div>
                  </>
                )}
                {cas.has_optical && cas.optical?.cloud_cover_pct != null && (
                  <div>
                    <dt>Optical cloud cover</dt>
                    <dd>{Number(cas.optical.cloud_cover_pct).toFixed(0)}% · Sentinel-2 7 Jul</dd>
                  </div>
                )}
              </dl>
              <h2>Why SAR</h2>
              <p>
                {cas.case_id === "latvia"
                  ? "Cloud and rain hide optical. L-band still sees new water as a dark HH return. Lakes that were dark on both dates are not flood."
                  : cas.has_optical
                    ? "Click Optical: Sentinel-2 on 7 Jul (during the fire) is white cloud over this box. Radar still returns a scar. That is the point of NISAR."
                    : "Optical would be smoke and cloud. Radar still returns a scar. Run python scripts/fetch_optical.py to load the 7 Jul Sentinel-2 scene."}
              </p>
              <h2>Why we trust it</h2>
              <p>
                {cas.case_id === "latvia"
                  ? "Valid GCOV pixels, 3×3 median despeckle, HH log-ratio ≥ 2 dB darker after, and the after pixel looks like water. Permanent water (dark on both dates) is not flagged. Copernicus EMSR926 is the named event; official flood vectors were not in HDX yet."
                  : `Valid GCOV pixels only, 3×3 median despeckle, HVHV log-ratio ≥ 1.5 dB darker after the fire. Every flagged pixel sits inside NIFC WFIGS ${cite.unique_fire_identifier || ""}. GUNW HH coherence barely drops on this arid mesa (0.73 vs 0.76) — so detection stays on GCOV, not a fake second layer.`}
              </p>
              <h2>Source</h2>
              <p>
                {cas.case_id === "latvia"
                  ? "Copernicus EMS Rapid Mapping EMSR926. Pitch still opens on Snyder."
                  : `Perimeter: ${cite.polygon || ""}${cite.unique_fire_identifier ? ` · ${cite.unique_fire_identifier}` : ""}. FIRMS is hotspots, not this outline.`}
              </p>
              <p className="source-links">
                {cite.url && (
                  <a href={cite.url} target="_blank" rel="noreferrer">
                    {cite.event || "Event source"}
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
