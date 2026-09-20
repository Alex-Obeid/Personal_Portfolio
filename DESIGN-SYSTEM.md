# Alex Obeid — Design Language

A portable spec for the Swiss / International Typographic identity used across this site.
It is written to be handed to a person or to Claude as standalone context: everything
needed to draw a new component, poster, diagram or icon that looks native to the site is
here, without reading `index.html`.

**Read the [Ten Rules](#ten-rules) first. They are the whole system compressed; the rest
is detail.**

---

## Ten rules

1. **Three colours, no more.** Cream `#f0ebe1`, ink `#0a0a0a`, vermillion `#f05a00`.
2. **Colour arrives in full-bleed panels**, never as accents scattered on a neutral ground.
3. **No depth.** No shadows, no gradients, no blur, no rounded corners, no glass.
4. **Hover inverts colour.** That is the entire interaction vocabulary.
5. **Type is huge or tiny.** Nothing comfortable in between.
6. **Three faces only:** Archivo Black (display), Archivo (body), DM Mono (labels).
7. **Labels are uppercase mono at `0.2em` tracking.** Always.
8. **Hairlines, not borders.** `1px`, and it is a rule that divides, not a box that contains.
9. **Everything sits on a grid and is allowed to bleed off the edge.**
10. **Asymmetry over centring.** Centre only a numeral or a single mark.

---

## 1. Colour

### Brand constants

| Name | Hex | Role |
| --- | --- | --- |
| `--paper` | `#f0ebe1` | Warm cream. The default ground. Never pure white. |
| `--paper-shade` | `#e5dfd3` | One step down from paper. Tinted blocks on cream. |
| `--ink` | `#0a0a0a` | Near-black. Never pure `#000`. |
| `--orange` | `#f05a00` | Vermillion. The only chromatic colour in the system. |
| `--orange2` | `#ff7a1a` | Lighter vermillion. Rare — a highlight inside orange artwork. |
| `--warm-muted` | `#6b6459` | Warm grey. Secondary type on cream only. |

There is no blue, no green, no second accent, no success/warning palette. If a graphic
must distinguish more than three things, distinguish them by **value, shape or texture** —
hatching, dot density, outline vs. fill — not by adding a colour.

### Territories

The palette is applied as **territories**: full-bleed panels that each redefine the
semantic tokens. A component written against semantic tokens works on all three grounds.

| Territory | Ground | Type | Secondary type | Accent | On-accent |
| --- | --- | --- | --- | --- | --- |
| **Paper** (default) | `#f0ebe1` | `#0a0a0a` | `#6b6459` | `#f05a00` | `#f0ebe1` |
| **Vermillion** | `#f05a00` | `#0a0a0a` | `rgba(10,10,10,.62)` | `#0a0a0a` | `#f05a00` |
| **Ink** | `#0a0a0a` | `#f0ebe1` | `rgba(240,235,225,.55)` | `#f05a00` | `#0a0a0a` |

Note what flips: **on the orange ground the accent is ink, not orange.** Orange-on-orange
does not exist. The accent is always whatever contrasts hardest with the ground.

### Semantic tokens

| Token | Role |
| --- | --- |
| `--bg` / `--fg` | Ground and primary type |
| `--fg-2` | Secondary type, captions, meta |
| `--accent` / `--on-accent` | Accent fill and the colour that reads on it |
| `--surface` | Tinted block one step off the ground |
| `--rule` | Hairline, ~20–30% opacity — quiet division |
| `--rule-strong` | Keyline, ~85% opacity — an edge you are meant to see |

```css
:root{
  --paper:#f0ebe1; --paper-shade:#e5dfd3; --ink:#0a0a0a;
  --orange:#f05a00; --orange2:#ff7a1a; --warm-muted:#6b6459;

  --bg:var(--paper); --fg:var(--ink); --fg-2:var(--warm-muted);
  --accent:var(--orange); --on-accent:var(--paper);
  --surface:var(--paper-shade);
  --rule:rgba(10,10,10,.20); --rule-strong:rgba(10,10,10,.85);
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
```

**Build against the semantic layer, never the brand constants.** A component using
`var(--fg)` survives every ground; one using `var(--ink)` disappears on the Ink panel.

### Proportion

Roughly **70% ground / 25% type / 5% accent** within any one panel. Vermillion is loud
because it is rationed. A page that is half orange has no accent left.

---

## 2. Type

| Face | Use | Setting |
| --- | --- | --- |
| **Archivo Black** | Display, titles, numerals | Uppercase, tight: `-0.03em` to `-0.045em`, line-height `0.8–0.9` |
| **Archivo** | Body, UI, form fields | 400/500/700, line-height `1.55–1.6`, normal tracking |
| **DM Mono** | Labels, spec tags, index numbers, buttons | Uppercase, `0.15em–0.2em` tracking, `0.54–0.66rem` |

```html
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Archivo+Black&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
```

### The scale is polarised

```css
.t-display{font-size:clamp(3.4rem,13vw,12rem);  line-height:.86; letter-spacing:-.035em;}
.t-title  {font-size:clamp(2.2rem,7.5vw,5.5rem); line-height:.9;  letter-spacing:-.03em;}
.t-numeral{font-size:clamp(4.5rem,19vw,15rem);  line-height:.8;  letter-spacing:-.045em;}
.t-label  {font-size:.62rem; letter-spacing:.2em; text-transform:uppercase;}
```

Display sizes are `vw`-driven so the type **fills its measure** at every width — that is
the Swiss move. Body copy caps at `46ch`; captions and meta at `26ch`.

There is no `h3`-sized step. If something feels like it needs one, it is either a title or
a label — pick.

### Rules of setting

- Display type is **always uppercase** and **always tight**. Negative tracking is not
  optional; Archivo Black at default tracking reads as a different typeface.
- Labels are **always uppercase mono with wide tracking**. The contrast between tight
  display and loose mono is the signature.
- One accent word per headline at most — set it in `var(--accent)`, never bold or italic.
- Never centre body copy. Left-aligned, ragged right.

### Wordmark

`Alex.Obeid` — Archivo Black, uppercase, `-0.02em`, with **the dot in vermillion** and the
words in `--fg`. The orange dot is the smallest unit of the identity; it recurs in the
favicon as a square.

---

## 3. Space and structure

- **Panel padding:** `118px 48px 96px` desktop, tightening to roughly `96px 22px 72px`
  below 768px. Top padding exceeds bottom — panels hang from their top edge.
- **Rhythm:** spacing steps are `6 / 8 / 12 / 18 / 26 / 30 / 48 / 56 / 96 / 118`. Prefer
  these to arbitrary values.
- **Full-bleed by default.** Panels run edge to edge; content sits on an inset grid inside
  them. Never put a panel in a rounded card with a margin.
- **Breakpoints:** `1000px`, `860px`, `768px`, `580px`.
- **Border radius is `0`.** Everywhere. Not on buttons, inputs, images, tags or portraits.

### Composition

Build with **asymmetric two-column grids** (`minmax(0,1fr) auto`), baseline- or
bottom-aligned, with one element deliberately oversized. Let artwork and numerals **crop
against the panel edge** rather than fitting politely inside it — panels use
`overflow:clip` precisely so things can bleed.

---

## 4. Lines, marks and texture

- **Hairline** — `1px solid var(--rule)`. A quiet divider between rows.
- **Keyline** — `1px solid var(--rule-strong)`. A visible edge: buttons, image frames,
  tags, input underlines.
- **Bar** — a `2px` block of `var(--accent)`, typically `46–48px` wide. The kicker bar and
  the divider under the name. This is the system's only ornament.
- **Spec mark** — a mono micro-label with a tiny bar cluster, set into a panel corner:

  ```html
  <span class="spec-mark"><i class="sm-bars"><i></i><i></i><i></i></i>FIG. 03</span>
  ```

  Bars are `2px × 9px`, `2px` apart, in `currentColor`.

- **Paper grain** — SVG `feTurbulence` fractal noise, `baseFrequency 0.85`,
  `numOctaves 4`, fixed over the viewport at `opacity .14` with `mix-blend-mode:multiply`,
  so it reads as tooth on cream rather than haze on black. It is a page-level effect;
  never bake grain into an individual graphic.

---

## 5. Interaction

**No shadows and no transforms on hover. Colour inverts instead.**

```css
.inv        { border:1px solid var(--rule-strong); background:transparent; color:var(--fg); }
.inv:hover,
.inv:focus-visible { background:var(--accent); color:var(--on-accent); border-color:var(--accent); }
.inv:active { background:var(--fg); color:var(--bg); border-color:var(--fg); }

/* Already-solid variant inverts the other way */
.inv-solid       { background:var(--accent); color:var(--on-accent); border-color:var(--accent); }
.inv-solid:hover { background:var(--fg);     color:var(--bg);        border-color:var(--fg); }
```

Two transitions exist:

| Token | Value | Use |
| --- | --- | --- |
| `--snap` | `.16s cubic-bezier(.4,0,.2,1)` | Every hover, press and state change |
| `--territory-fade` | `.65s cubic-bezier(.4,0,.2,1)` | Ground colour changing beneath the nav |

Motion is **linear sweeps and hard wipes**, not springy curves. Page transitions are three
staggered full-height colour bars (orange, ink, paper) crossing the viewport. Nothing
scales, glows or bounces.

`:focus-visible` gets the same treatment as `:hover` — never remove the outline without
replacing it with the inversion.

---

## 6. Buttons and controls

```css
.btn{
  display:inline-flex; align-items:center; gap:10px;
  padding:15px 30px;
  font-family:'DM Mono',monospace; font-size:.66rem; letter-spacing:.18em;
  text-transform:uppercase;
  border:1px solid var(--rule-strong); background:transparent; color:var(--fg);
  transition:background var(--snap), color var(--snap), border-color var(--snap);
}
```

Buttons are **mono, uppercase, wide-tracked, rectangular — small in type, generous in
padding**. `.btn-primary` starts filled with the accent; `.btn-ghost` stays transparent.
Inputs have **no box**: a `1px` bottom keyline that changes colour on focus, nothing else.

Tags and pills: mono, `0.55–0.66rem`, `0.1–0.18em` tracking, `1px` keyline, square,
transparent fill.

---

## 7. Graphics

Follow this section when drawing something new — a diagram, a project illustration, a
poster panel, an icon.

### Format

**Inline SVG, hand-authored.** No raster exports for anything geometric, no icon fonts, no
icon libraries. The site has zero dependencies and graphics must not break that.

### The `.gfx` slot

Artwork drops into any panel as a positioned layer behind the content:

```html
<svg class="gfx" viewBox="0 0 200 200" style="left:-80px; bottom:-60px; width:clamp(160px,20vw,320px);">
  <path fill="currentColor" d="…"/>
</svg>
```

`.gfx` is `position:absolute; pointer-events:none; z-index:0;` and the panel clips it, so
**position artwork so it deliberately runs off an edge.** A graphic sitting fully inside
the panel with even margins looks like stock illustration; a graphic cropped by the edge
looks like the identity.

### Drawing rules

- **Use `currentColor` and `var(--accent)` — never hex.** A graphic built on
  `currentColor` inherits each territory's foreground, so one file works on cream, orange
  and ink with no variants.
- **Two tones per graphic, three at most:** `currentColor`, `var(--accent)`, and
  optionally a `var(--rule)`-weight hairline. No gradients, no opacity ramps for depth, no
  `filter`.
- **Flat and orthographic.** Elevation, section and plan views; isometric only if a third
  dimension is genuinely load-bearing. No perspective, no rendering, no lighting.
- **Geometry is constructed, not sketched.** Circles, arcs, straight runs, angles at 15°
  increments. No freehand bezier wobble.
- **Overlap by knockout, not transparency.** Where two shapes cross, knock one out in the
  ground colour (`fill-rule="evenodd"`, or an over-painted shape) rather than setting
  `opacity`. The favicon does exactly this.
- **Scale line weights honestly.** They should match the page's hairlines at rendered
  size — aim for `1–2px` on screen, so set `stroke-width` relative to the `viewBox` scale.
- **Annotate in mono.** Labels on a graphic are uppercase DM Mono, `0.2em` tracking,
  ~`0.54rem`, in `--fg-2`, with a `1px` leader line — engineering-drawing convention, not
  chart-library convention.

### Icons

Strict spec, already used throughout the site:

```html
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <path d="M5 12h14M12 5l7 7-7 7"/>
</svg>
```

`24×24` viewBox · `fill="none"` · `stroke="currentColor"` · `stroke-width="2"` · round
caps · rendered at `12–18px`. Geometric and open — no filled glyphs, no duotone, no detail
that dies below 16px.

### Photography

Portraits and process photos are **`grayscale(1) contrast(1.06)` behind a `1px`
`--rule-strong` keyline**, no radius, `object-fit:cover`. Colour photography is reserved
for project renders, where the render's own colour is the content. Captions sit beneath in
mono, split left/right across the image's measure.

### Starter template

```html
<svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <!-- hairline construction -->
  <path d="M0 120 H240 M120 0 V240" stroke="currentColor" stroke-width="1" opacity=".22"/>
  <!-- primary form, inherits the territory's foreground -->
  <circle cx="120" cy="120" r="78" fill="none" stroke="currentColor" stroke-width="2"/>
  <!-- the one accent element -->
  <rect x="112" y="16" width="16" height="16" fill="var(--accent)"/>
</svg>
```

---

## 8. What breaks the language

Reliable tells that something was designed outside the system:

- Drop shadows, `box-shadow`, elevation, layering by blur
- Rounded corners of any radius
- Gradients — including subtle ones on buttons, and "glass" overlays
- Pure `#000` or `#fff`
- A fourth colour, or a chart palette
- Centred body text, or a centred layout generally
- Display type at default tracking, or body type set large
- Sentence-case labels, or labels set in the body face
- Hover states that lift, scale, glow or tint
- Emoji as icons, or icons from a library (Material, Font Awesome, Heroicons)
- Illustration with perspective, shading or characters
- Cards with margins floating on a neutral background instead of full-bleed panels

---

## 9. Prompting Claude with this

Paste this file — or the [Ten Rules](#ten-rules) plus §1, §2 and §7 for graphics work — as
context, then state the job concretely:

> Design in the Alex Obeid Swiss language defined in DESIGN-SYSTEM.md. Target territory:
> **ink**. Deliver hand-authored inline SVG on a 240×240 viewBox using `currentColor` and
> `var(--accent)` only, flat and orthographic, cropping off the left edge.

Always specify four things: **territory**, **output format**, **viewBox or dimensions**,
and **whether it crops**. Those answers determine most of the drawing.

Reference points for the sensibility: Josef Müller-Brockmann's concert posters, Wim
Crouwel's grids, Massimo Vignelli's subway system, 1980s cassette-cover spec marks — and
the engineering drawing conventions this portfolio's subject matter is actually about.
