"""Source-specific static evidence, no native execution or reference admission."""
import json,hashlib,itertools,collections,zipfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from whole_building_candidates import iso,AIR
from PIL import Image
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(f,d):(OUT/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
n=json.loads((OUT/'original.json').read_text());pal=n['palette'];st={tuple(b['pos']):b for b in n['blocks']};binding=json.loads((OUT/'source-binding.json').read_text());checks=[]
def check(name,ok,detail):
 assert ok,name
 checks.append({'check':name,'pass':True,'detail':detail})
check('fixed archive and member unchanged',sha(Path(binding['archive']).read_bytes())==binding['archive_sha256'] and sha(zipfile.ZipFile(binding['archive']).read(binding['member']))==binding['nbt_sha256'],'Rechecks both independent byte bindings after primary source reading.')
rows=json.loads((OUT/'full-space.json').read_text())['rows'];decoded={}
for r in rows:
 x=0
 for s,c in r['runs_x']:
  for _ in range(c):decoded[x,r['y'],r['z']]=s;x+=1
 assert x==20
check('full volume rows exactly reproduce original states',len(decoded)==9000 and all(st[p]['state']==s for p,s in decoded.items()),'450 rows over15 layers reproduce all9000 stored states, no omitted cells.')
groups=json.loads((OUT/'all-rows-grouped.json').read_text());expanded=[]
for g in groups:
 for z in range(g['z_start'],g['z_end']+1):expanded.append({'y':g['y'],'z':z,'runs_x':g['runs_x']})
check('actually read grouped rows are lossless',expanded==rows,'Contiguous identical Z-row groups retain full source volume; grouping is not new building count.')
sand=[p for p,b in st.items() if pal[b['state']]['Name']=='minecraft:sandstone'];contexts=json.loads((OUT/'source-contexts.json').read_text());pool=next(r['object'] for r in contexts if '/template_pool/' in r['member']);processor=pool['elements'][0]['element']['processors']['processors'][0]
check('entire apparent y0 ground skipped by source pool',len(sand)==600 and set(sand)=={(x,0,z) for x in range(20) for z in range(30)} and {'Name':'minecraft:sandstone'} in processor['blocks'],'All20×30 y0 sandstone cells are ignored. Replaced with nothing in source projection; actual existing world ground remains unknown.')
fluid=[p for p,b in st.items() if pal[b['state']]['Name']=='radiation_zone_reborn:decaying_waste_liquid']
check('south hollow pier contains exact five-high source fluid',set(fluid)=={(x,y,z) for x in range(6,9) for y in range(1,6) for z in range(23,26)},'45 stored liquid blocks, not a mercury moat or tested hazard implementation.')
features=[b for b in st.values() if any(k in pal[b['state']]['Name'] for k in ['ladder','door','jigsaw','campfire','furnace','bed'])]
check('no source saved vertical ladder door beacon or bed',not features,'No saved ladder, door, jigsaw, campfire, furnace or bed. Does not prove impossibility of jumping rubble or missing external world paths.')
positions=set()
for y in range(7,12):
 for z in range(16,22):positions.add((13,y,z))
for z in [11,12,13]:
 for y in [8,9,10,11]:
  for x in [11,12,13,14,15]:positions.add((x,y,z))
for x in [5,7,13]:
 for y in [0,1,5,6,9,10,11,14]:positions.add((x,y,24 if x<10 else 6))
selected=[{'position':p,'state':pal[st[p]['state']]} for p in sorted(positions)]
save('selected-route-states.json',selected)
check('specific missing y8 horizontal bridge continuation',all(pal[st[13,8,z]['state']]['Name']=='minecraft:air' for z in [19,20,21]),'At x13,y8,z17 source brick, z18 bottom brick slab, z19..21 explicit air. This disproves an unbroken level y8 support strip only, not all possible ascent/jump routes.')
cells={p:pal[b['state']]['Name'] for p,b in st.items() if pal[b['state']]['Name'] not in AIR and pal[b['state']]['Name']!='minecraft:sandstone'}
im=Image.new('RGB',(1520,680),'#edf0f2')
for r in range(2):im.paste(iso(cells,n['size'],r,'Source ignore projection: y0 sandstone omitted; world terrain UNKNOWN'),(760*r,0))
im.save(OUT/'source-ignore-projection.png')
save('verification.json',{'static_only':True,'checks':checks,'selected_original_positions':len(selected),'Java_run':False,'native_collision_claimed':False})
print(json.dumps({'checks':checks,'selected_positions':len(selected)},ensure_ascii=False))
print('SELECTED',json.dumps(selected,separators=(',',':')))
