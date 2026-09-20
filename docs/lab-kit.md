# Lab kit

Every playground in `labs/` is a standalone HTML document built on two shared files:

- `assets/lab.css` supplies the interface: tokens, layout, panels, controls, data display.
- `assets/lab-bridge.js` supplies `window.SGLab`: data colours, marker shapes, colour ramps, a responsive canvas helper, a tooltip, theme sync with the portfolio, and iframe height reporting.

`labs/k-means.html` is the reference implementation. Read it before building or changing a lab.

## Document skeleton

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>… playground | Srinjoy Ghosh</title>
<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
<link rel="stylesheet" href="../assets/lab.css">
<script src="../assets/lab-bridge.js"></script>   <!-- synchronous on purpose: SGLab must exist first -->
<style>/* only rules specific to this lab's plots */</style>
</head>
<body>
<div class="lab">
  <header class="lab-head">…back link + h1…</header>          <!-- hidden automatically when embedded -->
  <aside class="lab-note">…</aside>                            <!-- optional honesty note -->
  <div class="lab-app">                                        <!-- add .side-wide for a 380px sidebar -->
    <aside class="lab-side"><section class="group">…</section></aside>
    <main class="lab-stage"><div class="panel">…</div></main>
  </div>
</div>
<script>(() => { 'use strict'; … })();</script>
</body>
</html>
```

On screens under 860px the stage moves above the sidebar, so the main actions live in the panel's `.toolbar`, next to the plot.

## Components

| Class | Use |
|---|---|
| `.group` + `.group-title` | A sidebar card and its mono heading. `details.group` makes it collapsible. |
| `.panel`, `.panel-head` (h2 + `.toolbar`), `.panel-body`, `.plot`, `.statusbar` | A stage card. `.plot` owns the opaque chart surface. |
| `.stage-grid` | Auto-fitting grid for several panels. |
| `.field` (label + `output` + control), `.field-pair`, `.hint` | Form rows. Range inputs get their filled track automatically. |
| `.btn`, `.btn-primary`, `.btn-ghost`, `.btn-danger`, `.btn-block`, `.btn-row` | Buttons. One primary action per toolbar. |
| `.seg`, `.tabs` / `.tab` | Segmented control and tabs (`aria-pressed` / `aria-selected`). |
| `.check` | Checkbox rendered as a switch. |
| `.stat-grid` / `.stat` (`.stat-label`, `.stat-value`) | Stat tiles. Proportional figures. |
| `.kv` | Definition list for label and value rows. |
| `.chip`, `.chip-row` | Small mono tags. |
| `.legend` | Legend list. Text stays in ink; only the swatch is coloured. |
| `.scale` (`.scale-bar`, `.scale-ends`) | Legend for a colour ramp. |
| `.explain`, `.lab-note` | Body copy and the honesty note. |
| `.table-wrap` + `table` | Data tables. |
| `.statusbar[data-state]` | `idle`, `running`, `done`, `warn`, `error`. Set it with `SGLab.status(el, state, text)`. |

## `SGLab`

| Member | Purpose |
|---|---|
| `series`, `color(slot)` | The eight categorical colours, in fixed order. |
| `shapes`, `shape(slot)`, `marker(ctx, slot, x, y, r, options)` | Marker per slot. `options`: `color`, `shape`, `ring`, `ringWidth`, `ringColor`. |
| `ramp(t)`, `rampRGB(t)`, `rampCSS` | One-hue sequential ramp, `t` in 0..1. |
| `diverging(t)`, `divergingRGB(t)`, `divergingCSS` | Blue to grey to red, `t` in -1..1. |
| `ink()`, `muted()`, `faint()`, `grid()`, `axis()`, `plot()`, `unassigned()`, `accent(n)` | Chart chrome read from the stylesheet. |
| `fitCanvas(canvas, width, height, draw)` | Fixed logical coordinates with a crisp, responsive backing store. Returns `{ctx, begin(), px(n), mark(n), toLogical(event), toClient(x, y), scale, dpr}`. Call `view.begin()` at the top of `draw`. The first `draw` runs after your script finishes initialising. |
| `tooltip.show(clientX, clientY, html)`, `tooltip.hide()`, `escapeHTML(text)` | One shared tooltip. Escape any user-supplied text. |
| `status(el, state, text)`, `syncRanges()`, `resize()` | Status bar, refresh range fills after setting `value` from code, re-report height. |
| `onTheme(listener)`, `embedded`, `reducedMotion` | Redraw on theme change; skip non-essential animation when `reducedMotion` is true. |

## Data colour rules

These follow a validated method, so do not pick colours by eye.

1. **Categorical** (which series): use `SGLab.color(slot)` in slot order. Never cycle past eight, never invent a ninth, and never recolour a series when another is filtered out. The palette passes lightness, chroma, colour-vision-deficiency and contrast checks on `--plot`.
2. **Scatter plots**: only the first three slots stay distinct when any two marks can sit side by side, so draw points with `SGLab.marker`, which pairs every slot with its own shape.
3. **Sequential** (how much): `SGLab.ramp`. One hue, and on this dark surface low values recede while high values get lighter. No rainbow or multi-hue colormaps. Show a `.scale` legend.
4. **Diverging** (which side of zero): `SGLab.diverging`. The midpoint is neutral grey.
5. **Status** (`--good`, `--warning`, `--serious`, `--critical`) means state only, always with an icon or label. Never use it as "series 4".
6. Text, values and legend labels wear `--ink`, `--muted` or `--faint`, never a series colour. Put a coloured swatch beside the text instead.
7. Grids and axes are solid hairlines in `SGLab.grid()` / `SGLab.axis()`. No dashed grids. Lines are about 2px, markers at least 8px across, with a ring of `SGLab.plot()` where marks overlap.
8. Two or more series always get a legend. Inspectable marks get a hover tooltip, and the value must also be readable without hovering.

## Behaviour rules

- Keep each lab's algorithm and its documented controls. Presentation, layout and bugs are fair game.
- Guard timers with a token (see `cancel()` and `later()` in the reference) so Reset or a parameter change during a run cannot fire a stale step.
- Counts shown to the user must match what was asked for.
- No emoji in the interface and no network requests. Third-party libraries come from `assets/vendor/`.
- Inline scripts must pass `node --check`; `python scripts/check.py` enforces this along with unique IDs, a `<title>` and `lang`.
