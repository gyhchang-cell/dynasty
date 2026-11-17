"""Research-only four-layer contact sheets, with omitted/explicit-air distinction retained in JSON."""
import json,sys
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists();sys.path.insert(0,str(R/'tools/architecture'))
from whole_building_candidates import plans,AIR
parts=json.loads((P/'original-two-part-source.json').read_text())['parts'];cells={};states={};rows=[];be=[]
for i,a in enumerate(parts):
 d=a['nbt_decoded_original'];pal=d['palette']
 for b in d['blocks']:
  x,y,z=b['pos'];pos=(x,y+32*i,z);states[pos]=pal[b['state']]
  if pal[b['state']]['Name']not in AIR:cells[pos]=pal[b['state']]['Name']
  if 'nbt'in b:be.append({'part':i,'local_pos':b['pos'],'global_pos':list(pos),'state':pal[b['state']],'nbt':b['nbt']})
for y in range(64):
 plane=[{'pos':list(p),'state':s}for p,s in states.items()if p[1]==y];rows.append({'y':y,'stored':len(plane),'explicit_air':sum(p['state']['Name']in AIR for p in plane),'nonair':sum(p['state']['Name']not in AIR for p in plane),'omitted':48*34-len(plane),'ladder':[p for p in plane if 'ladder'in p['state']['Name']]})
for y in range(0,64,4):
 im=Image.new('RGB',(1520,1600),'#edf0f2');im.paste(plans(cells,[48,64,34],y,'joint-derived mill'),(0,0));im.paste(plans(cells,[48,64,34],y+2,'joint-derived mill'),(0,800));im.save(P/f'assembly-y{y:02}.png')
(P/'layer-inventory.json').write_text(json.dumps({'layers':rows,'block_entities':be},ensure_ascii=False,indent=2)+'\n');print('16 four-layer sheets generated; no semantic credit')
for r in rows:
 if r['ladder']:print(r['y'],[(p['pos'],p['state'])for p in r['ladder']])
print('BLOCK ENTITIES GROUPED BY IDENTICAL ORIGINAL NBT AND STATE')
groups={}
for b in be:
 key=json.dumps({'state':b['state'],'nbt':b['nbt']},sort_keys=True);groups.setdefault(key,[]).append(b['global_pos'])
for k,positions in groups.items():print(k,'positions',positions)
