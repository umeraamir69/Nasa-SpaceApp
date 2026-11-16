# EchoLens — complete demo video (tool guide)

Goal: a **full narrated walkthrough** of https://echolens-theta.vercel.app  
(plus a **≤30 s** cut for Space Apps submission — see `docs/submission.md`).

Script source of truth: `docs/pitch.md` (30 s + 3 min).

Topics checked: [video-generation](https://github.com/topics/video-generation), [product-demo](https://github.com/topics/product-demo).

---

## What “complete” means for EchoLens

| Length | Use | Content |
|---|---|---|
| **~30 s** | Space Apps required demo | Hook → Snyder change inside NIFC → cloudy optical → “nine cases / honest negatives” |
| **~2–3 min** | Complete project video | Globe → Snyder layers → Nepal or Second Flat → Coleman negative → About / live URL |
| **Optional 15–45 s vertical** | Social / Shorts | Same story, cropped |

Record against the **live** site (or `./demo.sh`) so pins and briefing numbers match production.

---

## Best fit (ranked for you)

### 1) Fastest polished result — SaaS (paid, least setup)

Paste the live URL, get voice + zooms + captions.

| Tool | Why | Link |
|---|---|---|
| **[Demosmith](https://demosmith.ai)** | Agent walks the URL, returns narrated MP4 (+ interactive demo). Trial available. | demosmith.ai |
| **[Clueso](https://www.clueso.io)** | You record once → AI rewrites script, voice, captions, zooms | clueso.io |
| **[Trupeer](https://www.trupeer.ai)** | Browser recording → voiced MP4 + written guide | trupeer.ai |
| **[Voom](https://madewithvoom.com)** | Short “product film” from link/screenshots (good for 30 s) | madewithvoom.com |

**Screen Studio** (Mac) looks great (auto-zoom) but has **no AI voice** — pair with ElevenLabs / Descript if you use it.

### 2) Best open-source for a *real browser* demo + AI voice

These drive Chromium (Playwright), sync TTS to clicks, export MP4.

| Repo | Stars / vibe | Voice | Best for EchoLens |
|---|---|---|---|
| **[shreyaskarnik/argo](https://github.com/shreyaskarnik/argo)** | Strong, mature CLI | **Kokoro local (free)** or ElevenLabs / OpenAI | **Top pick** — write Playwright scenes for globe → Snyder → Optical → Pitch |
| **[tandryukha/aidemo](https://github.com/tandryukha/aidemo)** | Agent writes `storyboard.json`; CI re-render | OpenAI / ElevenLabs / local | Good if you want Cursor/Claude to author the flow |
| **[gabosarmiento/demotape](https://github.com/gabosarmiento/demotape)** | macOS agentic recorder + captions + TTS | Local or hosted | Great if you want *me* / an agent to drive the Mac |
| **[NEURASCOPE/neurascreen](https://github.com/NEURASCOPE/neurascreen)** | JSON scenario → Playwright → TTS → MP4 | OpenAI / ElevenLabs / Coqui… | Simple JSON scripting |
| **[ldmallari/scenecast](https://github.com/ldmallari/scenecast)** | YAML scenes + local Kokoro + audit | Local free | Strict sync checks |
| **[ShowDemoProject/showdemo](https://github.com/ShowDemoProject/showdemo)** | URL/GitHub → Gemini script → Remotion | ElevenLabs | “Paste URL” style, more cloud deps |
| **[andrewluxem/ultrademo](https://github.com/andrewluxem/ultrademo)** | Playwright → TTS → Remotion | ElevenLabs / Piper | Agent skill + local render |
| **[mrieck/demoday-claude-plugin](https://github.com/mrieck/demoday-claude-plugin)** | Claude plugin, Remotion edit | ElevenLabs | If you live in Claude Code on macOS |

### 3) Voice-only stack (if you already record the screen)

| Piece | Role |
|---|---|
| **[ElevenLabs](https://elevenlabs.io)** | Best hosted voice quality (paid) |
| **[Kokoro TTS](https://github.com/hexgrad/kokoro)** / mlx-audio | Free local voice (used by Argo / Scenecast) |
| **OpenAI TTS** (`tts-1-hd`) | Simple API, good quality |
| **[Descript](https://www.descript.com)** | Edit video by editing the transcript; Overdub voices |
| **Whisper / faster-whisper** | Captions / word timestamps |

### 4) Composition frameworks (more DIY)

| Tool | Notes |
|---|---|
| **[Remotion](https://www.remotion.dev)** | React → video; free for individuals (company license above headcount) |
| **ffmpeg** | Always needed under the hood for mux/trim |

Pure “text → cinematic AI video” models (Runway, Kling, Veo, Luma) are **weak** for a real product UI — prefer browser capture + TTS for EchoLens.

---

## Recommended plan for EchoLens (practical)

### Path A — tonight, minimal friction

1. Open https://echolens-theta.vercel.app  
2. Sign up **Demosmith** trial *or* record with **Clueso / Trupeer**  
3. Prompt / script from `docs/pitch.md` 30 s + extend to 2–3 min  
4. Export 1080p MP4 → upload unlisted YouTube → paste into Space Apps  

### Path B — free / local, high control (best OSS)

1. `brew install ffmpeg`  
2. Use **Argo** (or NeuraScreen) against `https://echolens-theta.vercel.app`  
3. Scenes (example):

```text
1. Overview globe — “Two radar passes in…”
2. Click Snyder — Change + NIFC on
3. Before → After → Change
4. Optical — cloudy why-SAR
5. Overview filter Negative — Coleman honesty
6. Close on live URL
```

4. Voice with **Kokoro** (free) or **ElevenLabs** (prettier)  
5. Burn captions; export MP4  

### Path C — agent-made on your Mac

Use **DemoTape** or **aidemo** / **DemoDay**: point the agent at this repo + live URL, hand it `docs/pitch.md`, ask for a 2–3 min verified demo MP4.

---

## Shot list (complete ~2:30 video)

| Time | On screen | Narration cue |
|---|---|---|
| 0:00–0:15 | Globe overview | Hook: smoke vs L-band; EchoLens briefing |
| 0:15–0:45 | Snyder Change + NIFC | Exam with answer key; 40.9 km²; P 1.00 |
| 0:45–1:10 | Before → After → Change | Same track, log-ratio |
| 1:10–1:25 | Optical | 34% cloud — why SAR |
| 1:25–1:50 | Nepal or Second Flat | Method reuses; precision headline |
| 1:50–2:10 | Coleman / Latvia | Honest negative |
| 2:10–2:30 | About + URL | Solo build; echolens-theta.vercel.app |

Cut 0:00–0:30 for the official Space Apps slot.

---

## Disclose SI / AI (Space Apps)

If the voice or editing is AI-generated, say so on the project page (see `docs/submission.md` SI section). Map layers themselves are real NISAR / truth data — not AI imagery.

---

## Links from the topic pages

- https://github.com/topics/video-generation  
- https://github.com/topics/product-demo  

**Start here tonight:** Demosmith trial on the live URL, **or** Argo + Kokoro for a free local render.

---

## Built-in recorder (this repo)

A Playwright + macOS `say` + ffmpeg pipeline already produced:

| File | Length | Path |
|---|---|---|
| Full demo | ~86 s | [`docs/assets/echolens-demo.mp4`](assets/echolens-demo.mp4) |
| Space Apps cut | 30 s | [`docs/assets/echolens-demo-30s.mp4`](assets/echolens-demo-30s.mp4) |

Rebuild:

```bash
cd scripts/demo-video
npm install
npx playwright install chromium   # once
npm run make                      # needs macOS + Chrome; records live site
```

Env overrides: `DEMO_URL=…` `DEMO_VOICE='Flo (English (US))'`
