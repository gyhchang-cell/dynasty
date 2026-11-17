import json,sys
from pathlib import Path
from collections import Counter
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[2];sys.path.insert(0,str(R/'tools/architecture'))
from whole_building_candidates import AIR,color,iso
def ld(n):return json.loads((P/n).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
parts=[ld('F01-original.json'),ld('F02-original.json')]
raw=[]
for d in parts:raw.append({tuple(b['pos']):dict(state=d['palette'][b['state']],**({'nbt':b['nbt']}if 'nbt'in b else {}))for b in d['blocks']})
js=[[dict(pos=list(p),**b)for p,b in r.items()if b['state']['Name']=='minecraft:jigsaw']for r in raw]
parent,child=js[0][0],js[1][0]
assert parent['state']['Properties']['orientation']=='down_west' and child['state']['Properties']['orientation']=='up_west'
assert parent['nbt']['joint']=='aligned' and parent['nbt']['target']==child['nbt']['name']=='minecraft:connector'
delta=tuple(parent['pos'][i]+(0,-1,0)[i]-child['pos'][i]for i in range(3));assert delta==(-17,-48,2)
assembled=dict(raw[0]);over=[]
for p,b in raw[1].items():
 q=tuple(p[i]+delta[i]for i in range(3))
 if q in assembled:over.append(q)
 assembled[q]=b
assert not over
put('assembly-interface.json',dict(parent=parent,child=child,rotation_degrees=0,child_origin_relative_to_parent=list(delta),horizontal_same_top_west_and_opposite_vertical_front=True,connector_target_name_match=True,no_stored_position_overlaps=True,stored_positions=len(assembled),derivation='parent(4,0,6)+(0,-1,0)-child(21,47,4)=(-17,-48,2); fixed rigid pool, no terrain or processor/native execution',new_whole_credit=0,complete_native_placement_verified=False))
sets=[]
for i,(d,r) in enumerate(zip(parts,raw),1):sets.append((f'F{i:02d}',d['size'],r))
# The composite view replaces ONLY the two connector markers by their literal final state.
rr={}
for p,b in assembled.items():
 q=(p[0]+17,p[1]+48,p[2]);state=b['state']
 if state['Name']=='minecraft:jigsaw':state={'Name':b['nbt']['final_state']}
 rr[q]=dict(state=state)
sets.append(('assembly',[26,58,47],rr))
for ident,size,r in sets:
 cells={p:b['state']['Name']for p,b in r.items()if b['state']['Name']not in AIR}
 im=Image.new('RGB',(1520,680));im.paste(iso(cells,size,0,ident+' complete stored nonair'),(0,0));im.paste(iso(cells,size,1,ident+' quarter turn'),(760,0));im.save(P/(ident+'-whole.png'))
 if ident!='assembly':
  for start in range(0,size[1],4):
   im=Image.new('RGB',(1520,1400),'#edf0f2');dr=ImageDraw.Draw(im)
   for k in range(4):
    y=start+k;ox=(k%2)*760+60;oy=(k//2)*700+45;step=min(24,610/size[2],620/size[0])
    dr.text((ox,oy-28),f'{ident} y={y}; WHITE explicit air / BLACK omitted; +X right +Z down',fill='black')
    if y>=size[1]:dr.text((ox,oy),'OUTSIDE DECLARED TEMPLATE',fill='black');continue
    for z in range(size[2]):
     for x in range(size[0]):
      b=r.get((x,y,z));n=b['state']['Name']if b else None;c='#151a24'if n is None else '#ffffff'if n in AIR else color(n)
      dr.rectangle((ox+x*step,oy+z*step,ox+(x+1)*step,oy+(z+1)*step),fill=c,outline='#a9afb5')
    for x in range(0,size[0],5):dr.text((ox+x*step,oy-14),str(x),fill='black')
    for z in range(0,size[2],5):dr.text((ox-23,oy+z*step),str(z),fill='black')
   im.save(P/f'{ident}-layers-{start:02d}-{min(start+3,size[1]-1):02d}.png')
  counts=[]
  for y in range(size[1]):
   c=Counter('unknown'if(x,y,z)not in r else 'air'if r[x,y,z]['state']['Name']in AIR else 'nonair'for z in range(size[2])for x in range(size[0]));counts.append(dict(y=y,**c))
  put(ident+'-layer-counts.json',counts)
# Remove upper layers only, retaining original coordinates and omitted terrain.
for ident,size,r in [sets[1],sets[2]]:
 for cut in ([3,7]if ident=='F02'else[5,48]):
  cells={p:b['state']['Name']for p,b in r.items()if b['state']['Name']not in AIR}
  im=Image.new('RGB',(1520,680));im.paste(iso(cells,size,0,f'{ident} cut y<={cut}',cut),(0,0));im.paste(iso(cells,size,1,'quarter turn cut',cut),(760,0));im.save(P/f'{ident}-cut-{cut:02d}.png')
print('ASSEMBLY',delta,'PNG',len(list(P.glob('*.png'))))
print('F02_LAYER_COUNTS',ld('F02-layer-counts.json'))
