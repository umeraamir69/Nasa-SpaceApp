#!/usr/bin/env node
/**
 * EchoLens demo video builder
 * 1) macOS `say` TTS per scene
 * 2) Playwright (Chrome) records the live site timed to narration
 * 3) ffmpeg muxes → out/echolens-demo.mp4 (+ 30s cut)
 */
import { chromium } from "playwright";
import { execFileSync, spawnSync } from "node:child_process";
import {
  mkdirSync,
  readFileSync,
  writeFileSync,
  existsSync,
  rmSync,
  copyFileSync,
} from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = join(__dirname, "out");
const VOICE = process.env.DEMO_VOICE || "Flo (English (US))";
const URL = process.env.DEMO_URL || "https://echolens-theta.vercel.app";
const scenes = JSON.parse(readFileSync(join(__dirname, "narration.json"), "utf8"));

mkdirSync(OUT, { recursive: true });
mkdirSync(join(OUT, "clips"), { recursive: true });
mkdirSync(join(OUT, "audio"), { recursive: true });

function sh(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, { encoding: "utf8", ...opts });
  if (r.status !== 0) {
    throw new Error(`${cmd} ${args.join(" ")}\n${r.stderr || r.stdout}`);
  }
  return r;
}

function durationSec(path) {
  const r = sh("ffprobe", [
    "-v",
    "error",
    "-show_entries",
    "format=duration",
    "-of",
    "default=noprint_wrappers=1:nokey=1",
    path,
  ]);
  return Math.max(0.5, parseFloat(String(r.stdout).trim()));
}

console.log(`Voice: ${VOICE}`);
console.log(`URL:   ${URL}`);

// --- TTS ---
const audioFiles = [];
for (const s of scenes) {
  const aiff = join(OUT, "audio", `${s.id}.aiff`);
  const wav = join(OUT, "audio", `${s.id}.wav`);
  console.log(`TTS ${s.id}…`);
  sh("say", ["-v", VOICE, "-o", aiff, s.text]);
  sh("ffmpeg", ["-y", "-i", aiff, "-ar", "44100", "-ac", "1", wav], {
    stdio: "ignore",
  });
  const dur = durationSec(wav);
  audioFiles.push({ ...s, wav, dur });
  console.log(`  ${dur.toFixed(2)}s`);
}

const totalAudio = audioFiles.reduce((a, s) => a + s.dur, 0);
console.log(`Narration total: ${totalAudio.toFixed(1)}s`);

// Concat audio
const listPath = join(OUT, "audio", "concat.txt");
writeFileSync(
  listPath,
  audioFiles.map((a) => `file '${a.wav.replace(/'/g, "'\\''")}'`).join("\n") + "\n",
);
const narrationWav = join(OUT, "narration.wav");
sh("ffmpeg", ["-y", "-f", "concat", "-safe", "0", "-i", listPath, "-c", "copy", narrationWav], {
  stdio: "ignore",
});

// --- Browser record ---
rmSync(join(OUT, "raw"), { recursive: true, force: true });
mkdirSync(join(OUT, "raw"), { recursive: true });

console.log("Launching Chrome + recording…");
const browser = await chromium.launch({
  channel: "chrome",
  headless: false,
  args: ["--disable-blink-features=AutomationControlled"],
});
const context = await browser.newContext({
  viewport: { width: 1280, height: 720 },
  deviceScaleFactor: 1,
  recordVideo: { dir: join(OUT, "raw"), size: { width: 1280, height: 720 } },
});
const page = await context.newPage();
page.setDefaultTimeout(60000);

async function waitUi(ms) {
  await page.waitForTimeout(ms);
}

async function clickRole(role, name, exact = false) {
  const loc = page.getByRole(role, { name, exact });
  await loc.first().click({ timeout: 20000 });
}

try {
  await page.goto(URL, { waitUntil: "domcontentloaded" });
  // Wait for overview / cases to settle
  await page.waitForTimeout(4000);
  try {
    await page.getByText(/incidents|Detected|Snyder/i).first().waitFor({ timeout: 20000 });
  } catch {
    /* still record */
  }

  // 01 hook — overview
  await waitUi(audioFiles[0].dur * 1000);

  // 02 globe stay
  await waitUi(audioFiles[1].dur * 1000);

  // 03 open Snyder map
  try {
    await clickRole("button", /Snyder Fire/i);
  } catch {
    try {
      await page.getByRole("button", { name: "Map" }).click();
    } catch {
      /* already map */
    }
  }
  await page.waitForTimeout(2500);
  await waitUi(Math.max(0, audioFiles[2].dur * 1000 - 2500));

  // 04 change layer emphasis
  try {
    await page.getByRole("tab", { name: "Change" }).click();
  } catch {
    /* ok */
  }
  await waitUi(audioFiles[3].dur * 1000);

  // 05 before / after / change
  const layerBeat = (audioFiles[4].dur * 1000) / 3;
  try {
    await page.getByRole("tab", { name: "Before" }).click();
  } catch {}
  await waitUi(layerBeat);
  try {
    await page.getByRole("tab", { name: "After" }).click();
  } catch {}
  await waitUi(layerBeat);
  try {
    await page.getByRole("tab", { name: "Change" }).click();
  } catch {}
  await waitUi(layerBeat);

  // 06 optical
  try {
    await page.getByRole("tab", { name: "Optical" }).click();
  } catch {}
  await waitUi(audioFiles[5].dur * 1000);

  // 07 negative — Coleman
  try {
    await page.getByRole("button", { name: /Coleman Creek/i }).click();
    await page.waitForTimeout(2000);
    try {
      await page.getByRole("tab", { name: "Change" }).click();
    } catch {}
  } catch {
    try {
      await page.getByRole("button", { name: /EchoLens/i }).first().click();
      await page.waitForTimeout(1500);
      await page.getByRole("tab", { name: /Negative/i }).click();
    } catch {}
  }
  await waitUi(Math.max(0, audioFiles[6].dur * 1000 - 2000));

  // 08 close — About
  try {
    await page.getByRole("button", { name: "About", exact: true }).click();
  } catch {}
  await waitUi(audioFiles[7].dur * 1000 + 800);
} finally {
  await context.close();
  await browser.close();
}

// Find recorded webm
const { readdirSync } = await import("node:fs");
const rawFiles = readdirSync(join(OUT, "raw")).filter((f) => f.endsWith(".webm"));
if (!rawFiles.length) throw new Error("No Playwright video in out/raw");
const rawWebm = join(OUT, "raw", rawFiles[0]);
console.log("Raw video:", rawWebm);

const screenMp4 = join(OUT, "screen.mp4");
sh(
  "ffmpeg",
  [
    "-y",
    "-i",
    rawWebm,
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-r",
    "30",
    "-an",
    screenMp4,
  ],
  { stdio: "ignore" },
);

const screenDur = durationSec(screenMp4);
const narrDur = durationSec(narrationWav);
console.log(`Screen ${screenDur.toFixed(1)}s · Narration ${narrDur.toFixed(1)}s`);

// Pad shorter stream so mux is clean
const finalMp4 = join(OUT, "echolens-demo.mp4");
const target = Math.max(screenDur, narrDur);
sh(
  "ffmpeg",
  [
    "-y",
    "-i",
    screenMp4,
    "-i",
    narrationWav,
    "-filter_complex",
    `[0:v]tpad=stop_mode=clone:stop_duration=${Math.max(0, target - screenDur).toFixed(3)}[v];` +
      `[1:a]apad=pad_dur=${Math.max(0, target - narrDur).toFixed(3)}[a]`,
    "-map",
    "[v]",
    "-map",
    "[a]",
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-c:a",
    "aac",
    "-b:a",
    "192k",
    "-shortest",
    "-movflags",
    "+faststart",
    finalMp4,
  ],
  { stdio: "pipe" },
);

// 30-second Space Apps cut (first ~30s of full)
const shortMp4 = join(OUT, "echolens-demo-30s.mp4");
sh(
  "ffmpeg",
  [
    "-y",
    "-i",
    finalMp4,
    "-t",
    "30",
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-c:a",
    "aac",
    "-movflags",
    "+faststart",
    shortMp4,
  ],
  { stdio: "ignore" },
);

const pub = join(__dirname, "../../docs/assets");
mkdirSync(pub, { recursive: true });
copyFileSync(finalMp4, join(pub, "echolens-demo.mp4"));
copyFileSync(shortMp4, join(pub, "echolens-demo-30s.mp4"));

console.log("\nDone:");
console.log(" ", finalMp4);
console.log(" ", shortMp4);
console.log(" Copied to docs/assets/ for the repo");
console.log(` Duration ~${durationSec(finalMp4).toFixed(1)}s`);
