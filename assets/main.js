(() => {
  'use strict';
  const root = document.documentElement;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const motionOn = () => root.dataset.motion !== 'off';
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const store = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch { /* Private browsing may block storage. */ } },
  };
  // Same-document view transitions (filtering, theme) reuse the page-transition styles via data-vt.
  let activeMorph = null;
  function morph(kind, update) {
    if (!document.startViewTransition || !motionOn()) { update(); return; }
    root.dataset.vt = kind;
    const transition = activeMorph = document.startViewTransition(update);
    transition.ready.catch(() => { /* Superseded by a newer transition; the update itself still ran. */ });
    transition.finished.finally(() => { if (activeMorph === transition) delete root.dataset.vt; });
  }

  /* ------------------------------------------------------------ Navigation */
  const header = document.querySelector('.site-header');
  const menu = document.querySelector('.menu-button');
  const nav = document.querySelector('#primary-nav');
  function closeMenu() {
    nav?.classList.remove('is-open');
    menu?.setAttribute('aria-expanded', 'false');
  }
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      menu.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!event.target.closest('.site-header')) closeMenu();
  });
  nav?.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });

  // A soft pill follows the pointer across the nav links.
  if (nav && finePointer) {
    const glider = document.createElement('span');
    glider.className = 'nav-glider';
    glider.setAttribute('aria-hidden', 'true');
    nav.prepend(glider);
    nav.addEventListener('pointerover', event => {
      const link = event.target.closest('a');
      if (!link) return;
      nav.style.setProperty('--gx', `${link.offsetLeft}px`);
      nav.style.setProperty('--gw', `${link.offsetWidth}px`);
      nav.classList.add('is-gliding');
    });
    nav.addEventListener('pointerleave', () => nav.classList.remove('is-gliding'));
  }

  // Remember where a navigation started so the next page can open from that point.
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || link.target === '_blank' || link.origin !== location.origin || event.metaKey || event.ctrlKey || event.shiftKey) return;
    const rect = link.getBoundingClientRect();
    const x = event.detail ? event.clientX : rect.left + rect.width / 2;
    const y = event.detail ? event.clientY : rect.top + rect.height / 2;
    try { sessionStorage.setItem('sg-vt', `${Math.round(x)},${Math.round(y)}`); } catch { /* The transition falls back to its default origin. */ }
  });

  /* ---------------------------------------------------------------- Scroll */
  const progress = document.querySelector('.scroll-progress');
  const marquee = document.querySelector('[data-marquee] .marquee-track');
  let lastY = scrollY;
  let velocity = 0;
  let marqueeFrame = 0;
  function easeMarquee() {
    velocity *= .92;
    const animation = marquee.getAnimations?.()[0];
    if (animation) animation.playbackRate = 1 + Math.min(7, Math.abs(velocity) * .09);
    marquee.style.setProperty('--skew', `${clamp(velocity * -.12, -9, 9).toFixed(2)}deg`);
    marqueeFrame = Math.abs(velocity) > .05 ? requestAnimationFrame(easeMarquee) : 0;
  }
  const labShell = document.querySelector('.lab-shell');
  // A running playground is an app surface: the floating nav would sit on top of its controls.
  function labInFocus() {
    if (!labShell || !labShell.querySelector('[data-lab-frame]:not([hidden])')) return false;
    const rect = labShell.getBoundingClientRect();
    return rect.top < 96 && rect.bottom > 160;
  }
  function onScroll() {
    const y = scrollY;
    const delta = y - lastY;
    lastY = y;
    progress?.style.setProperty('--progress', (y / Math.max(1, root.scrollHeight - innerHeight)).toFixed(4));
    if (header && Math.abs(delta) > 4 && menu?.getAttribute('aria-expanded') !== 'true') header.classList.toggle('is-hidden', (delta > 0 && y > 260) || labInFocus());
    if (marquee && motionOn()) {
      velocity = clamp(velocity + delta * .35, -80, 80);
      if (!marqueeFrame) marqueeFrame = requestAnimationFrame(easeMarquee);
    }
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* --------------------------------------------------------------- Reveals */
  const revealTargets = [...document.querySelectorAll('[data-reveal],[data-split]')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      // Elements entering together cascade in reading order.
      entries.filter(entry => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top || a.boundingClientRect.left - b.boundingClientRect.left)
        .forEach((entry, i) => {
          entry.target.style.setProperty('--d', `${Math.min(i, 6) * 90}ms`);
          entry.target.classList.add('is-in');
          observer.unobserve(entry.target);
        });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    revealTargets.forEach(el => observer.observe(el));
  } else {
    revealTargets.forEach(el => el.classList.add('is-in'));
  }

  const counters = [...document.querySelectorAll('[data-count]')];
  if (counters.length && 'IntersectionObserver' in window) {
    const counterObserver = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      counterObserver.unobserve(entry.target);
      const el = entry.target;
      const end = Number(el.dataset.count);
      if (!motionOn() || !Number.isFinite(end)) return;
      const start = performance.now();
      (function step(now) {
        const t = clamp((now - start) / 1600, 0, 1);
        el.textContent = String(Math.round(end * (1 - Math.pow(1 - t, 4)))).padStart(2, '0');
        if (t < 1) requestAnimationFrame(step);
      })(start);
    }), { threshold: .6 });
    counters.forEach(el => counterObserver.observe(el));
  }

  /* ------------------------------------------------------- Pointer effects */
  if (finePointer) {
    const ring = document.createElement('div');
    ring.className = 'cursor-ring';
    ring.setAttribute('aria-hidden', 'true');
    const ringLabel = ring.appendChild(document.createElement('span'));
    document.body.append(ring);
    const target = { x: -100, y: -100 };
    const position = { x: -100, y: -100 };
    let ringFrame = 0;
    function follow() {
      position.x += (target.x - position.x) * .2;
      position.y += (target.y - position.y) * .2;
      ring.style.setProperty('--cx', `${position.x.toFixed(1)}px`);
      ring.style.setProperty('--cy', `${position.y.toFixed(1)}px`);
      ringFrame = Math.abs(target.x - position.x) + Math.abs(target.y - position.y) > .2 ? requestAnimationFrame(follow) : 0;
    }

    let tilted = null;
    let pulled = null;
    function release(el, props) { props.forEach(prop => el.style.removeProperty(prop)); }

    function describe(el) {
      const labelled = el?.closest('[data-cursor]');
      ringLabel.textContent = labelled ? labelled.dataset.cursor : '';
      ring.classList.toggle('has-label', Boolean(labelled));
      ring.classList.toggle('is-link', !labelled && Boolean(el?.closest('a,button,summary,[data-cloud]')));
    }
    // Content moves under a resting pointer while scrolling, so look again afterwards.
    let scrollCheck = 0;
    addEventListener('scroll', () => {
      if (scrollCheck || !ring.classList.contains('is-visible')) return;
      scrollCheck = requestAnimationFrame(() => { scrollCheck = 0; describe(document.elementFromPoint(target.x, target.y)); });
    }, { passive: true });

    document.addEventListener('pointermove', event => {
      if (event.pointerType !== 'mouse' || !motionOn()) { ring.classList.remove('is-visible'); return; }
      const el = event.target instanceof Element ? event.target : null;
      target.x = event.clientX;
      target.y = event.clientY;
      if (!ring.classList.contains('is-visible')) { position.x = target.x; position.y = target.y; ring.classList.add('is-visible'); }
      if (!ringFrame) ringFrame = requestAnimationFrame(follow);
      describe(el);

      const lit = el?.closest('[data-spotlight]');
      if (lit) {
        const rect = lit.getBoundingClientRect();
        lit.style.setProperty('--mx', `${event.clientX - rect.left}px`);
        lit.style.setProperty('--my', `${event.clientY - rect.top}px`);
      }
      const tilt = el?.closest('[data-tilt]') || null;
      if (tilted && tilted !== tilt) { tilted.classList.remove('is-tilting'); release(tilted, ['--rx', '--ry']); }
      tilted = tilt;
      if (tilt) {
        const rect = tilt.getBoundingClientRect();
        tilt.classList.add('is-tilting');
        tilt.style.setProperty('--ry', `${(((event.clientX - rect.left) / rect.width - .5) * 7).toFixed(2)}deg`);
        tilt.style.setProperty('--rx', `${(((event.clientY - rect.top) / rect.height - .5) * -7).toFixed(2)}deg`);
      }
      const magnet = el?.closest('[data-magnetic]') || null;
      if (pulled && pulled !== magnet) release(pulled, ['--tx', '--ty']);
      pulled = magnet;
      if (magnet) {
        const rect = magnet.getBoundingClientRect();
        magnet.style.setProperty('--tx', `${((event.clientX - rect.left - rect.width / 2) * .28).toFixed(1)}px`);
        magnet.style.setProperty('--ty', `${((event.clientY - rect.top - rect.height / 2) * .38).toFixed(1)}px`);
      }
    }, { passive: true });
    document.addEventListener('pointerdown', () => ring.classList.add('is-down'));
    document.addEventListener('pointerup', () => ring.classList.remove('is-down'));
    // The pointer leaves our document when it enters a lab iframe or exits the window.
    root.addEventListener('pointerleave', () => ring.classList.remove('is-visible'));
    document.querySelectorAll('iframe').forEach(frame => frame.addEventListener('pointerenter', () => ring.classList.remove('is-visible')));

    // Variable-font headline: letters gain weight as the pointer approaches.
    const field = document.querySelector('[data-weight-field]');
    if (field) {
      const letters = [...field.querySelectorAll('.ch')].map(el => ({ el, weight: 600, goal: 600 }));
      let weightFrame = 0;
      function settle() {
        let moving = false;
        for (const letter of letters) {
          letter.weight += (letter.goal - letter.weight) * .14;
          if (Math.abs(letter.goal - letter.weight) > .5) moving = true;
          letter.el.style.fontWeight = letter.weight.toFixed(0);
        }
        weightFrame = moving ? requestAnimationFrame(settle) : 0;
      }
      function aim(event) {
        if (!motionOn()) return;
        for (const letter of letters) {
          const rect = letter.el.getBoundingClientRect();
          const distance = event ? Math.hypot(event.clientX - rect.left - rect.width / 2, event.clientY - rect.top - rect.height / 2) : Infinity;
          const pull = clamp(1 - distance / 320, 0, 1);
          letter.goal = 600 + pull * pull * 300 - (event ? (1 - pull) * 180 : 0);
        }
        if (!weightFrame) weightFrame = requestAnimationFrame(settle);
      }
      field.addEventListener('pointermove', aim, { passive: true });
      field.addEventListener('pointerleave', () => aim(null));
    }
  }

  /* ------------------------------------------------------ Motion and theme */
  const motionButton = document.querySelector('.motion-toggle');
  function applyMotion() {
    const off = !motionOn();
    if (motionButton) {
      motionButton.textContent = off ? 'Animations paused' : 'Pause animations';
      motionButton.setAttribute('aria-pressed', String(off));
    }
  }
  applyMotion();
  motionButton?.addEventListener('click', () => {
    root.dataset.motion = motionOn() ? 'off' : 'on';
    store.set('sg-motion', root.dataset.motion);
    applyMotion();
    dispatchEvent(new Event('sg-motion'));
  });

  // Labs run in sandboxed frames, so the theme reaches them as a message rather than shared storage.
  const labFrames = [...document.querySelectorAll('.lab-frame,.comparison-frame')];
  function postTheme(frame) { frame.contentWindow?.postMessage({ type: 'sg-theme', theme: currentTheme() }, '*'); }
  labFrames.forEach(frame => frame.addEventListener('load', () => postTheme(frame)));

  const themeButtons = [...document.querySelectorAll('[data-theme-set]')];
  const themes = themeButtons.map(button => button.dataset.themeSet);
  const currentTheme = () => root.dataset.theme || themes[0];
  function markTheme() { themeButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.themeSet === currentTheme()))); }
  function setTheme(name, event) {
    if (!themes.includes(name) || name === currentTheme()) return;
    if (event) {
      const rect = event.currentTarget.getBoundingClientRect();
      root.style.setProperty('--vt-x', `${rect.left + rect.width / 2}px`);
      root.style.setProperty('--vt-y', `${rect.top + rect.height / 2}px`);
    }
    morph('theme', () => {
      root.dataset.theme = name;
      markTheme();
      dispatchEvent(new Event('sg-theme'));
      labFrames.forEach(postTheme);
    });
    store.set('sg-theme', name);
  }
  markTheme();
  themeButtons.forEach(button => button.addEventListener('click', event => setTheme(button.dataset.themeSet, event)));
  document.querySelector('[data-theme-cycle]')?.addEventListener('click', event => setTheme(themes[(themes.indexOf(currentTheme()) + 1) % themes.length], event));

  document.querySelectorAll('[data-local-time]').forEach(el => {
    const format = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Berlin', hour: '2-digit', minute: '2-digit' });
    const update = () => { el.textContent = `${format.format(new Date())} local time`; };
    update();
    setInterval(update, 30000);
  });

  /* -------------------------------------------------------------- Projects */
  const search = document.querySelector('#project-search');
  const projects = [...document.querySelectorAll('[data-project]')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  let category = 'All';
  function filterProjects() {
    const query = search.value.trim().toLowerCase();
    morph('filter', () => {
      let count = 0;
      projects.forEach(card => {
        const visible = (category === 'All' || card.dataset.category === category) && card.dataset.search.includes(query);
        card.hidden = !visible;
        if (visible) { count++; card.classList.add('is-in'); }
      });
      document.querySelector('#result-count').textContent = `${count} ${count === 1 ? 'project' : 'projects'}`;
      document.querySelector('#empty-state').hidden = count > 0;
    });
  }
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    filters.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    filterProjects();
  }));
  // Typing settles briefly before the grid re-flows, so each keystroke doesn't restart the morph.
  let searchTimer = 0;
  search?.addEventListener('input', () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(filterProjects, 140);
  });
  document.querySelector('#clear-filters')?.addEventListener('click', () => {
    search.value = '';
    category = 'All';
    filters.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filter === 'All')));
    filterProjects();
    search.focus();
  });

  /* --------------------------------------------------------------- Contact */
  const copy = document.querySelector('#copy-email');
  copy?.addEventListener('click', async () => {
    const status = document.querySelector('#copy-status');
    try {
      await navigator.clipboard.writeText(copy.dataset.email);
      status.textContent = 'Email address copied.';
    } catch {
      status.textContent = `Copy this address: ${copy.dataset.email}`;
    }
  });

  /* ------------------------------------------------------------------ Labs */
  document.querySelector('[data-launch-lab]')?.addEventListener('click', event => {
    const button = event.currentTarget;
    const iframe = document.querySelector('[data-lab-frame]');
    // The query string lets the lab paint in the right theme on its very first frame.
    iframe.src = `${button.dataset.launchLab}?theme=${encodeURIComponent(currentTheme())}${motionOn() ? '' : '&motion=off'}`;
    iframe.hidden = false;
    document.querySelector('[data-lab-placeholder]').hidden = true;
    iframe.addEventListener('load', () => { iframe.focus(); }, { once: true });
  });
  window.addEventListener('message', event => {
    const frames = [...document.querySelectorAll('.lab-frame,.comparison-frame')];
    const frame = frames.find(candidate => candidate.contentWindow === event.source);
    if (!frame || event.data?.type !== 'sg-lab-height' || !Number.isFinite(event.data.height)) return;
    const height = Math.max(300, Math.min(6000, Math.ceil(event.data.height)));
    if (Math.abs(frame.getBoundingClientRect().height - height) > 3) frame.style.height = `${height}px`;
  });

  root.classList.add('js-ready');
})();
