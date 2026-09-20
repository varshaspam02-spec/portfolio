(() => {
  'use strict';
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

  const motionButton = document.querySelector('.motion-toggle');
  let reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  try { reduced = localStorage.getItem('sg-motion') === 'off' || reduced; } catch { /* Private browsing may block storage. */ }
  function applyMotion() {
    document.documentElement.dataset.motion = reduced ? 'off' : 'on';
    if (motionButton) {
      motionButton.textContent = reduced ? 'Animations paused' : 'Pause animations';
      motionButton.setAttribute('aria-pressed', String(reduced));
    }
  }
  applyMotion();
  motionButton?.addEventListener('click', () => {
    reduced = !reduced;
    applyMotion();
    try { localStorage.setItem('sg-motion', reduced ? 'off' : 'on'); } catch { /* Preference remains active on this page. */ }
  });

  const search = document.querySelector('#project-search');
  const projects = [...document.querySelectorAll('[data-project]')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  let category = 'All';
  function filterProjects() {
    const query = search.value.trim().toLowerCase();
    let count = 0;
    projects.forEach(card => {
      const visible = (category === 'All' || card.dataset.category === category) && card.dataset.search.includes(query);
      card.hidden = !visible;
      if (visible) count++;
    });
    document.querySelector('#result-count').textContent = `${count} ${count === 1 ? 'project' : 'projects'}`;
    document.querySelector('#empty-state').hidden = count > 0;
  }
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    filters.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    filterProjects();
  }));
  search?.addEventListener('input', filterProjects);
  document.querySelector('#clear-filters')?.addEventListener('click', () => {
    search.value = '';
    category = 'All';
    filters.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filter === 'All')));
    filterProjects();
    search.focus();
  });

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

  document.querySelector('[data-launch-lab]')?.addEventListener('click', event => {
    const button = event.currentTarget;
    const iframe = document.querySelector('[data-lab-frame]');
    iframe.src = button.dataset.launchLab;
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
})();
