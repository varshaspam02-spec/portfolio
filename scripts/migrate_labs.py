"""Import the author's public Google Sites embeds without changing their algorithms.

The default source is a local audit download. Pass --fetch to download the seven
original public pages again. Existing vendored dependencies are reused.
"""
import argparse
import json
import re
import urllib.request
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from content import LABS

ROOT = Path(__file__).resolve().parents[1]
VENDORS = {
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js': 'chart-4.4.1.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js': 'papaparse-5.4.1.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js': 'd3-7.8.5.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js': 'd3-7.9.0.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js': 'three-r128.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/d3-sankey/0.12.3/d3-sankey.min.js': 'd3-sankey-0.12.3.min.js',
}

class Embeds(HTMLParser):
    def __init__(self):
        super().__init__()
        self.code = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'data-code' in a:
            self.code.append(a['data-code'])

def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Portfolio-content-migration'})
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read()

def migrate(source, refresh):
    target = ROOT / 'labs'
    vendor = ROOT / 'assets' / 'vendor'
    target.mkdir(exist_ok=True)
    vendor.mkdir(parents=True, exist_ok=True)
    for url, name in VENDORS.items():
        file = vendor / name
        if not file.exists():
            file.write_bytes(fetch(url))
    inventory = []
    for lab in LABS:
        slug = lab['slug']
        url = 'https://sites.google.com/view/srinjoy-ghosh/spaces/' + slug
        if refresh:
            parser = Embeds()
            parser.feed(fetch(url).decode())
            codes = parser.code
        else:
            codes = [p.read_text() for p in sorted(source.glob(slug + '-embed-*.html'))]
        if not codes:
            raise RuntimeError('No original embed found for ' + slug)
        for i, code in enumerate(codes):
            name = slug + (f'-{i}' if i else '') + '.html'
            for external, local in VENDORS.items():
                code = code.replace(external, '../assets/vendor/' + local)
            code = re.sub(r'<html(?![^>]*\blang=)', '<html lang="en"', code, count=1)
            theme = '<link rel="stylesheet" href="../assets/lab-theme.css">\n<script defer src="../assets/lab-bridge.js"></script>\n'
            code = code.replace('</head>', theme + '</head>')
            if lab['note']:
                code = code.replace('<body>', '<body>\n<aside class="sg-context-note">' + escape(lab['note']) + '</aside>', 1)
            # Canvas colors are presentation constants, independent of the math.
            if slug == 'pca-dimensionality-reduction':
                code = code.replace("fillStyle = '#ffffff'", "fillStyle = '#0b141e'")
                code = code.replace("strokeStyle = '#e2e8f0'", "strokeStyle = '#253b49'")
                code = code.replace("strokeStyle = '#2d3748'", "strokeStyle = '#9dbab6'")
                code = code.replace("fillStyle = '#2d3748'", "fillStyle = '#b5cec8'")
            # Each source includes its own complete document and working controls.
            (target / name).write_text(code)
            inventory.append({'source':url, 'file':'labs/' + name, 'kind':'original embedded application'})
    (ROOT / 'docs').mkdir(exist_ok=True)
    (ROOT / 'docs' / 'lab-provenance.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print(f'Migrated {len(inventory)} embeds and {len(VENDORS)} pinned dependencies.')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, default=ROOT.parent / 'source-audit')
    p.add_argument('--fetch', action='store_true')
    args = p.parse_args()
    migrate(args.source, args.fetch)
