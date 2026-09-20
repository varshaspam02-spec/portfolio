"""Create a portable HTML preview and a clean source ZIP for review."""
import base64
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'deliverables'

def inline_css(file):
    css=file.read_text()
    def asset(match):
        url=match.group(1).strip('\'"')
        target=file.parent/url
        if urlsplit(url).scheme or not target.is_file():return match.group(0)
        media='font/woff2' if target.suffix=='.woff2' else 'application/octet-stream'
        return 'url("data:'+media+';base64,'+base64.b64encode(target.read_bytes()).decode()+'")'
    return re.sub(r'url\(([^)]+)\)',asset,css)

def inline_document(file):
    html=file.read_text()
    deferred=[]
    def stylesheet(match):
        tag=match.group(0)
        href=re.search(r'href="([^"]+)"',tag)
        if href and 'stylesheet' in tag and not urlsplit(href[1]).scheme:
            return '<style>'+inline_css(file.parent/href[1])+'</style>'
        return '' if 'rel="icon"' in tag else tag
    html=re.sub(r'<link\b[^>]*>',stylesheet,html)
    def script(match):
        target=(file.parent/match.group(2)).resolve()
        if not target.is_file():return match.group(0)
        code=target.read_text().replace('</script','<\\/script')
        tag='<script>'+code+'</script>'
        if 'defer' in match.group(1):
            deferred.append(tag);return ''
        return tag
    html=re.sub(r'<script\b([^>]*?)src="([^"]+)"[^>]*>\s*</script>',script,html)
    return html.replace('</body>',''.join(deferred)+'</body>')

BRIDGE=r'''
(() => {
  const currentPath = __PATH__;
  function localPath(raw) {
    return new URL(raw, 'https://portfolio.preview/' + currentPath).pathname.slice(1);
  }
  document.addEventListener('click', event => {
    const launch = event.target.closest('[data-launch-lab]');
    if (launch) {
      event.preventDefault(); event.stopImmediatePropagation();
      parent.postMessage({type:'sg-preview-launch', path:localPath(launch.dataset.launchLab)}, '*');
      return;
    }
    const link = event.target.closest('a');
    if (!link) return;
    const raw = link.getAttribute('href') || '';
    if (!raw || raw.startsWith('#') || /^[a-z][a-z0-9+.-]*:/i.test(raw) || raw.startsWith('//')) return;
    event.preventDefault();
    parent.postMessage({type:'sg-preview-navigate',path:localPath(raw)}, '*');
  }, true);
  window.addEventListener('message', event => {
    if (event.source !== parent || event.data?.type !== 'sg-preview-lab') return;
    const frame = document.querySelector('[data-lab-frame]');
    if (!frame) return;
    frame.srcdoc=event.data.html;
    frame.hidden=false;
    document.querySelector('[data-lab-placeholder]').hidden=true;
  });
  // The comparison table is embedded locally in the portable preview as well.
  const comparison=document.querySelector('.comparison-frame');
  if (comparison) {
    comparison.removeAttribute('src');
    parent.postMessage({type:'sg-preview-comparison',path:'labs/k-means-1.html'},'*');
    window.addEventListener('message',event=>{
      if(event.source===parent && event.data?.type==='sg-preview-comparison') comparison.srcdoc=event.data.html;
    });
  }
})();
'''

def build():
    OUT.mkdir(exist_ok=True)
    routes={}
    for file in sorted(ROOT.rglob('*.html')):
        path=file.relative_to(ROOT).as_posix()
        html=inline_document(file)
        if not path.startswith('labs/'):
            bridge=BRIDGE.replace('__PATH__',json.dumps(path))
            html=html.replace('</body>','<script>'+bridge+'</script></body>')
        routes[path]=html
    encoded=json.dumps(routes,ensure_ascii=False).replace('<','\\u003c')
    shell='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Srinjoy Ghosh · Cyberpunk portfolio preview</title><style>html,body{margin:0;height:100%;background:#080c13}iframe{display:block;width:100%;height:100dvh;border:0}</style></head><body><iframe id="preview" title="Srinjoy Ghosh portfolio preview" sandbox="allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox"></iframe><script>
const routes=__ROUTES__;
const preview=document.getElementById('preview');
function render(){const path=decodeURIComponent(location.hash.slice(1))||'index.html';preview.srcdoc=routes[path]||routes['404.html'];}
window.addEventListener('hashchange',render);
window.addEventListener('message',event=>{
 if(event.source!==preview.contentWindow||!event.data)return;
 const {type,path}=event.data;if(!routes[path])return;
 if(type==='sg-preview-navigate') { if(location.hash.slice(1)===path)render();else location.hash=path; }
 if(type==='sg-preview-launch') preview.contentWindow.postMessage({type:'sg-preview-lab',html:routes[path]},'*');
 if(type==='sg-preview-comparison') preview.contentWindow.postMessage({type:'sg-preview-comparison',html:routes[path]},'*');
});
render();
</script></body></html>'''.replace('__ROUTES__',encoded)
    preview_file=OUT/'srinjoy-cyberpunk-preview.html'
    preview_file.write_text(shell)
    archive=OUT/'srinjoy-cyberpunk-source.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for file in sorted(ROOT.rglob('*')):
            if not file.is_file() or any(p in ('.git','__pycache__','.cache') for p in file.parts):continue
            z.write(file,'portfolio/'+file.relative_to(ROOT).as_posix())
    print(json.dumps({'preview':str(preview_file),'preview_bytes':preview_file.stat().st_size,'source_zip':str(archive),'zip_bytes':archive.stat().st_size,'routes':len(routes)},indent=2))

if __name__=='__main__':build()
