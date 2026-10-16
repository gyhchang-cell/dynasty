#!/usr/bin/env python3
"""Original segmented hybrid, authored as cuboids; no third-party asset data."""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'src/main/resources/assets/dynasty'
ID='gudu_tianzhunv'
COLORS={'dark':'#282130','shell':'#665372','green':'#75B54A','pale':'#FFFFFF'}
UV={'dark':[2,2],'shell':[10,2],'green':[2,10],'pale':[10,10]}
bones=[]
def bone(name,parent=None,pivot=(0,0,0),rotation=None):
 b={'name':name,'pivot':list(pivot)}
 if parent:b['parent']=parent
 if rotation:b['rotation']=list(rotation)
 bones.append(b);return b

def cube(b,origin,size,color='dark',rotation=None,pivot=None):
 c={'origin':list(origin),'size':list(size),'uv':{f:{'uv':UV[color],'uv_size':[4,4]} for f in ('north','south','east','west','up','down')}}
 if rotation:c.update(rotation=list(rotation),pivot=list(pivot or b['pivot']))
 b.setdefault('cubes',[]).append(c)

def key(values):return {str(t):v for t,v in values}
root=bone('root',pivot=(0,16,0))
thorax=bone('thorax','root',(0,11,-5));cube(thorax,(-8,7,-13),(16,9,18),'shell');cube(thorax,(-6,9,-14),(12,7,2),'dark')
abd=bone('abdomen','thorax',(0,11,6));cube(abd,(-8,7,3),(16,10,8),'shell');cube(abd,(-12,6,9),(24,11,17),'dark');cube(abd,(-9,8,24),(18,8,9),'shell');cube(abd,(-9,16,11),(18,3,17),'shell');cube(abd,(-7,19,13),(14,2,12),'dark')
sac=bone('venom_sac','abdomen',(0,9,18));cube(sac,(-5,5,25),(10,5,9),'green')
fusion=bone('pelvis','thorax',(0,15,-8));cube(fusion,(-4,13,-11),(8,5,7),'shell')
waist=bone('waist','pelvis',(0,18,-8));cube(waist,(-3,18,-10),(6,4,5),'pale')
chest=bone('chest','waist',(0,22,-8));cube(chest,(-4,22,-11),(8,5,6),'pale');cube(chest,(-4,22,-5),(8,5,1),'dark')
neck=bone('neck','chest',(0,27,-8));cube(neck,(-1.5,27,-9.5),(3,2,3),'pale')
face=bone('face','neck',(0,29,-8));cube(face,(-3,28,-11),(6,6,5),'pale');cube(face,(-2.75,30,-11.35),(2,2,.5),'dark');cube(face,(.75,30,-11.35),(2,2,.5),'dark');cube(face,(-1,28,-11.35),(2,2,.5),'shell')
hair=bone('hair','face',(0,31,-6));cube(hair,(-3.5,32,-11),(7,3,6),'dark');cube(hair,(-3.5,25,-6.5),(7,9,3),'dark');cube(hair,(-2.5,20,-5.5),(5,6,3),'dark')
for side,s in (('left',1),('right',-1)):
 h=bone(side+'_hair','hair',(s*3,31,-8));cube(h,(2 if s>0 else -5,22,-9),(3,12,3),'dark')
 shoulder=bone(side+'_upper_arm','chest',(s*4,25,-8));cube(shoulder,(4 if s>0 else -7,21,-10),(3,5,4),'pale',rotation=(0,0,s*12))
 arm=bone(side+'_forearm',side+'_upper_arm',(s*5.5,21,-8));cube(arm,(4 if s>0 else -7,17,-10),(3,5,3),'pale',rotation=(0,0,-s*15))
 hand=bone(side+'_hand',side+'_forearm',(s*5.5,17,-9));cube(hand,(4 if s>0 else -7,15,-10),(3,3,3),'dark')
 for i,z in enumerate((-10,-4,3,9)):
  hip=bone(f'{side}_leg{i}_hip','thorax',(s*7,11,z),(0,s*(i-1.5)*15,0));cube(hip,(7 if s>0 else -16,10,z-1.5),(9,3,3),'shell')
  knee=bone(f'{side}_leg{i}_knee',hip['name'],(s*16,11,z));cube(knee,(15 if s>0 else -25,8,z-1.5),(10,3,3),'dark',rotation=(0,0,s*12))
  tip=bone(f'{side}_leg{i}_tip',knee['name'],(s*24,9,z));cube(tip,(23 if s>0 else -26,0,z-1.5),(3,10,3),'dark',rotation=(0,0,-s*18))
  cube(tip,(23 if s>0 else -26,6,z-3.5),(3,3,2),'shell')
  if i==0:cube(tip,(22 if s>0 else -27,0,z-4),(5,2,5),'shell')
# Fixed timing matches authoritative server frames: acid20, drop12, eggs18.
anims={}
def anim(name,length,loop=False):
 d={'animation_length':length,'bones':{}}
 if loop:d['loop']=True
 anims['animation.'+ID+'.'+name]=d;return d['bones']
a=anim('idle',2,True);a['venom_sac']={'scale':key([(0,[1,1,1]),(1,[1.04,1.08,1.04]),(2,[1,1,1])])};a['chest']={'rotation':key([(0,[3,0,0]),(1,[0,0,0]),(2,[3,0,0])])}
a=anim('walk',.8,True);a['thorax']={'position':key([(0,[0,0,0]),(.2,[0,1,0]),(.4,[0,0,0]),(.6,[0,1,0]),(.8,[0,0,0])])}
for side,s in (('left',1),('right',-1)):
 for i in range(4):
  sign=1 if (i+(s<0))%2==0 else -1
  a[f'{side}_leg{i}_hip']={'rotation':key([(0,[0,sign*10,0]),(.4,[0,-sign*10,s*6]),(.8,[0,sign*10,0])])}
  a[f'{side}_leg{i}_knee']={'rotation':key([(0,[0,0,0]),(.4,[0,0,-s*12]),(.8,[0,0,0])])}
a=anim('acid',7.5);a['venom_sac']={'scale':key([(0,[1,1,1]),(.95,[1.3,1.4,1.2]),(1,[1,1,1]),(2,[1.2,1.3,1.1]),(3,[1,1,1]),(4,[1.2,1.3,1.1]),(5,[1,1,1]),(6,[1,1,1]),(7.5,[1,1,1])])};a['chest']={'rotation':key([(0,[0,0,0]),(.8,[28,0,0]),(1,[38,0,0]),(6,[38,0,0]),(7.5,[0,0,0])])}
a=anim('drop',3.85);a['thorax']={'position':key([(0,[0,0,0]),(.55,[0,2,0]),(.6,[0,0,0]),(1.1,[0,-3,0]),(1.8,[0,0,0]),(3.85,[0,0,0])])};a['chest']={'rotation':key([(0,[0,0,0]),(.5,[55,0,0]),(.6,[60,0,0]),(1.1,[20,0,0]),(3.85,[0,0,0])])}
for side,s in (('left',1),('right',-1)):
 for i in range(4):
  a[f'{side}_leg{i}_hip']={'rotation':key([(0,[0,0,0]),(.55,[0,0,s*65]),(.6,[0,0,s*65]),(1.1,[0,0,-s*8]),(3.85,[0,0,0])])}
  a[f'{side}_leg{i}_knee']={'rotation':key([(0,[0,0,0]),(.55,[0,0,-s*75]),(1.1,[0,0,0]),(3.85,[0,0,0])])}
a=anim('eggs',2.95);a['abdomen']={'rotation':key([(0,[0,0,0]),(.8,[-20,0,0]),(.9,[10,0,0]),(1.4,[0,0,0]),(2.95,[0,0,0])])};a['venom_sac']={'scale':key([(0,[1,1,1]),(.8,[1.3,1.3,1.3]),(.9,[.75,.75,.75]),(2.95,[1,1,1])])};a['chest']={'rotation':key([(0,[0,0,0]),(.8,[-15,0,0]),(.9,[20,0,0]),(2.95,[0,0,0])])}
a=anim('hurt',.4);a['chest']={'rotation':key([(0,[0,0,0]),(.1,[-18,0,8]),(.4,[0,0,0])])}
a=anim('death',4);a['thorax']={'position':key([(0,[0,0,0]),(1.6,[0,-5,0]),(4,[0,-5,0])])};a['chest']={'rotation':key([(0,[0,0,0]),(1,[80,0,0]),(4,[80,0,0])])};a['abdomen']={'scale':key([(0,[1,1,1]),(1,[1.2,1.3,1.2]),(2,[1,.15,1]),(4,[1,.15,1])])}
for side,s in (('left',1),('right',-1)):
 for i in range(4):
  t=.4+i*.16;a[f'{side}_leg{i}_hip']={'rotation':key([(0,[0,0,0]),(t,[0,0,0]),(t+.8,[0,0,s*60]),(4,[0,0,s*60])])};a[f'{side}_leg{i}_knee']={'rotation':key([(0,[0,0,0]),(t+.8,[0,0,-s*80]),(4,[0,0,-s*80])])}
def write_geo(id,model,extent=5):
 data={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+id,'texture_width':16,'texture_height':16,'visible_bounds_width':extent,'visible_bounds_height':4,'visible_bounds_offset':[0,1,0]},'bones':model}]}
 p=ASSET/'geo/blueprint/elite'/f'{id}.geo.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
def write_animation(id,data):
 p=ASSET/'animations/blueprint/elite'/f'{id}.animation.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'format_version':'1.8.0','animations':data},indent=2)+'\n')
# Keep the whole hybrid within the native two-block collision height.
for b in bones:
 if b['name'] in {'waist','chest','neck','face','hair','left_hair','right_hair','left_upper_arm','right_upper_arm','left_forearm','right_forearm','left_hand','right_hand'}:
  b['pivot'][1]-=3
  for c in b.get('cubes',[]):
   c['origin'][1]-=3
   if 'pivot' in c:c['pivot'][1]-=3
write_geo(ID,bones);write_animation(ID,anims)
texture=Image.new('RGB',(16,16),'white')
for color,xy in UV.items():
 for x in range(xy[0]-1,xy[0]+5):
  for y in range(xy[1]-1,xy[1]+5):texture.putpixel((x,y),tuple(bytes.fromhex(COLORS[color][1:])))
p=ASSET/'textures/entity/blueprint/elite'/f'{ID}.png';p.parent.mkdir(parents=True,exist_ok=True);texture.save(p)
# One native brood entity, mutually exclusive egg and articulated spider branches.
bones=[];b=bone('root');b=bone('egg','root',(0,3,0));cube(b,(-3,0,-3),(6,6,6),'green');cube(b,(-2,6,-2),(4,2,4),'shell')
b=bone('spider','root',(0,3,0));cube(b,(-3,1,-3),(6,4,8),'dark');cube(b,(-2,2,-4),(4,3,2),'shell')
for side,s in (('left',1),('right',-1)):
 for i,z in enumerate((-3,-1,1,3)):
  b=bone(f'{side}_leg{i}','spider',(s*3,3,z));cube(b,(3 if s>0 else -7,2,z),(4,1,1),'dark');cube(b,(6 if s>0 else -7,0,z),(1,3,1),'shell')
write_geo('tianzhu_brood',bones,1)
brood_animations={
 'animation.tianzhu_brood.egg':{'loop':True,'animation_length':1,'bones':{'egg':{'scale':key([(0,[1,1,1]),(.5,[1.08,1.08,1.08]),(1,[1,1,1])])}}},
 'animation.tianzhu_brood.walk':{'loop':True,'animation_length':.4,'bones':{f'{side}_leg{i}':{'rotation':key([(0,[0,12*(-1)**i,0]),(.2,[0,-12*(-1)**i,0]),(.4,[0,12*(-1)**i,0])])} for side in ('left','right') for i in range(4)}}
}
write_animation('tianzhu_brood',brood_animations)
print('Original adult: 42 bones, '+str(sum(len(b.get('cubes',[])) for b in json.loads((ASSET/'geo/blueprint/elite'/f'{ID}.geo.json').read_text())['minecraft:geometry'][0]['bones']))+' cuboids; 7 animations; actual 16x16 four-colour PNG')

# Original component-directed cod1 creature atlas; preserve the approved rig.
import runpy as _creature_runpy
from pathlib import Path as _CreaturePath
_creature_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/cod1-creatures-v32/paint.py"))["finish"]('gudu_tianzhunv')

# Original MC creature shape correction, after the material export.
import runpy as _creature33_runpy
_creature33_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v33/refine.py"))["finish"]('gudu_tianzhunv')
