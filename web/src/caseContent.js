export const RASTERS = [
  { id: "before", label: "Before" },
  { id: "after", label: "After" },
  { id: "swipe", label: "Swipe" },
  { id: "change", label: "Change" },
  { id: "confidence", label: "Confidence" },
  { id: "optical", label: "Optical" },
];

export const CASE_META = {
  snyder: { type: "Wildfire", verdict: "detected", verdictNote: "40.9 km² inside the official line" },
  thunderbay: { type: "Wildfire", verdict: "detected", verdictNote: "Severe core of Ontario's largest fire" },
  nepal: { type: "Glacier flood", verdict: "detected", verdictNote: "Wet channel at 0.99 precision" },
  latvia: { type: "Flood", verdict: "negative", verdictNote: "Dry-down confirmed — no flood left" },
  crete: { type: "Flash flood", verdict: "negative", verdictNote: "Drained before the Oct 9 pass" },
  isaias: { type: "Hurricane surge", verdict: "marginal", verdictNote: "0.5 km² fringe, unvalidated" },
  coleman: { type: "Wildfire", verdict: "negative", verdictNote: "Grass range — no L-band darkening" },
  secondflat: { type: "Wildfire", verdict: "detected", verdictNote: "68.9 km² at 0.97 precision vs NIFC" },
  spokane: { type: "WUI fire", verdict: "negative", verdictNote: "Grass + structures — no HV darkening" },
};

export const VERDICT_LABEL = { detected: "Detected", negative: "Negative", marginal: "Marginal" };

export const EVENT_INFO = {
  snyder: { label: "Fire active", date: "late Jun – Jul" },
  thunderbay: { label: "Ignition", date: "12 Jul" },
  nepal: { label: "GLOF", date: "26 Aug" },
  latvia: { label: "Peak rain", date: "21–22 Aug" },
  crete: { label: "Storm (440 mm)", date: "2–4 Oct" },
  isaias: { label: "Landfall", date: "9 Oct" },
  coleman: { label: "Ignition", date: "25 Jul" },
  secondflat: { label: "Ignition", date: "24 Jul" },
  spokane: { label: "Ignition", date: "1 Aug" },
};

/** "048_A_021 · DHDH" from a GCOV filename, or null. */
export function pairFor(file) {
  const m = /_(\d{3}_[AD]_\d+)_(\d+)_([A-Z]+)_A_\d{8}T/.exec(file || "");
  return m ? `${m[1]} · ${m[3]}` : null;
}

export const LAYER_TIPS = {
  before: "Radar brightness before the event — the baseline pass",
  after: "Radar brightness after the event — same track, same settings",
  swipe: "Drag the slider to wipe between before (left) and after (right)",
  change: "After minus before, in decibels — blue got darker, red got brighter",
  confidence: "Where the radar is valid (grey) vs change we ship (colour)",
  optical: "Sentinel-2 photo near the event — usually cloud, that is the point",
};

export const OVERLAY_TIPS = {
  change: "Our flagged-change polygons — click any fragment for its area",
  perim: "Official reference outline (NIFC fire perimeter or equivalent)",
  ir: "NIROPS aircraft heat map from the same week — independent truth",
  lakes: "Permanent lakes and rivers, masked out so they never count as flood",
  emsr: "Official Copernicus Emergency Mapping polygons for this event",
  flood: "Official flood-extent polygon used to score our detection",
  rivers: "OpenStreetMap rivers — the null test: do flags follow water?",
};

export const STAT_TIPS = {
  "Before / after": "The two satellite passes compared — always same track, same radar mode",
  "EchoLens change": "Total area we flag as changed. We under-map on purpose: precision over recall",
  "Official flood in crop": "How much official flood polygon falls inside our map box",
  "Precision vs flood": "Of what we flagged, how much is really flood — 1.00 means zero false alarms",
  "Recall vs flood": "Of the real flood, how much we found — low means we map the core only",
  "GUNW coherence 19→31 Aug": "Independent check: flood water destroys radar coherence (~0.1); dry land stays high (~0.6)",
  "GUNW coherence 18→30 Aug": "Independent check: low coherence means the ground truly changed — but only rivers tell if it is water",
  "Reported complex": "Official incident size, including unburned interior and merged fires",
  "Mapped severe core": "What our threshold catches: the severely burned heart of the complex",
  "Truth overlay": "Independent data that would confirm or deny our map",
  "Permanent water masked": "Lakes and rivers dark on both dates — excluded so they never fake a flood",
  "Waterways check": "Null test: median distance of flags vs random points to mapped rivers",
  "Pair search": "We checked every pass near the peak — no better-timed pair exists on any track",
  "Copernicus water in crop": "Official mapped flood water inside our box",
  "Precision / recall vs EMSR": "Scored against Copernicus truth — low recall here means the water had drained",
  "Bay fringe flagged": "Dark shoreline pixels that may be residual surge water — shown with caveats",
  "NIFC GIS area": "Official US fire perimeter area for this incident",
  "Precision vs NIFC": "Of what we flagged, how much sits inside the official line",
  "Recall vs NIFC": "Of the official fire, how much we mapped — the severe core",
  "NIROPS heat perimeter": "Aircraft infrared outline vs ours — a second, independent witness",
  "Scattered heat 30 Jun": "Share of airborne heat detections falling inside our mapped core",
  "HVHV inside perimeter": "Median echo drop in the fire channel — the physical burn signal",
  "GUNW coherence": "Phase-stability second vote — barely split on this arid mesa, so we stayed on backscatter",
  "Optical cloud cover": "Cloud over this box in the nearest clear-photo attempt — the why-radar beat",
  "SME2 soil moisture": "Official NISAR soil-moisture product over our box — independent wetness witness",
  "NISAR pair": "Same flight track and radar mode on both dates — the guard refuses mismatched pairs",
  "NIFC perimeter": "Official US fire perimeter area for this incident",
  "Fuel check": "Median echo move inside the fire in both bands — near zero means the fuel is radar-invisible",
  "Homes lost": "Reported structure toll that makes this interface fire historic",
};

export const PITCH = [
  {
    caseId: "snyder",
    raster: "change",
    caption: "Snyder Fire: 40.9 km² of radar darkening — every pixel inside the official NIFC line.",
  },
  {
    caseId: "snyder",
    raster: "optical",
    caption: "Same week, Sentinel-2: cloud and smoke. The radar saw straight through it.",
  },
  {
    caseId: "thunderbay",
    raster: "change",
    caption:
      "Thunder Bay 36: same method on boreal forest — the mapped core of Ontario's largest fire ever.",
  },
  {
    caseId: "secondflat",
    raster: "change",
    caption:
      "Second Flat: pine burns darken hard — 68.9 km² at 0.97 precision. Same week, 60 km away, grass-fire Coleman barely registers.",
  },
  {
    caseId: "coleman",
    raster: "change",
    caption:
      "Coleman Creek: 309,000 acres of range fire, nearly invisible to L-band. Fuel physics, documented with numbers — our third kind of negative.",
  },
  {
    caseId: "latvia",
    raster: "change",
    caption:
      "Latvia, 8 days after peak rain: fragments match rivers no better than random. An honest negative.",
  },
  {
    caseId: "crete",
    raster: "change",
    caption:
      "Crete: the flash flood drained before Oct 9 — Copernicus truth itself shows no darkening. Timing is everything.",
  },
  {
    caseId: "isaias",
    raster: "change",
    caption:
      "Isaias: 3 days after landfall only a 0.5 km² bay fringe remains — marginal, unvalidated, shown with caveats.",
  },
  {
    caseId: "nepal",
    raster: "change",
    caption:
      "Nepal: same-mode pair maps the wet GLOF channel at 0.99 precision against the official flood polygon.",
  },
  {
    caseId: "snyder",
    raster: "confidence",
    caption: "Confidence: grey is valid radar, colour only where we ship. No fake second layers.",
  },
];

export function fmtKm2(n) {
  if (n == null) return "—";
  return `${Number(n).toFixed(1)} km²`;
}

function fmt2(n) {
  if (n == null) return "—";
  return Number(n).toFixed(2);
}

export function legendFor(raster, caseId) {
  if (["latvia", "nepal", "crete", "isaias"].includes(caseId)) {
    switch (raster) {
      case "before":
      case "after":
        return "HHHH backscatter · dark = water";
      case "change":
        return caseId === "nepal"
          ? "Blue: darker after (wet channel) · red: brighter · flags only inside official polygons"
          : caseId === "crete"
            ? "Blue: darker after · red: brighter (rain) · sea masked, scored vs Copernicus water"
            : caseId === "isaias"
              ? "Blue: darker after · red: brighter (rain) · bay fringe, unvalidated"
              : "Blue: darker after · red: brighter — fragments unvalidated, no river association";
      case "confidence":
        return "Grey: valid · steel: lakes · cyan: flagged fragments";
      case "swipe":
        return "Drag the slider: left = before, right = after";
      case "optical":
        return "Sentinel-2 true-colour: white = cloud";
      default:
        return "";
    }
  }
  switch (raster) {
    case "before":
    case "after":
      return "HVHV backscatter · brighter = stronger return";
    case "change":
      return "Blue: darker after the fire · red: brighter (not burn)";
    case "confidence":
      return "Grey: valid radar · colour: change we ship";
    case "swipe":
      return "Drag the slider: left = before, right = after";
    case "optical":
      return "Sentinel-2 true-colour 7 Jul: white = cloud";
    default:
      return "";
  }
}

export function ledeFor(cas) {
  if (cas.case_id === "latvia") {
    return "Two NISAR L-band passes around the Latvia–Lithuania floods (EMSR926). Peak rain was ~21–22 Aug; this pair is 18 Aug → 30 Aug, 8+ days later — L-band confirms dry-down (the scene brightened), not a flood map. The 40 flagged fragments sit no closer to rivers than random points: a negative result. Permanent lakes are masked.";
  }
  if (cas.case_id === "nepal") {
    return "Two NISAR L-band passes (19 → 31 Aug, same track and mode) around the Rasuwa glacier-lake outburst (26 Aug, EMSR927). 2.4 km² of HH darkening traces the wet gorge at 0.99 precision vs the HOT 27 Aug flood polygon — five days after the peak, the wettest channel still shows. Official Copernicus landslides and the HOT polygon sit on the same map.";
  }
  if (cas.case_id === "thunderbay") {
    return "Two NISAR L-band passes (11 Jul → 16 Aug, same track and mode) around Thunder Bay 36 in Wabakimi, Ontario — the largest fire in Ontario history (~314,000 ha). The before pass is one day pre-ignition. We map the severe burn core; Ontario publishes no 2026 perimeter yet, so FIRMS hotspots are the pending check.";
  }
  if (cas.case_id === "crete") {
    return "Two NISAR L-band passes (27 Sep → 9 Oct, same track and mode) around the Crete flash flood (2–4 Oct, EMSR933, 440 mm in 48 h). By Oct 9 the water had drained — the mapped polygons show no darkening, so this case is an honest negative: sea masked, rain brightening visible, no flood left to map.";
  }
  if (cas.case_id === "isaias") {
    return "Two NISAR L-band passes (30 Sep → 12 Oct, same track and mode) around Hurricane Isaias, Cat 2 landfall near Destin FL on 9 Oct. The 9-hour-post-landfall pass turned out to be a frame-edge sliver; this pair is 3 days post-landfall — surge receded, rain brightening everywhere, and a 0.5 km² dark bay fringe that may be residual surge water. Unvalidated: no USGS water-mark event published yet.";
  }
  if (cas.case_id === "coleman") {
    return "Two NISAR L-band passes (8 Jul → 13 Aug, same track and mode) around the Coleman Creek fire in Harney County, Oregon — 309,000 acres of high-desert range, ignited 25 Jul. The fire barely darkens L-band in either polarization: a fuel-type negative. Sixty kilometres west, the same satellite and week caught pine-fire Second Flat cleanly.";
  }
  if (cas.case_id === "secondflat") {
    return "Two NISAR L-band passes (8 Jul → 13 Aug, same track and mode — the same granules as Coleman Creek) around the Second Flat fire in Lake County, Oregon: 106,000 acres of sage and pine, ignited 24 Jul. Pine canopy loss darkens HV hard: 68.9 km² at 0.97 precision vs the NIFC perimeter.";
  }
  if (cas.case_id === "spokane") {
    return "Two NISAR L-band passes (23 Jul → 16 Aug, same track and mode) around the Autumn Lane fire at Spokane's edge — 5,764 acres, ignited 1 Aug, part of the early-August complex that burned 833 homes and became Washington's costliest wildfire disaster. The burn was grass and structures at the urban edge: inside the NIFC line the echo moves +0.13 dB, indistinguishable from background — a fuel-context negative.";
  }
  return "Two NISAR L-band passes around the Snyder Fire. The map is not a photo — it is radar backscatter change, checked against an official perimeter.";
}

export function whySarFor(cas) {
  if (cas.case_id === "latvia") {
    return cas.has_optical
      ? "Click Optical: Sentinel-2 around the storm is cloud. L-band still sees new water as a dark HH return. Lakes dark on both dates are not flood."
      : "Cloud and rain hide optical. L-band still sees new water as a dark HH return. Lakes that were dark on both dates are not flood.";
  }
  if (cas.case_id === "nepal") {
    return "Steep Himalaya, monsoon cloud, and a narrow gorge — optical cannot see the valley floor, but L-band maps the wet channel at 80 m. Flags stay inside official Copernicus/HOT polygons so layover slopes stay off the map; no morphological opening, so rivers narrower than two pixels survive.";
  }
  if (cas.case_id === "thunderbay") {
    return "Boreal smoke for weeks — optical stacks white. L-band HV sees canopy loss directly: boreal burns drop 3–6 dB, the strongest fire signal in the book.";
  }
  if (cas.case_id === "crete") {
    return "Flash floods drain in hours on steep islands — timing is everything. The Oct 9 pass came 5 days after the rain; a mid-event Oct 4 pair exists but its valid swath misses Lasithi. Negative results still teach: this is what a missed window looks like.";
  }
  if (cas.case_id === "isaias") {
    return "Surge peaks at landfall and drains in hours; our usable pass is 3 days later. What remains is a rain-soaked landscape (+0.9 dB) and a marginal dark bay fringe. We show the 0.5 km² with its caveats rather than a clean false map.";
  }
  if (cas.case_id === "coleman") {
    return "Range grass holds almost no L-band structure to lose: green or charred, the echo barely changes. Optical sees the blackened acres fine — but this case asks what radar alone can say, and the answer, measured, is almost nothing.";
  }
  if (cas.case_id === "secondflat") {
    return "Pine canopy is ideal L-band fuel: dense volume scattering before, char and ash after. Same sensor, same week as Coleman — the difference is what burned, not how we looked.";
  }
  if (cas.case_id === "spokane") {
    return "Buildings dominate the L-band echo whether they stand or burn — rubble and cleared lots scatter almost as loudly as roofs, and the surrounding grass behaves as at Coleman Creek. Optical counts the 833 homes; radar alone cannot see this fire, and we measured exactly how invisible it is.";
  }
  return cas.has_optical
    ? "Click Optical: Sentinel-2 on 7 Jul (during the fire) is 34% cloud over this box. Radar still returns a scar. NIROPS IR is the aircraft heat map from the same week — not FIRMS."
    : "Optical would be smoke and cloud. Radar still returns a scar. Run python scripts/fetch_optical.py to load the 7 Jul Sentinel-2 scene.";
}

export function trustFor(cas, cite) {
  if (cas.case_id === "latvia") {
    return "Valid GCOV pixels, 3×3 median despeckle, HH log-ratio ≥ 2 dB darker after, and the after pixel looks like water. Permanent water (dark on both dates) is not flagged. GUNW coherence confirms the fragments are real surface changes (0.19 vs 0.39 background — late-August field activity is plausible), but checked against HOTOSM rivers they sit a median 1.1 km from water vs 1.0 km for random points — no river association, so we report a negative result. Official EMSR926 flood vectors were still not on HDX as of 29 Oct 2026.";
  }
  if (cas.case_id === "nepal") {
    return "Same-mode pair (098_A_016, DHDH both dates), 3×3 despeckle, HH ≥ 2 dB darker — the knee of a threshold sweep against the HOT flood polygon and EMSR landslides. Precision 0.99, recall 0.18 vs HOT: we under-map the receded flood on purpose, and slope audit confirms flags sit on valley floors (8° median vs 33° background). GUNW coherence independently agrees: 0.11 inside flags vs 0.59 background.";
  }
  if (cas.case_id === "thunderbay") {
    return "Same-mode pair (041_D_063, DHDH both dates), 3×3 despeckle, HV ≥ 1.5 dB darker — Snyder parity for a like-for-like boreal comparison. We map the severe core only (~7% of the reported 314,000 ha complex, which includes unburned interior and merged fires). FIRMS hotspot overlay pending.";
  }
  if (cas.case_id === "crete") {
    return "Same-mode pair (137_D_071, DHDH both dates), DEM land mask (sea-state change would fake flood), HH ≥ 2 dB darker + water-like after. Result: 27 pixels, precision 0.33 / recall 0.01 vs 748 Copernicus polygons — the truth pixels themselves read −9 dB with zero darkening. Water gone by Oct 9.";
  }
  if (cas.case_id === "isaias") {
    return "Same-mode pair (004_A_017, DHDH both dates), DEM land mask, HH ≥ 1.5 dB darker + after ≤ −10 dB for turbid surge water. Result: 81 pixels / 0.52 km² of bay fringe. Unvalidated — treat as a marginal detection, not a flood map.";
  }
  if (cas.case_id === "coleman") {
    return "Same-mode pair (005_A_024, DHDH both dates), HV ≥ 1.5 dB darker — Snyder parity. Inside the 1,307 km² NIFC perimeter the HV median moves −0.10 dB (HH −0.03 dB): only 4.5% of fire pixels cross the cut vs 1.2% background noise. Precision 0.48, recall 0.013 — a measured fuel limit, and the reason Second Flat exists on this map.";
  }
  if (cas.case_id === "secondflat") {
    return "Same-mode pair (005_A_024, DHDH both dates — shared granules with Coleman), HV ≥ 1.5 dB darker. Precision 0.97, recall 0.16 vs the 432 km² NIFC perimeter: the pine core maps cleanly with almost nothing outside the line. The Coleman/Second Flat pair is a controlled experiment in fuel physics.";
  }
  if (cas.case_id === "spokane") {
    return "Same-mode pair (042_D_065, DHDH both dates), HV ≥ 1.5 dB darker — Snyder parity — scored against the Autumn Lane NIFC perimeter. Inside median +0.13 dB (HH +0.35 dB), only 1.6% of fire pixels cross the cut vs 1.3% background noise: precision and recall 0.0. Nine stray pixels flagged, none inside the line.";
  }
  return `Valid GCOV pixels only, 3×3 median despeckle, HVHV log-ratio ≥ 1.5 dB darker after the fire. Every flagged pixel sits inside NIFC WFIGS ${cite.unique_fire_identifier || ""}. The red patch east of the perimeter brightened between the June and July passes (likely vegetation/moisture change); detection flags darkening only, so it stays off the map. GUNW HH coherence barely drops on this arid mesa (0.73 vs 0.76) — so detection stays on GCOV, not a fake second layer.`;
}

export function sourceFor(cas, cite) {
  if (cas.case_id === "latvia") {
    return "Copernicus EMS Rapid Mapping EMSR926. Pitch still opens on Snyder.";
  }
  if (cas.case_id === "thunderbay") {
    return "Ontario AFFES incident THU036 (sizes; no 2026 perimeter layer). Pitch still opens on Snyder.";
  }
  if (cas.case_id === "crete") {
    return "Copernicus EMS Rapid Mapping EMSR933 (observed flood water). Pitch still opens on Snyder.";
  }
  if (cas.case_id === "isaias") {
    return "NHC Hurricane Isaias advisory archive; USGS high-water marks pending. Pitch still opens on Snyder.";
  }
  if (cas.case_id === "nepal") {
    return "Copernicus EMSR927 (landslides along the GLOF path) + HOT flood extent 27 Aug (Bhote Koshi / Trishuli). UNOSAT Rasuwa mudflow and barrier-lake maps are the same event. Pitch still opens on Snyder.";
  }
  if (cas.case_id === "coleman") {
    return "NIFC WFIGS 2026-ORBUD-002696 (308,864 acres, 100% contained). Pitch still opens on Snyder.";
  }
  if (cas.case_id === "secondflat") {
    return "NIFC WFIGS 2026-ORBUD-002693 (105,854 acres, 100% contained). Pitch still opens on Snyder.";
  }
  if (cas.case_id === "spokane") {
    return "NIFC WFIGS 2026-WANES-001857 (5,764 acres) + WA damage reports (833 homes). Pitch still opens on Snyder.";
  }
  return `Perimeter: ${cite.polygon || ""}${cite.unique_fire_identifier ? ` · ${cite.unique_fire_identifier}` : ""}. FIRMS is hotspots, not this outline.`;
}

/** Per-case stat rows for the briefing panel. Values are preformatted strings. */
export function statsFor(cas) {
  const cloud =
    cas.has_optical && cas.optical?.cloud_cover_pct != null
      ? `${Number(cas.optical.cloud_cover_pct).toFixed(0)}% · Sentinel-2 ${
          cas.optical.datetime
            ? String(cas.optical.datetime).slice(0, 10)
            : cas.case_id === "snyder"
              ? "7 Jul"
              : ""
        }`.trim()
      : null;
  const base = [
    { k: "Before / after", v: `${cas.before} → ${cas.after}` },
    { k: "EchoLens change", v: fmtKm2(cas.area_km2), big: true },
  ];
  const pair = pairFor(cas.before_file);
  if (pair) base.push({ k: "NISAR pair", v: `${pair} both dates` });
  if (cas.case_id === "nepal") {
    base.push(
      { k: "Official flood in crop", v: fmtKm2(cas.official_flood_km2_in_crop) },
      { k: "Precision vs flood", v: fmt2(cas.precision_vs_flood), hl: true },
      { k: "Recall vs flood", v: fmt2(cas.recall_vs_flood) },
    );
    const g = cas.gunw_check?.regions;
    if (g?.[0]?.mean != null && g?.[1]?.mean != null) {
      base.push({
        k: "GUNW coherence 19→31 Aug",
        v: `${fmt2(g[0].mean)} inside flags vs ${fmt2(g[1].mean)} background — independent water vote`,
        hl: true,
      });
    }
  } else if (cas.case_id === "thunderbay") {
    base.push(
      { k: "Reported complex", v: "~3,140 km² (AFFES)" },
      {
        k: "Mapped severe core",
        v: `${fmtKm2(cas.area_km2)} — ≈${cas.area_km2 != null ? Number((cas.area_km2 / 3140) * 100).toFixed(0) : "—"}% of reported`,
      },
      { k: "Truth overlay", v: "FIRMS hotspots pending" },
    );
  } else if (cas.case_id === "latvia") {
    base.push({ k: "Permanent water masked", v: fmtKm2(cas.permanent_water_km2) });
    if (cas.waterways_check) {
      base.push({
        k: "Waterways check",
        v: `Fragments ${(cas.waterways_check.change_median_m / 1000).toFixed(1)} km from rivers vs ${(cas.waterways_check.random_median_m / 1000).toFixed(1)} km random — no association`,
      });
    }
    if (cas.pair_search) {
      base.push({
        k: "Pair search",
        v: "No 21–24 Aug pass on any track — shipped pair is best-timed",
      });
    }
    const g = cas.gunw_check?.regions;
    if (g?.[0]?.mean != null && g?.[1]?.mean != null) {
      base.push({
        k: "GUNW coherence 18→30 Aug",
        v: `${fmt2(g[0].mean)} inside fragments vs ${fmt2(g[1].mean)} background — real change, but rivers test says not flood`,
      });
    }
  } else if (cas.case_id === "crete") {
    base.push(
      { k: "Copernicus water in crop", v: fmtKm2(cas.emsr_water_km2_in_crop) },
      {
        k: "Precision / recall vs EMSR",
        v: `${fmt2(cas.precision_vs_emsr)} / ${fmt2(cas.recall_vs_emsr)} — drained before Oct 9`,
      },
    );
  } else if (["coleman", "secondflat", "spokane"].includes(cas.case_id)) {
    base.push(
      { k: "NIFC perimeter", v: fmtKm2(cas.truth_km2) },
      {
        k: "Precision vs NIFC",
        v: fmt2(cas.precision_vs_truth),
        hl: (cas.precision_vs_truth ?? 0) > 0.5,
      },
      { k: "Recall vs NIFC", v: fmt2(cas.recall_vs_truth) },
    );
    if (cas.case_id === "coleman" && cas.fuel_check) {
      base.push({
        k: "Fuel check",
        v: `HV ${fmt2(cas.fuel_check.inside_hv_median_db)} dB inside (HH ${fmt2(cas.fuel_check.inside_hh_median_db)}) — no darkening in either band`,
      });
    }
    if (cas.case_id === "spokane") {
      base.push({ k: "Homes lost", v: "833 — costliest WA fire disaster" });
    }
  } else if (cas.case_id === "isaias") {
    base.push(
      { k: "Bay fringe flagged", v: `${fmtKm2(cas.area_km2)} — marginal, unvalidated`, hl: true },
      { k: "Truth overlay", v: "No USGS water-mark event yet" },
    );
    const sm = cas.soil_moisture_check;
    if (sm?.delta_DSG != null && sm?.delta_TSR != null) {
      const db = cas.hh_median_diff_db != null ? `+${Number(cas.hh_median_diff_db).toFixed(1)} dB` : "scene brightening";
      base.push({
        k: "SME2 soil moisture",
        v: `All 3 algorithms wetter after (+${sm.delta_DSG.toFixed(2)} to +${sm.delta_TSR.toFixed(2)} m³/m³) — matches ${db}`,
      });
    }
  } else {
    base.push(
      { k: "NIFC GIS area", v: fmtKm2(cas.nifc_km2) },
      {
        k: "Precision vs NIFC",
        v: cas.precision_vs_nifc === 1 ? "1.00 — nothing outside the line" : fmt2(cas.precision_vs_nifc),
        hl: true,
      },
    );
    if (cas.recall_vs_nifc != null) {
      base.push({ k: "Recall vs NIFC", v: `${fmt2(cas.recall_vs_nifc)} — under-mapped on purpose` });
    }
    const hp = cas.nirops_check?.find((r) => r.kind === "heat_perimeter");
    if (hp) {
      base.push({
        k: "NIROPS heat perimeter",
        v: `Precision ${fmt2(hp.precision_vs_ir)} · recall ${fmt2(hp.recall_vs_ir)} — aircraft IR agrees`,
      });
    }
    const sh = cas.nirops_check?.find((r) => r.kind === "scattered_heat");
    if (sh) {
      base.push({
        k: "Scattered heat 30 Jun",
        v: `${fmt2(sh.recall_vs_ir)} inside our change — active fire in the core`,
      });
    }
    base.push({ k: "HVHV inside perimeter", v: `${fmt2(cas.inside_hv_median_db)} dB (drop)` });
    const sm = cas.soil_moisture_check;
    const dsgB = sm?.before?.DSG;
    const dsgA = sm?.after?.DSG;
    if (dsgB?.east_median != null && dsgA?.east_median != null) {
      base.push({
        k: "SME2 soil moisture",
        v: `East half ${dsgB.east_median.toFixed(2)}→${dsgA.east_median.toFixed(2)} vs west ${dsgB.west_median.toFixed(2)}→${dsgA.west_median.toFixed(2)} m³/m³ — moisture read confirmed`,
      });
    }
    if (cas.gunw_coherence) {
      base.push({
        k: "GUNW coherence",
        v: `${fmt2(cas.gunw_coherence.inside_mean)} inside vs ${fmt2(cas.gunw_coherence.outside_mean)} outside`,
      });
    }
  }
  if (cloud) base.push({ k: "Optical cloud cover", v: cloud });
  return base;
}

export const SOURCE_LINKS = [
  ["url", null],
  ["hdx", "HDX EMSR927"],
  ["unosat_mudflow", "UNOSAT mudflow"],
  ["inciweb", "InciWeb"],
  ["wfigs_layer", "NIFC WFIGS"],
  ["ops_maps", "Ops maps"],
];
