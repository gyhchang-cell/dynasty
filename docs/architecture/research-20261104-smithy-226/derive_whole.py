import json,hashlib,sys,itertools,importlib.util
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];assert not(P/'RECEIPT.json').exists();sys.path.insert(0,str(ROOT/'tools/architecture'))
from whole_building_candidates import iso,plans,AIR
spec=importlib.util.spec_from_file_location('sections',ROOT/'docs/architecture/research-20261101-task-map/inspect_expanded_sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
rows=read(P/'raw-source-audit.json')['candidates']; component=read(P.parent/'research-20261104-smithy-224/raw-source-audit.json')['candidates'][1]; component2=json.loads(json.dumps(component)); component2['id']='F05'; rows.extend([component,component2]); put('reused-component.json',dict(source_path=str((P.parent/'research-20261104-smithy-224/raw-source-audit.json').resolve()),source_sha256=hashlib.sha256((P.parent/'research-20261104-smithy-224/raw-source-audit.json').read_bytes()).hexdigest(),component=component,placements=2,unique_reused_sources=1,not_two_buildings=True,old_PNG_reopened=False));raw={};allstates={};conflicts=[];subs=[]
for r,o in zip(rows,[(0,0,0),(3,1,4),(4,1,12)]):
 n=r['nbt_decoded_original'];pal=n['palette'];c={tuple(b['pos']):b for b in n['blocks']};sx,sy,sz=n['size'];lines=['Original state indices; rows z columns x; all declared positions stored.']
 for y in range(sy):
  lines.append(f'y={y}')
  for z in range(sz):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([c[(x,y,z)]['state']for x in range(sx)])))
 (P/f"{r['id']}-full-layer-index-rle.txt").write_text('\n'.join(lines)+'\n');print(r['id']);print('\n'.join(lines))
 for b in n['blocks']:
  st=pal[b['state']];name=st['Name'];q0=b['pos'];q0=([q0[2],q0[1],-q0[0]] if r['id']in ['F04','F05'] else q0);q=tuple(a+w for a,w in zip(q0,o));st=json.loads(json.dumps(st))
  if r['id']in ['F04','F05'] and 'facing' in st.get('Properties',{}):st['Properties']['facing']={'north':'west','west':'south','south':'east','east':'north'}[st['Properties']['facing']]
  if name=='minecraft:jigsaw':
   name=b['nbt']['final_state'];subs.append(dict(id=r['id'],pos=b['pos'],composite_pos=q,state=st,BE=b['nbt']));st=dict(Name=name)
   if '[' in name:
    name,props=name.rstrip(']').split('[',1);st=dict(Name=name,Properties=dict(kv.split('=') for kv in props.split(',')))
  if name in AIR or name=='minecraft:structure_void':
   if r['id']=='F01':allstates[q]=st
   continue
  if q in raw:conflicts.append(dict(pos=q,parent=raw[q],child=name))
  raw[q]=name;allstates[q]=st
size=[17,9,15];rev={(16-x,y,14-z):n for(x,y,z),n in raw.items()};whole=Image.new('RGB',(1520,1360),'#edf0f2')
for i,(c,rot)in enumerate([(raw,0),(raw,1),(rev,0),(rev,1)]):whole.paste(iso(c,size,rot,'226 one Iberian large house1 + two toolsmith placements; derived no native world'),(760*(i%2),680*(i//2)))
whole.save(P/'whole-assembly.png');cut=Image.new('RGB',(1520,1360),'#edf0f2')
for i,(y,rot)in enumerate([(2,0),(2,1),(5,0),(5,1)]):cut.paste(iso(raw,size,rot,f'226 derived cutoff y{y}',cutoff=y),(760*(i%2),680*(i//2)))
cut.save(P/'whole-cutaway.png');m.vertical(raw,size,'226 Iberian house + rotated toolsmith').save(P/'whole-vertical.png')
for y in [0,2,4,6,8]:plans(raw,size,y,'226 one composite; original source, processors unexecuted').save(P/f'whole-y{y}.png')
put('derived-assembly.json',dict(parent_origin=[0,0,0],module_origins=[[3,1,4],[4,1,12]],derivation='CCW90(x,y,z)=(z,y,-x); parent(5,0,3) and(6,0,11) +up -R(1,0,2) gives(3,1,4)/(4,1,12)',orientation='parent up_east aligned; child down_south aligned rotated CCW90 gives down_east; parent target=child name=bottom',one_whole_only=True,module_boxes=[[[3,1,2],[5,2,4]],[[4,1,10],[6,2,12]]],all_inside_parent=True,overlap_nonair=conflicts,substitutions=subs,derived_nonair=len(raw),legacy_ignores_air=True,source_processor_not_executed=True,original_palette_properties_preserved=True,worldgen_not_executed=True))
put('derived-source-cells.json',dict(cells=[dict(pos=q,state=st)for q,st in sorted(allstates.items())],not_actual_world_air_or_processor_result=True))
print('DEVICEPOSITIONS',[(q,n)for q,n in raw.items()if any(k in n for k in ['chest','crafting','smithing','bamboo','fence'])]);print('CONFLICTS',conflicts,'nonair',len(raw))
