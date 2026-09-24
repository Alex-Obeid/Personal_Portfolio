# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file, dependency-free personal portfolio. `index.html` (~200 KB) holds all markup,
CSS and JS. No build step, no framework, no package manager, no tests. The only external
dependency is Google Fonts.

`README.md` (~34 KB) and `DESIGN-SYSTEM.md` (~18 KB) are thorough. **Grep them for the
section you need rather than reading them whole** — the same goes for `index.html`, which is
~56k tokens.

## Commands

`file://` works for everything. For a server:

```bash
python -m http.server 5500
```

There is no build, lint or test command. Four optional generators:

```bash
python tools/build-icons.py           # → icons/ · 5 PNGs + favicon.ico
python tools/build-logo-masks.py      # → images/company-logos/masks/ + writes into index.html
python tools/build-design-system.py   # → design-system/ (23 preview cards + stylesheets)
python tools/build-banner.py          # → docs/banner.png + palette.png
```

**Edit the generator, never its output.** `build-logo-masks.py` is the one that writes *into*
`index.html`, replacing everything between the `══ masks: generated … ══` and `══ end masks ══`
comments. Hand edits there are silently discarded.

## Architecture

### Routing

A hash-routed SPA with no router library. Every `<section>` is a page; exactly one carries
`.active`, the rest are `display:none`. Sections: `home`, `projects`, `project-detail`,
`contact`, `cv`, `easter`.

`navigate()` plays the three-bar sweep and calls `applySection()` at 730 ms. `routeFromHash()`
runs on load and `hashchange`.

### Territories

Colour is applied as **territories** — full-bleed panels carrying `data-territory="ink"` or
`="vermillion"` that redefine semantic custom properties. Three brand colours only: `--paper`
`#f0ebe1`, `--ink` `#0a0a0a`, `--orange` `#f05a00`.

**Build against the semantic tokens (`--fg`, `--bg`, `--accent`, `--rule`), never the raw brand
colours.** A component using `var(--ink)` disappears on the Ink panel. On the vermillion ground
`--accent` resolves to ink, not orange.

### Momentum scrolling — the thing most likely to bite

Desktop scrolling is eased in JS: a rAF loop lerps the **real document scroll position**
(not a transformed wrapper, which would break the `position:sticky` three sections depend on).

> **Scroll-linked animation is driven from `ssApply()`, not the `scroll` event.** Programmatic
> scrolls fire `scroll` unreliably. `ssApply()` calls `updateCylinder`, `updateSoftwareReel`,
> `updateParallax`, `updateGfxScroll`, `updateNavTerritory`, `updateCanvasTerritory`. Anything
> new that tracks scroll position belongs there too.

Touch is excluded (`pointer:fine`) and the whole thing is off under `prefers-reduced-motion`.

### The pinned-stage pattern

Three home panels pin a stage and consume scroll from a tall wrapper. Same shape each time —
wrapper `height: 100vh + n × step`, a `position:sticky; top:0; height:100vh` child, and a JS
`update*()` that derives progress from `-wrapper.getBoundingClientRect().top / (offsetHeight - vh)`:

| Panel | Wrapper | Step |
| --- | --- | :-: |
| 02 Project gallery | `.px-wrap` | horizontal parallax |
| 03 Skills | `.cyl-wrap` | `--cyl-step` 64vh |
| 04 Software reel | `.sw-sect` | `--sw-step` 40vh |

Each falls back to a static layout on touch / reduced motion, because pinning a multi-screen
stage would swallow vertical swipes.

Use `getBoundingClientRect()`, never `offsetTop` — `.terr` is `position:relative`, so
`offsetTop` is relative to the panel, not the document.

### Section slivers

The numbers are not in the markup. Each mark is an empty `<span class="spec-mark"
data-section="Name">`, and `numberSections()` walks `#home [data-section]` in DOM order filling
in `Name · NN`. Insert, remove or reorder a panel and the rest renumber themselves.

## Invariants

- **`overflow:clip`, never `overflow:hidden`** on panels. `hidden` creates a scroll container
  and kills `position:sticky`. Note `clip` opens no block formatting context, so margins still
  collapse through it.
- **No shadows anywhere.** Hover and press invert colour instead. `--snap`
  (`.16s cubic-bezier(.4,0,.2,1)`) is the standard transition.
- **Hairlines, not borders** — `1px`. Weight comes from type, not from thicker rules.
- **`openProject(idx)` takes a raw array index that does not match the card badge.** Append to
  `PROJECTS`, never insert, or every existing handler repoints.
- **Everything under `images/` and `icons/` is lowercase kebab-case, no spaces.** Deploy is
  Linux-backed and case-sensitive; Windows is not, so a mismatch 404s only in production.
- **`mask-image` is CORS-restricted** and Chrome gives every `file://` document an opaque
  origin. Masks must be inlined as `data:` URIs or the element paints *nothing* when the page
  is opened from disk.
- **Never put a `transform` on an ancestor of `.sw-list li`** — it would make that element a
  containing block and collapse `background-attachment:fixed` to `scroll`, killing the reel's
  highlight. Move things with `top` instead.
- **Text fitting must wait for fonts.** `layoutCylinder()` measures rendered text width and
  re-runs on `document.fonts.ready`; fallback metrics oversize by ~13%.

## Editing this file safely

`index.html` is one very large file, so edits are usually scripted. Two mistakes have already
cost real damage here:

- **Never `.replace()` a single letter as a placeholder.** A `.replace('D', '—')` turned
  `'DM Mono'` into `'—M Mono'` and `Design` into `—esign`.
- **Anchor slices on text you have just verified is unique.** A slice anchored on
  `/* Was a .62rem mono label` matched a *different* rule's comment and deleted ten rules
  between it and the next anchor.

After a scripted edit, verify: the file still decodes as UTF-8, `{` and `}` balance, and
`grep` finds the new text exactly once.

## Known debt

Documented in the README's Gotchas, but worth knowing before you touch related code: the
contact form is decorative (validates, sends nothing); project cards are `<div onclick>` and
not keyboard-reachable; the home bio is `contenteditable` and edits save nowhere; there is no
print stylesheet; images are unoptimised; most project galleries are labelled placeholder
tiles, not real photography.

## Other agent configs

A Codex config exists at `~/.codex`. To bring any of it across (MCP servers, slash commands,
subagents, skills, instructions), reply `/import` to scan and list what's importable, then
`/import --yes=<digest>` using the digest the scan prints. If `/import` isn't available on this
surface, run `claude import` from a terminal instead.
