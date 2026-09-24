#!/usr/bin/env python3
"""Generate the Claude Design bundle in design-system/ from a single source of truth.

Ships three layers, each emitted as its own file and also inlined into every preview:

    tokens.css   custom properties only — the semantic layer and its three territories
    system.css   component classes built on those tokens
    (doc chrome) preview-only scaffolding; deliberately NOT shipped as CSS

Previews inline all three rather than linking them, so a card renders correctly no
matter how the host resolves relative paths. That duplication is the reason this
generator exists — edit here, never the generated HTML.

    python tools/build-design-system.py
"""

import io
import os
import shutil

VERSION = "1.0"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "design-system")

FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700"
         "&family=Archivo+Black&family=DM+Mono:wght@400;500&display=swap")

GRAIN = ("url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'"
         "%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85'"
         " numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25'"
         " height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E\")")


# ══════════════════════════════ LAYER 1 — TOKENS ══════════════════════════════

TOKENS = """
:root{
  /* ── Brand constants — raw values. Never reference these in a component. ── */
  --paper:#f0ebe1;
  --paper-shade:#e5dfd3;
  --ink:#0a0a0a;
  --orange:#f05a00;          /* fills, large display, artwork */
  --orange-deep:#ab4000;     /* small accent TEXT on cream — AA, see Accessibility */
  --orange2:#ff7a1a;
  --warm-muted:#6b6459;

  /* ── Semantic layer — redefined per territory. Build against these. ── */
  --bg:var(--paper);
  --fg:var(--ink);
  --fg-2:var(--warm-muted);
  --accent:var(--orange);
  --accent-text:var(--orange-deep);
  --on-accent:var(--ink);
  --surface:var(--paper-shade);
  --rule:rgba(10,10,10,.20);
  --rule-strong:rgba(10,10,10,.85);

  /* ── Motion ── */
  --snap:.16s cubic-bezier(.4,0,.2,1);
  --territory-fade:.65s cubic-bezier(.4,0,.2,1);
}

/* Vermillion — orange ground. Accent flips to ink; orange on orange never happens. */
[data-territory="vermillion"]{
  --bg:var(--orange);
  --fg:var(--ink);
  --fg-2:rgba(10,10,10,.62);
  --accent:var(--ink);
  --accent-text:var(--ink);
  --on-accent:var(--orange);
  --surface:rgba(10,10,10,.07);
  --rule:rgba(10,10,10,.30);
  --rule-strong:rgba(10,10,10,.88);
}

/* Ink — near-black ground. Full-strength vermillion is safe on ink at any size. */
[data-territory="ink"]{
  --bg:var(--ink);
  --fg:var(--paper);
  --fg-2:rgba(240,235,225,.55);
  --accent:var(--orange);
  --accent-text:var(--orange);
  --on-accent:var(--ink);
  --surface:#161513;
  --rule:rgba(240,235,225,.20);
  --rule-strong:rgba(240,235,225,.85);
}
"""


# ══════════════════════════════ LAYER 2 — SYSTEM ══════════════════════════════

SYSTEM = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:auto;}
body{
  background:var(--bg);color:var(--fg);
  font-family:'Archivo',system-ui,sans-serif;font-weight:400;
  -webkit-font-smoothing:antialiased;
  transition:background var(--territory-fade),color var(--territory-fade);
}

/* Paper grain — multiply so it reads as tooth on cream, not haze on black */
.grain::after{
  content:'';position:fixed;inset:0;background-image:GRAIN;
  mix-blend-mode:multiply;pointer-events:none;z-index:9999;opacity:.14;
}

/* ── Type scale: extreme contrast, nothing in between ── */
.t-display{font-family:'Archivo Black',sans-serif;font-size:clamp(3.4rem,13vw,12rem);line-height:.86;letter-spacing:-.035em;text-transform:uppercase;}
.t-title{font-family:'Archivo Black',sans-serif;font-size:clamp(2.2rem,7.5vw,5.5rem);line-height:.9;letter-spacing:-.03em;text-transform:uppercase;}
.t-numeral{font-family:'Archivo Black',sans-serif;font-size:clamp(4.5rem,19vw,15rem);line-height:.8;letter-spacing:-.045em;}
.t-label{font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;}

/* ── Territories — full-bleed colour panels ── */
.terr{
  position:relative;background:var(--bg);color:var(--fg);
  padding:118px 48px 96px;
  /* clip, not hidden: overflow:hidden creates a scroll container and kills
     position:sticky on anything pinned inside. */
  overflow:clip;
}
.terr-min{min-height:100vh;display:flex;flex-direction:column;justify-content:center;}

/* Drop-in slot for artwork — position with inline offsets so it crops on an edge */
.gfx{position:absolute;pointer-events:none;z-index:0;}

/* Spec mark — the small tagged micro-label */
.spec-mark{
  position:absolute;z-index:1;display:inline-flex;align-items:center;gap:7px;
  font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--fg-2);
}
.spec-mark .sm-bars{display:inline-flex;gap:2px;}
.spec-mark .sm-bars i{width:2px;height:9px;background:currentColor;display:block;}

/* ── Inversion: the entire hover vocabulary. No shadows, no transforms. ── */
.inv{
  border:1px solid var(--rule-strong);background:transparent;color:var(--fg);
  transition:background var(--snap),color var(--snap),border-color var(--snap);
}
.inv:hover,.inv:focus-visible{background:var(--accent);color:var(--on-accent);border-color:var(--accent);outline:none;}
.inv:active{background:var(--fg);color:var(--bg);border-color:var(--fg);}
.inv-solid{background:var(--accent);color:var(--on-accent);border-color:var(--accent);}
.inv-solid:hover,.inv-solid:focus-visible{background:var(--fg);color:var(--bg);border-color:var(--fg);}

/* ── Button ── */
.btn{
  display:inline-flex;align-items:center;gap:10px;padding:15px 30px;
  font-family:'DM Mono',monospace;font-size:.66rem;letter-spacing:.18em;
  text-transform:uppercase;text-decoration:none;cursor:pointer;
  border:1px solid var(--rule-strong);background:transparent;color:var(--fg);
  transition:background var(--snap),color var(--snap),border-color var(--snap);
}
.btn:hover,.btn:focus-visible{background:var(--accent);color:var(--on-accent);border-color:var(--accent);outline:none;}
.btn:active{background:var(--fg);color:var(--bg);border-color:var(--fg);}
.btn-primary{background:var(--accent);color:var(--on-accent);border-color:var(--accent);}
.btn-primary:hover,.btn-primary:focus-visible{background:var(--fg);color:var(--bg);border-color:var(--fg);}
.btn-ghost{background:transparent;color:var(--fg);}

/* ── Tag / pill ── */
.tag{
  display:inline-flex;align-items:center;gap:8px;padding:5px 10px;
  font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:.15em;
  text-transform:uppercase;border:1px solid var(--rule-strong);
  color:var(--fg);background:transparent;
  transition:background var(--snap),color var(--snap),border-color var(--snap);
}
.tag:hover{background:var(--accent);color:var(--on-accent);border-color:var(--accent);}
.pill{
  display:inline-flex;align-items:center;gap:8px;padding:8px 13px;
  font-family:'DM Mono',monospace;font-size:.66rem;letter-spacing:.1em;
  text-transform:uppercase;border:1px solid var(--rule-strong);color:var(--fg);
  transition:background var(--snap),color var(--snap),border-color var(--snap);
}
.pill:hover{background:var(--accent);color:var(--on-accent);border-color:var(--accent);}
.pill svg,.tag svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;}

/* ── Field: no box, one keyline ── */
.field{display:flex;flex-direction:column;gap:7px;}
.field label{font-family:'DM Mono',monospace;font-size:.56rem;letter-spacing:.18em;text-transform:uppercase;color:var(--fg-2);}
.field input,.field textarea{
  background:transparent;border:0;border-bottom:1px solid var(--rule-strong);
  color:var(--fg);font-family:'Archivo',sans-serif;font-size:.95rem;
  padding:10px 2px;outline:none;resize:none;transition:border-color var(--snap);
}
.field input::placeholder,.field textarea::placeholder{color:var(--fg-2);}
.field input:focus,.field textarea:focus{border-bottom-color:var(--accent);}

/* ── Accent bar — the system's only ornament ── */
.bar{display:block;width:46px;height:2px;background:var(--accent);flex:none;}

/* ── Photography ── */
.plate{border:1px solid var(--rule-strong);display:block;width:100%;object-fit:cover;}
.plate-mono{filter:grayscale(1) contrast(1.06);}
.fig-cap{display:flex;justify-content:space-between;margin-top:8px;color:var(--fg-2);}

@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation:none !important;transition:none !important;}
}
"""


# ══════════════════════════ LAYER 3 — PREVIEW CHROME ══════════════════════════
# Documentation scaffolding. Never shipped as CSS; previews only.

DOC = """
.ds-page{min-height:100vh;display:flex;flex-direction:column;background:var(--paper);}
.ds-main{flex:1;display:flex;flex-direction:column;min-height:0;}
.ds-main > *{flex:1;}

/* Title block — the drawing-sheet footer every card carries */
.ds-block{
  flex:none;background:var(--ink);color:var(--paper);
  border-top:1px solid var(--ink);
}
.ds-block-row{display:grid;grid-template-columns:58px 1fr 2fr 74px;align-items:stretch;}
.ds-cell{
  padding:9px 14px;border-right:1px solid rgba(240,235,225,.22);
  display:flex;flex-direction:column;justify-content:center;gap:3px;min-width:0;
}
.ds-cell:last-child{border-right:0;}
.ds-k{font-family:'DM Mono',monospace;font-size:.44rem;letter-spacing:.2em;text-transform:uppercase;color:rgba(240,235,225,.5);}
.ds-v{font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:var(--paper);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.ds-v.name{font-family:'Archivo Black',sans-serif;font-size:.78rem;letter-spacing:-.01em;}
.ds-v.ix{font-size:.9rem;color:var(--orange);letter-spacing:.04em;}
.ds-code{
  border-top:1px solid rgba(240,235,225,.22);padding:10px 14px;
  font-family:'DM Mono',monospace;font-size:.58rem;line-height:1.75;
  color:rgba(240,235,225,.82);white-space:pre-wrap;word-break:break-word;
  max-height:88px;overflow:auto;
}
.ds-code b{color:var(--orange);font-weight:400;}

/* Section kicker used inside specimens */
.ds-kicker{display:flex;align-items:center;gap:12px;color:var(--fg-2);margin-bottom:18px;}
.ds-note{font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.16em;text-transform:uppercase;color:var(--fg-2);}
.ds-row{display:flex;flex-wrap:wrap;gap:16px;align-items:center;}
.ds-stack{display:flex;flex-direction:column;gap:10px;}
.ds-rule{height:1px;background:var(--rule);margin:20px 0;}

/* Specimens sit in panels that fill the card, not the viewport */
.terr{padding:40px 38px 34px;}
.fill{min-height:100%;}
"""


# ═════════════════════════════════ PAGE MODEL ═════════════════════════════════

PAGES = []


def page(path, group, name, subtitle, viewport, body, usage, extra_css=""):
    PAGES.append(dict(path=path, group=group, name=name, subtitle=subtitle,
                      viewport=viewport, body=body, usage=usage,
                      extra_css=extra_css))


def kicker(text):
    return ('<div class="ds-kicker"><span class="bar"></span>'
            '<span class="t-label">%s</span></div>' % text)


# ──────────────────────────────── FOUNDATIONS ────────────────────────────────

RULES = [
    "Three colours, no more. Cream, ink, vermillion.",
    "Colour arrives in full-bleed panels, never scattered accents.",
    "No depth. No shadows, gradients, blur, radius or glass.",
    "Hover inverts colour. That is the whole interaction vocabulary.",
    "Type is huge or tiny. Nothing comfortable in between.",
    "Three faces: Archivo Black, Archivo, DM Mono.",
    "Labels are uppercase mono at .2em tracking. Always.",
    "Hairlines, not borders. A rule divides; it does not contain.",
    "Everything sits on a grid and may bleed off the edge.",
    "Asymmetry over centring. Centre only a numeral or a mark.",
]

page("foundations/overview.html", "Foundations", "Overview — the ten rules",
     "The system compressed to ten lines", "1280x760",
     '<section class="terr fill" data-territory="ink">'
     + '<div class="ov-head">'
     + '<span class="t-label">Alex Obeid</span>'
     + '<span class="t-label">Design Language &middot; Rev ' + VERSION + '</span>'
     + '</div>'
     + '<h1 class="t-title ov-title">Ten<br><span style="color:var(--accent)">Rules</span></h1>'
     + '<ol class="ov-list">'
     + "".join('<li><span class="n">%02d</span><span class="r">%s</span></li>' % (i + 1, r)
               for i, r in enumerate(RULES))
     + '</ol></section>',
     "Start here. Every other card is detail on one of these ten lines.",
     extra_css="""
.terr{display:grid;grid-template-columns:minmax(0,260px) minmax(0,1fr);
      grid-template-rows:auto 1fr;column-gap:48px;align-content:start;}
.ov-head{grid-column:1/-1;display:flex;justify-content:space-between;
         color:var(--fg-2);border-bottom:1px solid var(--rule);padding-bottom:12px;margin-bottom:26px;}
.ov-title{grid-column:1;align-self:start;}
.ov-list{grid-column:2;list-style:none;display:grid;grid-template-columns:1fr 1fr;
         gap:0 34px;align-content:start;}
.ov-list li{display:grid;grid-template-columns:30px 1fr;gap:12px;
            padding:10px 0;border-bottom:1px solid var(--rule);align-items:baseline;}
.ov-list .n{font-family:'DM Mono',monospace;font-size:.56rem;letter-spacing:.16em;color:var(--accent);}
.ov-list .r{font-size:.82rem;line-height:1.5;color:var(--fg-2);}
@media(max-width:900px){.terr{grid-template-columns:1fr;}.ov-title{margin-bottom:20px;}
  .ov-list{grid-column:1;grid-template-columns:1fr;}}
""")


def terr_swatches(terr, label, rows):
    attr = ' data-territory="%s"' % terr if terr else ""
    cells = "".join(
        '<div class="sw-row"><span class="chip" style="background:%s;%s"></span>'
        '<span class="ds-note">%s</span><span class="ds-note val">%s</span></div>'
        % (var, border, tok, val) for tok, var, val, border in rows)
    return ('<section class="terr t-block"%s>%s<div class="sw-set">%s</div>'
            '<p class="t-demo">Primary type in <b>--fg</b>, meta in '
            '<span style="color:var(--fg-2)">--fg-2</span>, one word in '
            '<span style="color:var(--accent-text)">--accent-text</span>.</p></section>'
            % (attr, kicker(label), cells))


page("foundations/colour-territories.html", "Foundations", "Colour territories",
     "Paper / Vermillion / Ink — one component, three grounds", "1280x700",
     '<div class="wrap">'
     + terr_swatches("", "Paper — default", [
         ("--bg", "var(--bg)", "#f0ebe1", "border:1px solid var(--rule-strong)"),
         ("--fg", "var(--fg)", "#0a0a0a", ""),
         ("--accent", "var(--accent)", "#f05a00", ""),
         ("--accent-text", "var(--accent-text)", "#ab4000", ""),
         ("--surface", "var(--surface)", "#e5dfd3", "border:1px solid var(--rule)"),
     ])
     + terr_swatches("vermillion", "Vermillion", [
         ("--bg", "var(--bg)", "#f05a00", ""),
         ("--fg", "var(--fg)", "#0a0a0a", ""),
         ("--accent", "var(--accent)", "= --ink", ""),
         ("--fg-2", "var(--fg-2)", "ink 62%", ""),
         ("--surface", "var(--surface)", "ink 7%", "border:1px solid var(--rule)"),
     ])
     + terr_swatches("ink", "Ink", [
         ("--bg", "var(--bg)", "#0a0a0a", "border:1px solid var(--rule)"),
         ("--fg", "var(--fg)", "#f0ebe1", ""),
         ("--accent", "var(--accent)", "#f05a00", ""),
         ("--fg-2", "var(--fg-2)", "paper 55%", ""),
         ("--surface", "var(--surface)", "#161513", "border:1px solid var(--rule)"),
     ])
     + '</div>',
     '&lt;section class="terr" <b>data-territory="ink"</b>&gt;\n'
     '  &lt;!-- components inside adapt automatically --&gt;\n'
     '&lt;/section&gt;',
     extra_css="""
.wrap{display:grid;grid-template-columns:repeat(3,1fr);min-height:100%;}
.t-block{display:flex;flex-direction:column;}
.sw-set{display:flex;flex-direction:column;gap:0;margin-bottom:22px;}
.sw-row{display:grid;grid-template-columns:34px 1fr auto;gap:12px;align-items:center;
        padding:7px 0;border-bottom:1px solid var(--rule);}
.chip{width:34px;height:20px;display:block;}
.sw-row .val{opacity:.75;}
.t-demo{font-size:.8rem;line-height:1.6;color:var(--fg-2);max-width:28ch;margin-top:auto;}
.t-demo b{color:var(--fg);font-weight:700;}
@media(max-width:950px){.wrap{grid-template-columns:1fr;}}
""")


CONTRAST = [
    ("Paper", "--fg on --bg", "16.66", "AAA", "ok"),
    ("Paper", "--fg-2 on --bg", "4.92", "AA", "ok"),
    ("Paper", "--fg on --surface", "14.92", "AAA", "ok"),
    ("Paper", "--accent-text on --bg", "5.10", "AA", "ok"),
    ("Paper", "--on-accent on --accent", "5.81", "AA", "ok"),
    ("Paper", "raw --orange on --bg", "2.87", "FAIL", "bad"),
    ("Vermillion", "--fg on --bg", "5.81", "AA", "ok"),
    ("Vermillion", "--fg-2 on --bg", "3.40", "AA Large", "warn"),
    ("Vermillion", "--on-accent on --accent", "5.81", "AA", "ok"),
    ("Ink", "--fg on --bg", "16.66", "AAA", "ok"),
    ("Ink", "--fg-2 on --bg", "5.44", "AA", "ok"),
    ("Ink", "--accent on --bg", "5.81", "AA", "ok"),
    ("Ink", "--fg on --surface", "15.36", "AAA", "ok"),
]

page("foundations/accessibility.html", "Foundations", "Accessibility & contrast",
     "Measured WCAG 2.1 ratios, including where the brand fails", "1280x820",
     '<section class="terr fill">'
     + kicker("Measured contrast &middot; WCAG 2.1")
     + '<table class="ct"><thead><tr>'
       '<th class="ds-note">Territory</th><th class="ds-note">Pair</th>'
       '<th class="ds-note">Ratio</th><th class="ds-note">Grade</th></tr></thead><tbody>'
     + "".join('<tr class="%s"><td class="ds-note">%s</td><td class="ds-note pair">%s</td>'
               '<td class="ratio">%s</td><td class="ds-note grade">%s</td></tr>'
               % (cls, t, p, r, g) for t, p, r, g, cls in CONTRAST)
     + '</tbody></table>'
     + '<div class="warn-box">'
       '<span class="t-label" style="color:var(--accent-text)">The one real trap</span>'
       '<p>Full-strength <b>--orange</b> on cream measures <b>2.87:1</b> — it fails AA for '
       'normal text and misses even the 3:1 large-text floor. Use <b>--accent-text</b> '
       '(#ab4000, same hue and saturation, 5.10:1) for any accent TEXT on a cream ground. '
       'Reserve raw --orange for fills, rules, artwork and display type set as decoration. '
       'On ink, full-strength orange is safe at any size.</p>'
       '</div>'
     + '<p class="ds-note foot">Ratios computed from the token values; rgba secondaries '
       'composited over their ground first. Non-text marks (rules, bars) are exempt from '
       'text minima but still target 3:1 where they carry meaning.</p>'
     + '</section>',
     'color:var(<b>--accent-text</b>);  /* accent text on cream — AA */\n'
     'background:var(<b>--accent</b>);  /* fills, bars, artwork — any ground */',
     extra_css="""
.ct{width:100%;border-collapse:collapse;margin-bottom:26px;}
.ct th{text-align:left;padding:0 0 10px;border-bottom:1px solid var(--rule-strong);}
.ct td{padding:9px 0;border-bottom:1px solid var(--rule);vertical-align:baseline;}
.ct .pair{color:var(--fg);}
.ct .ratio{font-family:'Archivo Black',sans-serif;font-size:.95rem;letter-spacing:-.01em;width:80px;}
.ct .grade{width:90px;}
.ct tr.bad .ratio,.ct tr.bad .grade{color:var(--accent-text);}
.ct tr.bad{background:var(--surface);}
.ct tr.warn .grade{opacity:.8;}
.warn-box{border:1px solid var(--rule-strong);padding:18px 20px;margin-bottom:20px;
          display:flex;flex-direction:column;gap:8px;}
.warn-box p{font-size:.84rem;line-height:1.65;color:var(--fg-2);max-width:78ch;}
.warn-box b{color:var(--fg);font-weight:700;}
.foot{line-height:1.9;max-width:80ch;}
""")


page("foundations/type-scale.html", "Foundations", "Type scale",
     "Archivo Black / Archivo / DM Mono — deliberately polarised", "1280x900",
     '<section class="terr fill">'
     + kicker("Huge or tiny, nothing between")
     + """
    <div class="spec">
      <div class="t-display">Aa</div>
      <div class="meta ds-note"><span>.t-display</span><span>Archivo Black</span>
        <span>clamp(3.4rem,13vw,12rem)</span><span>lh .86 &middot; ls -.035em</span></div>
    </div>
    <div class="spec">
      <div class="t-title">Section Title</div>
      <div class="meta ds-note"><span>.t-title</span><span>Archivo Black</span>
        <span>clamp(2.2rem,7.5vw,5.5rem)</span><span>lh .9 &middot; ls -.03em</span></div>
    </div>
    <div class="spec">
      <div class="t-numeral">04</div>
      <div class="meta ds-note"><span>.t-numeral</span><span>Archivo Black</span>
        <span>clamp(4.5rem,19vw,15rem)</span><span>lh .8 &middot; ls -.045em</span></div>
    </div>
    <div class="spec">
      <p class="body-demo">Body is Archivo at 1.02rem, line-height 1.55, capped at 46ch.
        Left-aligned, ragged right — never centred, never set large.</p>
      <div class="meta ds-note"><span>body</span><span>Archivo 400</span>
        <span>1.02rem &middot; lh 1.55</span><span>max 46ch</span></div>
    </div>
    <div class="spec">
      <div class="t-label">Label &middot; Spec Tag &middot; Index</div>
      <div class="meta ds-note"><span>.t-label</span><span>DM Mono</span>
        <span>.62rem</span><span>ls .2em &middot; uppercase</span></div>
    </div>
    <p class="ds-note foot">Display sizes are vw-driven so type fills its measure at every
      width. There is no h3-sized step: a thing is either a title or a label.</p>
  </section>""",
     '&lt;h1 class="<b>t-display</b>"&gt;Alex&lt;/h1&gt;\n'
     '&lt;span class="<b>t-label</b>"&gt;Mechanical Engineering&lt;/span&gt;',
     extra_css="""
.spec{border-top:1px solid var(--rule);padding:20px 0 16px;display:grid;
      grid-template-columns:1fr auto;gap:28px;align-items:baseline;}
.spec .meta{justify-self:end;text-align:right;color:var(--fg-2);}
.spec .meta span{display:block;}
.body-demo{font-size:1.02rem;line-height:1.55;color:var(--fg-2);max-width:46ch;}
.foot{border-top:1px solid var(--rule);padding-top:16px;line-height:1.9;max-width:70ch;}
""")


page("foundations/space-and-grid.html", "Foundations", "Space & grid",
     "Rhythm, panel padding, breakpoints, zero radius", "1280x820",
     '<section class="terr fill">'
     + kicker("Spacing rhythm")
     + '<div class="steps">'
     + "".join('<figure><div style="height:%dpx"></div><span>%d</span></figure>' % (n, n)
               for n in (6, 8, 12, 18, 26, 30, 48, 56, 96, 118))
     + '</div>'
     + kicker("Asymmetric grid &middot; minmax(0,1fr) auto")
     + '<div class="cols"><div class="f"></div><div class="x"></div></div>'
     + kicker("Breakpoints")
     + '<div class="bps">'
     + "".join('<div><span class="bp">%d</span><span class="ds-note">%s</span></div>' % (w, note)
               for w, note in ((1000, "masonry 3 to 2"), (860, "detail to one column"),
                               (768, "nav collapses"), (580, "masonry to 1")))
     + '</div>'
     + '<p class="ds-note foot">Panel padding is 118px 48px 96px, tightening to 96px 22px 72px '
       'below 768px — top exceeds bottom so panels hang from their top edge. Radius is 0 '
       'everywhere. Panels are full-bleed and use overflow:clip so artwork can crop.</p>'
     + '</section>',
     '.terr{padding:<b>118px 48px 96px</b>; overflow:<b>clip</b>;}\n'
     '.grid{grid-template-columns:<b>minmax(0,1fr) auto</b>;}',
     extra_css="""
.steps{display:flex;align-items:flex-end;gap:10px;margin:4px 0 30px;}
.steps div{background:var(--accent);width:24px;}
.steps span{display:block;margin-top:8px;font-family:'DM Mono',monospace;font-size:.5rem;
            letter-spacing:.1em;color:var(--fg-2);text-align:center;}
.steps figure{display:flex;flex-direction:column;align-items:center;}
.cols{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:56px;align-items:end;
      border:1px solid var(--rule);padding:22px;margin-bottom:30px;}
.cols .f{height:92px;background:var(--surface);border:1px solid var(--rule);}
.cols .x{width:150px;height:150px;background:var(--surface);border:1px solid var(--rule-strong);}
.bps{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--rule);
     margin-bottom:24px;}
.bps div{border-bottom:1px solid var(--rule);border-right:1px solid var(--rule);
         padding:14px 14px 14px 0;display:flex;flex-direction:column;gap:5px;}
.bps div:last-child{border-right:0;}
.bp{font-family:'Archivo Black',sans-serif;font-size:1.7rem;letter-spacing:-.03em;}
.foot{line-height:1.9;max-width:78ch;}
""")


MARK_ITEMS = [
    ('<div class="d-hair"></div>', "--rule &middot; 1px &middot; divides"),
    ('<div class="d-key"></div>', "--rule-strong &middot; 1px &middot; an edge"),
    ('<span class="bar"></span>', "accent bar &middot; 2px &times; 46px"),
    ('<span class="spec-mark st"><i class="sm-bars"><i></i><i></i><i></i></i>FIG. 03</span>',
     ".spec-mark &middot; micro-label"),
    ('<div class="d-frame"></div>', "--surface + keyline"),
]


def marks_panel(terr, label):
    attr = ' data-territory="%s"' % terr if terr else ""
    items = "".join('<div class="item">%s<span class="ds-note">%s</span></div>' % (d, n)
                    for d, n in MARK_ITEMS)
    return '<section class="terr"%s>%s%s</section>' % (attr, kicker(label), items)


page("foundations/rules-and-marks.html", "Foundations", "Rules & marks",
     "Hairline, keyline, accent bar, spec mark", "1280x620",
     '<div class="wrap">'
     + marks_panel("", "On paper")
     + marks_panel("vermillion", "On vermillion")
     + marks_panel("ink", "On ink")
     + '</div>',
     '&lt;span class="<b>spec-mark</b>"&gt;&lt;i class="sm-bars"&gt;'
     '&lt;i&gt;&lt;/i&gt;&lt;i&gt;&lt;/i&gt;&lt;i&gt;&lt;/i&gt;&lt;/i&gt;FIG. 03&lt;/span&gt;',
     extra_css="""
.wrap{display:grid;grid-template-columns:repeat(3,1fr);min-height:100%;}
.terr{display:flex;flex-direction:column;gap:22px;}
.item{display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center;min-height:26px;}
.d-hair{height:1px;background:var(--rule);}
.d-key{height:1px;background:var(--rule-strong);}
.d-frame{height:56px;background:var(--surface);border:1px solid var(--rule-strong);}
.spec-mark.st{position:static;}
@media(max-width:950px){.wrap{grid-template-columns:1fr;}}
""")


page("foundations/what-breaks-it.html", "Foundations", "What breaks the language",
     "Side-by-side tells", "1280x780",
     '<section class="terr fill">'
     + kicker("Left is wrong. Right is the system.")
     + """
    <div class="pair">
      <div class="half no"><span class="hl">Never</span>
        <button class="bad-btn">Get started</button>
        <span class="ds-note">radius &middot; gradient &middot; shadow &middot; sentence case</span></div>
      <div class="half yes"><span class="hl">Always</span>
        <button class="btn btn-primary">Get Started</button>
        <span class="ds-note">square &middot; flat &middot; mono &middot; uppercase &middot; tracked</span></div>
    </div>
    <div class="pair">
      <div class="half no"><span class="hl">Never</span>
        <div class="bad-card">A floating card with a margin<br>on a neutral background</div></div>
      <div class="half yes"><span class="hl">Always</span>
        <div class="good-card">A full-bleed panel, keylined,<br>content on an inset grid</div></div>
    </div>
    <p class="ds-note foot">Also disqualifying: pure #000 or #fff &middot; a fourth colour &middot;
      centred body text &middot; display type at default tracking &middot; hover states that lift,
      scale or glow &middot; icons from a library &middot; emoji as icons &middot; illustration with
      perspective or shading.</p>
  </section>""",
     "/* the tell is almost always depth or radius */\n"
     "border-radius:<b>0</b>; box-shadow:<b>none</b>; background:<b>flat</b>;",
     extra_css="""
.pair{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--rule-strong);margin-bottom:20px;}
.half{padding:24px 22px;display:flex;flex-direction:column;gap:13px;min-height:140px;}
.half.no{border-right:1px solid var(--rule-strong);background:var(--surface);}
.hl{font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.18em;text-transform:uppercase;}
.no .hl{color:var(--fg-2);}
.yes .hl{color:var(--accent-text);}
.bad-btn{align-self:flex-start;padding:12px 22px;border-radius:24px;border:0;
  background:linear-gradient(180deg,#ff8a3d,#f05a00);color:#fff;
  box-shadow:0 6px 16px rgba(0,0,0,.28);font-family:'Archivo',sans-serif;font-size:.9rem;}
.bad-card{border-radius:14px;background:#fff;box-shadow:0 8px 24px rgba(0,0,0,.14);
  padding:16px;text-align:center;font-size:.8rem;color:#555;}
.good-card{border:1px solid var(--rule-strong);padding:16px;font-size:.8rem;color:var(--fg-2);}
.foot{line-height:2;max-width:86ch;}
""")


# ─────────────────────────────────── BRAND ───────────────────────────────────

FAVICON_SVG = """<svg class="favi" viewBox="0 0 64 64" role="img" aria-label="Alex Obeid">
        <rect width="64" height="64" fill="#0a0a0a"/>
        <path fill="#f0ebe1" fill-rule="evenodd" d="M32 8 L59 57 L5 57 Z M32 27 L45 57 L19 57 Z"/>
        <path fill="#f0ebe1" d="M15 41 H49 V48 H15 Z"/>
        <rect x="48" y="7" width="10" height="10" fill="#f05a00"/>
      </svg>"""

page("brand/wordmark.html", "Brand", "Wordmark & mark",
     "Alex.Obeid — the vermillion dot", "1280x620",
     '<section class="terr fill">'
     + kicker("Wordmark")
     + '<div class="mark-row"><div class="wordmark">Alex<span>.</span>Obeid</div>'
     + FAVICON_SVG + '</div>'
     + '<div class="ds-rule"></div>'
     + '<div class="mark-row"><div class="wordmark-sm">Alex<span>.</span>Obeid</div>'
       '<span class="ds-note">nav lock-up &middot; 1.22rem &middot; ls -.02em</span></div>'
     + '<p class="ds-note foot">Archivo Black, uppercase, -.02em. Words in --fg, the dot in '
       '--accent. The dot is the smallest unit of the identity; the favicon squares it.<br>'
       'The favicon letterform is drawn as paths, never &lt;text&gt; — favicons render outside '
       'the page context and a webfont would silently fall back to a system face.</p>'
     + '</section>',
     '&lt;a class="nav-logo"&gt;Alex&lt;span&gt;<b>.</b>&lt;/span&gt;Obeid&lt;/a&gt;\n'
     '.nav-logo span{color:var(<b>--accent</b>);}',
     extra_css="""
.terr{display:flex;flex-direction:column;justify-content:center;gap:34px;}
.mark-row{display:flex;align-items:center;gap:50px;flex-wrap:wrap;}
.wordmark{font-family:'Archivo Black',sans-serif;font-size:clamp(2.2rem,6.5vw,4.2rem);
          letter-spacing:-.02em;text-transform:uppercase;line-height:1;}
.wordmark span{color:var(--accent);}
.wordmark-sm{font-family:'Archivo Black',sans-serif;font-size:1.22rem;letter-spacing:-.02em;
             text-transform:uppercase;}
.wordmark-sm span{color:var(--accent);}
.favi{width:88px;height:88px;flex:none;}
.foot{line-height:2;max-width:72ch;}
""")


# ───────────────────────────────── COMPONENTS ────────────────────────────────

BTN_SET = """
      <div class="ds-row">
        <button class="btn btn-primary">Primary Action</button>
        <button class="btn">Secondary</button>
        <a class="btn" href="#">With Icon
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
      </div>"""


def btn_panel(terr, label, note):
    attr = ' data-territory="%s"' % terr if terr else ""
    return ('<section class="terr"%s>%s%s<p class="ds-note nb">%s</p></section>'
            % (attr, kicker(label), BTN_SET, note))


page("components/buttons.html", "Components", "Buttons",
     "Primary / secondary / icon — hover to invert", "1280x560",
     '<div class="wrap">'
     + btn_panel("", "Paper", "hover &rarr; accent fill<br>active &rarr; fg fill")
     + btn_panel("vermillion", "Vermillion", "accent is ink here —<br>orange on orange never happens")
     + btn_panel("ink", "Ink", "one component,<br>three grounds, no variants")
     + '</div>',
     '&lt;button class="<b>btn btn-primary</b>"&gt;Primary Action&lt;/button&gt;\n'
     '&lt;button class="<b>btn</b>"&gt;Secondary&lt;/button&gt;',
     extra_css="""
.wrap{display:grid;grid-template-columns:repeat(3,1fr);min-height:100%;}
.terr{display:flex;flex-direction:column;gap:22px;}
.nb{line-height:2;margin-top:auto;}
@media(max-width:950px){.wrap{grid-template-columns:1fr;}}
""")


TAG_SET = """
      <div class="ds-row" style="margin-bottom:26px;">
        <span class="tag">SolidWorks</span><span class="tag">FEA</span>
        <span class="tag">CFD</span><span class="tag">GD&amp;T</span>
      </div>
      <div class="ds-row">
        <span class="pill"><svg viewBox="0 0 24 24"><path d="M4 18l4-6 4 3 6-9"/></svg>FEA</span>
        <span class="pill"><svg viewBox="0 0 24 24"><path d="M3 9c3-2.5 6 2.5 9 0s6 2.5 9 0M3 15c3-2.5 6 2.5 9 0s6 2.5 9 0"/></svg>CFD</span>
        <span class="pill"><svg viewBox="0 0 24 24"><circle cx="7" cy="17" r="2"/><circle cx="17" cy="7" r="2"/><path d="M8.5 15.5l7-7"/></svg>Kinematics</span>
      </div>"""

page("components/tags-and-pills.html", "Components", "Tags & pills",
     "Mono, square, keylined — .tag and .pill", "1280x520",
     '<div class="wrap">'
     + '<section class="terr">' + kicker("Tag .58rem / .15em &middot; Pill .66rem / .1em") + TAG_SET + '</section>'
     + '<section class="terr" data-territory="ink">' + kicker("On ink") + TAG_SET + '</section>'
     + '</div>',
     '&lt;span class="<b>tag</b>"&gt;SolidWorks&lt;/span&gt;\n'
     '&lt;span class="<b>pill</b>"&gt;&lt;svg&gt;&hellip;&lt;/svg&gt;FEA&lt;/span&gt;',
     extra_css="""
.wrap{display:grid;grid-template-columns:1fr 1fr;min-height:100%;}
@media(max-width:800px){.wrap{grid-template-columns:1fr;}}
""")


page("components/form-fields.html", "Components", "Form fields",
     "No box — one keyline that accents on focus", "1280x620",
     '<section class="terr fill">'
     + kicker("Fields &middot; click one to see focus")
     + """
    <form class="form" onsubmit="return false">
      <div class="field"><label for="n">Name</label><input id="n" placeholder="Your name"></div>
      <div class="field"><label for="e">Email</label><input id="e" type="email" placeholder="you@domain.com"></div>
      <div class="field"><label for="m">Message</label><textarea id="m" rows="3" placeholder="What are you building?"></textarea></div>
      <div class="ds-row"><button class="btn btn-primary" type="submit">Send Message</button></div>
    </form>
    <p class="ds-note foot">Inputs have no box and no radius — one 1px bottom keyline.
      Focus moves the keyline to --accent. Labels are mono, uppercase, .18em.</p>
  </section>""",
     '&lt;div class="<b>field</b>"&gt;\n'
     '  &lt;label for="n"&gt;Name&lt;/label&gt;&lt;input id="n"&gt;\n'
     '&lt;/div&gt;',
     extra_css="""
.form{max-width:500px;display:flex;flex-direction:column;gap:22px;}
.foot{margin-top:28px;line-height:1.9;max-width:64ch;}
""")


NAV_CSS = """
.wrap{display:flex;flex-direction:column;min-height:100%;}
.wrap > div{flex:1;display:flex;flex-direction:column;}
.navbar{display:flex;align-items:center;justify-content:space-between;
  padding:16px 38px;border-bottom:1px solid var(--rule);background:var(--bg);color:var(--fg);}
.nav-logo{font-family:'Archivo Black',sans-serif;font-size:1.22rem;letter-spacing:-.02em;
  text-transform:uppercase;color:var(--fg);text-decoration:none;}
.nav-logo span{color:var(--accent);}
.nav-links{display:flex;gap:28px;list-style:none;}
.nav-links a{display:inline-flex;align-items:center;gap:8px;text-decoration:none;
  font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--fg-2);transition:color var(--snap);}
.nav-links a.active,.nav-links a:hover{color:var(--accent-text);}
.nav-links svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;}
.bed{flex:1;display:flex;align-items:center;padding:0 38px;background:var(--bg);}
"""


def navbar(active):
    ico = {
        "Home": '<svg viewBox="0 0 24 24"><path d="M3 10.5L12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/></svg>',
        "Projects": '<svg viewBox="0 0 24 24"><path d="M4 12h16M4 16h10M4 8h12"/></svg>',
        "CV": '<svg viewBox="0 0 24 24"><path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/></svg>',
    }
    items = "".join('<li><a href="#"%s>%s<span>%s</span></a></li>'
                    % (' class="active"' if k == active else "", v, k)
                    for k, v in ico.items())
    return ('<nav class="navbar"><a href="#" class="nav-logo">Alex<span>.</span>Obeid</a>'
            '<ul class="nav-links">%s</ul></nav>' % items)


page("components/navigation.html", "Components", "Navigation",
     "Fixed bar that adopts the territory beneath it", "1280x660",
     '<div class="wrap">'
     + '<div>' + navbar("Home") + '<div class="bed"><span class="ds-note">Paper ground</span></div></div>'
     + '<div data-territory="vermillion">' + navbar("Projects")
     + '<div class="bed"><span class="ds-note">Vermillion &middot; accent flips to ink</span></div></div>'
     + '<div data-territory="ink">' + navbar("CV")
     + '<div class="bed"><span class="ds-note">Ink &middot; accent returns to vermillion</span></div></div>'
     + '</div>',
     'updateNavTerritory();  /* reads the panel under the bar */\n'
     'transition:background var(<b>--territory-fade</b>);',
     extra_css=NAV_CSS)


page("components/stat-rows.html", "Components", "Stat rows",
     "Oversized numeral against right-aligned meta", "1280x700",
     '<section class="terr fill" data-territory="ink">'
     + '<div class="sh"><span class="t-label">Selected figures</span>'
       '<span class="t-label">2026</span></div>'
     + """
    <div class="stat-row"><div class="stat-num">12<span class="unit">:1</span></div>
      <div class="stat-meta"><strong>Gear reduction</strong>Planetary set, three stages, printed and tested</div></div>
    <div class="stat-row"><div class="stat-num">340<span class="unit">MPa</span></div>
      <div class="stat-meta"><strong>Peak von Mises</strong>FEA under worst-case torque, 1.8 safety factor</div></div>
    <div class="stat-row"><div class="stat-num">05</div>
      <div class="stat-meta"><strong>Axis CNC</strong>Mill, turning and 5-axis toolpath experience</div></div>
  </section>""",
     '&lt;div class="<b>stat-row</b>"&gt;\n'
     '  &lt;div class="<b>stat-num</b>"&gt;12&lt;span class="unit"&gt;:1&lt;/span&gt;&lt;/div&gt;\n'
     '  &lt;div class="<b>stat-meta</b>"&gt;&lt;strong&gt;Gear reduction&lt;/strong&gt;&hellip;&lt;/div&gt;\n'
     '&lt;/div&gt;',
     extra_css="""
.terr{display:flex;flex-direction:column;justify-content:center;}
.sh{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;color:var(--fg-2);}
.stat-row{border-top:1px solid var(--rule);padding:16px 0 10px;display:grid;
          grid-template-columns:auto 1fr;gap:28px;align-items:center;}
.stat-row:last-child{border-bottom:1px solid var(--rule);}
.stat-num{color:var(--fg);font-family:'Archivo Black',sans-serif;
          font-size:clamp(2.6rem,8vw,6rem);line-height:.8;letter-spacing:-.045em;}
.stat-num .unit{font-size:.28em;letter-spacing:.02em;vertical-align:super;color:var(--accent);}
.stat-meta{justify-self:end;text-align:right;color:var(--fg-2);max-width:26ch;
           font-size:.79rem;line-height:1.5;}
.stat-meta strong{display:block;color:var(--fg);font-weight:700;font-size:.9rem;margin-bottom:3px;}
""")


page("components/project-cards.html", "Components", "Project cards",
     "Masonry bricks — flat panels, size and colour classes", "1280x800",
     '<section class="terr fill">'
     + kicker("Masonry &middot; columns 3 / 2 / 1 &middot; hover a brick")
     + """
    <div class="masonry">
      <article class="brick tall"><div class="brick-visual"><span class="brick-num">03</span></div>
        <div class="brick-body"><h3 class="brick-title">Planetary Gearbox</h3>
          <p class="brick-desc">Three-stage reduction, printed, instrumented and tested.</p>
          <span class="brick-cta">Open Project
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span></div></article>
      <article class="brick orange short"><div class="brick-visual"><span class="brick-num">01</span></div>
        <div class="brick-body"><h3 class="brick-title">Suspension Rig</h3>
          <p class="brick-desc">Kinematics sweep and camber study.</p>
          <span class="brick-cta">Open Project
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span></div></article>
      <article class="brick ink sq"><div class="brick-visual"><span class="brick-num">02</span></div>
        <div class="brick-body"><h3 class="brick-title">Duct Flow Study</h3>
          <p class="brick-desc">CFD on an intake plenum, pressure-loss driven.</p>
          <span class="brick-cta">Open Project
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span></div></article>
    </div>
    <p class="ds-note foot">Sizes: tall 3:4 &middot; wide 16:9 &middot; sq 1:1 &middot; short 4:3
      &middot; mini 3:2. Each visual sets --v-bg / --v-fg so its number and marks adapt.</p>
  </section>""",
     '&lt;article class="<b>brick tall ink</b>"&gt;\n'
     '  &lt;div class="brick-visual"&gt;&lt;span class="brick-num"&gt;03&lt;/span&gt;&lt;/div&gt;\n'
     '&lt;/article&gt;',
     extra_css="""
.masonry{columns:3;column-gap:16px;}
.brick{break-inside:avoid;margin-bottom:16px;border:1px solid var(--rule-strong);
       cursor:pointer;background:var(--bg);}
.brick-visual{--v-bg:var(--paper-shade);--v-fg:var(--ink);background:var(--v-bg);color:var(--v-fg);
  position:relative;transition:background var(--snap),color var(--snap);}
.brick.ink .brick-visual{--v-bg:var(--ink);--v-fg:var(--paper);}
.brick.orange .brick-visual{--v-bg:var(--orange);--v-fg:var(--ink);}
.tall .brick-visual{aspect-ratio:3/4;} .sq .brick-visual{aspect-ratio:1/1;}
.short .brick-visual{aspect-ratio:4/3;}
.brick-num{position:absolute;top:11px;left:13px;font-family:'DM Mono',monospace;
           font-size:.54rem;letter-spacing:.18em;}
.brick-body{padding:13px;border-top:1px solid var(--rule-strong);}
.brick-title{font-family:'Archivo Black',sans-serif;font-size:1rem;letter-spacing:-.02em;
             text-transform:uppercase;margin-bottom:5px;line-height:1.1;}
.brick-desc{font-size:.78rem;line-height:1.55;color:var(--fg-2);margin-bottom:9px;}
.brick-cta{display:inline-flex;align-items:center;gap:7px;font-family:'DM Mono',monospace;
           font-size:.55rem;letter-spacing:.18em;text-transform:uppercase;color:var(--accent-text);}
.brick:hover .brick-visual{--v-bg:var(--accent);--v-fg:var(--on-accent);}
.foot{margin-top:18px;line-height:1.9;}
@media(max-width:1000px){.masonry{columns:2;}}
@media(max-width:580px){.masonry{columns:1;}}
""")


page("components/gallery.html", "Components", "Gallery & captions",
     "Image cells and the labelled placeholder tile", "1280x640",
     '<section class="terr fill">'
     + kicker("Detail gallery &middot; 4:3 cells")
     + '<div class="gal">'
     + '<div class="gal-cell"><svg viewBox="0 0 120 90" class="ph" aria-hidden="true">'
       '<rect width="120" height="90" fill="var(--surface)"/>'
       '<path d="M0 68 L34 40 L58 60 L82 34 L120 68 V90 H0 Z" fill="currentColor" opacity=".18"/>'
       '<circle cx="90" cy="22" r="9" fill="currentColor" opacity=".3"/></svg></div>'
     + '<div class="gal-cell empty">CFD Pressure Map</div>'
     + '<div class="gal-cell empty">Assembly Section</div>'
     + '<div class="gal-cell"><svg viewBox="0 0 120 90" class="ph" aria-hidden="true">'
       '<rect width="120" height="90" fill="var(--surface)"/>'
       '<circle cx="60" cy="45" r="26" fill="none" stroke="currentColor" stroke-width="3" opacity=".35"/>'
       '<circle cx="60" cy="45" r="10" fill="none" stroke="currentColor" stroke-width="3" opacity=".35"/></svg></div>'
     + '</div>'
     + '<p class="ds-note foot">Gallery entries ending .png/.jpg/.jpeg/.gif/.webp/.svg render as '
       '&lt;img&gt;; any other string becomes a labelled placeholder tile. The same convention '
       'governs heroImage — omit it and the hero shows the panel ground with the num watermark.</p>'
     + '</section>',
     "gallery: [\n"
     "  'images/gearbox/<b>photo-1.jpg</b>',   // renders as an image\n"
     "  '<b>CFD Pressure Map</b>',             // renders as a labelled tile\n"
     "]",
     extra_css="""
.gal{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;}
.gal-cell{background:var(--surface);border:1px solid var(--rule-strong);aspect-ratio:4/3;
  display:flex;align-items:center;justify-content:center;overflow:hidden;
  font-family:'DM Mono',monospace;font-size:.56rem;letter-spacing:.18em;
  color:var(--fg-2);text-transform:uppercase;text-align:center;padding:8px;
  transition:background var(--snap),color var(--snap),border-color var(--snap);}
.gal-cell.empty:hover{background:var(--accent);color:var(--on-accent);border-color:var(--accent);}
.ph{width:100%;height:100%;display:block;color:var(--fg);}
.foot{margin-top:22px;line-height:1.9;max-width:82ch;}
@media(max-width:800px){.gal{grid-template-columns:repeat(2,1fr);}}
""")


# ─────────────────────────────────── PATTERNS ─────────────────────────────────

page("patterns/hero-panel.html", "Patterns", "Hero panel",
     "The canonical composition — asymmetric, bottom-aligned, cropped", "1280x780",
     """
  <section class="terr fill">
    <span class="spec-mark corner"><i class="sm-bars"><i></i><i></i><i></i></i>FIG. 01</span>
    <svg class="gfx" viewBox="0 0 200 200" style="left:-86px;bottom:-72px;width:270px;opacity:.45;" aria-hidden="true">
      <circle cx="100" cy="100" r="86" fill="none" stroke="currentColor" stroke-width="2"/>
      <circle cx="100" cy="100" r="44" fill="none" stroke="currentColor" stroke-width="2"/>
      <path d="M100 0 V200 M0 100 H200" stroke="currentColor" stroke-width="1" opacity=".3"/>
    </svg>
    <div class="hero-grid">
      <div class="hero-kicker"><span class="bar"></span><span class="t-label">Mechanical Engineering &middot; Beirut</span></div>
      <h1 class="hero-name t-display"><span class="ln">Alex</span><span class="ln accent">Obeid</span></h1>
      <p class="hero-bio">Body copy sits at 46ch in secondary type. One accent word in the
        headline, never more. The portrait keeps its own column at every width.</p>
      <div class="hero-meta"><span class="t-label">LAU &middot; 2026</span>
        <span class="t-label">CAD / FEA / CFD</span></div>
      <div class="cta-row"><a class="btn btn-primary" href="#">View Projects</a>
        <a class="btn" href="#">Download CV</a></div>
      <figure class="hero-figure">
        <div class="plate ph"><span class="ds-note">Portrait &middot; grayscale(1)</span></div>
        <figcaption class="fig-cap"><span class="t-label">Fig. A</span><span class="t-label">2026</span></figcaption>
      </figure>
    </div>
  </section>""",
     'grid-template-areas:\n'
     '  "kicker figure" "name figure" "bio figure" "meta figure" "<b>cta figure</b>";\n'
     '/* the portrait never drops below the name */',
     extra_css="""
.terr{display:flex;flex-direction:column;justify-content:center;padding:52px 46px;}
.hero-grid{position:relative;z-index:1;display:grid;grid-template-columns:minmax(0,1fr) auto;
  column-gap:48px;align-items:end;
  grid-template-areas:"kicker figure" "name figure" "bio figure" "meta figure" "cta figure";}
.hero-kicker{grid-area:kicker;display:flex;align-items:center;gap:12px;color:var(--fg-2);margin-bottom:18px;}
.hero-name{grid-area:name;margin:0 0 22px;font-size:clamp(3rem,10vw,7rem);}
.hero-name .ln{display:block;}
.hero-name .accent{color:var(--accent-text);}
.hero-bio{grid-area:bio;max-width:46ch;font-size:.98rem;line-height:1.55;color:var(--fg-2);margin-bottom:24px;}
.hero-meta{grid-area:meta;display:flex;flex-wrap:wrap;gap:0 26px;color:var(--fg-2);margin-bottom:24px;}
.cta-row{grid-area:cta;display:flex;gap:14px;flex-wrap:wrap;}
.hero-figure{grid-area:figure;align-self:end;position:relative;width:clamp(180px,20vw,250px);}
.hero-figure .ph{aspect-ratio:5/6;background:var(--surface);display:flex;
  align-items:center;justify-content:center;text-align:center;padding:10px;}
.corner{right:38px;top:34px;}
""")


page("patterns/colour-inversion.html", "Patterns", "Colour inversion",
     "The entire interaction vocabulary — rest / hover / active", "1280x660",
     '<section class="terr fill">'
     + kicker("No shadows. No transforms. Colour inverts.")
     + """
    <div class="seq">
      <div class="state s-rest"><span class="lbl">Rest</span><span class="val">Transparent</span><span class="lbl">border --rule-strong</span></div>
      <div class="state s-hover"><span class="lbl">Hover / focus-visible</span><span class="val">Accent fill</span><span class="lbl">colour --on-accent</span></div>
      <div class="state s-active"><span class="lbl">Active</span><span class="val">FG fill</span><span class="lbl">colour --bg</span></div>
    </div>
    <div class="ds-rule"></div>
    <div class="ds-row" style="gap:44px;">
      <div class="ds-stack"><span class="t-label">--snap</span>
        <span class="ds-note">.16s cubic-bezier(.4,0,.2,1) &middot; every state change</span></div>
      <div class="ds-stack"><span class="t-label">--territory-fade</span>
        <span class="ds-note">.65s cubic-bezier(.4,0,.2,1) &middot; ground under the nav</span></div>
    </div>
    <p class="ds-note liv">Live — hover these:</p>
    <div class="ds-row"><button class="btn">Ghost</button>
      <button class="btn btn-primary">Solid</button><span class="tag">Tag</span></div>
  </section>""",
     '.inv:hover{background:var(<b>--accent</b>);color:var(<b>--on-accent</b>);}\n'
     '.inv:active{background:var(<b>--fg</b>);color:var(<b>--bg</b>);}',
     extra_css="""
.terr{display:flex;flex-direction:column;justify-content:center;gap:24px;}
.seq{display:grid;grid-template-columns:repeat(3,minmax(0,210px));gap:16px;}
.state{border:1px solid var(--rule-strong);padding:22px 20px;display:flex;flex-direction:column;gap:12px;}
.s-hover{background:var(--accent);color:var(--on-accent);border-color:var(--accent);}
.s-active{background:var(--fg);color:var(--bg);border-color:var(--fg);}
.state .lbl{font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.18em;
            text-transform:uppercase;opacity:.75;}
.state .val{font-family:'Archivo Black',sans-serif;font-size:1.05rem;letter-spacing:-.02em;
            text-transform:uppercase;}
.liv{margin-top:4px;}
""")


page("patterns/page-sweep.html", "Patterns", "Page sweep",
     "Three staggered bars — the only page transition", "1280x600",
     '<section class="terr fill">'
     + kicker("Linear, hard-edged, no easing curve")
     + '<div class="track"><div class="lyr l1"></div><div class="lyr l2"></div><div class="lyr l3"></div></div>'
     + '<div class="tl">'
     + "".join('<div><span class="ms">%s</span><span class="ds-note">%s</span></div>' % (m, n)
               for m, n in (("900", "ms per layer, linear"), ("140", "ms stagger between layers"),
                            ("730", "ms &mdash; swap content here"), ("1180", "ms &mdash; release the lock")))
     + '</div>'
     + '<p class="ds-note foot">Order is vermillion, ink, paper. Nothing scales, fades slowly, '
       'springs or bounces. Skipped entirely under prefers-reduced-motion.</p>'
     + '</section>',
     'navigate(target);            // plays the sweep\n'
     'applySection(target);        // called at <b>730ms</b>, when cover is total',
     extra_css="""
.terr{display:flex;flex-direction:column;justify-content:center;gap:30px;}
.track{position:relative;height:104px;border:1px solid var(--rule);overflow:hidden;background:var(--surface);}
.lyr{position:absolute;top:0;bottom:0;width:130%;left:-130%;animation:sweep 2.6s linear infinite;}
.l1{background:var(--orange);}
.l2{background:var(--ink);animation-delay:.14s;}
.l3{background:var(--paper);animation-delay:.28s;}
@keyframes sweep{0%{transform:translateX(0)}35%{transform:translateX(100%)}100%{transform:translateX(100%)}}
.tl{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--rule);}
.tl div{border-bottom:1px solid var(--rule);border-right:1px solid var(--rule);
        padding:14px 14px 14px 0;display:flex;flex-direction:column;gap:5px;}
.tl div:last-child{border-right:0;}
.ms{font-family:'Archivo Black',sans-serif;font-size:1.5rem;letter-spacing:-.03em;}
.foot{line-height:1.9;max-width:76ch;}
""")


page("patterns/loading-sequence.html", "Patterns", "Loading sequence",
     "Rule, mask-reveal wordmark, spec line — then a wipe", "1280x600",
     '<section class="terr fill" data-territory="ink">'
     + kicker("Intro &middot; replays every 4s")
     + '<div class="stage">'
       '<div class="lock">'
       '<div class="lrule"></div>'
       '<div class="mask"><span class="lmark">Alex<span>.</span>Obeid</span></div>'
       '<div class="lspec">Portfolio &middot; Rev ' + VERSION + ' &middot; Beirut</div>'
       '</div></div>'
     + '<div class="tl">'
     + "".join('<div><span class="ms">%s</span><span class="ds-note">%s</span></div>' % (m, n)
               for m, n in (("1620", "ms &mdash; closing"), ("2080", "ms &mdash; done"),
                            ("2780", "ms &mdash; hidden")))
     + '</div>'
     + '<p class="ds-note foot">A rule draws across the wordmark&rsquo;s measure, the wordmark '
       'rises from behind it as a mask reveal, then a mono spec line fades in. On close the '
       'wordmark drops back below the rule and the panel slides up to wipe the hero into view. '
       'Skipped entirely under prefers-reduced-motion.</p>'
     + '</section>',
     "/* the stack sizes itself to the wordmark so the rule matches its measure */\n"
     "animation:<b>markRise</b> 580ms cubic-bezier(.16,.84,.26,1) 290ms forwards;",
     extra_css="""
.terr{display:flex;flex-direction:column;justify-content:center;gap:26px;}
.stage{border:1px solid var(--rule);min-height:190px;display:flex;align-items:center;
       justify-content:center;background:var(--bg);}
.lock{display:inline-flex;flex-direction:column;align-items:stretch;}
.lrule{height:2px;background:var(--accent);width:0;animation:draw 620ms cubic-bezier(.4,0,.2,1) infinite;}
.mask{overflow:hidden;}
.lmark{display:block;font-family:'Archivo Black',sans-serif;font-size:2.1rem;letter-spacing:-.02em;
  text-transform:uppercase;color:var(--fg);transform:translateY(110%);
  animation:rise 4s cubic-bezier(.16,.84,.26,1) infinite;}
.lmark span{color:var(--accent);}
.lspec{font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.2em;text-transform:uppercase;
  color:var(--fg-2);margin-top:9px;opacity:0;animation:fade 4s linear infinite;}
@keyframes draw{0%{width:0}100%{width:100%}}
@keyframes rise{0%,6%{transform:translateY(110%)}18%,74%{transform:translateY(0)}
                88%,100%{transform:translateY(110%)}}
@keyframes fade{0%,20%{opacity:0}30%,72%{opacity:1}82%,100%{opacity:0}}
.tl{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--rule);}
.tl div{border-bottom:1px solid var(--rule);border-right:1px solid var(--rule);
        padding:12px 14px 12px 0;display:flex;flex-direction:column;gap:4px;}
.tl div:last-child{border-right:0;}
.ms{font-family:'Archivo Black',sans-serif;font-size:1.4rem;letter-spacing:-.03em;}
.foot{line-height:1.9;max-width:84ch;}
""")


page("patterns/skills-carousel.html", "Patterns", "Skills carousel",
     "The scroll-pinned cylinder, and why the angle is not 360/n", "1280x700",
     '<section class="terr fill">'
     + kicker("Geometry &middot; an arc, not a closed circle")
     + '<div class="lay">'
     + """
      <svg viewBox="0 0 300 300" class="dia" aria-hidden="true">
        <circle cx="150" cy="150" r="108" fill="none" stroke="currentColor" stroke-width="1" opacity=".22"/>
        <path d="M150 150 L150 30" stroke="currentColor" stroke-width="1" opacity=".3"/>
        <path d="M150 150 L254 90" stroke="currentColor" stroke-width="1" opacity=".3"/>
        <path d="M150 42 A108 108 0 0 1 243 96" fill="none" stroke="var(--accent)" stroke-width="2"/>
        <!-- leader line out to the label, drawing-sheet convention -->
        <path d="M206 56 L250 34" stroke="currentColor" stroke-width="1" opacity=".45"/>
        <text x="254" y="32" class="dlab">32&deg;</text>
        <g stroke="currentColor" stroke-width="2" fill="none">
          <rect x="96" y="28" width="108" height="20" opacity="1"/>
          <rect x="96" y="70" width="108" height="20" opacity=".62"/>
          <rect x="96" y="112" width="108" height="20" opacity=".34"/>
          <rect x="96" y="154" width="108" height="20" opacity=".18"/>
          <rect x="96" y="196" width="108" height="20" opacity=".09"/>
        </g>
        <text x="150" y="284" class="dlab" text-anchor="middle">cos&sup3;&#8901;&#8308; falloff from front</text>
      </svg>
      <div class="notes">
        <dl>
          <dt class="t-label">CYL_ANGLE</dt>
          <dd>32&deg; — <b>not</b> 360/n. Tighter spacing keeps about five copies inside the
              visible &plusmn;90&deg;, which is what creates the stacked cascade. A closed
              circle would space them out and kill it.</dd>
          <dt class="t-label">CYL_TIGHTNESS</dt>
          <dd>1.45 — multiplies the measured size to get the radius. This is the overlap control.</dd>
          <dt class="t-label">Opacity</dt>
          <dd>Falls off as cos&sup3;&#8901;&#8308; of the angle from front, so the lead copy
              reads solid and the rest recede.</dd>
          <dt class="t-label">Sizing</dt>
          <dd>One uniform size for every skill, scaled until the <b>longest</b> line fills 92%
              of the stage. The longest string caps the size for all of them.</dd>
          <dt class="t-label">Scroll length</dt>
          <dd>Wrapper height is 100vh + (n&minus;1) &times; --cyl-step. Change the multiplier
              when you add a skill.</dd>
        </dl>
      </div>
    </div>""",
     'transform:rotateX(i * <b>CYL_ANGLE</b>) translateZ(radius);\n'
     '/* driven from <b>ssApply()</b>, not the scroll event — see Momentum note */',
     extra_css="""
.lay{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:40px;align-items:center;}
.dia{width:100%;max-width:300px;color:var(--fg);}
.dlab{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:.14em;
      text-transform:uppercase;fill:var(--fg-2);}
.notes dl{display:grid;grid-template-columns:auto;gap:0;}
.notes dt{padding-top:12px;border-top:1px solid var(--rule);color:var(--accent-text);}
.notes dd{font-size:.8rem;line-height:1.6;color:var(--fg-2);padding:5px 0 12px;max-width:62ch;}
.notes dd b{color:var(--fg);font-weight:700;}
@media(max-width:900px){.lay{grid-template-columns:1fr;}}
""")


# ─────────────────────────────────── GRAPHICS ─────────────────────────────────

ICON_CELLS = [
    ("Arrow", '<path d="M5 12h14M12 5l7 7-7 7"/>'),
    ("Back", '<path d="M19 12H5M12 19l-7-7 7-7"/>'),
    ("Download", '<path d="M12 4v15M6 13l6 6 6-6"/>'),
    ("Home", '<path d="M3 10.5L12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>'),
    ("Document", '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/><path d="M10 12h6M10 15h6"/>'),
    ("Mail", '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>'),
    ("Location", '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>'),
    ("FEA", '<path d="M4 18l4-6 4 3 6-9"/>'),
    ("CFD", '<path d="M3 9c3-2.5 6 2.5 9 0s6 2.5 9 0M3 15c3-2.5 6 2.5 9 0s6 2.5 9 0"/>'),
    ("Kinematics", '<circle cx="7" cy="17" r="2"/><circle cx="17" cy="7" r="2"/><path d="M8.5 15.5l7-7"/>'),
    ("Surface", '<path d="M4 17c2-9 14-9 16 0"/><circle cx="4" cy="17" r="1.6"/><circle cx="12" cy="10.2" r="1.6"/><circle cx="20" cy="17" r="1.6"/>'),
    ("Machining", '<path d="M9 3h6v9l-3 4-3-4V3zM4 21h16"/>'),
]

page("graphics/icons.html", "Graphics", "Icons",
     "24x24, stroke 2, round caps, currentColor", "1280x600",
     '<div class="wrap"><section class="terr">'
     + kicker("Icon set &middot; hover a cell")
     + '<div class="grid">'
     + "".join('<div class="cell"><svg viewBox="0 0 24 24" aria-hidden="true">%s</svg>'
               '<span>%s</span></div>' % (d, n) for n, d in ICON_CELLS)
     + '</div></section>'
     + '<section class="terr" data-territory="ink">'
     + kicker("Spec")
     + '<ul class="rl">'
       '<li><b>viewBox</b> 0 0 24 24</li><li><b>fill</b> none</li>'
       '<li><b>stroke</b> currentColor</li><li><b>stroke-width</b> 2</li>'
       '<li><b>linecap</b> round</li><li><b>rendered</b> 12&ndash;18px</li></ul>'
     + '<div class="ds-rule"></div>'
     + '<ul class="rl"><li>Geometric and open. No filled glyphs, no duotone, no detail that '
       'dies below 16px.</li><li>Never an icon library. Never emoji.</li></ul>'
     + '</section></div>',
     '&lt;svg viewBox="<b>0 0 24 24</b>" fill="<b>none</b>" stroke="<b>currentColor</b>"\n'
     '     stroke-width="<b>2</b>" stroke-linecap="round"&gt;&lt;path d="&hellip;"/&gt;&lt;/svg&gt;',
     extra_css="""
.wrap{display:grid;grid-template-columns:2fr 1fr;min-height:100%;}
.terr{display:flex;flex-direction:column;}
.grid{display:grid;grid-template-columns:repeat(6,1fr);border-top:1px solid var(--rule);
      border-left:1px solid var(--rule);}
.cell{border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);aspect-ratio:1/1;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:9px;
  transition:background var(--snap),color var(--snap);}
.cell:hover{background:var(--accent);color:var(--on-accent);}
.cell svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:2;
          stroke-linecap:round;stroke-linejoin:round;}
.cell span{font-family:'DM Mono',monospace;font-size:.44rem;letter-spacing:.14em;
           text-transform:uppercase;opacity:.7;}
.rl{display:flex;flex-direction:column;gap:11px;list-style:none;}
.rl li{font-family:'DM Mono',monospace;font-size:.55rem;letter-spacing:.14em;
       text-transform:uppercase;color:var(--fg-2);line-height:1.7;}
.rl li b{color:var(--fg);}
@media(max-width:900px){.wrap{grid-template-columns:1fr;}.grid{grid-template-columns:repeat(4,1fr);}}
""")


ARTWORK_SVG = """<svg class="gfx" viewBox="0 0 240 240" style="left:-96px;bottom:-86px;width:300px;" aria-hidden="true">
        <path d="M0 120 H240 M120 0 V240" stroke="currentColor" stroke-width="1" opacity=".22"/>
        <circle cx="120" cy="120" r="78" fill="none" stroke="currentColor" stroke-width="2"/>
        <circle cx="120" cy="120" r="34" fill="none" stroke="currentColor" stroke-width="2"/>
        <g stroke="currentColor" stroke-width="2">
          <path d="M120 42 V26"/><path d="M175 65 L186 54"/><path d="M198 120 H214"/>
          <path d="M175 175 L186 186"/><path d="M120 198 V214"/><path d="M65 175 L54 186"/>
          <path d="M42 120 H26"/><path d="M65 65 L54 54"/>
        </g>
        <rect x="112" y="14" width="16" height="16" fill="var(--accent)"/>
      </svg>"""


def art_panel(terr, label, rules):
    attr = ' data-territory="%s"' % terr if terr else ""
    items = "".join("<li>%s</li>" % r for r in rules)
    return ('<section class="terr"%s>%s<div class="stage">%s'
            '<span class="spec-mark cap"><i class="sm-bars"><i></i><i></i><i></i></i>Fig. 02</span>'
            '</div><ul class="rl">%s</ul></section>' % (attr, kicker(label), ARTWORK_SVG, items))


page("graphics/artwork.html", "Graphics", "Artwork & the .gfx slot",
     "currentColor, flat, orthographic, cropped by the panel", "1280x740",
     '<div class="wrap">'
     + art_panel("", "Same file, paper ground", [
         "<b>currentColor and var(--accent) only</b> — never hex. One file works on all three grounds.",
         "<b>Two tones, three at most.</b> No gradients, no opacity ramps for depth, no filter.",
         "<b>Flat and orthographic.</b> Elevation, section, plan. Isometric only if load-bearing.",
     ])
     + art_panel("ink", "Same file, ink ground", [
         "<b>Constructed, not sketched.</b> Circles, arcs, straight runs, 15&deg; increments.",
         "<b>Overlap by knockout</b>, not transparency — fill-rule evenodd or an over-painted shape.",
         "<b>Crop against the panel edge.</b> Artwork fully inside with even margins reads as stock.",
     ])
     + '</div>',
     '&lt;svg class="<b>gfx</b>" viewBox="0 0 240 240"\n'
     '     style="left:-96px; bottom:-86px; width:300px;"&gt;\n'
     '  &lt;circle stroke="<b>currentColor</b>"/&gt;&lt;rect fill="<b>var(--accent)</b>"/&gt;\n'
     '&lt;/svg&gt;',
     extra_css="""
.wrap{display:grid;grid-template-columns:1fr 1fr;min-height:100%;}
.terr{display:flex;flex-direction:column;}
.stage{position:relative;flex:1;min-height:230px;border:1px solid var(--rule);
       overflow:clip;margin-bottom:18px;}
.cap{right:12px;bottom:10px;}
.rl{display:flex;flex-direction:column;gap:10px;list-style:none;}
.rl li{font-size:.76rem;line-height:1.6;color:var(--fg-2);padding-left:15px;position:relative;}
.rl li::before{content:'';position:absolute;left:0;top:.6em;width:7px;height:2px;background:var(--accent);}
.rl li b{color:var(--fg);font-weight:700;}
@media(max-width:850px){.wrap{grid-template-columns:1fr;}}
""")


page("graphics/photography.html", "Graphics", "Photography",
     "Grayscale portraits, colour reserved for renders", "1280x620",
     '<section class="terr fill">'
     + kicker("Treatment")
     + '<div class="row">'
     + '<figure class="f"><div class="plate mono-demo"><span class="ds-note">Portrait</span></div>'
       '<figcaption class="fig-cap"><span class="t-label">Fig. A</span>'
       '<span class="t-label">grayscale(1)</span></figcaption></figure>'
     + '<figure class="f"><div class="plate proc-demo"><span class="ds-note">Process photo</span></div>'
       '<figcaption class="fig-cap"><span class="t-label">Fig. B</span>'
       '<span class="t-label">contrast(1.06)</span></figcaption></figure>'
     + '<figure class="f"><div class="plate render-demo"><span class="ds-note" '
       'style="color:var(--paper)">Project render</span></div>'
       '<figcaption class="fig-cap"><span class="t-label">Fig. C</span>'
       '<span class="t-label">colour kept</span></figcaption></figure>'
     + '</div>'
     + '<p class="ds-note foot">Portraits and process photos are grayscale(1) contrast(1.06) '
       'behind a 1px --rule-strong keyline, no radius, object-fit:cover. Colour is reserved for '
       'project renders, where the render&rsquo;s own colour is the content. Captions sit beneath '
       'in mono, split left/right across the image&rsquo;s measure.<br><br>'
       '<b>Deploy note:</b> image paths are case-sensitive on Linux-backed hosts. A mismatch '
       '404s in production with no error locally.</p>'
     + '</section>',
     '&lt;img class="<b>plate plate-mono</b>" src="images/headshot/a.jpg" alt=""&gt;\n'
     '.plate-mono{filter:<b>grayscale(1) contrast(1.06)</b>;}',
     extra_css="""
.row{display:grid;grid-template-columns:repeat(3,minmax(0,220px));gap:26px;}
.f{display:flex;flex-direction:column;}
.plate{aspect-ratio:5/6;display:flex;align-items:center;justify-content:center;}
.mono-demo{background:var(--surface);}
.proc-demo{background:repeating-linear-gradient(45deg,var(--surface),var(--surface) 8px,
           rgba(10,10,10,.05) 8px,rgba(10,10,10,.05) 16px);}
.render-demo{background:var(--ink);}
.foot{margin-top:26px;line-height:1.9;max-width:86ch;}
.foot b{color:var(--fg);}
""")


# ═══════════════════════════════════ SHELL ════════════════════════════════════

SHELL = """<!-- @dsCard group="{group}" name="{name}" subtitle="{subtitle}" viewport="{viewport}" -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} &mdash; Alex Obeid Design System</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<style>
/* ── tokens.css ── */
{tokens}
/* ── system.css ── */
{system}
/* ── preview chrome (not shipped) ── */
{doc}
/* ── this card ── */
{extra}
</style>
</head>
<body class="grain">
<div class="ds-page">
  <main class="ds-main">
{body}
  </main>
  <footer class="ds-block">
    <div class="ds-block-row">
      <div class="ds-cell"><span class="ds-k">Sheet</span><span class="ds-v ix">{index}</span></div>
      <div class="ds-cell"><span class="ds-k">Group</span><span class="ds-v">{group}</span></div>
      <div class="ds-cell"><span class="ds-k">Component</span><span class="ds-v name">{name}</span></div>
      <div class="ds-cell"><span class="ds-k">Rev</span><span class="ds-v">{version}</span></div>
    </div>
    <div class="ds-code">{usage}</div>
  </footer>
</div>
</body>
</html>
"""

GROUP_ORDER = ["Foundations", "Brand", "Components", "Patterns", "Graphics"]


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)

    system = SYSTEM.replace("GRAIN", GRAIN)
    ordered = sorted(PAGES, key=lambda p: (GROUP_ORDER.index(p["group"]),
                                           PAGES.index(p)))

    for i, p in enumerate(ordered, 1):
        dest = os.path.join(OUT, p["path"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        html = SHELL.format(
            group=p["group"], name=p["name"], subtitle=p["subtitle"],
            viewport=p["viewport"], fonts=FONTS,
            tokens=TOKENS.strip(), system=system.strip(),
            doc=DOC.strip(), extra=p["extra_css"].strip(),
            body=p["body"].strip(), usage=p["usage"],
            index="%02d" % i, version=VERSION)
        io.open(dest, "w", encoding="utf-8", newline="\n").write(html)
        print("  %02d  %-38s %s" % (i, p["path"], p["group"]))

    header = ("/* Alex Obeid — Design Language, Rev %s\n"
              "   Generated by tools/build-design-system.py. Do not edit. */\n\n" % VERSION)

    io.open(os.path.join(OUT, "tokens.css"), "w", encoding="utf-8", newline="\n").write(
        header + "/* Custom properties only. Build components against the semantic\n"
                 "   layer (--bg/--fg/--accent...), never the brand constants. */\n"
        + TOKENS.lstrip())

    io.open(os.path.join(OUT, "system.css"), "w", encoding="utf-8", newline="\n").write(
        header + "/* Component classes. Requires tokens.css. */\n" + system.lstrip())

    shutil.copyfile(os.path.join(ROOT, "DESIGN-SYSTEM.md"),
                    os.path.join(OUT, "README.md"))

    print("\n  tokens.css  system.css  README.md")
    print("\n%d cards + 2 stylesheets + README -> design-system/  (Rev %s)"
          % (len(ordered), VERSION))


if __name__ == "__main__":
    build()
