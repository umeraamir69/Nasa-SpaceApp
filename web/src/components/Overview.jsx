import { Suspense, lazy, useState } from "react";
import { CASE_META, EVENT_INFO, METHOD, VERDICT_LABEL, fmtKm2 } from "../caseContent.js";

const Globe = lazy(() => import("./Globe.jsx"));

function keyMetric(cas) {
  if (cas.precision_vs_nifc != null) return `P ${Number(cas.precision_vs_nifc).toFixed(2)} vs NIFC`;
  if (cas.case_id === "thunderbay" && cas.precision_vs_truth != null)
    return `P ${Number(cas.precision_vs_truth).toFixed(2)} / R ${Number(cas.recall_vs_truth).toFixed(2)} vs FIRMS`;
  if (cas.precision_vs_truth != null)
    return `P ${Number(cas.precision_vs_truth).toFixed(2)} / R ${Number(cas.recall_vs_truth).toFixed(2)} vs NIFC`;
  if (cas.precision_vs_flood != null)
    return `P ${Number(cas.precision_vs_flood).toFixed(2)} / R ${Number(cas.recall_vs_flood).toFixed(2)} vs HOT`;
  if (cas.precision_vs_emsr != null)
    return `P ${Number(cas.precision_vs_emsr).toFixed(2)} / R ${Number(cas.recall_vs_emsr).toFixed(2)} vs EMSR`;
  if (cas.waterways_check) return "No river association — negative";
  if (cas.case_id === "thunderbay") return "Severe core · FIRMS scored";
  if (cas.case_id === "isaias") return "Unvalidated fringe";
  return "";
}

export default function Overview({ cases, onOpen }) {
  if (!cases) {
    return (
      <div className="overview">
        <div className="ov-grid">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="skel skel-card" />
          ))}
        </div>
      </div>
    );
  }
  const [filter, setFilter] = useState("all");
  const counts = { detected: 0, negative: 0, marginal: 0 };
  let total = 0;
  for (const c of cases) {
    const v = (CASE_META[c.case_id] || {}).verdict || "detected";
    counts[v] = (counts[v] || 0) + 1;
    total += c.area_km2 || 0;
  }
  const visible =
    filter === "all"
      ? cases
      : cases.filter((c) => ((CASE_META[c.case_id] || {}).verdict || "detected") === filter);
  return (
    <div className="overview">
      <div className="ov-head">
        <div>
          <p className="eyebrow">
            {cases.length} incidents · {cases.filter((c) => ["snyder", "thunderbay", "coleman", "secondflat"].includes(c.case_id)).length} fires ·{" "}
            {cases.filter((c) => !["snyder", "thunderbay", "coleman", "secondflat"].includes(c.case_id)).length} floods, storms & interface
          </p>
          <h1>Every case, one verdict each</h1>
        </div>
        <div className="ov-totals">
          <span className="ov-total">
            <b>{counts.detected}</b> detected
          </span>
          <span className="ov-total">
            <b>{counts.negative}</b> negative
          </span>
          <span className="ov-total">
            <b>{counts.marginal}</b> marginal
          </span>
          <span className="ov-total">
            <b>{total.toFixed(0)}</b> km² mapped
          </span>
        </div>
      </div>
      <Suspense fallback={<div className="globe-fallback">Loading 3D globe…</div>}>
        <Globe cases={visible} onOpen={onOpen} />
      </Suspense>
      <div className="ov-filters" role="tablist" aria-label="Filter cases by verdict">
        {[
          ["all", `All ${cases.length}`],
          ["detected", `Detected ${counts.detected}`],
          ["negative", `Negative ${counts.negative}`],
          ["marginal", `Marginal ${counts.marginal}`],
        ].map(([v, label]) => (
          <button
            key={v}
            type="button"
            role="tab"
            aria-selected={filter === v}
            className={filter === v ? "ov-filter on" : "ov-filter"}
            onClick={() => setFilter(v)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="ov-grid">
        {visible.map((cas) => {
          const meta = CASE_META[cas.case_id] || {};
          const verdict = meta.verdict || "detected";
          const ev = EVENT_INFO[cas.case_id];
          return (
            <button key={cas.case_id} type="button" className="ov-card" onClick={() => onOpen(cas.case_id)}>
              <div className="ov-card-top">
                <span className="ov-type">{meta.type || "Case"}</span>
                <span className={`verdict v-${verdict}`}>{VERDICT_LABEL[verdict]}</span>
              </div>
              <h2>{cas.label}</h2>
              <p className="ov-area">{fmtKm2(cas.area_km2)}</p>
              <p className="ov-dates">
                {cas.before} → {cas.after}
                {ev && (
                  <span className="ov-event">
                    {" "}· {ev.label} {ev.date}
                  </span>
                )}
              </p>
              <p className="ov-metric">{keyMetric(cas)}</p>
              {meta.verdictNote && <p className="ov-note">{meta.verdictNote}</p>}
            </button>
          );
        })}
      </div>
      <div className="ov-method">
        {METHOD.map((m) => (
          <div key={m.n} className="ov-step" title={m.d}>
            <span className="ov-step-n">{m.n}</span>
            <div>
              <b>{m.t}</b>
              <p>{m.d}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
