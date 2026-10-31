"""Fetch pinned source bytes with verified TLS; never execute downloaded code."""
from pathlib import Path
import json, ssl, urllib.request, hashlib, sys
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'sources/talhanation__recruits'
BASE.mkdir(parents=True,exist_ok=True)
REPO='talhanation/recruits'
CTX=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Halley-local-source-research','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req,context=CTX,timeout=35) as r:return r.read()
def savejson(name,obj):
    (BASE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__' and sys.argv[1]=='pin':
    if (BASE/'source.json').exists():
        print('Existing immutable pin retained:',json.loads((BASE/'source.json').read_text())['sha'])
        raise SystemExit(0)
    metadata=json.loads(get('https://api.github.com/repos/'+REPO))
    commit=json.loads(get('https://api.github.com/repos/'+REPO+'/commits/'+metadata['default_branch']))
    sha=commit['sha'];tree_sha=commit['commit']['tree']['sha']
    tree=json.loads(get(f'https://api.github.com/repos/{REPO}/git/trees/{tree_sha}?recursive=1'))
    assert not tree['truncated'] and tree['sha']==tree_sha
    savejson('repository.json',metadata);savejson('commit.json',commit);savejson('tree.json',tree)
    savejson('source.json',dict(repo=REPO,sha=sha,commit=sha,branch=metadata['default_branch'],tree_sha=tree_sha,
                               official_url=metadata['html_url'],tls_verified=True,research_credit=0,files=[]))
    print(json.dumps({'repo':REPO,'commit':sha,'tree':tree_sha,'entries':len(tree['tree'])}))
    for x in tree['tree']:
        if x['path'].endswith('.java') and any(s in x['path'].lower() for s in ['target','recruit','guard','team','damage','owner','attack']):print(x['path'])
elif __name__=='__main__' and sys.argv[1]=='files':
    meta=json.loads((BASE/'source.json').read_text());tree=json.loads((BASE/'tree.json').read_text())
    paths=sys.argv[2:]
    def fetch(path):
        entry=next(x for x in tree['tree'] if x['path']==path and x['type']=='blob')
        p=BASE/path
        data=p.read_bytes() if p.exists() else get(f"https://raw.githubusercontent.com/{REPO}/{meta['sha']}/{path}")
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert blob==entry['sha'],path
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        return dict(path=path,sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=blob)
    errors=[]
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures=[(path,pool.submit(fetch,path)) for path in paths]
        for path,f in futures:
            try:
                item=f.result();meta['files']=[x for x in meta['files'] if x['path']!=path]+[item]
                print('verified',path)
            except Exception as e:errors.append(dict(path=path,error=str(e)));print('FAILED',path,str(e))
    savejson('source.json',meta)
    if errors:savejson('fetch-errors.json',errors)
