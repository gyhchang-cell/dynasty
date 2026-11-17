"""Original temple spatial inspection; never production or automatic credit."""
import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
from collections import Counter,defaultdict
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from whole_building_candidates import AIR,iso,color
from nbt_read import read
from reference_components import geometry_hash,role
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();raw=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
a=ld(P/'F02-source.json');d=ld(P/'F02-original.json');ar=bind(a['source_archive'])
meta=ld(R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json');inv=ld(meta['fixed_archive_inventory']['path'])
assert ar['sha256']==next(v['sha256']for v in inv['archives']if v['path']==ar['path'])
resources=[]
with ZipFile(ar['path'])as z:
 raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['nbt_sha256'];assert read(raw)==d
 for n in z.namelist():
  if n.endswith('.json')and (('fortified_temple'in n and '/worldgen/'in n)or n=='data/ati_structures/worldgen/template_pool/terrain_large.json'):
   raw=z.read(n);resources.append(dict(member=n,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),text=raw.decode(),json=json.loads(raw)))
put('original-context.json',dict(archive=ar,resources=resources))
pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR}
put('source-counts.json',dict(archive=ar,member=a['member'],sha256=a['nbt_sha256'],DataVersion=d['DataVersion'],size=d['size'],stored=len(bs),air=len(bs)-len(cells),nonair=len(cells),unknown=math.prod(d['size'])-len(bs),palette=len(pal),BE=sum('nbt'in b for b in bs.values()),entities=len(d.get('entities',[]))))
groups=defaultdict(list)
for p,b in bs.items():
 if 'nbt'in b:groups[json.dumps(b['nbt'],sort_keys=True,separators=(',',':'))].append(p)
put('all-BE-lossless-groups.json',[dict(nbt=json.loads(k),positions=v)for k,v in groups.items()])
functional=[dict(pos=list(p),state=pal[b['state']],**({'nbt':b['nbt']}if 'nbt'in b else {}))for p,b in bs.items()if any(t in pal[b['state']]['Name']for t in ['_door','ladder','scaffolding','chest','barrel','anvil','furnace','smoker','brewing_stand','jigsaw'])]
put('functional-original-states.json',functional)
layers=[dict(y=y,**dict(Counter('unknown'if(x,y,z)not in bs else'air'if pal[bs[(x,y,z)]['state']]['Name']in AIR else'nonair'for x in range(48)for z in range(48))))for y in range(48)]
put('layer-counts.json',layers)
for title,cut in [('whole',None),('cut-04',4),('cut-12',12),('cut-24',24),('cut-34',34),('cut-42',42)]:
 im=Image.new('RGB',(1520,680),'#edf0f2');sz=d['size']if cut is None else[48,cut+1,48]
 for i in range(2):im.paste(iso(cells,sz,i,'F02 '+title+' / source class cubes',cut),(760*i,0))
 im.save(P/('F02-'+title+'.png'))
for start in range(0,48,4):
 im=Image.new('RGB',(1400,1450),'#edf0f2');dr=ImageDraw.Draw(im);step=13
 for j,y in enumerate(range(start,start+4)):
  ox=40+700*(j%2);oy=50+715*(j//2);dr.text((ox,oy-28),f'F02 y{y}; WHITE air BLACK omitted; x right z down',fill='black')
  for x in range(48):
   for z in range(48):
    b=bs.get((x,y,z));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else '#ffffff'if n in AIR else color(n)
    dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#bdc3c8')
  for k in range(0,48,5):dr.text((ox+k*step,oy-15),str(k),fill='black');dr.text((ox-20,oy+k*step),str(k),fill='black')
 im.save(P/f'F02-layers-{start:02d}-{start+3:02d}.png')
put('protected-before.json',dict(files=[dict(previous290=a['current290'],before291=bind(a['current290']['path']),this_chat_wrote_file=False)for a in ld(P.parent/'research-20261104-smithy-290/protected-current.json')['files']]))
old=ld(R/'docs/architecture/research-20261101-task-map/scope-expansion-sources.json');mono=next(v for v in old['candidates']if v.get('source_member','').endswith('monastery_tower.nbt'))
put('excluded-monastery-history.json',dict(prior_binding=bind(R/'docs/architecture/research-20261101-task-map/scope-expansion-sources.json'),preserved_scalar_metadata={k:v for k,v in mono.items()if isinstance(v,(str,int,bool))},current_reading='仅读palette总数/材料/接头机器元数据，未画新图或新完整空间研究；发现旧实际阅读后排除，不计本批完整例。',credit=0))
put('active-checkpoint.json',dict(batch=291,status='IN_PROGRESS_FORTIFIED_TEMPLE_ORIGINAL_SPATIAL_READING_NOT_ACCEPTED',source=bind(P/'F02-original.json'),archive=ar,generated_png=18,images_actually_viewed=0,formal_credit_added=0,qualifying_reference_proposal=0,next='实际查看18PNG、原始关键材质/设施/实体与楼梯通路及地形池；补齐历史语义归属对比，再决定完成或HOLD。不算图数/组件为完整建筑。',no_session_written=True))
print(json.dumps(dict(counts=ld(P/'source-counts.json'),context=[dict(member=v['member'],bytes=v['bytes'])for v in resources],BE_unique_groups=len(groups),functional=len(functional)),ensure_ascii=False))
