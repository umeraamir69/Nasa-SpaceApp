import { useEffect } from "react";
import { PITCH } from "../caseContent.js";

export default function PitchBar({ step, onStep, onExit }) {
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "ArrowRight" && step < PITCH.length - 1) onStep(step + 1);
      else if (e.key === "ArrowLeft" && step > 0) onStep(step - 1);
      else if (e.key === "Escape") onExit();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [step, onStep, onExit]);

  return (
    <div className="pitch-bar" role="dialog" aria-label="Guided pitch tour">
      <div className="pitch-main">
        <span className="pitch-count">
          {step + 1} / {PITCH.length}
        </span>
        <p className="pitch-caption">{PITCH[step].caption}</p>
      </div>
      <div className="pitch-controls">
        <div className="pitch-dots" aria-hidden="true">
          {PITCH.map((_, i) => (
            <button
              key={i}
              type="button"
              tabIndex={-1}
              className={i === step ? "pitch-dot on" : "pitch-dot"}
              onClick={() => onStep(i)}
              title={`Go to step ${i + 1} of ${PITCH.length}`}
            />
          ))}
        </div>
        <div className="pitch-nav">
          <button type="button" className="btn ghost" disabled={step === 0} onClick={() => onStep(step - 1)} title="Previous step (← arrow key)">
            Back
          </button>
          {step < PITCH.length - 1 ? (
            <button type="button" className="btn solid" onClick={() => onStep(step + 1)} title="Next step (→ arrow key)">
              Next
            </button>
          ) : (
            <button type="button" className="btn solid" onClick={onExit} title="End the tour and explore freely">
              Finish
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
