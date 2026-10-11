"""Eight original boss bodies. Unit = 1/16 block. No humanoid base or prior rig input."""
from pathlib import Path
import json,math,copy
from PIL import Image
R=Path(__file__).resolve().parents[3];A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/boss-forms-v2';D.mkdir(parents=True,exist_ok=True)
IDS=['undead_first_emperor','eunuch_mastermind','rebel_general','xianzhen_duantoujiang','qianji_bailian_yanshi','pilin_zhijinwu','baimian_huxiangu','juchui_jinjia_lishi']
NAMES=['帝棺尸龙','帷幕面灵','兵煞残甲','刑枷悬首','六足机关架','金鳞镇门兽','三尾狐妖','炉腹锤魔像']
PALETTES=[['#263330','#776644','#d0c3a1'],['#231e32','#705578','#bb9a73'],['#242c33','#725746','#9d3d35'],['#252b2e','#696158','#afac8c'],['#242f32','#997845','#607b72'],['#242f2b','#b5944f','#69786c'],['#242438','#9b6580','#c7b8a4'],['#232a2c','#ab7950','#d48a39']]
class Rig:
 def __init__(self,id):self.id=id;self.bones=[];self.by={};self.anim={};self.weapons=[];self.decor=[];self.gait=[];self.bone('root',None,[0,0,0])
 def bone(self,n,p='root',pivot=(0,0,0),rotation=None):
  assert n not in self.by,n;b={'name':n,'pivot':list(pivot),'cubes':[]}
  if p:b['parent']=p
  if rotation:b['rotation']=list(rotation)
  self.by[n]=b;self.bones.append(b);return n
 def cube(self,n,o,s,m=1,rot=None,pivot=None,pattern=False):
  rect=([2,2],[6,2],[10,2],[2,10])[m]
  uv={f:{'uv':rect[:],'uv_size':[2,2]} for f in ['north','south','east','west','up','down']}
  if pattern:
   for f in ['north','south']:uv[f]={'uv':[6,6],'uv_size':[4,4]}
  c={'origin':list(o),'size':list(s),'uv':uv,'_material':m}
  if rot:c['rotation']=rot;c['pivot']=pivot or self.by[n]['pivot']
  self.by[n]['cubes'].append(c);return c
 def box(self,n,c,s,m=1,**kw):return self.cube(n,[c[i]-s[i]/2 for i in range(3)],s,m,**kw)
 def beam(self,n,a,b,w=4,m=1,d=None):
  v=[b[i]-a[i] for i in range(3)];length=math.sqrt(sum(t*t for t in v));c=[(a[i]+b[i])/2 for i in range(3)]
  return self.box(n,c,[w,length,d or w],m,rot=[-math.degrees(math.asin(v[2]/length)),0,math.degrees(math.atan2(v[0],v[1]))],pivot=c)
 def chain(self,n,a,b,count=4):
  v=[b[j]-a[j] for j in range(3)];length=math.sqrt(sum(t*t for t in v));v=[t/length for t in v]
  reference=[0,0,1] if abs(v[2])<.9 else [1,0,0]
  cross=lambda x,y:[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]]
  p=cross(v,reference);mag=math.sqrt(sum(t*t for t in p));p=[t/mag for t in p];q=cross(v,p)
  for k in range(count):
   center=[a[j]+(b[j]-a[j])*(k+.5)/count for j in range(3)];side=p if k%2==0 else q;half=(length/count+1.5)/2
   corners=[[center[j]+v[j]*t*half+side[j]*d*1.5 for j in range(3)] for t,d in [(-1,-1),(-1,1),(1,1),(1,-1)]]
   for e in range(4):self.beam(n,corners[e],corners[(e+1)%4],1,0)
 def track(self,clip,bone,channel,keys):self.anim.setdefault(clip,{'bones':{}})['bones'].setdefault(bone,{})[channel]={str(k):v for k,v in keys} if isinstance(keys,list) and keys and isinstance(keys[0],tuple) else keys

def coffin():
 g=Rig(IDS[0]);g.bone('coffin','root',[0,12,2]);g.cube('coffin',[-15,12,8],[30,49,5],1,pattern=True)
 for s in [-1,1]:
  g.box('coffin',[s*15,37,0],[5,51,21],1);g.box('coffin',[s*15,37,-11.25],[3,49,3],2)
  lid=g.bone('lid_'+str(s),'coffin',[s*16,37,-10],[0,s*40,0]);g.box(lid,[s*9,37,-12],[13,42,3],1,pattern=True);g.box(lid,[s*9,37,-14],[3,32,1],2)
 for y in [13,60]:g.box('coffin',[0,y,0],[34,5,25],1);g.box('coffin',[0,y,-13],[30,3,2],2)
 g.bone('relic','coffin',[0,34,1]);g.box('relic',[0,38,3],[9,22,5],0)
 for y in [32,38,44]:
  for s in [-1,1]:g.beam('relic',[s*1,y,0],[s*7,y+2,-3],2,2)
 g.bone('imperial_mask','relic',[0,50,-1]);g.box('imperial_mask',[0,52,-2],[8,9,6],2);g.box('imperial_mask',[0,52,-5.1],[5,2,1],0)
 g.bone('regalia','imperial_mask',[0,57,-2]);g.box('regalia',[0,59,-2],[13,3,10],1);g.decor.append('regalia')
 g.bone('edict_arm','relic',[-5,43,0]);g.beam('edict_arm',[-5,43,0],[-13,42,-12],4,2);g.beam('edict_arm',[-13,42,-12],[-8,47,-20],3,2);g.box('edict_arm',[-8,47,-22],[6,4,6],1)
 # A continuous dragon coils behind, across and under the coffin; no pair of legs.
 points=[(20,8,0),(26,9,18),(18,22,24),(-17,31,25),(-24,44,15),(-18,61,5),(4,67,-4),(25,58,-14)]
 for i,(a,b) in enumerate(zip(points,points[1:])):
  n=g.bone('dragon_spine_'+str(i),'coffin' if i==0 else 'dragon_spine_'+str(i-1),a);g.beam(n,a,b,7,2)
  c=[(a[j]+b[j])/2 for j in range(3)];g.box(n,c,[10,5,10],2);g.beam(n,c,[c[0]*1.22,c[1]+6,c[2]+4],3,1)
  if i in [1,2,3]:
   for s in [-1,1]:g.beam(n,c,[c[0]+s*8,c[1]-5,c[2]-9],3,2)
 g.bone('dragon_skull','dragon_spine_6',points[-1]);g.box('dragon_skull',[26,56,-21],[14,12,18],2);g.box('dragon_skull',[26,53,-32],[10,7,10],2)
 for s in [-1,1]:g.box('dragon_skull',[26+s*7,57,-22],[1.5,3,7],0);g.beam('dragon_skull',[26+s*5,61,-16],[26+s*10,70,-10],3,2)
 g.bone('dragon_jaw','dragon_skull',[26,49,-16]);g.box('dragon_jaw',[26,48,-25],[11,3,23],2)
 for x in [22,30]:g.box('dragon_skull',[x,49,-29],[2,5,2],2)
 g.bone('coil_base');g.beam('coil_base',[-23,5,-13],[20,5,-13],7,2);g.beam('coil_base',[-23,5,-13],[-22,6,19],7,2);g.beam('coil_base',[-22,6,19],[22,6,19],7,2)
 for x,z in [(-24,-13),(22,-13),(-20,18),(20,18)]:g.beam('coil_base',[x,7,z],[x*1.25,4,z*1.5],5,2)
 return g

def curtain():
 g=Rig(IDS[1]);g.bone('canopy','root',[0,44,6]);g.box('canopy',[0,43,6],[52,6,9],0)
 for i in range(7):
  angle=(i-3)*19;layer=i*.35;n=g.bone('curtain_fan_'+str(i),'canopy',[0,41,8],[0,0,angle]);g.cube(n,[-6,41,8+layer],[12,34,3],1);g.cube(n,[-5,41,7+layer],[2,34,1],2)
  g.cube(n,[-6,67,7+layer],[12,5,2],2)
 g.bone('mask','canopy',[0,49,-13]);g.box('mask',[0,53,-13],[13,17,5],3);g.box('mask',[0,50,-16],[7,3,1],0)
 for s in [-1,1]:g.box('mask',[s*4,56,-16],[3,2,1],0)
 g.beam('canopy',[0,51,7],[0,51,-11],2,0)
 g.box('mask',[0,54,-17],[3,6,3],3)
 for side in [-1,1]:g.box('mask',[side*5,51,-16],[3,6,2],3,rot=[0,0,side*16],pivot=[side*5,53,-16])
 # Hollow robe: open centre, back and side strips; a viewer can see through it.
 for s in [-1,1]:
  n=g.bone('sleeve_'+str(s),'canopy',[s*19,43,2]);g.beam(n,[s*19,43,2],[s*39,34,-2],9,1,d=13)
  for dx in [-6,6]:g.box(n,[s*39+dx,28.5,-6],[3,10,14],1)
  g.box(n,[s*39,22,-6],[15,3,14],2);g.box(n,[s*39,35,-6],[15,3,14],2)
  h=g.bone('fingers_'+str(s),n,[s*39,25,-12]);g.box(h,[s*39,24,-15],[9,4,7],3)
  for k in [-1,0,1]:g.beam(h,[s*39+k*3,24,-17],[s*39+k*4,14-abs(k)*2,-24],2,3)
 for i,(x,y,z) in enumerate([(-18,39,3),(18,39,3),(-9,40,14),(9,40,14),(-27,36,7),(27,36,7)]):
  n=g.bone('hanging_cloth_'+str(i),'canopy',[x,y,z]);g.beam(n,[x,y,z],[x*1.08,18+i%2*4,z+5],6,1,d=3);g.beam(n,[x*1.08,18+i%2*4,z+5],[x*1.5,5+i%3*3,z-5],5,1,d=2)
 return g

def war():
 g=Rig(IDS[2]);g.bone('war_frame','root',[0,21,2]);g.beam('war_frame',[-11,22,8],[-17,53,7],10,0);g.beam('war_frame',[13,22,8],[13,47,6],8,0)
 g.beam('war_frame',[-17,52,7],[10,50,8],10,1)
 for s in [-1,1]:
  for y in [31,40,49]:g.beam('war_frame',[s*14,y,4],[s*6,y-4,-11],5,1)
 g.bone('war_core','war_frame',[0,39,4]);g.box('war_core',[0,39,4],[7,11,7],2)
 g.bone('broken_helm','war_frame',[-4,52,4]);g.box('broken_helm',[-4,57,5],[14,10,12],0);g.box('broken_helm',[-4,56,-2],[8,8,2],1);g.box('broken_helm',[-4,56,-3.2],[4,2,1],2)
 g.bone('breach_arm','war_frame',[-20,49,3]);g.box('breach_arm',[-25,45,4],[22,19,25],1);g.beam('breach_arm',[-26,44,1],[-36,23,-7],12,0);g.box('breach_arm',[-36,23,-8],[23,20,24],1)
 for k in [-1,0,1]:g.beam('breach_arm',[-36+k*7,20,-15],[-36+k*7,12,-23],5,0)
 g.bone('weapon_arm','war_frame',[18,46,3]);g.beam('weapon_arm',[18,46,3],[25,35,-6],8,0);g.beam('weapon_arm',[25,35,-6],[30,32,-19],8,1)
 g.bone('right_grip','weapon_arm',[30,32,-20]);g.box('right_grip',[30,32,-20],[9,7,8],0)
 g.bone('war_glaive','right_grip',[30,32,-20]);g.beam('war_glaive',[30,18,-20],[30,62,-20],4,0);g.box('war_glaive',[34,54,-20],[8,20,4],3);g.box('war_glaive',[33,66,-20],[6,5,4],3);g.box('war_glaive',[32,42,-20],[13,3,6],1);g.weapons.append('war_glaive')
 # Penetrating old weapons remain separate from the articulated main spear.
 g.bone('old_blades','war_frame',[0,39,8]);g.weapons.append('old_blades')
 for x in [-9,6]:g.beam('old_blades',[x-7,30,10],[x+7,67,11],3,0,d=6)
 g.bone('war_banner','war_frame',[-14,51,10]);g.decor.append('war_banner');g.cube('war_banner',[-18,19,13],[7,31,2],2);g.cube('war_banner',[8,25,13],[6,26,2],2)
 for s in [-1,1]:
  n=g.bone('support_'+str(s),'root',[s*12,25,4]);g.beam(n,[s*12,25,4],[s*17,13,11],11,1);g.box(n,[s*17,12,10],[16,11,15],0);g.beam(n,[s*17,12,11],[s*18,5,-5],9,1);g.box(n,[s*18,3,-6],[17,6,22],0);g.gait.append(n)
 return g

def yoke():
 g=Rig(IDS[3]);g.bone('yoke','root',[0,44,3]);
 for s in [-1,1]:
  g.box('yoke',[s*21,48,1],[30,10,17],1,pattern=True);g.box('yoke',[s*29,48,-9],[8,13,3],0)
 g.box('yoke',[0,48,10],[20,10,4],1);g.box('yoke',[0,44,0],[10,3,10],0)
 for s in [-1,1]:
  n=g.bone('giant_arm_'+str(s),'yoke',[s*32,45,1]);g.beam(n,[s*32,45,1],[s*41,30,-3],12,0);g.box(n,[s*37,37,-2],[15,19,17],1)
  e=g.bone('forearm_'+str(s),n,[s*41,30,-3]);g.beam(e,[s*41,30,-3],[s*36,15,-17],14,1);g.box(e,[s*36,14,-18],[16,11,16],0)
  for j in [-1,0,1]:g.box(e,[s*36+j*4,12,-26],[3,6,5],2)
  g.beam('yoke',[s*12,41,5],[s*17,23,10],5,0);g.beam('yoke',[s*17,23,10],[s*9,20,-3],4,1)
 g.bone('bound_head','yoke',[-35,49,0]);g.chain('bound_head',[-34,49,0],[-52,35,-1],4);g.box('bound_head',[-53,28,-1],[16,16,16],2);g.box('bound_head',[-53,34,-1],[20,6,19],0)
 for x in [-58,-48]:g.box('bound_head',[x,30,-9.2],[4,3,1],0)
 g.bone('blade_mount','forearm_1',[36,14,-18]);g.beam('blade_mount',[36,14,-18],[44,27,-27],5,0);g.beam('blade_mount',[44,27,-27],[52,54,-35],11,2,d=3);g.weapons.append('blade_mount')
 for i,(x,z) in enumerate([(-17,10),(0,14),(17,10)]):
  n=g.bone('drag_runner_'+str(i),'root',[x,27,z]);g.beam(n,[x,27,z],[x*1.1,5,z+20],8,1);g.box(n,[x*1.1,3,z+17],[10,5,24],0);g.chain(n,[x,44,z],[x,14,z+14],6);g.gait.append(n)
 return g

def machine():
 g=Rig(IDS[4]);g.bone('chassis','root',[0,29,0]);g.box('chassis',[0,29,0],[27,14,46],0);g.box('chassis',[0,36,0],[29,5,43],1,pattern=True)
 for s in [-1,1]:g.box('chassis',[s*14,30,0],[4,10,42],1)
 g.bone('pilot','chassis',[0,36,-14]);g.box('pilot',[0,43,-15],[10,12,8],1);g.box('pilot',[0,44,-19.5],[8,7,1],2);g.box('pilot',[0,44,-20.1],[4,2,1],0)
 for j,z in enumerate([-18,0,18]):
  for s in [-1,1]:
   n=g.bone('outrigger_'+str(j)+'_'+str(s),'chassis',[s*12,29,z]);g.box(n,[s*16,29,z],[9,8,9],1);g.beam(n,[s*16,29,z],[s*31,19,z+3],6,0)
   k=g.bone('link_'+str(j)+'_'+str(s),n,[s*31,19,z+3]);g.box(k,[s*31,19,z+3],[9,7,9],1);g.beam(k,[s*31,19,z+3],[s*39,4,z-5],6,1);g.box(k,[s*39,3,z-5],[12,6,15],0);g.gait.append(n)
 for s in [-1,1]:
  g.beam('chassis',[s*10,35,15],[s*13,48,14],6,1)
  for j,z in enumerate([-3,14]):
   n=g.bone('manipulator_'+str(j)+'_'+str(s),'chassis',[s*13,43,z]);g.beam(n,[s*13,43,z],[s*27,57,z-4],5,0);g.box(n,[s*27,57,z-4],[8,8,8],1)
   tip=g.bone('tool_'+str(j)+'_'+str(s),n,[s*27,57,z-4]);g.beam(tip,[s*27,57,z-4],[s*40,40,z-21],5,1)
   for d in [-1,1]:g.beam(tip,[s*40,40,z-21],[s*40+d*5,32,z-24],3,0)
 g.bone('drive_shaft','chassis',[0,29,0]);g.box('drive_shaft',[0,29,0],[6,6,58],1)
 g.bone('boiler','chassis',[0,32,24]);g.box('boiler',[0,33,27],[20,20,13],1,pattern=True);g.box('boiler',[0,46,28],[9,8,9],0)
 return g

def beast():
 g=Rig(IDS[5]);g.bone('beast_body','root',[0,29,3]);g.box('beast_body',[0,29,5],[30,25,54],0);g.box('beast_body',[0,35,-14],[36,26,28],1)
 for j,z in enumerate([-14,0,14,28]):
  n=g.bone('dorsal_scale_'+str(j),'beast_body',[0,40,z]);g.box(n,[0,44,z],[13,12,15],1,rot=[-22,0,0],pivot=[0,40,z]);
  for s in [-1,1]:g.box(n,[s*13,39,z],[12,7,14],1,rot=[0,0,s*30],pivot=[s*13,39,z])
 g.bone('beast_neck','beast_body',[0,33,-24]);g.beam('beast_neck',[0,33,-23],[0,34,-35],19,0)
 g.bone('beast_mask','beast_neck',[0,33,-36]);g.box('beast_mask',[0,34,-39],[24,19,20],1);g.box('beast_mask',[0,28,-51],[18,10,14],0);g.box('beast_mask',[0,34,-48],[22,5,4],1)
 for s in [-1,1]:g.box('beast_mask',[s*12,37,-42],[2,4,8],2);g.beam('beast_mask',[s*9,42,-34],[s*18,51,-28],5,1);g.beam('beast_mask',[s*7,25,-54],[s*8,32,-57],3,2)
 for end,z,y,w in [('front',-17,35,10),('rear',24,29,8)]:
  for s in [-1,1]:
   n=g.bone(end+'_'+str(s),'beast_body',[s*15,y,z]);g.beam(n,[s*15,y,z],[s*19,17,z+4],w,0);g.box(n,[s*18,y-7,z],[w+4,16,13],1)
   k=g.bone(end+'_paw_'+str(s),n,[s*19,17,z+4]);g.beam(k,[s*19,17,z+4],[s*20,5,z-4],w,0);g.box(k,[s*20,4,z-6],[14,8,18],1);g.gait.append(n)
 g.bone('beast_tail','beast_body',[0,26,32]);g.beam('beast_tail',[0,26,32],[0,19,47],9,0);g.beam('beast_tail',[0,19,47],[0,12,60],6,1)
 # Articulated long-weapon saddle is visibly attached to the torso, not floating.
 g.bone('weapon_saddle','beast_body',[0,44,-5]);g.box('weapon_saddle',[0,48,-5],[27,6,14],0)
 g.bone('pole_turret','weapon_saddle',[0,51,-6]);g.box('pole_turret',[0,51,-6],[10,8,10],1);g.beam('pole_turret',[0,51,12],[0,51,-62],4,0)
 g.box('pole_turret',[0,51,-63],[5,6,14],1);g.box('pole_turret',[0,51,-58],[27,3,5],1)
 for s in [-1,1]:g.beam('pole_turret',[s*13,51,-56],[s*11,51,-69],4,1,d=5)
 g.weapons.append('pole_turret');return g

def fox():
 g=Rig(IDS[6]);g.bone('fox_body','root',[0,27,4]);g.box('fox_body',[0,28,6],[23,20,46],2);g.box('fox_body',[0,30,-14],[26,23,23],3);g.box('fox_body',[0,34,7],[21,9,41],0)
 g.bone('fox_neck','fox_body',[0,31,-22]);g.beam('fox_neck',[0,31,-20],[0,36,-34],17,3)
 g.bone('fox_head','fox_neck',[0,35,-34]);g.box('fox_head',[0,36,-36],[22,18,20],3);g.box('fox_head',[0,30,-48],[14,10,15],3);g.box('fox_head',[0,30,-56],[9,5,3],0)
 for s in [-1,1]:
  g.box('fox_head',[s*11.4,38,-42],[2,4,9],0);g.box('fox_head',[s*8,46,-31],[9,11,7],0,rot=[0,0,s*12],pivot=[s*8,43,-31]);g.box('fox_head',[s*9,53,-31],[5,6,5],3)
 g.bone('forehead_knot','fox_head',[0,42,-43]);g.box('forehead_knot',[0,44,-44],[4,6,2],1);g.decor.append('forehead_knot')
 for end,z in [('front',-17),('rear',22)]:
  for s in [-1,1]:
   n=g.bone(end+'_'+str(s),'fox_body',[s*10,27,z]);g.beam(n,[s*10,27,z],[s*13,14,z+(4 if end=='rear' else 0)],7,2)
   k=g.bone(end+'_paw_'+str(s),n,[s*13,14,z+(4 if end=='rear' else 0)]);g.beam(k,[s*13,14,z+(4 if end=='rear' else 0)],[s*14,5,z-5],5,3);g.box(k,[s*14,3,z-7],[8,6,12],0);g.gait.append(n)
 for j,s in enumerate([-1,0,1]):
  a=[s*6,28,24];b=[s*18,31,43];c=[s*32,44 if s else 50,63];e=[s*36,39 if s else 48,81]
  n=g.bone('tail_'+str(j)+'_root','fox_body',a);g.beam(n,a,b,10,3)
  n2=g.bone('tail_'+str(j)+'_mid',n,b);g.beam(n2,b,c,17,3,d=17)
  n3=g.bone('tail_'+str(j)+'_tip',n2,c);g.beam(n3,c,e,13,3,d=13);g.box(n3,e,[9,9,10],1)
 g.bone('silk_knot','fox_body',[0,32,-15]);g.decor.append('silk_knot');g.box('silk_knot',[0,38,-14],[6,7,6],1);g.beam('silk_knot',[0,37,-14],[20,18,3],4,1,d=2)
 return g

def forge():
 g=Rig(IDS[7]);g.bone('furnace','root',[0,20,3]);g.box('furnace',[0,38,14],[41,35,12],1,pattern=True)
 for s in [-1,1]:g.box('furnace',[s*19,35,0],[9,34,32],1);g.box('furnace',[s*16,35,-17],[5,28,5],0)
 g.box('furnace',[0,53,-1],[42,10,36],1);g.box('furnace',[0,20,0],[39,9,36],0);g.box('furnace',[0,36,7],[19,20,3],2)
 for x in [-9,0,9]:g.box('furnace',[x,35,-16],[3,23,3],0)
 g.bone('inset_face','furnace',[0,54,-6]);g.box('inset_face',[0,54,-11],[12,8,8],0);g.box('inset_face',[0,54,-15.2],[8,2,1],2)
 for x in [-11,11]:g.box('furnace',[x,61,13],[10,16,10],0);g.box('furnace',[x,66,13],[13,4,13],1)
 for s in [-1,1]:
  n=g.bone('support_'+str(s),'root',[s*14,20,5]);g.box(n,[s*14,16,5],[16,13,19],0);g.beam(n,[s*14,14,5],[s*19,8,-6],12,1);g.box(n,[s*19,4,-7],[21,8,26],0);g.gait.append(n)
 for s in [-1,1]:
  n=g.bone('hammer_yoke_'+str(s),'furnace',[s*22,48,2]);g.box(n,[s*29,47,2],[17,16,26],1);g.beam(n,[s*28,45,2],[s*40,28,-6],10,0)
  p=g.bone('hammer_piston_'+str(s),n,[s*40,28,-6]);g.beam(p,[s*40,28,-6],[s*43,15,-18],10 if s<0 else 8,1)
  h=g.bone('hammer_'+str(s),p,[s*43,15,-18]);g.beam(h,[s*43,25,-18],[s*43,7,-18],5,0)
  g.box(h,[s*43,13,-18],[26 if s<0 else 20,22 if s<0 else 18,28 if s<0 else 22],1);g.box(h,[s*43,13,-33 if s<0 else -30],[24 if s<0 else 18,19 if s<0 else 15,4],0)
  g.box(h,[s*43,13,-35.1 if s<0 else -32.1],[14 if s<0 else 10,11 if s<0 else 7,1],3);g.weapons.append(h)
 return g

BUILDERS=[coffin,curtain,war,yoke,machine,beast,fox,forge]
def save(g,index):
 for sub in ['geo','animations','textures/entity']:(A/sub/'boss_forms').mkdir(parents=True,exist_ok=True)
 from atlas import atlas
 im=atlas(g,index)
 im.save(A/'textures/entity/boss_forms'/f'{g.id}.png')
 geo={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+g.id,'texture_width':im.width,'texture_height':im.height,'visible_bounds_width':12,'visible_bounds_height':9,'visible_bounds_offset':[0,3,0]},'bones':g.bones}]}
 (A/'geo/boss_forms'/f'{g.id}.geo.json').write_text(json.dumps(geo,indent=2)+'\n')
 (A/'animations/boss_forms'/f'{g.id}.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':g.anim},indent=2)+'\n')
 return {'id':g.id,'name':NAMES[index],'weapons':g.weapons,'decor':g.decor,'gait':g.gait,'bones':len(g.bones),'cuboids':sum(len(b['cubes']) for b in g.bones)}
if __name__=='__main__':
 from animate import animate
 manifest=[]
 for i,f in enumerate(BUILDERS):
  g=f();animate(g,i);manifest.append(save(g,i))
 (D/'forms.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print([(m['id'],m['cuboids']) for m in manifest])
