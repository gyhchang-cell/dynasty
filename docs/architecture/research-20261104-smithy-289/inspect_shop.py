"""Local original shop reading only, with distinct-air/omission diagrams."""
import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from whole_building_candidates import AIR,iso,color
from reference_components import geometry_hash,role
from nbt_read import read
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
a=ld(P/'F02-source.json');d=ld(P/'F02-original.json');ar=bind(a['source_archive'])
meta=ld(R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json');inv=ld(meta['fixed_archive_inventory']['path'])
assert ar['sha256']==next(v['sha256']for v in inv['archives']if v['path']==ar['path'])
with ZipFile(ar['path'])as z:
 raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['nbt_sha256'];assert read(raw)==d
 resources=[]
 for name in z.namelist():
  if name.endswith('.json')and (('sparse_jungle_polynesian'in name and ('/worldgen/'in name or '/tags/worldgen/'in name))or name=='data/kaisyn/worldgen/template_pool/village/jungle_tribal/villagers.json'):
   raw=z.read(name);resources.append(dict(member=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),text=raw.decode(),json=json.loads(raw)))
 put('original-context.json',dict(archive=ar,resources=resources))
 print('CONTEXT',[(v['member'],v['bytes'])for v in resources])
pal=d['palette'];block={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name']for p,b in block.items()if pal[b['state']]['Name']not in AIR}
fp=dict(nbt_sha256=a['nbt_sha256'],role_sha256=geometry_hash({p:role(n)for p,n in cells.items()},d['size']),occupancy_sha256=geometry_hash({p:1 for p in cells},d['size']))
cache={}
for e in ld(R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json')['entries']:cache[e['source']['archive'],e['source']['member']]=e['fingerprints']
for i in range(153,289):
 for f in (P.parent/f'research-20261104-smithy-{i:03d}').glob('*history-screen.json'):
  doc=ld(f)
  for e in doc.get('rows',[]):
   if 'source_archive'in e and 'current_source_fingerprints'in e:cache[e['source_archive'],e['member']]=e['current_source_fingerprints']
matches=[dict(archive=k[0],member=k[1],equal=[j for j,v in fp.items()if v==f.get(j)])for k,f in cache.items()if any(v==f.get(j)for j,v in fp.items())]
put('shop-history-screen.json',dict(rows=[dict(source_archive=a['source_archive'],member=a['member'],current_source_fingerprints=fp,historical_cached_matches=matches)],pairs=len(cache),archive=ar,credit=0))
matrix=[dict(y=y,rows=[[block.get((x,y,z),{}).get('state',-1)for x in range(8)]for z in range(8)])for y in range(8)]
put('F02-all-512-state-matrix.json',matrix)
for v in matrix:print('LAYER',json.dumps(v,separators=(',',':')))
special=[dict(pos=list(p),state=pal[b['state']],**({'nbt':b['nbt']}if 'nbt'in b else {}))for p,b in block.items()if any(t in pal[b['state']]['Name']for t in ['door','gate','stairs','slab','loom','smoker','chest','bed','jigsaw','sign'])]
put('F02-functional-states.json',special)
put('F02-source-counts.json',dict(archive=ar,nbt_sha256=a['nbt_sha256'],size=d['size'],DataVersion=d['DataVersion'],palette=len(pal),stored=len(block),air=len(block)-len(cells),nonair=len(cells),unknown=math.prod(d['size'])-len(block),materials=dict(Counter(cells.values())),entities=d.get('entities',[]),block_entities=[b for b in d['blocks']if 'nbt'in b]))
for name,cut in [('whole',None),('lower',2),('upper',4)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 display_size=d['size'] if cut is None else [8,cut+1,8]
 for i in range(2):im.paste(iso(cells,display_size,i,f'F02 {name} / original states / rotation {i*90}',cut),(760*i,0))
 im.save(P/f'F02-{name}.png')
for start in (0,4):
 im=Image.new('RGB',(1200,1080),'#edf0f2');dr=ImageDraw.Draw(im)
 for j,y in enumerate(range(start,start+4)):
  ox=50+600*(j%2);oy=45+530*(j//2);step=55;dr.text((ox,oy-25),f'F02 y{y}: x right, z down; white saved air',fill='black')
  for z0 in range(8):
   for x in range(8):
    b=block.get((x,y,z0));n=pal[b['state']]['Name']if b else None;c='#151a24'if n is None else '#ffffff'if n in AIR else color(n)
    dr.rectangle((ox+x*step,oy+z0*step,ox+(x+1)*step,oy+(z0+1)*step),fill=c,outline='#9fa6ad');dr.text((ox+x*step+4,oy+z0*step+4),str(b['state'])if b else '-',fill='black')
 im.save(P/f'F02-layers-{start:02d}-{start+3:02d}.png')
before=ld(P.parent/'research-20261104-smithy-288/protected-after.json')
put('protected-before.json',dict(files=[dict(previous288=v['after'],before289=bind(v['after']['path']),this_chat_wrote_file=False)for v in before['files']]))
print('SOURCE',json.dumps(ld(P/'F02-source-counts.json'),ensure_ascii=False))
print('MATCHES',matches)
