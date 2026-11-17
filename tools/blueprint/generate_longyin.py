#!/usr/bin/env python3
"""Original2.2m blade/3m full polearm; shared held vanilla mesh and world Gecko export."""
from pathlib import Path
import ast,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty'
ID='longyin_zhanma_duanyue_dao';COLORS={'iron':'#475B69','edge':'#9DB6BE','cord':'#864E47','white':'#FFFFFF'}
UV={'iron':[3,3],'edge':[9,3],'cord':[3,9],'white':[9,9]};bones=[]
source=(R/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(source).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','geo','write'):exec(ast.get_source_segment(source,n).replace('blueprint/elite','blueprint/artifact'),globals())
root=bone('root');grip=bone('cinnabar_grip','root',(0,5,0));cube(grip,(-1,2,-1),(2,10,2),'cord')
ring=bone('closed_dragon_ring','cinnabar_grip',(0,2,0))
for o,s in [((-3,0,-1),(6,2,2)),((-3,0,-1),(2,5,2)),((1,0,-1),(2,5,2)),((-3,3,-1),(6,2,2))]:cube(ring,o,s,'iron')
guard=bone('swallow_guard','cinnabar_grip',(0,12,0));cube(guard,(-4,11,-2),(8,3,4),'iron')
for x in (-4,2):cube(guard,(x,12,-2),(2,4,4),'edge')
blade=bone('heavy_cleaver','swallow_guard',(0,14,0))
cube(blade,(-2,12.8,-1),(4,33.2,2),'iron');cube(blade,(-2,46,-1),(4,2,2),'edge')
cube(blade,(2,14.8,-1),(2,31.2,2),'edge');cube(blade,(3,16.8,-1),(1,27.2,2),'white')
# Coarse stepped dragon spine fitted to the blade, not disconnected decoration.
spine=bone('cast_dragon_spine','heavy_cleaver',(-2,18,0))
for o,s in [((-4,16,-2),(2,7,4)),((-4,22,-2),(4,4,4)),((-4,25,-2),(2,9,4)),((-4,33,-2),(4,4,4)),((-3,36,-2),(3,7,4))]:cube(spine,o,s,'iron')
geo(ID,bones,2,4,[0,1.5,0])
write(A/f'animations/blueprint/artifact/{ID}.animation.json',{'format_version':'1.8.0','animations':{'animation.'+ID+'.idle':{'animation_length':1,'loop':True,'bones':{'root':{'rotation':[0,0,0]}}}}})
im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
for color,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill=COLORS[color])
(A/'textures/entity/blueprint/artifact').mkdir(parents=True,exist_ok=True);im.save(A/f'textures/entity/blueprint/artifact/{ID}.png')
elements=[]
for b in bones:
 for c in b.get('cubes',[]):
  o=[c['origin'][0]+8,c['origin'][1]-16,c['origin'][2]+8];end=[o[i]+c['size'][i] for i in range(3)]
  elements.append({'from':o,'to':end,'faces':{face:{'uv':uv['uv']+[uv['uv'][0]+uv['uv_size'][0],uv['uv'][1]+uv['uv_size'][1]],'texture':'#all'} for face,uv in c['uv'].items()}})
write(A/f'models/item/{ID}_mesh.json',{'textures':{'all':'dynasty:entity/blueprint/artifact/'+ID,'particle':'dynasty:entity/blueprint/artifact/'+ID},'elements':elements})
display={'thirdperson_righthand':{'rotation':[0,-90,35],'translation':[0,0,0],'scale':[1,1,1]},'thirdperson_lefthand':{'rotation':[0,90,-35],'translation':[0,0,0],'scale':[1,1,1]},'firstperson_righthand':{'rotation':[0,-90,30],'translation':[1,1,1],'scale':[.55,.55,.55]},'firstperson_lefthand':{'rotation':[0,90,-30],'translation':[1,1,1],'scale':[.55,.55,.55]},'ground':{'rotation':[0,0,0],'translation':[0,3,0],'scale':[.6,.6,.6]},'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[.6,.6,.6]}}
write(A/f'models/item/{ID}.json',{'parent':'builtin/entity','display':display})
write(A/f'models/item/{ID}_icon.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+ID}})
icon=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(icon)
d.rectangle((6,8,9,13),fill=COLORS['cord']);d.rectangle((4,6,11,7),fill=COLORS['iron']);d.rectangle((4,2,9,5),fill=COLORS['iron']);d.rectangle((10,2,11,5),fill=COLORS['edge']);icon.save(A/f'textures/item/{ID}.png')
bones=[];b=bone('root');cube(b,(-12.8,0,-12.8),(25.6,4,25.6),'iron');cube(b,(-8,3,-6),(16,5,12),'edge');cube(b,(-4,7,-3),(8,5,6),'iron');geo('longyin_ground_crest',bones,4,3,[0,1,0])
soil=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(soil)
for color,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill={'iron':'#6B5748','edge':'#9A907C','cord':'#425258','white':'#FFFFFF'}[color])
soil.save(A/'textures/entity/blueprint/artifact/longyin_ground_crest.png')
write(A/'animations/blueprint/artifact/longyin_ground_crest.animation.json',{'format_version':'1.8.0','animations':{'animation.longyin_ground_crest.idle':{'animation_length':.2,'loop':True,'bones':{'root':{'scale':{'0.0':[1,.6,1],'0.1':[1,1,1],'0.2':[1,.6,1]}}}}}})
# Export-time contracts: same real cubes in the held and world models, with a fixed grip.
assert len(elements)==17
assert min(c['from'][1] for c in elements)==-16 and max(c['to'][1] for c in elements)==32
assert all(-16<=v<=32 for c in elements for k in ('from','to') for v in c[k])
assert abs((48-12.8)/16-2.2)<1e-8 and (48-0)/16==3
assert abs((5-16)/16-.5+1.1875)<1e-8
for p in (A/f'textures/entity/blueprint/artifact/{ID}.png',A/'textures/entity/blueprint/artifact/longyin_ground_crest.png',A/f'textures/item/{ID}.png'):
 im=Image.open(p).convert('RGB');assert im.size==(16,16) and len(set(im.get_flattened_data()))<=4
 for y in range(16):
  for x in range(16):
   c=im.getpixel((x,y))
   if x<2 or x>13 or y<2 or y>13:assert c==(255,255,255)
   assert any(all(im.getpixel((xx,yy))==c for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15)
print('Exported original2.2m blade/3m full polearm:6bones/17cubes; held mesh/world geo/earth crest/16px icons')

# Approved inventory transparency: preserve entity atlases.
import runpy as _inventory_runpy
from pathlib import Path as _InventoryPath
_inventory_runpy.run_path(str(_InventoryPath(__file__).resolve().parents[1]/"art/inventory-refresh/transparent.py"))["cleanup_white"]()
