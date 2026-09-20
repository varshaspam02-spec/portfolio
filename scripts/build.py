"""Generate a dependency-free, GitHub Pages-compatible static portfolio."""
from html import escape
from pathlib import Path
import json
import math
import random
from content import PROFILE, PROJECTS, ARTICLES, LABS, EXTERNAL_LAB

ROOT = Path(__file__).resolve().parents[1]
E = escape

def icon(name, size=24):
    paths = {
        'arrow': '<path d="M6 18 18 6M6 6h12v12"/>',
        'network': '<path d="m6 6 12 2-6 10L6 6Zm0 0L4 16l8 2 8-2-2-8"/><circle cx="6" cy="6" r="2"/><circle cx="18" cy="8" r="2"/><circle cx="12" cy="18" r="2"/>',
        'scan': '<path d="M8 3H3v5m13-5h5v5M3 16v5h5m8 0h5v-5M7 8h10M7 12h10M7 16h6"/>',
        'code': '<path d="m8 6-6 6 6 6m8-12 6 6-6 6m-3-15-2 18"/>',
        'search': '<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>',
        'chart': '<path d="M3 3v18h18M7 16v-4m5 4V8m5 8V5"/>',
        'calendar': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 2v6m10-6v6M3 11h18m-14 5h3m4 0h3"/>',
        'message': '<path d="M3 4h18v13H9l-6 4V4Z"/><path d="M7 8h10M7 12h6"/>',
        'play': '<path d="m8 4 12 8-12 8V4Z"/>',
        'terminal': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m6 9 3 3-3 3m6 0h5"/>',
        'swap': '<path d="M3 7h17l-4-4M21 17H4l4 4M20 7l-4 4M4 17l4-4"/>',
        'document': '<path d="M5 2h9l5 5v15H5V2Z"/><path d="M14 2v6h5M8 12h8M8 16h8"/>',
        'wave': '<path d="M3 10v4m4-8v12m5-16v20m5-16v12m4-8v4"/>',
        'mail': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 5 10 8L22 5"/>',
        'location': '<path d="M19 10c0 5-7 12-7 12S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2"/>',
    }
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths.get(name,paths["network"])}</svg>'

def diagram(kind, hero=False):
    rng = random.Random(11)
    shapes = ['<path d="M20 180H460M20 120H460M20 60H460M80 20V220M160 20V220M240 20V220M320 20V220M400 20V220" class="diagram-grid"/>']
    if hero:
        # Decorative network illustration, not a claimed model architecture.
        shapes = ['<circle cx="240" cy="230" r="181" class="orbit"/><circle cx="240" cy="230" r="144" class="orbit dashed"/>',
                  '<path d="M32 230h416M240 22v416" class="diagram-grid"/>']
        points=[]
        for col, n in enumerate([3,5,6,5,3]):
            points.append([(80+col*80,230+(j-(n-1)/2)*43) for j in range(n)])
        for left,right in zip(points,points[1:]):
            for x,y in left:
                for a,b in right:
                    shapes.append(f'<path d="M{x} {y}L{a} {b}" class="neural-edge"/>')
        for i, column in enumerate(points):
            for j,(x,y) in enumerate(column):
                shapes.append(f'<circle cx="{x}" cy="{y}" r="{5 if i!=2 else 7}" class="neuron n{(i+j)%3}"/>')
        shapes += ['<path d="M30 70V30h40M410 30h40v40M450 390v40h-40M70 430H30v-40" class="corner"/>',
                   '<text x="31" y="468" class="svg-label">RESEARCH → EXPERIMENT → BUILD</text>']
        return '<svg class="hero-network" viewBox="0 0 480 500" fill="none" aria-hidden="true">'+''.join(shapes)+'</svg>'
    if kind in ('clusters','pca'):
        for cx,cy,color in [(125,88,'cyan'),(270,163,'pink'),(355,66,'yellow')]:
            for _ in range(23):
                x,y=rng.gauss(cx,25),rng.gauss(cy,19)
                if kind=='pca': x,y=x*.8+40,y*.36+x*.26
                shapes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" class="dot {color}"/>')
            if kind=='clusters': shapes.append(f'<circle cx="{cx}" cy="{cy}" r="38" class="cluster-ring {color}"/>')
        if kind=='pca': shapes.append('<path d="M58 198 423 42" class="chart-line"/>')
    elif kind in ('network','tree'):
        nodes=[(240,42),(135,105),(345,105),(80,184),(188,184),(298,184),(409,184)]
        for a,b in [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]:
            x,y=nodes[a];u,v=nodes[b]
            shapes.append(f'<path d="M{x} {y}L{u} {v}" class="chart-line"/>')
        for x,y in nodes: shapes.append(f'<rect x="{x-16}" y="{y-10}" width="32" height="20" rx="3" class="chart-node"/>')
    elif kind=='contour':
        for i in range(8):
            shapes.append(f'<ellipse cx="240" cy="125" rx="{35+i*22}" ry="{14+i*10}" transform="rotate(-18 240 125)" class="cluster-ring cyan"/>')
        shapes.append('<path d="m80 55 90 130 125-90-88 53 49-17-16-6" class="trajectory"/><circle cx="240" cy="125" r="5" class="dot pink"/>')
    elif kind=='manifold':
        for i in range(34):
            t=i/5
            for j in range(9):
                x=240+(18+t*13)*math.cos(t)+j*5
                y=110+(12+t*7)*math.sin(t)-j*3
                shapes.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2" class="dot {"pink" if i>18 else "cyan"}"/>')
    elif kind=='attention':
        for i in range(7):
            for j in range(7):
                opacity= .15+.8/(1+abs(i-j))
                shapes.append(f'<rect x="{128+i*30}" y="{20+j*30}" width="25" height="25" fill="#55f4de" opacity="{opacity}"/>')
    elif kind=='quantization':
        points=' '.join(f'{40+i*4},{120-math.sin(i/12)*60}' for i in range(100))
        shapes.append(f'<polyline points="{points}" class="cluster-ring pink"/>')
        pts=[]
        for i in range(11):
            y=round((120-math.sin(i*10/12)*60)/25)*25
            pts.extend([(40+i*38,y),(78+i*38,y)])
        shapes.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+'" class="chart-line"/>')
    else:
        shapes.append('<path d="M120 75V40h40M320 40h40v35M360 165v35h-40M160 200h-40v-35" class="chart-line"/><rect x="179" y="76" width="100" height="109" class="cluster-ring pink"/><path d="M130 120h220" class="trajectory"/>')
    return '<svg viewBox="0 0 480 240" fill="none" aria-hidden="true">'+''.join(shapes)+'</svg>'

def external(url, label, cls='text-link'):
    return f'<a class="{cls}" href="{E(url)}" target="_blank" rel="noopener noreferrer">{label}{icon("arrow",18)}</a>'

def project_card(p, i, compact=False):
    tags=''.join(f'<span>{E(t)}</span>' for t in p['tags'])
    features=''.join(f'<li>{E(f)}</li>' for f in p['features'])
    search=E(' '.join([p['name'],p['description'],p['category'],*p['tags']]).lower())
    return f'''<article class="project-card" data-project data-category="{E(p['category'])}" data-search="{search}">
      <div class="card-top"><span class="project-icon">{icon(p['icon'],27)}</span><span class="mono muted">/{i:02}</span></div>
      <span class="eyebrow category-label">{E(p['category'])}</span><h3>{E(p['name'])}</h3>
      <p>{E(p['description'])}</p><div class="tags">{tags}</div>
      {'' if compact else '<details><summary>What it does<span aria-hidden="true">+</span></summary><ul>'+features+'</ul></details>'}
      <div class="card-bottom">{external('https://github.com/GhoshSrinjoy/'+p['repo'],'View repository')}</div>
    </article>'''

def lab_card(lab, i, prefix, ext=False):
    href=lab['url'] if ext else prefix+'spaces/'+lab['slug']+'/index.html'
    attrs=' target="_blank" rel="noopener noreferrer"' if ext else ''
    return f'''<a class="lab-card" href="{E(href)}"{attrs}><div class="lab-visual">{diagram(lab['visual'])}<span class="lab-number mono">EXPERIMENT {i:02}</span></div><div class="lab-copy"><span class="eyebrow">{E(lab['kind'])}</span><h3>{E(lab.get('short',lab['title']))}{icon('arrow',20)}</h3><p>{E(lab['description'])}</p><span class="lab-action mono">{'OPEN EXTERNAL DEMO' if ext else 'LAUNCH PLAYGROUND'} →</span></div></a>'''

def section_head(number, label, title, link=''):
    return f'<div class="section-head"><div><span class="eyebrow"><span>{number}</span> / {label}</span><h2>{title}</h2></div>{link}</div>'

def page(title, active, content, depth=0, description=None):
    pre='../'*depth
    nav=''.join(f'<a href="{pre+url}"'+(' aria-current="page"' if active==name else '')+f'>{name}</a>' for name,url in [('Home','index.html'),('Projects','projects/index.html'),('Spaces','spaces/index.html'),('Articles','articles/index.html'),('Contact','contact/index.html')])
    description=description or PROFILE['intro']
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#080c13"><title>{E(title)} | Srinjoy Ghosh</title>
<meta name="description" content="{E(description)}"><meta property="og:title" content="{E(title)} | Srinjoy Ghosh"><meta property="og:description" content="{E(description)}"><meta property="og:type" content="website">
<link rel="icon" type="image/svg+xml" href="{pre}assets/favicon.svg"><link rel="stylesheet" href="{pre}assets/styles.css"><script defer src="{pre}assets/main.js"></script></head>
<body><a class="skip-link" href="#main">Skip to content</a><div class="ambient" aria-hidden="true"></div>
<header class="site-header"><div class="container header-inner"><a class="brand" href="{pre}index.html" aria-label="Srinjoy Ghosh home"><span class="brand-mark">S<span>G</span></span><span>SRINJOY<span class="brand-dot">.</span></span></a>
<button class="menu-button" type="button" aria-expanded="false" aria-controls="primary-nav">MENU <span aria-hidden="true">☰</span></button>
<nav id="primary-nav" aria-label="Main navigation">{nav}</nav>{external(PROFILE['github'],'GitHub','header-github')}</div></header>
<main id="main" tabindex="-1">{content}</main>
<footer class="site-footer"><div class="container footer-top"><a class="brand" href="{pre}index.html"><span class="brand-mark">S<span>G</span></span><span>Keep building<span class="brand-dot">.</span></span></a><div class="footer-links">{external(PROFILE['github'],'GitHub')}{external(PROFILE['linkedin'],'LinkedIn')}<a href="mailto:{PROFILE['email']}">Email {icon('arrow',16)}</a></div></div><div class="container footer-bottom"><span>© <span data-year>2026</span> Srinjoy Ghosh</span><span class="footer-location"><span class="status-dot"></span>Nuremberg, Germany</span><button class="motion-toggle" aria-pressed="false" type="button">Pause animations</button><a href="#main" class="back-top">BACK TO TOP ↑</a></div></footer>
</body></html>'''

def write(path, html):
    target=ROOT/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(html)

def home():
    selected=''.join(project_card(PROJECTS[i],i+1,True) for i in [0,1,3])
    labcards=''.join(lab_card(LABS[i],i+1,'') for i in [0,3,6])
    return f'''<section class="hero container"><div class="hero-copy"><div class="hero-kicker"><span class="status-dot"></span>AI/ML ENGINEER & RESEARCHER</div><h1>SRINJOY<br><span class="outline-name">GHOSH</span><span class="cursor">_</span></h1><p class="hero-statement">Engineering intelligence.<br><span>From idea to real-world impact.</span></p><p class="hero-description">{PROFILE['intro']}</p><div class="hero-actions"><a href="projects/index.html" class="button primary">Explore projects {icon('arrow',19)}</a><a href="spaces/index.html" class="button secondary">Enter the lab <span>→</span></a></div><div class="hero-location mono">{icon('location',15)} NUREMBERG, GERMANY <span> / </span> BUILDING IN PUBLIC</div></div><div class="hero-art"><div class="art-label mono"><span>NEURAL SYSTEMS</span><span>SG / 001</span></div>{diagram('',True)}<div class="art-caption"><span class="signal-dots" aria-hidden="true">▮▮▮▮▮</span><span class="mono">CONNECTING RESEARCH TO REALITY</span></div></div></section>
    <div class="stats-strip"><div class="container stats-inner"><div><strong>14<span>_</span></strong><span>Open-source projects</span></div><div><strong>08<span>_</span></strong><span>Interactive demos</span></div><div><strong>05<span>+</span></strong><span>Years of experience</span></div><div class="stats-signature mono">AGENTS.<br>MODELS.<br>REAL-WORLD SYSTEMS.</div></div></div>
    <section class="section container">{section_head('01','SELECTED WORK','Ideas, built into systems.', '<a class="text-link" href="projects/index.html">All 14 projects '+icon('arrow',18)+'</a>')}<div class="project-grid">{selected}</div></section>
    <section class="about-section"><div class="container about-grid"><div><span class="eyebrow">02 / THE ENGINEER</span><h2>Curiosity in.<br><span class="cyan-text">Intelligence out.</span></h2></div><div class="about-copy"><p>{E(PROFILE['bio'])}</p><p>I’m currently architecting an end-to-end blackbox testing framework and software solutions. I’m also the creator of <strong>RICHES</strong>, a multimodal, cross-lingual RAG system.</p><div class="expertise-tags"><span>Agent systems</span><span>Multimodal RAG</span><span>Model optimization</span><span>Applied ML</span></div><a class="text-link" href="contact/index.html">Let’s connect {icon('arrow',18)}</a></div></div></section>
    <section class="section container">{section_head('03','EXPERIMENTAL SPACES','Less theory. More tinkering.', '<a class="text-link" href="spaces/index.html">Explore all spaces '+icon('arrow',18)+'</a>')}<p class="section-intro">Draw, adjust, run, repeat. Get a feel for the algorithms behind intelligent systems.</p><div class="lab-grid">{labcards}</div></section>
    <section class="section container writing-teaser">{section_head('04','FIELD NOTES','Making complex things click.')}<div class="article-list">{''.join(f'<a class="article-row" href="{a["url"]}" target="_blank" rel="noopener noreferrer"><span class="mono article-index">0{i+1}</span><div><span class="eyebrow">{a["format"]} / {a["category"]}</span><h3>{a["title"]}</h3></div>{icon("arrow",25)}</a>' for i,a in enumerate(ARTICLES))}</div></section>
    <section class="container contact-cta"><div><span class="eyebrow">HAVE SOMETHING IN MIND?</span><h2>Let’s build what’s next<span>.</span></h2></div><a class="button primary" href="contact/index.html">Get in touch {icon('arrow',20)}</a></section>'''

def projects():
    filters=''.join(f'<button class="filter-button" type="button" data-filter="{category}" aria-pressed="{str(category=="All").lower()}">{category}{" <span>14</span>" if category=="All" else ""}</button>' for category in ['All','AI agents','ML systems','Developer tools','Data tools'])
    return f'''<section class="container page-intro"><span class="eyebrow">01 / PROJECT ARCHIVE</span><h1>BUILT TO <span class="cyan-text">DO.</span></h1><p>Open-source tools, intelligent agents, and experiments that made it out of the notebook.</p></section><section class="container archive-section"><div class="project-toolbar"><div class="filters" role="group" aria-label="Filter projects by category">{filters}</div><label class="search-field">{icon('search',18)}<input id="project-search" type="search" placeholder="Search projects…" aria-label="Search projects"></label></div><div class="results-line mono"><span id="result-count" role="status" aria-live="polite">14 projects</span><span>CODE / EXPERIMENTS / TOOLS</span></div><div class="project-grid">{''.join(project_card(p,i+1) for i,p in enumerate(PROJECTS))}</div><div class="empty-state" id="empty-state" hidden><h2>No matching projects.</h2><p>Try another keyword or clear the filters.</p><button class="button secondary" id="clear-filters" type="button">Clear filters</button></div></section>'''

def spaces():
    return f'''<section class="container page-intro"><span class="eyebrow">02 / THE PLAYGROUND</span><h1>LEARN BY <span class="pink-text">DOING.</span></h1><p>Eight ways to explore machine learning. Change a parameter, follow a pattern, and see the idea come to life.</p></section><section class="container archive-section"><div class="results-line mono"><span>07 LOCAL LABS + 01 EXTERNAL DEMO</span><span>NO SETUP. JUST EXPLORE.</span></div><div class="lab-grid">{''.join(lab_card(l,i+1,'../') for i,l in enumerate(LABS))}{lab_card(EXTERNAL_LAB,8,'../',True)}</div></section>'''

def articles():
    cards=''.join(f'''<article class="article-feature"><div class="article-art">{diagram(a['visual'])}<span class="mono">FIELD NOTES / 0{i+1}</span></div><div class="article-feature-copy"><span class="eyebrow">{a['category']} / {a['format']}</span><h2>{a['title']}</h2><p class="article-subtitle">{a['subtitle']}</p><p>{a['description']}</p>{external(a['url'],'Read '+('on Medium' if i==0 else 'and explore'),'button secondary')}</div></article>''' for i,a in enumerate(ARTICLES))
    return f'''<section class="container page-intro"><span class="eyebrow">03 / FIELD NOTES</span><h1>IDEAS, <span class="cyan-text">UNPACKED.</span></h1><p>Practical writing on machine learning, data, and engineering. Mathematics meets things you can actually try.</p></section><section class="container archive-section article-features">{cards}</section>'''

def contact():
    return f'''<section class="container page-intro"><span class="eyebrow">04 / OPEN A CHANNEL</span><h1>LET’S <span class="pink-text">CONNECT.</span></h1><p>Research ideas, engineering challenges, or a conversation about what comes next.</p></section><section class="container contact-grid archive-section"><div class="contact-main"><span class="eyebrow">DIRECT LINE</span><h2>Good things start<br>with a conversation.</h2><a class="email-link" href="mailto:{PROFILE['email']}">{PROFILE['email']}{icon('arrow',25)}</a><div class="contact-buttons"><a class="button primary" href="mailto:{PROFILE['email']}">Write an email {icon('mail',18)}</a><button class="button secondary" type="button" id="copy-email" data-email="{PROFILE['email']}">Copy address</button></div><p class="copy-status" id="copy-status" role="status" aria-live="polite"></p><div class="contact-channels"><a href="{PROFILE['linkedin']}" target="_blank" rel="noopener noreferrer"><span class="mono">01</span><div><strong>LinkedIn</strong><span>Professional connections</span></div>{icon('arrow',22)}</a><a href="{PROFILE['github']}" target="_blank" rel="noopener noreferrer"><span class="mono">02</span><div><strong>GitHub</strong><span>Explore my code</span></div>{icon('arrow',22)}</a><a href="tel:+4915560812680"><span class="mono">03</span><div><strong>{PROFILE['phone']}</strong><span>Phone</span></div>{icon('arrow',22)}</a></div></div><aside class="contact-profile"><div class="profile-glyph" aria-hidden="true">SG<span>_</span></div><span class="eyebrow">THE PERSON BEHIND THE CODE</span><h2>Srinjoy Ghosh</h2><p class="cyan-text">AI & ML Engineer</p><p>Over five years building intelligent systems. Creator of RICHES, a multimodal, cross-lingual RAG system.</p><div class="location-card">{icon('location',24)}<div><span class="mono">BASED IN</span><strong>Nuremberg, Germany</strong></div></div></aside></section>'''

def lab_page(lab, i):
    slug=lab['slug']
    notice=f'<p class="lab-notice">{E(lab["note"])}</p>' if lab['note'] else ''
    extra='''<details class="comparison"><summary>Compare clustering algorithms</summary><iframe title="Clustering algorithm comparison" src="../../labs/k-means-1.html" class="comparison-frame" loading="lazy" sandbox="allow-scripts"></iframe></details>''' if slug=='k-means' else ''
    nextlab=LABS[(i+1)%len(LABS)]
    return f'''<section class="container lab-intro"><a class="back-link mono" href="../index.html">← ALL SPACES</a><span class="eyebrow">EXPERIMENT {i+1:02} / {lab['kind']}</span><h1>{lab['title']}<span class="cyan-text">.</span></h1><p>{lab['description']}</p></section><section class="container lab-section"><div class="lab-shell"><div class="lab-shell-bar"><span class="mono"><span class="status-dot"></span>INTERACTIVE WORKSPACE</span><a href="../../labs/{slug}.html" target="_blank" rel="noopener" class="mono">OPEN FULL WINDOW {icon('arrow',15)}</a></div><div class="lab-launch" data-lab-placeholder>{diagram(lab['visual'])}<div><span class="eyebrow">YOUR EXPERIMENT STARTS HERE</span><h2>Ready to explore?</h2><button class="button primary" type="button" data-launch-lab="../../labs/{slug}.html">Launch playground {icon('play',16)}</button><p>Runs in your browser.</p></div></div><iframe class="lab-frame" title="{lab['title']} interactive playground" data-lab-frame data-height="{lab['height']}" style="height:{lab['height']}px" hidden sandbox="allow-scripts allow-downloads"></iframe><noscript><p><a href="../../labs/{slug}.html">Open the playground in a full window.</a></p></noscript></div>{notice}<div class="lab-guide"><div><span class="eyebrow">QUICK START</span><h2>Get hands-on.</h2><p>{lab['controls']}</p></div><div><span class="eyebrow">WHAT TO LOOK FOR</span><ul>{''.join('<li>'+E(c)+'</li>' for c in lab['concepts'])}</ul></div></div>{extra}<div class="next-lab"><a class="text-link" href="../index.html">← All experiments</a><a class="text-link" href="../{nextlab['slug']}/index.html">Next: {nextlab['short']} {icon('arrow',18)}</a></div></section>'''

def build():
    write(Path('index.html'),page('AI/ML Engineer & Researcher','Home',home()))
    for name,renderer in [('Projects',projects),('Spaces',spaces),('Articles',articles),('Contact',contact)]:
        write(Path(name.lower())/'index.html',page(name,name,renderer(),1))
    for i,lab in enumerate(LABS):
        write(Path('spaces')/lab['slug']/'index.html',page(lab['title'],'Spaces',lab_page(lab,i),2,lab['description']))
    missing=page('Page not found','', '<section class="container page-intro"><span class="eyebrow">404 / SIGNAL LOST</span><h1>PAGE NOT FOUND<span class="cyan-text">.</span></h1><p>This page has moved or doesn’t exist.</p><a class="button primary" href="index.html">Back to home →</a></section>')
    write(Path('404.html'),missing.replace('<head>', '<head><base href="/portfolio/">', 1))
    (ROOT/'.nojekyll').touch()
    print('Generated 12 portfolio pages and the 404 page.')

if __name__=='__main__':
    build()
