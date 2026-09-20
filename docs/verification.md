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

