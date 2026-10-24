from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures,io
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'build/bestiary-v41/research';D.mkdir(parents=True,exist_ok=True)
def get(url):
 return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Dynasty-art-reference-research/1.0'}),timeout=35).read()
def project(slug):
 try:
  p=D/(slug+'.json')
  if not p.exists():p.write_bytes(get('https://api.modrinth.com/v2/project/'+slug))
  d=json.loads(p.read_text());return [{'mod':slug,'title':x.get('title'),'description':x.get('description'),'url':x['url'],'source':'https://modrinth.com/mod/'+slug+'/gallery'} for x in d.get('gallery',[])]
 except Exception as e:return []
slugs=['alexs-mobs','the-twilight-forest','goety','ice-and-fire-dragons','naturalist','better-animals-plus','exotic-birds','untamed-wilds','critters-and-companions','the-aether','alexs-caves','environmental','ecologics','critters-n-crawlers','duckling','species','born-in-chaos','mythic-mounts','wyrmroost','mythic-mobs','faunify','wilder-wild','friends-and-foes','creatures-and-beasts','endless-biomes','iter-rpg','earthmobs','upgrade-aquatic','ribbits','chirpy-wildlife']
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for results in ex.map(project,slugs):rows+=results
seen=set();rows=[r for r in rows if r['url'] not in seen and not seen.add(r['url'])]
def fetch(r):
 try:
  name='image-'+hashlib.sha256(r['url'].encode()).hexdigest()[:18]+'.img';p=D/name
  if not p.exists():p.write_bytes(get(r['url']))
  im=Image.open(p).convert('RGB');r.update(file=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),dimensions=list(im.size));return r
 except Exception:return None
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:rows=[r for r in ex.map(fetch,rows) if r]
for i,r in enumerate(rows):r['index']=i+1
(D/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
for start in range(0,len(rows),12):
 sheet=Image.new('RGB',(1800,1250),'#ecece4');dr=ImageDraw.Draw(sheet)
 for j,r in enumerate(rows[start:start+12]):
  im=Image.open(D/r['file']).convert('RGB');im.thumbnail((590,264));x=j%3*600;y=j//3*310;sheet.paste(im,(x+(590-im.width)//2,y));dr.text((x+8,y+267),str(r['index'])+' '+r['mod']+' '+str(r.get('title') or '')[:45],fill='black')
 sheet.save(D/f'sheet-{start//12+1:02}.jpg',quality=90)
print('Gallery images:',len(rows),'sheets:',(len(rows)+11)//12,flush=True)
