# Verification record

20 September 2026

- All 12 original Google Sites pages were inspected, including rendered content inside the embedded applications.
- All 14 linked project READMEs were retrieved and reviewed.
- The Medium article, quantization explorer, and external object-detection page were retrieved.
- Generated 12 main portfolio/lab-wrapper pages, a 404 page, and eight original embedded documents (seven labs plus the clustering comparison table).
- `python scripts/check.py` passes: 21 HTML documents; 238 local links and resources; unique IDs; document language and titles; local font assets; syntax checks for application JavaScript and the original inline lab scripts.
- Lab algorithms were retained. Changes inside the migrated documents are dependency paths, shared styles, accessibility/resize helpers, explanatory notes, and PCA canvas colors.
- The portable preview's bundled page scripts were separately syntax checked.

## Remaining verification

Live visual QA and browser interaction testing of the rebuilt pages have not been completed. The available cloud browser rejected the local file preview under its URL policy. The next verification should inspect the deployed GitHub Pages site at desktop and phone widths, exercise project filtering and the mobile menu, and launch each playground.

The checked-in static files are ready for GitHub Pages. Deployment settings and live browser verification are separate from the static checks recorded above.

## Visual redesign

20 September 2026

- Replaced the visual system (typography, color, layout, motion) without changing the content in `scripts/content.py` or the lab algorithms. The lab theme received a palette and radius update plus a contrast fix for inline stat labels.
- `python scripts/check.py` passes: 21 HTML documents; 264 local links and resources.
- Rendered in headless Chrome at 1440x900, 1024x768, 820x1180, and 390x844 (phone emulation): home, projects, spaces, a lab page, articles, contact, and 404. No console errors or uncaught exceptions on the pages served locally. The 404 page resolves its assets only under `/portfolio/`, as before.
- Exercised: project filtering and search, the empty state, all three accent themes, the mobile menu, hover states (spotlight, tilt, cursor labels), all five point-cloud shapes, click navigation between pages, and launching the K-Means playground inside the new shell.
- `python scripts/package_preview.py` now runs on Windows; it previously failed with a `UnicodeEncodeError` because files were written with the system code page.

### Remaining verification

- Cross-document page transitions were exercised in Chromium only. Safari 18.2+ supports them; Firefox falls back to normal navigation. Neither was tested here.
- Animation smoothness and GPU cost were not measured on real hardware; headless rendering used a software rasterizer.
- The deployed GitHub Pages site has not been checked after this change.

## Playground rebuild

20 September 2026

- All seven playgrounds and the clustering comparison table were rebuilt on the lab kit (`docs/lab-kit.md`). `assets/lab-theme.css`, the old `!important` override sheet, was removed; nothing references it.
- `python scripts/check.py` passes: 21 HTML documents; 278 local links and resources; every inline lab script passes `node --check`.
- Each lab was exercised in headless Chrome standalone at 1240x900 and in phone emulation at 390x844, then launched inside the sandboxed frame on its portfolio page. No console errors or uncaught exceptions, and no horizontal overflow at 390px, in any of them.
- Data colours: the categorical palette was run through a palette validator against the plot surface `#0b0d16` (lightness band, chroma floor, adjacent colour-vision-deficiency separation, normal-vision separation, 3:1 contrast: all pass). Only the first three slots stay distinct when any two marks can touch, so scatter plots pair every slot with a marker shape.
- The decision tree's new sample, Fisher's Iris (150 rows), was checked against the published dataset: overall and per-species column means match exactly. On it the lab grows the textbook CART tree (root split `petal_length <= 2.45`).
- The gradient descent lab checks each analytic gradient against a central finite difference on load; the largest relative gap measured was 6.6e-10.

Defects fixed, by lab:

- K-Means: status stuck on "Running" after convergence; 148 points for N=150 (remainder dropped); near-identical cluster colours; Reset during a run threw a TypeError; raising K after initialisation crashed the assignment step; an unbounded search loop when placing cluster centres.
- PCA: white panels with invisible titles; 198 points for N=200; the 3D view drew no points before the first run.
- Decision tree: root label clipped and the tree unfitted; errors shown through `alert()`, which the sandbox blocks.
- Neural network: visualization tabs blank on load; the label defaulted to 0 with auto-correct on, so Predict taught the network that any non-zero drawing was a 0; training could be started twice at once.
- Gradient descent: learning-rate and momentum sliders had no effect until the optimizer type changed; momentum and Adam state carried over between runs; pressing Play repeatedly multiplied the speed; a diverged run was silently moved to the origin; the self-test took a real step; display settings wiped the run; smoothing was baked into stored values; step labels drifted after 1,000 steps; contour lines were mostly missing because of a bit-mask comparison bug in the marching-squares code.
- Attention: Sankey labels and next-token bars unreadable; duplicate tokens now get separate lanes; more than 10 tokens are capped with a message.
- Manifold: rainbow colouring replaced by a one-hue ramp shared by both views; default camera now shows each dataset as a surface.

### Remaining verification

- Real devices, Safari and Firefox were not tested. Touch drawing and drag-to-rotate were only driven with synthetic pointer events.
- The SVG and JSON exports in the tree builder report success, but the downloaded files were not opened and inspected.
- Frame rate was not measured on real hardware; headless rendering used a software rasterizer.
- Fonts inside the sandboxed lab frames fall back to the system font on a plain local server, because it sends no CORS header. GitHub Pages does send `Access-Control-Allow-Origin: *`, which was confirmed on the live site.

