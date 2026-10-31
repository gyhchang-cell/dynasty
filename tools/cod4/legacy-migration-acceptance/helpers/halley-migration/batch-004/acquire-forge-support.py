"""Read exact declared source artifact and official Git byte provenance, never execute upstream."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,io,zipfile,ssl,urllib.request
BASE=Path(__file__).resolve().parent
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
CTX=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
def get(u):
 with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Halley-static-source-audit'}),context=CTX,timeout=55) as r:return r.read()
def sha(b):return hashlib.sha256(b).hexdigest()
repo='MinecraftForge/MinecraftForge';commit='d13dd327bdc75c010f3358992e80e7e92f51e030'
cb=get('https://api.github.com/repos/'+repo+'/git/commits/'+commit);c=json.loads(cb)
tb=get('https://api.github.com/repos/'+repo+'/git/trees/'+c['tree']['sha']+'?recursive=1');t=json.loads(tb)
assert not t.get('truncated')
rel='src/main/java/net/minecraftforge/items/ItemStackHandler.java'
raw=get('https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+rel)
blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
assert next(x['sha'] for x in t['tree'] if x['path']==rel)==blob
url='https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.1.3/forge-1.20.1-47.1.3-sources.jar'
jar=get(url)
with zipfile.ZipFile(io.BytesIO(jar)) as z:
 names=[n for n in z.namelist() if n.endswith('net/minecraftforge/items/ItemStackHandler.java')]
 assert len(names)==1
 artifact_source=z.read(names[0])
meta=BASE/'provenance'/'MinecraftForge__MinecraftForge';meta.mkdir(parents=True,exist_ok=True)
(meta/'commit.json').write_bytes(cb);(meta/'tree.json').write_bytes(tb)
(meta/'ItemStackHandler-47.1.3.java').write_bytes(artifact_source)
artifact={'url':url,'artifact_sha256':sha(jar),'entry':names[0],'entry_sha256':sha(artifact_source),'git_source_sha256':sha(raw),'exact_byte_match':artifact_source==raw,'note':'Only a supporting codec for actual ToolBelt owner lifecycle, credit0; branch commit is not asserted to be release47.1.3 commit.'}
(meta/'declared-source-artifact.json').write_text(json.dumps(artifact,indent=2)+'\n')
source=BASE/'sources'/'MinecraftForge__MinecraftForge'/rel;source.parent.mkdir(parents=True,exist_ok=True);source.write_bytes(raw)
a=json.loads((BASE/'source-manifest.json').read_text());a=[s for s in a if s['repo']!=repo]
a.append({'repo':repo,'branch':'1.20.1','commit':commit,'git_tree':c['tree']['sha'],'scope':'support only ItemStackHandler for declared ToolBelt Forge1.20.1-47.1.3','commit_metadata_sha256':sha(cb),'tree_metadata_sha256':sha(tb),'files':[{'path':rel,'source':str(source.relative_to(ROOT)),'sourceSha256':sha(raw),'source_blob':blob}]})
(BASE/'source-manifest.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(artifact,indent=2))
