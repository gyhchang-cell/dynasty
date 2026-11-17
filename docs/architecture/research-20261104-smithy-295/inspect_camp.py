"""Read original camp4, research evidence only."""
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
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
meta=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json'
e=next(x for x in json.loads(meta.read_text())['entries']if x['member']=='data/trek/structures/overworld/medium/camp_4.nbt')
archive=bind(e['source_archive']);assert archive['sha256']=='fea95f69d7d023a8d990c043ee63bc07ea0a85cde1a558b369ef4884d3ac5012'
resources=[]
with ZipFile(archive['path'])as z:
 raw=z.read(e['member']);assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256'];d=read(raw)
 for n in ['data/trek/worldgen/structure/overworld/medium/camp_4.json','data/trek/worldgen/template_pool/overworld/medium/camp_4.json','data/trek/worldgen/template_pool/mobs/villagers/taiga/unemployed.json']:
  if n not in z.namelist():continue
  b=z.read(n);resources.append(dict(member=n,sha256=hashlib.sha256(b).hexdigest(),text=b.decode(),json=json.loads(b)))
put('source-original.json',d);put('source-binding.json',dict(archive=archive,member=e['member'],raw_sha256=e['nbt_sha256'],original=bind(P/'source-original.json')));put('source-context.json',dict(resources=resources))
pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR};size=d['size']
counts=dict(size=size,stored=len(bs),nonair=len(cells),air=len(bs)-len(cells),omitted=math.prod(size)-len(bs),palette=len(pal),BE=sum('nbt'in b for b in d['blocks']),entities=len(d.get('entities',[])),materials=dict(Counter(cells.values())))
put('source-counts.json',counts);be=[dict(pos=b['pos'],state=pal[b['state']],nbt=b['nbt'])for b in d['blocks']if'nbt'in b];put('all-BE-original.json',be)
hits=[];files=[]
for pat in ['research-*/manual-review.json','continuation-20261022/references/**/*.json']:
 for f in sorted((R/'docs/architecture').glob(pat)):
  if f.parent==P:continue
  text=f.read_text()
  files.append(bind(f))
  if any(t in text for t in ('camp_4.nbt','camp_4"','camp4')):hits.append(bind(f))
put('history-screen.json',dict(files=files,hits=hits,boundary='Exact family/name screen includes legacy candidate-ID keyed reviews but not proof against semantic alias.'))
for name,cut in [('whole',None),('cut-05',5)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,size,i,'295 source '+name,cut),(760*i,0))
 im.save(P/(name+'.png'))
for start in (0,8):
 im=Image.new('RGB',(1600,800),'#edf0f2');dr=ImageDraw.Draw(im);step=17
 for y in range(start,min(start+8,size[1])):
  i=y-start;ox=45+395*(i%4);oy=45+395*(i//4);dr.text((ox,oy-23),f'y{y}; whiteAIR blackOMITTED',fill='black')
  for x in range(size[0]):
   for z in range(size[2]):
    b=bs.get((x,y,z));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
    dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#aab1b7')
  for x in (0,5,10,15,18):dr.text((ox+x*step,oy-12),str(x),fill='black')
  for z in (0,4,8,12,16):dr.text((ox-20,oy+z*step),str(z),fill='black')
 im.save(P/f'layers-{start:02}.png')
im=Image.new('RGB',(1140,620),'#edf0f2');dr=ImageDraw.Draw(im);step=25
for i,(axis,fixed)in enumerate([('x',9),('z',8)]):
 ox=45+570*i;oy=45;extent=size[2]if axis=='x'else size[0];dr.text((ox,20),f'{axis}={fixed}; source sections',fill='black')
 for u in range(extent):
  for y in range(size[1]):
   q=(fixed,y,u)if axis=='x'else(u,y,fixed);b=bs.get(q);n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+u*step,oy+(size[1]-1-y)*step,ox+(u+1)*step,oy+(size[1]-y)*step),fill=c,outline='#aab1b7')
 for u in range(0,extent,2):dr.text((ox+u*step,oy+size[1]*step+5),str(u),fill='black')
 for y in range(size[1]):dr.text((ox-20,oy+(size[1]-1-y)*step),str(y),fill='black')
im.save(P/'sections.png')
put('active-checkpoint.json',dict(batch=295,status='SOURCE_RENDERED_PENDING_ACTUAL_READING',images_generated=5,images_actually_viewed=0,formal_credit_added=0,tasks_deleted=0,next='Read five images/all16layers/2sections,61palette/fullBE/context and assess whole-camp relevance.'))
print(json.dumps(dict(counts=counts,history_hits=hits,palette=pal,BE=be,resources=resources),ensure_ascii=False))
