"""Fetch the author's original Google Sites embeds for reference.

The playgrounds in labs/ were first imported from these embeds and have since been
rebuilt by hand on the lab kit (docs/lab-kit.md). They are now maintained in this
repository, so this script never writes into labs/. It saves the untouched originals
to a folder outside the repository, which is useful for checking a rebuilt lab's
behaviour against its source.

The default source is a local audit download. Pass --fetch to download the seven
original public pages again. Existing vendored dependencies are reused.
"""
import argparse
import re
import urllib.request
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

def migrate(source, refresh, out):
    out = out.resolve()
    labs = (ROOT / 'labs').resolve()
    if out == labs or labs in out.parents:
        raise SystemExit('Refusing to write into labs/: those files are the hand-built playgrounds.')
    vendor = ROOT / 'assets' / 'vendor'
    vendor.mkdir(parents=True, exist_ok=True)
    for url, name in VENDORS.items():
        file = vendor / name
        if not file.exists():
            file.write_bytes(fetch(url))
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for lab in LABS:
        slug = lab['slug']
        url = 'https://sites.google.com/view/srinjoy-ghosh/spaces/' + slug
        if refresh:
            parser = Embeds()
            parser.feed(fetch(url).decode('utf-8'))
            codes = parser.code
        else:
            codes = [p.read_text(encoding='utf-8') for p in sorted(source.glob(slug + '-embed-*.html'))]
        if not codes:
            raise RuntimeError('No original embed found for ' + slug)
        for i, code in enumerate(codes):
            name = slug + (f'-{i}' if i else '') + '.html'
            # Point the pinned dependencies at this repository so the original opens offline.
            for external, local in VENDORS.items():
                code = code.replace(external, (vendor / local).as_uri())
            code = re.sub(r'<html(?![^>]*\blang=)', '<html lang="en"', code, count=1)
            with open(out / name, 'w', encoding='utf-8', newline='\n') as f:
                f.write(code)
            count += 1
    print(f'Saved {count} original embeds to {out}. Nothing in labs/ was changed.')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--source', type=Path, default=ROOT.parent / 'source-audit')
    p.add_argument('--out', type=Path, default=ROOT.parent / 'source-audit' / 'original-embeds')
    p.add_argument('--fetch', action='store_true')
    args = p.parse_args()
    migrate(args.source, args.fetch, args.out)
