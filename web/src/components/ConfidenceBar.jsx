import { useEffect, useState } from "react";

export default function ConfidenceBar({ caseId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    setData(null);
    fetch(`/api/confidence?name=${caseId}`)
      .then((r) => (r.ok ? r.json() : null))
      .then(setData)
      .catch(() => setData(null));
  }, [caseId]);

  if (!data) return null;
  return (
    <div className="conf-block" aria-label="Confidence pixel breakdown">
      <div
        className="conf-bar"
        title={`${data.valid_km2} km² valid background · ${data.flagged_km2} km² flagged · ${data.total_km2} km² frame`}
      >
        {data.buckets.map((b) => (
          <span
            key={b.color + b.label}
            className="conf-seg"
            style={{ width: `${(b.share * 100).toFixed(2)}%`, background: b.color }}
            title={`${b.label}: ${b.km2} km² (${(b.share * 100).toFixed(1)}%)`}
          />
        ))}
      </div>
      <ul className="conf-legend">
        {data.buckets.map((b) => (
          <li key={b.color + b.label} title={`${b.pixels.toLocaleString()} pixels`}>
            <i className="swatch" style={{ background: b.color }} aria-hidden="true" />
            <span className="conf-label">{b.label}</span>
            <span className="conf-km2">
              {b.km2} km² · {(b.share * 100).toFixed(1)}%
            </span>
          </li>
        ))}
      </ul>
      <p className="muted fine">
        {data.valid_km2} km² valid · {data.flagged_km2} km² flagged · {data.pixel_m} m pixels
      </p>
    </div>
  );
}
