"""Cache author galleries for visual study. Downloads are not viewed selections."""
import concurrent.futures
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw

P=Path(__file__).resolve().parent
ROOT=P.parents[3]
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Dynasty-original-art-study/1.0'})
    with urllib.request.urlopen(req,timeout=35) as f:return f.read()
previous=json.loads((ROOT/'docs/art/cod3-great-wall-echo-v2/references/prior-manifests.json').read_text())
paths=[ROOT/r['path'] for r in previous['sources']]
paths += [ROOT/'docs/art/cod3-great-wall-echo-v2/references/selected-100.json']
army=ROOT/'docs/art/cod3-ghost-army-v2/references/selected-100.json'
if army.exists():paths.append(army)
army_texture=ROOT/'docs/art/cod3-ghost-army-v2/texture/research/selected-100.json'
if army_texture.exists():paths.append(army_texture)
prior=set();sources=[]
for p in paths:
    d=json.loads(p.read_text());rows=d if isinstance(d,list) else d['references']
    prior.update(r['sha256'] for r in rows)
    sources.append({'path':str(p.relative_to(ROOT)),'count':len(rows),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
dump(P/'prior-manifests.json',{'sources':sources,'records':sum(r['count'] for r in sources),'hashes':sorted(prior)})
queries=['chinese','japanese','shrine','village','market','haunted','underground village','ruins']
projects={};errors=[]
for q in queries:
    try:
        data=json.loads(get('https://api.modrinth.com/v2/search?'+urllib.parse.urlencode({'query':q,'limit':30})))
        for row in data['hits']:
            if row['project_type'] in ('mod','datapack'):
                projects.setdefault(row['slug'],{'search':q,'id':row['project_id']})
    except Exception as e:errors.append({'query':q,'error':str(e)})
def project(item):
    slug,row=item
    try:return slug,{**json.loads(get('https://api.modrinth.com/v2/project/'+row['id'])),'search':row['search']}
    except Exception as e:return slug,{'error':str(e)}
projects=dict(concurrent.futures.ThreadPoolExecutor(8).map(project,projects.items()))
dump(P/'projects.json',projects)
rows=[];urls=set()
for slug,d in projects.items():
    for g in d.get('gallery',[]):
        if g['url'] in urls:continue
        urls.add(g['url']);rows.append({'number':len(rows)+1,'slug':slug,'project':d['title'],'search':d['search'],'title':g.get('title'),'description':g.get('description'),'page':f"https://modrinth.com/{d['project_type']}/{slug}/gallery",'url':g['url']})
# Cap the cache, preserving the search order so traditional architecture comes first.
rows=rows[:420]
def fetch(row):
    p=P/f"candidate-{row['number']:03}.img";row['file']=p.name
    try:
        if not p.exists():p.write_bytes(get(row['url']))
        with Image.open(p) as im:row['dimensions']=list(im.size)
        row['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();row['prior_overlap']=row['sha256'] in prior
    except Exception as e:row['error']=str(e)
    return row
rows=list(concurrent.futures.ThreadPoolExecutor(12).map(fetch,rows))
dump(P/'candidates.json',rows);dump(P/'discovery-errors.json',errors)
usable=[r for r in rows if 'error' not in r and not r['prior_overlap']]
for start in range(0,len(usable),12):
    sheet=Image.new('RGB',(1800,1120),(24,27,30));dr=ImageDraw.Draw(sheet)
    for j,r in enumerate(usable[start:start+12]):
        x=j%4*450;y=j//4*373;im=Image.open(P/r['file']).convert('RGB');im.thumbnail((444,320));sheet.paste(im,(x,y))
        dr.text((x+3,y+323),f"{r['number']:03} {r['slug'][:42]}",fill='white')
        dr.text((x+3,y+341),str(r['title'])[:65],fill='white')
    sheet.save(P/f'sheet-{start//12+1:02}.jpg',quality=94)
print(json.dumps({'candidates':len(rows),'usable_new':len(usable),'prior_records':sum(r['count'] for r in sources),'errors':sum('error' in r for r in rows)}),flush=True)
