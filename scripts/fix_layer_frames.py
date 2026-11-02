#!/usr/bin/env python3
"""One-time layer-frame registration fixes (idempotent, stdlib only).

1. Snyder optical.png: center-crop to the exact radar bounds aspect.
   fetch_optical rounds its read window to whole Sentinel-2 pixels, so the
   PNG covered a slightly taller frame than bounds.json; Leaflet stretched
   it back, misregistering the overlay by ~6% of frame height.
2. Latvia: drop fully-invalid rows 531..992 from every web layer (the
   diagonal swath wedge leaves rows 700+ with zero valid pixels) and
   re-crop optical.png to the same geographic window + exact aspect.
   All 40 change polygons sit in rows 21..512, so nothing is lost.

Run:  venv/bin/python scripts/fix_layer_frames.py
Verify: venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from png_crop import crop_png, read_png  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def aspect(w: int, h: int) -> float:
    return w / h


def center_crop_to_aspect(png: Path, target_aspect: float) -> None:
    w, h, _, _ = read_png(str(png))
    if abs(aspect(w, h) - target_aspect) / target_aspect < 0.005:
        print(f"  {png.name}: aspect ok ({w}x{h}), skip")
        return
    # Optical frames cover a slightly larger window than bounds.json (read
    # window rounded outward): trim the excess dimension to exact aspect.
    if aspect(w, h) < target_aspect:
        new_h = round(w / target_aspect)
        assert new_h < h, f"{png.name}: {w}x{h} vs {target_aspect:.4f}"
        y0 = (h - new_h) // 2
        crop_png(str(png), str(png), 0, y0, w, new_h)
        print(f"  {png.name}: {w}x{h} -> {w}x{new_h} (center rows {y0}..{y0 + new_h})")
    else:
        new_w = round(h * target_aspect)
        assert new_w < w, f"{png.name}: {w}x{h} vs {target_aspect:.4f}"
        x0 = (w - new_w) // 2
        crop_png(str(png), str(png), x0, 0, new_w, h)
        print(f"  {png.name}: {w}x{h} -> {new_w}x{h} (center cols {x0}..{x0 + new_w})")


def fix_optical_aspect(case: str) -> None:
    print(f"{case} optical:")
    layers = ROOT / "outputs" / case / "layers"
    opt = layers / "optical.png"
    if not opt.exists():
        print("  no optical.png, skip")
        return
    b = json.loads((layers / "bounds.json").read_text())
    center_crop_to_aspect(opt, aspect(b["width"], b["height"]))


def main() -> int:
    fix_optical_aspect("snyder")
    fix_optical_aspect("thunderbay")
    fix_optical_aspect("crete")
    fix_optical_aspect("isaias")
    fix_optical_aspect("coleman")
    fix_optical_aspect("secondflat")
    fix_optical_aspect("spokane")

    # --- Latvia recrop ---
    print("latvia recrop:")
    layers = ROOT / "outputs" / "latvia" / "layers"
    bounds_path = layers / "bounds.json"
    b = json.loads(bounds_path.read_text())
    KEEP_ROWS = 531  # rows 0..530 hold 100% of change polygons + margin
    if b["height"] == KEEP_ROWS:
        print("  bounds already recropped, skip")
        return 0
    assert (b["width"], b["height"]) == (970, 993), f"unexpected bounds {b}"

    for name in ("before.png", "after.png", "change.png", "confidence.png"):
        w, h, _, _ = read_png(str(layers / name))
        assert (w, h) == (970, 993), f"{name} is {w}x{h}"
        crop_png(str(layers / name), str(layers / name), 0, 0, 970, KEEP_ROWS)
        print(f"  {name}: 970x993 -> 970x{KEEP_ROWS}")

    # Optical covers the same geo window at its own resolution: fix its aspect
    # first (symmetric padding from window rounding), then take the same window.
    opt = layers / "optical.png"
    center_crop_to_aspect(opt, aspect(970, 993))
    ow, oh, _, _ = read_png(str(opt))
    oh_keep = round(KEEP_ROWS / 993 * oh)
    crop_png(str(opt), str(opt), 0, 0, ow, oh_keep)
    print(f"  optical.png: top-cropped to {ow}x{oh_keep}")

    frac = KEEP_ROWS / 993
    new_bounds = dict(b)
    new_bounds["south"] = b["north"] - frac * (b["north"] - b["south"])
    new_bounds["height"] = KEEP_ROWS
    new_bounds["frame_note"] = (
        "Web layers keep rows 0..530 of the 993-row processing crop; rows below "
        "are mostly outside the valid swath overlap. All change polygons are kept."
    )
    bounds_path.write_text(json.dumps(new_bounds, indent=2))
    print(f"  bounds: height 993 -> {KEEP_ROWS}, south {new_bounds['south']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
