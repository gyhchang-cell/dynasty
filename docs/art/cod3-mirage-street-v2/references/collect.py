"""Download author gallery candidates, recording cross-task collisions before selection."""
import json,hashlib,subprocess,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
paths=[ROOT/f'docs/art/cod3-{n}/references.json' for n in ['silverfall-v1','ancient-array-v1','crystal-canopy-v2','sun-crow-v2','ice-bloom-v2','xuanwu-v2','azure-dragon-v2']]
paths += [ROOT/'docs/art/cod3-fire-tree-v2/references/selected-100.json',ROOT/'docs/art/cod3-ghost-ship-v2/references/reference-index.json']
prior=set();sources=[]
for p in paths:
 d=json.loads(p.read_text());rs=d if isinstance(d,list) else d['references'];prior.update(r['sha256'] for r in rs);sources.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'count':len(rs)})
(P/'prior-manifests.json').write_text(json.dumps({'sources':sources,'records':sum(r['count'] for r in sources),'hashes':sorted(prior)},indent=2))
rows=[];urls=set()
for slug,d in json.loads((P/'projects.json').read_text()).items():
 for g in d.get('gallery',[]):
  if g['url'] in urls:continue
  urls.add(g['url']);rows.append({'number':len(rows)+1,'project':d['title'],'slug':slug,'type':d['project_type'],'page':f"https://modrinth.com/{d['project_type']}/{slug}/gallery",'title':g.get('title'),'description':g.get('description'),'url':g['url'],'raw_url':g.get('raw_url')})
def fetch(r):
 f=P/f"candidate-{r['number']:03}.img";r['file']=f.name
 if not f.exists():subprocess.run(['curl','-fLsS','--max-time','35','-o',str(f),r['url']],capture_output=True)
 try:
  with Image.open(f) as im:r['dimensions']=im.size
  r['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();r['prior_overlap']=r['sha256'] in prior
 except Exception as e:r['error']=str(e)
 return r
rs=list(concurrent.futures.ThreadPoolExecutor(8).map(fetch,rows));(P/'candidates.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2)+'\n')
for start in range(0,len(rs),20):
 sheet=Image.new('RGB',(1600,1320),(25,28,31));draw=ImageDraw.Draw(sheet)
 for j,r in enumerate(rs[start:start+20]):
  x=j%4*400;y=j//4*264
  if 'error' not in r:
   im=Image.open(P/r['file']).convert('RGB');im.thumbnail((394,218));sheet.paste(im,(x,y))
  draw.text((x+3,y+220),f"{r['number']:03} {r['slug'][:34]}",fill='white');draw.text((x+3,y+234),str(r.get('title'))[:48],fill='white')
  if r.get('prior_overlap'):draw.text((x+3,y+248),'PRIOR TASK DUPLICATE',fill='red')
 sheet.save(P/f"sheet-{start//20+1}.jpg",quality=94)
print('candidates',len(rs),'downloaded',sum('error' not in r for r in rs),'prior collisions',sum(r.get('prior_overlap',False) for r in rs))
