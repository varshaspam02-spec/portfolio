"""Generate a dependency-free, GitHub Pages-compatible static portfolio."""
from html import escape
from pathlib import Path
import math
import random
import re
from content import PROFILE, PROJECTS, ARTICLES, LABS, EXTERNAL_LAB

ROOT = Path(__file__).resolve().parents[1]
E = escape

# Runs before first paint: enables JS-only styles, restores motion/theme preferences,
# and hands the click position to the page-transition reveal. The timeout is a
# failsafe so content never stays hidden if main.js fails to load.
HEAD_SCRIPT = (
    "(function(){var d=document.documentElement;d.classList.add('js');"
    "setTimeout(function(){if(!d.classList.contains('js-ready'))d.classList.remove('js')},4000);"
    "try{var p=sessionStorage.getItem('sg-vt');"
    "if(p){p=p.split(',');d.style.setProperty('--vt-x',p[0]+'px');d.style.setProperty('--vt-y',p[1]+'px');sessionStorage.removeItem('sg-vt')}"
    "var m=localStorage.getItem('sg-motion');"
    "if(m==='off'||(!m&&matchMedia('(prefers-reduced-motion: reduce)').matches))d.dataset.motion='off';"
    "var t=localStorage.getItem('sg-theme');if(t)d.dataset.theme=t}catch(e){}})();"
)

THEMES = [('aurora', 'Aurora'), ('ember', 'Ember'), ('acid', 'Acid')]

# Repositories shown under "Selected work" on the home page, in archive order.
FEATURED = ['linkedin-job-mcp', 'DeepseekOCR', 'Web_search_mcp']

def icon(name, size=24):
    paths = {
        'arrow': '<path d="M6 18 18 6M6 6h12v12"/>',
        'arrow-right': '<path d="M4 12h16m-6-6 6 6-6 6"/>',
        'arrow-left': '<path d="M20 12H4m6-6-6 6 6 6"/>',
        'arrow-down': '<path d="M12 4v16m-6-6 6 6 6-6"/>',
        'arrow-up': '<path d="M12 20V4M6 10l6-6 6 6"/>',
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
        'copy': '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
        'menu': '<path d="M4 8h16M4 16h16"/>',
        'box': '<path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
    }
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths.get(name,paths["network"])}</svg>'

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def split_words(html):
    """Wrap each word for the staggered headline reveal; tags and spacing pass through."""
    out, count = [], 0
    for token in re.split(r'(<[^>]+>|\s+)', html):
        if not token or token.startswith('<') or token.isspace():
            out.append(token)
        else:
            out.append(f'<span class="w" style="--i:{count}">{token}</span>')
            count += 1
    return ''.join(out)

def split_chars(text, start=0):
    return ''.join(f'<span class="ch" style="--i:{start+i}">{E(c)}</span>' for i, c in enumerate(text))

def diagram(kind):
    rng = random.Random(11)
    shapes = ['<path d="M20 180H460M20 120H460M20 60H460M80 20V220M160 20V220M240 20V220M320 20V220M400 20V220" class="diagram-grid"/>']
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
        for x,y in nodes: shapes.append(f'<rect x="{x-16}" y="{y-10}" width="32" height="20" rx="6" class="chart-node"/>')
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
                shapes.append(f'<rect x="{128+i*30}" y="{20+j*30}" width="25" height="25" rx="5" class="heat" opacity="{opacity:.3f}"/>')
    elif kind=='quantization':
        points=' '.join(f'{40+i*4},{120-math.sin(i/12)*60}' for i in range(100))
        shapes.append(f'<polyline points="{points}" class="cluster-ring pink"/>')
        pts=[]
        for i in range(11):
            y=round((120-math.sin(i*10/12)*60)/25)*25
            pts.extend([(40+i*38,y),(78+i*38,y)])
        shapes.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+'" class="chart-line"/>')
    else:
        shapes.append('<path d="M120 75V40h40M320 40h40v35M360 165v35h-40M160 200h-40v-35" class="chart-line"/><rect x="179" y="76" width="100" height="109" rx="8" class="cluster-ring pink"/><path d="M130 120h220" class="trajectory"/>')
    return '<svg viewBox="0 0 480 240" fill="none" aria-hidden="true">'+''.join(shapes)+'</svg>'

def external(url, label, cls='text-link'):
    return f'<a class="{cls}" href="{E(url)}" target="_blank" rel="noopener noreferrer">{label}{icon("arrow",18)}</a>'

def button(label, href='', cls='primary', ico='arrow', attrs=''):
    """Pill button with a rolling label. Renders a link when href is given."""
    inner=f'<span class="label" data-text="{E(label)}"><span>{E(label)}</span></span><span class="button-icon">{icon(ico,17)}</span>'
    if href:
        return f'<a class="button {cls}" href="{E(href)}" data-magnetic{attrs}>{inner}</a>'
    return f'<button class="button {cls}" type="button" data-magnetic{attrs}>{inner}</button>'

def project_card(p, i, compact=False):
    tags=''.join(f'<span>{E(t)}</span>' for t in p['tags'])
    features=''.join(f'<li>{E(f)}</li>' for f in p['features'])
    search=E(' '.join([p['name'],p['description'],p['category'],*p['tags']]).lower())
    details='' if compact else '<details><summary>What it does<span aria-hidden="true">+</span></summary><ul>'+features+'</ul></details>'
    repo='https://github.com/GhoshSrinjoy/'+p['repo']
    return f'''<article class="project-card surface" data-project data-spotlight data-tilt data-reveal data-category="{E(p['category'])}" data-search="{search}" style="view-transition-name:p-{slugify(p['repo'])}">
      <div class="card-top"><span class="project-icon">{icon(p['icon'],26)}</span><span class="card-index mono">{i:02}</span></div>
      <span class="category-label">{E(p['category'])}</span><h3>{E(p['name'])}</h3>
      <p>{E(p['description'])}</p><div class="tags">{tags}</div>
      {details}
      <a class="card-link" href="{E(repo)}" target="_blank" rel="noopener noreferrer"><span>View repository</span><span class="arrow-circle">{icon('arrow',17)}</span></a>
    </article>'''

def lab_card(lab, i, prefix, ext=False):
    href=lab['url'] if ext else prefix+'spaces/'+lab['slug']+'/index.html'
    attrs=' target="_blank" rel="noopener noreferrer"' if ext else ''
    name='lab-external' if ext else 'lab-'+lab['slug']
    action='Open external demo' if ext else 'Launch playground'
    return f'''<a class="lab-card surface" href="{E(href)}"{attrs} data-spotlight data-tilt data-reveal data-cursor="Open"><div class="lab-visual" style="view-transition-name:{name}">{diagram(lab['visual'])}<span class="lab-number mono">Experiment {i:02}</span></div><div class="lab-copy"><span class="category-label">{E(lab['kind'])}</span><h3>{E(lab.get('short',lab['title']))}</h3><p>{E(lab['description'])}</p><span class="lab-action"><span>{action}</span><span class="arrow-circle">{icon('arrow',17)}</span></span></div></a>'''

def section_head(number, label, title, link=''):
    return f'<div class="section-head"><div><span class="eyebrow" data-reveal><b>{number}</b>{label}</span><h2 data-split>{split_words(title)}</h2></div>{link}</div>'

def page_intro(number, label, title, text):
    return f'<section class="container page-intro"><span class="eyebrow" data-reveal><b>{number}</b>{label}</span><h1 data-split>{split_words(title)}</h1><p data-reveal>{text}</p></section>'

def page(title, active, content, depth=0, description=None):
    pre='../'*depth
    links=[('Home','index.html'),('Projects','projects/index.html'),('Spaces','spaces/index.html'),('Articles','articles/index.html'),('Contact','contact/index.html')]
    nav=''.join(f'<a href="{pre+url}"'+(' aria-current="page"' if active==name else '')+f' style="--i:{i}">{name}</a>' for i,(name,url) in enumerate(links))
    themes=''.join(f'<button type="button" data-theme-set="{key}" aria-pressed="{str(key=="aurora").lower()}" aria-label="{label} accent theme" title="{label}"></button>' for key,label in THEMES)
    description=description or PROFILE['intro']
    brand=f'<a class="brand" href="{pre}index.html" aria-label="Srinjoy Ghosh home"><span class="brand-mark" aria-hidden="true">SG</span><span class="brand-name">Srinjoy Ghosh</span></a>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#05060b"><title>{E(title)} | Srinjoy Ghosh</title>
<meta name="description" content="{E(description)}"><meta property="og:title" content="{E(title)} | Srinjoy Ghosh"><meta property="og:description" content="{E(description)}"><meta property="og:type" content="website">
<script>{HEAD_SCRIPT}</script>
<link rel="icon" type="image/svg+xml" href="{pre}assets/favicon.svg"><link rel="preload" href="{pre}assets/fonts/geist.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{pre}assets/styles.css"><script defer src="{pre}assets/fx.js"></script><script defer src="{pre}assets/main.js"></script></head>
<body><a class="skip-link" href="#main">Skip to content</a>
<div class="backdrop" aria-hidden="true"><div class="ambient"><i></i><i></i><i></i></div><canvas class="aurora" data-aurora></canvas><div class="grain"></div></div>
<div class="scroll-progress" aria-hidden="true"></div>
<header class="site-header"><div class="header-pill">{brand}
<nav id="primary-nav" aria-label="Main navigation">{nav}</nav>
<div class="header-tools"><button class="theme-cycle" type="button" data-theme-cycle aria-label="Switch accent theme" title="Switch accent theme"><i></i></button>{external(PROFILE['github'],'GitHub','header-github')}<button class="menu-button" type="button" aria-expanded="false" aria-controls="primary-nav"><span>Menu</span>{icon('menu',18)}</button></div></div></header>
<main id="main" tabindex="-1">{content}</main>
<footer class="site-footer"><div class="container footer-top"><div><a class="brand" href="{pre}index.html"><span class="brand-mark" aria-hidden="true">SG</span><span class="brand-name">Srinjoy Ghosh</span></a><p class="footer-tagline">Keep <em>building.</em></p></div><div class="footer-links">{external(PROFILE['github'],'GitHub')}{external(PROFILE['linkedin'],'LinkedIn')}<a class="text-link" href="mailto:{PROFILE['email']}">Email{icon('arrow',18)}</a></div></div>
<div class="footer-wordmark" aria-hidden="true">Srinjoy Ghosh</div>
<div class="container footer-bottom"><span>© <span data-year>2026</span> Srinjoy Ghosh</span><span class="footer-location"><span class="status-dot"></span>Nuremberg, Germany<span class="local-time" data-local-time></span></span><div class="theme-switch" role="group" aria-label="Accent theme">{themes}</div><button class="motion-toggle" aria-pressed="false" type="button">Pause animations</button><a href="#main" class="back-top">Back to top {icon('arrow-up',14)}</a></div></footer>
</body></html>'''

def write(path, html):
    target=ROOT/path
    target.parent.mkdir(parents=True,exist_ok=True)
    # Explicit encoding and newlines keep the output identical on Windows, macOS and Linux.
    with open(target,'w',encoding='utf-8',newline='\n') as f: f.write(html)

def home():
    selected=''.join(project_card(p,i+1,True) for i,p in enumerate(PROJECTS) if p['repo'] in FEATURED)
    labcards=''.join(lab_card(LABS[i],i+1,'') for i in [0,3,6])
    stack=[]
    for p in PROJECTS:
        for t in p['tags']:
            if t not in stack: stack.append(t)
    marquee=''.join(f'<span>{E(t)}</span>' for t in stack)
    article_rows=''.join(f'<a class="article-row" href="{a["url"]}" target="_blank" rel="noopener noreferrer" data-reveal data-cursor="Read"><span class="mono article-index">{i+1:02}</span><div><span class="category-label">{a["format"]} / {a["category"]}</span><h3>{a["title"]}</h3></div><span class="arrow-circle">{icon("arrow",20)}</span></a>' for i,a in enumerate(ARTICLES))
    demos=len(LABS)+1
    return f'''<section class="hero"><canvas class="hero-cloud" data-cloud aria-hidden="true"></canvas>
    <div class="container hero-inner"><p class="hero-badge"><span class="status-dot"></span>AI/ML Engineer &amp; Researcher<span class="hero-place"><i aria-hidden="true"></i>Nuremberg, Germany</span></p>
    <h1 class="hero-title" aria-label="Srinjoy Ghosh" data-weight-field><span class="hero-line" aria-hidden="true">{split_chars('Srinjoy')}</span><span class="hero-line" aria-hidden="true">{split_chars('Ghosh',7)}<span class="ch hero-period" style="--i:12"></span></span></h1>
    <p class="hero-statement">Engineering intelligence.<br><em>From idea to real-world impact.</em></p><p class="hero-description">{PROFILE['intro']}</p>
    <div class="hero-actions">{button('Explore projects','projects/index.html')}{button('Enter the lab','spaces/index.html','secondary','arrow-right')}</div></div>
    <div class="container hero-foot"><span class="scroll-cue mono"><span class="scroll-cue-line"></span>Scroll</span><button class="cloud-label mono" type="button" data-cloud-next hidden><span data-cloud-name>Embedding space</span><span class="cloud-hint">Click to morph</span></button></div></section>
    <div class="marquee" aria-hidden="true" data-marquee><div class="marquee-track">{marquee}{marquee}</div></div>
    <section class="section container">{section_head('01','Selected work','Ideas, built into <em>systems.</em>', '<a class="text-link" href="projects/index.html" data-reveal>All '+str(len(PROJECTS))+' projects'+icon('arrow',18)+'</a>')}<div class="project-grid">{selected}</div></section>
    <section class="section container">{section_head('02','The engineer','Curiosity in. <em>Intelligence out.</em>')}<div class="bento">
      <article class="bento-item bento-bio surface" data-spotlight data-reveal><p class="lead">{E(PROFILE['bio'])}</p><p>{PROFILE['now']}</p><a class="text-link" href="contact/index.html">Let’s connect{icon('arrow',18)}</a></article>
      <div class="bento-item bento-stat surface" data-spotlight data-reveal><strong><span data-count="{len(PROJECTS)}">{len(PROJECTS)}</span></strong><span>Open-source projects</span></div>
      <div class="bento-item bento-stat surface" data-spotlight data-reveal><strong><span data-count="{demos}">{demos:02}</span></strong><span>Interactive demos</span></div>
      <div class="bento-item bento-stat surface" data-spotlight data-reveal><strong><span data-count="5">05</span><i>+</i></strong><span>Years of experience</span></div>
      <div class="bento-item bento-place surface" data-spotlight data-reveal>{icon('location',22)}<span class="category-label">Based in</span><strong>Nuremberg, Germany</strong><span class="local-time mono" data-local-time></span></div>
      <div class="bento-item bento-focus surface" data-spotlight data-reveal><span class="category-label">Focus areas</span><div class="expertise-tags"><span>Agent systems</span><span>Multimodal RAG</span><span>Model optimization</span><span>Applied ML</span></div><p class="bento-signature">Agents. Models. <em>Real-world systems.</em></p></div>
    </div></section>
    <section class="section container">{section_head('03','Experimental spaces','Less theory. <em>More tinkering.</em>', '<a class="text-link" href="spaces/index.html" data-reveal>Explore all spaces'+icon('arrow',18)+'</a>')}<p class="section-intro" data-reveal>Draw, adjust, run, repeat. Get a feel for the algorithms behind intelligent systems.</p><div class="lab-grid">{labcards}</div></section>
    <section class="section container">{section_head('04','Field notes','Making complex things <em>click.</em>')}<div class="article-list">{article_rows}</div></section>
    <section class="container"><div class="contact-cta surface" data-spotlight data-reveal><div class="cta-orb" aria-hidden="true"></div><span class="eyebrow">Have something in mind?</span><h2 data-split>{split_words('Let’s build <em>what’s next.</em>')}</h2>{button('Get in touch','contact/index.html')}</div></section>'''

def projects():
    categories=['All','AI agents','ML systems','Developer tools','Data tools']
    counts={c:sum(p['category']==c for p in PROJECTS) for c in categories}
    counts['All']=len(PROJECTS)
    filters=''.join(f'<button class="filter-button" type="button" data-filter="{c}" aria-pressed="{str(c=="All").lower()}">{c}<span>{counts[c]}</span></button>' for c in categories)
    cards=''.join(project_card(p,i+1) for i,p in enumerate(PROJECTS))
    intro=page_intro('01','Project archive','Built to <em>do.</em>','Open-source tools, intelligent agents, and experiments that made it out of the notebook.')
    return f'''{intro}<section class="container archive-section"><div class="project-toolbar" data-reveal><div class="filters" role="group" aria-label="Filter projects by category">{filters}</div><label class="search-field">{icon('search',18)}<input id="project-search" type="search" placeholder="Search projects…" aria-label="Search projects"></label></div><div class="results-line mono"><span id="result-count" role="status" aria-live="polite">{len(PROJECTS)} projects</span><span>Code / Experiments / Tools</span></div><div class="project-grid">{cards}</div><div class="empty-state surface" id="empty-state" hidden><h2>No matching projects.</h2><p>Try another keyword or clear the filters.</p>{button('Clear filters','','secondary','arrow-right',' id="clear-filters"')}</div></section>'''

def spaces():
    cards=''.join(lab_card(l,i+1,'../') for i,l in enumerate(LABS))+lab_card(EXTERNAL_LAB,len(LABS)+1,'../',True)
    intro=page_intro('02','The playground','Learn by <em>doing.</em>','Eight ways to explore machine learning. Change a parameter, follow a pattern, and see the idea come to life.')
    return f'''{intro}<section class="container archive-section"><div class="results-line mono"><span>{len(LABS):02} local labs + 01 external demo</span><span>No setup. Just explore.</span></div><div class="lab-grid">{cards}</div></section>'''

def articles():
    cards=''.join(f'''<article class="article-feature surface" data-spotlight data-reveal><div class="article-art">{diagram(a['visual'])}<span class="mono">Field notes / {i+1:02}</span></div><div class="article-feature-copy"><span class="category-label">{a['category']} / {a['format']}</span><h2>{a['title']}</h2><p class="article-subtitle">{a['subtitle']}</p><p>{a['description']}</p>{button('Read '+('on Medium' if i==0 else 'and explore'),a['url'],'secondary','arrow',' target="_blank" rel="noopener noreferrer"')}</div></article>''' for i,a in enumerate(ARTICLES))
    intro=page_intro('03','Field notes','Ideas, <em>unpacked.</em>','Practical writing on machine learning, data, and engineering. Mathematics meets things you can actually try.')
    return f'''{intro}<section class="container archive-section article-features">{cards}</section>'''

def contact():
    email=PROFILE['email']
    intro=page_intro('04','Open a channel','Let’s <em>connect.</em>','Research ideas, engineering challenges, or a conversation about what comes next.')
    channels=f'''<div class="contact-channels"><a href="{PROFILE['linkedin']}" target="_blank" rel="noopener noreferrer"><span class="mono">01</span><div><strong>LinkedIn</strong><span>Professional connections</span></div><span class="arrow-circle">{icon('arrow',18)}</span></a><a href="{PROFILE['github']}" target="_blank" rel="noopener noreferrer"><span class="mono">02</span><div><strong>GitHub</strong><span>Explore my code</span></div><span class="arrow-circle">{icon('arrow',18)}</span></a><a href="tel:+4915560812680"><span class="mono">03</span><div><strong>{PROFILE['phone']}</strong><span>Phone</span></div><span class="arrow-circle">{icon('arrow',18)}</span></a></div>'''
    return f'''{intro}<section class="container contact-grid archive-section"><div class="contact-main" data-reveal><span class="eyebrow">Direct line</span><h2>Good things start<br>with a <em>conversation.</em></h2><a class="email-link" href="mailto:{email}"><span>{email}</span>{icon('arrow',26)}</a><div class="contact-buttons">{button('Write an email','mailto:'+email,'primary','mail')}{button('Copy address','','secondary','copy',f' id="copy-email" data-email="{email}"')}</div><p class="copy-status" id="copy-status" role="status" aria-live="polite"></p>{channels}</div><aside class="contact-profile surface" data-spotlight data-tilt data-reveal><div class="profile-glyph" aria-hidden="true">SG</div><span class="eyebrow">The person behind the code</span><h2>Srinjoy Ghosh</h2><p class="profile-role">AI &amp; ML Engineer</p><p>Over five years building intelligent systems. Creator of RICHES, a multimodal, cross-lingual RAG system.</p><div class="location-card">{icon('location',24)}<div><span class="category-label">Based in</span><strong>Nuremberg, Germany</strong><span class="local-time mono" data-local-time></span></div></div></aside></section>'''

def lab_page(lab, i):
    slug=lab['slug']
    notice=f'<p class="lab-notice">{E(lab["note"])}</p>' if lab['note'] else ''
    extra='''<details class="comparison surface"><summary>Compare clustering algorithms</summary><iframe title="Clustering algorithm comparison" src="../../labs/k-means-1.html" class="comparison-frame" loading="lazy" sandbox="allow-scripts"></iframe></details>''' if slug=='k-means' else ''
    nextlab=LABS[(i+1)%len(LABS)]
    concepts=''.join('<li>'+E(c)+'</li>' for c in lab['concepts'])
    launch=button('Launch playground','','primary','play',f' data-launch-lab="../../labs/{slug}.html"')
    return f'''<section class="container lab-intro"><a class="back-link mono" href="../index.html">{icon('arrow-left',15)}All spaces</a><span class="eyebrow" data-reveal><b>{i+1:02}</b>{lab['kind']}</span><h1 data-split>{split_words(lab['title']+'<em>.</em>')}</h1><p data-reveal>{lab['description']}</p></section><section class="container lab-section"><div class="lab-shell surface"><div class="lab-shell-bar"><span class="mono"><span class="status-dot"></span>Interactive workspace</span><a href="../../labs/{slug}.html" target="_blank" rel="noopener" class="mono">Open full window {icon('arrow',15)}</a></div><div class="lab-launch" data-lab-placeholder><div class="lab-launch-visual" style="view-transition-name:lab-{slug}">{diagram(lab['visual'])}</div><div><span class="eyebrow">Your experiment starts here</span><h2>Ready to <em>explore?</em></h2>{launch}<p>Runs in your browser.</p></div></div><iframe class="lab-frame" title="{lab['title']} interactive playground" data-lab-frame data-height="{lab['height']}" style="height:{lab['height']}px" hidden sandbox="allow-scripts allow-downloads"></iframe><noscript><p><a href="../../labs/{slug}.html">Open the playground in a full window.</a></p></noscript></div>{notice}<div class="lab-guide"><div class="surface" data-spotlight data-reveal><span class="eyebrow">Quick start</span><h2>Get hands-on.</h2><p>{lab['controls']}</p></div><div class="surface" data-spotlight data-reveal><span class="eyebrow">What to look for</span><ul>{concepts}</ul></div></div>{extra}<div class="next-lab"><a class="text-link" href="../index.html">{icon('arrow-left',18)}All experiments</a><a class="text-link" href="../{nextlab['slug']}/index.html">Next: {nextlab['short']}{icon('arrow',18)}</a></div></section>'''

def build():
    write(Path('index.html'),page('AI/ML Engineer & Researcher','Home',home()))
    for name,renderer in [('Projects',projects),('Spaces',spaces),('Articles',articles),('Contact',contact)]:
        write(Path(name.lower())/'index.html',page(name,name,renderer(),1))
    for i,lab in enumerate(LABS):
        write(Path('spaces')/lab['slug']/'index.html',page(lab['title'],'Spaces',lab_page(lab,i),2,lab['description']))
    lost=page_intro('404','Signal lost','Page not <em>found.</em>','This page has moved or doesn’t exist.')
    lost=lost.replace('</section>',button('Back to home','index.html','primary','arrow-right')+'</section>')
    missing=page('Page not found','',lost)
    write(Path('404.html'),missing.replace('<head>', '<head><base href="/portfolio/">', 1))
    (ROOT/'.nojekyll').touch()
    print('Generated 12 portfolio pages and the 404 page.')

if __name__=='__main__':
    build()
