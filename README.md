# Alex Obeid — Personal Portfolio

A single-file, dependency-free portfolio site for a mechanical engineering student. No
build step, no framework, no package manager — open the HTML file and it runs.

The design language is Swiss / International Typographic Style: heavy neo-grotesque type
at poster scale, flat colour blocking, hairline rules, and no depth effects.

## Contents

| Path | What it is |
| --- | --- |
| `index.html` | The entire site: markup, CSS and JS in one file |
| `DESIGN-SYSTEM.md` | The design language as a portable spec — tokens, type, graphics rules |
| `design-system/` | Generated Claude Design bundle — 17 preview cards + `tokens.css` |
| `tools/build-design-system.py` | Generator for `design-system/` — edit this, not the output |
| `favicon.svg` | AO monogram mark — A over O, vermillion dot in the counter |
| `favicon.ico` `apple-touch-icon.png` `icon-512.png` `favicon-{16,32,48}.png` | Raster icons, generated from the mark |
| `tools/build-icons.py` | Redraws the raster icons from the mark's geometry |
| `Images/Headshot/` | Home-page portrait |
| `Images/Planetary Gearbox/` | Renders and build photos for the Planetary Gearbox project |
| `.claude/launch.json` | Local dev-server config (git-ignored) |

The only external dependency is Google Fonts. Everything else — icons, paper grain,
loading animation, the Snake game — is inline SVG, CSS or vanilla JS.

## Running it locally

`file://` works for everything; nothing here needs a server. If you prefer one:

```bash
python -m http.server 5500
```

Then open `http://localhost:5500/index.html`.

## Deploying

Served from the `main` branch. Any static host works — GitHub Pages, Netlify, Cloudflare
Pages, plain FTP. Upload `index.html`, `favicon.svg` and the `Images/` folder, preserving
folder structure **and file-name casing** (see [Gotchas](#gotchas)).

> **GitHub Pages is not yet enabled.** Repo → Settings → Pages → Source: *Deploy from a
> branch* → `main` / `/ (root)`. The site will then be at
> `https://alex-obeid.github.io/Personal_Portfolio/`.

---

## Shipping to Claude Design

`design-system/` is a ready-to-push Claude Design project: 17 self-contained preview
pages, each opening with a `<!-- @dsCard group="…" name="…" subtitle="…" viewport="…" -->`
marker that the app compiles into its card index. Cards are grouped **Foundations ·
Brand · Components · Patterns · Graphics**.

It is generated. **Edit `tools/build-design-system.py` and rebuild — never edit the
output**, or the next build silently discards your changes:

```bash
python tools/build-design-system.py
```

Tokens are inlined into every preview rather than linked, so a card renders correctly
regardless of how the host resolves relative paths. `tokens.css` ships alongside as the
canonical copy for anything consuming the system in code, and `README.md` inside the
bundle is a copy of [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md).

### Pushing

Pushing needs design-system authorization, which only an **interactive** Claude Code
session can grant. Once, on this machine:

```bash
/design-login
```

Then, from an interactive session in this directory:

```bash
/design-sync
```

That skill drives the upload: it lists your writable design-system projects (or creates
one), diffs `design-system/` against the remote, shows you the exact write/delete plan
for approval, and uploads. Headless and SDK runs reuse the authorization afterwards.

---

## Design system

> This section covers how the system is implemented here. For the design language
> itself — the rules for drawing new components and graphics in this style, in a form
> you can hand to a designer or paste into Claude as context — see
> [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md).

### Colour territories

The palette is three "territories". Each is a full-bleed colour panel that redefines a
set of semantic custom properties, so components adapt automatically wherever they sit.

| Territory | Ground | Type | Accent |
| --- | --- | --- | --- |
| **Paper** (default) | `--paper` `#f0ebe1` | ink | orange |
| **Vermillion** | `--orange` `#f05a00` | ink | ink |
| **Ink** | `--ink` `#0a0a0a` | paper | orange |

Apply one with `data-territory="vermillion"` or `="ink"` on any element; Paper is the
`:root` default. The semantic tokens are:

| Token | Role |
| --- | --- |
| `--bg` / `--fg` | ground and primary type |
| `--fg-2` | secondary type |
| `--accent` / `--on-accent` | accent fill and the colour that reads on it |
| `--surface` | tinted blocks |
| `--rule` / `--rule-strong` | hairlines and keylines |

**Build components against the semantic tokens, never the raw brand colours.** A
component using `var(--fg)` works on all three grounds; one using `var(--ink)` breaks on
the Ink panel.

A set of legacy aliases (`--black`, `--white`, `--mid`, `--grey`…) map onto the semantic
layer so nothing needed rewriting at once. Prefer the semantic names in new code.

### Type

- **`Archivo Black`** — display. Everything large, set tight (`-0.03em`).
- **`Archivo`** — body and UI.
- **`DM Mono`** — labels, spec tags, index numbers. Uppercase, `0.2em` tracking.

Helper classes: `.t-display`, `.t-title`, `.t-numeral`, `.t-label`. The scale is
deliberately polarised — huge or tiny, with nothing in between.

### Interaction: colour inversion

There are **no shadows anywhere**. Hover and press invert colour instead:

```css
.thing      { border:1px solid var(--rule-strong); background:transparent; color:var(--fg); }
.thing:hover{ background:var(--accent); color:var(--on-accent); border-color:var(--accent); }
.thing:active{ background:var(--fg); color:var(--bg); border-color:var(--fg); }
```

`--snap` (`.16s cubic-bezier(.4,0,.2,1)`) is the standard transition.

### Adding artwork

`.gfx` is a positioning hook for hand-authored SVG. Drop it inside any `.terr` and place
it with inline offsets:

```html
<svg class="gfx" style="left:-80px; bottom:-60px; width:clamp(160px,20vw,320px);">…</svg>
```

It sits behind content and is cropped by the panel edge (`.terr` uses `overflow:clip`).
Use `fill="currentColor"` and the artwork picks up each territory's foreground, so one
file works on all three grounds.

---

## How the site works

### Routing

A single-page app with no router library. Every `<section>` is a page; exactly one carries
`.active`, the rest are `display:none`.

- `navigate(target, options)` — plays the three-bar sweep, then calls `applySection()` at
  **730 ms**, which is when the last sweep layer fully covers the viewport. The sweep
  itself runs `900 ms` linear per layer, staggered `140 ms`; the lock releases at
  `1180 ms`.
- `applySection(target)` — swaps `.active`, restarts `.fade-in` animations, updates
  `location.hash`, closes the mobile menu, resets scroll and the momentum scroller.
- `routeFromHash()` — runs on load and on `hashchange`; unknown hashes fall back to `home`.

Sections: `home`, `projects`, `project-detail`, `contact`, `cv`, `easter`.

### Momentum scrolling

Desktop scrolling is eased in JS: `ssTarget` accumulates wheel delta, and a rAF loop
lerps `ssCurrent` toward it at `SS_EASE` (`0.082`) — lower is a longer glide.

It eases the **real document scroll position** rather than transforming a wrapper. That
matters: the wrapper-transform approach used by most smooth-scroll libraries would break
`position:sticky`, which the home carousel depends on.

Two consequences worth knowing:

- `html { scroll-behavior: auto }` is deliberate. Native smooth scrolling fights the loop.
- **Scroll-linked animation is driven from `ssApply()`, not the `scroll` event.**
  Programmatic scrolls fire `scroll` unreliably, which left the carousel a frame or more
  behind. Anything that must track scroll position should be called from there.

Touch is excluded (`pointer:fine` gate) — phones already have native momentum. Disabled
entirely under `prefers-reduced-motion`.

### Home page

Three stacked territories:

1. **Paper** — hero. Portrait occupies its own grid column at every width via
   `grid-template-areas`; on narrow screens it pairs with just the name while the bio,
   meta and buttons run full width beneath.
2. **Vermillion** — the skills carousel.
3. **Ink** — big-numeral stats panel.

The fixed nav reads which territory is beneath it (`updateNavTerritory()`) and adopts its
palette.

### Project showcase

A scroll-pinned **horizontal parallax** gallery on an Ink panel between the hero and the
skills carousel. Adapted from [Codrops' horizontal parallax
gallery](https://tympanus.net/codrops/2026/02/19/creating-a-smooth-horizontal-parallax-gallery-from-dom-to-webgl/),
rebuilt with no dependencies (the original is Vite + TypeScript with a Three.js path).

**Two rows of two, travelling against each other.** Both rows are the same thing — a
project title over its own plates — rendered by the same `pxGroup()`. They differ only in
direction: row A translates `-p × travelA`, row B `-(1-p) × travelB`, so B starts fully
left and unwinds to zero as A unwinds left. Each covers its own full distance over the
same progress; the pin lasts as long as the longer one needs.

Membership lives in `SHOWCASE_ROWS`, **not** `PROJECTS` — the gallery is a curated subset
and Planetary Gearbox is deliberately excluded. Galleries for projects that do exist in
`PROJECTS` are referenced rather than copied, so image lists stay single-sourced:

| Row | Projects |
| --- | --- |
| A (travels left) | Wheel Hub CNC Machining, Generic SUV CFD |
| B (travels right) | Formula Student, Custom CNC Machine Design |

- **Parallax.** Ported from the demo's three tunables, pushed well past its defaults
  because here the whole row is sliding too, which the demo never has to fight:

  | Constant | Here | Demo |
  | --- | --- | --- |
  | `PX_INTENSITY` | `1.15` | `0.4` |
  | `PX_SHADER_MULT` | `1.75` | `1.0` |
  | `PX_UV_SCALE` | `0.64` | `0.85` |

  Per plate: `n = (plateCentre − vw/2) / vw`, so **n spans about ±0.5 — the full viewport,
  not half**. Drift is `n × intensity × multiplier` as a **fraction of plate width**, so
  wide plates travel further. The image is scaled `1/PX_UV_SCALE` (1.563×), the DOM
  equivalent of the shader's `uv -= .5; uv *= uUvScale; uv += .5` — that zoom is the
  buffer the drift moves through. Max drift is **28% of plate width**.
  Raising intensity means lowering `PX_UV_SCALE` to match, at the cost of a tighter crop.
- Drift is eased into the buffer with `tanh` rather than clipping at it, bounded at
  `(1 − uvScale) / (2 × uvScale)` — exactly the headroom the zoom provides — so an image
  edge can never appear.
- **Driven from `ssApply()`**, like the carousel. The `scroll` event alone is not enough.
- **If it scrolls by hand instead of pinning**, the `.is-strip` fallback is active. Call
  `pxWhy()` in the console — it prints which trigger fired. There is **no width gate**: a
  narrow desktop window still pins. Only `hover:none` (touch) and `prefers-reduced-motion`
  fall back. Touch is excluded on purpose — the track is several screens wide, so pinning
  would capture vertical swipes for a long stretch. Note the browser devtools' device
  emulation also sets `hover:none` below 768px, so a narrow *emulated* window falls back
  where a real one would not.
- `.px-sticky` carries padding reserving the absolute head and progress bands, so flex
  centring cannot push the rows under them; a `max-height:680px` query tightens both.
- Gallery entries ending in an image extension render as photos, anything else as a
  labelled drawing-sheet tile. **Right now every entry is a tile** — the only photographed
  project was the one removed. Drop files into `Images/<Project>/` and swap the strings.

### Section slivers

Each home panel carries a mono sliver in its top corner — `Portfolio · 01`,
`Project Gallery · 02`, and so on. **The numbers are not in the markup.** Each mark is an
empty `<span class="spec-mark" data-section="Name">`, and `numberSections()` walks
`#home [data-section]` in DOM order and fills in `Name · NN`. Insert, remove or reorder a
panel and the rest renumber themselves.

- `data-bars="after"` puts the three-bar cluster on the right, for right-aligned marks.
- A panel can echo its own number elsewhere inside itself with `[data-section-num]` — the
  stats panel uses this for its `NN — Index` line.

The order is Portfolio, Project Gallery, Skills, Softwares / Programs, Data. The fourth
is a deliberately empty cream panel holding its place until it has content.

### Software reel

The `Softwares / Programs` panel. Adapted from jh3y's sticky scroll-highlight list: the
lead phrase pins at a focal line while the list scrolls past it, and each item is painted
with a **viewport-fixed gradient clipped to the glyphs**, so whichever line crosses the
band lights up. No JS, and it stays in step with the momentum scroller because the band
is fixed to the viewport rather than driven by a scroll handler.

Three things that will break it if you edit them:

- **The trailing space must be a sibling** (`.sw-runout`), not margin or padding. A margin
  on the sticky collapses through — `overflow:clip` opens no block formatting context —
  and padding on the panel sits outside the content box the sticky is constrained to.
  Either way the sticky ends up exactly as tall as its container and never pins.
- **Line height is also the scroll distance per item.** The list travels past the band 1:1
  with scroll, so a tight stack reads fast. `1.55` gives ~115px per item.
- `--sw-count` on the panel must match the number of items; the sticky's
  `top: calc((count - 1) * -1lh)` depends on it.

iOS Safari ignores `background-attachment:fixed`, so touch and `prefers-reduced-motion`
both get a solid static list instead.

### Skills carousel

A scroll-pinned 3D cylinder, built with CSS transforms and `position:sticky` — no library.

- Skills live in the `SKILL_REEL` array.
- Each is a layer at `rotateX(i × CYL_ANGLE) translateZ(radius)` inside a `preserve-3d`
  container under `perspective`. Scroll progress drives the container's `rotateX`.
- `CYL_ANGLE` is **32°**, not `360/n`. It's an arc, not a closed circle: tighter spacing
  keeps ~5 copies inside the visible ±90°, which is what creates the stacked cascade.
- Opacity falls off as `cos³·⁴` of the angle from front, so the lead copy reads solid and
  the rest recede.
- `layoutCylinder()` sets **one uniform size for every skill**, scaled up until the
  longest line fills 92% of the stage. The longest string therefore caps the size for all
  of them.
- `CYL_TIGHTNESS` (`2.15`) multiplies that size to get the radius — it controls overlap.
  **Radius is not independent of type size**, and the two pull against each other: a
  bigger radius brings the front copy closer to the camera, so the fitting pass shrinks
  the type to keep it inside the stage. At 1280px, raising it from 1.45 opened the copies
  from 67px to 99px apart while costing only 1px of type. Push it much further and the
  outer copies start reaching past the stage, which does not clip — `.cyl-viewport` has no
  `overflow` — so they would spill over the label and the dots.

The wrapper's height (`100vh + 6 × --cyl-step`) is the scroll distance the pinned stage
consumes. Add or remove skills and that `6` should change to match `n − 1`.

### Projects

Content lives in the `PROJECTS` array. Cards in `#projects` are hand-written HTML; clicking
one calls `openProject(idx)`, which fills `#project-detail`.

**`idx` is a raw array index and does not match the number on the card.** The card labelled
`03` (Planetary Gearbox) calls `openProject(0)`; `01` calls `openProject(1)`; `02` calls
`openProject(2)`. Check the array, not the badge.

#### Adding a project

1. Add an entry to `PROJECTS`:

   ```js
   {
     num: '04',
     badge: 'Category · Discipline',            // shown top-left of the detail hero
     heroImage: 'Images/My Project/hero.png',   // optional; omit for a plain panel
     title: 'My Project',
     tags: ['SolidWorks', 'FEA'],
     meta: [{ k: 'Year', v: '2026' }, { k: 'Role', v: 'Design' }],
     body: `<p>Paragraphs of HTML.</p>`,
     gallery: [
       'Images/My Project/photo-1.jpg',   // image paths render as photos
       'Caption Only Tile',               // any other string renders as a labelled tile
     ],
   }
   ```

   `gallery` entries ending `.png/.jpg/.jpeg/.gif/.webp/.svg` render as `<img>`; anything
   else becomes a labelled placeholder tile. The same convention applies to `heroImage` —
   omit it and the hero shows the panel ground with the `num` watermark.

2. Copy an existing `.proj-brick` inside the right `.projects-group` and point its
   `onclick` at the new index.

3. Pick a size class — `tall` (3:4), `wide` (16:9), `sq` (1:1), `short` (4:3), `mini`
   (3:2) — and a colour class `ca`–`ch`. These are **flat panels, not gradients**:
   `cb/ce/ch` are ink, `cc/cf` are orange, the rest paper-shade. Each sets `--v-bg` and
   `--v-fg`, so the badge and corner marks adapt automatically.

Masonry is CSS `columns: 3`, dropping to 2 at 1000px and 1 at 580px.

### Loading animation

Ink panel. A rule draws, the **AO mark** rises from behind it as a mask reveal, then a
mono spec line fades in. On close the mark drops back below the rule and the panel slides
up to wipe the hero into view.

The stack is a fixed measure with the mark centred over it — rule 10 permits centring a
single mark. The rise is `translateY(130%)`, a percentage of the mark's own height, so it
tracks the `clamp()` size. Mark colours are set as local custom properties on
`.startup-intro` rather than by giving it `data-territory="ink"`: the intro is
`position:fixed` over the whole viewport, and the canvas prober would then read it as the
territory on screen.

Timings live in JS: `closing` at `1620 ms`, `done` at `2080 ms`, `hidden` at `2780 ms`.
Skipped entirely under `prefers-reduced-motion`.

### Contact form

`handleForm()` validates and shows a "Message Sent ✓" confirmation. **It does not send
anything** — no backend, no form service. See [Gotchas](#gotchas).

### Easter egg

The keylined triangle at the right of the footer opens `#easter`, a Snake game on a
420×420 board. Fixed 130 ms timestep with interpolated rendering, WebAudio blips, and
`localStorage` for best score (`snakeBest`) and the top five (`snakeScores`). 50 points
wins. Keyboard input is only captured while `#easter` is active.

The board is drawn as a drafting sheet: hairline cell dots, a heavier rule every seven
cells (21 divides by 7), and a registration crosshair on the target. The snake is paper,
tapering from a 1 px inset at the head to 4 px at the tail so **direction reads by shape,
not by a fourth colour** — the only vermillion on the board is the food.

Things worth knowing before editing it:

- **The canvas is DPR-scaled.** `sizeCanvas()` sets the backing store to `420 × dpr` and
  transforms the context, so all drawing is still in 420-unit CSS space. Draw in CSS
  units; never assume `canvas.width` is 420.
- **Turns are queued, not overwritten.** `dirQueue` buffers up to two, each validated
  against the previous queued turn rather than the current heading. Overwriting meant two
  presses inside one 130 ms tick collapsed into the last one and silently dropped a dodge.
- **The tail is not a collision.** It vacates on the same tick unless the snake grows, so
  `stepGame()` tests against `snake.slice(0, -1)` when it hasn't eaten.
- **`AudioContext` is lazy.** Constructing it at page load leaves it suspended and logs a
  warning; `audio()` builds it on the first gesture.
- **Touch is swipe-to-steer, tap to start/pause**, which needs `touch-action:none` on the
  canvas. `TOUCH` also swaps the overlay and hint copy from "Press Space" to "Tap".

---

## Gotchas

- **Image paths are case-sensitive on the deploy target.** Windows and macOS don't care if
  `Images/Main-Render.png` is referenced as `images/main-render.png`; GitHub Pages
  (Linux-backed) does, and a mismatch 404s in production with no error locally. All current
  references match on-disk casing exactly — keep it that way.
- **Text fitting must wait for fonts.** `layoutCylinder()` measures rendered text width.
  Measured against fallback metrics it oversizes every line by ~13%, so it re-runs on
  `document.fonts.ready`. Any new measure-then-size code needs the same treatment.
- **`overflow:hidden` breaks the pinned carousel.** It creates a scroll container and kills
  `position:sticky`. `.terr` uses `overflow:clip`, which clips without that side effect.
- **The gallery/project placeholders are not real work.** Several gallery entries are
  labelled tiles awaiting actual photos and CFD/CAD screenshots.
- **The contact form is decorative.** Wire it to Formspree / Web3Forms / a `mailto:`
  fallback, or replace it with the footer email link.
- **The home bio is `contenteditable`.** Visitors can type over it; edits save nowhere.
  A leftover from the original template.
- **Project cards are `<div onclick>`.** Not keyboard-reachable and not announced as
  interactive by screen readers.
- **No print stylesheet.** The CV page's "Download / Print CV" calls `window.print()` and
  prints the screen styles as-is.
- **Images are unoptimised.** `Main-Render.png` alone is ~595 KB; the `Images/` folder is
  ~1.1 MB. Converting to WebP at sensible dimensions would cut that substantially.
