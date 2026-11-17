"""Original plains house research. No production writes."""
import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,iso,color
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
meta=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';member='data/simply_houses/structures/plains_house/plains_house.nbt'
e=next(x for x in ld(meta)['entries']if x['member']==member);archive=bind(e['source_archive']);assert archive['sha256']=='19600e85f62677245ca77428e2b16f0501ebd709c13bda24072675d3753a38c2'
resources=[]
with ZipFile(archive['path'])as z:
 raw=z.read(member);assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256'];d=read(raw)
 for n in ['data/simply_houses/worldgen/structure/plains_house.json','data/simply_houses/worldgen/template_pool/plains_house/plains_house_start.json','data/simply_houses/worldgen/template_pool/plains_house/plains_house_main.json','data/simply_houses/tags/worldgen/biome/has_structure/plains_house_biomes.json']:
  b=z.read(n);resources.append(dict(member=n,sha256=hashlib.sha256(b).hexdigest(),text=b.decode(),json=json.loads(b)))
 n='data/simply_houses/structures/plains_house/plains_house_bridge.nbt';b=z.read(n);v=read(b);put('bridge-original.json',v);bridge=dict(member=n,raw_sha256=hashlib.sha256(b).hexdigest(),original=bind(P/'bridge-original.json'),reading_boundary='Source palette/socket/header inspected only, not separate whole building credit.')
put('source-original.json',d);put('source-binding.json',dict(archive=archive,member=member,raw_sha256=e['nbt_sha256'],original=bind(P/'source-original.json'),bridge=bridge));put('source-context.json',dict(resources=resources))
pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR};size=d['size']
c=dict(size=size,DataVersion=d['DataVersion'],stored=len(bs),nonair=len(cells),air=len(bs)-len(cells),omitted=math.prod(size)-len(bs),palette=len(pal),BE=sum('nbt'in b for b in d['blocks']),entities=len(d.get('entities',[])),materials=dict(Counter(cells.values())));put('source-counts.json',c)
be=[dict(pos=b['pos'],state=pal[b['state']],nbt=b['nbt'])for b in d['blocks']if'nbt'in b];put('all-BE-original.json',be)
unique={}
for row in be:
 key=json.dumps(row['nbt'],sort_keys=True)
 if key not in unique:unique[key]=dict(nbt=row['nbt'],positions=[])
 unique[key]['positions'].append(dict(pos=row['pos'],state=row['state']))
put('grouped-full-BE.json',list(unique.values()));put('source-entities.json',d.get('entities',[]))
old=R/'docs/architecture/research-20261104-smithy-272/semantic-screen-decision.json';put('prior-partial-boundary.json',dict(binding=bind(old),decision=ld(old)['F03'],task_filter=ld(old)['original_task_filter'],old_checkpoint=ld(old.parent/'active-checkpoint.json')))
hits=[];scanned=[]
for pat in ['research-*/manual-review.json','continuation-20261022/references/**/*.json']:
 for f in sorted((R/'docs/architecture').glob(pat)):
  if f.parent==P:continue
  text=f.read_text();scanned.append(bind(f))
  if member in text or 'plains_house.nbt'in text:hits.append(bind(f))
put('history-screen.json',dict(scanned=scanned,hits=hits,boundary='Full member/basename includes old ID-keyed review and visual ledgers; not global semantic novelty proof. Prior272 partial context is preserved separately.'))
for name,cut in [('whole',None),('cut-08',8),('cut-14',14)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,size,i,'296 plains house '+name,cut),(760*i,0))
 im.save(P/(name+'.png'))
for start in (0,7,14,21):
 im=Image.new('RGB',(1560,1100),'#edf0f2');dr=ImageDraw.Draw(im);step=15
 for y in range(start,min(start+7,size[1])):
  i=y-start;ox=45+385*(i%4);oy=45+540*(i//4);dr.text((ox,oy-24),f'y{y}; WHITEair BLACKomitted',fill='black')
  for x in range(size[0]):
   for z in range(size[2]):
    b=bs.get((x,y,z));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
    dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#aab1b7')
  for x in (0,4,8,12,15):dr.text((ox+x*step,oy-12),str(x),fill='black')
  for z in (0,5,10,15,20,25,27):dr.text((ox-22,oy+z*step),str(z),fill='black')
 im.save(P/f'layers-{start:02}.png')
im=Image.new('RGB',(1300,760),'#edf0f2');dr=ImageDraw.Draw(im);step=22
for i,(axis,fixed)in enumerate([('x',8),('z',14)]):
 ox=45+700*i;oy=45;extent=size[2]if axis=='x'else size[0];dr.text((ox,20),f'{axis}={fixed}; source section',fill='black')
 for u in range(extent):
  for y in range(size[1]):
   q=(fixed,y,u)if axis=='x'else(u,y,fixed);b=bs.get(q);n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+u*step,oy+(size[1]-1-y)*step,ox+(u+1)*step,oy+(size[1]-y)*step),fill=c,outline='#aab1b7')
 for u in range(0,extent,2):dr.text((ox+u*step,oy+size[1]*step+5),str(u),fill='black')
 for y in range(size[1]):dr.text((ox-22,oy+(size[1]-1-y)*step),str(y),fill='black')
im.save(P/'sections.png')
put('active-checkpoint.json',dict(batch=296,status='ORIGINAL_SOURCE_RENDERED_NOT_YET_ACTUALLY_VIEWED',images_generated=8,images_actually_viewed=0,formal_credit_added=0,tasks_deleted=0,next='View8images/full25plans/2sections, read palette/BE/entities/context, source route and old whole comparison; no production.'))
print(json.dumps(dict(counts=ld(P/'source-counts.json'),history_hits=hits,unique_BE_payloads=len(unique),bridge_size=v['size'],source_binding=ld(P/'source-binding.json')),ensure_ascii=False))
