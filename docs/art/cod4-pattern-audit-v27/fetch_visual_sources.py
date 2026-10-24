"""Extend pinned existing primary-source caches with visual Java only. No artwork downloads."""
from pathlib import Path
import concurrent.futures,urllib.request,json,re
D=Path(__file__).resolve().parent;R=D.parents[2];jobs=[]
for directory in sorted((R/'build/item-use-references').iterdir()):
 meta=directory/'source.json';tree=directory/'tree.json'
 if not meta.exists() or not tree.exists():continue
 r=json.loads(meta.read_text());repo=r.get('repo');rev=r.get('sha')
 if not repo or not rev:continue
 for entry in json.loads(tree.read_text()).get('tree',[]):
  path=entry['path']
  if not path.endswith('.java') or not re.search(r'/(client|particle|particles|render|renderer|fx|vfx)/',path,re.I):continue
  if re.search(r'/(data|datagen|generated|model|models|test|tests|gui|screen|jei|rei|emi|compat|config|mixin)/',path,re.I):continue
  target=directory/path
  if not target.exists():jobs.append((repo,rev,path,target))
def fetch(row):
 repo,rev,path,target=row
 try:
  request=urllib.request.Request(f'https://raw.githubusercontent.com/{repo}/{rev}/{path}',headers={'User-Agent':'Dynasty-source-review'})
  data=urllib.request.urlopen(request,timeout=25).read();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);return {'repo':repo,'revision':rev,'path':path,'bytes':len(data)}
 except Exception as e:return {'repo':repo,'path':path,'error':str(e)}
print('Pinned Java fetch candidates',len(jobs),flush=True);out=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
 for i,row in enumerate(pool.map(fetch,jobs),1):
  out.append(row)
  if i%100==0:print('Fetched',i,'/',len(jobs),flush=True)
(D/'visual-source-fetch.json').write_text(json.dumps({'notReviewedCount':len(jobs),'files':out},indent=2)+'\n');print('Completed fetch; successful',sum('bytes'in r for r in out),flush=True)
