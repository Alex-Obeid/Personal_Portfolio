# Alex Obeid — Personal Portfolio

A single-file, dependency-free personal portfolio site for a mechanical engineering
student/graduate. No build step, no framework, no package manager — open the HTML file
and it runs.

## Contents

| Path | What it is |
| --- | --- |
| `index.html` | The entire site: markup, CSS, and JS in one file |
| `favicon.svg` | "A•O" monogram favicon (also used as the Apple touch icon) |
| `Images/Headshot/` | Home-page portrait |
| `Images/Planetary Gearbox/` | Renders and build photos for the Planetary Gearbox project |

The only external dependency is Google Fonts (Bebas Neue, DM Sans, DM Mono), loaded from
a CDN. Everything else — icons, the noise overlay, the loading animation — is inline SVG
or CSS.

## Running it locally

Double-clicking the HTML file works for everything except one thing: nothing here needs a
server, so `file://` is fine.

If you prefer a local server (closer to how a host will serve it):

```bash
cd "LAU - Files/Projects/Website"
python -m http.server 8000
# then open http://localhost:8000/index.html
```

## Deploying

Hosted on GitHub Pages at [alex-obeid.github.io/Personal_Portfolio](https://alex-obeid.github.io/Personal_Portfolio/),
served from the `main` branch. Any other static host works too (Netlify, Cloudflare
Pages, plain FTP) — just upload `index.html`, `favicon.svg`, and the `Images/` folder,
preserving the folder structure and file-name casing (the repo's host is case-sensitive,
unlike Windows/macOS — see [Gotchas](#gotchas)).

## How the site works

### Routing

The site is a single-page app with no router library. Every `<section>` is a "page";
exactly one carries the `.active` class at a time and the rest are `display:none`.

- `navigate(target, options)` — the entry point. Plays the three-bar sweep transition,
  then calls `applySection()` at the 900 ms mark.
- `applySection(target)` — swaps the `.active` class, re-triggers `.fade-in` animations,
  updates `location.hash`, closes the mobile menu, scrolls to top.
- `routeFromHash()` — runs on load and on `hashchange`; unknown hashes fall back to
  `home`.

Sections: `home`, `projects`, `project-detail`, `contact`, `cv`, `easter`.

Transitions and the startup animation are both skipped under
`prefers-reduced-motion: reduce`.

### Projects

Project content lives in the `PROJECTS` array near the top of the `<script>` block. The
cards in the `#projects` section are hand-written HTML; clicking one calls
`openProject(idx)`, which reads `PROJECTS[idx]` and fills in the `#project-detail`
section (hero, title, body HTML, gallery, meta rows, tags).

**`idx` is a raw array index, and it does not match the number shown on the card.** The
card labelled `03` (Planetary Gearbox) calls `openProject(0)`, `01` calls
`openProject(1)`, `02` calls `openProject(2)`. Check the array, not the badge.

#### Adding a project

1. Add an entry to `PROJECTS`:

   ```js
   {
     num: '04',
     badge: 'Category · Discipline',      // shown top-left of the detail hero
     gradient: 'linear-gradient(135deg,#1a1400 0%,#2d1800 100%)',
     heroImage: 'Images/My Project/hero.png',  // optional; overrides `gradient`
     title: 'My Project',
     tags: ['SolidWorks', 'FEA'],
     meta: [{ k: 'Year', v: '2026' }, { k: 'Role', v: 'Design' }],
     body: `<p>Paragraphs of HTML.</p>`,
     gallery: [
       'Images/My Project/photo-1.jpg',   // image paths render as photos
       'Caption Only Tile',               // plain strings render as placeholder tiles
     ],
   }
   ```

   `gallery` entries ending in `.png/.jpg/.jpeg/.gif/.webp/.svg` are rendered as
   `<img>`; anything else becomes a grey placeholder tile with that text.

2. Copy the card markup of an existing `.proj-brick` inside the right
   `.projects-group` ("Main Projects" or "Side Projects") and point its `onclick` at the
   new index.

3. Pick a size class on the brick — `tall` (3:4), `wide` (16:9), `sq` (1:1),
   `short` (4:3), or `mini` (3:2) — and an accent class `ca`–`ch` for the gradient
   backdrop. These drive the masonry layout (`columns: 3`, dropping to 2 then 1 on
   narrow screens).

### Contact form

`handleForm()` validates the fields and shows a "Message Sent ✓" confirmation. **It does
not send anything** — there is no backend and no form service wired up. See
[Gotchas](#gotchas).

### Easter egg

The orange warning-triangle button in the footer opens `#easter`, a Snake game on a
420×420 canvas. It uses a fixed 130 ms timestep with interpolated rendering, WebAudio
blips for eating and dying, and `localStorage` for the best score (`snakeBest`) and score
history (`snakeScores`). Reaching 50 points wins. Keyboard input is only captured while
the `#easter` section is active.

### Styling

Everything hangs off the CSS custom properties in `:root` — change `--orange` /
`--orange2` to re-theme the whole site. The palette is deliberately dark-only; there is
no light theme. Layout breakpoints are 1000px and 580px for the masonry, and 768px for
the mobile nav and general spacing.

## Gotchas

- **Image paths are case-sensitive on the deploy target.** Windows and macOS don't care
  if `Images/Main-Render.png` is referenced as `images/main-render.png`; GitHub Pages
  (Linux-backed) does, and a mismatch 404s in production without any error locally. All
  current references match the on-disk casing exactly — keep it that way when adding
  images.
- **The contact form is decorative.** Anyone who fills it in gets a success message and
  their message goes nowhere. Wire it to Formspree / Web3Forms / a `mailto:` fallback, or
  replace it with the email link that's already in the footer.
- **The home bio is `contenteditable`.** Visitors can type over it. Edits aren't saved
  anywhere — it's a leftover from the template it started from.
- **Project cards are `<div onclick>`.** They can't be reached by keyboard or announced
  by a screen reader as interactive.
- **No print stylesheet.** The CV page's "Download / Print CV" button calls
  `window.print()`, which prints the dark theme as-is.
