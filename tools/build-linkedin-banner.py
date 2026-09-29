#!/usr/bin/env python3
"""Render docs/linkedin-banner.png — 1584x396, LinkedIn's profile cover size.

The composition is the site's own hero, re-cut for a wide, short board: the
accent bar and mono kicker, the name with the surname in vermillion, a hairline,
and a mono meta row. Copy is lifted verbatim from index.html's hero rather than
rewritten, so the two cannot drift.

The right of the board steps through all three territories as full-height
bands — paper, vermillion, ink — with the mark dissolved into the ink one, the
same progression docs/banner.png uses for the README. The name stacks on the
paper ground the way index.html's hero does, surname in vermillion.

Two constraints shape the layout, and neither is visible in the file itself:

  * LinkedIn lays the circular profile photo over the BOTTOM-LEFT of the cover.
    Measured off a real render rather than a spec sheet: it is 330px across and
    its right edge lands at x=373, which is far wider than the figures usually
    quoted. SAFE_L clears it. Put anything left of that and the photo eats it.
  * The crop is not the same on mobile, which trims the sides. The bands are
    bleed, not content, so losing some of them costs nothing.

Archivo Black and DM Mono are not installed on a stock Windows box, so Arial
Black and Consolas stand in, exactly as tools/build-banner.py does for the
README artwork. The site itself always loads the real faces.

    python tools/build-linkedin-banner.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs")
OUT = os.path.join(OUT_DIR, "linkedin-banner.png")

PAPER = (240, 235, 225, 255)
INK = (10, 10, 10, 255)
ORANGE = (240, 90, 0, 255)
MUTED = (107, 100, 89, 255)
# PIL's draw replaces rather than composites, so the hairline is pre-blended:
# ink at 20% over paper, which is what --rule resolves to on this ground.
RULE = tuple(round(0.20 * a + 0.80 * b)
             for a, b in zip((10, 10, 10), (240, 235, 225))) + (255,)

W, H = 1584, 396          # LinkedIn profile cover
SS = 3                    # supersample

SAFE_L = 440              # clears the 330px avatar, whose edge is at x=373
BAND_X = 940              # where the paper ground gives way to the bands
GUTTER = 60               # between the wordmark and the first band

DISPLAY = r"C:\Windows\Fonts\ariblk.ttf"
MONO = r"C:\Windows\Fonts\consola.ttf"

# verbatim from index.html's hero
KICKER = "MECHANICAL ENGINEER \u00b7 LEBANON"
GIVEN, FAMILY = "ALEX ", "OBEID"
FOCUS = "FORMULA STUDENT \u00b7 VEHICLE DYNAMICS \u00b7 CNC MACHINING"
META = "BEIRUT, LB \u00b7 AVAILABLE 2026"


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
    """The AO monogram, from icons/favicon.svg — 64-unit board scaled to `size`."""
    k = size / 64.0
    P = lambda pts: [(x + px * k, y + py * k) for px, py in pts]
    d.rectangle([x, y, x + size, y + size], fill=ground)
    d.polygon(P([(5, 46.5), (16.5, 17.5), (22.5, 17.5), (34, 46.5)]), fill=letter)
    d.polygon(P([(19.5, 28), (23.8, 38.5), (15.2, 38.5)]), fill=ground)
    for r, col in ((17.5, ground), (14.5, letter), (6.9, ground), (5.0, dot)):
        d.ellipse([x + (44.5 - r) * k, y + (32 - r) * k,
                   x + (44.5 + r) * k, y + (32 + r) * k], fill=col)


def fit(d, text, path, target, track):
    """Largest size at which `text` still fits `target` px wide."""
    lo, hi = 8, 400
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if tracked_width(d, text, ImageFont.truetype(path, mid), track) <= target:
            lo = mid
        else:
            hi = mid - 1
    return ImageFont.truetype(path, lo)


def build():
    img = Image.new("RGBA", (W * SS, H * SS), PAPER)
    d = ImageDraw.Draw(img)
    s = lambda v: int(round(v * SS))

    # ── the three territories, stepping to the right edge ──
    band_w = (W - BAND_X) * SS // 2
    d.rectangle([s(BAND_X), 0, s(BAND_X) + band_w, H * SS], fill=ORANGE)
    d.rectangle([s(BAND_X) + band_w, 0, W * SS, H * SS], fill=INK)

    # the mark sits on the ink band, ground matching its page — so it dissolves
    # and only the letterforms read, exactly as it does in the site's nav
    m = s(120)
    mark(d, s(BAND_X) + band_w + (band_w - m) // 2, (H * SS - m) // 2,
         m, INK, PAPER, ORANGE)

    x0 = s(SAFE_L)
    right = s(BAND_X - GUTTER)

    # ── the name, stacked like the hero, fitted to the clear width ──
    f_name = fit(d, FAMILY, DISPLAY, right - x0, -0.03)
    f_name = ImageFont.truetype(DISPLAY, min(f_name.size, s(112)))
    line = int(f_name.size * 0.86)
    top = (H * SS - 2 * line) // 2 - s(6)
    tracked(d, (x0, top), GIVEN.strip(), f_name, INK, track=-0.03)
    tracked(d, (x0, top + line), FAMILY, f_name, ORANGE, track=-0.03)

    # ── kicker above, mono row below ──
    f_mono = ImageFont.truetype(MONO, s(12))
    d.rectangle([x0, s(58), x0 + s(46), s(58) + s(3)], fill=ORANGE)
    tracked(d, (x0 + s(60), s(51)), KICKER, f_mono, MUTED, track=0.20)

    # Location and availability are LinkedIn's own profile fields, so the row
    # carries only what the profile does not already say. Fitted rather than
    # set at a fixed size, but floored: shrinking it to fit made it unreadable.
    f_meta = fit(d, FOCUS, MONO, right - x0, 0.20)
    f_meta = ImageFont.truetype(MONO, max(s(10), min(f_meta.size, s(12))))
    tracked(d, (x0, s(330)), FOCUS, f_meta, MUTED, track=0.20)

    os.makedirs(OUT_DIR, exist_ok=True)
    img.resize((W, H), Image.LANCZOS).convert("RGB").save(OUT, "PNG", optimize=True)
    print("  docs/linkedin-banner.png  %dx%d  %d bytes  name %dpx"
          % (W, H, os.path.getsize(OUT), f_name.size // SS))


if __name__ == "__main__":
    build()
