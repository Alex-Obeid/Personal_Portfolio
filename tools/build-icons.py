#!/usr/bin/env python3
"""Render the raster app icons from the mark's geometry.

icons/favicon.svg is the source of truth for the mark; this redraws the same
construction with PIL so the PNGs cannot drift from it. Supersampled 8x and
downsampled with LANCZOS, because the mark is all hard edges and circles.

The A is drawn, then a filled ink disc knocks it back where the O crosses it —
the system's overlap-by-knockout rule, not transparency. Nested discs then
build the ring: ink r17.5, paper r14.5, ink r6.9, vermillion r5.

    python tools/build-icons.py
"""

import io
import os
import struct
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons")

INK = (10, 10, 10, 255)
PAPER = (240, 235, 225, 255)
ORANGE = (240, 90, 0, 255)

VIEWBOX = 64.0
SS = 8  # supersample factor

# The A, from icons/favicon.svg: M5 46.5 16.5 17.5 H22.5 L34 46.5 Z
A_OUTER = [(5, 46.5), (16.5, 17.5), (22.5, 17.5), (34, 46.5)]
# its counter: M19.5 28 23.8 38.5 H15.2 Z
A_COUNTER = [(19.5, 28), (23.8, 38.5), (15.2, 38.5)]

O_CX, O_CY = 44.5, 32.0
# radius, colour — painted in order, each disc over the last
O_DISCS = [(17.5, INK), (14.5, PAPER), (6.9, INK), (5.0, ORANGE)]

TARGETS = [
    ("apple-touch-icon.png", 180),
    ("icon-512.png", 512),
    ("favicon-48.png", 48),
    ("favicon-32.png", 32),
    ("favicon-16.png", 16),
]
ICO_SIZES = [16, 32, 48]    # what favicon.ico carries


def write_ico(path, sizes):
    """Assemble a PNG-encoded .ico by hand.

    The directory is built here rather than through PIL's ICO writer so the
    entry lengths are computed from the bytes actually written. The previous
    favicon.ico had a 48px entry whose declared length ran past the end of its
    IDAT with no IEND chunk at all — the 16 and 32 decoded, the 48 did not.
    """
    blobs = []
    for size in sizes:
        buf = io.BytesIO()
        render(size).save(buf, "PNG", optimize=True)
        blobs.append(buf.getvalue())

    offset = 6 + 16 * len(blobs)
    header = struct.pack("<HHH", 0, 1, len(blobs))
    entries, payload = b"", b""
    for size, blob in zip(sizes, blobs):
        entries += struct.pack("<BBBBHHII", size & 0xFF, size & 0xFF, 0, 0,
                               1, 32, len(blob), offset)
        payload += blob
        offset += len(blob)

    with open(path, "wb") as fh:
        fh.write(header + entries + payload)


def render(size):
    px = size * SS
    k = px / VIEWBOX

    img = Image.new("RGBA", (px, px), INK)
    d = ImageDraw.Draw(img)

    d.polygon([(x * k, y * k) for x, y in A_OUTER], fill=PAPER)
    d.polygon([(x * k, y * k) for x, y in A_COUNTER], fill=INK)

    for r, colour in O_DISCS:
        d.ellipse([(O_CX - r) * k, (O_CY - r) * k,
                   (O_CX + r) * k, (O_CY + r) * k], fill=colour)

    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, size in TARGETS:
        path = os.path.join(OUT, name)
        render(size).save(path, "PNG", optimize=True)
        print("  %-22s %4dpx  %5d bytes" % (name, size, os.path.getsize(path)))

    path = os.path.join(OUT, "favicon.ico")
    write_ico(path, ICO_SIZES)
    print("  %-22s %-7s %5d bytes"
          % ("favicon.ico", "/".join(str(s) for s in ICO_SIZES), os.path.getsize(path)))


if __name__ == "__main__":
    main()
