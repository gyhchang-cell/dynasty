#!/usr/bin/env python3
"""Original hollow oath shrine fused to a skeletal horse; then a two-rocker iron shrine.
Inspected Twilight Minoshroom's independent quadruped body/charge and KnightPhantom's
empty-armour visibility. No humanoid mesh, imported asset or copied animation.
"""
from pathlib import Path
import ast,json,math,importlib.util,copy
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'src/main/resources/assets/dynasty';ID='gongsun_wuwang'
COLORS={'iron':'#313D40','bone':'#CEBD96','oath':'#73454B','white':'#FFFFFF'}
UV={'iron':[3,3],'bone':[9,3],'oath':[3,9],'white':[9,9]};bones=[]
src=(ROOT/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(src).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','geo','write'):exec(ast.get_source_segment(src,n).replace('blueprint/elite','blueprint/boss'),globals())
sp=importlib.util.spec_from_file_location('actual_marshal_geometry',ROOT/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
def keys(rows):
 d=[(str(float(round(t,4))),[round(float(x),6) for x in v]) for t,v in rows]
 return {t:v for i,(t,v) in enumerate(d) if i in (0,len(d)-1) or v!=d[i-1][1] or v!=d[i+1][1]}
horse_source=[];horse_rest={}
for stage in (1,2):
 bones=[];bone('root');baseY=33 if stage==1 else 17;shrine=bone('oath_shrine','root',(0,baseY,0))
 # An open rectangular reliquary is the commander body, not head/chest/waist.
 for o,s in [((-14,baseY,-12),(28,3,24)),((-14,baseY,9),(28,23,3)),((-14,baseY,-12),(4,23,24)),((10,baseY,-12),(4,23,24)),((-14,baseY+20,-12),(28,3,24))]:cube(shrine,o,s,'iron')
 heart=bone('empty_oath_cavity','oath_shrine',(0,baseY+9,0));cube(heart,(-6,baseY+5,4),(12,12,3),'oath')
 # Two separate castle merlons and an inset blind mask keep the general's war identity.
 for x in (-10,6):cube(shrine,(x,baseY+23,-7),(4,4.8,14),'iron')
 mask=bone('blind_visor_hinge','oath_shrine',(0,baseY+17,-12))
 for o,s in [((-10,baseY+5,-15),(20,6,3)),((-10,baseY+15,-15),(20,7,3)),((-10,baseY+11,-15),(3,4,3)),((7,baseY+11,-15),(3,4,3)),((-2,baseY+11,-15),(4,4,3))]:cube(mask,o,s,'bone')
 for x in (-12,10):cube(shrine,(x,baseY+1,-13),(2,19,3),'oath')
 # A real bearing carries a two-clamp cutting yoke. The blade is gripped by both clamps.
 bearing=bone('glaive_bearing','oath_shrine',(0,baseY+10,-10));cube(bearing,(-6,baseY+6,-17),(12,8,9),'iron')
 yoke=bone('two_grip_yoke','glaive_bearing',(0,baseY+10,-18))
 for x in (-9,6):
  cube(yoke,(x,baseY+4,-20),(3,18,4),'iron');cube(yoke,(x-2,baseY+19,-20),(7,3,4),'bone')
 for y,sign in ((baseY+9,-1),(baseY+19,1)):
  cube(yoke,((-6 if sign<0 else 2),y,-20),(4,3,4),'iron');cube(yoke,(-3,y,-22),(6,3,2),'bone')
 #64u overall weapon length, with actual pole and broad stepped double cutting edge.
 weapon=bone('four_metre_glaive','two_grip_yoke',(0,baseY+12,-18))
 cube(weapon,(-2,baseY-4,-20),(4,52,4),'bone')
 for x in (-7,3):cube(weapon,(x,baseY+28,-21),(4,28,6),'iron')
 cube(weapon,(-5,baseY+48,-21),(10,12,6),'iron');cube(weapon,(-3,baseY+26,-22),(6,10,8),'oath')
 # Six two-joint mourning strips emerge from the shrine's back rim.
 for i in range(6):
  x=-12+i*4;top=bone('mourning_strip_'+str(i),'oath_shrine',(x,baseY+21,12));cube(top,(x,baseY+7,11),(3,14,2),'oath')
  tip=bone('mourning_tip_'+str(i),top['name'],(x,baseY+7,12));cube(tip,(x,baseY-7,11),(3,14,2),'iron')
 HIP={};REST={};L=14.
 if stage==1:
  horse=bone('bone_horse','root',(0,26,3))
  cube(horse,(-3,31,-22),(6,5,45),'iron')
  # Four coarse open rib arches, jointed shoulders and pelvis; no solid cow-shaped box.
  for z in (-15,-5,5,15):
   for o,s in [((-11,25,z-2),(4,10,4)),((7,25,z-2),(4,10,4)),((-8,33,z-2),(16,3,4))]:cube(horse,o,s,'bone')
  for z in (-19,18):cube(horse,(-13,22,z-3),(26,9,6),'iron')
  neck=bone('horse_neck_base','bone_horse',(0,32,-19));cube(neck,(-5,31,-31),(10,12,16),'bone')
  upper=bone('horse_neck_upper','horse_neck_base',(0,41,-29));cube(upper,(-5,39,-39),(10,11,13),'iron')
  skull=bone('horse_skull','horse_neck_upper',(0,48,-36));cube(skull,(-6,45,-51),(12,10,20),'bone');cube(skull,(-5,44,-56),(10,7,10),'iron')
  jaw=bone('horse_lower_jaw','horse_skull',(0,45,-36));cube(jaw,(-5,42,-54),(10,4,19),'bone')
  for x in (-5,2):cube(skull,(x,54,-39),(3,4,5),'iron')
  tail=bone('horse_chain_tail','bone_horse',(0,30,24));cube(tail,(-2,17,22),(4,15,4),'iron')
  for n,x,z in [('front_left',10,-19),('front_right',-10,-19),('rear_left',10,19),('rear_right',-10,19)]:
   HIP[n]=np.array([x,25,z],float);REST[n]=np.array([x*1.25,4,z],float)
   upper=bone(n+'_upper','bone_horse',HIP[n]);cube(upper,(x-2.5,25-L,z-2.5),(5,L,5),'iron')
   shin=bone(n+'_shin',upper['name'],(x,25-L,z));cube(shin,(x-2,25-2*L,z-2),(4,L,4),'bone')
   foot=bone(n+'_hoof','root',REST[n]);cube(foot,(REST[n][0]-4,0,z-5),(8,5,10),'iron');cube(foot,(REST[n][0]-3,3,z-6),(6,3,4),'bone')
 else:
  # Two massive rocker rails form a stalking gate. No normal thighs, knees or feet.
  for sign in (-1,1):
   rail=bone(('left' if sign>0 else 'right')+'_rocker','root',(sign*16,0,0))
   cube(rail,(sign*16-5,0,-18),(10,5,36),'iron');cube(rail,(sign*16-3,4,-10),(6,11,20),'bone')
   cube(rail,(sign*16-6,13,-8),(12,6,16),'iron')
 if stage==2:
  for old in horse_source:
   b=copy.deepcopy(old);b['name']='old_'+b['name'];b['parent']='old_'+b['parent'] if b.get('parent') not in (None,'root') else 'root';bones.append(b)
 anims={}
 def animation(name,length,loop=False):
  d={'animation_length':length,'bones':{}}
  if loop:d['loop']=True
  anims['animation.'+ID+'.'+name]=d;return d['bones']
 def supports(a,length,walk=False,rear=False):
  if stage==1:
   rows={n:[] for n in HIP};knees={n:[] for n in HIP};feet={n:[] for n in HIP}
   for t in np.linspace(0,length,round(length*100)+1):
    for i,n in enumerate(HIP):
     end=REST[n].copy();u=(float(t)/length-i/4)%1
     if walk:
      envelope=max(0,min(1,(float(t)-1)/.2,(3.4-float(t))/.2)) if name=='trample' else 1
      end[1]+=(max(0,math.sin(u*math.pi*4))*2 if u<.25 else 0)*envelope;end[2]+=(-3+24*u if u<.25 else 3-8*(u-.25))*envelope
     if rear and n.startswith('front'):end[1]+=math.sin(min(1,t/length)*math.pi)*7
     dx,dy,dz=end-HIP[n];rad=math.sqrt(dx*dx+dy*dy+dz*dz);alpha=math.acos(rad/(2*L));theta=math.atan2(math.hypot(dx,dz),-dy)+alpha;phi=math.atan2(dx,dz)
     rows[n].append((float(t),[math.degrees(theta),math.degrees(phi),0]));knees[n].append((float(t),[-math.degrees(2*alpha),0,0]));feet[n].append((float(t),end-REST[n]))
   for n in HIP:a[n+'_upper']={'rotation':keys(rows[n])};a[n+'_shin']={'rotation':keys(knees[n])};a[n+'_hoof']={'position':keys(feet[n])}
  else:
   for i,n in enumerate(('left_rocker','right_rocker')):
    a[n]={'position':keys([(0,[0,0,0]),(length/4,[0,0,-2 if i else 2]),(length/2,[0,0,0]),(3*length/4,[0,0,2 if i else -2]),(length,[0,0,0])]) if walk else [0,0,0]}
 def cloak(a,length):
  for i in range(6):
   for p in ('mourning_strip_','mourning_tip_'):a[p+str(i)]={'rotation':keys([(0,[0,0,0]),(length/4,[8+(i%2)*3,0,0]),(length/2,[0,0,0]),(3*length/4,[-6,0,0]),(length,[0,0,0])])}
 for name,length,loop in [('idle',3,True),('walk',2.4,True),('intro',9,False),('trample',4,False),('slash',3,False),('listen',5,False),('arrows',4,False),('morph',3,False),('onslaught',4.4,False),('storm',8,False),('hurt',.5,False),('death',12,False)]:
  a=animation(name,length,loop);supports(a,length,name in ('walk','trample','onslaught'),name=='intro');cloak(a,length)
  a['glaive_bearing']={'rotation':[0,0,0]};a['two_grip_yoke']={'rotation':[0,0,0]}
  if name in ('slash','onslaught'):
   rows=[(0,[0,-70,0])]
   for i in range(1 if name=='slash' else 7):
    t=(16+i*8)/20;rows.extend([(max(0,t-.1),[0,-70,0]),(t,[0,0,0]),(t+.1,[0,70,0])])
   rows.append((length,[0,0,0]));a['glaive_bearing']['rotation']=keys(rows);a['two_grip_yoke']['rotation']=keys([(0,[0,0,0]),(.7,[120 if stage==1 else 100,0,0]),(length-.4,[120 if stage==1 else 100,0,0]),(length,[0,0,0])])
  if name=='listen':a['blind_visor_hinge']={'rotation':keys([(0,[0,0,0]),(1,[12,0,0]),(4,[12,0,0]),(5,[0,0,0])])}
  if name=='arrows':a['glaive_bearing']['rotation']=keys([(0,[0,0,0]),(1.2,[-25,0,0]),(2,[-25,0,0]),(4,[0,0,0])])
  if name=='storm':a['two_grip_yoke']['position']=keys([(0,[0,0,0]),(1.2,[0,0,12]),(6.4,[0,0,12]),(8,[0,0,0])])
  if name=='hurt':a['oath_shrine']={'rotation':keys([(0,[0,0,0]),(.15,[0,5,0]),(.5,[0,0,0])])}
  if name=='death':
   # The coffin drops to ground while the horse dissolves; debris shrinks at floor pivots.
   a['oath_shrine']={'position':keys([(0,[0,0,0]),(2,[0,-baseY,0]),(7,[0,-baseY,0]),(10,[0,-baseY,0]),(12,[0,-baseY,0])]),'scale':keys([(0,[1,1,1]),(7,[1,1,1]),(10,[0,0,0]),(12,[0,0,0])])}
   a['two_grip_yoke']['scale']=keys([(0,[1,1,1]),(2,[1,1,1]),(7,[0,0,0]),(12,[0,0,0])])
   a['two_grip_yoke']['position']=keys([(0,[0,0,0]),(2,[0,4,0]),(12,[0,4,0])])
   for i in range(6):a['mourning_strip_'+str(i)]['scale']=keys([(0,[1,1,1]),(2,[0,0,0]),(12,[0,0,0])])
   if stage==1:
    a['bone_horse']={'scale':keys([(0,[1,1,1]),(2,[0,0,0]),(12,[0,0,0])])}
    for n in HIP:a[n+'_hoof']['position']=keys([(0,[0,0,0]),(2,[0,-4,0]),(12,[0,-4,0])]);a[n+'_hoof']['scale']=keys([(0,[1,1,1]),(2,[0,0,0]),(12,[0,0,0])])
   else:
    for n in ('left_rocker','right_rocker'):a[n]['scale']=keys([(0,[1,1,1]),(2,[1,1,1]),(7,[0,0,0]),(12,[0,0,0])])
 if stage==1:
  horse_source=[copy.deepcopy(b) for b in bones if b['name']=='bone_horse' or b['name'].startswith(('horse_','front_','rear_'))];horse_rest=copy.deepcopy(anims['animation.'+ID+'.idle']['bones'])
 else:
  for name,definition in anims.items():
   a=definition['bones'];length=definition['animation_length'];morph=name.endswith('.morph')
   for b in horse_source:
    key='old_'+b['name'];a[key]=copy.deepcopy(horse_rest.get(b['name'],{}))
    # Invisible horse channels in short clips must not retain the3s idle timeline.
    if not morph:
     for channel,track in a[key].items():
      if isinstance(track,dict):a[key][channel]=track[min(track,key=float)]
    # Fade the whole horse with one scale, not a multiplying scale at every joint.
    if morph:
     a[key]['scale']=keys([(0,[1,1,1]),(1.5,[1,1,1]),(2.5,[0,0,0]),(3,[0,0,0])]) if b['name']=='bone_horse' or b['name'].endswith('_hoof') else [1,1,1]
     if b['name']=='bone_horse':a[key]['position']=keys([(0,[0,0,0]),(1.5,[0,0,0]),(2.5,[0,-26,-3]),(3,[0,-26,-3])])
     if b['name'].endswith('_hoof'):
      v=-np.array(b['pivot'],float);a[key]['position']=keys([(0,[0,0,0]),(1.5,[0,0,0]),(2.5,v),(3,v)])
    else:a[key]['scale']=[0,0,0]
   if morph:
    a['oath_shrine']={'position':keys([(float(t),[0,max(baseY,33*max(0,min(1,(2.5-float(t))))) -baseY,0]) for t in np.linspace(0,3,301)])}
    for n in ('left_rocker','right_rocker'):a[n]['scale']=keys([(0,[0,0,0]),(1.5,[0,0,0]),(2,[1,1,1]),(3,[1,1,1])])
 ident=ID if stage==1 else ID+'_foot';geo(ident,bones,16,14,[0,6,0]);write(A/f'animations/blueprint/boss/{ident}.animation.json',{'format_version':'1.8.0','animations':anims})
 im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
 for col,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill=COLORS[col])
 im.save(A/f'textures/entity/blueprint/boss/{ident}.png')
 print(ident,len(bones),'bones',sum(len(b.get('cubes',[])) for b in bones),'cubes',len(anims),'clips',flush=True)
# Three independent runtime effects, all sampled from this actual16px palette.
for identifier in ('marshal_sand_blade','marshal_wall_arrow','marshal_blood_fissure'):
 bones=[];b=bone('root')
 if identifier.endswith('sand_blade'):
  cube(b,(-9,-6.5,-3),(18,13,6),'oath');cube(b,(-7,-2.5,-4),(14,7,8),'bone');cube(b,(-2,-5.5,-5),(4,11,10),'iron')
 elif identifier.endswith('wall_arrow'):
  cube(b,(-1,-20,-1),(2,17,2),'bone');cube(b,(-3,-5,-2),(6,5,4),'iron');cube(b,(-4,-18,-1),(8,4,2),'oath')
 else:
  cube(b,(-10,0,-10),(20,2,20),'iron');cube(b,(-8,1,-8),(16,5,16),'oath');cube(b,(-3,4,-3),(6,7,6),'bone')
 geo(identifier,bones,3,3,[0,1,0]);write(A/f'animations/blueprint/boss/{identifier}.animation.json',{'format_version':'1.8.0','animations':{'animation.'+identifier+'.idle':{'animation_length':1,'loop':True,'bones':{'root':{'scale':keys([(0,[1,1,1]),(.5,[1,1,1]),(1,[1,1,1])])}}}}})
for identifier in ('marshal_broken_horse_cleaver','marshal_broken_wing_helmet','marshal_last_city_oath'):
 im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
 if identifier.endswith('cleaver'):
  d.rectangle((6,2,9,13),fill=COLORS['bone']);d.rectangle((4,2,11,7),fill=COLORS['iron']);d.rectangle((6,8,9,11),fill=COLORS['oath'])
 elif identifier.endswith('helmet'):
  d.rectangle((4,4,11,11),fill=COLORS['iron']);d.rectangle((2,2,5,7),fill=COLORS['iron']);d.rectangle((10,2,13,7),fill=COLORS['iron']);d.rectangle((6,6,9,9),fill=COLORS['bone']);d.rectangle((6,10,9,13),fill=COLORS['oath'])
 else:
  d.rectangle((3,2,12,13),fill=COLORS['bone']);d.rectangle((3,2,4,13),fill=COLORS['iron']);d.rectangle((7,4,10,7),fill=COLORS['oath']);d.rectangle((7,10,10,11),fill=COLORS['iron'])
 im.save(A/f'textures/item/{identifier}.png');write(A/f'models/item/{identifier}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+identifier}})
write(A/f'models/item/{ID}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
write(A/'models/block/marshal_oath_socket.json',{'textures':{'all':'dynasty:entity/blueprint/boss/'+ID,'particle':'dynasty:entity/blueprint/boss/'+ID},'elements':[{'from':[0,0,0],'to':[16,16,16],'faces':{f:{'uv':[3,9,7,13],'texture':'#all'} for f in ('north','south','west','east','up','down')}}]})
write(A/'blockstates/marshal_oath_socket.json',{'variants':{'':{'model':'dynasty:block/marshal_oath_socket'}}})
write(A/'models/item/marshal_oath_socket.json',{'parent':'dynasty:block/marshal_oath_socket'})

# Final actor material stage. The original16px PNG remains authoritative for
# the three projectile effects and socket block; actor-only atlases are separate.
import sys as _marshal_sys
_marshal_sys.path.insert(0,str(ROOT/'tools/art/bestiary-v43'))
from marshal_materials import export_materials as _marshal_export_materials
_marshal_export_materials(A)

# Approved inventory transparency: preserve entity atlases.
import runpy as _inventory_runpy
from pathlib import Path as _InventoryPath
_inventory_runpy.run_path(str(_InventoryPath(__file__).resolve().parents[1]/"art/inventory-refresh/transparent.py"))["cleanup_white"]()
