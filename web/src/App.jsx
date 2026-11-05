import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import { PITCH } from "./caseContent.js";
import TopBar from "./components/TopBar.jsx";
import Dock from "./components/Dock.jsx";
import Brief from "./components/Brief.jsx";
import PitchBar from "./components/PitchBar.jsx";
import Overview from "./components/Overview.jsx";
import HomePage from "./components/HomePage.jsx";
import AboutModal from "./components/AboutModal.jsx";
import "./App.css";

const ALL_IDS = ["snyder", "thunderbay", "nepal", "latvia", "crete", "isaias", "coleman", "secondflat", "spokane"];

const OVERLAY_KEYS = ["change", "perim", "ir", "lakes", "emsr", "flood", "rivers", "firms"];
const ALL_ON = Object.fromEntries(OVERLAY_KEYS.map((k) => [k, true]));

const MEDIA_PREFIX = {
  latvia: "/media-latvia",
  nepal: "/media-nepal",
  thunderbay: "/media-thunderbay",
  crete: "/media-crete",
  isaias: "/media-isaias",
  coleman: "/media-coleman",
  secondflat: "/media-secondflat",
  spokane: "/media-spokane",
};

function layerUrl(cas, rasterId) {
  const hit = cas?.layers?.find((l) => l.id === rasterId);
  if (hit?.url) return hit.url;
  const prefix = MEDIA_PREFIX[cas?.case_id] || "/media";
  return `${prefix}/layers/${rasterId}.png`;
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
  const [overlays, setOverlays] = useState(ALL_ON);
  const [swipePos, setSwipePos] = useState(50);
  const [pitch, setPitch] = useState(null);
  const [overview, setOverview] = useState(false);
  const [home, setHome] = useState(true);
  const [about, setAbout] = useState(false);
  const [allCases, setAllCases] = useState(null);
  const [showAll, setShowAll] = useState(false);
  const showRef = useRef(ALL_ON);
  showRef.current = overlays;

  useEffect(() => {
    fetch("/api/cases")
      .then((r) => r.json())
      .then((d) => setAvailable(d.cases || []))
      .catch(() => setAvailable([]));
  }, []);

  useEffect(() => {
    setShowAll(false);
  }, [caseId]);

  useEffect(() => {
    const map = mapRef.current;
    const store = layersRef.current;
    if (!map) {
      store.allCases = null;
      return;
    }
    if (store.allCases) {
      map.removeLayer(store.allCases);
      store.allCases = null;
    }
    if (!showAll) return;
    let cancelled = false;
    Promise.all(
      ALL_IDS.map((id) =>
        fetch(`/api/geojson/change?name=${id}`).then((r) => r.json()),
      ),
    ).then((fcs) => {
      if (cancelled || mapRef.current !== map) return;
      const group = L.geoJSON(fcs.flatMap((fc) => fc.features || []), {
        style: { color: "#e4572e", weight: 1, fillColor: "#c1121f", fillOpacity: 0.35 },
      });
      store.allCases = group;
      group.addTo(map);
      const b = group.getBounds();
      if (b.isValid()) map.fitBounds(b, { padding: [30, 30] });
    });
    return () => {
      cancelled = true;
    };
  }, [showAll]);

  useEffect(() => {
    Promise.all(
      ALL_IDS.map((id) => fetch(`/api/case?name=${id}`).then((r) => r.json())),
    )
      .then((all) => setAllCases(all.filter((c) => c && c.case_id)))
      .catch(() => setAllCases([]));
  }, []);

  useEffect(() => {
    setCas(null);
    setErr(null);
    setRaster("change");
    setOverlays(ALL_ON);
    setSwipePos(50);
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
    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
      attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors &copy; <a href=\"https://www.esri.com/\">Esri</a>",
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
      cas.has_rivers
        ? fetch(`/api/geojson/overlay?name=${cid}&layer=rivers`).then((r) => r.json())
        : Promise.resolve(null),
      cas.has_firms
        ? fetch(`/api/geojson/overlay?name=${cid}&layer=firms`).then((r) => r.json())
        : Promise.resolve(null),
    ]).then(([change, perim, ir, lakes, emsr, flood, rivers, firms]) => {
      const show = showRef.current;
      const changeLayer = L.geoJSON(change, {
        style: {
          color: "#e4572e",
          weight: 1,
          fillColor: "#c1121f",
          fillOpacity: 0.35,
        },
        onEachFeature: (feat, layer) => {
          const p = feat?.properties || {};
          const part = p.part ? `Fragment ${p.part}` : "EchoLens change";
          const area = p.area_km2 != null ? `<br/>${Number(p.area_km2).toFixed(2)} km²` : "";
          layer.bindPopup(`<b>${part}</b>${area}<br/><span class="pop-dates">${cas.before} → ${cas.after}</span>`);
          layer.bindTooltip(`${part}${p.area_km2 != null ? ` · ${Number(p.area_km2).toFixed(2)} km²` : ""}`, { sticky: true });
        },
      });
      const perimLayer = L.geoJSON(perim, {
        style: {
          color: "#f0b429",
          weight: 2,
          fill: false,
        },
      });
      layersRef.current.changePoly = changeLayer;
      layersRef.current.perim = perimLayer;
      if (show.perim) perimLayer.addTo(map);
      if (show.change) changeLayer.addTo(map);
      if (ir) {
        const irLayer = L.geoJSON(ir, {
          style: (feat) => {
            const k = feat?.properties?.kind;
            if (k === "heat_perimeter") return { color: "#ff6b35", weight: 2, fill: false };
            if (k === "scattered_heat") {
              return { color: "#ffd166", weight: 1, fillColor: "#ffd166", fillOpacity: 0.4 };
            }
            return { color: "#e4572e", weight: 1, fill: false };
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
        if (show.ir) irLayer.addTo(map);
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
        if (show.lakes) lakeLayer.addTo(map);
      }
      if (emsr) {
        const emsrLayer = L.geoJSON(emsr, {
          style: {
            color: "#f0b429",
            weight: 2,
            fillColor: "#f0b429",
            fillOpacity: 0.18,
          },
        });
        layersRef.current.emsr = emsrLayer;
        if (show.emsr) emsrLayer.addTo(map);
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
        if (show.flood) floodLayer.addTo(map);
      }
      if (rivers) {
        const riverLayer = L.geoJSON(rivers, {
          style: {
            color: "#48cae4",
            weight: 1,
            opacity: 0.8,
          },
        });
        layersRef.current.rivers = riverLayer;
        if (show.rivers) riverLayer.addTo(map);
      }
      if (firms) {
        const firmsLayer = L.geoJSON(firms, {
          pointToLayer: (_feat, latlng) =>
            L.circleMarker(latlng, {
              radius: 3,
              color: "#ff9e00",
              fillColor: "#ff9e00",
              fillOpacity: 0.85,
              weight: 0,
            }),
          onEachFeature: (feat, layer) => {
            const p = feat?.properties || {};
            layer.bindPopup(
              `<b>FIRMS hotspot</b><br/>${p.acq_date || ""} ${p.acq_time || ""}<br/>${p.satellite || ""} · ${p.confidence || ""} · FRP ${p.frp || "—"}`
            );
          },
        });
        layersRef.current.firms = firmsLayer;
        if (show.firms) firmsLayer.addTo(map);
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
    for (const key of ["raster", "swipeTop", "swipeBottom"]) {
      if (store[key]) {
        map.removeLayer(store[key]);
        store[key] = null;
      }
    }
    const b = cas.bounds;
    const bounds = [
      [b.south, b.west],
      [b.north, b.east],
    ];
    if (raster === "swipe") {
      const bottom = L.imageOverlay(layerUrl(cas, "after"), bounds, {
        opacity: 0.88,
        pane: "rasterPane",
      });
      const top = L.imageOverlay(layerUrl(cas, "before"), bounds, {
        opacity: 0.88,
        pane: "rasterPane",
      });
      bottom.addTo(map);
      top.addTo(map);
      store.swipeBottom = bottom;
      store.swipeTop = top;
    } else {
      const img = L.imageOverlay(layerUrl(cas, raster), bounds, {
        opacity: 0.88,
        pane: "rasterPane",
      });
      img.addTo(map);
      store.raster = img;
    }
  }, [raster, cas]);

  useEffect(() => {
    const top = layersRef.current.swipeTop;
    const el = top?.getElement?.();
    if (el) el.style.clipPath = `inset(0 ${100 - swipePos}% 0 0)`;
  }, [swipePos, raster, cas]);

  useEffect(() => {
    if (pitch == null) return;
    const step = PITCH[pitch];
    if (step.caseId !== caseId) setCaseId(step.caseId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pitch]);

  useEffect(() => {
    if (pitch == null || !cas) return;
    const step = PITCH[pitch];
    if (cas.case_id === step.caseId && raster !== step.raster) setRaster(step.raster);
  }, [pitch, cas, caseId, raster]);

  useEffect(() => {
    const map = mapRef.current;
    const store = layersRef.current;
    if (!map) return;
    const pairs = [
      ["change", "changePoly"],
      ["perim", "perim"],
      ["ir", "ir"],
      ["lakes", "lakes"],
      ["emsr", "emsr"],
      ["flood", "flood"],
      ["rivers", "rivers"],
      ["firms", "firms"],
    ];
    for (const [key, ref] of pairs) {
      const layer = store[ref];
      if (!layer) continue;
      if (overlays[key]) layer.addTo(map);
      else map.removeLayer(layer);
    }
  }, [overlays]);

  const onRaster = (id) => {
    setRaster(id);
    // Polygons hide on Before/After/Optical so the raster is the beat.
    setOverlays((o) => ({ ...o, change: id === "change" }));
  };
  const onOverlay = (key) => setOverlays((o) => ({ ...o, [key]: !o[key] }));

  return (
    <div className="shell">
      <TopBar
        available={available}
        caseId={caseId}
        onCase={(id) => {
          setPitch(null);
          setOverview(false);
          setHome(false);
          setCaseId(id);
        }}
        onPitch={() => {
          setOverview(false);
          setHome(false);
          setPitch((p) => (p == null ? 0 : null));
        }}
        pitching={pitch != null}
        overview={overview}
        onOverview={() => {
          setPitch(null);
          setHome(false);
          setOverview((v) => !v);
        }}
        onHome={() => {
          setPitch(null);
          setOverview(false);
          setHome(true);
        }}
        onAbout={() => setAbout(true)}
      />
      <div className="stage">
        <div className="body">
          <div className="map-wrap">
            <div ref={mapEl} className="map" />
            {cas && (
              <Dock
                cas={cas}
                raster={raster}
                onRaster={onRaster}
                overlays={overlays}
                onOverlay={onOverlay}
                swipePos={swipePos}
                onSwipe={setSwipePos}
                showAll={showAll}
                onShowAll={() => setShowAll((v) => !v)}
              />
            )}
            {pitch != null && <PitchBar step={pitch} onStep={setPitch} onExit={() => setPitch(null)} />}
          </div>
          <Brief cas={cas} err={err} />
        </div>
        {overview && (
          <Overview
            cases={allCases}
            onOpen={(id) => {
              setOverview(false);
              setCaseId(id);
            }}
          />
        )}
        {home && (
          <HomePage
            cases={allCases}
            onOpen={(id) => {
              setHome(false);
              if (id) setCaseId(id);
            }}
            onPitch={() => {
              setHome(false);
              setPitch(0);
            }}
            onAbout={() => setAbout(true)}
          />
        )}
      </div>
      {about && <AboutModal onClose={() => setAbout(false)} />}
    </div>
  );
}
