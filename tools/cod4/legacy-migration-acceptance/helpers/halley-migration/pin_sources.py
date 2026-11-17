"""Fetch GitHub metadata only; verified TLS; no upstream execution."""
from pathlib import Path
import json, ssl, urllib.request, concurrent.futures, hashlib
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=ROOT/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration'
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
CTX=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Halley-static-source-audit','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req,context=CTX,timeout=50) as r: return r.read()
def one(s):
    dest=BASE/'provenance'/s['repo'].replace('/','__');dest.mkdir(parents=True,exist_ok=True)
    cp=dest/'commit.json'; tp=dest/'tree.json'
    if not cp.exists(): cp.write_bytes(fetch('https://api.github.com/repos/'+s['repo']+'/git/commits/'+s['commit']))
    c=json.loads(cp.read_bytes());assert c['sha']==s['commit']
    tree_sha=c['tree']['sha']
    if not tp.exists():tp.write_bytes(fetch('https://api.github.com/repos/'+s['repo']+'/git/trees/'+tree_sha+'?recursive=1'))
    t=json.loads(tp.read_bytes());assert t['sha']==tree_sha and not t.get('truncated')
    return {'repo':s['repo'],'commit':s['commit'],'root_tree':tree_sha,'commit_metadata_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'tree_metadata_sha256':hashlib.sha256(tp.read_bytes()).hexdigest(),'metadata_dir':str(dest.relative_to(ROOT)),'tls_verified':True}
if __name__=='__main__':
    sources=json.loads((DOC/'SOURCE-RESERVATION.json').read_text())['repos']
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: rows=list(pool.map(one,sources))
    (BASE/'source-pins.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
