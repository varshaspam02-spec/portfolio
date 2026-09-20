# Srinjoy Ghosh · Portfolio

A cyberpunk portfolio for Srinjoy Ghosh, AI/ML engineer and researcher. Dark surfaces, mint-cyan and magenta accents, a responsive layout, and the original interactive ML playgrounds.

## Included

- Home and engineering profile, with selected work and writing.
- All 14 projects, with category filters, text search, technology tags, and repository links.
- Both original articles and their reading destinations.
- Seven locally hosted interactive ML labs, plus the original external object-detection demo.
- Contact page with email, phone, LinkedIn, and the author's GitHub profile.
- Keyboard navigation, visible focus styles, a mobile menu, reduced-motion support, and a motion toggle.
- Self-hosted fonts and pinned local JavaScript dependencies. The portfolio and seven local labs do not require a CDN connection.

## Run locally

No npm install or build service is required. With Python 3 installed, run this from the repository root:

```sh
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

## GitHub Pages

The checked-in HTML is ready to publish. In repository **Settings → Pages**, select **Deploy from a branch**, then **main** and **/ (root)**. The `.nojekyll` file enables direct static-file hosting. Links and assets use relative paths, so the site supports a GitHub Pages project subdirectory.

## Edit content

Edit `scripts/content.py`, then regenerate the pages:

```sh
python scripts/build.py
```

The shared visual system lives in `assets/styles.css`; navigation, search, filtering, and lab launch behavior live in `assets/main.js`.

Run the static integrity checks with Python and Node.js:

```sh
python scripts/check.py
```

Create a self-contained HTML preview and clean source ZIP in the adjacent `deliverables` directory:

```sh
python scripts/package_preview.py
```

The portable preview bundles all pages and lab dependencies into one file. Its links and lab launch buttons work through a preview-only router; the deployed website uses normal static HTML URLs.

## Labs

The original publicly embedded applications were migrated from the author's Google Site into `labs/`. Their numerical algorithms and interactions have been retained. The shared stylesheet and bridge add the new theme, responsive layouts, accessible control names, and iframe resizing.

Each lab launches on demand to avoid running expensive visualizations in the background. **Open full window** provides a dedicated workspace. CSV input in the tree builder is processed locally in the visitor's browser.

The original manifold demo uses handcrafted geometric projections; it is explicitly labeled as an illustrative concept demo. The attention demo uses simulated patterns and illustrative next-token probabilities. Neither is presented as a trained model or a numerical implementation of the named manifold algorithms.

To intentionally refresh the applications from their original public sources:

```sh
python scripts/migrate_labs.py --fetch
```

This preserves the documented presentation adjustments and vendors the pinned dependencies. Review upstream changes before committing refreshed code. Source URLs and local destinations are recorded in `docs/lab-provenance.json` and `docs/source-inventory.md`.

## Project structure

```text
index.html                 Home
projects/index.html        Searchable project archive
articles/index.html        Writing
contact/index.html         Contact
spaces/index.html          Lab directory
spaces/*/index.html        Lab introduction and workspace
labs/*.html                Original interactive applications
assets/                    Styles, scripts, fonts, and pinned dependencies
scripts/                   Content and reproducible page generation
docs/                      Content sources and migration notes
```

Third-party notices and font licenses are included in `assets/vendor/NOTICE.md` and `assets/fonts/`.
