#!/usr/bin/env python3
"""Stdlib-only PNG crop/pad for 8-bit non-interlaced RGB/RGBA/greyscale.

Only what the layer-registration fixes need: read rows, slice a window,
write back. No numpy/PIL (the project venv cannot build them).
"""

from __future__ import annotations

import struct
import zlib


def _chunks(blob: bytes):
    assert blob[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos = 8
    while pos < len(blob):
        (length,) = struct.unpack(">I", blob[pos:pos + 4])
        ctype = blob[pos + 4:pos + 8]
        data = blob[pos + 8:pos + 8 + length]
        yield ctype, data
        pos += 12 + length


def read_png(path: str):
    """Return (width, height, channels, rows) with rows as list of bytes."""
    blob = open(path, "rb").read()
    w = h = bitd = ctype = interlace = None
    raw = b""
    for kind, data in _chunks(blob):
        if kind == b"IHDR":
            w, h, bitd, ctype, _, _, interlace = struct.unpack(">IIBBBBB", data)
        elif kind == b"IDAT":
            raw += data
    assert bitd == 8, f"only 8-bit PNG supported, got {bitd}"
    assert interlace == 0, "interlaced PNG not supported"
    ch = {0: 1, 2: 3, 6: 4}[ctype]
    stride = w * ch
    pix = zlib.decompress(raw)
    rows, prev = [], bytearray(stride)
    pos = 0
    for _ in range(h):
        f = pix[pos]
        pos += 1
        line = bytearray(pix[pos:pos + stride])
        pos += stride
        if f == 1:
            for i in range(ch, stride):
                line[i] = (line[i] + line[i - ch]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                b = prev[i]
                c = prev[i - ch] if i >= ch else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        elif f != 0:
            raise ValueError(f"bad filter {f}")
        rows.append(bytes(line))
        prev = line
    return w, h, ch, rows


def write_png(path: str, w: int, h: int, ch: int, rows) -> None:
    ctype = {1: 0, 3: 2, 4: 6}[ch]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    stride = w * ch
    raw = b"".join(b"\x00" + r[:stride] for r in rows)
    blob = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    open(path, "wb").write(blob)


def crop_png(src: str, dst: str, x0: int, y0: int, w: int, h: int) -> tuple[int, int]:
    """Crop rectangle [x0, x0+w) x [y0, y0+h) from src into dst."""
    sw, sh, ch, rows = read_png(src)
    assert 0 <= x0 < x0 + w <= sw and 0 <= y0 < y0 + h <= sh, "crop outside image"
    out = [r[x0 * ch:(x0 + w) * ch] for r in rows[y0:y0 + h]]
    write_png(dst, w, h, ch, out)
    return w, h
