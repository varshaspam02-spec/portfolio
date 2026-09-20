# Srinjoy Ghosh · Portfolio

A portfolio for Srinjoy Ghosh, AI/ML engineer and researcher. A living aurora backdrop, glass surfaces, large fluid typography, morphing page transitions, and the original interactive ML playgrounds.

## Included

- Home and engineering profile, with selected work and writing.
- All 14 projects, with category filters, text search, technology tags, and repository links.
- Both original articles and their reading destinations.
- Seven locally hosted interactive ML labs, plus the original external object-detection demo.
- Contact page with email, phone, LinkedIn, and the author's GitHub profile.
- Keyboard navigation, visible focus styles, a mobile menu, reduced-motion support, and a motion toggle.
- Three accent themes (Aurora, Ember, Acid), switchable from the header or footer and remembered between visits.
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

The shared visual system lives in `assets/styles.css`; navigation, search, filtering, pointer effects, themes, and lab launch behavior live in `assets/main.js`. The WebGL aurora backdrop and the hero's morphing point cloud live in `assets/fx.js`.

### Design system

- **Tokens.** Colors, radii, easing, and font stacks are CSS custom properties at the top of `assets/styles.css`. Each accent theme only overrides `--a1`, `--a2`, `--a3`, and `--warm`; the canvases read the same variables, so a new theme is one CSS rule plus an entry in `THEMES` in `scripts/build.py`. To change the default theme, edit the `:root` values.
- **Type.** Geist (variable, 100 to 900) for interface and headlines, Instrument Serif Italic for the gradient accent words (`<em>` inside a headline), and Geist Mono for labels.
- **Page transitions.** Navigation uses the cross-document View Transitions API: the next page opens from the click point, while the nav indicator, lab visuals, and project cards travel to their new positions through matching `view-transition-name` values. Browsers without support navigate normally.
- **Motion.** Every animation respects the footer toggle and the operating system's reduced-motion setting. With motion off, the backdrop and point cloud hold a still frame.
- **Progressive enhancement.** Content is fully readable without JavaScript or WebGL. A CSS gradient backdrop stands in when WebGL is unavailable.

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

The playgrounds began as the embedded applications on the author's Google Site. They have since been rebuilt by hand on a shared lab kit: `assets/lab.css` for the interface and `assets/lab-bridge.js` for data colours, marker shapes, colour ramps, responsive canvases, tooltips and theme sync. `docs/lab-kit.md` documents the kit, and `labs/k-means.html` is the reference implementation. Each lab keeps its original algorithm; the interface, colour encoding, responsiveness and a number of bugs were redone.

Data colours come from a palette validated for colour-vision deficiency and contrast on the plot surface. Clusters and other categories use fixed colours paired with marker shapes, magnitudes use a one-hue ramp, and signed values use a blue to grey to red scale. Interface accents follow the site's accent theme live, even though each lab runs in a sandboxed frame.

Each lab launches on demand to avoid running expensive visualizations in the background. **Open full window** provides a dedicated workspace. CSV input in the tree builder is processed locally in the visitor's browser.

The original manifold demo uses handcrafted geometric projections; it is explicitly labeled as an illustrative concept demo. The attention demo uses simulated patterns and illustrative next-token probabilities. Neither is presented as a trained model or a numerical implementation of the named manifold algorithms.

To fetch the untouched originals for comparison:

```sh
python scripts/migrate_labs.py --fetch
```

This saves them to a folder outside the repository and never writes into `labs/`. Source URLs and local destinations are recorded in `docs/lab-provenance.json` and `docs/source-inventory.md`.

## Project structure

```text
index.html                 Home
projects/index.html        Searchable project archive
articles/index.html        Writing
contact/index.html         Contact
spaces/index.html          Lab directory
spaces/*/index.html        Lab introduction and workspace
labs/*.html                Interactive playgrounds built on the lab kit
assets/                    Styles, scripts, fonts, and pinned dependencies
scripts/                   Content and reproducible page generation
docs/                      Content sources and migration notes
```

Third-party notices and font licenses are included in `assets/vendor/NOTICE.md` and `assets/fonts/`.
