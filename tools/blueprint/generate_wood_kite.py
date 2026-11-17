#!/usr/bin/env python3
"""Original9m folding rail-wing aircraft/5.5m machine bird. No borrowed geometry or humanoid rig.

Studied actual TF RavenModel wing/leg parents and Cataclysm Harbinger jetpack/hinged frames,
not their geometry or texture. Five serial slide bearings per wing, two articulated landing
claws, a real open bomb bay and four attached oil engines explain all movement.
"""
from pathlib import Path
import ast,copy,json,math
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';ID='luban_yisha'
COLORS={'wood':'#583E36','bronze':'#9B8354','core':'#624071','white':'#FFFFFF'}
UV={'wood':[3,3],'bronze':[9,3],'core':[3,9],'white':[9,9]};bones=[]
source=(R/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(source).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','geo','write'):exec(ast.get_source_segment(source,n).replace('blueprint/elite','blueprint/boss'),globals())
bone('root');frame=bone('mortise_airframe','root',(0,26,0))
# A genuinely open rectangular gearbox cage, with a keel and tied cross-beams.
for x in (-14,10):cube(frame,(x,14,-18),(4,20,48),'bronze')
for z in (-18,26):cube(frame,(-14,14,z),(28,4,4),'bronze');cube(frame,(-14,30,z),(28,4,4),'bronze')
cube(frame,(-3,18,-22),(6,6,56),'bronze')
skin=bone('redwood_hull_panels','mortise_airframe',(0,26,0))
for o,s in [((-18,20,-16),(4,16,40)),((14,20,-16),(4,16,40)),((-14,34,-16),(28,4,40)),((-14,18,22),(28,8,4))]:cube(skin,o,s,'wood')
# Four visible geared islands rotate around supported axles. Teeth remain coarse cuboids.
gears=[]
for i,(x,z) in enumerate([(-7,-5),(7,-5),(-7,15),(7,15)]):
 g=bone(f'gear_{i}','mortise_airframe',(x,26,z));gears.append(g['name']);cube(g,(x-5,25,z-3),(10,2,6),'bronze');cube(g,(x-3,25,z-5),(6,2,10),'bronze');cube(g,(x-1,19,z-1),(2,12,2),'core')
 for dx,dz in [(-6,0),(6,0),(0,-6),(0,6)]:cube(g,(x+dx-1,25,z+dz-1),(2,2,2),'bronze')
bay=bone('open_bomb_cassette','mortise_airframe',(0,14,3))
for o,s in [((-10,10,-12),(3,8,32)),((7,10,-12),(3,8,32)),((-10,10,-12),(20,4,3)),((-10,10,17),(20,4,3))]:cube(bay,o,s,'bronze')
for side,sign in [('left',1),('right',-1)]:
 hatch=bone(side+'_bomb_hatch','open_bomb_cassette',(sign*10,12,3));cube(hatch,(0 if sign>0 else -10,10,-9),(10,3,25),'wood')
neck=bone('forward_head_carriage','mortise_airframe',(0,30,-18));cube(neck,(-6,26,-28),(12,10,14),'bronze')
head=bone('eagle_tool_head','forward_head_carriage',(0,34,-27))
cube(head,(-9,28,-34),(18,16,16),'wood');cube(head,(-7,40,-33),(14,8,12),'bronze')
core=bone('forehead_thunder_core','eagle_tool_head',(0,41,-33.5));cube(core,(-4,38,-35),(8,6,3),'core')
for x in (-7,5):cube(head,(x,30,-30),(2,14,8),'bronze')
upper=bone('upper_shear_beak','eagle_tool_head',(0,33,-32));cube(upper,(-5,31,-38),(10,5,8),'white');cube(upper,(-3,30,-40),(6,3,4),'white')
lower=bone('lower_shear_beak','eagle_tool_head',(0,30,-32));cube(lower,(-4,27,-38),(8,3,8),'bronze')
for side,sign in [('left',1),('right',-1)]:
 lens=bone(side+'_focusing_lens','eagle_tool_head',(sign*9,35,-29));cube(lens,(7 if sign>0 else -11,32,-33),(4,6,8),'bronze');cube(lens,(10 if sign>0 else -12,34,-32),(2,3,5),'white')
wing_lengths=[14,13,12,11,6];wing_names={};wood_parts=['redwood_hull_panels','left_bomb_hatch','right_bomb_hatch']
for side,sign in [('left',1),('right',-1)]:
 bearing=bone(side+'_wing_bearing','mortise_airframe',(sign*16,30,2));cube(bearing,(12 if sign>0 else -20,26,-3),(8,8,10),'bronze')
 parent=bearing['name'];start=16;wing_names[side]=[]
 for i,length in enumerate(wing_lengths):
  name=f'{side}_folding_rail_{i}';rail=bone(name,parent,(sign*start,30,2));wing_names[side].append(name)
  x=start if sign>0 else -start-length
  cube(rail,(x,28,0),(length,4,4),'bronze');cube(rail,(x,27,-2),(length,2,8),'white')
  # Bearings clamp the next rail rather than leaving each feather independently floating.
  cube(rail,(sign*start-2,27,-1),(4,6,6),'bronze')
  feather=bone(f'{side}_redwood_vanes_{i}',name,(sign*(start+length*.5),30,2));wood_parts.append(feather['name'])
  for j in range(3):
   width=(length-1)/3;cx=start+j*width if sign>0 else -start-(j+1)*width
   depth=26-i*3+j*2;cube(feather,(cx,28,3),(width+.25,2,depth),'wood')
  # A bronze cutting edge survives shell loss and retains the mechanical wing outline.
  cube(rail,(x,27,6),(length,2,max(4,18-i*2)),'bronze')
  start+=length;parent=name
tails=[]
for side,sign in [('left',1),('right',-1)]:
 t=bone(side+'_tail_link','mortise_airframe',(sign*5,23,25));cube(t,(sign*5-2,21,25),(4,4,13),'bronze')
 end=bone(side+'_tail_tip',t['name'],(sign*5,23,38));cube(end,(sign*5-2,21,38),(4,4,10),'wood');tails.extend([t['name'],end['name']])
engines=[]
for i,(x,z) in enumerate([(-10,1),(10,1),(-10,18),(10,18)]):
 mount=bone(f'engine_{i}_mount','mortise_airframe',(x,34,z));cube(mount,(x-2,32,z-2),(4,8,4),'bronze')
 e=bone(f'oil_jet_{i}',mount['name'],(x,36,z));engines.append(e['name']);cube(e,(x-4,34,z-3),(8,8,10),'bronze');cube(e,(x-3,35,z+7),(6,6,4),'core');cube(e,(x-2,36,z+11),(4,4,3),'white')
leg_names=[];foot_names=[];toe_names=[]
for side,sign in [('left',1),('right',-1)]:
 x=sign*15;hip=bone(side+'_landing_upper','mortise_airframe',(x,26,4));cube(hip,(x-3,14,1),(6,12,6),'bronze')
 knee=bone(side+'_landing_lower',hip['name'],(x,14,4));cube(knee,(x-2,4,2),(4,10,4),'bronze')
 ankle=bone(side+'_four_claw_ankle',knee['name'],(x,4,4));cube(ankle,(x-4,3,0),(8,4,8),'bronze');leg_names.extend([hip['name'],knee['name']]);foot_names.append(ankle['name'])
 for i,(dx,z,direction) in enumerate([(-2,0,-1),(0,0,-1),(2,0,-1),(0,7,1)]):
  toe=bone(f'{side}_claw_{i}',ankle['name'],(x+dx,3,z));cube(toe,(x+dx-1,1,z-6 if direction<0 else z),(2,3,6),'bronze')
  tip=bone(f'{side}_claw_{i}_tip',toe['name'],(x+dx,2,z+direction*6));cube(tip,(x+dx-.8,0,z-10 if direction<0 else z+6),(1.6,2,4),'white');toe_names.extend([toe['name'],tip['name']])
original=copy.deepcopy(bones);phase2=copy.deepcopy(original)
for b in phase2:
 if b['name'] in wood_parts:b.pop('cubes',None)
 # The head remains a distinct open-sided bronze eagle tool, with no concealed human face.
 if b['name']=='eagle_tool_head':b['cubes'][0]['size']=[18,6,16];b['cubes'][0]['origin'][1]=28
geo(ID,original,24,22,[0,2,0]);geo(ID+'_metal',phase2,24,22,[0,2,0])
def texture(name,metal=False):
 im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
 for color,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill=('#4E594F' if metal and color=='wood' else COLORS[color]))
 p=A/f'textures/entity/blueprint/boss/{name}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
texture(ID);texture(ID+'_metal',True)
def key(rows):return {str(round(t/20,5)):v for t,v in rows}
def clip(name,length,loop=False,channels=None):return {'animation_length':length/20,'loop':loop,'bones':channels or {}}
def motors(length):return {name:{'rotation':key([(0,[0,0,0]),(length/2,[0,180,0]),(length,[0,360,0])])} for name in gears}
def wing_pose(rows):
 channels={}
 for side,sign in [('left',1),('right',-1)]:
  for i,name in enumerate(wing_names[side]):channels[name]={'rotation':key([(t,[0,sign*sweep*(1 if i==0 else .15),-sign*lift*(1 if i==0 else .12)]) for t,lift,sweep in rows])}
 return channels
def flight_legs(length):
 ch={}
 for side in ('left','right'):
  ch[side+'_landing_upper']={'rotation':[-48,0,0]};ch[side+'_landing_lower']={'rotation':[80,0,0]};ch[side+'_four_claw_ankle']={'rotation':[-32,0,0]}
 return ch
clips={}
clips['idle']=clip('idle',80,True,motors(80))
ch=motors(40);ch.update(wing_pose([(0,0,0),(10,8,3),(20,0,0),(30,-8,-3),(40,0,0)]));ch.update(flight_legs(40));clips['fly']=clip('fly',40,True,ch)
ch=motors(200);ch.update(wing_pose([(0,24,30),(60,24,30),(120,2,0),(160,12,0),(200,0,0)]))
for side in ('left','right'):
 ch[side+'_landing_upper']={'rotation':key([(0,[-48,0,0]),(140,[-48,0,0]),(160,[0,0,0]),(200,[0,0,0])])};ch[side+'_landing_lower']={'rotation':key([(0,[80,0,0]),(140,[80,0,0]),(160,[0,0,0]),(200,[0,0,0])])}
 ch[side+'_four_claw_ankle']={'rotation':key([(0,[-32,0,0]),(140,[-32,0,0]),(160,[0,0,0]),(200,[0,0,0])])}
clips['intro']=clip('intro',200,False,ch)
ch=motors(72);ch.update(wing_pose([(0,18,18),(24,0,0),(56,0,0),(72,18,18)]));ch.update(flight_legs(72));clips['wing_cut']=clip('wing_cut',72,False,ch)
ch=motors(104);ch.update(wing_pose([(0,0,0),(24,6,0),(84,6,0),(104,0,0)]));ch.update(flight_legs(104))
for side,sign in [('left',1),('right',-1)]:ch[side+'_bomb_hatch']={'rotation':key([(0,[0,0,0]),(24,[0,0,sign*75]),(84,[0,0,sign*75]),(104,[0,0,0])])}
clips['bombs']=clip('bombs',104,False,ch)
ch=motors(92);ch.update(wing_pose([(0,16,16),(28,24,20),(36,8,0),(48,8,0),(92,0,0)]))
for side in ('left','right'):
 ch[side+'_landing_upper']={'rotation':key([(0,[-48,0,0]),(28,[-48,0,0]),(36,[0,0,0]),(48,[0,0,0]),(92,[0,0,0])])};ch[side+'_landing_lower']={'rotation':key([(0,[80,0,0]),(28,[80,0,0]),(36,[0,0,0]),(48,[0,0,0]),(92,[0,0,0])])}
 ch[side+'_four_claw_ankle']={'rotation':key([(0,[-32,0,0]),(28,[-32,0,0]),(36,[0,0,0]),(48,[0,0,0]),(92,[0,0,0])])}
clips['claws']=clip('claws',92,False,ch)
ch=motors(120);ch.update(wing_pose([(0,0,0),(24,12,0),(40,-6,0),(56,12,0),(72,-6,0),(88,12,0),(104,-6,0),(120,0,0)]));clips['wind']=clip('wind',120,False,ch)
ch=motors(48);ch.update(wing_pose([(0,12,0),(24,24,15),(48,0,0)]));ch.update(flight_legs(48))
for name in wood_parts:ch[name]={'scale':key([(0,[1,1,1]),(24,[1,1,1]),(48,[0,0,0])])}
clips['overheat']=clip('overheat',48,False,ch)
ch=motors(112);ch.update(wing_pose([(0,16,0),(32,0,0),(48,10,0),(64,0,0),(80,10,0),(112,0,0)]));ch.update(flight_legs(112));clips['lightning']=clip('lightning',112,False,ch)
ch=motors(108);ch.update(wing_pose([(0,12,0),(36,40,30),(60,40,30),(68,0,0),(108,0,0)]))
for side in ('left','right'):
 ch[side+'_landing_upper']={'rotation':key([(0,[-48,0,0]),(60,[-48,0,0]),(68,[0,0,0]),(108,[0,0,0])])};ch[side+'_landing_lower']={'rotation':key([(0,[80,0,0]),(60,[80,0,0]),(68,[0,0,0]),(108,[0,0,0])])}
 ch[side+'_four_claw_ankle']={'rotation':key([(0,[-32,0,0]),(60,[-32,0,0]),(68,[0,0,0]),(108,[0,0,0])])}
clips['meteor']=clip('meteor',108,False,ch)
ch=motors(40);ch.update(wing_pose([(0,18,20),(40,18,20)]));clips['stun']=clip('stun',40,True,ch)
ch=motors(220);ch['root']={'rotation':key([(0,[0,0,0]),(40,[20,0,30]),(80,[50,0,65]),(160,[70,0,100]),(220,[70,0,100])]),'scale':key([(0,[1,1,1]),(160,[1,1,1]),(220,[0,0,0])])};ch.update(wing_pose([(0,0,0),(40,30,15),(80,50,35),(160,50,35),(220,50,35)]));clips['death']=clip('death',220,False,ch)
for name in tails:
 for cname,data in clips.items():
  if cname in ('idle','fly'):data['bones'][name]={'rotation':key([(0,[0,0,0]),(data['animation_length']*5,[5,0,0]),(data['animation_length']*10,[0,0,0]),(data['animation_length']*15,[-5,0,0]),(data['animation_length']*20,[0,0,0])])}
for cname,data in clips.items():
 length=data['animation_length']*20
 if cname!='death':data['bones']['forehead_thunder_core']={'scale':key([(0,[1,1,1]),(length*.25,[1.08,1.08,1.08]),(length*.5,[1,1,1]),(length*.75,[1.08,1.08,1.08]),(length,[1,1,1])])}
 if cname in ('intro','wind','lightning'):
  data['bones']['lower_shear_beak']={'rotation':key([(0,[0,0,0]),(length*.25,[24,0,0]),(length*.75,[24,0,0]),(length,[0,0,0])])}
  for name in engines:data['bones'][name]={'rotation':key([(0,[0,0,0]),(length*.25,[-8,0,0]),(length*.75,[-8,0,0]),(length,[0,0,0])])}
for identifier in (ID,ID+'_metal'):write(A/f'animations/blueprint/boss/{identifier}.animation.json',{'format_version':'1.8.0','animations':{'animation.'+ID+'.'+name:value for name,value in clips.items()}})
# A slow wooden bomb's small body and its resting fuse have their own geometry.
bones=[];b=bone('root');cube(b,(-4,0,-4),(8,8,8),'wood');cube(b,(-5,3,-5),(10,2,10),'bronze');cube(b,(-1,8,-1),(2,3,2),'core');geo('wood_kite_thunder_bomb',bones,2,2,[0,.5,0]);texture('wood_kite_thunder_bomb');write(A/'animations/blueprint/boss/wood_kite_thunder_bomb.animation.json',{'format_version':'1.8.0','animations':{'animation.wood_kite_thunder_bomb.idle':clip('idle',40,True,{'root':{'rotation':key([(0,[0,0,0]),(20,[0,180,0]),(40,[0,360,0])])}}),'animation.wood_kite_thunder_bomb.rest':clip('rest',1,False,{})}})
assert max(c['origin'][2]+c['size'][2] for b in original for c in b.get('cubes',[]))-min(c['origin'][2] for b in original for c in b.get('cubes',[]))==88
assert max(c['origin'][0]+c['size'][0] for b in original for c in b.get('cubes',[]))-min(c['origin'][0] for b in original for c in b.get('cubes',[]))==144
for identifier in (ID,ID+'_metal','wood_kite_thunder_bomb'):
 im=Image.open(A/f'textures/entity/blueprint/boss/{identifier}.png').convert('RGB');assert im.size==(16,16) and len(set(im.get_flattened_data()))<=4
 for y in range(16):
  for x in range(16):
   color=im.getpixel((x,y));assert 2<=x<=13 and 2<=y<=13 or color==(255,255,255)
   assert any(all(im.getpixel((xx,yy))==color for xx in (sx,sx+1) for yy in (sy,sy+1)) for sx in (x-1,x) for sy in (y-1,y) if 0<=sx<15 and 0<=sy<15)
print('Exported original9m x5.5m serial-wing aircraft:',len(original),'bones',sum(len(b.get('cubes',[])) for b in original),'wood and',sum(len(b.get('cubes',[])) for b in phase2),'metal cuboids;',len(clips),'clips each')
# Final, authoritative UV/material pass for the two existing actor forms. The
# bomb keeps its separate legacy atlas. Exporting must not restore flat colours.
import importlib.util
_material_path=R/'tools/art/bestiary-v43/wood_kite_materials.py'
_material_spec=importlib.util.spec_from_file_location('wood_kite_materials',_material_path)
_material_module=importlib.util.module_from_spec(_material_spec);_material_spec.loader.exec_module(_material_module)
_material_module.export_materials(A)
