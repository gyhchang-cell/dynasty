"""Separate original cuboid elite art; no legacy elite file is overwritten."""
import json,hashlib,math
from build_models import Rig,track,OUT,REPO
from mechanicals import clip,lengths,wave
from armies_tree import skeleton,steps,fist
from corpse_ghost_palanquin_flag import ordered
from resource_paths import resource_paths
IDS=['xianzhen_duantoujiang','qianji_bailian_yanshi','yanshi_clockwork_spider']
SPECS=[
 (['#ffffff','#566965','#233535','#b99963'],['.1.3.1.','1111113','.1231.3','.122113','.111..3','.11...3','.22...3']),
 (['#ffffff','#738878','#304343','#cfaa61'],['..121..','..323..','.11111.','3111113','.11311.','33.1.33','.22.22.']),
 (['#ffffff','#738878','#304343','#cfaa61'],['...3...','.11111.','3121213','2111112','3121213','21...12','.3...3.']),
]
def headless(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 put('pelvis',[c([-7,15,-5],[14,5,10]),c([-7.5,17,-5.5],[15,2,11],3)])
 put('waist',[c([-5,19,-4],[10,4,8],2)]);put('waist_upper',[c([-6,22,-4.5],[12,4,9])])
 put('chest',[c([-8,25,-5],[16,13,10])])
 put('chest_front',[c([-8,25,-7],[16,12,2]),c([-8.5,35,-7.5],[17,2,2.5],3)])
 put('chest_back',[c([-8,25,5],[16,12,2],2),c([-6,35,6],[12,2,2],3)])
 put('chest_mirror',[c([-3.5,28,-8],[7,7,1.5],2),c([-2.5,29,-9],[5,5,1.5],3),c([-1.25,30.25,-9.5],[2.5,2.5,1],1)])
 put('neck',[c([-2.5,37,-2.5],[5,3,5],2)])
 put('neck_seal',[c([-3,39.5,-3],[6,1.5,6],3)])
 put('seal_flame',[c([-1.5,41,-1.5],[3,2,3]),c([-1,42.5,-1],[2,1.5,2],3)])
 for side,s in [('right',-1),('left',1)]:
  a=[s*10,37.25,0];e=[s*10,29.75,-.5];w=[s*10,22.75,-1]
  for n in ['shoulder','upper_arm']:by[side+'_'+n]['pivot']=a.copy()
  for n in ['elbow','forearm']:by[side+'_'+n]['pivot']=e.copy()
  for n in ['wrist','hand','grip']:by[side+'_'+n]['pivot']=w.copy()
  put(side+'_upper_arm',steps(c,a,e,5));put(side+'_elbow',[c([s*10-3,28.5,-3],[6,3,6],3)])
  put(side+'_forearm',steps(c,e,w,4.5,2));put(side+'_wrist',[c([s*10-2.5,21.5,-3.5],[5,3,5])])
  put(side+'_beast_shoulder',[c([s*10-4,35,-5.5],[8,5,11],2),c([s*10-3.5,39,-5],[7,2,10],3),c([s*10-3.5,35,-7],[7,4,2],3),c([s*10-3,37,-7.5],[2,1.5,1],2),c([s*10+1,37,-7.5],[2,1.5,1],2),c([s*10-2.5,40,-4],[2,4,2],3),c([s*10+.5,40,-4],[2,4,2],3)])
  x=s*4.125;k=9.625
  put(side+'_thigh',[c([x-2.5,k,-3.5],[5,9,7],2)])
  put(side+'_hip_plate',[c([x-3,12,-5],[6,6,2]),c([x-3,12,-5.5],[6,2,2],3)])
  put(side+'_knee',[c([x-3,k-1.5,-4],[6,3,8],3)])
  put(side+'_shin',[c([x-2.25,2.5,-3],[4.5,k-1,6],2),c([x-2.5,3,-4],[5,5,1.5])])
  put(side+'_ankle',[c([x-2.5,1.5,-3.5],[5,3,7])])
  put(side+'_foot',[c([x-3,.125,-5],[6,2.5,9],2),c([x-3,1.5,-5],[6,2,3],3)])
  if side=='right':
   by['greatblade']['pivot']=w.copy();by['greatblade']['rotation']=[-115,0,0];fist(r,by,side,w,[-115,0,0])
  else:
   by['held_head']['pivot']=w.copy();fist(r,by,side,w)
 x,y,z=by['greatblade']['pivot']
 put('greatblade',[c([x-.625,y-2,z-.625],[1.25,7,1.25],2),c([x-4,y+4,z-1.25],[8,1.5,2.5],3)])
 for i in range(3):
  n='blade_fragment_'+str(i);by[n]['pivot']=[x,y+5+i*10,z]
  put(n,[c([x-2.5,y+5+i*10,z-1],[5,10,2],3),c([x-2.5,y+5+i*10,z-1.25],[1.5,10,.75],2)])
 by['blade_fragment_2']['cubes']+=[c([x-1.5,y+35,z-1],[3,3,2],3)]
 x,y,z=by['held_head']['pivot']
 put('held_head',[c([x-.625,y-4,z-.625],[1.25,6,1.25],2),c([x-3.5,y-11,-3.5],[7,7,7],3),c([x-2,y-9,-4.5],[4,2,1],2)])
 put('held_helmet',[c([x-4.5,y-5,-4.5],[9,2,9],2),c([x-3.5,y-3.5,-3.5],[7,1.5,7]),c([x-1,y-2.5,-3],[2,2,6],3)])
 put('held_eyes',[c([x-2.5,y-7,-4],[2,1.5,1],2),c([x+.5,y-7,-4],[2,1.5,1],2)])
 ordered(r)
 for name in ['idle','walk']:
  ticks=lengths(r)[name];ch={'chest':wave(0,ticks,.75),'seal_flame':wave(1,ticks,4)}
  if name=='walk':
   for side,s in [('right',-1),('left',1)]:
    ph=0 if s<0 else math.pi
    ch[side+'_thigh']=wave(0,ticks,12,ph);ch[side+'_knee']=wave(0,ticks,-4,ph);ch[side+'_ankle']=wave(0,ticks,-8,ph);ch[side+'_shoulder']=wave(0,ticks,-4,ph)
  clip(r,name,ch,True)
 clip(r,'roar',{'chest':track('rotation',[(0,[0,0,0]),(18,[-8,0,0]),(24,[-15,0,0]),(50,[0,0,0])]),'seal_flame':track('scale',[(0,[1,1,1]),(18,[1.2,1.4,1.2]),(24,[1.3,1.6,1.3]),(50,[1,1,1])])})
 clip(r,'spin',{'waist_upper':track('rotation',[(0,[0,0,0]),(16,[0,-30,0]),(26,[0,120,0]),(36,[0,360,0]),(46,[0,600,0]),(66,[0,720,0]),(76,[0,720,0])]),'right_shoulder':track('rotation',[(0,[0,0,0]),(16,[-40,0,-40]),(26,[-65,0,-40]),(46,[-65,0,-40]),(76,[0,0,0])]),'left_shoulder':track('rotation',[(0,[0,0,0]),(16,[0,0,30]),(46,[0,0,30]),(76,[0,0,0])])})
 clip(r,'throw',{'left_shoulder':track('rotation',[(0,[0,0,0]),(14,[-100,0,0]),(20,[-75,0,0]),(42,[0,0,0]),(50,[0,0,0])]),'held_head':track('scale',[(0,[1,1,1]),(19,[1,1,1]),(20,[.001,.001,.001]),(40,[.001,.001,.001]),(42,[1,1,1]),(50,[1,1,1])])})
 clip(r,'hurt',{'chest':track('rotation',[(0,[0,0,0]),(2,[-8,0,0]),(7,[0,0,0])])})
 death={'pelvis':track('position',[(0,[0,0,0]),(40,[0,-10,0]),(70,[0,-10,0])]),'waist_upper':track('rotation',[(0,[0,0,0]),(40,[45,0,0]),(70,[45,0,0])]),'seal_flame':track('scale',[(0,[1,1,1]),(40,[.001,.001,.001]),(70,[.001,.001,.001])]),'held_head':track('scale',[(0,[1,1,1]),(28,[.001,.001,.001]),(70,[.001,.001,.001])])}
 for side in ['right','left']:
  for joint,angle in [('thigh',-35),('knee',125),('ankle',-90)]:death[side+'_'+joint]=track('rotation',[(0,[0,0,0]),(40,[angle,0,0]),(70,[angle,0,0])])
 clip(r,'death',death)

def mechanist(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 by['waist_upper']=r.bone('waist_upper','waist',[0,17,0]);by['chest']['parent']='waist_upper'
 put('pelvis',[c([-4.5,10,-3],[9,5,6]),c([-5,13,-3.5],[10,2,7],3)])
 put('waist',[c([-3.5,14,-2.5],[7,3,5],2)])
 by['waist_upper']['cubes']=[c([-4,16,-3],[8,3,6])]
 put('chest',[c([-5.5,17,-3.5],[11,8,7]),c([-6,23,-4],[12,2,8],2)])
 put('chest_mirror',[c([-2,19,-4.5],[4,4,1.5],3),c([-1,20,-5],[2,2,1],2)])
 r.bone('neck','chest',[0,25,0],[c([-1.5,24,-1.5],[3,2,3],2)]);by['head']['parent']='neck'
 put('head',[c([-3.5,25.5,-3.5],[7,6,7],3),c([-3.5,25.5,-4],[7,1.5,1],2)])
 put('left_monocle',[c([.5,27,-4.5],[3,3,1.5],2),c([1,27.5,-5],[2,2,1],1)])
 put('nose',[c([-.75,26.5,-5],[1.5,2,1.5],3)])
 put('right_eye',[c([-3,28,-4.5],[2,1.5,1],2)])
 put('hair',[c([-4,30.5,-4],[8,1.5,8],2),c([-3,31.5,-3],[6,1.5,6],1),c([-4,27,2],[8,4,2],2)])
 put('apron',[c([-4.5,6.5,-4.5],[9,8.5,1.5],3),c([-4.5,7,-5],[9,2,1],2)])
 put('backpack',[c([-4,14.5,3.5],[8,13,8],2),c([-4.5,16,4],[9,10,7],3),c([-3,18,11],[6,5,1.5],1)])
 put('box_lid',[c([-4.5,26.5,3],[9,2,9.5],2),c([-3.5,28,4],[7,1.5,7.5],3)])
 put('box_valve',[c([-1.5,19,12],[3,4,1.5],2),c([-3,20,12.5],[6,2,1.5],3)])
 for side,s in [('right',-1),('left',1)]:
  a=[s*6,24,0];e=[s*6,19,-.5];w=[s*6,14,-1]
  by[side+'_shoulder']['pivot']=a;by[side+'_elbow']['pivot']=e;by[side+'_hand']['pivot']=w
  put(side+'_shoulder',steps(c,a,e,3.5));put(side+'_elbow',[c([s*6-1.75,17.75,-2.25],[3.5,2.5,3.5],2)])
  r.bone(side+'_forearm',side+'_elbow',e,steps(c,e,w,3,2))
  r.bone(side+'_wrist',side+'_forearm',w,[c([s*6-1.75,13,-2.5],[3.5,2,3.5],2)])
  by[side+'_hand']['parent']=side+'_wrist'
  put(side+'_hand',[c([s*6-2,12.5,-2.5],[4,3,3.5],3)])
  for i in range(5):
   n=f'{side}_finger_{i}';x=s*6+(i-2)*1.5
   by[n]['pivot']=[x,13,-1];put(n,[c([x-.625,10.5,-2.5],[1.25,2.5,2],3)] if i%2==0 else [])
   put(f'{side}_thread_{i}',[c([x-.625,3,-2],[1.25,7.5,.75],1)] if i in [0,4] else [])
  x=s*2.25;by[side+'_thigh']['pivot'][0]=x;by[side+'_knee']['pivot'][0]=x;by[side+'_boot']['pivot'][0]=x
  put(side+'_thigh',[c([x-1.5,6,-2],[3,7,4],2)])
  put(side+'_knee',[c([x-1.75,4.5,-2.5],[3.5,2.5,5],3)])
  r.bone(side+'_shin',side+'_knee',[x,6,0],[c([x-1.5,1.5,-2],[3,4,4],2)])
  r.bone(side+'_ankle',side+'_shin',[x,1.5,0])
  r.bone(side+'_foot',side+'_ankle',[x,1.5,0]);by[side+'_boot']['parent']=side+'_foot'
  put(side+'_boot',[c([x-2,.125,-3.5],[4,2,6],2),c([x-2,1.5,-3.5],[4,1.5,2],3)])
 for i in range(4):
  s=1 if i%2==0 else -1;y=20 if i<2 else 13;names=['aux_'+str(i),'aux_'+str(i)+'_elbow','aux_'+str(i)+'_claw']
  a=[s*4,y,7];e=[s*9,y,7];w=[s*10,y-5,7]
  for n,p in zip(names,[a,e,w]):by[n]['pivot']=p.copy();by[n].pop('rotation',None)
  put(names[0],steps(c,a,e,2.5,2));put(names[1],steps(c,e,w,2.5,3))
  put(names[2],[c([s*10-2,y-7,5.5],[1.5,3,3],2),c([s*10+.5,y-7,5.5],[1.5,3,3],2),c([s*10-2,y-4.5,5.5],[4,1.5,3],3)])
 ordered(r)
 for name in ['idle','walk']:
  ticks=lengths(r)[name];ch={'head':wave(1,ticks,1.25)}
  if name=='walk':
   for side,s in [('right',-1),('left',1)]:ch[side+'_thigh']=wave(0,ticks,12,0 if s<0 else math.pi);ch[side+'_knee']=wave(0,ticks,-8,0 if s<0 else math.pi)
  for i in range(4):ch['aux_'+str(i)]=wave(2,ticks,2,i*math.pi/2)
  clip(r,name,ch,True)
 for name,hit,end in [('net',14,42),('wheels',10,75),('spiders',20,56)]:
  ch={'chest':track('rotation',[(0,[0,0,0]),(hit-4,[-5,0,0]),(hit,[5,0,0]),(end,[0,0,0])])}
  for side,s in [('right',-1),('left',1)]:
   pitch=-100 if name=='net' else -25 if name=='wheels' else -35
   spread=35 if name=='net' else 12
   ch[side+'_shoulder']=track('rotation',[(0,[0,0,0]),(hit-4,[pitch*.75,0,s*spread*.6]),(hit,[pitch,0,s*spread]),(end,[0,0,0])])
   if name=='net':ch[side+'_wrist']=track('rotation',[(0,[0,0,0]),(hit,[-15,0,0]),(end,[0,0,0])])
  for i in range(4):
   s=1 if i%2==0 else -1;pitch=-50 if name=='wheels' and i<2 else -25 if name=='spiders' else 10;spread=35 if name=='spiders' and i>=2 else 25 if name=='wheels' and i<2 else 10
   ch['aux_'+str(i)]=track('rotation',[(0,[0,0,0]),(hit-4,[pitch*.5,0,s*spread*.5]),(hit,[pitch,0,s*spread]),(end,[0,0,0])])
  if name=='spiders':ch['box_lid']=track('rotation',[(0,[0,0,0]),(16,[-70,0,0]),(20,[-85,0,0]),(36,[-85,0,0]),(56,[0,0,0])])
  clip(r,name,ch)
 clip(r,'hurt',{'chest':track('rotation',[(0,[0,0,0]),(2,[-8,0,0]),(8,[0,0,0])])})
 death={'pelvis':track('position',[(0,[0,0,0]),(36,[0,-5,0]),(60,[0,-5,0])]),'waist_upper':track('rotation',[(0,[0,0,0]),(36,[35,0,0]),(60,[35,0,0])]),'head':track('rotation',[(0,[0,0,0]),(36,[15,0,0]),(60,[15,0,0])])}
 # Keep the production overload sequence while retaining the authored knee/foot contact.
 death['chest_mirror']=track('scale',[(0,[1,1,1]),(14,[1,1,1]),(22,[.001,.001,.001]),(60,[.001,.001,.001])])
 death['box_lid']=track('rotation',[(0,[0,0,0]),(14,[-100,0,0]),(20,[-150,0,0]),(60,[-150,0,0])])
 death['backpack']=track('scale',[(0,[1,1,1]),(16,[1.15,1.15,1.15]),(24,[.6,.5,.8]),(60,[.6,.5,.8])])
 for i in range(4):death['aux_'+str(i)]=track('rotation',[(0,[0,0,0]),(6,[30,50,70]),(12,[-40,-40,-60]),(18,[60,60,90]),(28,[0,0,(-1 if i%2 else 1)*60]),(60,[0,0,(-1 if i%2 else 1)*60])])
 for side in ['right','left']:
  for joint,angle in [('thigh',-35),('knee',125),('ankle',-90)]:death[side+'_'+joint]=track('rotation',[(0,[0,0,0]),(36,[angle,0,0]),(60,[angle,0,0])])
 clip(r,'death',death)

def spider(r):
 by=skeleton(r);c=r.cube
 by['boiler']['cubes']=[c([-2.5,2,-3.5],[5,3,7],2),c([-3,4,-3],[6,1.5,6],3),c([-2,5.5,-2],[4,1,4]),c([-1.5,2,-4.25],[3,2,1.5],3)]
 r.bone('mandibles','boiler',[0,3,-3.5],[c([-2,1.5,-5],[1.5,1.5,3],3),c([.5,1.5,-5],[1.5,1.5,3],3)])
 for i in range(8):
  s=1 if i%2==0 else -1;z=(i//2-1.5)*2
  a=[s*2.5,3.5,z];e=[s*4.5,2.5,z];f=[s*5.5,.75,z+(i//2-1.5)*.5]
  n='leg_'+str(i);by[n]['pivot']=a;by[n].pop('rotation',None);by[n+'_tip']['pivot']=e
  by[n]['cubes']=steps(c,a,e,1.25,2);by[n+'_tip']['cubes']=steps(c,e,f,1.25,3)+[c([f[0]-1,.125,f[2]-1],[2,1,2],2)]
 ordered(r)
 for name in ['walk','fuse']:
  ticks=lengths(r)[name];ch={}
  for i in range(8):ch['leg_'+str(i)]=wave(1,ticks,6 if name=='walk' else 2,i%2*math.pi);ch['leg_'+str(i)+'_tip']=wave(0,ticks,3 if name=='walk' else 1,i%2*math.pi)
  if name=='fuse':ch['boiler']=track('scale',[(0,[1,1,1]),(3,[1.12,1.2,1.12]),(6,[1,1,1])])
  clip(r,name,ch,True)

def preserve():
 data=json.loads((OUT/'elites-preserve-before.json').read_text())
 for rel,wanted in data.items():assert hashlib.sha256((REPO/rel).read_bytes()).hexdigest()==wanted,'Parallel elite edit: '+rel
 return data
def main():
 prior=preserve();guard=OUT/'elites-owned-hashes.json';owned=json.loads(guard.read_text()) if guard.exists() else {}
 for name in IDS:
  for p in resource_paths(name):assert not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()==owned.get(str(p)),'Concurrent new art edit'
 for name,spec,builder in zip(IDS,SPECS,[headless,mechanist,spider]):
  r=Rig(name,*spec);builder(r);r.save();print(name,len(r.bones),'bones',sum(len(b.get('cubes',[])) for b in r.bones),'Cuboids',flush=True)
  for p in resource_paths(name):owned[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
  guard.write_text(json.dumps(owned,indent=2)+'\n')
 from contacts import settle
 try:settle(IDS)
 finally:
  for name in IDS:
   for p in resource_paths(name):owned[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
  guard.write_text(json.dumps(owned,indent=2)+'\n')
 for name in IDS:(OUT/'blockbench'/(name+'.animation.json')).write_bytes(resource_paths(name)[1].read_bytes())
 assert preserve()==prior
 (OUT/'elite-legacy-preservation.json').write_text(json.dumps(dict(passed=True,unchanged=prior),indent=2)+'\n')
if __name__=='__main__':main()
