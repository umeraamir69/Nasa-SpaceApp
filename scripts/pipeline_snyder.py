#!/usr/bin/env python3
"""Unattended Snyder pipeline: perimeter → GCOV change → cloudy optical.

Does not download NISAR granules. Needs the GCOV pair already in data/snyder/gcov/.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def run(script: str) -> None:
    path = ROOT / "scripts" / script
    print(f"\n==> {script}")
    subprocess.check_call([PY, str(path)], cwd=ROOT)


def main() -> int:
    gcov = list((ROOT / "data" / "snyder" / "gcov").glob("*.h5"))
    if len(gcov) < 2:
        print("Need two GCOV .h5 files in data/snyder/gcov/. See notes/docs/Get the data.md.", file=sys.stderr)
        return 1
    run("fetch_snyder_perimeter.py")
    run("change_snyder.py")
    run("fetch_optical.py")
    print("\noutputs/snyder is ready. Start the app: notes/Runbooks/Run the app.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
