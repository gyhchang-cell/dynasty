"""Original armored professions and a dedicated coarse tree rig; art only."""
import hashlib
import json
import math
import numpy as np
from build_models import Rig, track, OUT, ASSETS
from mechanicals import clip, lengths, wave

IDS=['juma_changqiangbing','kuijun_sishi','kumu_shujing','liannu_zhenzu']
SPECS=[
 (['#ffffff','#536b61','#273733','#bfa574'],['..121.3','..323.3','.111113','1131133','.1211.3','..121.3','.22.223']),
 (['#ffffff','#874636','#292e2a','#bd9b65'],['..111..','..323..','.11111.','1131133','3311133','.21212.','.22.22.']),
 (['#ffffff','#76543b','#30382a','#c0a45e'],['.1.1.1.','1131131','.11211.','1321231','1131131','1.111.1','1121211']),
 (['#ffffff','#8d734b','#293931','#b99c63'],['..111..','..323..','.11111.','1133133','3333333','..121..','.22.22.']),
]

def skeleton(r):
 for old in json.loads((OUT/'source'/r.name/'original.geo.json').read_text())['minecraft:geometry'][0]['bones']:
  r.bone(old['name'],old.get('parent'),[round(v*8)/8 for v in old['pivot']],rotation=old.get('rotation'))
 return {b['name']:b for b in r.bones}

def steps(c,a,b,width=4,material=1):
 """Two connected coarse rectangular steps between authored joints."""
 result=[]
 for k in range(2):
  p=np.array(a)+(np.array(b)-a)*k/2;q=np.array(a)+(np.array(b)-a)*(k+1)/2
  lo=np.minimum(p,q);hi=np.maximum(p,q)
  origin=[round((v-width/2)*8)/8 for v in lo]
  size=[round((hi[i]-lo[i]+width)*8)/8 for i in range(3)]
  result.append(c(origin,size,material))
 return result

def fist(r,by,side,center,rotation=None):
 """Four broad palm blocks leave a square channel for a real handle."""
 c=r.cube;x,y,z=center;n=side+'_grip';by[n]['pivot']=list(center)
 if rotation:by[n]['rotation']=rotation
 by[n]['cubes']=[c([x-2,y-1.5,z-1.75],[1.25,3,3.5],3),c([x+.75,y-1.5,z-1.75],[1.25,3,3.5],3),c([x-.75,y-1.5,z-1.75],[1.5,3,1],3),c([x-.75,y-1.5,z+.75],[1.5,3,1],3)]

def human(r,job):
 by=skeleton(r);c=r.cube
 def put(n,items):by[n]['cubes']=items
 hip=by['pelvis']['pivot'][1];top=by['chest']['pivot'][1];hy=by['head']['pivot'][1]
 width=10 if job=='spear' else 11;depth=7 if job=='spear' else 8
 put('pelvis',[c([-4.5,hip-2,-3.5],[9,4,7]),c([-5,hip,-4],[10,2,8],3)])
 put('waist',[c([-3.5,hip+1,-3],[7,3,6],2)])
 put('waist_upper',[c([-4,hip+3,-3.5],[8,3,7])])
 put('chest',[c([-width/2,hip+5,-depth/2],[width,top-hip-4,depth]),c([-width/2-.5,top-2,-depth/2-.5],[width+1,2,depth+1],2)])
 put('chest_front',[c([-width/2,hip+5,-depth/2-1.25],[width,top-hip-5,1.25]),c([-1.5,hip+5,-depth/2-1.75],[3,top-hip-5,.5],3)])
 put('chest_back',[c([-width/2,hip+5,depth/2],[width,top-hip-5,1.5]),c([-3,top-2,depth/2+1],[6,2,1],3)])
 put('neck',[c([-2,top-1,-2],[4,2,4],2)])
 put('head',[c([-3.5,hy-2.5,-3.5],[7,5.5,7],2),c([-3,hy-2,-4.5],[6,4,1],3),c([-3,hy-.25,-5],[6,1.5,.5],2)])
 put('belt',[c([-5,hip+.5,-4],[10,1.5,8],2),c([-1.5,hip+.5,-5],[3,2,1],3)])
 if job=='spear':
  # A shorter support span gives the front arm enough reach when the pike pitches forward.
  second=[-4+math.sin(math.radians(40))*4,17+math.cos(math.radians(40))*4,-3.75]
  second=[round(v*8)/8 for v in second]
  for n in ['left_wrist','left_hand']:by[n]['pivot']=second.copy()
  for n in ['left_elbow','left_forearm']:by[n]['pivot']=[5.25,19,-1.75]
  put('iron_crown',[c([-4.5,hy+2,-4.5],[9,2,9]),c([-3.5,hy+4,-3.5],[7,1.5,7]),c([-1,hy+5,-3],[2,1.5,6],3),c([-4.5,hy-2,-2.5],[1.5,5,6]),c([3,hy-2,-2.5],[1.5,5,6])])
  for side,s in [('left',1),('right',-1)]:
   put(side+'_shoulder_plate',[c([s*5-3,top-2,-4],[6,3,8]),c([s*5-2.5,top-3,-4.5],[5,1.5,9],3)])
  for n,x,z in [('front',0,-4.5),('back',0,4),('left',4.25,0),('right',-4.25,0)]:
   put('skirt_'+n,[c([x-3,hip-6,z-.75],[6,6,1.5]),c([x-3,hip-6,z-1],[6,1.5,2],3)] if n in ['front','back'] else [c([x-.75,hip-5,-3.5],[1.5,5,7]),c([x-1,hip-5,-3.5],[2,1.5,7],3)])
  for i in range(3):
   y=-1+i*15;put('spear_'+str(i),[c([-4.625,y,-4.375],[1.25,15,1.25],2)])
  by['spear_2']['cubes'] += [c([-5,44,-4.75],[2,4,2],3),c([-4.75,48,-4.5],[1.5,3,1.5],3),c([-6.5,43,-4.5],[5,1.5,1.5],1)]
  for side in ['right','left']:fist(r,by,side,by[side+'_hand']['pivot'],[0,0,-40])
 elif job=='powder':
  for side in ['right','left']:
   for n in ['wrist','hand']:by[side+'_'+n]['pivot'][2]=-3.5
   x=by[side+'_hand']['pivot'][0];y=by[side+'_hand']['pivot'][1]
   by[side+'_broken_dao']['pivot']=[x,y,-3.5]
   put(side+'_broken_dao',[c([x-.625,y-1.5,-4.125],[1.25,3,1.25],2),c([x-2,y-1.5,-4.5],[4,1,2],3),c([x-1,y-7,-4.25],[2,5.5,1.5],3),c([x-.5,y-8,-4.25],[1.5,2,1.5],1)])
   fist(r,by,side,by[side+'_hand']['pivot'])
   px=-6.5 if side=='right' else 6.5;put(side+'_powder_jar',[c([px-2.5,hip-3,-3],[5,6,6]),c([px-3,hip-1.5,-3.5],[6,2,7],2),c([px-1.5,hip+3,-1.5],[3,1.5,3],3),c([px-.75,hip+4,-.75],[1.5,3,1.5],3)])
   r.bone(side+'_fuse_tip',side+'_powder_jar',[px,hip+7,0],[c([px-1,hip+6,-1],[2,2,2],3)])
  put('blindfold',[c([-4,hy+1.5,-4.5],[8,2,9]),c([-3,hy+3,-3.5],[6,2,7]),c([-1,hy-2,-5],[2,2,1],1),c([-4.5,hy-2,-2.5],[1.5,4,5]),c([3,hy-2,-2.5],[1.5,4,5])])
 else:
  put('headband',[c([-4.5,hy+1.5,-5],[9,2,9]),c([-3.5,hy+3,-3.5],[7,1.5,7]),c([-4.5,hy-2,-2],[1.5,4,6]),c([3,hy-2,-2],[1.5,4,6])])
  put('arrow_box',[c([-4,top-8,4],[8,10,5],2),c([-4.5,top+1,3.5],[9,2,6]),c([-3,top+3,5],[2,3,2],3),c([1,top+3,5],[2,3,2],3)])
  for i in range(3):
   x=-3+i*3;put('gear_pouch_'+str(i),[c([x-1,hip-2,3.5],[2,3,3],2),c([x-1.25,hip,.125+3.5],[2.5,1,3],3)])
  put('crossbow',[c([-2.5,16,-14],[5,3,12],2),c([-2.5,18,-14.25],[5,1,12.5]),c([-7.5,16,-12.5],[15,2,2],3),c([-7.5,15.5,-11.5],[15,1,1],2),c([-1.75,15.75,-6.125],[1.25,3,1.25],2),c([1.125,15.75,-11.125],[1.25,3,1.25],2)])
  put('crossbow_lever',[c([-1,18,-11],[2,1.5,7],3),c([-2,18.5,-5],[4,2,2],1)])
  put('crossbow_magazine',[c([-1.5,19,-10],[3,4,5]),c([-2,22,-10.5],[4,1.5,6],3)])
  put('crossbow_tongue',[c([-1,17.5,-15],[2,1,4],3)])
  for side in ['right','left']:fist(r,by,side,by[side+'_hand']['pivot'])
 for side,s in [('right',-1),('left',1)]:
  a=by[side+'_shoulder']['pivot'];e=by[side+'_elbow']['pivot'];w=by[side+'_hand']['pivot']
  put(side+'_upper_arm',steps(c,a,e,3.5));put(side+'_elbow',[c([e[0]-2,e[1]-2,e[2]-2],[4,4,4],2)])
  put(side+'_forearm',steps(c,e,w,3.5,2));put(side+'_wrist',[c([w[0]-1.75,w[1]-1.75,w[2]-1.75],[3.5,3.5,3.5],1)])
  x=by[side+'_thigh']['pivot'][0];z=by[side+'_thigh']['pivot'][2];k=by[side+'_knee']['pivot'][1]
  put(side+'_thigh',[c([x-1.75,k,z-2.5],[3.5,hip-k,5],2),c([x-2,hip-4,z-3],[4,3,6])])
  put(side+'_knee',[c([x-2,k-1,z-3],[4,2.5,6],3)])
  put(side+'_shin',[c([x-1.5,1.5,z-2],[3,k-1,4],2),c([x-1.75,2,z-2.75],[3.5,k-2,1.5])])
  put(side+'_ankle',[c([x-1.75,1,z-2.5],[3.5,2,5],2)])
  put(side+'_foot',[c([x-2,.125,z-4],[4,2,7],2),c([x-2,1,z-4],[4,1.5,2],3)])
 return by

def strides(r,arm_swing=False):
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'head':wave(1,ticks,1)}
  if name!='idle':
   for side,s in [('right',-1),('left',1)]:
    ph=0 if s==1 else math.pi;amp=12 if name=='walk' else 22
    ch[side+'_thigh']=wave(0,ticks,amp,ph);ch[side+'_knee']=wave(0,ticks,-amp*.35,ph);ch[side+'_ankle']=wave(0,ticks,-amp*.65,ph)
    if arm_swing:ch[side+'_shoulder']=wave(0,ticks,-amp*.5,ph)
  clip(r,name,ch,True)

def human_end(r):
 ticks=lengths(r)['hurt'];clip(r,'hurt',{'chest':track('rotation',[(0,[0,0,0]),(2,[-8,0,0]),(ticks,[0,0,0])])})
 ticks=lengths(r)['death'];clip(r,'death',{'pelvis':track('position',[(0,[0,0,0]),(28,[0,-5,0]),(ticks,[0,-5,0])]),'waist_upper':track('rotation',[(0,[0,0,0]),(28,[32,0,0]),(ticks,[32,0,0])]),'head':track('rotation',[(0,[0,0,0]),(28,[18,0,0]),(ticks,[18,0,0])]),**{side+'_thigh':track('rotation',[(0,[0,0,0]),(28,[0,0,s*32]),(ticks,[0,0,s*32])]) for side,s in [('right',-1),('left',1)]}})

def spear(r):
 human(r,'spear');strides(r)
 for name,tell,hit,end in [('attack',8,12,26),('brace',5,8,48)]:
  hold=16 if name=='attack' else 33
  pitch=72 if name=='attack' else 74
  rot=track('rotation',[(0,[0,0,0]),(tell,[pitch-8,0,0]),(hit,[pitch,0,0]),(hold,[pitch,0,0]),(end,[0,0,0])])
  ch={'spear':rot,'right_grip':rot,'chest':track('position',[(0,[0,0,0]),(tell,[0,0,1]),(hit,[0,0,-5 if name=='attack' else -1]),(hold,[0,0,-4 if name=='attack' else -1]),(end,[0,0,0])])}
  if name=='brace':ch['right_thigh']=track('rotation',[(0,[0,0,0]),(hit,[-20,0,0]),(hold,[-20,0,0]),(end,[0,0,0])]);ch['right_knee']=track('rotation',[(0,[0,0,0]),(hit,[38,0,0]),(hold,[38,0,0]),(end,[0,0,0])])
  clip(r,name,ch)
 human_end(r);pin_all(r,'spear')

def powder(r):
 human(r,'powder');strides(r,True)
 ch={'waist':track('rotation',[(0,[0,0,0]),(8,[0,16,0]),(12,[0,-16,0]),(17,[0,16,0]),(30,[0,0,0])])}
 for side,s in [('right',-1),('left',1)]:
  ch[side+'_shoulder']=track('rotation',[(0,[0,0,0]),(5,[-30,0,0]),(8,[-65 if s<0 else -30,0,s*5]),(12,[-30 if s<0 else -65,0,s*5]),(17,[-65 if s<0 else -30,0,s*5]),(30,[0,0,0])])
 clip(r,'attack',ch)
 ch={'chest':track('rotation',[(0,[0,0,0]),(14,[-8,0,0]),(20,[-14,0,0]),(36,[-14,0,0])])}
 for side,s in [('right',-1),('left',1)]:
  ch[side+'_shoulder']=track('rotation',[(0,[0,0,0]),(14,[0,0,s*40]),(20,[0,0,s*65]),(36,[0,0,s*65])])
  ch[side+'_powder_jar']=track('scale',[(0,[1,1,1]),(14,[1.08,1.08,1.08]),(20,[1.18,1.18,1.18]),(36,[1.18,1.18,1.18])])
  ch[side+'_fuse_tip']=track('scale',[(0,[1,1,1]),(14,[1.4,1.4,1.4]),(20,[1.8,1.8,1.8]),(36,[1.8,1.8,1.8])])
 clip(r,'detonate',ch);human_end(r)

def crossbow(r):
 human(r,'crossbow');strides(r)
 frames=[(0,[0,0,0]),(10,[-25,0,0]),(14,[8,0,0]),(16,[-20,0,0]),(18,[8,0,0]),(20,[-20,0,0]),(22,[8,0,0]),(35,[-20,0,0]),(46,[0,0,0])]
 clip(r,'attack',{'crossbow_lever':track('rotation',frames),'crossbow_tongue':track('position',[(0,[0,0,0]),(14,[0,0,-1.5]),(16,[0,0,0]),(18,[0,0,-1.5]),(20,[0,0,0]),(22,[0,0,-1.5]),(30,[0,0,0]),(46,[0,0,0])]),'chest':track('rotation',[(0,[0,0,0]),(14,[-3,0,0]),(16,[0,0,0]),(18,[-3,0,0]),(20,[0,0,0]),(22,[-3,0,0]),(46,[0,0,0])])})
 # Rotate around the pelvis rather than the ground origin; actual retreat is server motion.
 clip(r,'roll',{'pelvis':track('rotation',[(0,[0,0,0]),(6,[15,0,0]),(10,[100,0,0]),(14,[225,0,0]),(20,[350,0,0]),(32,[360,0,0])]),**{side+'_knee':track('rotation',[(0,[0,0,0]),(6,[50,0,0]),(20,[50,0,0]),(32,[0,0,0])]) for side in ['right','left']}})
 human_end(r);pin_all(r,'crossbow')

def tree(r):
 by=skeleton(r);c=r.cube
 def put(n,items):by[n]['cubes']=items
 put('lower_log',[c([-8,.125,-6],[16,14,12]),c([-9,.125,-5],[18,5,10],2),c([-4,5,-7],[8,7,2])])
 put('middle_log',[c([-6,12,-5.5],[12,16,11]),c([-5,14,-6.5],[10,13,2],2)])
 put('mid_log_left',[c([4,16,-5],[4,12,10]),c([6,23,-4],[3,6,8])])
 put('mid_log_right',[c([-8,13,-4],[4,12,8]),c([-9,18,-3],[3,6,6],2)])
 put('upper_log',[c([-4,26,-5],[14,12,10]),c([-3,36,-4],[12,3,8],2),c([0,38,-3],[6,3,6])])
 by['tree_heart']['pivot']=[0,23,-6.5]
 put('tree_heart',[c([-4.5,18,-7.5],[9,9,1],2),c([-4,24,-8],[3,2,1],3),c([1,24,-8],[3,2,1],3),c([-2,19,-8],[4,3,1],3)])
 for side,s in [('right',-1),('left',1)]:
  put(side+'_branch',[c([min(s*6,s*14)-2,24,-2.5],[12,5,5]),c([s*10-2,27,-2],[4,3,4],2)])
  put(side+'_elbow',[c([s*13-2.5,18,-2.5],[5,8,5],2)])
  rise=4 if s<0 else 0
  put(side+'_root_club',[c([s*15-3.5,12+rise,-3.5],[7,8,7]),c([s*15-4,12+rise,-4],[8,3,8],2),c([s*15-4,10+rise,-3],[3,3,6]),c([s*15+1,10+rise,-3],[3,3,6])])
  put('fungus_'+side,[c([s*6-3,31,-5],[6,2,6],3),c([s*6-2,33,-4],[4,2,4],3)])
 for i in range(6):
  put('root_upper_'+str(i),[c([-2.5,1,3],[5,4,6]),c([-2,3,4],[4,3,4])])
  put('root_joint_'+str(i),[c([-2,1,8],[4,3,5],2)])
  put('root_tip_'+str(i),[c([-2.5,.125,12],[5,2,5]),c([-1.5,.125,16],[3,1.5,3],2)])
 crowns=[
  ([-4,36,-2],[c([-12,36,-3.5],[11,3,3]),c([-13,38,-3.5],[3,7,3],2),c([-15,43,-3.5],[5,2,3])]),
  ([6,36,-2],[c([6,35,-3.5],[11,3,3]),c([14,37,-3.5],[3,7,3],2),c([16,40,-3.5],[3,3,3])]),
  ([-2,37,3],[c([-3.5,37,1.5],[3,5,3]),c([-6,40,1.5],[7,3,3],2)]),
  ([5,36,3],[c([3.5,36,1.5],[3,6,3]),c([5,40,1.5],[6,3,3],2)]),
 ]
 for i,(pivot,cubes) in enumerate(crowns):r.bone('crown_branch_'+str(i),'upper_log',pivot,cubes)
 camo={'tree_heart':track('scale',[(0,[.05,.05,.05]),(40,[.05,.05,.05])])}
 for side,s in [('right',-1),('left',1)]:camo[side+'_branch']=track('rotation',[(0,[0,0,s*-58]),(40,[0,0,s*-58])])
 clip(r,'camouflage',camo,True)
 clip(r,'wake',{'tree_heart':track('scale',[(0,[.05,.05,.05]),(18,[.05,.05,.05]),(20,[1,1,1]),(30,[1,1,1])]),**{side+'_branch':track('rotation',[(0,[0,0,s*-58]),(20,[0,0,0]),(30,[0,0,0])]) for side,s in [('right',-1),('left',1)]}})
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'upper_log':wave(1,ticks,1)}
  if name!='idle':
   for i in range(6):
    ph=(i%2)*math.pi;ch['root_upper_'+str(i)]=wave(0,ticks,4 if name=='walk' else 7,ph)
  clip(r,name,ch,True)
 clip(r,'attack',{'middle_log':track('rotation',[(0,[0,0,0]),(12,[0,-12,0]),(18,[0,16,0]),(28,[0,8,0]),(42,[0,0,0])]),'right_branch':track('rotation',[(0,[0,0,0]),(12,[-10,-30,-15]),(18,[15,28,10]),(28,[5,15,5]),(42,[0,0,0])])})
 clip(r,'roots',{'middle_log':track('rotation',[(0,[0,0,0]),(22,[-8,0,0]),(28,[8,0,0]),(60,[0,0,0])]),**{'root_upper_'+str(i):track('rotation',[(0,[0,0,0]),(22,[-12,0,0]),(28,[6,0,0]),(42,[0,0,0]),(60,[0,0,0])]) for i in range(6)}})
 clip(r,'hurt',{'middle_log':track('rotation',[(0,[0,0,0]),(2,[0,0,5]),(10,[0,0,0])])})
 clip(r,'death',{'trunk':track('scale',[(0,[1,1,1]),(32,[1,.35,1]),(44,[1,.35,1])]),'upper_log':track('rotation',[(0,[0,0,0]),(32,[20,0,12]),(44,[20,0,12])]),**{side+'_branch':track('rotation',[(0,[0,0,0]),(32,[0,0,s*-35]),(44,[0,0,s*-35])]) for side,s in [('right',-1),('left',1)]}})

def matrices(r,channels,tick):
 from review import sample,transform
 world={};piv={b['name']:np.array(b['pivot']) for b in r.bones}
 for b in r.bones:
  ch=channels.get(b['name'],{});pos=piv[b['name']]-piv.get(b.get('parent'),np.zeros(3));rot=np.array(b.get('rotation',[0,0,0]),dtype=float)
  if 'position' in ch:pos=pos+sample(ch['position'],tick/20)
  if 'rotation' in ch:rot=rot+sample(ch['rotation'],tick/20)
  sc=sample(ch['scale'],tick/20) if 'scale' in ch else [1,1,1]
  world[b['name']]=world.get(b.get('parent'),np.eye(4))@transform(pos,rot,sc)
 return world

def euler(m):
 y=math.asin(float(np.clip(-m[2,0],-1,1)));cy=math.cos(y)
 if abs(cy)>.000001:x=math.atan2(m[2,1],m[2,2]);z=math.atan2(m[1,0],m[0,0])
 else:x=0;z=math.atan2(-m[0,1],m[1,1])
 return [round(v,7) for v in np.degrees([-x,-y,z])]

def between(a,b):
 a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);d=float(a@b);v=np.cross(a,b)
 assert d>-.99999,'Explicit half turn needed'
 k=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
 return np.eye(3)+k+k@k/(1+d)

def pin_all(r,weapon):
 """Bake a two-link support arm; no runtime source or server motion changes."""
 by={b['name']:b for b in r.bones};mirror=np.array([-1,1,1]);rest=matrices(r,{},0)
 upper=(np.array(by['left_elbow']['pivot'])-by['left_shoulder']['pivot'])*mirror
 lower=(np.array(by['left_hand']['pivot'])-by['left_elbow']['pivot'])*mirror;l1=np.linalg.norm(upper);l2=np.linalg.norm(lower)
 offset=rest[weapon][:3,:3].T@(rest['left_hand'][:3,3]-rest[weapon][:3,3]);orientation=rest[weapon][:3,:3].T@rest['left_hand'][:3,:3]
 pole_local=rest['chest'][:3,:3].T@(rest['left_elbow'][:3,3]-rest['left_shoulder'][:3,3])
 for animation in r.animations.values():
  ch=animation['bones'];duration=animation['animation_length']*20
  for tick in np.arange(0,duration+.01,.5):
   tr=matrices(r,ch,tick);target=tr[weapon][:3,3]+tr[weapon][:3,:3]@offset;start=tr['left_shoulder'][:3,3];delta=target-start;distance=np.linalg.norm(delta);u=delta/distance
   assert distance<l1+l2+.03,(r.name,weapon,tick,'overreach',distance,l1+l2)
   along=(distance**2+l1**2-l2**2)/(2*distance);bend=math.sqrt(max(0,l1**2-along**2));pole=tr['chest'][:3,:3]@pole_local;pole=pole-u*(pole@u);pole/=np.linalg.norm(pole)
   wanted=start+u*along+pole*bend
   for name,matrix in [('left_shoulder',between(upper,tr['chest'][:3,:3].T@(wanted-start)))]:ch.setdefault(name,{}).setdefault('rotation',{})[str(tick/20)]=euler(matrix)
   bent=matrices(r,ch,tick);ch.setdefault('left_elbow',{}).setdefault('rotation',{})[str(tick/20)]=euler(between(lower,bent['left_upper_arm'][:3,:3].T@(target-bent['left_elbow'][:3,3])))
   bent=matrices(r,ch,tick);ch.setdefault('left_wrist',{}).setdefault('rotation',{})[str(tick/20)]=euler(bent['left_forearm'][:3,:3].T@tr[weapon][:3,:3]@orientation)
   assert np.linalg.norm(matrices(r,ch,tick)['left_hand'][:3,3]-target)<.001,'Support hand missed handle'

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--ids',nargs='+',choices=IDS,default=IDS);selected=p.parse_args().ids
 owned_path=OUT/'armies-tree-owned-hashes.json';owned=json.loads(owned_path.read_text()) if owned_path.exists() else {}
 for name in selected:
  for folder,suffix,original in [('geo','.geo.json','original.geo.json'),('animations','.animation.json','original.animation.json')]:
   current=ASSETS/f'{folder}/blueprint/{name}{suffix}'
   assert current.read_bytes()==(OUT/'source'/name/original).read_bytes() or hashlib.sha256(current.read_bytes()).hexdigest()==owned.get(str(current)),'Concurrent modification: '+name
 for name,spec,builder in zip(IDS,SPECS,[spear,powder,tree,crossbow]):
  if name not in selected:continue
  rig=Rig(name,*spec);builder(rig);rig.save();print(name,len(rig.bones),'bones',sum(len(b.get('cubes',[])) for b in rig.bones),'cuboids',flush=True)
 from contacts import settle
 settle(selected)
 for name in selected:
  a=ASSETS/f'animations/blueprint/{name}.animation.json';(OUT/'blockbench'/(name+'.animation.json')).write_bytes(a.read_bytes())
  for folder,suffix in [('geo','.geo.json'),('animations','.animation.json')]:
   current=ASSETS/f'{folder}/blueprint/{name}{suffix}';owned[str(current)]=hashlib.sha256(current.read_bytes()).hexdigest()
 owned_path.write_text(json.dumps(owned,indent=2)+'\n')

if __name__=='__main__':main()
