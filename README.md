# Alex Obeid — Personal Portfolio

A single-file, dependency-free portfolio site for a mechanical engineering student. No
build step, no framework, no package manager — open the HTML file and it runs.

The design language is Swiss / International Typographic Style: heavy neo-grotesque type
at poster scale, flat colour blocking, hairline rules, and no depth effects.

## Contents

| Path | What it is |
| --- | --- |
| `index.html` | The entire site: markup, CSS and JS in one file |
| `favicon.svg` | "A•O" monogram favicon (also the Apple touch icon) |
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

## Design system

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
- `CYL_TIGHTNESS` (`1.45`) multiplies that size to get the radius — it controls overlap.

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

Ink panel. A rule draws across the wordmark's measure, the wordmark rises from behind it
as a mask reveal, then a mono spec line fades in. On close the wordmark drops back below
the rule and the panel slides up to wipe the hero into view.

Timings live in JS: `closing` at `1620 ms`, `done` at `2080 ms`, `hidden` at `2780 ms`.
Skipped entirely under `prefers-reduced-motion`.

### Contact form

`handleForm()` validates and shows a "Message Sent ✓" confirmation. **It does not send
anything** — no backend, no form service. See [Gotchas](#gotchas).

### Easter egg

The orange triangle in the footer opens `#easter`, a Snake game on a 420×420 canvas. Fixed
130 ms timestep with interpolated rendering, WebAudio blips, and `localStorage` for best
score (`snakeBest`) and history (`snakeScores`). 50 points wins. Keyboard input is only
captured while `#easter` is active.

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
