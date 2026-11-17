import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not (P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
from reference_components import geometry_hash,role
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
mp=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';m=ld(mp)
inv=ld(m['fixed_archive_inventory']['path']);cache=R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json'
results=[]
for key in ['cartographer','fletcher']:
 member=f'data/kaisyn/structures/village/flower_forest_japanese/houses/flower_forest_{key}_1.nbt'
 e=next(x for x in m['entries']if x['member']==member);arc=bind(e['source_archive'])
 assert arc['sha256']==next(x['sha256']for x in inv['archives']if x['path']==arc['path'])
 with ZipFile(arc['path'])as z:
  raw=z.read(member);assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256'];d=read(raw)
 pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};size=d['size'];cells={p:pal[b['state']]['Name']for p,b in bs.items()if pal[b['state']]['Name']not in AIR}
 fp=dict(nbt_sha256=e['nbt_sha256'],role_sha256=geometry_hash({p:role(n)for p,n in cells.items()},size),occupancy_sha256=geometry_hash({p:1 for p in cells},size))
 matches=[x for x in ld(cache)['entries']if any(x['fingerprints'].get(k)==v for k,v in fp.items())]
 counts=dict(size=size,DataVersion=d['DataVersion'],declared=math.prod(size),stored=len(bs),nonair=len(cells),air=len(bs)-len(cells),unknown=math.prod(size)-len(bs),palette=len(pal),BE=sum('nbt'in b for b in bs.values()),entities=d.get('entities',[]),materials=dict(Counter(cells.values())))
 plans=[dict(y=y,rows_z=[' '.join(str(bs[x,y,z]['state'])if(x,y,z)in bs else'_' for x in range(size[0]))for z in range(size[2])])for y in range(size[1])]
 put(key+'-original.json',d)
 put(key+'-precheck.json',dict(source=dict(archive=arc,member=member,raw_sha256=e['nbt_sha256'],original=bind(P/(key+'-original.json')),metadata=bind(mp)),counts=counts,all_palette=pal,all_BE=[dict(pos=b['pos'],state=pal[b['state']],nbt=b['nbt'])for b in bs.values()if'nbt'in b],all_layers=plans,fingerprint_cache=bind(cache),fingerprints=fp,historical_matches=matches,limits='Original metadata/plans prequalification only; no PNG/complete-whole/reference credit yet. No match is not novelty.'))
 results.append(dict(key=key,counts=counts,matches=len(matches)))
put('active-checkpoint.json',dict(batch=308,status='ORIGINALS_EXTRACTED_PENDING_PURPOSE_FAMILY_PRECHECK_NO_PNG',sources=results,PNGs=0,complete_whole_studies=0,formal_credit_added=0,next='Actually read all original palette/BE/plans; compare old301/family and original market/forge tasks before any PNG.'))
print(json.dumps(results,ensure_ascii=False))
