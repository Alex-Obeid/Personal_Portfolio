#!/usr/bin/env python3
"""Turn the supplied company logos into alpha masks for the software reel.

The reel paints a viewport-fixed gradient through each logo's alpha, the same
way the text version painted it through the glyphs. That needs the alpha to be
a clean silhouette, trimmed and consistently scaled — the originals carry very
different padding (MATLAB's ink is 44% of its canvas) and one is 3840px wide
for something that renders at about 50.

Colour is discarded by design: the mask only uses the alpha channel, so each
logo picks up the panel's own dim/accent ramp instead of introducing a fourth,
fifth and sixth colour.

    python tools/build-logo-masks.py
"""

import os
import glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Images", "Company Logos")
OUT = os.path.join(SRC, "masks")

MASK_H = 180          # plenty for a ~50px render on a 3x display

# source filename → (slug, label, knockout_light)
#
# `knockout_light` is for logos whose alpha is a solid block. Fusion's and
# AutoCAD's icons are ~97% opaque tiles with a white glyph sitting on them, so
# their alpha alone silhouettes to a featureless slab; knocking out the
# near-white pixels recovers the letterform.
#
# Deliberately NOT set for Python: 41% of its opaque pixels read as "light",
# but that is the yellow snake, and knocking it out would delete half the mark.
LOGOS = [
    ("solidworks logo.png",        "solidworks", "SolidWorks", False),
    ("Fusion logo.png",            "fusion360",  "Fusion 360", True),
    ("AutoCad_new_logo.svg.webp",  "autocad",    "AutoCAD",    True),
    ("MATLAB-logo.png",            "matlab",     "MATLAB",     False),
    ("python logo.webp",           "python",     "Python",     False),
]
LIGHT_CUTOFF = 210          # luminance above this counts as "the paper showing"


def build():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for fname, slug, label, knockout in LOGOS:
        path = os.path.join(SRC, fname)
        if not os.path.exists(path):
            print("  MISSING  " + fname)
            continue

        im = Image.open(path).convert("RGBA")
        im = im.crop(im.getchannel("A").getbbox())          # trim to the ink

        if knockout:
            lum = im.convert("L")
            a = im.getchannel("A")
            knocked = Image.new("L", im.size)
            knocked.putdata([0 if (al > 8 and l > LIGHT_CUTOFF) else al
                             for al, l in zip(a.getdata(), lum.getdata())])
            im.putalpha(knocked)

        ratio = MASK_H / im.height
        im = im.resize((max(1, round(im.width * ratio)), MASK_H), Image.LANCZOS)

        # Keep only the alpha. The mask is painted by the page, so the RGB the
        # logo happened to ship with is irrelevant — and dropping it also drops
        # the brand colours we are deliberately not using.
        mask = Image.new("RGBA", im.size, (0, 0, 0, 0))
        mask.putalpha(im.getchannel("A"))

        dest = os.path.join(OUT, slug + ".png")
        mask.save(dest, "PNG", optimize=True)
        ar = im.width / im.height
        rows.append((slug, label, im.width, im.height, ar, os.path.getsize(dest)))

    print("  %-12s %-12s %-11s %-7s %s" % ("slug", "label", "size", "aspect", "bytes"))
    for slug, label, w, h, ar, size in rows:
        print("  %-12s %-12s %4dx%-6d %-7.3f %d" % (slug, label, w, h, ar, size))

    print("\n  CSS:")
    for slug, label, w, h, ar, size in rows:
        print("    .lg-%-11s{--logo:url('Images/Company Logos/masks/%s.png');--ar:%.3f;}"
              % (slug, slug, ar))


if __name__ == "__main__":
    build()
