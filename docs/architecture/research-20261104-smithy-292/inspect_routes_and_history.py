"""Bounded source route probes and semantic-history screening, without runtime."""
import json,hashlib,sys
from pathlib import Path
from collections import Counter,defaultdict
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
graph=ld(P/'source-socket-graph.json');templates={p.stem.removesuffix('-original'):ld(p)for p in P.glob('*-original.json')}
def rot(p,r):
 x,y,z=p
 for _ in range(r):x,z=-z,x
 return x,y,z
full={};stairs=[];by_template=[]
for pl in graph['placements']:
 d=templates[pl['key']];pal=d['palette']
 for b in d['blocks']:
  q=rot(b['pos'],pl['rotation_quarter_turns']);q=tuple(q[i]+pl['offset'][i]for i in range(3))
  full[q]=dict(pos=q,state=pal[b['state']],source_key=pl['key'],source_position=b['pos'],placement=pl['id'],state_coordinate_system='ORIGINAL LOCAL properties, position transformed only')
for key in sorted(set(pl['key']for pl in graph['placements'])):
 d=templates[key];pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']}
 bottom={q:pal[b['state']]for q,b in bs.items()if pal[b['state']]['Name'].endswith('_stairs')and pal[b['state']].get('Properties',{}).get('half')=='bottom'}
 chains=[]
 for q,s in bottom.items():
  dx,dz={'east':(1,0),'west':(-1,0),'south':(0,1),'north':(0,-1)}[s['Properties']['facing']]
  def match(t):return t in bottom and bottom[t]['Name']==s['Name']and bottom[t]['Properties']['facing']==s['Properties']['facing']
  if match((q[0]-dx,q[1]-1,q[2]-dz)):continue
  chain=[q]
  while match((chain[-1][0]+dx,chain[-1][1]+1,chain[-1][2]+dz)):chain.append((chain[-1][0]+dx,chain[-1][1]+1,chain[-1][2]+dz))
  if len(chain)>=3:chains.append(dict(name=s['Name'],facing=s['Properties']['facing'],positions=chain))
 by_template.append(dict(key=key,bottom_stair_y_counts=dict(Counter(q[1]for q in bottom)),long_straight_flights=chains,door_ladder_scaffold_states=[v for v in pal if any(t in v['Name']for t in ['_door','ladder','scaffolding'])],interpretation='Straight source runs only; neither proof of continuity nor proof no route exists.'))
put('source-stair-reading.json',dict(templates=by_template,credit=0))
probes=[]
for e in graph['edges']:
 points=[]
 for tag,base in [('parent',e['parent_world_socket']),('child',e['desired_child_world_socket'])]:
  for y in range(base[1]-1,base[1]+3):
   q=(base[0],y,base[2]);points.append(dict(tag=tag,**full.get(q,dict(pos=q,omitted=True))))
 probes.append(dict(parent=e['parent'],child=e['child'],points=points))
put('socket-floor-head-probes.json',dict(edges=probes,boundary='Markers not replaced, no directional state rotation, collision/processor/terrain not executed; no native route certificate'))
paths=[];hits=[]
names=set(templates)
def walk(v,loc):
 if isinstance(v,dict):
  if any(isinstance(t,str)and any(t.endswith('/'+n+'.nbt')for n in names)for t in v.values()):
   hits.append(dict(location=loc,keys=list(v),scalars={k:t for k,t in v.items()if isinstance(t,(str,int,bool))}))
  for k,t in v.items():walk(t,loc+'/'+str(k))
 elif isinstance(v,list):
  for i,t in enumerate(v):walk(t,loc+'/'+str(i))
for pattern in ['research-*/manual-review.json','research-*/reference-proposals.json','research-*/*scope*register.json','continuation-20261022/references/*/candidates.json','continuation-20261022/references/full-buildings.json']:
 for p in sorted((R/'docs/architecture').glob(pattern)):
  if p.parent==P:continue
  paths.append(bind(p));walk(ld(p),str(p))
put('history-own-record-search.json',dict(paths=paths,hits=hits,boundary='Bounded direct own-member occurrences, distinguish machine candidates and nearest comparisons; no full chat-history novelty claim'))
comparisons=[]
for path,selection in [(R/'docs/architecture/research-20261104-smithy-291/manual-review.json',None),(R/'docs/architecture/research-20261101-dungeons-002/manual-review.json','F09')]:
 d=ld(path);entry=d if selection is None else next(x for x in d['entries']if x['id']==selection)
 comparisons.append(dict(binding=bind(path),whole_entry=entry,current_actual_reading='Full own seven observations and all limits/credit read; historical PNG not reopened/recounted.'))
put('prior-whole-comparisons.json',dict(prior=comparisons,current='Current94×39×94 source complex is central circular high arena plus four radial colonnaded halls and attached miniature pavilions, unlike291 asymmetric stacked residential fortress or old002F09 axial lower hall/central upper pavilion. This supports a different whole source layout; source glass/Greek columns and ground heightmap do not become Chinese floating islands.'))
cp=ld(P/'active-checkpoint.json');cp.update(images_actually_viewed=9,plan_layers_actually_viewed=16,section_planes_actually_viewed=2,palette_material_groups_read=32,BE_unique_payload_groups_read=22,entity_profiles_read=17,next='实际读64接头足头状态与完整历史命中，再写七维结论及保留入口/上层/地形差距；不删除任务。');put('active-checkpoint.json',cp)
print(json.dumps(dict(history_paths=len(paths),hits=hits,stairs=[dict(key=t['key'],long_flights=len(t['long_straight_flights']),door_ladder_scaffold_states=t['door_ladder_scaffold_states'])for t in by_template]),ensure_ascii=False))
