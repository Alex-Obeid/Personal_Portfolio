# Poster Graphics — Rev 1.2

Seventeen graphic components for **alexobeid** — drawn from the cassette-plate poster set,
built strictly in the Alex Obeid Swiss language (see `DESIGN-SYSTEM.md`).

> **Contract.** Every component uses `currentColor` and `var(--accent)` only — no hex, no
> gradient, no shadow, no radius, no fourth colour. Each one therefore works unchanged on
> the paper, vermillion and ink grounds. If you find yourself writing a hex value while
> integrating these, something has gone wrong.

## Files

```
handoff/
  GRAPHICS-SPEC.md          ← this file
  components/
    01-arc-quadrant.html      ← Arc quadrant
    02-stripe-fan.html        ← Stripe fan
    03-numeral-bleed.html     ← Numeral bleed
    04-halftone-drift.html    ← Halftone drift
    05-plate-disc.html        ← Plate — split disc
    06-plate-checker.html     ← Plate — checker ramp
    07-plate-hatch.html       ← Plate — hatch ramp
    08-index-plate.html       ← Plate — index numeral
    09-load-arc.html          ← Loader — arc counter
    10-shutter.html           ← Loader — stripe shutter
    11-grid-fill.html         ← Loader — grid fill
    12-spec-stamp.html        ← Spec stamp
    13-crop-marks.html        ← Crop marks
    14-edge-ticker.html       ← Edge ticker
    15-scan.html              ← Scan bar
    16-count.html             ← Count-up stat
    17-steps.html             ← Step sequencer
```

Each component file is a **complete, runnable page**. It contains, in order:

1. A tokens + system excerpt in the first `<style>` — **delete this block**, your site
   already ships `tokens.css` and `system.css`.
2. A banner comment naming the slot, ground, sizing and motion.
3. The component's own `<style>` — **this is the part you lift** into `system.css`
   (or a new `graphics.css`).
4. The markup inside a `.terr` demo panel — lift the component element, drop the
   `.demo`/`.demo-hd` harness.
5. Where relevant, a `<script>`.

## Integration order

1. Create `design-system/graphics.css`. Paste each component's second `<style>` block into
   it, in file order, keeping the banner comments as section headers.
2. Add one `<link>` (or paste into the existing single-file `index.html` style block —
   the site is currently one file, so that is the honest answer).
3. Add the shared scroll driver once, at the end of the body script.
4. Drop markup into panels per the placement map below.

## Motion vocabulary

Three kinds only, matching §5 of the design system:

| Kind | Components | Driver |
|---|---|---|
| **Static** | 01, 03, 05, 06, 07, 08, 12, 13 | none |
| **Scroll-reactive** | 02, 04, 14 | one shared listener writing `--sp` |
| **Driven** | 09, 10, 11, 15, 16 | CSS animation, or a few lines of local JS |
| **Stateful** | 17 | none — state is authored in the markup |

Everything is a linear sweep or a hard wipe. Nothing scales, glows, springs or bounces.

### Shared scroll driver

The three scroll-reactive components do not each carry a listener — they all read one
custom property, `--sp` (scroll progress, 0 → 1, from the element's own viewport
position). Ship **one** copy:

```js
(function(){
  var els = [].slice.call(document.querySelectorAll('[data-gfx-scroll]'));
  if (!els.length) return;
  if (matchMedia('(prefers-reduced-motion:reduce)').matches) {
    els.forEach(function(e){ e.style.setProperty('--sp','1'); });  // resting state
    return;
  }
  var queued = false;
  function update(){
    queued = false;
    var vh = innerHeight || 1;
    els.forEach(function(el){
      var r = el.getBoundingClientRect();
      var p = (vh - r.top) / (vh + r.height);
      el.style.setProperty('--sp', Math.min(1, Math.max(0, p)).toFixed(4));
    });
  }
  addEventListener('scroll', function(){
    if (!queued) { queued = true; requestAnimationFrame(update); }
  }, { passive:true });
  addEventListener('resize', update);
  update();
})();
```

Reduced motion pins `--sp` to `1`, which is each component's *finished* state — the
graphic is fully present, it simply does not travel. Never pin it to `0`; several
components are invisible at `0`.

### Demo blocks — read this before "fixing" anything

Three files (09, 16 and the previews generally) carry a `@property`/`@keyframes` block
fenced in `/* ── DEMO ONLY ── */` comments, plus a `data-gfx-demo` attribute on the
component root.

**Why.** The catalogue previews each component in a nested iframe, whose document is
`visibilityState:"hidden"`. Browsers throttle *every* JS timer there — `requestAnimationFrame`
and `setInterval` alike — so a JS-driven demo shows a dead frame. CSS animation is the only
clock that still runs. The demos therefore animate custom properties directly, and roll
their numerals as a **stack of real `<b>` rows** behind an `overflow:hidden` window — an
odometer. (A CSS `counter()` would be terser but is invisible to most screenshot and
PDF pipelines, so the digits are real text.) 09 counts in fives, 16 in ones.

**What to do.** Delete the fenced block, drop `data-gfx-demo`, replace the `<b>` stack with
a single text node, and use the production JS quoted with each component. Your site is a
top-level document where timers run normally.

Component 17 has **no** script and needs none — its three-state appearance is authored in
the markup.

### Determinate vs indeterminate

`gfx-load-arc` (09) and `gfx-grid-fill` (11) are determinate — drive them with real
numbers or do not use them. `gfx-scan` (15) is the indeterminate case and takes no input.
`gfx-shutter` (10) is a transition, not progress.

## The seventeen

### Hero & bleed artwork

Drop into any `.terr` panel as a `.gfx` layer. The panel already has `overflow:clip`; every one of these is positioned with negative offsets so it leaves the frame. Keep the headline column clear of the densest part of the artwork — these sit at z-index 0, text at z-index 2.

#### 01 · Arc quadrant — `.gfx-arc-quadrant`

The concentric quarter-rings from the Universal Tape and Super Visual 700 plates. Anchored to a panel corner and cropped hard by it.

| | |
|---|---|
| Ground | paper |
| Sizing | Fluid |
| Motion | Static |
| File | `handoff/components/01-arc-quadrant.html` |

- `left` / `bottom` / `width` inline — always negative offsets so two rings leave the frame
- Swap the accent ring index by moving `stroke="var(--accent)"` to another path

#### 02 · Stripe fan — `.gfx-stripe-fan`

The skewed accelerating stripe block from the Super Fomo and K4 E240 plates. Widths ramp geometrically, the whole field shears.

| | |
|---|---|
| Ground | ink |
| Sizing | Fluid |
| Motion | Scroll-reactive |
| File | `handoff/components/02-stripe-fan.html` |

- `--sp` (0→1) is written by the shared scroll script; the fan slides 34px across the scroll
- Drop `data-gfx-scroll` for the static version

#### 03 · Numeral bleed — `.gfx-numeral-bleed`

The cropped 240 / 700. A display numeral run off two edges with one accent knockout cut through it.

| | |
|---|---|
| Ground | vermillion |
| Sizing | Fluid |
| Motion | Static |
| File | `handoff/components/03-numeral-bleed.html` |

- Numeral text is live HTML — set anything 2–3 glyphs wide
- `.gfx-num-cut` angle and offset via `--cut-deg` / `--cut-y`

#### 04 · Halftone drift — `.gfx-halftone-drift`

The dot field from the Item E-180HR plate. Density ramps left-to-right and up; the whole field opens as the panel enters the viewport.

| | |
|---|---|
| Ground | ink |
| Sizing | Fluid |
| Motion | Scroll-reactive |
| File | `handoff/components/04-halftone-drift.html` |

- Each dot carries `--i` (its own density weight, baked at author time)
- `--sp` scales every dot from 15% to 100% of its weight

### Project card plates

Full-bleed covers for the masonry bricks in `components/project-cards.html`. All four fill their container; the three SVG plates use `preserveAspectRatio` slice so any card ratio crops rather than letterboxes.

#### 05 · Plate — split disc — `.gfx-plate-disc`

The SXG/High plate: two discs overlapping, the intersection knocked out in the ground colour, one slash across.

| | |
|---|---|
| Ground | paper |
| Sizing | Fixed 16:10 |
| Motion | Static |
| File | `handoff/components/05-plate-disc.html` |

- `preserveAspectRatio="xMidYMid slice"` — the plate fills any card ratio and crops
- Recolour by territory only; no hex in the file
- Discs sit 96 apart at r72 — a deliberate 48-unit vesica, knocked back to the accent by `fill-rule="evenodd"`. Do not narrow it; a small overlap reads as a printing error
- The slash runs 8 units past the circumference at both ends so its butt caps fall on accent ground and vanish

#### 06 · Plate — checker ramp — `.gfx-plate-checker`

The square-built glyph from the grey Super Fomo plate, rebuilt as an honest density ramp: column c keeps every (c+1)th cell.

| | |
|---|---|
| Ground | paper-shade |
| Sizing | Fixed 1:1 |
| Motion | Static |
| File | `handoff/components/06-plate-checker.html` |

- Cell size 40, gutter 6 — edit both in the viewBox, not in CSS
- Reads as texture at card scale, as a rule at hero scale

#### 07 · Plate — hatch ramp — `.gfx-plate-hatch`

The K4 E240 plate: 45° rules thickening across the field, stopped dead by one solid accent block.

| | |
|---|---|
| Ground | ink |
| Sizing | Fixed 16:10 |
| Motion | Static |
| File | `handoff/components/07-plate-hatch.html` |

- Stroke widths ramp 1.5 → ~19 at a constant 13 gutter
- The solid block is the only thing that is not a line

#### 08 · Plate — index numeral — `.gfx-index-plate`

A card cover that is nothing but its index. Oversized numeral bleeding left, mono spec column right-aligned against it.

| | |
|---|---|
| Ground | paper |
| Sizing | Fluid |
| Motion | Static |
| File | `handoff/components/08-index-plate.html` |

- Numeral, three spec rows and the caption are all live text
- Numeral bleeds `-0.08em` left — never pad it back inside

### Loading & page transition

These extend `patterns/loading-sequence.html` and `patterns/page-sweep.html` with a determinate counter, an uneven-column wipe, a grid progress field and an indeterminate scan bar. Pick determinate or indeterminate honestly — never fake a percentage.

#### 09 · Loader — arc counter — `.gfx-load-arc`

A single accent arc against a hairline ring, with the count set in mono. No spinner, no easing bounce — linear fill only.

| | |
|---|---|
| Ground | ink |
| Sizing | Fixed |
| Motion | Driven |
| File | `handoff/components/09-load-arc.html` |

- `el.style.setProperty("--p", 0…1)` is the whole API
- The numeral is `[data-gfx-count]`; write the same value there, plus `aria-valuenow`
- The shipped file sweeps on CSS for the preview's sake (see *Demo blocks*). In production:

```js
function setArc(el, p){                      // p: 0…1
  el.style.setProperty('--p', p);
  el.setAttribute('aria-valuenow', Math.round(p * 100));
  el.querySelector('[data-gfx-count]').textContent =
    String(Math.round(p * 100)).padStart(2, '0');
}
```

#### 10 · Loader — stripe shutter — `.gfx-shutter`

The page sweep re-cut as uneven stripes: twelve columns of ink, vermillion and paper wiping top-to-bottom on a stagger. Hard linear wipe, nothing fades.

| | |
|---|---|
| Ground | paper |
| Sizing | Overlay |
| Motion | Driven |
| File | `handoff/components/10-shutter.html` |

- Add `.is-out` to run it; remove to reset — the demo loops it
- Column widths come from `flex-grow`, so it is resolution-free

#### 11 · Loader — grid fill — `.gfx-grid-fill`

A 9 × 5 field filling in reading order — a progress bar that is a grid, not a bar. Doubles as an empty-state placeholder.

| | |
|---|---|
| Ground | ink |
| Sizing | Fixed |
| Motion | Driven |
| File | `handoff/components/11-grid-fill.html` |

- Cell delay is `--d`, baked per cell; 0.035s step
- For real progress, set `--n` (cells lit) and drop the animation

#### 15 · Scan bar — `.gfx-scan`

The indeterminate twin of the arc counter. Nine uneven keylined segments with one accent block sweeping at constant speed — for waits whose length you do not know.

| | |
|---|---|
| Ground | ink |
| Sizing | Fluid |
| Motion | Driven |
| File | `handoff/components/15-scan.html` |

- Pure CSS, no script — mount it and it runs
- `linear` timing on purpose: a constant sweep is honest, an eased one implies progress it does not have
- Segment widths are `flex-grow` values, so it is resolution-free

### Progress & readouts

State, not decoration. Both read their state from classes or a data attribute, so server-rendered markup is already correct before any script runs.

#### 16 · Count-up stat — `.gfx-count`

An oversized numeral that counts to its target the first time it enters the viewport, with the accent rule drawing out beneath it. Feeds the existing stat-row pattern instead of replacing it.

| | |
|---|---|
| Ground | paper |
| Sizing | Fluid |
| Motion | Driven |
| File | `handoff/components/16-count.html` |

- Target comes from `data-gfx-count-to`; the rule width is `calc(var(--p) * 168px)`
- Runs once, on first sight — never re-triggers on scroll back
- Reduced motion jumps straight to the target

The shipped file animates on **CSS only** (see *Demo blocks* below) so it runs in the
catalogue preview. In production, delete the demo block and drive it:

```js
(function(){
  var els = [].slice.call(document.querySelectorAll('.gfx-count'));
  if (!els.length || typeof IntersectionObserver !== 'function') return;
  var reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  function run(fig){
    var n  = fig.querySelector('[data-gfx-count-to]');
    var to = parseInt(n.getAttribute('data-gfx-count-to'), 10) || 0;
    if (reduce) { n.textContent = to; fig.style.setProperty('--p', 1); return; }
    var t0 = performance.now(), dur = 900;
    requestAnimationFrame(function step(t){
      var p = Math.min(1, (t - t0) / dur);
      n.textContent = Math.round(p * to);
      fig.style.setProperty('--p', p.toFixed(3));
      if (p < 1) requestAnimationFrame(step);
    });
  }
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if (e.isIntersecting) { io.unobserve(e.target); run(e.target); } });
  }, { threshold:.4 });
  els.forEach(function(e){ io.observe(e); });
})();
```

Server-render the resting value (`<span … data-gfx-count-to="14">0</span>`) so the stat is
correct with JS off.

#### 17 · Step sequencer — `.gfx-steps`

A four-stage spine: completed stages keylined, the live one solid accent, the rest hairline. For a build log or a project-detail process strip — the one place the site needs ordered state.

| | |
|---|---|
| Ground | ink |
| Sizing | Fluid |
| Motion | Driven |
| File | `handoff/components/17-steps.html` |

- State is two classes: `.is-done` and `.is-now`. **No JS at all** — render the state server-side
- The spine is a single hairline behind the markers, not a border on each
- Four stages max — a fifth turns it into a chart. The spine `right:calc(25% - 14px)` assumes four equal columns; change the 25% if you change the count

### Corner marks & stamps

Furniture. Scatter sparingly — one stamp or one ticker per panel, never both. They are the only components here allowed to sit fully inside the frame.

#### 12 · Spec stamp — `.gfx-spec-stamp`

The FIG / REV / SHEET cluster from every plate corner, expanded to two rows with a bar cluster and one accent square.

| | |
|---|---|
| Ground | paper |
| Sizing | Fixed |
| Motion | Static |
| File | `handoff/components/12-spec-stamp.html` |

- `.tl` / `.tr` / `.bl` / `.br` pin it to any panel corner
- Rows are live text — three max, or it stops being a stamp

#### 13 · Crop marks — `.gfx-crop-marks`

Registration brackets and a target, set inside the panel padding. Print-shop furniture that frames a panel without boxing it.

| | |
|---|---|
| Ground | paper |
| Sizing | Overlay |
| Motion | Static |
| File | `handoff/components/13-crop-marks.html` |

- Inset via `--m` (default 22px)
- Drop `.gfx-crop-target` if a single corner set is enough

#### 14 · Edge ticker — `.gfx-edge-ticker`

A ruler rail hugging the panel edge: rotated mono label, 25 ticks, and an accent marker that travels with scroll position.

| | |
|---|---|
| Ground | ink |
| Sizing | Fluid |
| Motion | Scroll-reactive |
| File | `handoff/components/14-edge-ticker.html` |

- Marker position is `--sp` from the shared scroll script
- Rotate the label with `writing-mode` — never with a transform hack

## Placement map — where each one goes in `index.html`

| Section | Component | Note |
|---|---|---|
| `#home` hero | `gfx-arc-quadrant` or `gfx-stripe-fan` | One, not both. The arc suits the cream ground; the fan wants ink. |
| `#home` hero, second screen | `gfx-halftone-drift` | Opens as the panel enters — rewards the scroll the carousel already invites. |
| `#home` stats | `gfx-count` | Counts once, on first sight. Pairs with the existing stat-row meta column. |
| `#projects` cards | `gfx-plate-disc` / `gfx-plate-checker` / `gfx-plate-hatch` | Rotate through the three so no two adjacent bricks match. |
| `#projects` cards without a render | `gfx-index-plate` | The honest placeholder — an index, not a grey box. |
| `#project-detail` hero | `gfx-numeral-bleed` | Feed it `detail-hero-wm`'s number; retire the existing watermark span. |
| `#project-detail` process strip | `gfx-steps` | Brief → drawing → fabrication → test. Four stages, no more. |
| `#project-detail` left edge | `gfx-edge-ticker` | Reads as a sheet index down the long scroll. |
| Page transition | `gfx-shutter` | Replaces the three-bar sweep with twelve uneven columns. |
| Initial load | `gfx-load-arc` | Or `gfx-grid-fill` if you want the count to feel discrete. |
| Form submit / fetch | `gfx-scan` | The wait whose length you do not know. |
| `#contact` (ink) | `gfx-spec-stamp` | Bottom-right, under the form. |
| Any panel | `gfx-crop-marks` | Once per page at most. It is a joke that stops being funny on the third telling. |

## Accessibility

- Every graphic is `aria-hidden="true"` or carries `role="progressbar"`. None of them hold meaning.
- `gfx-load-arc` exposes `aria-valuenow`; keep it in sync if you drive it with real progress.
- `gfx-scan` is a `progressbar` with no value — correct for indeterminate.
- `gfx-steps` is an `<ol>`, so the order survives with styles off.
- Contrast: graphics sit at z-index 0 behind type at z-index 2. **Do not let the dense
  end of a ramp fall under body copy** — on the ink ground the vermillion is bright enough
  to swallow `--fg-2` text.
- `prefers-reduced-motion` is handled in the base reset (`animation:none`), in the scroll
  driver, and explicitly in the production count-up script.

## What would break these

Adding a colour. Rounding a corner. Putting one in a card with a margin instead of letting
it bleed. Easing an indeterminate sweep so it implies progress it does not have. Fitting
artwork politely inside the panel — a graphic with even margins on all four sides reads as
stock illustration; the crop *is* the identity.
