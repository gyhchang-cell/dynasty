"""Read-only original snow hut analysis; own research outputs only."""
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
from reference_components import geometry_hash,role
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
meta=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';mm=ld(meta)
member='data/trek/structures/village/snowy/houses/snowy_small_house_4.nbt'
e=next(x for x in mm['entries']if x['member']==member);archive=bind(e['source_archive']);inv=ld(mm['fixed_archive_inventory']['path']);assert archive['sha256']==next(x['sha256']for x in inv['archives']if x['path']==archive['path'])
resources=[]
with ZipFile(archive['path'])as z:
 raw=z.read(member);assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256'];d=read(raw)
 for n in ['data/trek/worldgen/structure/village/snowy.json','data/trek/worldgen/template_pool/village/snowy/houses.json','data/trek/worldgen/template_pool/village/snowy/town_centers.json']:
  b=z.read(n);resources.append(dict(member=n,sha256=hashlib.sha256(b).hexdigest(),json=json.loads(b)))
put('source-original.json',d);put('source-binding.json',dict(archive=archive,member=member,raw_sha256=e['nbt_sha256'],original=bind(P/'source-original.json'),metadata=bind(meta)));put('source-context.json',dict(resources=resources))
pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR};size=d['size']
c=dict(size=size,DataVersion=d['DataVersion'],stored=len(bs),nonair=len(cells),air=len(bs)-len(cells),omitted=math.prod(size)-len(bs),palette=len(pal),BE=sum('nbt'in b for b in d['blocks']),entities=len(d.get('entities',[])),materials=dict(Counter(cells.values())));put('source-counts.json',c)
put('all-BE-original.json',[dict(pos=b['pos'],state=pal[b['state']],nbt=b['nbt'])for b in d['blocks']if'nbt'in b])
fp=dict(nbt_sha256=e['nbt_sha256'],role_sha256=geometry_hash({p:role(n)for p,n in cells.items()},size),occupancy_sha256=geometry_hash({p:1 for p in cells},size));cache=R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json';matches=[v for v in ld(cache)['entries']if any(v['fingerprints'].get(k)==h for k,h in fp.items())];put('historical-fingerprint-check.json',dict(binding=bind(cache),current=fp,matches=matches,boundary='Only nonair fingerprints; no-match is not semantic originality proof.'))
hits=[];scanned=[]
for pat in ['research-*/manual-review.json','research-*/sources.json','continuation-20261022/references/**/*.json']:
 for f in sorted((R/'docs/architecture').glob(pat)):
  if f.parent==P:continue
  t=f.read_text();scanned.append(bind(f))
  if member in t:hits.append(bind(f))
put('history-screen.json',dict(scanned=scanned,exact_member_hits=hits,limits='Exact source appearance only; legacy fingerprints separately checked. Same-theme spatial comparison still required.'))
for name,cut in [('whole',None),('cut-02',2),('cut-04',4)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,size,i,'298 original snow hut '+name,cut),(760*i,0))
 im.save(P/(name+'.png'))
im=Image.new('RGB',(1440,960),'#edf0f2');dr=ImageDraw.Draw(im);step=29
for y in range(8):
 ox=40+360*(y%4);oy=45+470*(y//4);dr.text((ox,oy-24),f'y{y} white air / black omitted',fill='black')
 for x in range(size[0]):
  for z in range(size[2]):
   b=bs.get((x,y,z));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#aab1b7')
 for x in range(size[0]):dr.text((ox+x*step,oy-12),str(x),fill='black')
 for z in range(size[2]):dr.text((ox-20,oy+z*step),str(z),fill='black')
im.save(P/'layers.png')
im=Image.new('RGB',(1200,460),'#edf0f2');dr=ImageDraw.Draw(im);step=36
for i,(axis,fixed)in enumerate([('x',3),('z',3)]):
 ox=45+600*i;oy=45;extent=size[2]if axis=='x'else size[0];dr.text((ox,20),f'{axis}={fixed}; original section',fill='black')
 for u in range(extent):
  for y in range(size[1]):
   q=(fixed,y,u)if axis=='x'else(u,y,fixed);b=bs.get(q);n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+u*step,oy+(size[1]-1-y)*step,ox+(u+1)*step,oy+(size[1]-y)*step),fill=c,outline='#aab1b7')
 for u in range(extent):dr.text((ox+u*step,oy+size[1]*step+5),str(u),fill='black')
 for y in range(size[1]):dr.text((ox-22,oy+(size[1]-1-y)*step),str(y),fill='black')
im.save(P/'sections.png')
# All declared cells in compact palette-index plans, '_' means omitted unknown.
plans=[]
for y in range(size[1]):plans.append(dict(y=y,rows_z=[' '.join(str(bs[(x,y,z)]['state'])if(x,y,z)in bs else'_' for x in range(size[0]))for z in range(size[2])]))
put('all-layers-state-index.json',dict(legend='x increases within each row; z increases by row; palette index, _ omitted',layers=plans))
put('active-checkpoint.json',dict(batch=298,status='SOURCE_RENDERED_NOT_YET_ACTUALLY_VIEWED',images_generated=5,images_actually_viewed=0,new_whole_studies=0,formal_credit_added=0,tasks_deleted=0,next='Read all images/palette/BE/layers/context; compare252F03/249 before semantic decision. Prior297 correction preserved.'))
print(json.dumps(dict(counts=ld(P/'source-counts.json'),matches=matches,exact_member_history_hits=hits),ensure_ascii=False))
