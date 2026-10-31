import {
  CASE_META,
  SOURCE_LINKS,
  VERDICT_LABEL,
  ledeFor,
  sourceFor,
  statsFor,
  trustFor,
  whySarFor,
} from "../caseContent.js";

export default function Brief({ cas, err }) {
  if (err) {
    return (
      <aside className="brief">
        <div className="state-card">
          <h1>Backend unreachable</h1>
          <p>API: {err}. Start the backend on :8000.</p>
          <code>venv/bin/python -m uvicorn app.main:app --port 8000</code>
        </div>
      </aside>
    );
  }
  if (!cas) {
    return (
      <aside className="brief" aria-busy="true">
        <div className="state-card loading">
          <div className="skel skel-title" />
          <div className="skel skel-line" />
          <div className="skel skel-line short" />
          <div className="skel skel-stat" />
          <p className="muted">Loading case…</p>
        </div>
      </aside>
    );
  }
  const cite = cas.citation || {};
  const meta = CASE_META[cas.case_id] || {};
  const verdict = meta.verdict || "detected";
  const rows = statsFor(cas);
  const primary = rows.find((r) => r.big);
  const rest = rows.filter((r) => !r.big);

  return (
    <aside className="brief">
      <p className="eyebrow">
        {meta.type || "Case"} · {cas.before} → {cas.after}
      </p>
      <div className="brief-head">
        <h1>{cas.label || "Incident briefing"}</h1>
        <span className={`verdict v-${verdict}`} title={meta.verdictNote || ""}>
          {VERDICT_LABEL[verdict]}
        </span>
      </div>
      {meta.verdictNote && <p className="verdict-note">{meta.verdictNote}</p>}
      <p className="lede">{ledeFor(cas)}</p>

      {primary && (
        <div className="primary-stat">
          <span className="primary-value">{primary.v}</span>
          <span className="primary-label">{primary.k}</span>
        </div>
      )}

      <dl className="stats">
        {rest.map((r) => (
          <div key={r.k} className={r.hl ? "stat-row hl" : "stat-row"}>
            <dt>{r.k}</dt>
            <dd>{r.v}</dd>
          </div>
        ))}
      </dl>

      <section>
        <h2>Why radar sees it</h2>
        <p>{whySarFor(cas)}</p>
      </section>
      <section>
        <h2>Why we trust it</h2>
        <p>{trustFor(cas, cite)}</p>
      </section>
      <section>
        <h2>Source</h2>
        <p>{sourceFor(cas, cite)}</p>
        <p className="source-links">
          {SOURCE_LINKS.filter(([key]) => cite[key]).map(([key, fallback]) => (
            <a key={key} href={cite[key]} target="_blank" rel="noreferrer">
              {key === "url" ? cite.event || "Event source" : fallback}
            </a>
          ))}
        </p>
      </section>
      <p className="muted fine">Offline: 80 m GCOV, 3×3 median despeckle, fixed dB cut. No ML, no live downloads.</p>
    </aside>
  );
}
