import pathlib,json,urllib.request,ssl,hashlib
R=pathlib.Path(__file__).resolve().parent;D=R/'.work/sources/AlexModGuy__DomesticationInnovation';D.mkdir(parents=True,exist_ok=True);ctx=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Dynasty-guard-source-review'}),context=ctx,timeout=30) as r:return r.read()
try:
 p=D/'source.json'
 if p.exists():meta=json.loads(p.read_text())
 else:
  commit=json.loads(get('https://api.github.com/repos/AlexModGuy/DomesticationInnovation/commits/main'));meta=dict(repo='AlexModGuy/DomesticationInnovation',sha=commit['sha'],officialRepoVerified='https://github.com/AlexModGuy/DomesticationInnovation');p.write_text(json.dumps(meta,indent=2)+'\n')
 p=D/'tree.json'
 if p.exists():tree=json.loads(p.read_text())
 else:tree=json.loads(get('https://api.github.com/repos/'+meta['repo']+'/git/trees/'+meta['sha']+'?recursive=1'));p.write_text(json.dumps(tree,indent=2)+'\n')
 files=[x for x in tree['tree'] if x['path'].endswith('.java') and ('/mixin/' in x['path'] or '/server/entity/' in x['path'] or '/server/misc/' in x['path'] or '/server/item/' in x['path'])];rows=[]
 for x in files:
  out=D/x['path'];out.parent.mkdir(parents=True,exist_ok=True)
  if not out.exists():out.write_bytes(get('https://raw.githubusercontent.com/'+meta['repo']+'/'+meta['sha']+'/'+x['path']))
  raw=out.read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==x['sha'];rows.append(dict(path=x['path'],blob=x['sha'],sha256=hashlib.sha256(raw).hexdigest()))
 (D/'fetch-receipt.json').write_text(json.dumps(dict(files=rows,accepted=0),indent=2)+'\n');print(meta['sha'],len(rows),'sources; zero review credit')
except Exception as e:
 (D/'fetch-failure.json').write_text(json.dumps({'error':repr(e),'retry':False},indent=2)+'\n');raise
