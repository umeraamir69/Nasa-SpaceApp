import { useEffect, useState } from "react";

function boundsOf(geom) {
  let polys = [];
  if (!geom) return null;
  if (geom.type === "Polygon") polys = [geom.coordinates];
  else if (geom.type === "MultiPolygon") polys = geom.coordinates;
  else return null;
  let s = 90, w = 180, n = -90, e = -180;
  for (const poly of polys)
    for (const ring of poly)
      for (const [x, y] of ring) {
        if (y < s) s = y;
        if (y > n) n = y;
        if (x < w) w = x;
        if (x > e) e = x;
      }
  if (s > n || w > e) return null;
  return { south: s, west: w, north: n, east: e };
}

export default function Fragments({ caseId, onZoom }) {
  const [frags, setFrags] = useState(null);

  useEffect(() => {
    setFrags(null);
    fetch(`/api/geojson/change?name=${caseId}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((fc) => {
        if (!fc) {
          setFrags([]);
          return;
        }
        const rows = (fc.features || [])
          .map((f) => ({
            part: f.properties?.part || "?",
            area: f.properties?.area_km2 ?? 0,
            bounds: boundsOf(f.geometry),
          }))
          .sort((a, b) => b.area - a.area);
        setFrags(rows);
      })
      .catch(() => setFrags([]));
  }, [caseId]);

  if (frags === null || frags.length === 0) return null;
  return (
    <section aria-label="Change fragments">
      <h2>
        Fragments <span className="frag-count">{frags.length}</span>
      </h2>
      <p className="muted fine">Sorted largest first — click a row to zoom.</p>
      <ol className="frag-list">
        {frags.map((f) => (
          <li key={f.part}>
            <button
              type="button"
              className="frag-row"
              disabled={!f.bounds}
              onClick={() => f.bounds && onZoom(f.bounds)}
              title={f.bounds ? `Zoom to fragment ${f.part}` : "No geometry"}
            >
              <span className="frag-part">{f.part}</span>
              <span className="frag-area">{Number(f.area).toFixed(2)} km²</span>
            </button>
          </li>
        ))}
      </ol>
    </section>
  );
}
