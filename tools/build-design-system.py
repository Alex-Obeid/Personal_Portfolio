#!/usr/bin/env python3
"""Generate the Claude Design bundle in design-system/ from a single source of tokens.

Every preview is self-contained: the token block is inlined rather than linked, so a
card renders correctly no matter how the host resolves relative paths. That duplication
is the reason this generator exists — edit TOKENS/BASE here, never the generated HTML.

    python tools/build-design-system.py
"""

import io
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "design-system")

FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700"
         "&family=Archivo+Black&family=DM+Mono:wght@400;500&display=swap")

GRAIN = ("url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'"
         "%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85'"
         " numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25'"
         " height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E\")")

TOKENS = """
:root{
  --paper:#f0ebe1; --paper-shade:#e5dfd3; --ink:#0a0a0a;
  --orange:#f05a00; --orange2:#ff7a1a; --warm-muted:#6b6459;

  --bg:var(--paper); --fg:var(--ink); --fg-2:var(--warm-muted);
  --accent:var(--orange); --on-accent:var(--paper);
  --surface:var(--paper-shade);
  --rule:rgba(10,10,10,.20); --rule-strong:rgba(10,10,10,.85);

  --snap:.16s cubic-bezier(.4,0,.2,1);
  --territory-fade:.65s cubic-bezier(.4,0,.2,1);
}
[data-territory="vermillion"]{
  --bg:var(--orange); --fg:var(--ink); --fg-2:rgba(10,10,10,.62);
  --accent:var(--ink); --on-accent:var(--orange);
  --surface:rgba(10,10,10,.07);
  --rule:rgba(10,10,10,.30); --rule-strong:rgba(10,10,10,.88);
}
[data-territory="ink"]{
  --bg:var(--ink); --fg:var(--paper); --fg-2:rgba(240,235,225,.55);
  --accent:var(--orange); --on-accent:var(--ink);
  --surface:#161513;
  --rule:rgba(240,235,225,.20); --rule-strong:rgba(240,235,225,.85);
}
"""

BASE = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{background:var(--paper);}
body{
  color:var(--fg);
  font-family:'Archivo',system-ui,sans-serif;font-weight:400;
  -webkit-font-smoothing:antialiased;
}
/* Paper grain: tooth on cream, not haze on black */
body::after{
  content:'';position:fixed;inset:0;background-image:GRAIN;
  mix-blend-mode:multiply;pointer-events:none;z-index:9999;opacity:.14;
}

/* ── Type scale ── */
.t-display{font-family:'Archivo Black',sans-serif;font-size:clamp(3.4rem,13vw,12rem);line-height:.86;letter-spacing:-.035em;text-transform:uppercase;}
.t-title{font-family:'Archivo Black',sans-serif;font-size:clamp(2.2rem,7.5vw,5.5rem);line-height:.9;letter-spacing:-.03em;text-transform:uppercase;}
.t-numeral{font-family:'Archivo Black',sans-serif;font-size:clamp(4.5rem,19vw,15rem);line-height:.8;letter-spacing:-.045em;}
.t-label{font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;}

/* ── Territory panel ── */
.terr{position:relative;background:var(--bg);color:var(--fg);padding:44px 40px 40px;overflow:clip;}
.gfx{position:absolute;pointer-events:none;z-index:0;}

/* ── Spec mark ── */
.spec-mark{display:inline-flex;align-items:center;gap:7px;font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.18em;text-transform:uppercase;color:var(--fg-2);}
.spec-mark .sm-bars{display:inline-flex;gap:2px;}
.spec-mark .sm-bars i{width:2px;height:9px;background:currentColor;display:block;}

/* ── Inversion: the hover language ── */
.inv{border:1px solid var(--rule-strong);background:transparent;color:var(--fg);transition:background var(--snap),color var(--snap),border-color var(--snap);}
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

/* ── Tag / pill ── */
.tag{display:inline-flex;align-items:center;gap:8px;padding:5px 10px;font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:.15em;text-transform:uppercase;border:1px solid var(--rule-strong);color:var(--fg);background:transparent;transition:background var(--snap),color var(--snap),border-color var(--snap);}
.tag:hover{background:var(--accent);color:var(--on-accent);border-color:var(--accent);}

/* ── Card scaffolding (documentation chrome only — not part of the language) ── */
.ds-note{font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.16em;text-transform:uppercase;color:var(--fg-2);}
.ds-row{display:flex;flex-wrap:wrap;gap:16px;align-items:center;}
.ds-stack{display:flex;flex-direction:column;gap:10px;}
.ds-rule{height:1px;background:var(--rule);margin:20px 0;}
.ds-kicker{display:flex;align-items:center;gap:12px;color:var(--fg-2);margin-bottom:18px;}
.ds-kicker .bar{width:46px;height:2px;background:var(--accent);flex:none;}
"""


def page(path, group, name, subtitle, viewport, body, title=None, extra_css=""):
    return dict(path=path, group=group, name=name, subtitle=subtitle,
                viewport=viewport, body=body, title=title or name,
                extra_css=extra_css)


# ───────────────────────────────── FOUNDATIONS ─────────────────────────────────

def territory_block(terr, label, ground, type_c, sec, accent):
    attr = f' data-territory="{terr}"' if terr else ""
    return f"""
  <section class="terr t-block"{attr}>
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">{label}</span></div>
    <div class="t-grid">
      <div class="sw" style="background:var(--bg);border:1px solid var(--rule-strong);"></div>
      <div class="sw" style="background:var(--fg);"></div>
      <div class="sw" style="background:var(--accent);"></div>
      <div class="sw" style="background:var(--surface);border:1px solid var(--rule);"></div>
    </div>
    <dl class="t-tok">
      <dt class="ds-note">--bg</dt><dd class="ds-note">{ground}</dd>
      <dt class="ds-note">--fg</dt><dd class="ds-note">{type_c}</dd>
      <dt class="ds-note">--fg-2</dt><dd class="ds-note">{sec}</dd>
      <dt class="ds-note">--accent</dt><dd class="ds-note">{accent}</dd>
    </dl>
    <p class="t-demo">Body copy sits in <b>--fg</b>, meta in <span style="color:var(--fg-2)">--fg-2</span>,
       and one word may take the <span style="color:var(--accent)">accent</span>.</p>
  </section>"""


COLOR_CSS = """
.wrap{display:grid;grid-template-columns:repeat(3,1fr);min-height:100vh;}
.t-block{display:flex;flex-direction:column;justify-content:flex-start;}
.t-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:22px;}
.sw{aspect-ratio:1/1;}
.t-tok{display:grid;grid-template-columns:auto 1fr;gap:6px 18px;margin-bottom:22px;}
.t-tok dd{justify-self:end;}
.t-demo{font-size:.82rem;line-height:1.6;color:var(--fg-2);max-width:26ch;}
.t-demo b{color:var(--fg);font-weight:700;}
@media(max-width:900px){.wrap{grid-template-columns:1fr;}}
"""

COLOR = page(
    "foundations/colour-territories.html", "Foundations", "Colour territories",
    "Paper / Vermillion / Ink", "1280x720",
    "<div class=\"wrap\">"
    + territory_block("", "Paper — default", "#f0ebe1", "#0a0a0a", "#6b6459", "#f05a00")
    + territory_block("vermillion", "Vermillion", "#f05a00", "#0a0a0a", "10,10,10 / .62", "#0a0a0a")
    + territory_block("ink", "Ink", "#0a0a0a", "#f0ebe1", "240,235,225 / .55", "#f05a00")
    + "</div>",
    extra_css=COLOR_CSS)


TYPE_CSS = """
.terr{min-height:100vh;}
.spec{border-top:1px solid var(--rule);padding:22px 0 18px;display:grid;grid-template-columns:1fr auto;gap:28px;align-items:baseline;}
.spec:last-child{border-bottom:1px solid var(--rule);}
.spec .meta{justify-self:end;text-align:right;color:var(--fg-2);}
.spec .meta span{display:block;}
.body-demo{font-size:1.02rem;line-height:1.55;color:var(--fg-2);max-width:46ch;}
"""

TYPE = page(
    "foundations/type-scale.html", "Foundations", "Type scale",
    "Archivo Black / Archivo / DM Mono — polarised", "1280x900",
    """
  <section class="terr">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Type — huge or tiny, nothing between</span></div>

    <div class="spec">
      <div class="t-display">Aa</div>
      <div class="meta ds-note">
        <span>.t-display</span><span>Archivo Black</span>
        <span>clamp(3.4rem,13vw,12rem)</span><span>lh .86 &middot; ls -.035em</span>
      </div>
    </div>

    <div class="spec">
      <div class="t-title">Section Title</div>
      <div class="meta ds-note">
        <span>.t-title</span><span>Archivo Black</span>
        <span>clamp(2.2rem,7.5vw,5.5rem)</span><span>lh .9 &middot; ls -.03em</span>
      </div>
    </div>

    <div class="spec">
      <div class="t-numeral">04</div>
      <div class="meta ds-note">
        <span>.t-numeral</span><span>Archivo Black</span>
        <span>clamp(4.5rem,19vw,15rem)</span><span>lh .8 &middot; ls -.045em</span>
      </div>
    </div>

    <div class="spec">
      <p class="body-demo">Body copy is Archivo at 1.02rem, line-height 1.55, capped at
      46ch. Left-aligned, ragged right — never centred, never set large.</p>
      <div class="meta ds-note">
        <span>body</span><span>Archivo 400</span>
        <span>1.02rem &middot; lh 1.55</span><span>max 46ch</span>
      </div>
    </div>

    <div class="spec">
      <div class="t-label">Label &middot; Spec Tag &middot; Index</div>
      <div class="meta ds-note">
        <span>.t-label</span><span>DM Mono</span>
        <span>.62rem</span><span>ls .2em &middot; uppercase</span>
      </div>
    </div>
  </section>""",
    extra_css=TYPE_CSS)


SPACE_CSS = """
.terr{min-height:100vh;}
.steps{display:flex;align-items:flex-end;gap:10px;margin:8px 0 34px;}
.steps div{background:var(--accent);width:26px;}
.steps span{display:block;margin-top:8px;font-family:'DM Mono',monospace;font-size:.5rem;letter-spacing:.1em;color:var(--fg-2);text-align:center;}
.steps figure{display:flex;flex-direction:column;align-items:center;}
.cols{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:56px;align-items:end;border:1px solid var(--rule);padding:26px;margin-bottom:30px;}
.cols .fill{height:120px;background:var(--surface);border:1px solid var(--rule);}
.cols .fix{width:160px;height:190px;background:var(--surface);border:1px solid var(--rule-strong);}
.bps{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-top:1px solid var(--rule);}
.bps div{border-bottom:1px solid var(--rule);border-right:1px solid var(--rule);padding:14px 0;}
.bps div:last-child{border-right:0;}
"""

SPACE = page(
    "foundations/space-and-grid.html", "Foundations", "Space & grid",
    "Rhythm, panel padding, breakpoints, zero radius", "1280x860",
    """
  <section class="terr">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Spacing rhythm</span></div>
    <div class="steps">
      <figure><div style="height:6px"></div><span>6</span></figure>
      <figure><div style="height:8px"></div><span>8</span></figure>
      <figure><div style="height:12px"></div><span>12</span></figure>
      <figure><div style="height:18px"></div><span>18</span></figure>
      <figure><div style="height:26px"></div><span>26</span></figure>
      <figure><div style="height:30px"></div><span>30</span></figure>
      <figure><div style="height:48px"></div><span>48</span></figure>
      <figure><div style="height:56px"></div><span>56</span></figure>
      <figure><div style="height:96px"></div><span>96</span></figure>
      <figure><div style="height:118px"></div><span>118</span></figure>
    </div>

    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Asymmetric grid — minmax(0,1fr) auto</span></div>
    <div class="cols">
      <div class="fill"></div>
      <div class="fix"></div>
    </div>

    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Panel padding &middot; 118px 48px 96px</span></div>
    <p class="ds-note" style="margin-bottom:26px;line-height:2;">
      Top exceeds bottom — panels hang from their top edge. Tightens to 96px 22px 72px below 768px.<br>
      Border radius is 0 everywhere. Panels are full-bleed and use overflow:clip so artwork can crop.
    </p>

    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Breakpoints</span></div>
    <div class="bps">
      <div><span class="t-numeral" style="font-size:2.1rem">1000</span></div>
      <div><span class="t-numeral" style="font-size:2.1rem">860</span></div>
      <div><span class="t-numeral" style="font-size:2.1rem">768</span></div>
      <div><span class="t-numeral" style="font-size:2.1rem">580</span></div>
    </div>
  </section>""",
    extra_css=SPACE_CSS)


MARKS_CSS = """
.wrap{display:grid;grid-template-columns:1fr 1fr;min-height:100vh;}
.terr{display:flex;flex-direction:column;gap:30px;}
.item{display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center;}
.demo-hair{height:1px;background:var(--rule);}
.demo-key{height:1px;background:var(--rule-strong);}
.demo-bar{width:46px;height:2px;background:var(--accent);}
.frame{border:1px solid var(--rule-strong);height:74px;background:var(--surface);}
"""

MARKS = page(
    "foundations/rules-and-marks.html", "Foundations", "Rules & marks",
    "Hairline, keyline, accent bar, spec mark, grain", "1280x620",
    """
  <div class="wrap">
  <section class="terr">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Marks on paper</span></div>

    <div class="item"><div class="demo-hair"></div><span class="ds-note">--rule &middot; 1px &middot; divides</span></div>
    <div class="item"><div class="demo-key"></div><span class="ds-note">--rule-strong &middot; 1px &middot; an edge</span></div>
    <div class="item"><div class="demo-bar"></div><span class="ds-note">accent bar &middot; 2px &times; 46px</span></div>
    <div class="item"><span class="spec-mark"><i class="sm-bars"><i></i><i></i><i></i></i>FIG. 03</span><span class="ds-note">.spec-mark</span></div>
    <div class="item"><div class="frame"></div><span class="ds-note">--surface + keyline</span></div>
  </section>

  <section class="terr" data-territory="ink">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">The same marks on ink</span></div>

    <div class="item"><div class="demo-hair"></div><span class="ds-note">--rule &middot; 1px &middot; divides</span></div>
    <div class="item"><div class="demo-key"></div><span class="ds-note">--rule-strong &middot; 1px &middot; an edge</span></div>
    <div class="item"><div class="demo-bar"></div><span class="ds-note">accent bar &middot; 2px &times; 46px</span></div>
    <div class="item"><span class="spec-mark"><i class="sm-bars"><i></i><i></i><i></i></i>FIG. 03</span><span class="ds-note">.spec-mark</span></div>
    <div class="item"><div class="frame"></div><span class="ds-note">--surface + keyline</span></div>
  </section>
  </div>""",
    extra_css=MARKS_CSS)


# ─────────────────────────────────── BRAND ─────────────────────────────────────

BRAND_CSS = """
.terr{min-height:100vh;display:flex;flex-direction:column;justify-content:center;gap:52px;}
.mark-row{display:flex;align-items:center;gap:56px;flex-wrap:wrap;}
.wordmark{font-family:'Archivo Black',sans-serif;font-size:clamp(2.4rem,7vw,4.6rem);letter-spacing:-.02em;text-transform:uppercase;line-height:1;}
.wordmark span{color:var(--accent);}
.wordmark-sm{font-family:'Archivo Black',sans-serif;font-size:1.22rem;letter-spacing:-.02em;text-transform:uppercase;}
.wordmark-sm span{color:var(--accent);}
.favi{width:96px;height:96px;flex:none;}
"""

FAVICON_SVG = """<svg class="favi" viewBox="0 0 64 64" role="img" aria-label="Alex Obeid">
        <rect width="64" height="64" fill="#0a0a0a"/>
        <path fill="#f0ebe1" fill-rule="evenodd" d="M32 8 L59 57 L5 57 Z M32 27 L45 57 L19 57 Z"/>
        <path fill="#f0ebe1" d="M15 41 H49 V48 H15 Z"/>
        <rect x="48" y="7" width="10" height="10" fill="#f05a00"/>
      </svg>"""

BRAND = page(
    "brand/wordmark.html", "Brand", "Wordmark & mark",
    "Alex.Obeid — the vermillion dot", "1280x600",
    f"""
  <section class="terr">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Wordmark</span></div>

    <div class="mark-row">
      <div class="wordmark">Alex<span>.</span>Obeid</div>
      {FAVICON_SVG}
    </div>

    <div class="ds-rule"></div>

    <div class="mark-row">
      <div class="wordmark-sm">Alex<span>.</span>Obeid</div>
      <span class="ds-note">nav lock-up &middot; 1.22rem &middot; ls -.02em</span>
    </div>

    <p class="ds-note" style="line-height:2;max-width:60ch;">
      Archivo Black, uppercase, -.02em. Words in --fg, the dot in --accent.<br>
      The dot is the smallest unit of the identity; the favicon squares it.<br>
      The favicon letterform is drawn as paths, never &lt;text&gt; — favicons render
      outside the page context and a webfont would silently fall back.
    </p>
  </section>""",
    extra_css=BRAND_CSS)


# ───────────────────────────────── COMPONENTS ──────────────────────────────────

def button_set():
    return """
      <div class="ds-row">
        <button class="btn btn-primary">Primary Action</button>
        <button class="btn">Secondary</button>
        <a class="btn" href="#">With Icon
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
      </div>"""


BUTTONS_CSS = """
.wrap{display:grid;grid-template-columns:repeat(3,1fr);min-height:100vh;}
.terr{display:flex;flex-direction:column;gap:26px;}
"""

BUTTONS = page(
    "components/buttons.html", "Components", "Buttons",
    "Primary / secondary / icon — hover inverts", "1280x560",
    f"""
  <div class="wrap">
    <section class="terr">
      <div class="ds-kicker"><span class="bar"></span><span class="t-label">Paper</span></div>
      {button_set()}
      <p class="ds-note" style="line-height:2;">hover &rarr; accent fill<br>active &rarr; fg fill</p>
    </section>
    <section class="terr" data-territory="vermillion">
      <div class="ds-kicker"><span class="bar"></span><span class="t-label">Vermillion</span></div>
      {button_set()}
      <p class="ds-note" style="line-height:2;">accent is ink here —<br>orange on orange never happens</p>
    </section>
    <section class="terr" data-territory="ink">
      <div class="ds-kicker"><span class="bar"></span><span class="t-label">Ink</span></div>
      {button_set()}
      <p class="ds-note" style="line-height:2;">one component,<br>three grounds, no variants</p>
    </section>
  </div>""",
    extra_css=BUTTONS_CSS)


TAGS_CSS = """
.terr{min-height:100vh;}
.wrap{display:grid;grid-template-columns:1fr 1fr;gap:0;min-height:100vh;}
.pill{padding:8px 13px;border:1px solid var(--rule-strong);font-family:'DM Mono',monospace;font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:var(--fg);display:inline-flex;align-items:center;gap:8px;transition:background var(--snap),color var(--snap),border-color var(--snap);}
.pill:hover{background:var(--accent);color:var(--on-accent);border-color:var(--accent);}
.pill svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;}
"""

TAGS = page(
    "components/tags-and-pills.html", "Components", "Tags & pills",
    "Mono, square, keylined — with and without icon", "1280x520",
    """
  <div class="wrap">
    <section class="terr">
      <div class="ds-kicker"><span class="bar"></span><span class="t-label">Spec tags &middot; .58rem / .15em</span></div>
      <div class="ds-row" style="margin-bottom:34px;">
        <span class="tag">SolidWorks</span>
        <span class="tag">FEA</span>
        <span class="tag">CFD</span>
        <span class="tag">GD&amp;T</span>
      </div>
      <div class="ds-kicker"><span class="bar"></span><span class="t-label">Skill pills &middot; .66rem / .1em</span></div>
      <div class="ds-row">
        <span class="pill"><svg viewBox="0 0 24 24"><path d="M4 18l4-6 4 3 6-9"/></svg>FEA</span>
        <span class="pill"><svg viewBox="0 0 24 24"><path d="M3 9c3-2.5 6 2.5 9 0s6 2.5 9 0M3 15c3-2.5 6 2.5 9 0s6 2.5 9 0"/></svg>CFD</span>
        <span class="pill"><svg viewBox="0 0 24 24"><circle cx="7" cy="17" r="2"/><circle cx="17" cy="7" r="2"/><path d="M8.5 15.5l7-7"/></svg>Kinematics</span>
      </div>
    </section>
    <section class="terr" data-territory="ink">
      <div class="ds-kicker"><span class="bar"></span><span class="t-label">On ink</span></div>
      <div class="ds-row" style="margin-bottom:34px;">
        <span class="tag">SolidWorks</span>
        <span class="tag">FEA</span>
        <span class="tag">CFD</span>
        <span class="tag">GD&amp;T</span>
      </div>
      <div class="ds-row">
        <span class="pill"><svg viewBox="0 0 24 24"><path d="M4 18l4-6 4 3 6-9"/></svg>FEA</span>
        <span class="pill"><svg viewBox="0 0 24 24"><path d="M3 9c3-2.5 6 2.5 9 0s6 2.5 9 0M3 15c3-2.5 6 2.5 9 0s6 2.5 9 0"/></svg>CFD</span>
      </div>
    </section>
  </div>""",
    extra_css=TAGS_CSS)


FORM_CSS = """
.terr{min-height:100vh;}
.form{max-width:520px;display:flex;flex-direction:column;gap:26px;}
.fg{display:flex;flex-direction:column;gap:7px;}
.fg label{font-family:'DM Mono',monospace;font-size:.56rem;letter-spacing:.18em;text-transform:uppercase;color:var(--fg-2);}
.fg input,.fg textarea{
  background:transparent;border:0;border-bottom:1px solid var(--rule-strong);
  color:var(--fg);font-family:'Archivo',sans-serif;font-size:.95rem;
  padding:10px 2px;outline:none;resize:none;
  transition:border-color var(--snap);
}
.fg input::placeholder,.fg textarea::placeholder{color:var(--fg-2);}
.fg input:focus,.fg textarea:focus{border-bottom-color:var(--accent);}
"""

FORM = page(
    "components/form-fields.html", "Components", "Form fields",
    "No box — a single keyline that accents on focus", "1280x620",
    """
  <section class="terr">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Fields</span></div>
    <form class="form" onsubmit="return false">
      <div class="fg"><label for="n">Name</label><input id="n" placeholder="Your name"></div>
      <div class="fg"><label for="e">Email</label><input id="e" type="email" placeholder="you@domain.com"></div>
      <div class="fg"><label for="m">Message</label><textarea id="m" rows="3" placeholder="What are you building?"></textarea></div>
      <div class="ds-row"><button class="btn btn-primary" type="submit">Send Message</button></div>
    </form>
    <p class="ds-note" style="margin-top:30px;line-height:2;">
      Inputs have no box and no radius — one 1px bottom keyline.<br>
      Focus moves the keyline to --accent. Labels are mono, uppercase, .18em.
    </p>
  </section>""",
    extra_css=FORM_CSS)


NAV_CSS = """
.wrap{display:flex;flex-direction:column;min-height:100vh;}
.navbar{
  display:flex;align-items:center;justify-content:space-between;
  padding:18px 40px;border-bottom:1px solid var(--rule);
  background:var(--bg);color:var(--fg);
  transition:background var(--territory-fade),color var(--territory-fade);
}
.nav-logo{font-family:'Archivo Black',sans-serif;font-size:1.22rem;letter-spacing:-.02em;text-transform:uppercase;color:var(--fg);text-decoration:none;}
.nav-logo span{color:var(--accent);}
.nav-links{display:flex;gap:30px;list-style:none;}
.nav-links a{
  display:inline-flex;align-items:center;gap:8px;text-decoration:none;
  font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--fg-2);transition:color var(--snap);
}
.nav-links a.active,.nav-links a:hover{color:var(--accent);}
.nav-links svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;}
.bed{flex:1;display:flex;align-items:center;padding:0 40px;}
"""


def navbar(active="Home"):
    def li(label, icon, is_active):
        cls = ' class="active"' if is_active else ""
        return f'<li><a href="#"{cls}>{icon}<span>{label}</span></a></li>'
    home = '<svg viewBox="0 0 24 24"><path d="M3 10.5L12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/></svg>'
    proj = '<svg viewBox="0 0 24 24"><path d="M4 12h16M4 16h10M4 8h12"/></svg>'
    cv = '<svg viewBox="0 0 24 24"><path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/></svg>'
    return f"""    <nav class="navbar">
      <a href="#" class="nav-logo">Alex<span>.</span>Obeid</a>
      <ul class="nav-links">
        {li("Home", home, active == "Home")}
        {li("Projects", proj, active == "Projects")}
        {li("CV", cv, active == "CV")}
      </ul>
    </nav>"""


NAV = page(
    "components/navigation.html", "Components", "Navigation",
    "Fixed bar that adopts the territory beneath it", "1280x680",
    f"""
  <div class="wrap">
    <div>
{navbar("Home")}
      <section class="terr bed" style="min-height:150px;">
        <span class="ds-note">Paper ground &middot; nav reads --fg / --accent from it</span>
      </section>
    </div>
    <div data-territory="vermillion">
{navbar("Projects")}
      <section class="terr bed" style="min-height:150px;">
        <span class="ds-note">Vermillion ground &middot; accent flips to ink</span>
      </section>
    </div>
    <div data-territory="ink">
{navbar("CV")}
      <section class="terr bed" style="min-height:150px;">
        <span class="ds-note">Ink ground &middot; accent returns to vermillion</span>
      </section>
    </div>
  </div>""",
    extra_css=NAV_CSS)


STAT_CSS = """
.terr{min-height:100vh;display:flex;flex-direction:column;justify-content:center;}
.stats-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;color:var(--fg-2);}
.stat-row{border-top:1px solid var(--rule);padding:18px 0 10px;display:grid;grid-template-columns:auto 1fr;gap:28px;align-items:center;}
.stat-row:last-child{border-bottom:1px solid var(--rule);}
.stat-num{color:var(--fg);font-family:'Archivo Black',sans-serif;font-size:clamp(3rem,9vw,7rem);line-height:.8;letter-spacing:-.045em;}
.stat-num .unit{font-size:.28em;letter-spacing:.02em;vertical-align:super;color:var(--accent);}
.stat-meta{justify-self:end;text-align:right;color:var(--fg-2);max-width:26ch;font-size:.8rem;line-height:1.5;}
.stat-meta strong{display:block;color:var(--fg);font-weight:700;font-size:.92rem;margin-bottom:3px;}
"""

STAT = page(
    "components/stat-rows.html", "Components", "Stat rows",
    "Oversized numeral against right-aligned meta", "1280x720",
    """
  <section class="terr" data-territory="ink">
    <div class="stats-head">
      <span class="t-label">Selected figures</span>
      <span class="t-label">2026</span>
    </div>
    <div class="stat-row">
      <div class="stat-num">12<span class="unit">:1</span></div>
      <div class="stat-meta"><strong>Gear reduction</strong>Planetary set, three stages, printed and tested</div>
    </div>
    <div class="stat-row">
      <div class="stat-num">340<span class="unit">MPa</span></div>
      <div class="stat-meta"><strong>Peak von Mises</strong>FEA under worst-case torque, 1.8 safety factor</div>
    </div>
    <div class="stat-row">
      <div class="stat-num">05</div>
      <div class="stat-meta"><strong>Axis CNC</strong>Mill, turning and 5-axis toolpath experience</div>
    </div>
  </section>""",
    extra_css=STAT_CSS)


BRICK_CSS = """
.terr{min-height:100vh;}
.masonry{columns:3;column-gap:18px;}
.brick{break-inside:avoid;margin-bottom:18px;border:1px solid var(--rule-strong);cursor:pointer;background:var(--bg);}
.brick-visual{--v-bg:var(--paper-shade);--v-fg:var(--ink);background:var(--v-bg);color:var(--v-fg);position:relative;display:flex;align-items:flex-end;padding:14px;}
.brick.ink .brick-visual{--v-bg:var(--ink);--v-fg:var(--paper);}
.brick.orange .brick-visual{--v-bg:var(--orange);--v-fg:var(--ink);}
.tall .brick-visual{aspect-ratio:3/4;}
.wide .brick-visual{aspect-ratio:16/9;}
.sq .brick-visual{aspect-ratio:1/1;}
.short .brick-visual{aspect-ratio:4/3;}
.brick-num{position:absolute;top:12px;left:14px;font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.18em;}
.brick-body{padding:14px;border-top:1px solid var(--rule-strong);}
.brick-title{font-family:'Archivo Black',sans-serif;font-size:1.05rem;letter-spacing:-.02em;text-transform:uppercase;margin-bottom:6px;line-height:1.1;}
.brick-desc{font-size:.82rem;line-height:1.6;color:var(--fg-2);margin-bottom:10px;}
.brick-cta{display:inline-flex;align-items:center;gap:7px;font-family:'DM Mono',monospace;font-size:.55rem;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);}
.brick:hover .brick-visual{--v-bg:var(--accent);--v-fg:var(--on-accent);}
.brick-visual{transition:background var(--snap),color var(--snap);}
@media(max-width:1000px){.masonry{columns:2;}}
@media(max-width:580px){.masonry{columns:1;}}
"""

BRICK = page(
    "components/project-cards.html", "Components", "Project cards",
    "Masonry bricks — flat panels, size and colour classes", "1280x820",
    """
  <section class="terr">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Masonry &middot; columns 3 / 2 / 1</span></div>
    <div class="masonry">
      <article class="brick tall">
        <div class="brick-visual"><span class="brick-num">03</span></div>
        <div class="brick-body">
          <h3 class="brick-title">Planetary Gearbox</h3>
          <p class="brick-desc">Three-stage reduction, printed, instrumented and tested.</p>
          <span class="brick-cta">Open Project
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </span>
        </div>
      </article>
      <article class="brick orange short">
        <div class="brick-visual"><span class="brick-num">01</span></div>
        <div class="brick-body">
          <h3 class="brick-title">Suspension Rig</h3>
          <p class="brick-desc">Kinematics sweep and camber study.</p>
          <span class="brick-cta">Open Project
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </span>
        </div>
      </article>
      <article class="brick ink sq">
        <div class="brick-visual"><span class="brick-num">02</span></div>
        <div class="brick-body">
          <h3 class="brick-title">Duct Flow Study</h3>
          <p class="brick-desc">CFD on an intake plenum, pressure-loss driven.</p>
          <span class="brick-cta">Open Project
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </span>
        </div>
      </article>
    </div>
    <p class="ds-note" style="margin-top:22px;line-height:2;">
      Sizes: tall 3:4 &middot; wide 16:9 &middot; sq 1:1 &middot; short 4:3 &middot; mini 3:2.<br>
      Each visual sets --v-bg / --v-fg so the number and marks adapt automatically.
    </p>
  </section>""",
    extra_css=BRICK_CSS)


# ─────────────────────────────────── PATTERNS ──────────────────────────────────

HERO_CSS = """
.terr{min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:96px 48px;}
.hero-grid{position:relative;z-index:1;display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:56px;align-items:end;
  grid-template-areas:"kicker figure" "name figure" "bio figure" "meta figure" "cta figure";}
.hero-kicker{grid-area:kicker;display:flex;align-items:center;gap:12px;color:var(--fg-2);margin-bottom:20px;}
.hero-kicker .bar{width:46px;height:2px;background:var(--accent);}
.hero-name{grid-area:name;margin:0 0 26px;}
.hero-name .ln{display:block;}
.hero-name .accent{color:var(--accent);}
.hero-bio{grid-area:bio;max-width:46ch;font-size:1.02rem;line-height:1.55;color:var(--fg-2);margin-bottom:30px;}
.hero-meta{grid-area:meta;display:flex;flex-wrap:wrap;gap:0 26px;color:var(--fg-2);margin-bottom:30px;}
.cta-row{grid-area:cta;display:flex;gap:16px;flex-wrap:wrap;}
.hero-figure{grid-area:figure;align-self:end;position:relative;width:clamp(210px,24vw,290px);}
.hero-figure .plate{width:100%;aspect-ratio:5/6;background:var(--surface);border:1px solid var(--rule-strong);display:flex;align-items:center;justify-content:center;}
.hero-figure .fig-cap{display:flex;justify-content:space-between;margin-top:8px;color:var(--fg-2);}
.corner{position:absolute;right:40px;top:40px;}
"""

HERO = page(
    "patterns/hero-panel.html", "Patterns", "Hero panel",
    "The canonical composition — asymmetric, bottom-aligned, cropped", "1280x820",
    """
  <section class="terr">
    <span class="spec-mark corner"><i class="sm-bars"><i></i><i></i><i></i></i>FIG. 01</span>
    <svg class="gfx" viewBox="0 0 200 200" style="left:-70px;bottom:-60px;width:280px;opacity:.5;" aria-hidden="true">
      <circle cx="100" cy="100" r="86" fill="none" stroke="currentColor" stroke-width="2"/>
      <circle cx="100" cy="100" r="44" fill="none" stroke="currentColor" stroke-width="2"/>
      <path d="M100 0 V200 M0 100 H200" stroke="currentColor" stroke-width="1" opacity=".3"/>
    </svg>

    <div class="hero-grid">
      <div class="hero-kicker"><span class="bar"></span><span class="t-label">Mechanical Engineering &middot; Beirut</span></div>
      <h1 class="hero-name t-display"><span class="ln">Alex</span><span class="ln accent">Obeid</span></h1>
      <p class="hero-bio">Body copy sits at 46ch in secondary type. One accent word in the
        headline, never more. The portrait keeps its own column at every width.</p>
      <div class="hero-meta">
        <span class="t-label">LAU &middot; 2026</span>
        <span class="t-label">CAD / FEA / CFD</span>
      </div>
      <div class="cta-row">
        <a class="btn btn-primary" href="#">View Projects</a>
        <a class="btn" href="#">Download CV</a>
      </div>
      <figure class="hero-figure">
        <div class="plate"><span class="ds-note">Portrait &middot; grayscale(1)</span></div>
        <figcaption class="fig-cap"><span class="t-label">Fig. A</span><span class="t-label">2026</span></figcaption>
      </figure>
    </div>
  </section>""",
    extra_css=HERO_CSS)


INV_CSS = """
.terr{min-height:100vh;display:flex;flex-direction:column;justify-content:center;gap:34px;}
.seq{display:grid;grid-template-columns:repeat(3,minmax(0,220px));gap:18px;}
.state{border:1px solid var(--rule-strong);padding:26px 22px;display:flex;flex-direction:column;gap:14px;}
.s-rest{background:transparent;color:var(--fg);}
.s-hover{background:var(--accent);color:var(--on-accent);border-color:var(--accent);}
.s-active{background:var(--fg);color:var(--bg);border-color:var(--fg);}
.state .lbl{font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.18em;text-transform:uppercase;opacity:.75;}
.state .val{font-family:'Archivo Black',sans-serif;font-size:1.1rem;letter-spacing:-.02em;text-transform:uppercase;}
"""

INVERSION = page(
    "patterns/colour-inversion.html", "Patterns", "Colour inversion",
    "The entire interaction vocabulary — rest / hover / active", "1280x680",
    """
  <section class="terr">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">No shadows. No transforms. Colour inverts.</span></div>

    <div class="seq">
      <div class="state s-rest"><span class="lbl">Rest</span><span class="val">Transparent</span><span class="lbl">border --rule-strong</span></div>
      <div class="state s-hover"><span class="lbl">Hover / focus-visible</span><span class="val">Accent fill</span><span class="lbl">colour --on-accent</span></div>
      <div class="state s-active"><span class="lbl">Active</span><span class="val">FG fill</span><span class="lbl">colour --bg</span></div>
    </div>

    <div class="ds-rule"></div>

    <div class="ds-row" style="gap:40px;">
      <div class="ds-stack">
        <span class="t-label">--snap</span>
        <span class="ds-note">.16s cubic-bezier(.4,0,.2,1) &middot; every state change</span>
      </div>
      <div class="ds-stack">
        <span class="t-label">--territory-fade</span>
        <span class="ds-note">.65s cubic-bezier(.4,0,.2,1) &middot; ground changing under the nav</span>
      </div>
    </div>

    <p class="ds-note" style="line-height:2;max-width:64ch;">
      Live examples below — hover them. Focus-visible gets the identical treatment;
      never remove the outline without replacing it with the inversion.
    </p>
    <div class="ds-row">
      <button class="btn">Ghost</button>
      <button class="btn btn-primary">Solid</button>
      <span class="tag">Tag</span>
    </div>
  </section>""",
    extra_css=INV_CSS)


SWEEP_CSS = """
.terr{min-height:100vh;display:flex;flex-direction:column;justify-content:center;gap:40px;}
.track{position:relative;height:120px;border:1px solid var(--rule);overflow:hidden;background:var(--surface);}
.lyr{position:absolute;top:0;bottom:0;width:130%;left:-130%;animation:sweep 2.6s linear infinite;}
.l1{background:var(--orange);}
.l2{background:var(--ink);animation-delay:.14s;}
.l3{background:var(--paper);animation-delay:.28s;}
@keyframes sweep{0%{transform:translateX(0)}35%{transform:translateX(100%)}100%{transform:translateX(100%)}}
.timeline{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--rule);}
.timeline div{border-bottom:1px solid var(--rule);border-right:1px solid var(--rule);padding:16px 14px;}
.timeline div:last-child{border-right:0;}
.timeline .ms{font-family:'Archivo Black',sans-serif;font-size:1.6rem;letter-spacing:-.03em;display:block;margin-bottom:4px;}
@media (prefers-reduced-motion: reduce){.lyr{animation:none;transform:translateX(100%);}}
"""

SWEEP = page(
    "patterns/page-sweep.html", "Patterns", "Page sweep",
    "Three staggered bars — the only page transition", "1280x620",
    """
  <section class="terr">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Transition &middot; linear, hard-edged, no easing curve</span></div>

    <div class="track">
      <div class="lyr l1"></div>
      <div class="lyr l2"></div>
      <div class="lyr l3"></div>
    </div>

    <div class="timeline">
      <div><span class="ms">900</span><span class="ds-note">ms per layer, linear</span></div>
      <div><span class="ms">140</span><span class="ds-note">ms stagger between layers</span></div>
      <div><span class="ms">730</span><span class="ds-note">ms — swap content here</span></div>
      <div><span class="ms">1180</span><span class="ds-note">ms — release the lock</span></div>
    </div>

    <p class="ds-note" style="line-height:2;max-width:64ch;">
      Order is vermillion, ink, paper. Nothing scales, fades slowly, springs or bounces.
      Skipped entirely under prefers-reduced-motion.
    </p>
  </section>""",
    extra_css=SWEEP_CSS)


# ─────────────────────────────────── GRAPHICS ──────────────────────────────────

ICONS_CSS = """
.wrap{display:grid;grid-template-columns:2fr 1fr;min-height:100vh;}
.terr{display:flex;flex-direction:column;}
.grid{display:grid;grid-template-columns:repeat(6,1fr);gap:0;border-top:1px solid var(--rule);border-left:1px solid var(--rule);}
.cell{border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);aspect-ratio:1/1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;transition:background var(--snap),color var(--snap);}
.cell:hover{background:var(--accent);color:var(--on-accent);}
.cell svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;}
.cell span{font-family:'DM Mono',monospace;font-size:.46rem;letter-spacing:.14em;text-transform:uppercase;opacity:.7;}
.rule-list{display:flex;flex-direction:column;gap:14px;}
.rule-list li{list-style:none;font-family:'DM Mono',monospace;font-size:.56rem;letter-spacing:.14em;text-transform:uppercase;color:var(--fg-2);line-height:1.7;}
.rule-list li b{color:var(--fg);}
"""

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

ICONS = page(
    "graphics/icons.html", "Graphics", "Icons",
    "24×24, stroke 2, round caps, currentColor", "1280x620",
    "<div class=\"wrap\">\n  <section class=\"terr\">\n"
    "    <div class=\"ds-kicker\"><span class=\"bar\"></span><span class=\"t-label\">Icon set</span></div>\n"
    "    <div class=\"grid\">\n"
    + "\n".join(
        f'      <div class="cell"><svg viewBox="0 0 24 24" aria-hidden="true">{d}</svg><span>{n}</span></div>'
        for n, d in ICON_CELLS)
    + """
    </div>
  </section>
  <section class="terr" data-territory="ink">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Spec</span></div>
    <ul class="rule-list">
      <li><b>viewBox</b> 0 0 24 24</li>
      <li><b>fill</b> none</li>
      <li><b>stroke</b> currentColor</li>
      <li><b>stroke-width</b> 2</li>
      <li><b>linecap</b> round</li>
      <li><b>rendered</b> 12–18px</li>
    </ul>
    <div class="ds-rule"></div>
    <ul class="rule-list">
      <li>Geometric and open. No filled glyphs, no duotone, no detail that dies below 16px.</li>
      <li>Never an icon library. Never emoji.</li>
    </ul>
  </section>
  </div>""",
    extra_css=ICONS_CSS)


ART_CSS = """
.wrap{display:grid;grid-template-columns:1fr 1fr;min-height:100vh;}
.terr{display:flex;flex-direction:column;}
.stage{position:relative;flex:1;min-height:300px;border:1px solid var(--rule);overflow:clip;margin-bottom:22px;}
.stage .caption{position:absolute;right:14px;bottom:12px;}
.rule-list{display:flex;flex-direction:column;gap:12px;}
.rule-list li{list-style:none;font-size:.78rem;line-height:1.65;color:var(--fg-2);padding-left:16px;position:relative;}
.rule-list li::before{content:'';position:absolute;left:0;top:.62em;width:7px;height:2px;background:var(--accent);}
.rule-list li b{color:var(--fg);font-weight:700;}
"""

ARTWORK_SVG = """<svg class="gfx" viewBox="0 0 240 240" style="left:-108px;bottom:-96px;width:340px;" aria-hidden="true">
        <!-- hairline construction -->
        <path d="M0 120 H240 M120 0 V240" stroke="currentColor" stroke-width="1" opacity=".22"/>
        <!-- primary form: inherits the territory's foreground -->
        <circle cx="120" cy="120" r="78" fill="none" stroke="currentColor" stroke-width="2"/>
        <circle cx="120" cy="120" r="34" fill="none" stroke="currentColor" stroke-width="2"/>
        <!-- teeth, constructed at 15-degree increments -->
        <g stroke="currentColor" stroke-width="2">
          <path d="M120 42 V26"/><path d="M175 65 L186 54"/><path d="M198 120 H214"/>
          <path d="M175 175 L186 186"/><path d="M120 198 V214"/><path d="M65 175 L54 186"/>
          <path d="M42 120 H26"/><path d="M65 65 L54 54"/>
        </g>
        <!-- the one accent element -->
        <rect x="112" y="14" width="16" height="16" fill="var(--accent)"/>
      </svg>"""

ARTWORK = page(
    "graphics/artwork.html", "Graphics", "Artwork & the .gfx slot",
    "currentColor, flat, orthographic, cropped by the panel", "1280x760",
    f"""
  <div class="wrap">
    <section class="terr">
      <div class="ds-kicker"><span class="bar"></span><span class="t-label">Same file, paper ground</span></div>
      <div class="stage">
        {ARTWORK_SVG}
        <span class="spec-mark caption"><i class="sm-bars"><i></i><i></i><i></i></i>Fig. 02 &middot; Gear</span>
      </div>
      <ul class="rule-list">
        <li><b>currentColor and var(--accent) only</b> — never hex. One file works on all three grounds.</li>
        <li><b>Two tones, three at most.</b> No gradients, no opacity ramps for depth, no filter.</li>
        <li><b>Flat and orthographic.</b> Elevation, section, plan. Isometric only if load-bearing.</li>
      </ul>
    </section>

    <section class="terr" data-territory="ink">
      <div class="ds-kicker"><span class="bar"></span><span class="t-label">Same file, ink ground</span></div>
      <div class="stage">
        {ARTWORK_SVG}
        <span class="spec-mark caption"><i class="sm-bars"><i></i><i></i><i></i></i>Fig. 02 &middot; Gear</span>
      </div>
      <ul class="rule-list">
        <li><b>Constructed, not sketched.</b> Circles, arcs, straight runs, 15&deg; increments.</li>
        <li><b>Overlap by knockout</b>, not transparency — fill-rule evenodd or an over-painted shape.</li>
        <li><b>Crop against the panel edge.</b> Artwork fully inside with even margins reads as stock.</li>
      </ul>
    </section>
  </div>""",
    extra_css=ART_CSS)


DONT_CSS = """
.terr{min-height:100vh;}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:0;border:1px solid var(--rule-strong);margin-bottom:22px;}
.half{padding:26px 24px;display:flex;flex-direction:column;gap:14px;min-height:150px;}
.half.no{border-right:1px solid var(--rule-strong);background:var(--surface);}
.hl{font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.18em;text-transform:uppercase;}
.no .hl{color:var(--fg-2);}
.yes .hl{color:var(--accent);}
/* deliberately wrong, for contrast */
.bad-btn{align-self:flex-start;padding:12px 22px;border-radius:24px;border:0;
  background:linear-gradient(180deg,#ff8a3d,#f05a00);color:#fff;
  box-shadow:0 6px 16px rgba(0,0,0,.28);font-family:'Archivo',sans-serif;font-size:.9rem;}
.bad-card{border-radius:14px;background:#fff;box-shadow:0 8px 24px rgba(0,0,0,.14);padding:16px;text-align:center;font-size:.8rem;color:#555;}
.good-card{border:1px solid var(--rule-strong);padding:16px;font-size:.8rem;color:var(--fg-2);}
"""

DONT = page(
    "foundations/what-breaks-it.html", "Foundations", "What breaks the language",
    "Side-by-side tells", "1280x760",
    """
  <section class="terr">
    <div class="ds-kicker"><span class="bar"></span><span class="t-label">Left is wrong. Right is the system.</span></div>

    <div class="pair">
      <div class="half no">
        <span class="hl">Never</span>
        <button class="bad-btn">Get started</button>
        <span class="ds-note">radius &middot; gradient &middot; shadow &middot; sentence case</span>
      </div>
      <div class="half yes">
        <span class="hl">Always</span>
        <button class="btn btn-primary">Get Started</button>
        <span class="ds-note">square &middot; flat &middot; mono &middot; uppercase &middot; tracked</span>
      </div>
    </div>

    <div class="pair">
      <div class="half no">
        <span class="hl">Never</span>
        <div class="bad-card">A floating card with a margin<br>on a neutral background</div>
      </div>
      <div class="half yes">
        <span class="hl">Always</span>
        <div class="good-card">A full-bleed panel, keylined,<br>content on an inset grid</div>
      </div>
    </div>

    <p class="ds-note" style="line-height:2.1;">
      Also disqualifying: pure #000 or #fff &middot; a fourth colour &middot; centred body text &middot;
      display type at default tracking &middot; hover states that lift, scale or glow &middot;
      icons from a library &middot; illustration with perspective or shading.
    </p>
  </section>""",
    extra_css=DONT_CSS)


PAGES = [COLOR, TYPE, SPACE, MARKS, DONT, BRAND,
         BUTTONS, TAGS, FORM, NAV, STAT, BRICK,
         HERO, INVERSION, SWEEP, ICONS, ARTWORK]


TEMPLATE = """<!-- @dsCard group="{group}" name="{name}" subtitle="{subtitle}" viewport="{viewport}" -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Alex Obeid Design System</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<style>
{tokens}
{base}
{extra}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    base = BASE.replace("GRAIN", GRAIN)

    for p in PAGES:
        dest = os.path.join(OUT, p["path"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        html = TEMPLATE.format(
            group=p["group"], name=p["name"], subtitle=p["subtitle"],
            viewport=p["viewport"], title=p["title"], fonts=FONTS,
            tokens=TOKENS.strip(), base=base.strip(),
            extra=p["extra_css"].strip(), body=p["body"].strip())
        io.open(dest, "w", encoding="utf-8", newline="\n").write(html)
        print("  " + p["path"].ljust(44) + p["group"])

    # tokens.css — the canonical copy for anyone consuming the system in code
    tok = os.path.join(OUT, "tokens.css")
    io.open(tok, "w", encoding="utf-8", newline="\n").write(
        "/* Alex Obeid — design tokens. Generated by tools/build-design-system.py */\n"
        + TOKENS.lstrip() + base)
    print("  tokens.css")

    # README.md — the written language spec travels with the bundle
    src = os.path.join(ROOT, "DESIGN-SYSTEM.md")
    shutil.copyfile(src, os.path.join(OUT, "README.md"))
    print("  README.md")

    print("\n%d previews + tokens.css + README.md -> design-system/" % len(PAGES))


if __name__ == "__main__":
    build()
