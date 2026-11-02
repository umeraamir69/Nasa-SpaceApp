# EchoLens next steps — ranked by win leverage

*Saved 30 Oct 2026. Status: all core build done; everything below is
hardening, submission, or optional depth. Check off as you go.*

## High leverage — demo & submission (do first)

- [ ] **Submission package.** Space Apps needs a project page + short demo
  video + slides. Draft page text, slide outline, video shot list; record.
  Owner: human (+ assistant drafts). Effort: ~half day.
- [ ] **Judge Q&A drill.** Out-loud pitch + hostile questions ("why only 41 of
  122 km²?", "why no AI?", "Latvia found nothing — failure?").
  Owner: human + assistant as judge. Effort: ~20 min × 2 rounds.
- [ ] **One-command demo.** `demo.sh` starting API + web + opening the browser,
  plus USB backup pack (`outputs/`, built site, deps).
  Owner: assistant. Effort: ~1 h.
- [x] **Printable briefing.** One-page print/PDF per case (map + numbers +
  verdict) — makes "a briefing out" literal; judges keep it.
  Shipped 31 Oct (print stylesheet + button).

## Medium — product depth (if days to spare)

- [ ] **Thunder Bay FIRMS overlay.** Needs free FIRMS key from human, then wire
  `--truth` overlay + precision/recall (~1 h).
- [x] **Cases-at-a-glance landing.** Now 9 verdicts/areas/dates side by side
  (Overview mode, shipped 31 Oct).
- [ ] **Screenshots/GIFs** of swipe + pitch mode for the project page.

## Done 2 Nov (see `docs/expansion.md`)

- [x] Valencia attempted → documented dead end (truth outside valid swath)
- [x] Second Flat (detected, P 0.97), Coleman Creek (fuel negative),
  Spokane/Autumn Lane (WUI negative) — all wired, 9 cases live
- [x] Otsu (IoU 0.61) + KI/split-KI (IoU 0.94) tested, recorded, not shipped
- [x] OpenCV 5.0 installed in `.conda/env`; test bounds epsilon documented

## Standing tasks (from before)

- [ ] Rotate Earthdata password (was pasted in chat).
- [ ] Commit + push regularly (working tree is the only copy until pushed).
- [ ] Cold-start drill on fresh terminals before demo day.
- [ ] Confirm weekend roles; offline copies of data/code; deps pre-installed.

## Deliberately skipped (low leverage)

Adaptive thresholds, ML comparison classifier, SMAP extras, 3D globe, mobile
app, live Earthdata on demo day. The science already exceeds demo needs —
more numbers won't convert to votes. Revisit only after everything above
is done.
