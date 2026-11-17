"""Read a frozen authored shrine as one source building, not per-block credit."""
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
from reference_components import role,geometry_hash
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
meta_path=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';meta=ld(meta_path)
a=next(x for x in meta['entries']if x['member'].endswith('/holy_shrine.nbt'));archive=bind(a['source_archive'])
inv=ld(meta['fixed_archive_inventory']['path']);assert archive['sha256']==next(x['sha256']for x in inv['archives']if x['path']==archive['path'])
context=[]
with ZipFile(archive['path'])as z:
 raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['nbt_sha256'];d=read(raw)
 for n in z.namelist():
  if 'holy_shrine'in n and n.endswith('.json'):
   b=z.read(n);context.append(dict(member=n,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),text=b.decode(),json=json.loads(b)))
put('source-original.json',d);put('source-context.json',dict(archive=archive,resources=context))
pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR}
counts=dict(size=d['size'],DataVersion=d['DataVersion'],stored=len(bs),nonair=len(cells),explicit_air=len(bs)-len(cells),omitted=math.prod(d['size'])-len(bs),palette=len(pal),materials=dict(Counter(cells.values())),BE=sum('nbt'in b for b in bs.values()),entities=len(d.get('entities',[])))
put('source-counts.json',counts);put('source-binding.json',dict(archive=archive,member=a['member'],raw_sha256=a['nbt_sha256'],raw_bytes=len(raw),metadata_binding=bind(meta_path),original_json=bind(P/'source-original.json')))
put('original-special-states.json',[dict(pos=b['pos'],state=pal[b['state']],**({'nbt':b['nbt']}if'nbt'in b else{}))for b in d['blocks']if'nbt'in b or any(k in pal[b['state']]['Name']for k in ['stair','slab','door','ladder','jigsaw'])])
fp=dict(nbt_sha256=a['nbt_sha256'],role_sha256=geometry_hash({p:role(n)for p,n in cells.items()},d['size']),occupancy_sha256=geometry_hash({p:1 for p in cells},d['size']))
cache=R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json';matches=[e for e in ld(cache)['entries']if any(e['fingerprints'].get(k)==v for k,v in fp.items())]
put('historical-fingerprint-check.json',dict(binding=bind(cache),current=fp,matches=matches,method='Historical NONAIR material/rotation invariant convention; machine candidate identity is not semantic credit.'))
paths=[];hits=[]
def walk(v,loc):
 if isinstance(v,dict):
  if any(isinstance(t,str)and t.endswith('/holy_shrine.nbt')for t in v.values()):hits.append(dict(location=loc,keys=list(v),scalars={k:t for k,t in v.items()if isinstance(t,(str,int,bool))}))
  for k,t in v.items():walk(t,loc+'/'+str(k))
 elif isinstance(v,list):
  for i,t in enumerate(v):walk(t,loc+'/'+str(i))
for pat in ['research-*/manual-review.json','research-*/reference-proposals.json','research-*/*scope*register.json','continuation-20261022/references/*/candidates.json','continuation-20261022/references/full-buildings.json']:
 for f in sorted((R/'docs/architecture').glob(pat)):
  if f.parent==P:continue
  paths.append(bind(f));walk(ld(f),str(f))
put('history-own-record-search.json',dict(paths=paths,hits=hits,boundary='Bounded own source fields, not all chat history or semantic alias proof.'))
registry=R/'docs/architecture/continuation-20261022/references/full-buildings.json';old=ld(registry)
put('excluded-already-credited-chapels.json',dict(binding=bind(registry),entries=[e for e in old['entries']if e['id']in ['COD4-R002-B006','COD4-R002-B007']],current_action='Read prior full seven observations and native limits, do not reopen pictures/recount either chapel.',credit_added=0))
sx,sy,sz=d['size']
for label,cut in [('whole',None),('cut-04',4)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,d['size']if cut is None else[sx,cut+1,sz],i,'293 holy_shrine '+label+' / source classes',cut),(760*i,0))
 im.save(P/(label+'.png'))
for start in range(0,sy,4):
 im=Image.new('RGB',(1120,1140),'#edf0f2');dr=ImageDraw.Draw(im);step=23
 for j,y in enumerate(range(start,min(start+4,sy))):
  ox=45+560*(j%2);oy=55+570*(j//2);dr.text((ox,oy-25),f'293 y{y}; WHITE air BLACK omitted',fill='black')
  for x in range(sx):
   for z in range(sz):
    b=bs.get((x,y,z));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
    dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#bdc3c8')
  for x in range(0,sx,3):dr.text((ox+x*step,oy-14),str(x),fill='black')
  for z in range(0,sz,3):dr.text((ox-22,oy+z*step),str(z),fill='black')
 im.save(P/f'layers-{start:02d}-{min(start+3,sy-1):02d}.png')
im=Image.new('RGB',(1120,650),'#edf0f2');dr=ImageDraw.Draw(im);step=24
for i,(axis,fixed)in enumerate([('x',9),('z',10)]):
 ox=40+560*i;oy=55;extent=sz if axis=='x'else sx;dr.text((ox,20),f'293 {axis}={fixed}; y up',fill='black')
 for u in range(extent):
  for y in range(sy):
   q=(fixed,y,u)if axis=='x'else(u,y,fixed);b=bs.get(q);n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+u*step,oy+(sy-1-y)*step,ox+(u+1)*step,oy+(sy-y)*step),fill=c,outline='#bdc3c8')
 for u in range(0,extent,3):dr.text((ox+u*step,oy+sy*step+5),str(u),fill='black')
 for y in range(0,sy,3):dr.text((ox-22,oy+(sy-1-y)*step),str(y),fill='black')
im.save(P/'sections.png')
put('protected-before.json',dict(files=[dict(before293=bind(x['after']['path']))for x in ld(P.parent/'research-20261104-smithy-292/protected-current.json')['files']]))
put('active-checkpoint.json',dict(batch=293,status='IN_PROGRESS_SHRINE_ORIGINAL_SPATIAL_READING',source=archive,generated_png=8,images_actually_viewed=0,formal_credit_added=0,next='实际查看8图/全20层与2剖面；读全部10palette与原设施，判断完整用途/入口/地形后封存，不把候选数当信用。'))
print(json.dumps(dict(counts=counts,palette=pal,history_hits=hits,cache_matches=matches,generated_png=8),ensure_ascii=False))
