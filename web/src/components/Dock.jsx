import { LAYER_TIPS, OVERLAY_TIPS, RASTERS, legendFor } from "../caseContent.js";

export default function Dock({
  cas,
  raster,
  onRaster,
  overlays,
  onOverlay,
  swipePos,
  onSwipe,
}) {
  const layers = RASTERS.filter((r) => r.id !== "optical" || cas?.has_optical);
  const toggles = [
    { key: "change", label: "EchoLens change", flag: true, dot: "echo" },
    { key: "perim", label: cas?.case_id === "snyder" ? "NIFC perimeter" : "Official perimeter", flag: cas?.has_perimeter, dot: "nifc" },
    { key: "ir", label: "NIROPS IR", flag: cas?.has_ir, dot: "ir" },
    { key: "lakes", label: "Permanent lakes", flag: cas?.has_lakes, dot: "lakes" },
    { key: "emsr", label: cas?.case_id === "crete" ? "EMSR933" : "EMSR927", flag: cas?.has_emsr, dot: "nifc" },
    { key: "flood", label: "Official flood", flag: cas?.has_flood_extent, dot: "flood" },
    { key: "rivers", label: "Rivers (OSM)", flag: cas?.has_rivers, dot: "rivers" },
  ].filter((t) => t.flag);

  return (
    <div className="dock" role="toolbar" aria-label="Map layers">
      <div className="dock-group">
        <span className="dock-label">Layer</span>
        <div className="seg" role="tablist" aria-label="Raster layer">
          {layers.map((r) => (
            <button
              key={r.id}
              type="button"
              role="tab"
              aria-selected={raster === r.id}
              className={raster === r.id ? "seg-btn on" : "seg-btn"}
              onClick={() => onRaster(r.id)}
              title={LAYER_TIPS[r.id] || r.label}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>
      {raster === "swipe" && cas && (
        <div className="swipe-bar">
          <span className="swipe-date">{cas.before}</span>
          <input
            type="range"
            min={0}
            max={100}
            value={swipePos}
            onChange={(e) => onSwipe(Number(e.target.value))}
            aria-label="Before-after swipe position"
          />
          <span className="swipe-date">{cas.after}</span>
        </div>
      )}
      <div className="dock-group">
        <span className="dock-label">Overlays</span>
        <div className="toggles">
          {toggles.map((t) => (
            <button
              key={t.key}
              type="button"
              aria-pressed={!!overlays[t.key]}
              className={overlays[t.key] ? "toggle on" : "toggle"}
              onClick={() => onOverlay(t.key)}
              title={OVERLAY_TIPS[t.key] || t.label}
            >
              <i className={`swatch ${t.dot}`} aria-hidden="true" />
              {t.label}
            </button>
          ))}
        </div>
      </div>
      <p className="dock-legend">{legendFor(raster, cas?.case_id)}</p>
    </div>
  );
}
