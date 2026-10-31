#!/usr/bin/env python3
"""Parse NISAR GCOV granule names and refuse cross-mode change pairs.

Comparing dual-pol (DHDH) against quad-pol (QPDH), or different beam
configs (…_4005_… vs …_2005_…), mixes different calibrations and swath
coverage. The Nepal case shipped exactly that pair, which produced a
scene-wide red/blue gradient artifact and a near-empty detection.

Stdlib only, so the unit tests can import it anywhere.
"""

from __future__ import annotations

import re

_GRANULE = re.compile(
    r"NISAR_L2_PR_GCOV_"        # product
    r"(?P<cycle>\d+)_"         # cycle
    r"(?P<rel_orbit>\d+)_"     # relative orbit
    r"(?P<dir>[AD])_"          # ascending / descending
    r"(?P<frame>\d+)_"         # frame
    r"(?P<beam>[^_]+)_"          # beam / mode config, e.g. 4005
    r"(?P<polmode>[^_]+)_"       # polarisation mode, e.g. DHDH, QPDH
    r"(?P<rest>.*)"
)


def parse(granule: str) -> dict[str, str]:
    """Split a GCOV granule filename into its comparable fields."""
    m = _GRANULE.match(granule.strip())
    if not m:
        raise ValueError(f"not a NISAR GCOV granule name: {granule!r}")
    return m.groupdict()


def modes_compatible(before: str, after: str) -> tuple[bool, str]:
    """True when two granules share track, beam and polarisation mode.

    Returns (ok, reason). Cycle and sensing date are expected to differ.
    """
    try:
        b, a = parse(before), parse(after)
    except ValueError as exc:
        return False, str(exc)
    for key in ("rel_orbit", "dir", "frame", "beam", "polmode"):
        if b[key] != a[key]:
            return False, (
                f"cross-mode pair: {key} {b[key]!r} (before) vs {a[key]!r} (after); "
                "log-ratio change is not valid across modes"
            )
    return True, "same track, beam and polarisation mode"


def require_compatible(before: str, after: str) -> None:
    """Raise SystemExit unless the pair is comparable."""
    ok, reason = modes_compatible(before, after)
    if not ok:
        raise SystemExit(f"refusing {reason}")
