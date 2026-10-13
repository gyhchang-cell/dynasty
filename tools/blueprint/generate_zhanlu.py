#!/usr/bin/env python3
"""Original1.4m sword: real eight-faced cuboid bevels, plain stepped bronze disc, deerhide grip."""
from pathlib import Path
import ast,json,math
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'src/main/resources/data/dynasty'
ID='zhanlu_rendao_bamian_jian';COLORS={'jade':'#253F3C','bronze':'#817650','hide':'#7A5440','white':'#FFFFFF'}
UV={'jade':[3,3],'bronze':[9,3],'hide':[3,9],'white':[9,9]};bones=[]
source=(R/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(source).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','geo','write'):exec(ast.get_source_segment(source,n).replace('blueprint/elite','blueprint/artifact'),globals())
bone('root');pommel=bone('bronze_pommel','root',(0,1,0));cube(pommel,(-1.2,0,-1.2),(2.4,1.6,2.4),'bronze')
grip=bone('deerhide_grip','bronze_pommel',(0,3,0));cube(grip,(-.8,1.4,-.8),(1.6,4.8,1.6),'hide')
for y in (1.4,3,4.6):cube(grip,(-1,y,-1),(2,.5,2),'hide')
guard=bone('plain_bronze_disc','deerhide_grip',(0,6.8,0))
cube(guard,(-3.5,6.2,-2.5),(7,1.4,5),'bronze');cube(guard,(-2.5,6.2,-3.5),(5,1.4,7),'bronze')
blade=bone('eight_facet_jade_core','plain_bronze_disc',(0,7.3,0))
cube(blade,(-1.5,7.3,-1),(3,13.1,2),'jade');cube(blade,(-2,7.3,-.5),(4,13.1,1),'jade')
# A square diamond at each of four corners completes the exact eight-faced octagonal section.
q=math.sqrt(.5)
for x in (-1.5,1.5):
 for z in (-.5,.5):
  facet=bone(('west' if x<0 else 'east')+('_front_bevel' if z<0 else '_back_bevel'),'eight_facet_jade_core',(x,7.3,z))
  cube(facet,(x-q/2,7.3,z-q/2),(q,13.1,q),'jade',(0,45,0))
tip=bone('stepped_jade_point','eight_facet_jade_core',(0,20.4,0));cube(tip,(-1,20.4,-.7),(2,1,.7*2),'jade');cube(tip,(-.65,21.4,-.5),(1.3,1,1),'jade')
geo(ID,bones,2,3,[0,.7,0]);write(A/f'animations/blueprint/artifact/{ID}.animation.json',{'format_version':'1.8.0','animations':{'animation.'+ID+'.idle':{'animation_length':1,'loop':True,'bones':{'root':{'rotation':[0,0,0]}}}}})
def texture(identifier,palette):
 im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
 for c,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill=palette[c])
 p=A/f'textures/entity/blueprint/artifact/{identifier}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
texture(ID,COLORS);elements=[]
for b in bones:
 for c in b.get('cubes',[]):
  o=[c['origin'][0]+8,c['origin'][1]+5,c['origin'][2]+8];end=[o[i]+c['size'][i] for i in range(3)]
  element={'from':o,'to':end,'faces':{f:{'uv':u['uv']+[u['uv'][0]+u['uv_size'][0],u['uv'][1]+u['uv_size'][1]],'texture':'#all'} for f,u in c['uv'].items()}}
  if c.get('rotation'):element['rotation']={'origin':[c['pivot'][0]+8,c['pivot'][1]+5,c['pivot'][2]+8],'axis':'y','angle':-45,'rescale':False}
  elements.append(element)
write(A/f'models/item/{ID}_mesh.json',{'textures':{'all':'dynasty:entity/blueprint/artifact/'+ID,'particle':'dynasty:entity/blueprint/artifact/'+ID},'elements':elements})
display={k:{'rotation':[0,-90 if 'righthand' in k else 90,0],'translation':[0,0,0],'scale':[1,1,1]} for k in ('thirdperson_righthand','thirdperson_lefthand','firstperson_righthand','firstperson_lefthand')}
display.update({'ground':{'rotation':[0,0,0],'translation':[0,3,0],'scale':[.7,.7,.7]},'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[.7,.7,.7]}})
write(A/f'models/item/{ID}.json',{'parent':'builtin/entity','display':display});write(A/f'models/item/{ID}_icon.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+ID}})
im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im);d.rectangle((6,2,9,9),fill=COLORS['jade']);d.rectangle((4,10,11,11),fill=COLORS['bronze']);d.rectangle((6,12,9,13),fill=COLORS['hide']);im.save(A/f'textures/item/{ID}.png')
# The field is a ground object: fixed white eight-trigram perimeter and a rotating jade Taiji core.
bones=[];bone('root');r=79*math.cos(math.pi/8);length=158*math.sin(math.pi/8)-1
for i in range(8):
 angle=i*45;boundary=bone(f'white_perimeter_{i}','root',(0,0,0))
 cube(boundary,(-length/2,0,r-1),(length,.5,2),'white',(0,angle,0))
 trigram=bone(f'white_trigram_{i}','root',(0,0,0))
 for j in range(3):
  z=58+j*3
  if ((i>>j)&1):cube(trigram,(-8,0,z),(16,.5,1.5),'white',(0,angle,0))
  else:
   for x in (-8,2):cube(trigram,(x,0,z),(6,.5,1.5),'white',(0,angle,0))
taiji=bone('rotating_jade_taiji','root',(0,0,0))
for o,s,c in [((-24,.2,-16),(24,.4,32),'jade'),((-16,.2,-24),(16,.4,8),'jade'),((-16,.2,16),(16,.4,8),'jade'),((0,.2,-16),(24,.4,32),'white'),((0,.2,-24),(16,.4,8),'white'),((0,.2,16),(16,.4,8),'white'),((-8,.65,-20),(16,.4,16),'white'),((-8,.65,4),(16,.4,16),'jade'),((-2,1.1,-14),(4,.4,4),'jade'),((-2,1.1,10),(4,.4,4),'white')]:cube(taiji,o,s,c)
geo('zhanlu_ceasefire_field',bones,11,2,[0,.5,0]);texture('zhanlu_ceasefire_field',COLORS)
write(A/'animations/blueprint/artifact/zhanlu_ceasefire_field.animation.json',{'format_version':'1.8.0','animations':{'animation.zhanlu_ceasefire_field.idle':{'animation_length':4,'loop':True,'bones':{'rotating_jade_taiji':{'rotation':{'0.0':[0,0,0],'1.0':[0,90,0],'2.0':[0,180,0],'3.0':[0,270,0],'4.0':[0,360,0]}}}}}})
write(D/'advancements/blueprint'/f'acquire_{ID}.json',{'display':{'icon':{'item':'dynasty:'+ID},'title':{'translate':'advancement.dynasty.acquire_zhanlu'},'description':{'translate':'advancement.dynasty.acquire_zhanlu.desc'},'frame':'challenge','show_toast':True,'announce_to_chat':False,'hidden':False},'criteria':{'acquired':{'trigger':'minecraft:inventory_changed','conditions':{'items':[{'items':['dynasty:'+ID]}]}}}})
assert abs(22.4/16-1.4)<1e-8 and abs((3+5)/16-.5)<1e-8
assert all(-16<=v<=32 for e in elements for key in ('from','to') for v in e[key]);assert len([e for e in elements if 'rotation' in e])==4
for p in (A/f'textures/entity/blueprint/artifact/{ID}.png',A/'textures/entity/blueprint/artifact/zhanlu_ceasefire_field.png',A/f'textures/item/{ID}.png'):
 im=Image.open(p).convert('RGB');assert im.size==(16,16) and len(set(im.get_flattened_data()))<=4
 for y in range(16):
  for x in range(16):
   c=im.getpixel((x,y));assert 2<=x<=13 and 2<=y<=13 or c==(255,255,255)
   assert any(all(im.getpixel((xx,yy))==c for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15)
print(f'Exported original1.4m eight-faced sword: {len(elements)} actual held cuboids, rotating80tick ground field, original16px four-color PNGs')
