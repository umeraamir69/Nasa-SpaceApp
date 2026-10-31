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
};

export const VERDICT_LABEL = { detected: "Detected", negative: "Negative", marginal: "Marginal" };

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
