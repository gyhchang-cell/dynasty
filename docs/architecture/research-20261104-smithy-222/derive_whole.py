import json,hashlib,sys,itertools,importlib.util
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];assert not(P/'RECEIPT.json').exists();sys.path.insert(0,str(ROOT/'tools/architecture'))
from whole_building_candidates import iso,plans,AIR
spec=importlib.util.spec_from_file_location('sections',ROOT/'docs/architecture/research-20261101-task-map/inspect_expanded_sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
rows=read(P/'raw-source-audit.json')['candidates'];raw={};allstates={};conflicts=[];subs=[]
for r,o in zip(rows,[(0,0,0),(2,1,2)]):
 n=r['nbt_decoded_original'];pal=n['palette'];c={tuple(b['pos']):b for b in n['blocks']};sx,sy,sz=n['size'];lines=['Original state indices; rows z columns x; all declared positions stored.']
 for y in range(sy):
  lines.append(f'y={y}')
  for z in range(sz):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([c[(x,y,z)]['state']for x in range(sx)])))
 (P/f"{r['id']}-full-layer-index-rle.txt").write_text('\n'.join(lines)+'\n');print(r['id']);print('\n'.join(lines))
 for b in n['blocks']:
  st=pal[b['state']];name=st['Name'];q=tuple(a+w for a,w in zip(b['pos'],o))
  if name=='minecraft:jigsaw':
   name=b['nbt']['final_state'];subs.append(dict(id=r['id'],pos=b['pos'],composite_pos=q,state=st,BE=b['nbt']));st=dict(Name=name)
  if name in AIR:
   if r['id']=='F01':allstates[q]=st
   continue
  if q in raw:conflicts.append(dict(pos=q,parent=raw[q],child=name))
  raw[q]=name;allstates[q]=st
size=[7,6,7];rev={(6-x,y,6-z):n for(x,y,z),n in raw.items()};whole=Image.new('RGB',(1520,1360),'#edf0f2')
for i,(c,rot)in enumerate([(raw,0),(raw,1),(rev,0),(rev,1)]):whole.paste(iso(c,size,rot,'222 one original pavilion + toolsmith; orange is processor placeholder'),(760*(i%2),680*(i//2)))
whole.save(P/'whole-assembly.png');cut=Image.new('RGB',(1520,1360),'#edf0f2')
for i,(y,rot)in enumerate([(1,0),(1,1),(2,0),(2,1)]):cut.paste(iso(raw,size,rot,f'222 derived cutoff y{y}',cutoff=y),(760*(i%2),680*(i//2)))
cut.save(P/'whole-cutaway.png');m.vertical(raw,size,'222 original pavilion + toolsmith module').save(P/'whole-vertical.png')
for y in [0,2,4]:plans(raw,size,y,'222 original one composite; processor not executed').save(P/f'whole-y{y}.png')
put('derived-assembly.json',dict(parent_origin=[0,0,0],module_origin=[2,1,2],derivation='(3,0,3)+(0,1,0)-(1,0,1)=(2,1,2)',orientation='parent up_east rollable and child down_east rollable; selected no rotation',one_whole_only=True,module_box=[[2,1,2],[4,2,4]],all_inside_parent=True,overlap_nonair=conflicts,substitutions=subs,derived_nonair=len(raw),legacy_ignores_air=True,orange_concrete_not_final_surface=True,original_palette_properties_preserved=True,worldgen_not_executed=True))
put('derived-source-cells.json',dict(cells=[dict(pos=q,state=st)for q,st in sorted(allstates.items())],not_actual_world_air_or_processor_result=True))
print('DEVICEPOSITIONS',[(q,n)for q,n in raw.items()if any(k in n for k in ['chest','crafting','smithing','bamboo','fence'])]);print('CONFLICTS',conflicts,'nonair',len(raw))
