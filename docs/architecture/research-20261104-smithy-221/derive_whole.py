import json,hashlib,sys,itertools,importlib.util
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];assert not(P/'RECEIPT.json').exists();sys.path.insert(0,str(ROOT/'tools/architecture'))
from whole_building_candidates import iso,plans,AIR
spec=importlib.util.spec_from_file_location('sections',ROOT/'docs/architecture/research-20261101-task-map/inspect_expanded_sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def read(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
host=read(P/'raw-source-audit.json')['candidates'][0]['nbt_decoded_original'];old=ROOT/'docs/architecture/research-20261104-smithy-220';mod=read(old/'raw-source-audit.json')['candidates'][0]['nbt_decoded_original'];put('reused-component.json',dict(raw_binding=bind(old/'raw-source-audit.json'),judgment_binding=bind(old/'manual-review.json'),complete_component_judgment=read(old/'manual-review.json'),old_PNG_reopened=0,source_palette_BE_layers_reused_not_new_credit=True))
raw={};conflicts=[];substitutions=[];offset=(3,1,2)
for label,d,o in [('host',host,(0,0,0)),('module',mod,offset)]:
 pal=d['palette'];c={tuple(b['pos']):b for b in d['blocks']}
 if label=='host':
  lines=['Original state indices; rows z columns x; explicit air14; no omitted.']
  for y in range(14):
   lines.append(f'y={y}')
   for z in range(10):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([c[(x,y,z)]['state']for x in range(11)])))
  (P/'F01-full-layer-index-rle.txt').write_text('\n'.join(lines)+'\n')
 for b in d['blocks']:
  name=pal[b['state']]['Name'];q=tuple(v+w for v,w in zip(b['pos'],o));state=pal[b['state']]
  if name=='minecraft:jigsaw':
   final=b['nbt']['final_state'];substitutions.append(dict(source=label,pos=b['pos'],composite_pos=q,original=state,BE=b['nbt'],final_state=final));name=final.split('[')[0]
  # Legacy STRUCTURE_AND_AIR skips air, including replacement air; structure_void preserved as unplaced here.
  if name in AIR or name=='minecraft:structure_void':continue
  if label=='module'and q in raw:conflicts.append(dict(pos=q,host=raw[q],module=name))
  raw[q]=name
size=host['size'];rev={(size[0]-1-x,y,size[2]-1-z):n for(x,y,z),n in raw.items()};whole=Image.new('RGB',(1520,1360),'#edf0f2')
for i,(c,rot)in enumerate([(raw,0),(raw,1),(rev,0),(rev,1)]):whole.paste(iso(c,size,rot,'221 one barn + weapon module; legacy skips air; derived'),(760*(i%2),680*(i//2)))
whole.save(P/'whole-assembly.png');cut=Image.new('RGB',(1520,1360),'#edf0f2')
for i,(y,rot)in enumerate([(3,0),(3,1),(7,0),(7,1)]):cut.paste(iso(raw,size,rot,f'221 derived cutoff y{y}',cutoff=y),(760*(i%2),680*(i//2)))
cut.save(P/'whole-cutaway.png');m.vertical(raw,size,'221 DERIVED barn + single module').save(P/'whole-vertical.png')
for y in [0,3,6,9,12]:plans(raw,size,y,'221 derived original host + weapon module').save(P/f'whole-y{y}.png')
put('derived-assembly.json',dict(host_origin=[0,0,0],module_origin=offset,derivation='host(5,0,4)+UP(0,1,0)-child(2,0,2)=(3,1,2)',orientation='host up_west aligned; child down_west rollable, both top west, target/name minecraft:bottom',host_size=size,module_inside_host_bounds=True,module_box=[[3,1,2],[7,12,6]],one_whole_only=True,legacy_skip_air=True,not_generated_world_terrain=True,substitutions=substitutions,overlap_nonair_before_override=conflicts,derived_nonair=len(raw),native_collision_entity_worldgen_not_run=True))
print('8 derived PNG; overwritten original nonair',len(conflicts),'composite nonair',len(raw));print(json.dumps(conflicts,ensure_ascii=False));print((P/'F01-full-layer-index-rle.txt').read_text())
