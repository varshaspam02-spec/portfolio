/* Only layout information is sent to the embedding portfolio. */
(() => {
  'use strict';
  let lastHeight = 0;
  let queued = false;
  function reportSize() {
    queued = false;
    const height = Math.ceil(document.body.getBoundingClientRect().height + 12);
    if (Math.abs(height - lastHeight) > 3) {
      lastHeight = height;
      if (parent !== window) parent.postMessage({ type: 'sg-lab-height', height }, '*');
    }
  }
  function queueSize() {
    if (!queued) { queued = true; requestAnimationFrame(reportSize); }
  }
  // Restore accessible names for original controls whose labels were visual only.
  for (const control of document.querySelectorAll('input,select,textarea')) {
    if (control.type === 'hidden' || control.getAttribute('aria-label') || control.labels?.length) continue;
    const group = control.closest('.control,.control-group,.row,.setting-group') || control.parentElement;
    const label = group?.querySelector('label,.control-label,.label');
    const text = label?.textContent.trim() || control.placeholder || control.id.replace(/[-_]/g, ' ');
    if (text) control.setAttribute('aria-label', text);
  }
  document.querySelectorAll('canvas').forEach(canvas => {
    canvas.setAttribute('role', 'img');
    canvas.setAttribute('aria-label', canvas.id === 'draw' ? 'Drawing area. Use a mouse or touch to draw a digit.' : 'Interactive algorithm visualization');
  });
  new ResizeObserver(queueSize).observe(document.body);
  window.addEventListener('load', queueSize);
  window.addEventListener('resize', queueSize);
  queueSize();
})();
