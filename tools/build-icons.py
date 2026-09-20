#!/usr/bin/env python3
"""Render the raster app icons from the mark's geometry.

favicon.svg is the source of truth for the mark; this redraws the same
construction with PIL so the PNGs cannot drift from it. Supersampled 8x and
downsampled with LANCZOS, because the mark is all hard edges and circles.

The A is drawn, then a filled ink disc knocks it back where the O crosses it —
the system's overlap-by-knockout rule, not transparency. Nested discs then
build the ring: ink r17.5, paper r14.5, ink r6.9, vermillion r5.

    python tools/build-icons.py
"""

import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INK = (10, 10, 10, 255)
PAPER = (240, 235, 225, 255)
ORANGE = (240, 90, 0, 255)

VIEWBOX = 64.0
SS = 8  # supersample factor

# The A, from favicon.svg: M5 46.5 16.5 17.5 H22.5 L34 46.5 Z
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
    for name, size in TARGETS:
        path = os.path.join(ROOT, name)
        render(size).save(path, "PNG", optimize=True)
        print("  %-22s %4dpx  %5d bytes" % (name, size, os.path.getsize(path)))


if __name__ == "__main__":
    main()
