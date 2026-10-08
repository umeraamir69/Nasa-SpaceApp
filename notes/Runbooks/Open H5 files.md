---
tags:
  - ops
---

# Runbook: Open the .h5 files

Do **not** open them in Preview, Finder Quick Look, Excel, or as text in the editor. They are ~7 GB HDF5 scientific files.

## Fastest on this machine

`h5py` is already in the project venv:

```text
cd /Users/muhamamd/Documents/nasa
source venv/bin/activate
python scripts/inspect_h5.py
python scripts/inspect_h5.py data/snyder/gcov/NISAR_L2_PR_GCOV_026_048_A_021_4005_DHDH_A_20260723T122754_20260723T122829_P05023_N_F_J_001.h5
```

That prints the layer list, identity (date, track), and stats from the small 80 m `HHHH` grid. It does not load the full 10 m image.

## Clickable app — Panoply 5.10.1 (installed)

App: `/Applications/Panoply.app`. Needs Java 11+. OpenJDK 21 is installed. Your default `JAVA_HOME` is still enterprise Java 8 — leave that alone.

Do **not** double-click Panoply or the DMG. Your default Java is 8, so that dialog appears. Use:

```text
cd /Users/muhamamd/Documents/nasa
source venv/bin/activate   # optional
./scripts/open_panoply.sh
```

Panoply **cannot open these NISAR GCOV files**. It dies with `extendDimension: Dimscale has a different length than the dimension it references dimScale=yCoordinates`. Cause: `frequencyB/inputDataExceptionMask` is stored at Frequency A size (35064×35568) while `yCoordinates` is 4383. netCDF-Java/Panoply cannot attach that.

Look at the data with the preview instead:

```text
python scripts/preview_gcov.py
```

PNGs land in `data/snyder/preview/` (June, July, July−June). Open those in Preview.

The download in Downloads was named `.man` but it is the official 56 MB DMG (checksum matched). A copy is `Downloads/PanoplyMacOS-arm64-5.10.1.dmg`.

Related: [[research/What GCOV is]] [[Runbooks/Download NISAR]]
