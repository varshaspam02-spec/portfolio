/* Ambient visuals: the WebGL aurora backdrop and the hero's morphing point cloud.
   Both follow the accent theme, pause while hidden, and hold a still frame when motion is off. */
(() => {
  'use strict';
  const root = document.documentElement;
  const motionOn = () => root.dataset.motion !== 'off';
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

  function themeColors() {
    const style = getComputedStyle(root);
    return ['--a1', '--a2', '--a3'].map(name => {
      const hex = style.getPropertyValue(name).trim().replace('#', '');
      if (!/^[0-9a-f]{6}$/i.test(hex)) return [.5, .5, 1];
      return [0, 2, 4].map(i => parseInt(hex.slice(i, i + 2), 16) / 255);
    });
  }

  const pointer = { x: innerWidth / 2, y: innerHeight / 3, seen: false };
  addEventListener('pointermove', event => {
    pointer.x = event.clientX;
    pointer.y = event.clientY;
    pointer.seen = true;
  }, { passive: true });

  /* ---------------------------------------------------------------- Aurora */
  const VERTEX = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  const FRAGMENT = `
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 uRes;uniform float uTime;uniform float uScroll;uniform vec2 uMouse;
uniform vec3 uC1;uniform vec3 uC2;uniform vec3 uC3;
const vec3 BG=vec3(.0196,.0235,.0431);
vec2 hash(vec2 p){p=vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3)));return -1.+2.*fract(sin(p)*43758.5453);}
float noise(vec2 p){
  vec2 i=floor(p),f=fract(p),u=f*f*f*(f*(f*6.-15.)+10.);
  return 1.4*mix(mix(dot(hash(i),f),dot(hash(i+vec2(1,0)),f-vec2(1,0)),u.x),
                 mix(dot(hash(i+vec2(0,1)),f-vec2(0,1)),dot(hash(i+vec2(1,1)),f-vec2(1,1)),u.x),u.y);
}
void main(){
  vec2 uv=gl_FragCoord.xy/uRes;
  vec2 p=vec2((uv.x-.5)*uRes.x/uRes.y,uv.y-.5);
  vec2 m=vec2((uMouse.x-.5)*uRes.x/uRes.y,uMouse.y-.5);
  p.y-=uScroll*.22;
  float t=uTime*.045;
  /* Domain-warped noise: slow, folding curtains of colour. */
  vec2 w=vec2(noise(p*.75+vec2(t,-t*.6)),noise(p*.75+vec2(-t*.7,t)+7.3));
  vec2 q=p+w*.62;
  float n1=noise(q*.85+vec2(t*1.2,4.1))*.5+.5;
  float n2=noise(q*.7+vec2(9.7,-t))*.5+.5;
  float n3=noise(q*1.05+vec2(-3.2,t*.9)+w*.5)*.5+.5;
  float glow=exp(-5.5*dot(p-m+vec2(0.,uScroll*.22),p-m+vec2(0.,uScroll*.22)));
  vec3 col=BG;
  col=mix(col,uC1,smoothstep(.42,.98,n1)*.46);
  col=mix(col,uC2,smoothstep(.48,1.,n2)*.4);
  col=mix(col,uC3,smoothstep(.55,1.,n3)*.26+glow*.1);
  float ribbon=pow(1.-abs(noise(vec2(q.x*.9+t,q.y*2.4-t*1.4))),7.);
  col+=ribbon*.035*mix(uC2,uC3,n1);
  /* Keep the page edges and the reading column calm. */
  float calm=smoothstep(1.35,.15,length(vec2(p.x*.7,p.y*1.05)));
  col=mix(BG,col,calm*.82);
  col+=(fract(sin(dot(gl_FragCoord.xy+uTime,vec2(12.9898,78.233)))*43758.5453)-.5)/110.;
  gl_FragColor=vec4(col,1.);
}`;

  function initAurora(canvas) {
    let gl;
    try { gl = canvas.getContext('webgl', { antialias: false, alpha: false, powerPreference: 'low-power' }); } catch { return; }
    if (!gl) return;
    const program = gl.createProgram();
    for (const [type, source] of [[gl.VERTEX_SHADER, VERTEX], [gl.FRAGMENT_SHADER, FRAGMENT]]) {
      const shader = gl.createShader(type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) return;
      gl.attachShader(program, shader);
    }
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return;
    gl.useProgram(program);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const position = gl.getAttribLocation(program, 'p');
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
    const uniform = name => gl.getUniformLocation(program, name);
    const u = { res: uniform('uRes'), time: uniform('uTime'), scroll: uniform('uScroll'), mouse: uniform('uMouse'), c: [uniform('uC1'), uniform('uC2'), uniform('uC3')] };

    // The field is soft by nature, so a fraction of the screen resolution is plenty.
    const SCALE = .4;
    function resize() {
      canvas.width = Math.max(2, Math.round(innerWidth * SCALE));
      canvas.height = Math.max(2, Math.round(innerHeight * SCALE));
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.uniform2f(u.res, canvas.width, canvas.height);
    }
    function recolor() { themeColors().forEach((color, i) => gl.uniform3f(u.c[i], ...color)); }

    // Carry the animation clock across pages so the backdrop never jumps on navigation.
    let clock = 0;
    try { clock = Number(sessionStorage.getItem('sg-aurora-clock')) || 0; } catch { /* Storage may be blocked. */ }
    addEventListener('pagehide', () => { try { sessionStorage.setItem('sg-aurora-clock', String(clock)); } catch { /* Ignore. */ } });

    const mouse = { x: .5, y: .62 };
    let last = 0;
    let lastDraw = 0;
    let frame = 0;
    function draw() {
      gl.uniform1f(u.time, clock);
      gl.uniform1f(u.scroll, scrollY / Math.max(1, innerHeight));
      gl.uniform2f(u.mouse, mouse.x, mouse.y);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }
    function tick(now) {
      frame = requestAnimationFrame(tick);
      if (now - lastDraw < 30) return;
      clock += Math.min(.1, (now - (last || now)) / 1000);
      last = lastDraw = now;
      if (pointer.seen) {
        mouse.x += (pointer.x / innerWidth - mouse.x) * .04;
        mouse.y += (1 - pointer.y / innerHeight - mouse.y) * .04;
      }
      draw();
    }
    function sync() {
      cancelAnimationFrame(frame);
      last = 0;
      if (motionOn() && !document.hidden) frame = requestAnimationFrame(tick); else draw();
    }
    addEventListener('resize', () => { resize(); if (!motionOn()) draw(); });
    addEventListener('scroll', () => { if (!motionOn()) draw(); }, { passive: true });
    document.addEventListener('visibilitychange', sync);
    addEventListener('sg-motion', sync);
    addEventListener('sg-theme', () => { recolor(); draw(); });
    canvas.addEventListener('webglcontextlost', event => { event.preventDefault(); cancelAnimationFrame(frame); root.classList.remove('has-aurora'); });
    resize();
    recolor();
    draw();
    root.classList.add('has-aurora');
    sync();
  }

  /* ----------------------------------------------------------- Point cloud */
  // Decorative geometry borrowed from the labs; none of it is computed from real data.
  const SHAPES = [
    ['Embedding space', (i, n, rnd) => {
      const y = 1 - 2 * (i + .5) / n, r = Math.sqrt(1 - y * y), a = i * 2.399963, j = 1 + (rnd() - .5) * .06;
      return [r * Math.cos(a) * j, y * j, r * Math.sin(a) * j];
    }],
    ['Manifold', (i, n, rnd) => {
      const t = 1.5 * Math.PI * (1 + 2 * (i + rnd()) / n);
      return [t * Math.cos(t) / 15.5, (rnd() - .5) * 1.25, t * Math.sin(t) / 15.5];
    }],
    ['Loss landscape', (i, n) => {
      const g = Math.ceil(Math.sqrt(n)), x = ((i % g) / (g - 1) - .5) * 2.2, z = (Math.floor(i / g) / (g - 1) - .5) * 2.2;
      const y = .3 * Math.sin(x * 2.3) * Math.cos(z * 2.1) - .62 * Math.exp(-((x - .3) ** 2 + (z + .2) ** 2) * 2.2) + .12;
      return [x, y, z];
    }],
    ['Clusters', (i, n, rnd) => {
      const centers = [[.78, .2, .1], [-.62, .5, .3], [-.2, -.66, .45], [.25, -.3, -.78], [-.1, .56, -.66]];
      const c = centers[Math.min(4, Math.floor(i / n * 5))];
      const gauss = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd()) * .17;
      return [c[0] + gauss(), c[1] + gauss(), c[2] + gauss()];
    }],
    ['Network layers', (i, n) => {
      const per = n / 5, layer = Math.min(4, Math.floor(i / per)), k = i - layer * per;
      const r = [.42, .7, .9, .7, .42][layer] * Math.sqrt((k + .5) / per), a = k * 2.399963;
      return [(layer - 2) * .5, r * Math.cos(a), r * Math.sin(a)];
    }],
  ];

  function initCloud(canvas) {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const N = innerWidth < 760 ? 1000 : 1700;
    const COLORS = 8, DEPTHS = 3;
    let seed = 7;
    const rnd = () => { seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
    const targets = SHAPES.map(([, make]) => { const out = new Float32Array(N * 3); for (let i = 0; i < N; i++) out.set(make(i, N, rnd), i * 3); return out; });
    const from = new Float32Array(targets[0]);
    const current = new Float32Array(targets[0]);
    const delay = new Float32Array(N);
    const swirl = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      delay[i] = rnd() * .45;
      const a = rnd() * Math.PI * 2, b = Math.acos(2 * rnd() - 1);
      swirl.set([Math.sin(b) * Math.cos(a), Math.cos(b), Math.sin(b) * Math.sin(a)], i * 3);
    }
    const buckets = Array.from({ length: COLORS * DEPTHS }, () => []);
    const sx = new Float32Array(N), sy = new Float32Array(N), ss = new Float32Array(N);
    let palette = [];
    function recolor() {
      const [a, b, c] = themeColors();
      palette = Array.from({ length: COLORS }, (_, k) => {
        const t = k / (COLORS - 1) * 2, lo = t < 1 ? a : b, hi = t < 1 ? b : c, f = t < 1 ? t : t - 1;
        return `rgb(${lo.map((v, j) => Math.round((v + (hi[j] - v) * f) * 255)).join(',')})`;
      });
    }

    let shape = 0, morph = 1, width = 0, height = 0, dpr = 1;
    let rotX = -.32, rotY = 0, tiltX = 0, tiltY = 0, spin = 0;
    let frame = 0, last = 0, sinceMorph = 0, visible = true;
    const label = document.querySelector('[data-cloud-name]');
    const nextButton = document.querySelector('[data-cloud-next]');

    function resize() {
      const rect = canvas.getBoundingClientRect();
      dpr = Math.min(2, devicePixelRatio || 1);
      width = canvas.width = Math.max(2, Math.round(rect.width * dpr));
      height = canvas.height = Math.max(2, Math.round(rect.height * dpr));
    }
    function next() {
      from.set(current);
      shape = (shape + 1) % SHAPES.length;
      morph = motionOn() ? 0 : 1;
      sinceMorph = 0;
      if (label) label.textContent = SHAPES[shape][0];
      if (!motionOn()) render(0);
    }
    function render(dt) {
      const target = targets[shape];
      if (morph < 1) morph = Math.min(1, morph + dt / 2.4);
      spin += dt * .16;
      const rect = canvas.getBoundingClientRect();
      if (pointer.seen) {
        tiltY += ((pointer.x / innerWidth - .5) * 1.3 - tiltY) * .05;
        tiltX += ((pointer.y / innerHeight - .5) * .7 - tiltX) * .05;
      }
      const ry = rotY + spin + tiltY, rx = rotX + tiltX;
      const cy = Math.cos(ry), syn = Math.sin(ry), cx = Math.cos(rx), sxn = Math.sin(rx);
      const radius = Math.min(width, height) * .36;
      const mx = (pointer.x - rect.left) * dpr, my = (pointer.y - rect.top) * dpr, reach = 120 * dpr;
      for (const bucket of buckets) bucket.length = 0;
      for (let i = 0; i < N; i++) {
        const j = i * 3;
        let local = clamp(morph * 1.45 - delay[i], 0, 1);
        local = local < .5 ? 4 * local * local * local : 1 - Math.pow(-2 * local + 2, 3) / 2;
        const burst = Math.sin(Math.PI * local) * .24;
        const x = current[j] = from[j] + (target[j] - from[j]) * local + swirl[j] * burst;
        const y = current[j + 1] = from[j + 1] + (target[j + 1] - from[j + 1]) * local + swirl[j + 1] * burst;
        const z = current[j + 2] = from[j + 2] + (target[j + 2] - from[j + 2]) * local + swirl[j + 2] * burst;
        const x1 = x * cy + z * syn, z1 = -x * syn + z * cy;
        const y1 = y * cx - z1 * sxn, z2 = y * sxn + z1 * cx;
        const perspective = 3.4 / (3.4 + z2);
        let px = width / 2 + x1 * radius * perspective;
        let py = height / 2 - y1 * radius * perspective;
        if (pointer.seen) {
          const dx = px - mx, dy = py - my, distance = Math.hypot(dx, dy);
          if (distance < reach && distance > .01) {
            const push = (1 - distance / reach) ** 2 * 38 * dpr;
            px += dx / distance * push;
            py += dy / distance * push;
          }
        }
        const near = clamp((1.25 - z2) / 2.5, 0, 1);
        sx[i] = px; sy[i] = py; ss[i] = (.7 + near * 1.9) * dpr;
        buckets[Math.floor(i / N * COLORS) * DEPTHS + Math.min(DEPTHS - 1, Math.floor(near * DEPTHS))].push(i);
      }
      ctx.clearRect(0, 0, width, height);
      ctx.globalCompositeOperation = 'lighter';
      buckets.forEach((bucket, b) => {
        if (!bucket.length) return;
        ctx.globalAlpha = [.3, .62, 1][b % DEPTHS];
        ctx.fillStyle = palette[Math.floor(b / DEPTHS)];
        ctx.beginPath();
        for (const i of bucket) { ctx.moveTo(sx[i] + ss[i], sy[i]); ctx.arc(sx[i], sy[i], ss[i], 0, 6.2832); }
        ctx.fill();
      });
    }
    function tick(now) {
      frame = requestAnimationFrame(tick);
      const dt = Math.min(.05, (now - (last || now)) / 1000);
      last = now;
      sinceMorph += dt;
      if (sinceMorph > 7) next();
      render(dt);
    }
    function sync() {
      cancelAnimationFrame(frame);
      last = 0;
      if (motionOn() && visible && !document.hidden) frame = requestAnimationFrame(tick);
      else { morph = 1; render(0); }
    }
    new ResizeObserver(() => { resize(); if (!motionOn()) render(0); }).observe(canvas);
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); }).observe(canvas);
    document.addEventListener('visibilitychange', sync);
    addEventListener('sg-motion', sync);
    addEventListener('sg-theme', () => { recolor(); if (!motionOn()) render(0); });
    canvas.addEventListener('click', next);
    if (nextButton) { nextButton.hidden = false; nextButton.addEventListener('click', next); }
    recolor();
    resize();
    canvas.classList.add('is-ready');
    sync();
  }

  const aurora = document.querySelector('[data-aurora]');
  if (aurora) initAurora(aurora);
  const cloud = document.querySelector('[data-cloud]');
  if (cloud) initCloud(cloud);
})();
