#!/usr/bin/env python3
"""Case-asset integrity tests (stdlib only).

Run:  venv/bin/python -m unittest discover -s tests -v

Guards the committed demo artifacts without needing raw NISAR data:
bounds sanity, PNG dimensions matching bounds, GeoJSON validity,
summary fields, and the granule mode-compatibility guard that
must flag the Nepal cross-mode pair.
"""

from __future__ import annotations

import json
import struct
import sys
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CASES = ("snyder", "latvia", "nepal", "thunderbay", "crete", "isaias",
         "coleman", "secondflat", "spokane")
# Loose lon/lat plausibility boxes per case: (west, south, east, north).
PLAUSIBLE = {
    "snyder": (-110.0, 38.0, -108.0, 40.0),
    "latvia": (20.0, 56.0, 24.0, 58.0),
    "nepal": (84.0, 27.0, 86.0, 29.0),
    "thunderbay": (-91.0, 49.0, -88.0, 52.0),
    "crete": (24.0, 34.0, 27.0, 36.0),
    "isaias": (-88.0, 29.5, -85.0, 32.0),
    "coleman": (-119.0, 43.0, -117.0, 44.2),
    "secondflat": (-120.0, 43.2, -118.5, 44.1),
    "spokane": (-118.0, 47.4, -117.0, 48.1),
}


def read_png_size(path: Path) -> tuple[int, int]:
    with open(path, "rb") as fh:
        sig = fh.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"not a PNG: {path}")
        (length,) = struct.unpack(">I", fh.read(4))
        ctype = fh.read(4)
        if ctype != b"IHDR":
            raise ValueError(f"no IHDR: {path}")
        w, h = struct.unpack(">II", fh.read(8))
    return w, h


def walk_coords(geom, out: list):
    if geom is None:
        return
    t = geom.get("type")
    c = geom.get("coordinates")
    if t == "Point":
        out.append(c)
    elif t in ("MultiPoint", "LineString"):
        out.extend(c)
    elif t in ("MultiLineString", "Polygon"):
        for part in c:
            out.extend(part)
    elif t == "MultiPolygon":
        for poly in c:
            for ring in poly:
                out.extend(ring)
    elif t == "GeometryCollection":
        for g in geom.get("geometries", []):
            walk_coords(g, out)


class CaseAssets(unittest.TestCase):
    def test_bounds_sane(self):
        for case in CASES:
            with self.subTest(case=case):
                b = json.loads((ROOT / "outputs" / case / "layers" / "bounds.json").read_text())
                self.assertLess(b["south"], b["north"])
                self.assertLess(b["west"], b["east"])
                self.assertGreater(b["width"], 0)
                self.assertGreater(b["height"], 0)
                self.assertEqual(b["pixel_m"], 80.0)

    def test_png_dims_match_bounds(self):
        # Radar layers share the processing grid exactly. optical.png covers the
        # same geographic bounds at its own resolution (capped 896 wide), so it
        # is exempt here and checked for registration by its aspect ratio.
        for case in CASES:
            b = json.loads((ROOT / "outputs" / case / "layers" / "bounds.json").read_text())
            for png in sorted((ROOT / "outputs" / case / "layers").glob("*.png")):
                if png.name == "optical.png":
                    continue
                with self.subTest(case=case, png=png.name):
                    w, h = read_png_size(png)
                    self.assertEqual((w, h), (b["width"], b["height"]),
                                     f"{png.name} is {w}x{h}, bounds say {b['width']}x{b['height']}")

    def test_optical_aspect_matches_bounds(self):
        for case in CASES:
            png = ROOT / "outputs" / case / "layers" / "optical.png"
            if not png.exists():
                continue
            with self.subTest(case=case):
                b = json.loads((ROOT / "outputs" / case / "layers" / "bounds.json").read_text())
                w, h = read_png_size(png)
                # Same geographic extent: aspect ratios must agree within 2%.
                expect = b["width"] / b["height"]
                got = w / h
                self.assertAlmostEqual(got, expect, delta=0.02 * expect,
                                       msg=f"optical {w}x{h} aspect {got:.3f} vs bounds {expect:.3f}")

    def test_geojson_valid(self):
        for case in CASES:
            for gj_path in sorted((ROOT / "outputs" / case).glob("*.geojson")):
                with self.subTest(case=case, file=gj_path.name):
                    gj = json.loads(gj_path.read_text())
                    self.assertEqual(gj["type"], "FeatureCollection")
                    self.assertTrue(gj.get("features"), "no features")
                    west, south, east, north = PLAUSIBLE[case]
                    seen = 0
                    for feat in gj["features"]:
                        pts: list = []
                        walk_coords(feat.get("geometry"), pts)
                        for lon, lat in pts:
                            self.assertTrue(-180 <= lon <= 180 and -90 <= lat <= 90)
                            self.assertTrue(west <= lon <= east and south <= lat <= north,
                                            f"({lon}, {lat}) outside {case} plausibility box")
                            seen += 1
                    if gj_path.name in ("change.geojson", "perimeter_nifc.geojson",
                                        "lakes.geojson", "emsr927.geojson",
                                        "flood_extent.geojson", "rivers.geojson"):
                        self.assertGreater(seen, 0, "expected real coordinates")

    def test_change_inside_layer_bounds(self):
        for case in CASES:
            with self.subTest(case=case):
                b = json.loads((ROOT / "outputs" / case / "layers" / "bounds.json").read_text())
                gj = json.loads((ROOT / "outputs" / case / "change.geojson").read_text())
                pts: list = []
                for feat in gj["features"]:
                    walk_coords(feat.get("geometry"), pts)
                self.assertTrue(pts, "change.geojson has no coordinates")
                # 0.01° slack: UTM grids are rotated in lon/lat, so edge
                # pixels legitimately fall outside the corner-derived box
                # (measured 0.006° on secondflat's south edge, 2 Nov 2026).
                eps = 0.01
                for lon, lat in pts:
                    self.assertTrue(b["west"] - eps <= lon <= b["east"] + eps
                                    and b["south"] - eps <= lat <= b["north"] + eps,
                                    f"change coord ({lon}, {lat}) outside layer bounds")

    def test_summary_fields(self):
        for case in CASES:
            with self.subTest(case=case):
                s = json.loads((ROOT / "outputs" / case / "summary.json").read_text())
                for key in ("before", "after", "before_file", "after_file",
                            "pixel_m", "threshold_db", "area_km2", "citation"):
                    self.assertIn(key, s)
                self.assertGreaterEqual(s["area_km2"], 0)


class ChangeApi(unittest.TestCase):
    def test_exploded_fragments_sum_to_summary(self):
        sys.path.insert(0, str(ROOT))
        from app.main import geojson_change
        for case in CASES:
            with self.subTest(case=case):
                fc = json.loads(geojson_change(case).body)
                self.assertTrue(fc["features"])
                total = 0.0
                for feat in fc["features"]:
                    self.assertEqual(feat["geometry"]["type"], "Polygon")
                    self.assertIn("part", feat["properties"])
                    self.assertGreaterEqual(feat["properties"]["area_km2"], 0)
                    total += feat["properties"]["area_km2"]
                summary = json.loads((ROOT / "outputs" / case / "summary.json").read_text())
                # Equirectangular approx vs equal-area truth: within 5%.
                self.assertAlmostEqual(total, summary["area_km2"],
                                       delta=0.05 * max(summary["area_km2"], 0.5),
                                       msg=f"{case}: fragments sum {total:.2f} vs {summary['area_km2']}")


class GranuleModes(unittest.TestCase):
    def test_committed_pairs_are_same_mode(self):
        import granule_modes as gm
        # Every shipped case must be same track/beam/mode. Nepal was the
        # cross-mode offender until the 098_A_016 reprocessing (29 Oct 2026);
        # the negative path is covered by test_guard_parses_names.
        for case in ("snyder", "latvia", "nepal", "thunderbay", "crete", "isaias",
                     "coleman", "secondflat", "spokane"):
            with self.subTest(case=case):
                s = json.loads((ROOT / "outputs" / case / "summary.json").read_text())
                ok, reason = gm.modes_compatible(s["before_file"], s["after_file"])
                self.assertTrue(ok, f"{case}: {reason}")

    def test_guard_parses_names(self):
        import granule_modes as gm
        before = "NISAR_L2_PR_GCOV_028_080_D_059_2005_DHDH_A_20260818T180558_20260818T180634_P05023_N_F_J_001.h5"
        after = "NISAR_L2_PR_GCOV_029_080_D_059_2005_DHDH_A_20260830T180558_20260830T180634_P05023_N_F_J_001.h5"
        ok, _ = gm.modes_compatible(before, after)
        self.assertTrue(ok)
        bad = after.replace("_2005_DHDH_", "_2005_QPDH_")
        ok, reason = gm.modes_compatible(before, bad)
        self.assertFalse(ok)
        self.assertIn("QPDH", reason)


if __name__ == "__main__":
    unittest.main()
