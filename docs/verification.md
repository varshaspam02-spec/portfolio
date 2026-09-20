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
