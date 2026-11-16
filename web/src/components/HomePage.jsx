import { CASE_META, VERDICT_MEANING } from "../caseContent.js";
import { PROJECT_LINKS } from "../team.js";

export default function HomePage({ cases, onOpen, onPitch, onAbout }) {
  const counts = { detected: 0, negative: 0, marginal: 0 };
  let total = 0;
  for (const c of cases || []) {
    const v = (CASE_META[c.case_id] || {}).verdict || "detected";
    counts[v] = (counts[v] || 0) + 1;
    total += c.area_km2 || 0;
  }
  return (
    <div className="home">
      <div className="home-hero">
        <p className="eyebrow">NASA Space Apps 2026 · Dancing with the SARs</p>
        <h1>Two radar pictures in. An incident briefing out.</h1>
        <p className="home-lede">
          EchoLens compares two NISAR satellite passes over fires, floods, and
          storms — what changed, how many square kilometres, and why you should
          believe it. Including when the honest answer is&nbsp;no.
        </p>
        <div className="home-ctas">
          <button type="button" className="btn solid big" onClick={onPitch} title="Guided 12-step tour">
            Start the pitch
          </button>
          <button type="button" className="btn ghost big" onClick={() => onOpen()} title="Open the interactive map">
            Explore the map
          </button>
        </div>
        <div className="home-stats">
          <span>
            <b>{cases ? cases.length : "–"}</b> incidents
          </span>
          <span>
            <b>{counts.detected}</b> detected
          </span>
          <span>
            <b>{counts.negative}</b> honest negatives
          </span>
          <span>
            <b>{cases ? total.toFixed(0) : "–"}</b> km² mapped
          </span>
        </div>
      </div>

      <div className="home-section">
        <h2>Every case gets a verdict</h2>
        <div className="home-verdicts">
          {VERDICT_MEANING.map((m) => (
            <div key={m.v} className="home-verdict">
              <span className={`verdict v-${m.v}`}>{m.t}</span>
              <p>{m.d}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="home-foot">
        <span>{PROJECT_LINKS.challenge}</span>
        <span className="home-links">
          <a href={PROJECT_LINKS.github} target="_blank" rel="noreferrer">
            GitHub
          </a>
          <button type="button" className="linklike" onClick={onAbout}>
            About
          </button>
        </span>
      </div>
    </div>
  );
}
