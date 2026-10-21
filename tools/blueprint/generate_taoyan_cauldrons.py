#!/usr/bin/env python3
"""Original two-form living war cauldron. Three cast supports become eight crawling bone struts.
Actual Twilight HarbingerCube body/supports and UrGhast nested appendage code were read.
No imported geometry, no normal head/chest/waist/humanoid arms.
"""
from pathlib import Path
import ast,copy,json,math,importlib.util
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'src/main/resources/assets/dynasty';ID='taoyan_zhishi'
COLORS={'dark':'#293331','bronze':'#8C6B45','bone':'#D5C9A4','white':'#FFFFFF'};UV={'dark':[3,3],'bronze':[9,3],'bone':[3,9],'white':[9,9]};bones=[]
for n in ast.parse((ROOT/'tools/blueprint/generate_tide_yasha.py').read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','geo','write'):
  exec(ast.get_source_segment((ROOT/'tools/blueprint/generate_tide_yasha.py').read_text(),n).replace('blueprint/elite','blueprint/boss'),globals())
def keys(rows):
 data=[(str(float(round(t,4))),[round(float(x),6) for x in v]) for t,v in rows]
 return {t:v for i,(t,v) in enumerate(data) if i in (0,len(data)-1) or v!=data[i-1][1] or v!=data[i+1][1]}
spec=importlib.util.spec_from_file_location('cauldron_geometry',ROOT/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/boss'
base=np.array([0.,20.,0.]);L=14.
for stage in (1,2):
 bones=[];bone('root');v=bone('war_cauldron','root',base)
 # Genuine stepped-octagonal floor and thick walls. Open top and open frontal maw.
 for o,sz in [((-21,17,-21),(42,3,42)),((-25,17,-15),(50,3,30)),((-15,17,-25),(30,3,50))]:cube(v,o,sz,'dark')
 for o,sz in [((-25,20,-15),(4,26,30)),((21,20,-15),(4,26,30)),((-15,20,21),(30,26,4)),((-15,20,-25),(30,8,4)),((-15,43,-25),(30,3,4)),((-23,20,-23),(8,26,8)),((15,20,-23),(8,26,8)),((-23,20,15),(8,26,8)),((15,20,15),(8,26,8))]:cube(v,o,sz,'bronze')
 for o,sz in [((-26,46,-16),(5,5,32)),((21,46,-16),(5,5,32)),((-16,46,-26),(32,5,5)),((-16,46,21),(32,5,5)),((-24,46,-24),(10,5,10)),((14,46,-24),(10,5,10)),((-24,46,14),(10,5,10)),((14,46,14),(10,5,10))]:cube(v,o,sz,'bronze')
 oil=bone('boiling_oil','war_cauldron',(0,28,0));cube(oil,(-18,27,-18),(36,2,36),'dark')
 for i in range(4):cube(oil,(-13+i*8,29,-12+i*6),(5,3,8),'bone')
 mouth=bone('cauldron_maw','war_cauldron',(0,38,-25));cube(mouth,(-18,42,-32),(36,5,8),'dark')
 for sign in (-1,1):cube(mouth,(sign*16-3,29,-31),(6,16,7),'dark');cube(mouth,(sign*12-3,43,-34),(6,5,4),'bronze')
 jaw=bone('maw_lower_hinge','cauldron_maw',(0,29,-24));cube(jaw,(-18,26,-33),(36,5,10),'dark')
 # Three coarse, separated ranks of original bone teeth, never a flat painted mouth.
 for row in range(3):
  for x in (-10,0,10):cube(mouth,(x-2,36+row*2,-32+row*3),(4,6-row,3),'bone')
 for x in (-12,-4,4,12):cube(jaw,(x-2,31,-32),(4,5,4),'bone')
 # Bells hang from separate bronze yokes on the vessel rim. No shoulders/upper arms.
 for sign in (-1,1):
  n=('left' if sign>0 else 'right');yoke=bone(n+'_bell_yoke','war_cauldron',(sign*25,48,12));cube(yoke,(sign*27-4,44,6),(8,6,15),'bronze')
  bell=bone(n+'_mourning_bell',yoke['name'],(sign*29,44,12));x=sign*29
  for o,sz in [((x-5,32,6),(2,10,12)),((x+3,32,6),(2,10,12)),((x-3,32,6),(6,10,2)),((x-3,32,16),(6,10,2)),((x-5,41,6),(10,2,12))]:cube(bell,o,sz,'bronze')
  for o,sz in [((x-7,30,4),(3,3,16)),((x+4,30,4),(3,3,16)),((x-4,30,4),(8,3,3)),((x-4,30,17),(8,3,3))]:cube(bell,o,sz,'dark')
  cube(bell,(x-2,28,10),(4,11,4),'bone')
 # A socket, telescoping carriage and weighted rectangular siege point form a real cast mechanism.
 s=bone('siege_socket','war_cauldron',(-25,36,-9));cube(s,(-34.5,29.5,-16.5),(13,13,19),'bronze')
 rail=bone('siege_piston','siege_socket',(-30,36,-16));cube(rail,(-34,32,-31),(8,8,25),'dark')
 ram=bone('siege_ram','siege_piston',(-30,36,-30));cube(ram,(-38,28,-43),(16,16,22),'bronze');cube(ram,(-35,31,-49),(10,10,10),'dark');cube(ram,(-32,33,-53),(4,6,6),'bone')
 # Real bronze slide lets the bone whip lower to the attack plane without floating.
 guide=bone('whip_slide','war_cauldron',(27,39,0));cube(guide,(25,13,-3),(6,29,6),'bronze')
 # Twelve serial broad links, coiled at rest and unfolded at the attack plane.
 parent='whip_slide'
 for i in range(12):
  b=bone('bone_whip_'+str(i),parent,(27+i*6,39,0));cube(b,(27+i*6,37.5,-1.5),(6.7,3,3),'bone');cube(b,(27+i*6,37,-2),(2.4,4,4),'bronze');parent=b['name']
 # Broad rear fragments retain war identity while the vessel remains the body.
 crest=bone('war_relic_crest','war_cauldron',(0,48,14));cube(crest,(-14,48,9),(28,5,14),'dark')
 for x,y,z in [(-12,51,13),(0,53,17),(12,51,13)]:cube(crest,(x-2,y,z-2),(4,72-y,4),'bone');cube(crest,(x-4,65,z-2),(8,3,4),'bronze')
 HIP={};REST={}
 if stage==1:
  support=[('tripod_left',16,-9,22,-18),('tripod_right',-16,-9,-22,-18),('tripod_rear',0,18,0,24)]
 else:
  support=[('old_tripod_left',16,-9,22,-18),('old_tripod_right',-16,-9,-22,-18),('old_tripod_rear',0,18,0,24)]
  for i in range(8):
   a=i*math.pi/4+math.pi/8;support.append(('bone_strut_'+str(i),math.sin(a)*19,math.cos(a)*19,math.sin(a)*32,math.cos(a)*32))
 for n,x,z,fx,fz in support:
  is_cast=stage==1 or n.startswith('old_tripod');HIP[n]=np.array([x,20,z],dtype=float);REST[n]=np.array([fx,4 if is_cast else 6,fz],dtype=float);u=bone(n+'_upper','war_cauldron',HIP[n]);cube(u,(x-3,20-L,z-3),(6,L,6),'bronze' if is_cast else 'dark');lo=bone(n+'_shin',u['name'],(x,20-L,z));cube(lo,(x-2.3,20-2*L,z-2.3),(4.6,L,4.6),'dark' if is_cast else 'bone');foot=bone(n+'_foot','root',REST[n]);cube(foot,(fx-4,0,fz-4.5),(8,5 if is_cast else 7,9),'bronze' if is_cast else 'dark');cube(foot,(fx-3,1,fz-6),(6,3,4),'bone')
 ident=ID if stage==1 else ID+'_phase2';anims={}
 def anim(name,length,loop=False):
  d={'animation_length':length,'bones':{}}
  if loop:d['loop']=True
  anims['animation.'+ID+'.'+name]=d;return d['bones']
 def body_channels(a,rotrows=None,posrows=None):
  a['war_cauldron']={'rotation':keys(rotrows or [(0,[0,0,0])]),'position':keys(posrows or [(0,[0,0,0])])}
 def supports(a,length,walk=False):
  channels=a.get('war_cauldron',{});rows=[[] for _ in range(len(HIP))];knees=[[] for _ in HIP];feet=[[] for _ in HIP]
  for t in np.linspace(0,length,round(length*100)+1):
   rotation=r.sample(channels.get('rotation',[0,0,0]),float(t));position=r.sample(channels.get('position',[0,0,0]),float(t));world=r.transform(base+position,rotation);inverse=np.linalg.inv(world)
   for i,n in enumerate(HIP):
    endpoint=REST[n].copy()
    if walk:
     u=(float(t)/length-i/len(HIP))%1;slot=1/len(HIP)
     dz=-2+4*u/slot if u<slot else 2-4*(u-slot)/(1-slot);lift=math.sin(math.pi*u/slot)*2 if u<slot else 0;endpoint[1]+=lift;endpoint[2]+=dz
    local=inverse@np.r_[endpoint*[-1,1,1],1];target=np.array([-local[0],local[1]+20,local[2]]);dx,dy,dz=target-HIP[n];radius=math.sqrt(dx*dx+dy*dy+dz*dz);assert radius<2*L,(ident,n,t,radius)
    alpha=math.acos(radius/(2*L));outward=stage==2 and not n.startswith('old_tripod');theta=math.atan2(math.hypot(dx,dz),-dy)+(alpha if outward else -alpha);phi=math.atan2(dx,dz);rows[i].append((float(t),[math.degrees(theta),math.degrees(phi),0]));knees[i].append((float(t),[math.degrees(alpha*(-2 if outward else 2)),0,0]));feet[i].append((float(t),endpoint-REST[n]))
  for i,n in enumerate(HIP):a[n+'_upper']={'rotation':keys(rows[i])};a[n+'_shin']={'rotation':keys(knees[i])};a[n+'_foot']={'position':keys(feet[i])}
 def coil(a,length,unfold=False):
  for i in range(12):a['bone_whip_'+str(i)]={'rotation':keys([(0,[0,0,20]),(length,[0,0,20])])}
 a=anim('idle',3.2,True);body_channels(a);supports(a,3.2);coil(a,3.2);a['boiling_oil']={'position':keys([(0,[0,0,0]),(1.6,[0,1.2,0]),(3.2,[0,0,0])])}
 a=anim('walk',3.2,True);body_channels(a);supports(a,3.2,True);coil(a,3.2)
 for sign,n in [(1,'left'),(-1,'right')]:a[n+'_mourning_bell']={'rotation':keys([(0,[0,0,-sign*5]),(.8,[0,0,sign*5]),(1.6,[0,0,-sign*5]),(2.4,[0,0,sign*5]),(3.2,[0,0,-sign*5])])}
 a=anim('intro',8);body_channels(a);supports(a,8);coil(a,8);a['war_relic_crest']={'scale':keys([(0,[0,0,0]),(2,[0,0,0]),(5,[1,1,1]),(8,[1,1,1])])};a['maw_lower_hinge']={'rotation':keys([(0,[0,0,0]),(7,[0,0,0]),(8,[20,0,0])])};a['siege_piston']={'position':keys([(0,[0,0,12]),(5,[0,0,12]),(7,[0,0,0]),(8,[0,0,0])])}
 a=anim('ram',4.4);body_channels(a);supports(a,4.4);coil(a,4.4);a['siege_piston']={'position':keys([(0,[0,0,0]),(1,[0,0,14]),(1.05,[0,0,-4]),(1.6,[0,0,-4]),(2.6,[0,0,0]),(4.4,[0,0,0])])}
 a=anim('whip',4.4);body_channels(a);supports(a,4.4)
 for i in range(12):a['bone_whip_'+str(i)]={'rotation':keys([(0,[0,0,20]),(.4,[0,0,20]),(.8,[0,0,0]),(2.4,[0,0,0]),(2.8,[0,0,20]),(4.4,[0,0,20])])}
 a['bone_whip_0']['position']=keys([(0,[0,0,0]),(.8,[0,0,0]),(.9,[0,-24,0]),(2.4,[0,-24,0]),(2.8,[0,0,0]),(4.4,[0,0,0])]);a['bone_whip_0']['rotation']=keys([(0,[0,0,20]),(.4,[-90,0,20]),(.8,[-90,-45,0]),(.9,[-90,-45,0]),(2.35,[-90,225,0]),(2.4,[-90,225,0]),(2.8,[-90,0,20]),(3.3,[0,0,20]),(4.4,[0,0,20])])
 a=anim('oil',4.8);body_channels(a,[(0,[0,0,0]),(1.2,[15,0,0]),(1.8,[15,0,0]),(2.8,[0,0,0]),(4.8,[0,0,0])]);supports(a,4.8);coil(a,4.8);a['boiling_oil']={'position':keys([(0,[0,0,0]),(1.2,[0,0,-5]),(1.8,[0,0,-5]),(2.8,[0,0,0]),(4.8,[0,0,0])])};a['maw_lower_hinge']={'rotation':keys([(0,[0,0,0]),(1.2,[30,0,0]),(1.8,[30,0,0]),(2.8,[0,0,0]),(4.8,[0,0,0])])}
 a=anim('bells',5.0);body_channels(a);supports(a,5);coil(a,5)
 for sign,n in [(1,'left'),(-1,'right')]:a[n+'_mourning_bell']={'rotation':keys([(0,[0,0,0]),(1,[0,0,sign*22]),(1.2,[0,0,-sign*22]),(1.4,[0,0,sign*22]),(1.6,[0,0,-sign*22]),(2,[0,0,0]),(5,[0,0,0])])}
 a=anim('transition',3.2);body_channels(a);supports(a,3.2);coil(a,3.2);a['siege_socket']={'rotation':keys([(0,[0,0,0]),(1,[20,-70,0]),(2,[20,-70,0]),(3.2,[0,0,0])])};a['siege_piston']={'position':keys([(0,[0,0,0]),(1,[0,0,16]),(2,[0,0,16]),(3.2,[0,0,0])])}
 if stage==2:
  for n in HIP:
   for suffix in ('_upper','_shin','_foot'):a[n+suffix]['scale']=keys([(0,[1,1,1]),(1.2,[1,1,1]),(2.4,[0,0,0]),(3.2,[0,0,0])]) if n.startswith('old_tripod') else keys([(0,[0,0,0]),(1.2,[1,1,1]),(3.2,[1,1,1])])
 a=anim('slam',4.2);body_channels(a);supports(a,4.2);coil(a,4.2);a['siege_ram']={'rotation':keys([(0,[0,0,0]),(.8,[-35,0,0]),(1.6,[20,0,0]),(2.2,[0,0,0]),(4.2,[0,0,0])])}
 a=anim('drink',6.0);body_channels(a);supports(a,6);coil(a,6);a['maw_lower_hinge']={'rotation':keys([(0,[0,0,0]),(1.2,[35,0,0]),(4.4,[35,0,0]),(5.2,[0,0,0]),(6,[0,0,0])])};a['boiling_oil']={'position':keys([(0,[0,0,0]),(1.2,[0,-5,0]),(4.4,[0,-5,0]),(6,[0,0,0])])}
 a=anim('hurt',.5);body_channels(a,[(0,[0,0,0]),(.15,[0,4,0]),(.5,[0,0,0])]);supports(a,.5);coil(a,.5)
 a=anim('death',10);body_channels(a);supports(a,10);coil(a,10)
 for b in bones:
  if b['name']=='root' or b['name'].endswith('_foot'):continue
  if b.get('parent')=='root' or b['name'] in ('cauldron_maw','siege_ram','war_relic_crest','boiling_oil'):
   ch=a.setdefault(b['name'],{});ch['scale']=keys([(0,[1,1,1]),(2,[1,1,1]),(5,[1,.5,1]),(8,[0,0,0]),(10,[0,0,0])])
 for n in HIP:
  a[n+'_foot']['scale']=keys([(0,[1,1,1]),(4,[1,1,1]),(8,[0,0,0]),(10,[0,0,0])])
  a[n+'_foot']['position']=keys([(0,[0,0,0]),(4,[0,0,0]),(8,[0,-REST[n][1],0]),(10,[0,-REST[n][1],0])])
 a['war_cauldron']['position']=keys([(0,[0,0,0]),(2,[0,-17,0]),(5,[0,-18.5,0]),(10,[0,-18.5,0])])
 for n in HIP:a[n+'_upper']['scale']=keys([(0,[1,1,1]),(2,[0,0,0]),(10,[0,0,0])])
 a['bone_whip_0']['scale']=keys([(0,[1,1,1]),(2,[0,0,0]),(10,[0,0,0])]);a['whip_slide']={'scale':keys([(0,[1,1,1]),(2,[0,0,0]),(10,[0,0,0])])}
 # Old cast tripod supports remain grounded until all eight new struts have landed.
 if stage==2:
  for clip,definition in anims.items():
   if clip.endswith('.transition'):continue
   for n in HIP:
    if n.startswith('old_tripod'):
     for suffix in ('_upper','_shin','_foot'):definition['bones'][n+suffix]['scale']=keys([(0,[0,0,0]),(definition['animation_length'],[0,0,0])])
 # Three broad actual shell seams reveal white fractures only during the death timeline.
 for i,x in enumerate((-20,0,20)):
  fracture=bone('shell_fracture_'+str(i),'war_cauldron',(x,34,25 if x==0 else -23));cube(fracture,(x-1,27,24.9 if x==0 else -23.2),(2,17,.4),'white')
  for clip,definition in anims.items():definition['bones'][fracture['name']]={'scale':keys([(0,[0,0,0]),(2,[0,0,0]),(3,[1,1,1]),(7,[1,1,1]),(8,[0,0,0]),(10,[0,0,0])]) if clip.endswith('.death') else keys([(0,[0,0,0]),(definition['animation_length'],[0,0,0])])}
 if stage==2:
  heat=bone('ram_burning_cast','siege_ram',(-30,36,-30))
  for x in (-36,-31,-26):cube(heat,(x,40,-43),(3,10,7),'white')
  for clip,definition in anims.items():definition['bones'][heat['name']]={'scale':keys([(0,[1,1,1]),(2,[0,0,0]),(10,[0,0,0])]) if clip.endswith('.death') else keys([(0,[0,0,0]),(1.6,[0,0,0]),(2.2,[1,1,1]),(3.2,[1,1,1])]) if clip.endswith('.transition') else keys([(0,[1,1,1]),(definition['animation_length'],[1,1,1])])}
 geo(ident,bones,18,10,[0,4,0]);write(A/'animations/blueprint/boss'/f'{ident}.animation.json',{'format_version':'1.8.0','animations':anims})
 print(ident,'original bones',len(bones),'cuboids',sum(len(b.get('cubes',[])) for b in bones),'clips',len(anims),flush=True)
 im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
 for color,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill=('#A95F38' if stage==2 and color=='bronze' else COLORS[color]))
 (A/'textures/entity/blueprint/boss').mkdir(parents=True,exist_ok=True);im.save(A/'textures/entity/blueprint/boss'/f'{ident}.png')
# Two real finite spell exports; never substitute a particle plan for runtime meshes.
bones=[];b=bone('root')
for i in range(-6,6):
 z=(i+.5)*16;width=math.sqrt(max(0,96*96-z*z))*2
 cube(b,(-width/2,.1,i*16),(width,.9,16),'dark')
for i in range(8):
 a=i*math.pi/4;x,z=math.cos(a)*88,math.sin(a)*88;cube(b,(x-4,.9,z-4),(8,2,8),'bronze')
geo('taoyan_bounded_corpse_oil',bones,13,2,[0,.5,0]);write(A/'animations/blueprint/boss/taoyan_bounded_corpse_oil.animation.json',{'format_version':'1.8.0','animations':{'animation.taoyan_bounded_corpse_oil.idle':{'animation_length':1,'loop':True,'bones':{'root':{'scale':keys([(0,[1,1,1]),(.5,[1,1.2,1]),(1,[1,1,1])])}}}}})
bones=[];b=bone('root')
for i in range(16):cube(b,(-6,.1,-(i+1)*16),(12,3,16.1),'dark');cube(b,(-4,2,-i*16-12),(8,10+(i%3)*2,8),'bronze');cube(b,(-1,5,-i*16-10),(2,10,4),'white')
geo('taoyan_growing_fire_fissure',bones,34,3,[0,1,-8]);write(A/'animations/blueprint/boss/taoyan_growing_fire_fissure.animation.json',{'format_version':'1.8.0','animations':{'animation.taoyan_growing_fire_fissure.idle':{'animation_length':.8,'loop':True,'bones':{'root':{'scale':keys([(0,[1,1,1]),(.4,[1,.7,1]),(.8,[1,1,1])])}}}}})
# Original readable 16px component icons, and pure colour islands for the functional arena blocks.
for name in ('taoyan_bronze_cauldron_ear','taoyan_quenched_siege_stake','taoyan_army_soul_crystal'):
 im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
 if name.endswith('ear'):d.rectangle((3,3,12,12),fill=COLORS['bronze']);d.rectangle((5,5,10,10),fill='white');d.rectangle((2,6,4,9),fill=COLORS['dark']);d.rectangle((11,6,13,9),fill=COLORS['bone'])
 elif name.endswith('stake'):d.rectangle((6,2,9,13),fill=COLORS['dark']);d.rectangle((4,2,11,7),fill=COLORS['bronze']);d.rectangle((6,2,9,5),fill=COLORS['bone']);d.rectangle((4,10,11,11),fill=COLORS['bronze'])
 else:d.rectangle((4,2,11,13),fill=COLORS['dark']);d.rectangle((2,5,13,10),fill=COLORS['dark']);d.rectangle((4,4,11,11),fill=COLORS['bronze']);d.rectangle((6,4,9,9),fill=COLORS['bone'])
 im.save(A/'textures/item'/f'{name}.png');write(A/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+name}})
write(A/'models/item'/f'{ID}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for name,col in [('cauldron_abyss_oil','dark'),('cauldron_bone_ritual','bronze')]:
 write(A/'models/block'/f'{name}.json',{'textures':{'all':'dynasty:entity/blueprint/boss/'+ID,'particle':'dynasty:entity/blueprint/boss/'+ID},'elements':[{'from':[0,0,0],'to':[16,16,16],'faces':{f:{'uv':UV[col]+[UV[col][0]+4,UV[col][1]+4],'texture':'#all'} for f in ['north','south','west','east','up','down']}}]});write(A/'blockstates'/f'{name}.json',{'variants':{'':{'model':'dynasty:block/'+name}}})
write(A/'models/item/cauldron_bone_ritual.json',{'parent':'dynasty:block/cauldron_bone_ritual'})

# Approved inventory transparency: preserve entity atlases.
import runpy as _inventory_runpy
from pathlib import Path as _InventoryPath
_inventory_runpy.run_path(str(_InventoryPath(__file__).resolve().parents[1]/"art/inventory-refresh/transparent.py"))["cleanup_white"]()
