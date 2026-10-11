"""Authored cuboid professions and a dedicated flying skull rig; no battle edits."""
import hashlib,json,math
from build_models import Rig,track,OUT,ASSETS
from mechanicals import clip,lengths,wave
from armies_tree import skeleton,steps,fist,human_end
IDS=['ludun_jiashi','muxue_feilu','pijia_panjiang_huwei','tiesuo_chihou']
SPECS=[
 (['#ffffff','#54635c','#252f2b','#b29562'],['..111..','..323..','.11111.','1333331','1222221','1333331','1222221']),
 (['#ffffff','#b5ad94','#2c292b','#773f3b'],['.31113.','1111111','1221221','1111111','.21212.','.3.3.3.','.3.3.3.']),
 (['#ffffff','#48615a','#252f32','#b79657'],['.3.3.3.','..323..','3111113','1331331','.11111.','.21212.','.22.22.']),
 (['#ffffff','#49636a','#242d35','#b18c60'],['..222..','..323..','.11111.','3111113','.1211.3','.21212.','.22.223'])
]

def human(r,job):
 by=skeleton(r);c=r.cube
 def put(n,items):by[n]['cubes']=items
 hip=by['pelvis']['pivot'][1];top=by['chest']['pivot'][1];hy=by['head']['pivot'][1]
 wide,depth=(12,8) if job=='shield' else (13,9) if job=='guard' else (8,6)
 waist,hips=(8,10) if job=='shield' else (8,11) if job=='guard' else (6,8)
 put('pelvis',[c([-hips/2,hip-2,-depth/2],[hips,4,depth]),c([-hips/2-.5,hip,-depth/2-.5],[hips+1,2,depth+1],3)])
 put('waist',[c([-waist/2,hip+1,-depth/2+.5],[waist,3,depth-1],2)])
 put('waist_upper',[c([-waist/2-.5,hip+3,-depth/2],[waist+1,3,depth])])
 put('chest',[c([-wide/2,hip+5,-depth/2],[wide,top-hip-4,depth]),c([-wide/2-.5,top-2,-depth/2-.5],[wide+1,2,depth+1],2)])
 put('chest_front',[c([-wide/2,hip+5,-depth/2-1.5],[wide,top-hip-5,1.5]),c([-1.5,hip+5,-depth/2-2],[3,top-hip-5,.5],3)])
 put('chest_back',[c([-wide/2,hip+5,depth/2],[wide,top-hip-5,1.5])])
 put('neck',[c([-2,top-1,-2],[4,2,4],2)])
 put('head',[c([-3.5,hy-2.5,-3.5],[7,5.5,7],2),c([-3,hy-2,-4.5],[6,4,1],3),c([-3,hy-.25,-5],[6,1.5,.5],2)])
 if job=='scout':
  for side,s in [('right',-1),('left',1)]:
   for n in ['shoulder','upper_arm']:by[side+'_'+n]['pivot']=[s*5,top,0]
   for n in ['elbow','forearm']:by[side+'_'+n]['pivot']=[s*6.25,18.25,-1.25]
   for n in ['wrist','hand','grip','claw']:by[side+'_'+n]['pivot']=[s*6,13.125,-2]
 else:
  for side in ['right','left']:
   center=by[side+'_hand']['pivot'].copy();center[1]=by[side+'_grip']['pivot'][1]
   for n in ['wrist','hand','grip']:by[side+'_'+n]['pivot']=center.copy()
 if job=='shield':
  for n in ['wrist','hand','grip']:by['left_'+n]['pivot']=[4.75,18,-3.75]
  for n in ['elbow','forearm']:by['left_'+n]['pivot']=[6.5,20,-1]
  by['shield_grip']['pivot']=[4.75,18,-3.75]
 for side,s in [('right',-1),('left',1)]:
  a=by[side+'_shoulder']['pivot'];e=by[side+'_elbow']['pivot'];w=by[side+'_hand']['pivot']
  put(side+'_upper_arm',steps(c,a,e,3.5 if job=='scout' else 4.5))
  put(side+'_elbow',[c([e[0]-2,e[1]-1.5,e[2]-2],[4,3,4],2)])
  put(side+'_forearm',steps(c,e,w,3.5 if job=='scout' else 4,2))
  put(side+'_wrist',[c([w[0]-2,w[1]-1.75,w[2]-2],[4,3.5,4])])
  fist(r,by,side,w,by[side+'_grip'].get('rotation'))
  x=by[side+'_thigh']['pivot'][0];z=by[side+'_thigh']['pivot'][2];k=by[side+'_knee']['pivot'][1]
  width=4 if job!='scout' else 3.5
  put(side+'_thigh',[c([x-width/2,k,z-2.5],[width,hip-k,5],2),c([x-width/2-.25,hip-4,z-3],[width+.5,3,6])])
  put(side+'_knee',[c([x-width/2-.25,k-1,z-3],[width+.5,2.5,6],3)])
  put(side+'_shin',[c([x-width/2,1.5,z-2],[width,k-1,4],2),c([x-width/2,2,z-2.75],[width,k-2,1.5])])
  put(side+'_ankle',[c([x-width/2,1,z-2.5],[width,2,5],2)])
  put(side+'_foot',[c([x-width/2-.25,.125,z-4.5],[width+.5,2,7.5],2),c([x-width/2-.25,1,z-4.5],[width+.5,1.5,2],3)])
 return by

def locomotion(r,job):
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'head':wave(1,ticks,.8)}
  if name!='idle':
   for side,s in [('right',-1),('left',1)]:
    ph=0 if s==1 else math.pi;amp=(10 if name=='walk' else 17) if job=='shield' else (14 if name=='walk' else 25)
    ch[side+'_thigh']=wave(0,ticks,amp,ph);ch[side+'_knee']=wave(0,ticks,-amp*.35,ph);ch[side+'_ankle']=wave(0,ticks,-amp*.65,ph)
    if job!='shield':ch[side+'_shoulder']=wave(0,ticks,-amp*.5,ph)
  if job=='guard':
   for i,n in enumerate(['cape_upper','cape_mid','cape_lower']):ch[n]=wave(0,ticks,1 if name=='idle' else 3+i,i*.5)
  if job=='scout':
   for side,s in [('right',-1),('left',1)]:
    for i in range(8):ch[side+'_chain_'+str(i)]=wave(2,ticks,(.5 if name=='idle' else 1.5),i*.6+s)
  clip(r,name,ch,True)

def shield(r):
 by=human(r,'shield');c=r.cube
 def put(n,v):by[n]['cubes']=v
 hy=by['head']['pivot'][1];hip=by['pelvis']['pivot'][1];top=by['chest']['pivot'][1]
 put('helmet',[c([-4.5,hy+1.5,-4.5],[9,2,9]),c([-3.5,hy+3,-3.5],[7,1.25,7]),c([-4.5,hy-2,-2.5],[1.5,5,6]),c([3,hy-2,-2.5],[1.5,5,6]),c([-1,hy+4,-2],[2,1,4],3)])
 for side,s in [('right',-1),('left',1)]:
  x=s*6.5;put(side+'_shoulder_plate',[c([x-3,top-3,-4.5],[6,4,9]),c([x-2.5,top+1,-3],[5,2.5,6],3)])
  x=by[side+'_thigh']['pivot'][0];put(side+'_hip_plate',[c([x-2.5,hip-3,-3.75],[5,4,1.5])]);put(side+'_hip_plate_lower',[c([x-2.5,hip-7,-3.75],[5,4,1.5]),c([x-2.5,hip-7,-4],[5,1.5,2],3)])
 put('shield',[c([-7,3,-6.25],[14,27,2.5],2),c([-8,3,-6.75],[2,27,3.5],3),c([6,3,-6.75],[2,27,3.5],3),*[c([-6,y,-7],[12,2.5,3.5],3) for y in [3,15.25,27.5]],c([-2,15,-7.5],[4,4,1.5]),c([-1,18.5,-7.5],[2,2,1.5],3)])
 put('shield_grip',[c([4.125,16.5,-4.375],[1.25,3,1.25],2),c([3.5,15.5,-4.375],[2.5,1,2.5]),c([3.5,19.5,-4.375],[2.5,1,2.5])])
 x,y,z=by['right_hand']['pivot'];by['mace']['pivot']=[x,y,z]
 put('mace',[c([x-.625,y-4,z-.625],[1.25,16,1.25],2),c([x-2.5,y+8,z-2.5],[5,5,5],3),c([x-3.5,y+9,z-1.5],[7,3,3]),c([x-1.5,y+9,z-3.5],[3,3,7])])
 locomotion(r,'shield')
 # The production controller selects attack for both shield impacts; retain its old skill clip too.
 bash={'chest':track('position',[(0,[0,0,0]),(12,[0,0,1]),(16,[0,0,-3]),(20,[0,0,-1]),(32,[0,0,0])]),'right_shoulder':track('rotation',[(0,[0,0,0]),(18,[30,0,-10]),(24,[-80,0,-8]),(28,[-45,0,0]),(32,[0,0,0])]),'right_elbow':track('rotation',[(0,[0,0,0]),(18,[25,0,0]),(24,[-12,0,0]),(32,[0,0,0])])}
 for name in ['attack','skill']:clip(r,name,bash)
 human_end(r)

def guard(r):
 by=human(r,'guard');c=r.cube
 def put(n,v):by[n]['cubes']=v
 hy=by['head']['pivot'][1];hip=by['pelvis']['pivot'][1];top=by['chest']['pivot'][1]
 put('helmet',[c([-4.5,hy+1.5,-4.5],[9,2,9]),c([-3,hy+3,-3],[6,1.5,6]),c([-1,hy+4,-2],[2,1.5,4],3),c([-5,hy-.5,-1.5],[2,4,5]),c([3,hy-.5,-1.5],[2,4,5]),c([-6,hy+2,0],[2,3,3],3),c([4,hy+2,0],[2,3,3],3)])
 put('chest_mirror',[c([-3,hip+6,-6.25],[6,6,1.5],3),c([-2,hip+7,-6.875],[4,4,1],2)])
 for side,s in [('right',-1),('left',1)]:
  x=s*7;put(side+'_beast_shoulder',[c([x-3.5,top-2,-4.5],[7,5,9]),c([x-3,top-2,-5.5],[6,3,1.5],2),c([x-2.5,top-.5,-6],[2,2,1],3),c([x+.5,top-.5,-6],[2,2,1],3),c([x-3,top+3,-3],[2,3,3],3),c([x+1,top+3,-3],[2,3,3],3),c([x-4,top+5,-3],[3,2,3],3),c([x+1,top+5,-3],[3,2,3],3)])
  put(side+'_hip_plate',[c([s*3-3,hip-7,-4.5],[6,8,1.5]),c([s*3-3,hip-7,-4.75],[6,2,2],3)])
  x,y,z=by[side+'_hand']['pivot'];by[side+'_axe']['pivot']=[x,y,z];by[side+'_axe_trail']['pivot']=[x,y+8,z]
  by[side+'_axe']['rotation']=[0,0,s*25]
  fist(r,by,side,[x,y,z],[0,0,s*25])
  bladeX=x-6 if s<0 else x-2
  put(side+'_axe',[c([x-.625,y-10,z-.625],[1.25,23,1.25],2),c([x-1.5,y+7,z-1.5],[3,6,3]),c([bladeX,y+8,z-1.75],[8,5,3.5],3),c([bladeX,y+5,z-1.75],[5 if s<0 else 8,3,3.5],3)])
 # A thick three-panel cape is independent of the hips; its bottom remains above the feet.
 r.bone('cape_upper','chest',[0,top,5.5],[c([-5.5,top-9,5.5],[11,9,1.5],2),c([-6,top-3,6],[12,3,1.5])])
 r.bone('cape_mid','cape_upper',[0,top-9,6.25],[c([-6.5,top-18,6],[13,9,1.5],2)])
 r.bone('cape_lower','cape_mid',[0,top-18,6.75],[c([-7,3,6.5],[5,top-21,1.5],2),c([-1.5,4,6.5],[9,top-22,1.5],2),c([-7,3,7],[14.5,2,1],3)])
 locomotion(r,'guard')
 ch={'waist_upper':track('rotation',[(0,[0,0,0]),(12,[0,-14,0]),(16,[0,12,0]),(22,[0,-12,0]),(42,[0,0,0])])}
 for side,s in [('right',-1),('left',1)]:
  ch[side+'_shoulder']=track('rotation',[(0,[0,0,0]),(12,[-40,0,s*22]),(16,[-75,0,s*-25]),(19,[-40,0,s*15]),(22,[-45,0,s*35]),(42,[0,0,0])])
  ch[side+'_elbow']=track('rotation',[(0,[0,0,0]),(12,[25,0,0]),(16,[-12,0,0]),(22,[15,0,0]),(42,[0,0,0])])
 clip(r,'attack',ch)
 clip(r,'counter',{'waist_upper':track('rotation',[(0,[0,0,0]),(6,[0,-35,0]),(10,[0,120,0]),(18,[0,240,0]),(34,[0,360,0])]),**{side+'_shoulder':track('rotation',[(0,[0,0,0]),(6,[-15,0,s*35]),(10,[-15,0,s*70]),(18,[-15,0,s*70]),(34,[0,0,0])]) for side,s in [('right',-1),('left',1)]}})
 human_end(r)

def scout(r):
 by=human(r,'scout');c=r.cube
 def put(n,v):by[n]['cubes']=v
 hy=by['head']['pivot'][1];hip=by['pelvis']['pivot'][1];top=by['chest']['pivot'][1]
 put('headwrap',[c([-4.5,hy+1.5,-4.5],[9,2,9],2),c([-3.5,hy+3,-3.5],[7,1.25,7],2),c([-4.5,hy-2,-2.5],[1.5,5,6],2),c([3,hy-2,-2.5],[1.5,5,6],2),c([3.5,hy+1,2],[3,2,5],1)])
 put('belt',[c([-4.5,hip,-3.5],[9,2,7],2),c([-1.5,hip,-4.5],[3,2,1],3)])
 put('cross_straps',[c([-4,hip+8,-4.75],[8,2,1.5],2),c([-1,hip+5,-4.75],[2,top-hip-5,1.5],3)])
 r.bone('scout_pauldron','right_shoulder',[-5,top,0],[c([-8,top-2,-3.5],[6,3,7]),c([-8.5,top-2,-4],[7,1.5,8],3)])
 r.bone('rope_pack','chest',[0,top-5,4.5],[c([-3.5,top-9,4.5],[7,7,4],2),c([-3,top-8,8],[6,2,1.5],3),c([-3,top-4,8],[6,2,1.5],3)])
 for side,s in [('right',-1),('left',1)]:
  x,y,z=by[side+'_hand']['pivot'];put(side+'_claw',[c([x-.625,y-1.5,z-.625],[1.25,4,1.25],2),c([x-2.5,y+1.5,z-1],[5,1.5,2],3),c([x-2.5,y-5,z-1],[1.5,7,2],3),c([x+1,y-5,z-1],[1.5,7,2],3),c([x-2.5,y-5,z-2],[4,1.5,1.5],3)])
  # Eight broad rectangular segments form a hanging loop without the original tiny chain mesh.
  points=[[s*4.5,hip+1,3.5],[s*6.5,hip-1.5,3.5],[s*7.5,hip-4,3.5],[s*7.5,hip-6,3.5],[s*6,hip-6,3.5],[s*4.5,hip-4,3.5],[s*4.5,hip-1.5,3.5],[s*4.5,hip+1,3.5]]
  by[side+'_chain_spring']['pivot']=points[0].copy()
  for i,p in enumerate(points):
   p=[round(v*8)/8 for v in p];by[side+'_chain_'+str(i)]['pivot']=p
   q=points[min(i+1,7)] if i<7 else [p[0],p[1]+1,p[2]]
   put(side+'_chain_'+str(i),[c([min(p[j],q[j])-1 for j in range(3)],[abs(q[j]-p[j])+2 for j in range(3)],3 if i%2==0 else 2)])
 locomotion(r,'scout')
 clip(r,'attack',{'waist_upper':track('rotation',[(0,[0,0,0]),(6,[0,-20,0]),(9,[0,20,0]),(12,[0,10,0]),(15,[0,-20,0]),(30,[0,0,0])]),'right_shoulder':track('rotation',[(0,[0,0,0]),(6,[-25,0,-18]),(9,[-70,0,8]),(15,[-20,0,-8]),(30,[0,0,0])]),'left_shoulder':track('rotation',[(0,[0,0,0]),(9,[-20,0,8]),(15,[-70,0,-8]),(30,[0,0,0])])})
 clip(r,'grapple',{'chest':track('rotation',[(0,[0,0,0]),(8,[-8,0,0]),(12,[-5,0,0]),(40,[-5,0,0]),(58,[0,0,0])]),'right_shoulder':track('rotation',[(0,[0,0,0]),(8,[-25,0,-10]),(12,[-90,0,0]),(40,[-85,0,0]),(58,[0,0,0])]),'right_elbow':track('rotation',[(0,[0,0,0]),(8,[25,0,0]),(12,[-10,0,0]),(40,[-10,0,0]),(58,[0,0,0])])})
 clip(r,'knee',{'chest':track('rotation',[(0,[0,0,0]),(4,[8,0,0]),(6,[15,0,0]),(18,[0,0,0])]),'right_thigh':track('rotation',[(0,[0,0,0]),(4,[-30,0,0]),(6,[-65,0,0]),(18,[0,0,0])]),'right_knee':track('rotation',[(0,[0,0,0]),(4,[45,0,0]),(6,[85,0,0]),(18,[0,0,0])])})
 human_end(r)

def skull(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 put('head',[c([-5.5,15,-4],[11,7,8]),c([-4.5,14,-4.75],[9,6,1.5]),c([-5.5,13,-3],[3,4,5]),c([2.5,13,-3],[3,4,5]),c([-3.75,15.5,-5.75],[3,3,1.5],2),c([.75,15.5,-5.75],[3,3,1.5],2),c([-1,13.5,-6],[2,3,1.5],2),c([-4.5,12,-4.5],[2,2,1.5]),c([-.75,12,-4.5],[1.5,2,1.5]),c([2.5,12,-4.5],[2,2,1.5])])
 put('brow',[c([-5,18.5,-6],[10,2,1.5]),c([-2.5,20,-5],[5,2,1.5])])
 put('jaw',[c([-4,10.5,-4.75],[8,2.5,2]),c([-4.5,10.5,-3],[2,2.5,6]),c([2.5,10.5,-3],[2,2.5,6]),c([-3,12,-4.75],[2,2,1.5]),c([1,12,-4.75],[2,2,1.5])])
 put('helmet',[c([-6,21,-4.75],[12,2,9.5],3),c([-4.5,23,-3.5],[9,2,7],3),c([-6,20.5,-5],[12,1.5,2],2)])
 put('right_helmet_spike',[c([-6,22,-2],[2,4,3],1),c([-7,25,-2],[3,2,3],1)])
 put('left_helmet_spike',[c([4,22,-2],[2,3,3],1)])
 r.bone('neck_stump','head',[0,11,1],[c([-2.5,9.5,-1.5],[5,3,5],3),c([-1.5,8.5,-.5],[3,2,3],1)])
 for i in range(4):
  for j in range(4):
   x=-4.5+i*3;y=11-j*2.5;z=-1.5 if i%2==0 else 1.5
   by[f'viscera_{i}_{j}']['pivot']=[x,y,z]
   if j==0:by[f'viscera_spring_{i}']['pivot']=[x,y,z]
   short=1 if i==2 and j==3 else 0
   put(f'viscera_{i}_{j}',[c([x-1,y-2.5+short,z-1],[2,3-short,2],2 if j==3 else 3)])
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'head':wave(1,ticks,2),'jaw':wave(0,ticks,3)}
  for i in range(4):
   for j in range(4):ch[f'viscera_{i}_{j}']=wave(0 if i%2==0 else 2,ticks,3 if name=='idle' else 5,i*.8+j*.6)
  clip(r,name,ch,True)
 clip(r,'attack',{'head':track('rotation',[(0,[0,0,0]),(10,[-18,0,0]),(14,[28,0,0]),(26,[18,0,0]),(44,[0,0,0])]),'jaw':track('rotation',[(0,[0,0,0]),(10,[10,0,0]),(14,[35,0,0]),(26,[35,0,0]),(44,[0,0,0])]),**{f'viscera_{i}_0':track('rotation',[(0,[0,0,0]),(14,[-20,0,0]),(26,[-15,0,0]),(44,[0,0,0])]) for i in range(4)}})
 clip(r,'blood',{'head':track('rotation',[(0,[0,0,0]),(14,[-15,0,0]),(20,[12,0,0]),(28,[8,0,0]),(50,[0,0,0])]),'jaw':track('rotation',[(0,[0,0,0]),(14,[15,0,0]),(20,[45,0,0]),(28,[40,0,0]),(50,[0,0,0])]),**{f'viscera_{i}_0':track('rotation',[(0,[0,0,0]),(14,[-10,0,0]),(20,[-15,0,(i-1.5)*8]),(28,[-15,0,(i-1.5)*8]),(50,[0,0,0])]) for i in range(4)}})
 clip(r,'hurt',{'head':track('rotation',[(0,[0,0,0]),(2,[-12,0,4]),(8,[0,0,0])])})
 clip(r,'death',{'head':{**track('rotation',[(0,[0,0,0]),(28,[80,0,15]),(44,[80,0,15])]),**track('position',[(0,[0,0,0]),(28,[0,-12,0]),(44,[0,-12,0])])},'jaw':track('rotation',[(0,[0,0,0]),(28,[25,0,0]),(44,[25,0,0])])})

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--ids',nargs='+',choices=IDS,default=IDS);selected=p.parse_args().ids
 owned_path=OUT/'shield-skull-guard-scout-owned-hashes.json';owned=json.loads(owned_path.read_text()) if owned_path.exists() else {}
 for name in selected:
  for folder,suffix,original in [('geo','.geo.json','original.geo.json'),('animations','.animation.json','original.animation.json')]:
   current=ASSETS/f'{folder}/blueprint/{name}{suffix}'
   assert current.read_bytes()==(OUT/'source'/name/original).read_bytes() or hashlib.sha256(current.read_bytes()).hexdigest()==owned.get(str(current)),'Concurrent modification: '+name
 for name,spec,builder in zip(IDS,SPECS,[shield,skull,guard,scout]):
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
