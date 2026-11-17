#!/usr/bin/env python3
"""Original states, one-level sockets, exact family bounds; no assembly."""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def exact_value(value,identifier):
 if isinstance(value,str):return value==identifier
 if isinstance(value,dict):return any(exact_value(v,identifier) for v in value.values())
 if isinstance(value,list):return any(exact_value(v,identifier) for v in value)
 return False
def load(c):
 with ZipFile(c['source_archive']) as z:raw=z.read(c['member'])
 assert sha(raw)==c['nbt_sha256']
 d=read(raw);pal=d.get('palette') or d['palettes'][0]
 return d,{tuple(b['pos']):pal[b['state']] for b in d['blocks'] if pal[b['state']]['Name'] not in AIR}
def main():
 src=json.loads((OUT/'sources.json').read_text());rows=[];cache={}
 for c in src['candidates']:
  d,cells=load(c);cache[c['id']]=cells;outgoing=[];selectors=[]
  with ZipFile(c['source_archive']) as z:
   for pool in sorted({s['data']['pool'] for s in c['sockets']}):
    ns,name=pool.split(':',1);member=f'data/{ns}/worldgen/template_pool/{name}.json'
    row=dict(pool=pool,socket_positions=[s['position'] for s in c['sockets'] if s['data']['pool']==pool],member=member,
     assembled=False,building_credit=0)
    if pool=='minecraft:empty':row['status']='EMPTY_TERMINAL'
    elif member in z.namelist():
     raw=z.read(member);row.update(status='FOUND_LOCAL',sha256=sha(raw),data=json.loads(raw))
    else:row['status']='NOT_PRESENT_IN_FIXED_SOURCE_ARCHIVE'
    outgoing.append(row)
   ident=c['member'].split('/structures/',1)[0].split('/')[-1]+':'+c['member'].split('/structures/',1)[1][:-4]
   for n in z.namelist():
    if n.endswith('.json'):
     raw=z.read(n)
     if ident.encode() in raw:
      data=json.loads(raw)
      if exact_value(data,ident):selectors.append(dict(member=n,sha256=sha(raw),data=data))
  rows.append(dict(id=c['id'],nbt_sha256=c['nbt_sha256'],size=d['size'],
   occupied_bounds=[[min(p[a] for p in cells),max(p[a] for p in cells)] for a in range(3)],
   materials=dict(Counter(s['Name'] for s in cells.values())),
   original_vertical_opening_states=[dict(position=list(p),state=s) for p,s in cells.items() if s['Name'].endswith(('_stairs','_door','_trapdoor','_fence_gate')) or s['Name']=='minecraft:ladder'],
   sockets=c['sockets'],outgoing_pools=outgoing,archive_json_identity_mentions=selectors,
   json_search_limit='Exact JSON string values, never prefix matches, in source archive JSON only; absence is not proof of dead asset or whole-building authorship.',
   native_routes_verified=False,terrain_generated=False,components_assembled=False))
 dump('raw-source-audit.json',dict(entries=rows,building_credit_added=0,network_requests=0,java_run=False,game_run=False,
  limits='One-level pool definitions only, no component visual study, no recursive selection, projection or native terrain/collision verification.'))
 batch=int(OUT.name.rsplit('-',1)[1]);family={}
 if batch==17:
  a={(x,y-1,z):s for (x,y,z),s in cache['F03'].items() if 3<=y<=6}
  b={p:s for p,s in cache['F04'].items() if 2<=p[1]<=5}
  common=a.keys()&b.keys();family=dict(pair=['017-F03','017-F04'],left_original_y_band=[3,6],left_y_translation=-1,right_original_y_band=[2,5],
   left_nonair=len(a),right_nonair=len(b),common_positions=len(common),same_original_name_and_properties=sum(a[p]==b[p] for p in common),
   differences=[dict(translated_position=list(p),left=a.get(p),right=b.get(p)) for p in sorted(a.keys()|b.keys()) if a.get(p)!=b.get(p)],
   limits='Only specified lower room/landing band. Not whole-template equality. Extended upper shaft still recorded; same lower band alone is not proof of design identity.')
 elif batch==18:
  pairs=[]
  for a,b in itertools.combinations(cache,2):
   ca,cb=cache[a],cache[b];common=ca.keys()&cb.keys();union=ca.keys()|cb.keys()
   pairs.append(dict(pair=[a,b],left_nonair=len(ca),right_nonair=len(cb),common_positions=len(common),union_positions=len(union),
    occupancy_jaccard=len(common)/len(union),same_original_name_and_properties=sum(ca[p]==cb[p] for p in common)))
  family=dict(pairs=pairs,coordinate_transform='None; original stored axes and coordinates. No material/state normalization.',
   limits='Nonair occupancy only; air vs omitted cells, stair geometry/collision and native material behavior not equated. Manual seven-aspect comparison supports family grouping; no automatic credit.')
 else:family=dict(status='NO_AUTOMATIC_FAMILY_INFERENCE',building_credit_added=0)
 dump('family-evidence.json',dict(evidence=family,building_credit_added=0,semantic_decision_automatic=False))
 print(f'Audited {len(rows)} source bodies and original states; no assembly or credit.')
if __name__=='__main__':main()
