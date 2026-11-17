#!/usr/bin/env python3
"""Copy/download only pinned primary Java candidates into this research's cache."""
import concurrent.futures,hashlib,json,pathlib,re,ssl,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
shared=ROOT.parents[2]/'build/item-use-references/Polarice3__Goety-2'
meta=json.loads((shared/'source.json').read_text());tree=json.loads((shared/'tree.json').read_text())
paths=[x['path'] for x in tree['tree'] if x['path'].endswith('.java') and (re.search(r'/common/entities/(ai|ally|neutral)/',x['path']) or x['path'].endswith(('/api/entities/IOwned.java','/api/entities/ally/IServant.java','/utils/MobUtil.java','/utils/EntityFinder.java','/utils/ModDamageSource.java','/utils/ServantUtil.java','/utils/SEHelper.java')))]
dest=ROOT/'.work/sources/Polarice3__Goety-2';dest.mkdir(parents=True,exist_ok=True)
(dest/'source.json').write_text(json.dumps(meta,indent=2)+'\n')
context=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
def fetch(p):
 out=dest/p;out.parent.mkdir(parents=True,exist_ok=True)
 try:
  if out.exists(): b=out.read_bytes();mode='own-cache'
  elif (shared/p).exists():b=(shared/p).read_bytes();out.write_bytes(b);mode='shared-pinned-copy'
  else:
   url=f"https://raw.githubusercontent.com/{meta['repo']}/{meta['sha']}/{p}"
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Dynasty-guard-implementation-study'}),context=context,timeout=30) as r:b=r.read()
   out.write_bytes(b);mode='pinned-primary-download'
  return dict(path=p,sha256=hashlib.sha256(b).hexdigest(),mode=mode)
 except Exception as e:return dict(path=p,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:results=list(ex.map(fetch,paths))
(dest/'fetch-receipt.json').write_text(json.dumps(dict(repo=meta['repo'],commit=meta['sha'],files=results,acceptedReferences=0),indent=2)+'\n')
print(json.dumps(dict(downloaded=sum('sha256' in r for r in results),failed=sum('error' in r for r in results),accepted=0)))
