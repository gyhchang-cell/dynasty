import hashlib, importlib.util, json, math, sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
R=Path(__file__).resolve().parents[3]; P=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash,role
from whole_building_candidates import AIR,color
from PIL import Image,ImageDraw
def ld(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
sp=importlib.util.spec_from_file_location('dd',R/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
base=ld(R/'docs/architecture/research-20261104-smithy-282/additional-smith-history-screen.json');h={}
indices=base['historical_indices']+[str(p) for i in range(282,287) for p in (R/f'docs/architecture/research-20261104-smithy-{i}').glob('*.json')]
for n in indices:m.find_records(ld(n),n,h)
meta=ld(R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json');inv=ld(meta['fixed_archive_inventory']['path']);ars={};rows=[]
for a in meta['entries']:
 if (a['source_archive'],a['member'])in h or '/houses/' not in a['member'] or math.prod(a['size'])<=4500:continue
 jar=a['source_archive']
 if jar not in ars:
  bb=bind(jar);assert bb['sha256']==next(x['sha256'] for x in inv['archives'] if x['path']==jar);ars[jar]=(bb,ZipFile(jar))
 ar,z=ars[jar];raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['nbt_sha256'];d=read(raw);pal=d['palette'];co=Counter(pal[b['state']]['Name'] for b in d['blocks']);devices={k:v for k,v in co.items() if any(t in k for t in ['anvil','furnace','grindstone','smithing_table','lava'])}
 rows.append(dict(source=a,archive=ar,devices_machine_only=devices,potential_smith_signature=any(t in k for k in devices for t in ['anvil','blast_furnace','grindstone','smithing_table']),complete_semantic_study=False))
for _,z in ars.values():z.close()
save('larger-house-device-screen.json',dict(selection='fixed metadata, selected historical archive/member index absent, /houses/, declared volume>4500; no other names or multipart buildings covered',historical_indices=indices,rows=rows,screen_only_credit=0,not_proof_never_previously_bounded=True))
cache={}
for e in ld(R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json')['entries']:
 cache[e['source']['archive'],e['source']['member']]=e['fingerprints']
for i in range(153,283):
 for p in (R/f'docs/architecture/research-20261104-smithy-{i:03d}').glob('*history-screen.json'):
  doc=ld(p)
  for row in doc.get('rows',[]):
   if 'source_archive' in row and 'current_source_fingerprints' in row:cache[row['source_archive'],row['member']]=row['current_source_fingerprints']
s=ld(P/'source.json');d=ld(P/'original-all-source.json');pal=d['palette'];blocks={tuple(b['pos']):b for b in d['blocks']};cells={p:pal[b['state']]['Name'] for p,b in blocks.items() if pal[b['state']]['Name']not in AIR}
fp=dict(nbt_sha256=s['nbt_sha256'],role_sha256=geometry_hash({p:role(n) for p,n in cells.items()},d['size']),occupancy_sha256=geometry_hash({p:1 for p in cells},d['size']))
matches=[]
for (jar,n),f in cache.items():
 eq=[k for k in fp if fp[k]==f.get(k)]
 if eq:matches.append(dict(source_archive=jar,member=n,keys=eq))
save('fingerprint-screen.json',dict(source={k:s[k] for k in ['source_archive','member','nbt_sha256']},current_fingerprints=fp,historical_cached_pairs=len(cache),matches=matches,cache_is_machine_evidence_not_semantic_novelty=True))
comp=[]
for i in [270,275]:
 p=R/f'docs/architecture/research-20261104-smithy-{i}/manual-review.json';a=ld(p)
 comp.append(dict(binding=bind(p),actual_current_reading='own seven dimensions and ALL own limits; old nested families preserved only',seven_dimensions=a['seven_dimensions'],limits=a['limits'],status_at_original=a['status'],no_original_images_or_NBT_reopened=True))
save('prior-whole-comparison.json',dict(priors=comp,current_comparison='当前地面炉/台作业层—中部公共阅读层及东小阳台—上部三床阁层，围中心木柱内回转阶；270紧凑下织机上单床围羊院、275两西入口低床窄间/大厅内短直阶上局部炉床均不同。此只说明空间组织差异，不证明当前住宅与大雪山猎户任务直接相关，不以三床或高楼层单独加数。原待审不转已验；仍HOLD0。'))
im=Image.new('RGB',(1520,500),'#edf0f2');draw=ImageDraw.Draw(im)
for j,(axis,loc,w) in enumerate([('z',4,25),('x',13,18)]):
 ox=j*760+70;oy=55;step=20;draw.text((ox,20),f'F01 {axis}={loc}; y0..18 only; white air / black omitted',fill='black')
 for y in range(19):
  for a in range(w):
   p=(a,y,loc) if axis=='z' else (loc,y,a);b=blocks.get(p);n=pal[b['state']]['Name'] if b else None;c='#171d26' if n is None else '#ffffff' if n in AIR else color(n)
   draw.rectangle((ox+a*step,oy+(18-y)*step,ox+(a+1)*step,oy+(19-y)*step),fill=c,outline='#a9afb5')
 for y in range(0,19,2):draw.text((ox-25,oy+(18-y)*step),str(y),fill='black')
im.save(P/'F01-vertical.png')
print('LARGER_SCREEN',len(rows),'POTENTIAL',sum(a['potential_smith_signature']for a in rows),'FP',len(cache),'MATCHES',matches)
