"""Frozen-local laboratory source inspection; no native placement or credit."""
import json,hashlib,sys,importlib.util
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash,role
from whole_building_candidates import AIR
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
meta=ld(R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json');sel=[a for a in meta['entries'] if 'mutantmore/structures/derelict_laboratory' in a['member']]
assert len(sel)==2
jar=sel[0]['source_archive'];ar=bind(jar);inv=ld(meta['fixed_archive_inventory']['path']);assert ar['sha256']==next(a['sha256']for a in inv['archives'] if a['path']==jar)
cache={}
for e in ld(R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json')['entries']:cache[e['source']['archive'],e['source']['member']]=e['fingerprints']
for i in range(153,288):
 for p in (P.parent/f'research-20261104-smithy-{i:03d}').glob('*history-screen.json'):
  for a in ld(p).get('rows',[]):
   if 'source_archive'in a and 'current_source_fingerprints'in a:cache[a['source_archive'],a['member']]=a['current_source_fingerprints']
rows=[]
with ZipFile(jar) as z:
 for i,a in enumerate(sel,1):
  raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['nbt_sha256'];d=read(raw);put(f'F{i:02d}-original.json',d);pal=d['palette'];cells={tuple(b['pos']):pal[b['state']]['Name']for b in d['blocks']if pal[b['state']]['Name']not in AIR};co=Counter(cells.values());fp=dict(nbt_sha256=a['nbt_sha256'],role_sha256=geometry_hash({p:role(n)for p,n in cells.items()},d['size']),occupancy_sha256=geometry_hash({p:1 for p in cells},d['size']));matches=[]
  for (ar0,n),f in cache.items():
   eq=[k for k,v in fp.items()if v==f.get(k)]
   if eq:matches.append(dict(source_archive=ar0,member=n,keys=eq))
  rows.append(dict(id=f'F{i:02d}',**a,archive_binding=ar,current_fingerprints=fp,historical_cached_matches=matches,DataVersion=d.get('DataVersion'),stored=len(d['blocks']),nonair=len(cells),air=len(d['blocks'])-len(cells),unknown=d['size'][0]*d['size'][1]*d['size'][2]-len(d['blocks']),materials=dict(co),block_entities=[b for b in d['blocks']if 'nbt'in b],entities=d.get('entities',[])))
  print(f'F{i:02d}',a['member'],'size',d['size'],'palette',len(pal),'nonair',len(cells),'air',len(d['blocks'])-len(cells),'matches',matches)
 ctx=[]
 for n in z.namelist():
  if 'derelict_laboratory' in n and n.endswith('.json') and ('/worldgen/' in n or '/tags/worldgen/biome/' in n):
   raw=z.read(n);ctx.append(dict(member=n,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),text=raw.decode(),json=json.loads(raw)))
 put('direct-context.json',dict(archive=ar,resources=ctx,loot_not_fully_read=True))
put('sources.json',dict(candidates=rows,historical_cached_pairs=len(cache),old198_200_machine_only_not_whole=True,semantic_credit=0,source_archive_verified=True))
protected=[]
for a in ld(P.parent/'research-20261104-smithy-287/protected-inputs-current.json')['files']:
 old=a['current287'];new=bind(old['path']);protected.append(dict(previous287=old,before288=new,unchanged_since287=old==new,this_chat_wrote_file=False))
put('protected-before.json',dict(files=protected,cod5_missing_not_invented=True))
