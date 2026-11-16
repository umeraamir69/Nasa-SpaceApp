import { useEffect } from "react";
import { AUTHOR, PROJECT_LINKS } from "../team.js";

function GithubIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.6 7.6 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
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
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-label="About EchoLens"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-head">
          <h2>About EchoLens</h2>
          <button type="button" className="btn ghost" onClick={onClose}>
            Close
          </button>
        </div>
        <p className="lede">
          Two NISAR radar passes in, an incident briefing out — built for NASA Space Apps
          2026, Dancing with the SARs.
        </p>
        <h3>Solo project</h3>
        <div className="about-author">
          <img className="about-author-photo" src={AUTHOR.photo} alt={AUTHOR.name} width={96} height={96} />
          <div>
            <b>{AUTHOR.name}</b>
            <p className="about-role">{AUTHOR.role}</p>
            <p className="author-socials">
              <a href={PROJECT_LINKS.live} target="_blank" rel="noreferrer">
                {PROJECT_LINKS.live.replace(/^https:\/\//, "")}
              </a>
              {AUTHOR.github && (
                <a href={AUTHOR.github} target="_blank" rel="noreferrer" title="GitHub">
                  <GithubIcon />
                </a>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
