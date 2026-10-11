"""Original funeral child and folded paper duelist, preserving dirty legacy files."""
import json,hashlib,math
from build_models import Rig,track,OUT,REPO
from mechanicals import clip,lengths,wave
from armies_tree import skeleton,steps,fist
from corpse_ghost_palanquin_flag import ordered
from resource_paths import resource_paths
IDS=['fuhun_baibu_tongzi','zhiren_jianke']
SPECS=[
 (['#ffffff','#c8c1a6','#303d40','#9d744e'],['..111..','..212..','.11311.','3311133','.11311.','.12121.','.22.22.']),
 (['#ffffff','#d1c3a0','#333933','#914638'],['..111..','..323..','.11111.','1131133','.1111.3','.12.1.3','.22.2.3']),
]
def child(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 put('shroud_pelvis',[c([-3.5,4.5,-2.5],[7,3,5]),c([-4,5,-3],[8,2,6],2)])
 put('shroud_waist',[c([-3,6.5,-2],[6,3,4],2)])
 put('shroud_chest',[c([-4,8.5,-2.5],[8,4.5,5]),c([-4.5,10,-3],[9,2,6],3)])
 put('shroud_neck',[c([-1.5,11.5,-1.5],[3,2,3],2)])
 put('shroud_head',[c([-4.5,12.5,-4],[9,7,8]),c([-5,13,-4.5],[10,2,9],3),c([-5,17,-4.5],[10,2,9],2),c([-4,14,-5],[8,3,1],2),c([-4,14,-5.25],[4,3,1.25])])
 by['single_eye']['pivot']=[1.25,15.5,-5.25]
 put('shroud_single_eye',[c([0,14.5,-5.75],[2.5,2.5,1],3),c([.75,14.5,-6],[1.5,2.5,.5],2)])
 put('shroud_topknot',[c([-2,19.5,-1.5],[4,2.5,3],2),c([-3,21,-1],[6,1.5,2],3)])
 r.bone('mourning_collar','chest',[0,11,0],[c([-4.5,11.5,-3.5],[9,2,7],2),c([-1.5,8.5,-3.5],[3,3,1],3)])
 r.bone('robe_front','pelvis',[0,6,-2.5],[c([-4,2.5,-3.5],[8,4,1.5]),c([-3.5,1.5,-3.5],[7,1.5,1.5],3)])
 r.bone('robe_back','pelvis',[0,6,2.5],[c([-4,2.5,2],[8,4,1.5]),c([-3.5,1.5,2],[7,1.5,1.5],3)])
 for side,s in [('right',-1),('left',1)]:
  a=[s*4,11.25,0];e=[s*4,8.75,-1.5];w=[s*3.5,8.5,-4]
  for n in ['shoulder','upper_arm']:by[side+'_'+n]['pivot']=a.copy()
  for n in ['elbow','forearm']:by[side+'_'+n]['pivot']=e.copy()
  for n in ['wrist','hand','grip']:by[side+'_'+n]['pivot']=w.copy()
  put('shroud_'+side+'_upper_arm',steps(c,a,e,2.5));put('shroud_'+side+'_forearm',steps(c,e,w,2.5))
  r.bone(side+'_cuff',side+'_wrist',w,[c([w[0]-1.5,7.75,-5.25],[3,1.5,2.5],3)])
  fist(r,by,side,w,[0,0,90]);put('shroud_'+side+'_grip',[])
  x=s*1.75
  for n in ['thigh','knee','shin','ankle','foot']:by[side+'_'+n]['pivot'][0]=x
  put('shroud_'+side+'_thigh',[c([x-1.25,3,-1.5],[2.5,3.5,3],2)])
  put('shroud_'+side+'_shin',[c([x-1,1,-1.5],[2,3,3],3)])
  put('shroud_'+side+'_foot',[c([x-1.5,.125,-3],[3,1.5,5],2),c([x-1.5,1,-3],[3,1,2],3)])
 for n in ['lamp_handle','lamp_inertia','lantern']:by[n]['pivot']=[0,8.5,-4]
 put('lamp_handle',[c([-4.125,7.875,-4.625],[8.25,1.25,1.25],2)])
 # Seven broad frame pieces remain independently addressable on death.
 frames=[([-3.5,6.5,-6.5],[7,1.25,5]),([-3.5,2,-6.5],[7,1.25,5]),([-3.5,3.25,-6.5],[1.25,3.25,1.25]),([2.25,3.25,-6.5],[1.25,3.25,1.25]),([-3.5,3.25,-2.75],[1.25,3.25,1.25]),([2.25,3.25,-2.75],[1.25,3.25,1.25]),([-.625,7,-4.625],[1.25,1.5,1.25])]
 for i,(origin,size) in enumerate(frames):put('lamp_fragment_'+str(i),[c(origin,size,3)])
 put('lantern_flame',[c([-1.25,3.25,-5.25],[2.5,2.5,2.5],3),c([-.75,5.25,-4.75],[1.5,1.25,1.5],1)])
 for i,(x,z) in enumerate([(-3.75,2.25),(0,3.5),(3.75,2.25)]):
  for j in range(4):
   n=f'ribbon_{i}_{j}';y=10.5-j*2.25;by[n]['pivot']=[x,y,z]
   put(n,[c([x-1,y-2,z-.625],[2,2.5,1.25],3 if j%2==0 else 2)])
 ordered(r)
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'head':wave(1,ticks,2),'chest':wave(0,ticks,1)}
  if name!='idle':
   for side,s in [('right',-1),('left',1)]:
    ph=0 if s<0 else math.pi;amp=10 if name=='walk' else 18
    ch[side+'_thigh']=wave(0,ticks,amp,ph);ch[side+'_knee']=wave(0,ticks,-amp*.3,ph);ch[side+'_ankle']=wave(0,ticks,-amp*.7,ph)
  clip(r,name,ch,True)
 clip(r,'attack',{'chest':track('rotation',[(0,[0,0,0]),(8,[-12,0,0]),(12,[-20,0,0]),(18,[5,0,0]),(30,[0,0,0])]),'head':track('rotation',[(0,[0,0,0]),(8,[-12,0,0]),(12,[-18,0,0]),(30,[0,0,0])])})
 clip(r,'curse',{'chest':track('position',[(0,[0,0,0]),(34,[0,1.5,0]),(40,[0,2,0]),(60,[0,0,0])]),'head':track('rotation',[(0,[0,0,0]),(34,[8,12,0]),(40,[8,-12,0]),(60,[0,0,0])])})
 clip(r,'hurt',{'chest':track('rotation',[(0,[0,0,0]),(2,[-8,0,0]),(10,[0,0,0])])})
 clip(r,'death',{'pelvis':track('position',[(0,[0,0,0]),(28,[0,-2,0]),(44,[0,-2,0])]),'chest':track('rotation',[(0,[0,0,0]),(28,[25,0,0]),(44,[25,0,0])]),'head':track('rotation',[(0,[0,0,0]),(28,[18,0,0]),(44,[18,0,0])]),**{side+'_thigh':track('rotation',[(0,[0,0,0]),(28,[0,0,s*35]),(44,[0,0,s*35])]) for side,s in [('right',-1),('left',1)]}})

def paper(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 put('pelvis',[c([-4,9,-1.75],[8,4,3.5]),c([-4.5,10,-2.25],[9,2,4.5],3)])
 put('waist',[c([-3,12,-1.5],[6,3,3],2)]);put('waist_upper',[c([-3.5,14,-1.75],[7,3,3.5])])
 put('chest',[c([-5,16,-1.75],[10,7,3.5])])
 put('chest_front',[c([-5,16,-3],[10,7,1.25]),c([-4.5,19,-3.5],[4,3,1.25],3),c([.5,16,-3.5],[4,3,1.25],3)])
 put('chest_back',[c([-5,16,1.75],[10,7,1.25],2),c([-1,16,2.75],[2,7,1.25],1)])
 put('neck',[c([-1.5,23,-1.25],[3,2,2.5],2)])
 put('head',[c([-3.5,24.5,-1.5],[7,6,3]),c([-4.5,25.5,-1.5],[1.5,4,3],3),c([3,25.5,-1.5],[1.5,4,3],3),c([-2.75,27,-2],[2,1.5,.75],2),c([.75,27,-2],[2,1.5,.75],2),c([-1.5,25,-2],[3,1.25,.75],3)])
 r.bone('paper_crown','head',[0,30,0],[c([-4.5,30,-2.5],[9,1.5,5],2),c([-3,31.5,-1.5],[6,2,3]),c([-1.5,33.5,-1.5],[3,1.5,3],3)])
 for side,s in [('right',-1),('left',1)]:
  a=[s*6,22.5,0];e=[s*6,17.5,-.5];w=[s*6,12.5,-1]
  for n in ['shoulder','upper_arm']:by[side+'_'+n]['pivot']=a.copy()
  for n in ['elbow','forearm']:by[side+'_'+n]['pivot']=e.copy()
  for n in ['wrist','hand']:by[side+'_'+n]['pivot']=w.copy()
  put(side+'_upper_arm',steps(c,a,e,3));put(side+'_elbow',[c([s*6-2,16.5,-1.75],[4,2.5,2.5],3)])
  put(side+'_forearm',steps(c,e,w,2.5));put(side+'_wrist',[c([s*6-1.5,11.5,-2.5],[3,2,3],2)])
  r.bone(side+'_folded_sleeve',side+'_upper_arm',a,[c([s*6-2.5,19,-2],[5,4,4]),c([s*6-3,19,-2.25],[6,1.25,4.5],3)])
  r.bone(side+'_paper_skirt','pelvis',[s*3,11,0],[c([s*3-2.25,6.5,-2.5],[4.5,5,1.5]),c([s*3-2.25,6.5,1.5],[4.5,5,1.5],2)])
  x=s*2.5;k=5.875
  for n in ['thigh','knee','shin','ankle','foot']:by[side+'_'+n]['pivot'][0]=x
  put(side+'_thigh',[c([x-1.5,k,-1.5],[3,5.125,3])]);put(side+'_knee',[c([x-1.75,k-1,-1.75],[3.5,2,3.5],3)])
  put(side+'_shin',[c([x-1.25,1.5,-1.25],[2.5,k-1,2.5],2)])
  put(side+'_ankle',[c([x-1.5,1,-1.5],[3,2,3])]);put(side+'_foot',[c([x-1.75,.125,-3],[3.5,1.75,5],2),c([x-1.75,1,-3],[3.5,1,2],3)])
  if side=='right':
   by['paper_sword']['pivot']=w.copy();by['paper_sword']['rotation']=[0,0,50];fist(r,by,side,w,[0,0,50]);put('right_hand',[])
  else:put('left_hand',[c([w[0]-1.25,w[1]-1.5,w[2]-1.5],[2.5,3,3],3)])
 x,y,z=by['paper_sword']['pivot']
 put('paper_sword',[c([x-.625,y-1,z-.625],[1.25,4,1.25],2),c([x-2.25,y-1.5,z-1],[4.5,1.25,2],3),c([x-1.25,y-15,z-.625],[2.5,13.5,1.25]),c([x-.75,y-16.5,z-.625],[1.5,2,1.25],3),c([x-1.25,y-10,z-.875],[1.25,8.5,.75],3)])
 ordered(r)
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'head':wave(1,ticks,1.25)}
  if name!='idle':
   for side,s in [('right',-1),('left',1)]:
    ph=0 if s<0 else math.pi;amp=12 if name=='walk' else 24
    ch[side+'_thigh']=wave(0,ticks,amp,ph);ch[side+'_knee']=wave(0,ticks,-amp*.35,ph);ch[side+'_ankle']=wave(0,ticks,-amp*.65,ph);ch[side+'_shoulder']=wave(0,ticks,-amp*.35,ph)
  clip(r,name,ch,True)
 clip(r,'attack',{'waist_upper':track('rotation',[(0,[0,0,0]),(2,[0,-18,0]),(6,[0,28,0]),(20,[0,0,0])]),'right_shoulder':track('rotation',[(0,[0,0,0]),(2,[-65,0,-20]),(6,[-85,0,30]),(20,[0,0,0])]),'right_elbow':track('rotation',[(0,[0,0,0]),(2,[25,0,0]),(6,[-5,0,0]),(20,[0,0,0])]),'left_shoulder':track('rotation',[(0,[0,0,0]),(6,[-15,0,-20]),(20,[0,0,0])])})
 clip(r,'shed',{'chest':track('scale',[(0,[1,1,1]),(2,[1,.4,1]),(6,[1,.75,1]),(12,[1,1,1]),(16,[1,1,1])]),'right_shoulder':track('rotation',[(0,[0,0,0]),(2,[0,0,-25]),(6,[0,0,-15]),(16,[0,0,0])]),'left_shoulder':track('rotation',[(0,[0,0,0]),(2,[0,0,25]),(6,[0,0,15]),(16,[0,0,0])])})
 clip(r,'hurt',{'chest':track('rotation',[(0,[0,0,0]),(2,[-8,0,0]),(8,[0,0,0])])})
 clip(r,'death',{'pelvis':track('position',[(0,[0,0,0]),(8,[0,-5,0]),(10,[0,-5,0])]),'waist_upper':track('rotation',[(0,[0,0,0]),(8,[70,0,0]),(10,[70,0,0])]),**{side+'_thigh':track('rotation',[(0,[0,0,0]),(8,[0,0,s*40]),(10,[0,0,s*40])]) for side,s in [('right',-1),('left',1)]}})

def preserve_legacy():
 hashes={}
 for name in IDS:
  for rel,wanted in json.loads((OUT/'source'/name/'baseline.manifest.json').read_text()).items():
   actual=hashlib.sha256((REPO/rel).read_bytes()).hexdigest();assert actual==wanted,'Concurrent legacy change: '+rel;hashes[rel]=actual
 return hashes
def main():
 legacy=preserve_legacy();guard=OUT/'child-paper-owned-hashes.json';owned=json.loads(guard.read_text()) if guard.exists() else {}
 for name in IDS:
  for p in resource_paths(name):
   assert not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()==owned.get(str(p)),'Concurrent new-art edit: '+str(p)
 for name,spec,builder in zip(IDS,SPECS,[child,paper]):
  r=Rig(name,*spec);builder(r);r.save();print(name,len(r.bones),'bones',sum(len(b.get('cubes',[])) for b in r.bones),'cuboids',flush=True)
  for p in resource_paths(name):owned[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
  guard.write_text(json.dumps(owned,indent=2)+'\n')
 from contacts import settle
 try:settle(IDS)
 finally:
  for name in IDS:
   for p in resource_paths(name):owned[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
  guard.write_text(json.dumps(owned,indent=2)+'\n')
 for name in IDS:(OUT/'blockbench'/(name+'.animation.json')).write_bytes(resource_paths(name)[1].read_bytes())
 assert preserve_legacy()==legacy
 (OUT/'legacy-preservation-child-paper.json').write_text(json.dumps(dict(passed=True,unchanged_legacy=legacy),indent=2)+'\n')
if __name__=='__main__':main()
