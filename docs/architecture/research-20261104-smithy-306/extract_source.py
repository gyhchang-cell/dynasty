"""Read-only original East Asian dwelling analysis; own research outputs only."""
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
member='data/trek/structures/village/cherry/houses/cherry_small_house_1.nbt'
e=next(x for x in mm['entries']if x['member']==member);archive=bind(e['source_archive']);inv=ld(mm['fixed_archive_inventory']['path']);assert archive['sha256']==next(x['sha256']for x in inv['archives']if x['path']==archive['path'])
resources=[]
with ZipFile(archive['path'])as z:
 raw=z.read(member);assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256'];d=read(raw)
 for n in ['data/trek/worldgen/structure/village/cherry.json','data/trek/worldgen/template_pool/village/cherry/houses.json','data/trek/worldgen/template_pool/village/cherry/town_centers.json','data/trek/tags/worldgen/biome/has_structure/village_cherry.json','data/trek/loot_tables/village/village_cherry_house.json']:
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

plans=[]
for y in range(size[1]):plans.append(dict(y=y,rows_z=[' '.join(str(bs[(x,y,z)]['state'])if(x,y,z)in bs else'_' for x in range(size[0]))for z in range(size[2])]))
put('all-layers-state-index.json',dict(legend='x increases within row/z by row; _ omitted unknown',layers=plans))
put('active-checkpoint.json',dict(batch=306,status='ORIGINAL_EXTRACTED_NO_PNG_BEFORE_FAMILY_COMPARISON',new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,next='Read original plans/81palette/8BE, compare old249 and301/297 before PNG; wooden ladder storage access is not independent credit by itself.'))
print(json.dumps(dict(counts=ld(P/'source-counts.json'),matches=matches,exact_member_history_hits=hits),ensure_ascii=False))
