"""Reconstruct the author's fixed socket graph for source study, not production.
No Java, world, game asset, master checklist or existing sealed batch writes.
"""
import json, hashlib, sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter, defaultdict
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent; R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import iso,color,AIR
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
meta=ld(R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json')
a=next(x for x in meta['entries']if x['member'].endswith('/cloudy_temple_arena.nbt'))
archive=bind(a['source_archive']); inv=ld(meta['fixed_archive_inventory']['path'])
assert archive['sha256']==next(x['sha256']for x in inv['archives']if x['path']==archive['path'])
templates={};context=[]
with ZipFile(archive['path'])as z:
 for n in z.namelist():
  if '/structures/cloudy_temple'in n and n.endswith('.nbt'):
   raw=z.read(n);d=read(raw);key=Path(n).stem
   expected=next(x for x in meta['entries']if x['source_archive']==archive['path']and x['member']==n)
   assert hashlib.sha256(raw).hexdigest()==expected['nbt_sha256']
   templates[key]=d
   put(key+'-original.json',d)
  if 'cloudy_temple'in n and ('/worldgen/'in n or '/has_structure/'in n)and n.endswith(('.json','.txt')):
   raw=z.read(n);context.append(dict(member=n,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),text=raw.decode(),json=json.loads(raw)))
put('source-context.json',dict(archive=archive,resources=context))
sources=[]
for key,d in templates.items():
 pal=d['palette'];counts=Counter(pal[b['state']]['Name']for b in d['blocks'])
 sockets=[dict(pos=b['pos'],state=pal[b['state']],nbt=b.get('nbt'))for b in d['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw']
 sources.append(dict(key=key,size=d['size'],binding=bind(P/(key+'-original.json')),stored=len(d['blocks']),palette=len(pal),materials=dict(counts),sockets=sockets,entity_count=len(d.get('entities',[]))))
put('source-inventory.json',dict(archive=archive,templates=sources,source_index=bind(R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json')))
def rotate(p,r):
 x,y,z=p
 for _ in range(r):x,z=-z,x
 return x,y,z
faces=dict(east=(1,0,0),west=(-1,0,0),north=(0,0,-1),south=(0,0,1),up=(0,1,0),down=(0,-1,0))
opposite=dict(east='west',west='east',north='south',south='north',up='down',down='up')
def rotated_face(f,r):
 v=rotate(faces[f],r)
 return next(k for k,x in faces.items()if x==v)
def sockets(key):return next(x['sockets']for x in sources if x['key']==key)
placements=[dict(id='arena',key='cloudy_temple_arena',rotation_quarter_turns=0,offset=[0,0,0],parent=None)]
queue=[placements[0]];edges=[]
pools={x['json']['name']:x['json']for x in context if '/template_pool/'in x['member'] and x['member'].endswith('.json')}
while queue:
 parent=queue.pop(0)
 for socket in sockets(parent['key']):
  nbt=socket['nbt'];pool=nbt['pool']
  if pool=='minecraft:empty':continue
  pooldef=pools[pool];assert len(pooldef['elements'])==1
  element=pooldef['elements'][0]['element'];assert element['projection']=='rigid'and element['processors']=='minecraft:empty'
  key=element['location'].split(':')[1];matches=[s for s in sockets(key)if s['nbt']['name']==nbt['target']];assert len(matches)==1
  child_socket=matches[0]
  pf=rotated_face(socket['state']['Properties']['orientation'].split('_')[0],parent['rotation_quarter_turns'])
  cf=child_socket['state']['Properties']['orientation'].split('_')[0]
  rotations=[r for r in range(4)if rotated_face(cf,r)==opposite[pf]];assert len(rotations)==1
  rot=rotations[0];pp=rotate(socket['pos'],parent['rotation_quarter_turns']);pp=[pp[i]+parent['offset'][i]for i in range(3)]
  desired=[pp[i]+faces[pf][i]for i in range(3)];cp=rotate(child_socket['pos'],rot);offset=[desired[i]-cp[i]for i in range(3)]
  child=dict(id=parent['id']+'/'+pool.rsplit('/',1)[1],key=key,rotation_quarter_turns=rot,offset=offset,parent=parent['id'])
  placements.append(child);queue.append(child)
  edges.append(dict(parent=parent['id'],child=child['id'],pool=pool,parent_socket=socket,child_socket=child_socket,parent_world_socket=pp,desired_child_world_socket=desired,rotation_quarter_turns=rot,offset=offset,name_target_match=child_socket['nbt']['name']==nbt['target']))
assert len(placements)==9 and len(edges)==8
full={};owners={};collisions=[];bounds=[];be_groups=defaultdict(list);entities=[];palette_groups=defaultdict(dict)
for pl in placements:
 d=templates[pl['key']];pal=d['palette'];points=[]
 for state in pal:palette_groups[state['Name']][json.dumps(state.get('Properties',{}),sort_keys=True)]=state.get('Properties',{})
 for x in [0,d['size'][0]-1]:
  for y in [0,d['size'][1]-1]:
   for z in [0,d['size'][2]-1]:
    q=rotate((x,y,z),pl['rotation_quarter_turns']);points.append(tuple(q[i]+pl['offset'][i]for i in range(3)))
 low=[min(p[i]for p in points)for i in range(3)];high=[max(p[i]for p in points)for i in range(3)];bounds.append(dict(id=pl['id'],min=low,max=high))
 for b in d['blocks']:
  q=rotate(b['pos'],pl['rotation_quarter_turns']);q=tuple(q[i]+pl['offset'][i]for i in range(3))
  if q in full:collisions.append(dict(pos=q,a=owners[q],b=pl['id']))
  full[q]=dict(state=pal[b['state']],source_position=b['pos'],source_key=pl['key'],placement=pl['id'])
  owners[q]=pl['id']
  if 'nbt'in b:be_groups[json.dumps(b['nbt'],sort_keys=True)].append(dict(placement=pl['id'],source_position=b['pos'],world_source_position=q))
 for i,e in enumerate(d.get('entities',[])):
  q=rotate(e['pos'],pl['rotation_quarter_turns']);q=[q[i]+pl['offset'][i]for i in range(3)]
  entities.append(dict(placement=pl['id'],source_entity_index=i,world_source_position=q,nbt=e['nbt']))
intersections=[]
for i,a in enumerate(bounds):
 for b in bounds[i+1:]:
  if all(max(a['min'][j],b['min'][j])<=min(a['max'][j],b['max'][j])for j in range(3)):intersections.append([a['id'],b['id']])
put('source-socket-graph.json',dict(placements=placements,edges=edges,template_bounding_boxes=bounds,box_intersections=intersections,stored_cell_overlap_count=len(collisions),boundary='Exact rigid source-socket reconstruction, fixed single-option pools only. Root rotation held0 for readability; not native generation/collision/heightmap acceptance; block directional properties remain ORIGINAL LOCAL properties. Components and repeated mini placements count0 separately.'))
put('all-BE-lossless-groups.json',[dict(nbt=json.loads(n),positions=p)for n,p in be_groups.items()])
put('all-entity-originals.json',entities)
put('all-palette-properties.json',[dict(name=n,property_states=list(v.values()))for n,v in palette_groups.items()])
low=[min(p[i]for p in full)for i in range(3)];high=[max(p[i]for p in full)for i in range(3)];size=[high[i]-low[i]+1 for i in range(3)]
cells={tuple(p[i]-low[i]for i in range(3)):v['state']['Name']for p,v in full.items()if v['state']['Name']not in AIR}
put('assembled-source-counts.json',dict(source_min=low,source_max=high,size=size,placements=len(placements),distinct_used_templates=len(set(x['key']for x in placements)),stored_cells=len(full),nonair_cells=len(cells),unknown_cells=size[0]*size[1]*size[2]-len(full),BE_unique_groups=len(be_groups),BE_placed_positions=sum(len(v)for v in be_groups.values()),entity_positions=len(entities),material_groups=len(palette_groups),whole_reference_credit=0,final_state_or_processor_not_executed=True))
for label,cut in [('whole',None),('cut-05',5),('cut-14',14),('cut-24',24)]:
 im=Image.new('RGB',(1520,680),'#edf0f2')
 for i in range(2):im.paste(iso(cells,size if cut is None else[size[0],cut+1,size[2]],i,'292 author graph '+label,cut),(760*i,0))
 im.save(P/('complex-'+label+'.png'))
levels=[0,1,3,4,5,7,10,14,18,22,26,30,34,35,37,38]
for start in range(0,len(levels),4):
 im=Image.new('RGB',(1840,1940),'#edf0f2');dr=ImageDraw.Draw(im);step=9
 for j,y in enumerate(levels[start:start+4]):
  ox=40+920*(j%2);oy=45+970*(j//2);dr.text((ox,oy-24),f'292 y{y}; x={low[0]}..{high[0]}, z={low[2]}..{high[2]}; WHITE air / BLACK omitted',fill='black')
  for x in range(low[0],high[0]+1):
   for z in range(low[2],high[2]+1):
    v=full.get((x,y,z));n=v['state']['Name']if v else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
    dr.rectangle((ox+(x-low[0])*step,oy+(z-low[2])*step,ox+(x-low[0]+1)*step,oy+(z-low[2]+1)*step),fill=c,outline='#bdc3c8')
  for u in range(0,size[0],10):dr.text((ox+u*step,oy-12),str(u+low[0]),fill='black')
  for u in range(0,size[2],10):dr.text((ox-24,oy+u*step),str(u+low[2]),fill='black')
 im.save(P/f'complex-plans-{start//4+1}.png')
im=Image.new('RGB',(1880,570),'#edf0f2');dr=ImageDraw.Draw(im);step=9
for i,(axis,fixed)in enumerate([('x',20),('z',19)]):
 ox=40+940*i;oy=45;dr.text((ox,18),f'292 {axis}={fixed}, y up; class cubes, not native shapes',fill='black')
 for u in range(low[0],high[0]+1):
  for y in range(39):
   p=(fixed,y,u)if axis=='x'else(u,y,fixed);v=full.get(p);n=v['state']['Name']if v else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+(u-low[0])*step,oy+(38-y)*step,ox+(u-low[0]+1)*step,oy+(39-y)*step),fill=c,outline='#bdc3c8')
 for u in range(0,size[0],10):dr.text((ox+u*step,oy+39*step+5),str(u+low[0]),fill='black')
 for y in range(0,39,5):dr.text((ox-22,oy+(38-y)*step),str(y),fill='black')
im.save(P/'complex-sections.png')
put('protected-before.json',dict(files=[dict(before292=bind(x['after']['path']))for x in ld(P.parent/'research-20261104-smithy-291/protected-current.json')['files']]))
put('active-checkpoint.json',dict(batch=292,status='IN_PROGRESS_AUTHOR_CLOUD_COMPLEX_NOT_ACCEPTED',source=archive,source_json_count=len(templates),used_template_count=7,source_placements=9,source_socket_edges=8,generated_png=9,images_actually_viewed=0,whole_studies_completed=0,formal_credit_added=0,next='实际看9图/16层/2整剖；读原状态设施/实体/出入口与历史归属；排除unusedbase/txt/part455，不能把部件计多例。'))
print(json.dumps(dict(counts=ld(P/'assembled-source-counts.json'),boxes=intersections,images=9,context=len(context),placements=placements),ensure_ascii=False))
