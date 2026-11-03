import { useEffect } from "react";
import { PROJECT_LINKS, TEAM } from "../team.js";

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

function InstagramIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      <rect x="1" y="1" width="14" height="14" rx="4" />
      <circle cx="8" cy="8" r="3.2" />
      <circle cx="12" cy="4" r="1.1" fill="currentColor" stroke="none" />
    </svg>
  );
}

export default function AboutModal({ onClose }) {
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal"
        role="dialog"
        aria-label="About EchoLens"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-head">
          <h2>About EchoLens</h2>
          <button type="button" className="btn ghost" onClick={onClose} title="Close (Esc)">
            Close
          </button>
        </div>
        <p className="lede">
          EchoLens turns two NISAR radar passes into an incident briefing: what
          changed on the ground, how many square kilometres, and why you should
          believe the outline. Built for {PROJECT_LINKS.challenge}.
        </p>
        <p className="muted">
          Radar sees through cloud, smoke, and darkness. Every case is scored
          against official truth — fire perimeters, flood polygons, aircraft
          heat maps — and cases where the honest answer is “no” are published
          with their proof, not hidden.
        </p>
        <h3>Data & sources</h3>
        <p className="muted">
          NISAR L2 GCOV (NASA/JPL + ISRO, via ASF DAAC) · NIFC WFIGS perimeters ·
          NIROPS airborne infrared · Copernicus Emergency Mapping · HOT
          OpenStreetMap · Sentinel-2 optical · NASA FIRMS
        </p>
        <h3>The team</h3>
        <div className="team-grid">
          {TEAM.map((m) => (
            <div key={m.name} className="team-card">
              <span className="team-avatar" aria-hidden="true">
                {m.name.slice(0, 1).toUpperCase()}
              </span>
              <div>
                <b>{m.name}</b>
                <p>{m.role}</p>
                <p className="team-socials">
                  {m.github && (
                    <a href={m.github} target="_blank" rel="noreferrer" title="GitHub">
                      <GithubIcon />
                    </a>
                  )}
                  {m.linkedin && (
                    <a href={m.linkedin} target="_blank" rel="noreferrer" title="LinkedIn">
                      <LinkedinIcon />
                    </a>
                  )}
                  {m.instagram && (
                    <a href={m.instagram} target="_blank" rel="noreferrer" title="Instagram">
                      <InstagramIcon />
                    </a>
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
        <p className="source-links">
          <a href={PROJECT_LINKS.github} target="_blank" rel="noreferrer">
            Project on GitHub
          </a>
        </p>
      </div>
    </div>
  );
}
