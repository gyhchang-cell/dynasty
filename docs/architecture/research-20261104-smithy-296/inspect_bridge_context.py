"""One source house and its stair approach, not two building references."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from whole_building_candidates import AIR,iso,color
def ld(n):return json.loads((P/n).read_text())
house=ld('source-original.json');b=ld('bridge-original.json');shift=(-12,0,16)
def cells(d):return {tuple(v['pos']):d['palette'][v['state']]['Name']for v in d['blocks']if d['palette'][v['state']]['Name']not in AIR}
hc=cells(house);bc=cells(b);joined={};origin=(-12,0,0)
for (x,y,z),n in hc.items():joined[(x+12,y,z)]=n
for (x,y,z),n in bc.items():
 q=(x+shift[0]+12,y,z+shift[2]);assert q not in joined;joined[q]=n
im=Image.new('RGB',(1520,680),'#edf0f2')
for i in range(2):im.paste(iso(joined,[28,25,28],i,'296 source house + stair approach; unrotated derived placement',None),(760*i,0))
im.save(P/'house-bridge-context.png')
im=Image.new('RGB',(1540,600),'#edf0f2');dr=ImageDraw.Draw(im);m={tuple(v['pos']):b['palette'][v['state']]for v in b['blocks']};step=24
for y in range(7):
 ox=30+380*(y%4);oy=45+280*(y//4);dr.text((ox,oy-22),f'bridge y{y}; whiteAIR blackOMITTED',fill='black')
 for x in range(12):
  for z in range(5):
   s=m.get((x,y,z));n=s['Name']if s else None;c='#151a24'if n is None else'#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#aab1b7')
 for x in range(12):dr.text((ox+x*step,oy-12),str(x),fill='black')
 for z in range(5):dr.text((ox-18,oy+z*step),str(z),fill='black')
im.save(P/'bridge-seven-layers.png')
v=dict(house_connector=dict(pos=[0,0,18],orientation='west_up',name='minecraft:part_0',target='minecraft:part_1'),bridge_connector=dict(pos=[11,0,2],orientation='east_up',name='minecraft:part_1',target='minecraft:part_0'),derivation='house connector + west unit - bridge connector = (-12,0,16); opposite fronts/up tops match without rotation; original source states unchanged.',bridge_origin_in_house_axes=list(shift),render_origin=list(origin),whole_render_size=[28,25,28],same_whole_building_reference_maximum=1,components_extra_credit=0,engine_executed=False,limit='Only explicit one-hop original bridge option, not random pool generation or a house network. The bridge has one attaching socket, not a second exit socket. Rigid boxes disjoint; connector compatibility and source floor probes do not certify engine collision or world ground.')
(P/'bridge-placement-derivation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
rows=[]
for x in range(6,12):
 for z in (1,2,3):
  for y in (5,6):rows.append(dict(pos=[x,y,z],state=m.get((x,y,z),'OMITTED')))
(P/'bridge-upper-walk-probes.json').write_text(json.dumps(dict(cells=rows,count=len(rows)),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(bridge_counts=dict(stored=len(b['blocks']),nonair=len(bc),omitted=420-len(b['blocks']),palette=len(b['palette']),entities=len(b.get('entities',[]))),upper_walk=rows),ensure_ascii=False))
