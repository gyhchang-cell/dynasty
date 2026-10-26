"""Pinned entity/AI primary-source candidates. No acceptance from fetching/indexing."""
import concurrent.futures,hashlib,json,pathlib,re,ssl,sys,urllib.request
R=pathlib.Path(__file__).resolve().parent;B=R.parents[2]/'build/item-use-references';ctx=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
for dirname in sys.argv[1:]:
 src=B/dirname;meta=json.loads((src/'source.json').read_text());tree=json.loads((src/'tree.json').read_text());dest=R/'.work/sources'/dirname;dest.mkdir(parents=True,exist_ok=True);(dest/'source.json').write_text(json.dumps(meta,indent=2)+'\n')
 paths=[x['path'] for x in tree['tree'] if x['path'].endswith('.java') and re.search(r'/(entity|entities|ai)/',x['path']) and not re.search(r'/(client|render|model|datagen|test)/',x['path'],re.I)]
 def fetch(p):
  out=dest/p;out.parent.mkdir(parents=True,exist_ok=True)
  try:
   if out.exists():b=out.read_bytes();mode='own-cache'
   elif (src/p).exists():b=(src/p).read_bytes();out.write_bytes(b);mode='shared-pinned-copy'
   else:
    url=f"https://raw.githubusercontent.com/{meta['repo']}/{meta['sha']}/{p}"
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Dynasty-guard-implementation-study'}),context=ctx,timeout=30) as res:b=res.read()
    out.write_bytes(b);mode='pinned-primary-download'
   return dict(path=p,sha256=hashlib.sha256(b).hexdigest(),mode=mode)
  except Exception as e:return dict(path=p,error=str(e))
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:rows=list(ex.map(fetch,paths))
 (dest/'fetch-receipt.json').write_text(json.dumps(dict(repo=meta['repo'],commit=meta['sha'],files=rows,acceptedReferences=0),indent=2)+'\n')
 print(json.dumps(dict(repo=meta['repo'],downloaded=sum('sha256'in x for x in rows),failed=sum('error'in x for x in rows),accepted=0)),flush=True)
