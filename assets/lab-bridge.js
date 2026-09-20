/* Lab kit runtime. Load this synchronously in <head> so window.SGLab exists before a lab's own script runs.
   Only layout height is sent to the embedding portfolio; the theme name is the only thing received from it. */
window.SGLab = (() => {
  'use strict';
  const root = document.documentElement;
  const embedded = parent !== window;
  if (embedded) root.classList.add('is-embedded');
  const params = new URLSearchParams(location.search);

  /* ----------------------------------------------------------------- Theme */
  const THEMES = ['aurora', 'ember', 'acid'];
  const themeListeners = new Set();
  function applyTheme(name) {
    if (!THEMES.includes(name)) return;
    if (name === THEMES[0]) delete root.dataset.theme; else root.dataset.theme = name;
    themeListeners.forEach(listener => listener(name));
  }
  let initialTheme = params.get('theme');
  if (!initialTheme && !embedded) { try { initialTheme = localStorage.getItem('sg-theme'); } catch { /* Storage may be blocked. */ } }
  if (initialTheme) applyTheme(initialTheme);
  addEventListener('message', event => {
    if (event.source === parent && event.data?.type === 'sg-theme') applyTheme(event.data.theme);
  });
  const reducedMotion = params.get('motion') === 'off' || matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------- Colour */
  // Validated on the dark plot surface (#0b0d16): lightness band, chroma floor, adjacent CVD and
  // normal-vision separation, 3:1 contrast. Assign slots in this order and never cycle past eight.
  // Only the first three stay distinct when any two marks can touch (scatter), so scatter plots
  // pair each slot with its own marker shape.
  const SERIES = ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9', '#e66767'];
  const SHAPES = ['circle', 'square', 'triangle', 'diamond', 'triangle-down', 'plus', 'cross', 'hexagon'];
  // One-hue sequential ramp. On a dark surface "near zero" recedes into it and magnitude gets lighter.
  const SEQUENTIAL = ['#0b1a33', '#0d366b', '#184f95', '#256abf', '#3987e5', '#6da7ec', '#9ec5f4', '#cde2fb'];
  // Two opposite hues around a neutral grey midpoint, equal steps per arm.
  const NEGATIVE = ['#383835', '#1c5cab', '#3987e5', '#86b6ef'];
  const POSITIVE = ['#383835', '#a33f3f', '#e66767', '#f4aaaa'];

  const toRGB = hex => [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16));
  function sample(stops, t) {
    const x = Math.min(1, Math.max(0, Number.isFinite(t) ? t : 0)) * (stops.length - 1);
    const i = Math.min(stops.length - 2, Math.floor(x));
    const a = toRGB(stops[i]), b = toRGB(stops[i + 1]), f = x - i;
    return a.map((v, k) => Math.round(v + (b[k] - v) * f));
  }
  const css = (name, fallback) => getComputedStyle(root).getPropertyValue(name).trim() || fallback;

  /* --------------------------------------------------------------- Markers */
  function tracePath(ctx, shape, x, y, r) {
    ctx.beginPath();
    const poly = points => { points.forEach(([px, py], i) => (i ? ctx.lineTo(x + px * r, y + py * r) : ctx.moveTo(x + px * r, y + py * r))); ctx.closePath(); };
    const plus = [[-.38, -1.15], [.38, -1.15], [.38, -.38], [1.15, -.38], [1.15, .38], [.38, .38], [.38, 1.15], [-.38, 1.15], [-.38, .38], [-1.15, .38], [-1.15, -.38], [-.38, -.38]];
    switch (shape) {
      case 'square': poly([[-.9, -.9], [.9, -.9], [.9, .9], [-.9, .9]]); break;
      case 'triangle': poly([[0, -1.2], [1.1, .8], [-1.1, .8]]); break;
      case 'triangle-down': poly([[0, 1.2], [1.1, -.8], [-1.1, -.8]]); break;
      case 'diamond': poly([[0, -1.25], [1.05, 0], [0, 1.25], [-1.05, 0]]); break;
      case 'plus': poly(plus); break;
      case 'cross': poly(plus.map(([px, py]) => [(px - py) * .7071, (px + py) * .7071])); break;
      case 'hexagon': poly([0, 1, 2, 3, 4, 5].map(k => [Math.cos(k * Math.PI / 3) * 1.12, Math.sin(k * Math.PI / 3) * 1.12])); break;
      default: ctx.arc(x, y, r, 0, Math.PI * 2);
    }
  }
  // Draws series `slot` as its colour and shape, separated from neighbours by a ring of the plot surface.
  function marker(ctx, slot, x, y, r, options = {}) {
    const index = ((slot % SERIES.length) + SERIES.length) % SERIES.length;
    tracePath(ctx, options.shape || SHAPES[index], x, y, r);
    ctx.fillStyle = options.color || SERIES[index];
    ctx.fill();
    if (options.ring !== false) {
      ctx.lineWidth = options.ringWidth || Math.max(1, r * .4);
      ctx.strokeStyle = options.ringColor || css('--plot', '#0b0d16');
      ctx.stroke();
    }
  }

  /* ---------------------------------------------------------------- Canvas */
  // Keeps a fixed logical coordinate space (so the maths never changes) while the backing store
  // follows the element's real size and the device pixel ratio.
  function fitCanvas(canvas, logicalWidth, logicalHeight, draw) {
    const ctx = canvas.getContext('2d');
    const view = {
      ctx, width: logicalWidth, height: logicalHeight, scale: 1, dpr: 1,
      // A length in CSS pixels, expressed in logical units: marks keep their on-screen size.
      px: n => n / view.scale,
      // Like px(), but marks shrink a little on narrow plots so dense data does not turn into blobs.
      mark: n => n * Math.min(1, Math.max(.6, view.scale * 1.5)) / view.scale,
      toLogical(event) {
        const rect = canvas.getBoundingClientRect();
        return { x: (event.clientX - rect.left) / rect.width * logicalWidth, y: (event.clientY - rect.top) / rect.height * logicalHeight };
      },
      toClient(x, y) {
        const rect = canvas.getBoundingClientRect();
        return { x: rect.left + x / logicalWidth * rect.width, y: rect.top + y / logicalHeight * rect.height };
      },
      begin() {
        ctx.setTransform(view.scale * view.dpr, 0, 0, view.scale * view.dpr, 0, 0);
        ctx.clearRect(0, 0, logicalWidth, logicalHeight);
      },
    };
    canvas.style.aspectRatio = `${logicalWidth} / ${logicalHeight}`;
    let live = false;
    function resize() {
      const cssWidth = canvas.clientWidth || logicalWidth;
      view.dpr = Math.min(2, devicePixelRatio || 1);
      view.scale = cssWidth / logicalWidth;
      canvas.width = Math.max(1, Math.round(cssWidth * view.dpr));
      canvas.height = Math.max(1, Math.round(cssWidth * logicalHeight / logicalWidth * view.dpr));
      if (live && draw) draw();
    }
    resize();
    // The caller's `const view = fitCanvas(...)` is still being assigned right now, and its draw()
    // needs `view`. Painting starts once the calling script has finished initialising.
    queueMicrotask(() => { live = true; if (draw) draw(); new ResizeObserver(resize).observe(canvas); });
    return view;
  }

  /* --------------------------------------------------------------- Tooltip */
  let tip = null;
  const tooltip = {
    show(clientX, clientY, html) {
      if (!tip) { tip = document.createElement('div'); tip.className = 'lab-tip'; tip.setAttribute('role', 'tooltip'); document.body.append(tip); }
      tip.innerHTML = html;
      tip.classList.add('is-on');
      const box = tip.getBoundingClientRect();
      const x = Math.min(innerWidth - box.width - 8, Math.max(8, clientX + 14));
      const y = clientY + 18 + box.height > innerHeight ? clientY - box.height - 12 : clientY + 18;
      tip.style.transform = `translate(${Math.round(x)}px,${Math.round(Math.max(8, y))}px)`;
    },
    hide() { tip?.classList.remove('is-on'); },
  };
  const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  /* ------------------------------------------------------------------ Page */
  function syncRanges(scope = document) {
    scope.querySelectorAll('input[type=range]').forEach(input => {
      const min = Number(input.min || 0), max = Number(input.max || 100);
      input.style.setProperty('--p', `${max > min ? (Number(input.value) - min) / (max - min) * 100 : 0}%`);
    });
  }
  function status(el, state, text) {
    if (!el) return;
    el.dataset.state = state;
    el.textContent = text;
  }

  let lastHeight = 0;
  let queued = false;
  function reportSize() {
    queued = false;
    const height = Math.ceil(document.body.getBoundingClientRect().height + 12);
    if (Math.abs(height - lastHeight) > 3) {
      lastHeight = height;
      if (embedded) parent.postMessage({ type: 'sg-lab-height', height }, '*');
    }
  }
  function queueSize() {
    if (!queued) { queued = true; requestAnimationFrame(reportSize); }
  }
  function ready() {
    // Restore accessible names for controls whose labels are visual only.
    for (const control of document.querySelectorAll('input,select,textarea')) {
      if (control.type === 'hidden' || control.getAttribute('aria-label') || control.labels?.length) continue;
      const group = control.closest('.field,.control,.control-group,.row,.setting-group') || control.parentElement;
      const label = group?.querySelector('label,.label,.control-label');
      const text = label?.textContent.trim() || control.placeholder || control.id.replace(/[-_]/g, ' ');
      if (text) control.setAttribute('aria-label', text);
    }
    document.querySelectorAll('canvas:not([aria-label]):not([aria-hidden])').forEach(canvas => {
      canvas.setAttribute('role', 'img');
      canvas.setAttribute('aria-label', 'Interactive algorithm visualization');
    });
    syncRanges();
    document.addEventListener('input', event => { if (event.target.type === 'range') syncRanges(event.target.parentElement); });
    new ResizeObserver(queueSize).observe(document.body);
    addEventListener('load', queueSize);
    addEventListener('resize', queueSize);
    queueSize();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready); else ready();

  return {
    embedded, reducedMotion,
    series: SERIES, shapes: SHAPES,
    color: slot => SERIES[((slot % SERIES.length) + SERIES.length) % SERIES.length],
    shape: slot => SHAPES[((slot % SHAPES.length) + SHAPES.length) % SHAPES.length],
    marker, tracePath,
    rampRGB: t => sample(SEQUENTIAL, t),
    ramp: t => `rgb(${sample(SEQUENTIAL, t).join(',')})`,
    divergingRGB: t => sample(t < 0 ? NEGATIVE : POSITIVE, Math.abs(t)),
    diverging: t => `rgb(${sample(t < 0 ? NEGATIVE : POSITIVE, Math.abs(t)).join(',')})`,
    rampCSS: `linear-gradient(90deg,${SEQUENTIAL.join(',')})`,
    divergingCSS: `linear-gradient(90deg,${[...NEGATIVE].reverse().concat(POSITIVE.slice(1)).join(',')})`,
    // Chart chrome, read from the stylesheet so plots and interface always agree.
    ink: () => css('--ink', '#f4f3ef'),
    muted: () => css('--muted', '#a3a6b8'),
    faint: () => css('--faint', '#6f7286'),
    grid: () => css('--grid', '#1a1d2b'),
    axis: () => css('--axis', '#2d3147'),
    plot: () => css('--plot', '#0b0d16'),
    unassigned: () => css('--unassigned', '#7b7f93'),
    accent: n => css(`--a${n}`, '#4aa3ff'),
    onTheme(listener) { themeListeners.add(listener); return () => themeListeners.delete(listener); },
    fitCanvas, tooltip, escapeHTML, syncRanges, status, resize: queueSize,
  };
})();
