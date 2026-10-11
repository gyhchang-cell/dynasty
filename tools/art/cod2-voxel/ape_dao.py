"""Original low crouching mountain ape and armored dao profession."""
import json,hashlib,math
from build_models import Rig,track,OUT,ASSETS
from mechanicals import clip,lengths,wave
from armies_tree import skeleton,steps,fist,human_end
from corpse_ghost_palanquin_flag import ordered

IDS=['shanjing_shanxiao','zuwu_daoshou']
SPECS=[
 (['#ffffff','#446f66','#242e34','#b6a26e'],['..111..','.11311.','1132311','1122211','1111111','.11.11.','.33.33.']),
 (['#ffffff','#4c6159','#242e31','#b69b61'],['.22222.','..323..','.11111.','1131133','.111113','.12.1.3','.22.2.3']),
]

def ape(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 put('pelvis',[c([-4.5,5,3],[9,7,8]),c([-4,10,4],[8,2,7],2)])
 put('waist',[c([-4,7,-1],[8,6,7],2)])
 put('chest',[c([-6,6,-8],[12,8,12]),c([-6.5,10,-7],[13,4,10]),c([-5.5,7,-8.75],[11,5,1.5],2)])
 put('neck',[c([-3,8,-10],[6,5,5],2)])
 put('head',[c([-5,8.5,-15],[10,6,8]),c([-4.5,9,-17],[9,4.5,3],2),c([-2,10.5,-18],[4,2,1.5],3),c([-4.5,13,-16],[3,2,2],3),c([1.5,13,-16],[3,2,2],3)])
 put('jaw',[c([-4,6.5,-17],[8,2.5,8]),c([-4,8.5,-17.5],[2,3,2],3),c([2,8.5,-17.5],[2,3,2],3)])
 r.bone('ape_brow','head',[0,14,-13],[c([-5.5,14,-16],[11,2,3],2),c([-2,15,-15],[4,2,3],1)])
 for side,s in [('right',-1),('left',1)]:
  r.bone(side+'_ape_cheek','head',[s*5,11,-10],[c([s*5-1.5,8,-13],[3,8,7],1),c([s*5-2,12,-10],[4,4,5],2)])
  for n in ['climb_wrist','wrist']:by[side+'_'+n]['pivot'][1]=2.075
  a=by[side+'_shoulder']['pivot'];e=by[side+'_elbow']['pivot'];w=by[side+'_wrist']['pivot'];h=by[side+'_hand']['pivot']
  put(side+'_upper_arm',steps(c,a,e,4.5));put(side+'_elbow',[c([e[0]-2.5,5.5,e[2]-2.5],[5,3,5],2)])
  put(side+'_forearm',steps(c,e,w,4,2));put(side+'_wrist',[c([w[0]-2.5,1,w[2]-2.5],[5,2.5,5])])
  put(side+'_hand',[c([h[0]-2.75,.125,-10],[5.5,2.5,6],2),*[c([h[0]+i*1.75-.75,.125,-12],[1.5,1.5,3],3) for i in [-1,0,1]]])
  by[side+'_claw_contact']['pivot']=[h[0],.125,-11.5]
  # Leg crouch is explicit coarse stepped geometry, not a human standing rig.
  for n in ['thigh','shin']:by[side+'_'+n].pop('rotation',None)
  for n in ['climb_ankle','ankle']:by[side+'_'+n]['pivot'][1]=1.845
  a=by[side+'_thigh']['pivot'];e=by[side+'_knee']['pivot'];w=by[side+'_ankle']['pivot'];x=w[0]
  put(side+'_thigh',steps(c,a,e,4.5));put(side+'_knee',[c([x-2.5,3,e[2]-2.5],[5,3,5],2)])
  put(side+'_shin',steps(c,e,w,3.5,2));put(side+'_ankle',[c([x-2,0.5,w[2]-2],[4,2,4])])
  by[side+'_foot']['pivot'][1]=1
  put(side+'_foot',[c([x-2.5,.125,4.5],[5,2,7],2),c([x-2.5,.125,3.5],[2,1.5,2],3),c([x+.5,.125,3.5],[2,1.5,2],3)])
  by[side+'_foot_contact']['pivot']=[x,.125,4.75]
 for i in range(5):
  z=-5+i*2.75;y=14-i*.5
  put('spine_'+str(i),[c([-1.5,y-1,z-1.5],[3,3.5 if i<3 else 2.5,3],2)])
 put('tail',[c([-1.5,8.5,9],[3,3,5],1)])
 put('tail_hook',[c([-1,10,12],[2,4,3],2),c([-1,13,10],[2,2,4],2)])
 r.bone('held_rock','right_hand',[-5.375,3,-8],[c([-8,1,-11],[5,5,5],3),c([-7.5,5.5,-10.5],[4,1.5,4],2)])
 ordered(r)
 for name in ['idle','walk','run','climb']:
  ticks=lengths(r)[name];ch={'head':wave(1,ticks,1.5),'jaw':wave(0,ticks,2),'tail':wave(1,ticks,3),'held_rock':{'scale':[.001,.001,.001]}}
  if name!='idle':
   amp=10 if name=='walk' else 18 if name=='run' else 6
   for side,s in [('right',-1),('left',1)]:
    ph=0 if s==1 else math.pi
    ch[side+'_shoulder']=wave(0,ticks,amp,ph);ch[side+'_elbow']=wave(0,ticks,-amp*.4,ph);ch[side+'_wrist']=wave(0,ticks,-amp*.6,ph)
    ch[side+'_thigh']=wave(0,ticks,-amp,ph);ch[side+'_knee']=wave(0,ticks,amp*.4,ph);ch[side+'_ankle']=wave(0,ticks,amp*.6,ph)
  clip(r,name,ch,True)
 for name in ['attack','skill']:
  ch={'chest':track('rotation',[(0,[0,0,0]),(10,[12,0,0]),(14,[-5,0,0]),(24,[18,0,0]),(42,[0,0,0])]),'jaw':track('rotation',[(0,[0,0,0]),(10,[12,0,0]),(14,[28,0,0]),(24,[35,0,0]),(42,[0,0,0])]),'held_rock':{'scale':[.001,.001,.001]}}
  for side in ['right','left']:ch[side+'_shoulder']=track('rotation',[(0,[0,0,0]),(10,[20,0,0]),(14,[-65,0,0]),(20,[-45,0,0]),(24,[20,0,0]),(42,[0,0,0])])
  clip(r,name,ch)
 clip(r,'rock',{'chest':track('rotation',[(0,[0,0,0]),(12,[0,-18,0]),(18,[0,24,0]),(32,[0,0,0])]),'right_shoulder':track('rotation',[(0,[0,0,0]),(12,[-125,0,-12]),(17,[-125,0,-12]),(18,[-55,0,8]),(24,[-30,0,0]),(32,[0,0,0])]),'right_elbow':track('rotation',[(0,[0,0,0]),(12,[-20,0,0]),(18,[20,0,0]),(32,[0,0,0])]),'held_rock':track('scale',[(0,[1,1,1]),(17,[1,1,1]),(18,[.001,.001,.001]),(32,[.001,.001,.001])])})
 clip(r,'hurt',{'chest':track('rotation',[(0,[0,0,0]),(2,[-8,0,0]),(10,[0,0,0])]),'held_rock':{'scale':[.001,.001,.001]}})
 clip(r,'death',{'chest':track('rotation',[(0,[0,0,0]),(24,[0,0,20]),(32,[0,0,20])]),'head':track('rotation',[(0,[0,0,0]),(24,[25,0,0]),(32,[25,0,0])]),'jaw':track('rotation',[(0,[0,0,0]),(24,[35,0,0]),(32,[35,0,0])]),'tail_hook':track('rotation',[(0,[0,0,0]),(24,[0,0,65]),(32,[0,0,65])]),'held_rock':{'scale':[.001,.001,.001]}})

def dao(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 hip=by['pelvis']['pivot'][1];top=by['chest']['pivot'][1];hy=by['head']['pivot'][1]
 put('pelvis',[c([-4.5,hip-2,-3.5],[9,4,7]),c([-5,hip,-4],[10,2,8],3)])
 put('waist',[c([-3.5,hip+1,-3],[7,3,6],2)]);put('waist_upper',[c([-4,hip+3,-3.5],[8,3,7])])
 put('chest',[c([-5.5,hip+5,-3.5],[11,top-hip-4,7]),c([-6,top-2,-4],[12,2,8],2)])
 put('chest_front',[c([-5.5,hip+5,-5],[11,top-hip-5,1.5]),c([-1.5,hip+5,-5.5],[3,top-hip-5,1],3)])
 put('chest_back',[c([-5.5,hip+5,3.5],[11,top-hip-5,1.5],2)])
 put('neck',[c([-2,top-1,-2],[4,2,4],2)])
 put('head',[c([-3.5,hy-2.5,-3.5],[7,5.5,7],2),c([-3,hy-2,-4.5],[6,4,1],3),c([-3,hy-.25,-5],[6,1.5,.5],2)])
 put('helmet',[c([-6.5,hy+1.5,-6],[13,1.5,12],2),c([-5,hy+3,-4.5],[10,1.5,9],2),c([-3,hy+4.5,-3],[6,1.5,6],1),c([-4.5,hy-2,-2],[1.5,4,5]),c([3,hy-2,-2],[1.5,4,5])])
 put('chin_cord',[c([-3.5,hy-3,-4.5],[7,1.5,2],2),c([-1,hy-4,-4],[2,2,2],3)])
 put('belt',[c([-5,hip,-4],[10,2,8],2),c([-1.5,hip,-5],[3,2,1.5],3)])
 for side,s in [('right',-1),('left',1)]:
  a=[s*6,top,0];e=[s*6,17.125,-.375];w=[s*6,12,-.625]
  for n in ['shoulder','upper_arm']:by[side+'_'+n]['pivot']=a.copy()
  for n in ['elbow','forearm']:by[side+'_'+n]['pivot']=e.copy()
  for n in ['wrist','hand']:by[side+'_'+n]['pivot']=w.copy()
  put(side+'_upper_arm',steps(c,a,e,3.5));put(side+'_elbow',[c([e[0]-2,e[1]-1.5,e[2]-2],[4,3,4],2)])
  put(side+'_forearm',steps(c,e,w,3.5,2));put(side+'_wrist',[c([w[0]-1.75,w[1]-1.75,w[2]-1.75],[3.5,3.5,3.5])])
  if side=='right':
   by['dao']['pivot']=w.copy();by['right_grip']['pivot']=w.copy();fist(r,by,'right',w,[0,0,43])
  else:put('left_hand',[c([w[0]-1.5,w[1]-1.5,w[2]-2],[3,3,4],3)])
  put(side+'_shoulder_plate',[c([s*6-3,top-2,-4],[6,3,8],2),c([s*6-2.5,top+1,-3],[5,1.5,6],3)])
  put(side+'_rag',[c([s*6-2,top-5,-4.75],[4,5,1.5],1),c([s*6-2,top-5,-5],[4,2,1],3)])
  put('skirt_'+side,[c([s*2.5-2.5,hip-6,-3.75],[5,6,1.5],2),c([s*2.5-2.5,hip-6,-4],[5,2,2],3)])
  x=by[side+'_thigh']['pivot'][0];k=by[side+'_knee']['pivot'][1]
  put(side+'_thigh',[c([x-1.75,k,-2.5],[3.5,hip-k,5],2),c([x-2,hip-4,-3],[4,3,6])])
  put(side+'_knee',[c([x-2,k-1,-3],[4,2.5,6],3)]);put(side+'_shin',[c([x-1.75,1.5,-2],[3.5,k-1,4],2)])
  put(side+'_ankle',[c([x-1.75,1,-2.5],[3.5,2,5])]);put(side+'_foot',[c([x-2,.125,-4],[4,2,7],2),c([x-2,1,-4],[4,1.5,2],3)])
 x,y,z=by['dao']['pivot']
 put('dao',[c([x-.625,y-1.5,z-.625],[1.25,5,1.25],2),c([x-2,y-1.5,z-1],[4,1,2],3),c([x-1,y-10,z-.75],[2,8.5,1.5],3),c([x,y-7,z-.75],[1,6,1.5],3),c([x-.5,y-11.5,z-.75],[1.5,2,1.5],3)])
 put('scabbard',[c([2,2.5,.25],[2,13,2],2),c([1.5,13,0],[3,2,2.5],3),c([1.5,2.5,0],[3,2,2.5],3)])
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'head':wave(1,ticks,.75)}
  if name!='idle':
   amp=12 if name=='walk' else 24
   for side,s in [('right',-1),('left',1)]:
    ph=0 if s==1 else math.pi
    ch[side+'_thigh']=wave(0,ticks,amp,ph);ch[side+'_knee']=wave(0,ticks,-amp*.35,ph);ch[side+'_ankle']=wave(0,ticks,-amp*.65,ph);ch[side+'_shoulder']=wave(0,ticks,-amp*.4,ph)
  clip(r,name,ch,True)
 ch={'waist_upper':track('rotation',[(0,[0,0,0]),(8,[0,-24,0]),(12,[0,24,0]),(17,[0,20,0]),(22,[0,-25,0]),(36,[0,0,0])]),'right_shoulder':track('rotation',[(0,[0,0,0]),(8,[-65,0,-25]),(12,[-75,0,25]),(17,[-45,0,25]),(22,[-75,0,-25]),(36,[0,0,0])]),'right_elbow':track('rotation',[(0,[0,0,0]),(8,[30,0,0]),(12,[-5,0,0]),(17,[20,0,0]),(22,[-10,0,0]),(36,[0,0,0])]),'left_shoulder':track('rotation',[(0,[0,0,0]),(12,[-20,0,15]),(22,[-20,0,-15]),(36,[0,0,0])])}
 for name in ['attack','skill']:clip(r,name,ch)
 human_end(r)

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--ids',nargs='+',choices=IDS,default=IDS);selected=p.parse_args().ids
 owned_path=OUT/'ape-dao-owned-hashes.json';owned=json.loads(owned_path.read_text()) if owned_path.exists() else {}
 for name in selected:
  for folder,suffix,original in [('geo','.geo.json','original.geo.json'),('animations','.animation.json','original.animation.json')]:
   current=ASSETS/f'{folder}/blueprint/{name}{suffix}'
   assert current.read_bytes()==(OUT/'source'/name/original).read_bytes() or hashlib.sha256(current.read_bytes()).hexdigest()==owned.get(str(current)),'Concurrent modification '+name
 for name,spec,builder in zip(IDS,SPECS,[ape,dao]):
  if name not in selected:continue
  r=Rig(name,*spec);builder(r);r.save();print(name,len(r.bones),'bones',sum(len(b.get('cubes',[])) for b in r.bones),'cuboids',flush=True)
  for folder,suffix in [('geo','.geo.json'),('animations','.animation.json')]:
   current=ASSETS/f'{folder}/blueprint/{name}{suffix}';owned[str(current)]=hashlib.sha256(current.read_bytes()).hexdigest()
  owned_path.write_text(json.dumps(owned,indent=2)+'\n')
 from contacts import settle
 try:settle(selected)
 finally:
  for name in selected:
   for folder,suffix in [('geo','.geo.json'),('animations','.animation.json')]:
    current=ASSETS/f'{folder}/blueprint/{name}{suffix}';owned[str(current)]=hashlib.sha256(current.read_bytes()).hexdigest()
  owned_path.write_text(json.dumps(owned,indent=2)+'\n')
 for name in selected:
  a=ASSETS/f'animations/blueprint/{name}.animation.json';(OUT/'blockbench'/(name+'.animation.json')).write_bytes(a.read_bytes())
if __name__=='__main__':main()
