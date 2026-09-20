"""Check HTML links, resources, unique IDs, and JavaScript syntax (Python + Node)."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.ids=[]
        self.scripts=[]
        self.inline=False
        self.content=[]
        self.has_title=False
        self.has_lang=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='html': self.has_lang=bool(attrs.get('lang'))
        if tag=='title': self.has_title=True
        if 'id' in attrs:self.ids.append(attrs['id'])
        for attr in ('href','src','data-launch-lab'):
            if attr in attrs:self.links.append(attrs[attr])
        if tag=='script' and not attrs.get('src') and attrs.get('type','') not in ('application/ld+json','application/json'):
            self.inline=True;self.content=[]
    def handle_data(self,data):
        if self.inline:self.content.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.inline:
            self.scripts.append(''.join(self.content));self.inline=False

def check_js(code,label):
    result=subprocess.run(['node','--check'],input=code,text=True,encoding='utf-8',capture_output=True)
    if result.returncode:errors.append(label+': '+result.stderr.strip())

documents={}
for file in ROOT.rglob('*.html'):
    if '.git' in file.parts:continue
    doc=Document();doc.feed(file.read_text(encoding='utf-8'));documents[file]=doc
    if not doc.has_title:errors.append(str(file.relative_to(ROOT))+': missing title')
    if not doc.has_lang:errors.append(str(file.relative_to(ROOT))+': missing document language')
    duplicates={x for x in doc.ids if doc.ids.count(x)>1}
    if duplicates:errors.append(str(file.relative_to(ROOT))+': duplicate IDs '+str(duplicates))
    for i,code in enumerate(doc.scripts):check_js(code,str(file.relative_to(ROOT))+f' inline script {i}')

link_count=0
for file,doc in documents.items():
    for link in doc.links:
        parts=urlsplit(link)
        if parts.scheme or parts.netloc or link.startswith('/'):continue
        target=(file.parent/unquote(parts.path)).resolve() if parts.path else file
        if target.is_dir():target=target/'index.html'
        if not target.exists():errors.append(str(file.relative_to(ROOT))+': missing '+link)
        elif parts.fragment and target in documents and parts.fragment not in documents[target].ids:
            errors.append(str(file.relative_to(ROOT))+': missing anchor '+link)
        link_count+=1
for file in (ROOT/'assets').glob('*.js'):check_js(file.read_text(encoding='utf-8'),str(file.relative_to(ROOT)))
for file in (ROOT/'assets').glob('*.css'):
    for url in re.findall(r'url\([\'"]?([^\)\'\"]+)',file.read_text()):
        if not urlsplit(url).scheme and not (file.parent/url).exists():errors.append(str(file.relative_to(ROOT))+': missing CSS resource '+url)
if errors:
    print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(documents)} HTML documents, {link_count} local links/resources, page IDs, font files, and all application JavaScript syntax.')
