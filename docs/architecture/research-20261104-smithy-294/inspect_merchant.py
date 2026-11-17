"""Complete old215's partial trader-camp source reading; no production writes."""
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
a=next(x for x in meta['entries']if x['member'].endswith('/wandering_trader_oak.nbt'));archive=bind(a['source_archive'])
inv=ld(meta['fixed_archive_inventory']['path']);assert archive['sha256']==next(x['sha256']for x in inv['archives']if x['path']==archive['path'])
variants=[];context=[]
with ZipFile(archive['path'])as z:
 raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['nbt_sha256'];d=read(raw)
 for member in ['data/trek/worldgen/structure/overworld/medium/wandering_trader_oak.json','data/trek/worldgen/template_pool/overworld/medium/wandering_trader_oak.json']:
  b=z.read(member);context.append(dict(member=member,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),text=b.decode(),json=json.loads(b)))
 for key in ['wandering_trader_spruce','wandering_trader_dark_oak']:
  member='data/trek/structures/overworld/medium/'+key+'.nbt';b=z.read(member);v=read(b);put(key+'-original.json',v)
  variants.append(dict(member=member,raw_sha256=hashlib.sha256(b).hexdigest(),size=v['size'],source_json=bind(P/(key+'-original.json')),reading_boundary='Only machine shape/role comparison; not full spatial study or extra design credit.'))
put('source-original.json',d);put('source-context.json',dict(archive=archive,resources=context));put('variant-sources.json',variants)
pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR}
put('source-binding.json',dict(archive=archive,member=a['member'],raw_sha256=a['nbt_sha256'],raw_bytes=len(raw),original=bind(P/'source-original.json'),metadata=bind(meta_path)))
put('source-counts.json',dict(size=d['size'],DataVersion=d['DataVersion'],stored=len(bs),nonair=len(cells),air=len(bs)-len(cells),omitted=math.prod(d['size'])-len(bs),palette=len(pal),BE=sum('nbt'in b for b in d['blocks']),entities=len(d.get('entities',[])),materials=dict(Counter(cells.values()))))
put('all-BE-original.json',[dict(pos=b['pos'],state=pal[b['state']],nbt=b['nbt'])for b in d['blocks']if'nbt'in b])
put('all-source-state-positions.json',[dict(pos=b['pos'],state=pal[b['state']])for b in d['blocks']])
fp=dict(nbt_sha256=a['nbt_sha256'],role_sha256=geometry_hash({p:role(n)for p,n in cells.items()},d['size']),occupancy_sha256=geometry_hash({p:1 for p in cells},d['size']))
cache=R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json';matches=[v for v in ld(cache)['entries']if any(v['fingerprints'].get(k)==h for k,h in fp.items())]
put('historical-fingerprint-check.json',dict(binding=bind(cache),current=fp,matches=matches,method='Historical NONAIR only; not novelty proof.'))
old=R/'docs/architecture/research-20261104-smithy-215/manual-review.json';oldcase=[c for c in ld(old)['cases']if c['id']in ['F03','F04']]
put('prior-partial-reading.json',dict(binding=bind(old),cases=oldcase,actual_old_limits=ld(old)['limits'],current_boundary='Old215 BE/material partial prefilter explicitly had PNG0/full_palette false/full_layers false/complete_spatial false. Completing that bounded source reading, not ignoring/recounting it. Spruce same family never extra credit.'))
paths=[];hits=[]
def walk(v,loc):
 if isinstance(v,dict):
  if any(isinstance(t,str)and 'wandering_trader_'in t and t.endswith('.nbt')for t in v.values()):hits.append(dict(location=loc,keys=list(v),scalars={k:t for k,t in v.items()if isinstance(t,(str,int,bool))}))
  for k,t in v.items():walk(t,loc+'/'+str(k))
 elif isinstance(v,list):
  for i,t in enumerate(v):walk(t,loc+'/'+str(i))
for pat in ['research-*/manual-review.json','research-*/scope-expansion-sources.json','research-*/reference-proposals.json','research-*/*scope*register.json','continuation-20261022/references/**/*.json']:
 for f in sorted((R/'docs/architecture').glob(pat)):
  if f.parent==P:continue
  paths.append(bind(f));walk(ld(f),str(f))
put('history-source-and-old-format-screen.json',dict(paths=paths,hits=hits,old_candidate_ID_review_note='No target family member appears in legacy candidates, so no hidden candidate-ID key attribution found there; old review-batch/visual ledgers are included in paths. New215 partial own evidence retained in full.',boundary='Member/name screening is not proof against all semantic aliases.'))
other=R/'docs/architecture/research-20261104-smithy-273/manual-review.json';otherd=ld(other)
put('prior-whole-comparison.json',dict(binding=bind(other),whole_seven_dimensions=otherd['seven_dimensions'],whole_limits=otherd['limits'],old_status=otherd['status'],old_credit=otherd['formal_credit_added'],actual_current_reading='Full own seven dimensions and nine limits read; no old images reopened or credited again.'))
for label,cut in [('whole',None),('cut-02',2)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,d['size']if cut is None else[13,cut+1,10],i,'294 merchant '+label+' / source classes',cut),(760*i,0))
 im.save(P/(label+'.png'))
im=Image.new('RGB',(1520,1080),'#edf0f2');dr=ImageDraw.Draw(im);step=32
for y in range(6):
 ox=50+500*(y%3);oy=60+530*(y//3);dr.text((ox,oy-25),f'294 y{y}; WHITE air / BLACK omitted',fill='black')
 for x in range(13):
  for z in range(10):
   b=bs.get((x,y,z));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#bdc3c8')
 for x in range(13):dr.text((ox+x*step,oy-14),str(x),fill='black')
 for z in range(10):dr.text((ox-20,oy+z*step),str(z),fill='black')
im.save(P/'all-six-layers.png')
im=Image.new('RGB',(1140,500),'#edf0f2');dr=ImageDraw.Draw(im);step=36
for i,(axis,fixed)in enumerate([('x',6),('z',5)]):
 ox=45+570*i;oy=65;extent=10 if axis=='x' else 13;dr.text((ox,25),f'294 {axis}={fixed}; y up',fill='black')
 for u in range(extent):
  for y in range(6):
   q=(fixed,y,u)if axis=='x'else(u,y,fixed);b=bs.get(q);n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+u*step,oy+(5-y)*step,ox+(u+1)*step,oy+(6-y)*step),fill=c,outline='#bdc3c8')
 for u in range(extent):dr.text((ox+u*step,oy+6*step+5),str(u),fill='black')
 for y in range(6):dr.text((ox-22,oy+(5-y)*step),str(y),fill='black')
im.save(P/'sections.png')
put('protected-before.json',dict(files=[dict(before294=bind(x['after']['path']))for x in ld(P.parent/'research-20261104-smithy-293/protected-current.json')['files']]))
put('active-checkpoint.json',dict(batch=294,status='IN_PROGRESS_PRIOR215_PARTIAL_TRADER_CAMP_COMPLETION',images_generated=4,images_actually_viewed=0,new_distinct_building_credit=0,formal_credit_added=0,next='看4PNG全6层和2整剖，读全部palette/BE/原入口，比较oak/spruce/darkoak同族；old273七维补读。不制造新建筑。'))
print(json.dumps(dict(counts=ld(P/'source-counts.json'),palette=pal,BE=ld(P/'all-BE-original.json'),history_hits=hits,source_cache_matches=matches),ensure_ascii=False))
