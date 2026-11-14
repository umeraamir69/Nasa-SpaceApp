import { CASE_META } from "../caseContent.js";

function Mark() {
  return (
    <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">
      <circle cx="13" cy="13" r="11.5" fill="none" stroke="#3a4149" strokeWidth="1.5" />
      <circle cx="13" cy="13" r="6.5" fill="none" stroke="#3a4149" strokeWidth="1" />
      <path d="M13 13 L13 2.5 A10.5 10.5 0 0 1 23.5 13 Z" fill="#f0b429" opacity="0.85" />
      <circle cx="13" cy="13" r="1.8" fill="#f0b429" />
      <circle cx="17.5" cy="9.5" r="1.4" fill="#e4572e" />
    </svg>
  );
}

export default function TopBar({ available, caseId, onCase, onPitch, pitching, overview, onOverview, onHome, onAbout }) {
  const ready = available.filter((c) => c.ready);
  return (
    <header className="topbar">
      <button type="button" className="brand brand-btn" onClick={onHome} title="Back to home">
        <Mark />
        <span className="brand-text">
          <span className="brand-name">EchoLens</span>
          <span className="brand-sub">NISAR surface change · Dancing with the SARs</span>
        </span>
      </button>
      {ready.length > 1 && (
        <nav className="case-nav" aria-label="Cases">
          {ready.map((c, i) => {
            const meta = CASE_META[c.id] || {};
            return (
              <button
                key={c.id}
                type="button"
                className={caseId === c.id ? "case-tab on" : "case-tab"}
                onClick={() => onCase(c.id)}
                aria-current={caseId === c.id ? "true" : undefined}
                title={`${meta.verdictNote || c.label} (key ${i + 1})`}
              >
                <i className={`dot v-${meta.verdict || "detected"}`} aria-hidden="true" />
                {c.label}
              </button>
            );
          })}
        </nav>
      )}
      <div className="top-actions">
        <span className="offline-note" title="All radar products are precomputed — no live satellite downloads during the demo">Offline demo</span>
        <button
          type="button"
          className={overview ? "pitch-btn on" : "pitch-btn"}
          onClick={onOverview}
          title="Compare all cases side by side"
        >
          {overview ? "Map" : "Overview"}
        </button>
        <button
          type="button"
          className="pitch-btn ghost-btn"
          onClick={onAbout}
          title="About EchoLens and the team"
        >
          About
        </button>
        <button
          type="button"
          className={pitching ? "pitch-btn on" : "pitch-btn"}
          onClick={onPitch}
          title="Guided pitch tour (8 steps)"
        >
          {pitching ? "Exit pitch" : "Pitch"}
        </button>
      </div>
    </header>
  );
}
