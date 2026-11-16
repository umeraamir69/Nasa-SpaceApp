import { AUTHOR, PROJECT_LINKS } from "../team.js";

function GithubIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.6 7.6 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
    </svg>
  );
}

function LinkedinIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
      <path d="M13.6 0H2.4A2.4 2.4 0 0 0 0 2.4v11.2A2.4 2.4 0 0 0 2.4 16h11.2a2.4 2.4 0 0 0 2.4-2.4V2.4A2.4 2.4 0 0 0 13.6 0ZM4.9 13.4H2.5V5.9h2.4v7.5ZM3.7 4.9a1.4 1.4 0 1 1 0-2.8 1.4 1.4 0 0 1 0 2.8Zm9.7 8.5H11V9.7c0-.9-.3-1.5-1.2-1.5-.6 0-1 .4-1.2.9-.1.1-.1.4-.1.6v3.7H6.1V5.9h2.4v1c.3-.5 1-1.3 2.3-1.3 1.7 0 2.6 1.1 2.6 3.5v4.3Z" />
    </svg>
  );
}

const STEPS = [
  { n: "1", t: "Two NISAR passes", d: "Same track, same mode. Verified pair dates per case, so change is ground change, not orbit geometry." },
  { n: "2", t: "Change map", d: "Backscatter shifts (HV for fire, HH for flood) become polygons with km² areas and before → after dates." },
  { n: "3", t: "Truth check", d: "Every outline is scored against official truth: NIFC, NIROPS, EMSR, HOT, FIRMS, Sentinel-2." },
  { n: "4", t: "Honest verdict", d: "Detected, marginal, or negative. Negatives ship with proof — dry-down, drainage, or no darkening." },
];

export default function AboutPage({ onClose, onExplore }) {
  return (
    <div className="about-page" role="main" aria-label="About EchoLens">
      <div className="about-inner">
        <p className="eyebrow">{PROJECT_LINKS.challenge}</p>
        <h1>About EchoLens</h1>
        <p className="about-lede">
          Two NISAR radar pictures in. An incident briefing out. EchoLens compares
          two satellite passes over fires, floods, and storms — what changed, how
          many square kilometres, and why you should believe the outline.
          Radar sees through cloud, smoke, and darkness.
        </p>
        <div className="about-ctas">
          <button type="button" className="btn solid big" onClick={onExplore}>
            Explore the map
          </button>
          <button type="button" className="btn ghost big" onClick={onClose}>
            Back
          </button>
        </div>

        <section aria-label="Builder">
          <h2>Solo project</h2>
          <p className="muted">One person — research, code, validation, and demo.</p>
          <div className="about-author">
            <img
              className="about-author-photo"
              src={AUTHOR.photo}
              alt={AUTHOR.name}
              width={112}
              height={112}
            />
            <div>
              <b className="about-author-name">{AUTHOR.name}</b>
              <p className="about-role">{AUTHOR.role}</p>
              {AUTHOR.location && <p className="about-loc">{AUTHOR.location}</p>}
              {AUTHOR.bio && <p className="about-bio">{AUTHOR.bio}</p>}
              <p className="author-socials">
                {AUTHOR.github && (
                  <a href={AUTHOR.github} target="_blank" rel="noreferrer" title="GitHub">
                    <GithubIcon />
                    <span>{AUTHOR.handle}</span>
                  </a>
                )}
                {AUTHOR.linkedin && (
                  <a href={AUTHOR.linkedin} target="_blank" rel="noreferrer" title="LinkedIn">
                    <LinkedinIcon />
                    <span>LinkedIn</span>
                  </a>
                )}
                {AUTHOR.website && (
                  <a href={AUTHOR.website} target="_blank" rel="noreferrer" title="Website">
                    Website
                  </a>
                )}
              </p>
            </div>
          </div>
        </section>

        <section aria-label="How it works">
          <h2>How it works</h2>
          <div className="about-steps">
            {STEPS.map((s) => (
              <div key={s.n} className="about-step">
                <span className="about-step-n">{s.n}</span>
                <div>
                  <b>{s.t}</b>
                  <p>{s.d}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section aria-label="Data and sources">
          <h2>Data &amp; sources</h2>
          <p className="muted">
            NISAR L2 GCOV (NASA/JPL + ISRO, via ASF DAAC) · NIFC WFIGS perimeters ·
            NIROPS airborne infrared · Copernicus Emergency Mapping · HOT
            OpenStreetMap · Sentinel-2 optical · NASA FIRMS
          </p>
        </section>

        <section aria-label="Project links">
          <h2>Project</h2>
          <p className="source-links">
            <a href={PROJECT_LINKS.live} target="_blank" rel="noreferrer">
              Live demo
            </a>
            {" · "}
            <a href={PROJECT_LINKS.github} target="_blank" rel="noreferrer">
              GitHub
            </a>
          </p>
        </section>
      </div>
    </div>
  );
}
