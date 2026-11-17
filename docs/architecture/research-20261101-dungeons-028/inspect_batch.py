#!/usr/bin/env python3
"""Read one fixed whole candidate and an author's exact two-piece tower pairing.

Research images/JSON only. No NBT assets exported and no Java/game execution.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,iso,plans
sys.path.insert(0,str(BASE/'research-20261101-task-map'))
from inspect_expanded_sources import vertical
MODS=Path('/Users/a15356015027/Desktop/专业剪辑软件/虚饰作品 v1.3/overrides/mods')
def sha(b):return hashlib.sha256(b).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p.read_bytes()))
def dump(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def exact(v,k):
 if isinstance(v,str):return v==k
 if isinstance(v,dict):return any(exact(x,k)for x in v.values())
 if isinstance(v,list):return any(exact(x,k)for x in v)
 return False
def render(ident,cells,size,cutoff,level):
 names={p:s['Name']for p,s in cells.items()};im=Image.new('RGB',(1520,1400),'#edf0f2')
 for rot,x in [(0,0),(1,760)]:
  im.paste(iso(names,size,rot,ident+' full stored body'),(x,0))
  im.paste(iso(names,size,rot,ident+f' cutaway y <= {cutoff}',cutoff),(x,680))
 ImageDraw.Draw(im).text((18,1372),'RESEARCH / classification colours / full-cell approximation / not native terrain, textures or collision / no automatic credit',fill='#17252c')
 im.save(OUT/f'{ident}-whole.png');plans(names,size,level,ident).save(OUT/f'{ident}-plan.png')
 vertical(names,size,ident).save(OUT/f'{ident}-vertical.png')
def load(jar,member,ident,url):
 with ZipFile(jar)as z:
  raw=z.read(member);d=read(raw);pal=d.get('palette')or d['palettes'][0]
  states={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
  cells={p:s for p,s in states.items()if s['Name']not in AIR}
  source_id=member.split('/structures/')[0].split('/')[-1]+':'+member.split('/structures/')[1][:-4]
  refs=[]
  for name in z.namelist():
   if '/worldgen/template_pool/'in name and name.endswith('.json'):
    data=json.loads(z.read(name))
    if exact(data,source_id):refs.append(dict(member=name,data=data))
  sockets=[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{}))for b in d['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw']
 c=dict(id=ident,source_archive=str(jar),source_archive_sha256=sha(jar.read_bytes()),publisher_url=url,member=member,
  nbt_sha256=sha(raw),size=d['size'],nonair=len(cells),materials=dict(Counter(s['Name']for s in cells.values())),
  doors=[dict(position=list(p),state=s)for p,s in states.items()if s['Name'].endswith('_door')and s.get('Properties',{}).get('half')=='lower'],
  sockets=sockets,pool_references=refs,
  opening_and_vertical_states=[dict(position=list(p),state=s)for p,s in states.items()if any(k in s['Name']for k in ['stairs','ladder','door','gate','jigsaw'])],
  automatic_credit=0)
 return c,states,cells
def main():
 trek=next(MODS.glob('*远足*jar'));tower=next(MODS.glob('*totw_modded*jar'))
 f,fs,fc=load(trek,'data/trek/structures/overworld/medium/offshore_platform_pillager.nbt','F01','https://modrinth.com/datapack/trek')
 base,bs,bc=load(tower,'data/totw_modded/structures/aether/aether_skyroot_1.nbt','C01',None)
 cap,cs,cc=load(tower,'data/totw_modded/structures/aether/aether_skyroot_2.nbt','C02',None)
 render('F01',fc,f['size'],19,9)
 # The only considered transform comes from these exact aligned connectors.
 a,b=base['sockets'][0],cap['sockets'][0]
 assert len(base['sockets'])==len(cap['sockets'])==1
 assert a['state']['Properties']['orientation']=='up_south'and b['state']['Properties']['orientation']=='down_south'
 assert a['data']['joint']==b['data']['joint']=='aligned'
 assert a['data']['target']==b['data']['name']and b['data']['target']==a['data']['name']
 assert a['position']==[0,47,0]and b['position']==[0,0,0]
 assert a['data']['final_state']==b['data']['final_state']=='minecraft:air'
 offset=[0,48,0];cells={};sourcerows=[]
 for c,states,translation in [(base,bs,[0,0,0]),(cap,cs,offset)]:
  for p,s in states.items():
   pos=tuple(p[i]+translation[i]for i in range(3))
   if s['Name']=='minecraft:jigsaw':s=dict(Name='minecraft:air')
   if s['Name']not in AIR:
    assert pos not in cells;cells[pos]=s
  sourcerows.append(dict(component_id=c['id'],translation=translation,rotation_y_quarter_turns=0))
 render('A01',cells,[18,58,18],29,2)
 definitions=[];metadata=[]
 with ZipFile(tower)as z:
  for member in ['data/totw_modded/worldgen/structure/aether.json',
    'data/totw_modded/worldgen/template_pool/aether/aether_skyroot_1.json',
    'data/totw_modded/worldgen/template_pool/aether/aether_skyroot_2.json']:
   raw=z.read(member);definitions.append(dict(member=member,sha256=sha(raw),data=json.loads(raw)))
  raw=z.read('META-INF/mods.toml');metadata.append(dict(source_archive=str(tower),member='META-INF/mods.toml',sha256=sha(raw),text=raw.decode()))
 assert definitions[0]['data']['start_pool']=='totw_modded:aether/aether_skyroot_1'
 for row,ident in zip(definitions[1:],['totw_modded:aether/aether_skyroot_1','totw_modded:aether/aether_skyroot_2']):
  pool=row['data'];assert pool['fallback']=='minecraft:empty'and len(pool['elements'])==1
  element=pool['elements'][0];assert element['weight']==1 and element['element']['location']==ident
  assert element['element']['projection']=='rigid'and element['element']['processors']=='minecraft:empty'
 dump('sources.json',dict(candidates=[f],component_templates=[base,cap],source_archives=[
  dict(path=str(trek),sha256=sha(trek.read_bytes()),publisher_url=f['publisher_url']),
  dict(path=str(tower),sha256=sha(tower.read_bytes()),publisher_url=None)],automatic_credit=0,
  source_unit_limits='F01 is one candidate body with actor-only sockets. C01+C02 are two modules of at most one authored tower, never two complete references.'))
 dump('assembly-evidence.json',dict(id='A01',source_components=sourcerows,definitions=definitions,local_author_metadata=metadata,
  stored_size=[18,58,18],occupied_bounds=[[min(p[i]for p in cells),max(p[i]for p in cells)]for i in range(3)],
  nonair=len(cells),materials=dict(Counter(s['Name']for s in cells.values())),
  final_states_replaced=[dict(component_id=c['id'],original_position=c['sockets'][0]['position'],final_state='minecraft:air')for c in [base,cap]],
  cap_pool_back_edge='Cap connector points back to base pool and exactly back to already occupied base location; no repeated base is appended or new design inferred.',
  source_definition_only=True,native_jigsaw_generation_verified=False,nbt_exported=False,building_credit=0,
  limits='Exact rigid aligned two-piece relation, zero rotation. Does not simulate jigsaw scheduling, collision rejection, terrain projection or repeated selection; not a production asset.'))
 dump('assembly-original-states.json',dict(id='A01',states=[dict(position=list(p),state=s)for p,s in sorted(cells.items())],building_credit=0))
 # Discovery anchors are immutable prior stages, not guessed new publications.
 dump('discovery-boundary.json',dict(indices_checked=[ev(BASE/'research-20261101-dungeons-026/all-structure-metadata.json'),
  ev(BASE/'research-20261101-dungeons-027/source-needs.json'),ev(BASE/'research-20261101-dungeons-027/scoped-reference-update.json')],
  local_only=True,network_requests=0,java_run=False,game_run=False,production_changes=0,checklist_deletions=0,
  sound_brightness_window_save_changes=0,source_modules_read=3,possible_complete_design_candidates=2,
  scope_definitions_changed=False,automatic_reference_credit=0))
 print('Read one whole platform candidate, two exact tower modules; assembled research volume 18x58x18; credit 0.')
if __name__=='__main__':main()
