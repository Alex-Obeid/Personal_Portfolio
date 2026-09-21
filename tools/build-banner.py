#!/usr/bin/env python3
"""Render docs/banner.png and docs/palette.png — the README's artwork.

Geometry and palette come from DESIGN-SYSTEM.md. Archivo Black and DM Mono are
not installed on a stock Windows box, so Arial Black and Consolas stand in for
the banner only; the site itself always loads the real faces.

    python tools/build-banner.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs")
OUT = os.path.join(OUT_DIR, "banner.png")

PAPER = (240, 235, 225, 255)
SHADE = (229, 223, 211, 255)
INK = (10, 10, 10, 255)
ORANGE = (240, 90, 0, 255)
MUTED = (107, 100, 89, 255)
# PIL's draw replaces rather than composites, so the hairline is pre-blended:
# ink at 20% over paper, which is what --rule resolves to on this ground.
RULE = tuple(round(0.20 * a + 0.80 * b) for a, b in zip((10, 10, 10), (240, 235, 225))) + (255,)

W, H = 1200, 340
SS = 3  # supersample

DISPLAY = r"C:\Windows\Fonts\ariblk.ttf"
MONO = r"C:\Windows\Fonts\consola.ttf"


def tracked(d, xy, text, font, fill, track=0.0):
    """PIL has no letter-spacing, so advance per glyph. track is in em."""
    x, y = xy
    step = track * font.size
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + step
    return x


def tracked_width(d, text, font, track=0.0):
    step = track * font.size
    return sum(d.textlength(c, font=font) for c in text) + step * max(0, len(text) - 1)


def mark(d, x, y, size, ground, letter, dot):
    """The AO monogram, from favicon.svg — 64-unit board scaled to `size`."""
    k = size / 64.0
    P = lambda pts: [(x + px * k, y + py * k) for px, py in pts]
    d.rectangle([x, y, x + size, y + size], fill=ground)
    d.polygon(P([(5, 46.5), (16.5, 17.5), (22.5, 17.5), (34, 46.5)]), fill=letter)
    d.polygon(P([(19.5, 28), (23.8, 38.5), (15.2, 38.5)]), fill=ground)
    for r, col in ((17.5, ground), (14.5, letter), (6.9, ground), (5.0, dot)):
        d.ellipse([x + (44.5 - r) * k, y + (32 - r) * k,
                   x + (44.5 + r) * k, y + (32 + r) * k], fill=col)


def build():
    img = Image.new("RGBA", (W * SS, H * SS), PAPER)
    d = ImageDraw.Draw(img)
    s = lambda v: int(round(v * SS))

    f_disp = ImageFont.truetype(DISPLAY, s(88))
    f_mono = ImageFont.truetype(MONO, s(11))
    f_mono_sm = ImageFont.truetype(MONO, s(10))

    # ── right third: the three territories as full-height bands ──
    band_x = s(858)
    band_w = (W * SS - band_x) // 3
    d.rectangle([band_x, 0, band_x + band_w, H * SS], fill=SHADE)
    d.rectangle([band_x + band_w, 0, band_x + band_w * 2, H * SS], fill=ORANGE)
    d.rectangle([band_x + band_w * 2, 0, W * SS, H * SS], fill=INK)

    # the mark sits on the ink band, ground matching its page — so it dissolves
    # and only the letterforms read, exactly as it does in the site's nav
    m = s(92)
    mark(d, band_x + band_w * 2 + (band_w - m) // 2, s(124), m, INK, PAPER, ORANGE)

    # ── accent bar + kicker ──
    d.rectangle([s(48), s(52), s(48 + 46), s(52 + 3)], fill=ORANGE)
    tracked(d, (s(108), s(45)), "MECHANICAL ENGINEER \u00b7 LEBANON",
            f_mono, MUTED, track=0.2)

    # ── wordmark ──
    tracked(d, (s(44), s(96)), "ALEX", f_disp, INK, track=-0.035)
    tracked(d, (s(44), s(186)), "OBEID", f_disp, ORANGE, track=-0.035)

    # ── baseline rule + spec line ──
    d.rectangle([s(48), s(296), band_x - s(40), s(296) + SS], fill=RULE)
    tracked(d, (s(48), s(308)), "SINGLE FILE \u00b7 NO BUILD STEP \u00b7 NO DEPENDENCIES",
            f_mono_sm, MUTED, track=0.2)

    # spec bars, top-left corner mark
    for i in range(3):
        d.rectangle([s(48 + i * 4), s(20), s(48 + i * 4) + s(2), s(29)], fill=MUTED)
    tracked(d, (s(68), s(19)), "PORTFOLIO \u00b7 01", f_mono_sm, MUTED, track=0.2)

    os.makedirs(OUT_DIR, exist_ok=True)
    img.resize((W, H), Image.LANCZOS).convert("RGB").save(OUT, "PNG", optimize=True)
    print("  docs/banner.png  %dx%d  %d bytes" % (W, H, os.path.getsize(OUT)))


def build_palette():
    """Three true swatches. Emoji squares would be both off-palette and against
    the system's own rule about emoji."""
    w, h = 900, 132
    img = Image.new("RGBA", (w * SS, h * SS), PAPER)
    d = ImageDraw.Draw(img)
    s = lambda v: int(round(v * SS))
    f = ImageFont.truetype(MONO, s(11))
    f_sm = ImageFont.truetype(MONO, s(9))

    swatches = [
        (PAPER, INK, "PAPER", "#f0ebe1", "ground"),
        (INK, PAPER, "INK", "#0a0a0a", "type"),
        (ORANGE, INK, "VERMILLION", "#f05a00", "accent"),
    ]
    cw = w // 3
    for i, (bg, fg, name, hexv, role) in enumerate(swatches):
        x0 = i * cw
        d.rectangle([s(x0), 0, s(x0 + cw), s(h)], fill=bg)
        if bg == PAPER:                      # cream needs an edge to exist
            d.rectangle([s(x0), 0, s(x0 + cw) - SS, s(h) - SS], outline=RULE, width=SS)
        tracked(d, (s(x0 + 22), s(26)), name, f, fg, track=0.2)
        tracked(d, (s(x0 + 22), s(56)), hexv, f, fg, track=0.1)
        tracked(d, (s(x0 + 22), s(88)), role.upper(), f_sm, fg, track=0.2)

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "palette.png")
    img.resize((w, h), Image.LANCZOS).convert("RGB").save(out, "PNG", optimize=True)
    print("  docs/palette.png %dx%d  %d bytes" % (w, h, os.path.getsize(out)))


if __name__ == "__main__":
    build()
    build_palette()
