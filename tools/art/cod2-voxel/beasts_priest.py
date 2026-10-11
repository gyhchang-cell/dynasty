"""Four original species/profession rigs; preserve live bone and clip contracts."""
import hashlib
import json
import math
from build_models import Rig, track, OUT, ASSETS
from mechanicals import clip, lengths, wave

IDS=['baimu_mowu','bishui_xuanjiao_youzi','chimu_zhuha','fufa_jijiu']
SPECS=[
 (['#ffffff','#687a59','#263327','#d5af55'],['..313..','.11311.','3321233','.11111.','3311133','.11111.','33.1.33']),
 (['#ffffff','#428277','#183b3d','#cab582'],['.3...3.','.11311.','.12321.','..333..','.11111.','1.121.1','..121..']),
 (['#ffffff','#ac4934','#472b2a','#c6a478'],['.1...1.','.12121.','1111111','.22222.','.33333.','11.3.11','33...33']),
 (['#ffffff','#803b32','#302b29','#c5a775'],['..333..','..131..','..323..','.111113','1131133','..111.3','.22.223']),
]

def centipede(r):
 c,b=r.cube,r.bone;b('root',None,[0,0,0])
 xs=[-2,-3,-4,-3,-2,0,2,4,5,4,2,0,-2,-4,-4,-3]
 for i,x in enumerate(xs):
  z=-30+i*4;w=8 if i<14 else 6 if i==14 else 4
  seg='segment_'+str(i)
  b(seg,'root' if i==0 else 'segment_'+str(i-1),[x,5,z],[c([x-w/2,3,z-2],[w,5,4.5]),c([x-w/2-.5,6,z-2],[w+1,3,4],1),c([x-w/2,2.5,z-2],[w,2,4],2)])
  b('eye_'+str(i),seg,[x,9,z],[c([x-1,9,z-1],[2,2,2],3)])
  for side,s in [('left',1),('right',-1)]:
   hip=x+s*w/2;knee=hip+s*3;foot=knee+s*2;name=side+'_leg_'+str(i)
   b(name,seg,[hip,5,z],[c([min(hip,knee)-1,3.5,z-1],[5,2.5,2],3)])
   b(name+'_knee',name,[knee,4,z],[c([min(knee,foot)-1,.5,z-1],[4,4,2],2)])
   b(name+'_foot',name+'_knee',[foot,.75,z],[c([foot-1.5,.125,z-1.5],[3,1.5,3],3)])
 b('head','segment_0',[-2,6,-32],[c([-8,3,-37],[12,7,8]),c([-9,8,-36],[14,3,6],1),c([-8,7,-38],[3,2,1],3),c([1,7,-38],[3,2,1],3),c([-5,4,-39],[6,3,2],2)])
 for side,s in [('left',1),('right',-1)]:
  x=-2+s*4
  b(side+'_jaw','head',[x,4,-36],[c([x-1.5,2,-42],[3,4,7],3),c([x-1.5-s,2,-44],[4,3,3],2)])
  b(side+'_antenna','head',[x,10,-34],[c([x-1,10,-36],[2,4,2],2),c([x-1+s,13,-37],[2,2,4],3)])
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={}
  for i in range(16):
   ch['segment_'+str(i)]=wave(1,ticks,.3 if name=='idle' else 1.3,i*.6)
   if name!='idle':
    for side,s in [('left',1),('right',-1)]:
     n=side+'_leg_'+str(i);ph=i*.65+(0 if s==1 else math.pi)
     ch[n]=wave(1,ticks,9 if name=='walk' else 14,ph)
     ch[n+'_knee']=track('position',[(ticks*k/8,[0,round(max(0,math.sin(k*math.pi/4+ph))*.8,5),0]) for k in range(9)])
  clip(r,name,ch,True)
 ch={'head':track('position',[(0,[0,0,0]),(8,[0,1,2]),(12,[0,0,-3]),(16,[0,0,-2]),(32,[0,0,0])])}
 for side,s in [('left',1),('right',-1)]:ch[side+'_jaw']=track('rotation',[(0,[0,0,0]),(8,[0,s*-24,0]),(12,[0,s*14,0]),(32,[0,0,0])])
 clip(r,'attack',ch)
 clip(r,'gaze',{'eye_'+str(i):track('scale',[(0,[1,1,1]),(22,[1,1,1]),(26,[1.5,1.5,1.5]),(32,[1.5,1.5,1.5]),(52,[1,1,1])]) for i in range(16)})
 clip(r,'hurt',{'head':track('rotation',[(0,[0,0,0]),(2,[-7,0,0]),(10,[0,0,0])])})
 clip(r,'death',{'root':track('scale',[(0,[1,1,1]),(28,[1,.45,1]),(44,[1,.45,1])]),'head':track('rotation',[(0,[0,0,0]),(28,[15,0,0]),(44,[15,0,0])])})

def serpent(r):
 c,b=r.cube,r.bone;b('root',None,[0,0,0])
 xs=[-2,-3,-4,-3,-1,2,4,5,4,2,0,-3,-5,-6];ys=[12,10,7,5,4,4,4,4,4,4,4,5,6,8]
 for i,(x,y) in enumerate(zip(xs,ys)):
  z=-10+i*4;w=7 if i<3 else 8 if i<9 else [7,6,5,4,3][i-9];h=6 if i<3 else 5 if i<11 else 3
  seg='spine_'+str(i)
  b(seg,'root' if i==0 else 'spine_'+str(i-1),[x,y,z],[c([x-w/2,y-h/2,z-2.5],[w,h,5]),c([x-w/2,y-h/2-.25,z-2],[w,1.5,4],3)])
  b('fin_spring_'+str(i),seg,[x,y+h/2,z])
  b('fin_'+str(i),'fin_spring_'+str(i),[x,y+h/2,z],[c([x-1,y+h/2,z-1],[2,3 if i<10 else 2,4],2),c([x-1,y+h/2+2,z],[2,2,2],3)] if i<10 else [c([x-1,y+h/2,z-1],[2,3,3],2)])
 b('head','spine_0',[-2,12,-13],[c([-7,9,-20],[10,7,10]),c([-6,9,-25],[8,4,6]),c([-7.5,13,-21],[3,3,5],2),c([.5,13,-21],[3,3,5],2),c([-7,13,-22],[3,2,1],3),c([0,13,-22],[3,2,1],3),c([-4,13,-25],[4,2,2],2)])
 b('jaw','head',[-2,9,-16],[c([-6,7,-25],[8,2,10],3),c([-6,8,-23],[2,3,2],3),c([0,8,-23],[2,3,2],3)])
 for s in [-1,1]:
  x=-2+s*4
  b('whisker_'+str(s),'head',[x,10,-22],[c([x-1,9,-25],[2,2,4],3),c([x-1+s*2,8,-27],[2,2,3],3)])
  b('horn_'+str(s),'head',[x,15,-15],[c([x-1,15,-17],[2,3,3],2),c([x-1+s,17,-15],[2,2,3],3)])
  b('pectoral_'+str(s),'spine_2',[-4+s*4,7,-2],[c([-4+s*6-3,5,-4],[6,2,6],2),c([-4+s*8-2,5,-1],[4,2,4],3)])
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name]
  ch={'spine_'+str(i):wave(1,ticks,.6 if name=='idle' else 2.5 if name=='walk' else 4,i*.6) for i in range(14)}
  ch.update({'fin_'+str(i):wave(2,ticks,3,i*.6) for i in range(14)})
  clip(r,name,ch,True)
 clip(r,'attack',{'head':track('position',[(0,[0,0,0]),(8,[0,1,2]),(12,[0,0,-4]),(18,[0,0,-2]),(30,[0,0,0])]),'jaw':track('rotation',[(0,[0,0,0]),(8,[24,0,0]),(12,[0,0,0]),(30,[0,0,0])])})
 clip(r,'coil',{'spine_'+str(i):track('rotation',[(0,[0,0,0]),(14,[0,-2,0]),(18,[0,6 if i>=2 else -6,0]),(42,[0,6 if i>=2 else -6,0]),(64,[0,0,0])]) for i in range(14)})
 clip(r,'hurt',{'head':track('rotation',[(0,[0,0,0]),(2,[-6,0,0]),(10,[0,0,0])])})
 clip(r,'death',{'spine_0':track('scale',[(0,[1,1,1]),(30,[1,.35,1]),(44,[1,.35,1])]),'head':track('rotation',[(0,[0,0,0]),(30,[20,0,0]),(44,[20,0,0])])})

def toad(r):
 c,b=r.cube,r.bone;b('root',None,[0,0,0])
 b('body','root',[0,6,0],[c([-8,4,-5],[16,8,16]),c([-7,11,-3],[14,2,12],1)])
 b('belly','body',[0,4,0],[c([-6,2,-5],[12,3,12],3)])
 b('head','body',[0,8,-5],[c([-8,5,-12],[16,7,9]),c([-9,7,-11],[18,3,6]),c([-7,4,-13],[14,2,2],2)])
 b('mouth_jaw','head',[0,4,-7],[c([-7,2.5,-13],[14,2,10],3),c([-6,4,-13.5],[12,1,1],2)])
 b('throat_sac','head',[0,5,-7],[c([-5,3,-9],[10,3,6],3)])
 for side,s in [('right',-1),('left',1)]:
  b('eye_'+side,'head',[s*6,12,-9],[c([s*6-2,10,-11],[4,5,4],2),c([s*6-1.5,12,-12],[3,2,1],1)])
  for leg,z in [('front',-5),('hind',6)]:
   n=side+'_'+leg;x=s*8;kx=s*11;fx=s*12;rear=leg=='hind'
   b(n+'_thigh','body',[x,6,z],[c([x-3.5,3,z-3],[7,7,9 if rear else 5]),c([x-3,8,z-2],[6,2,5],1)])
   b(n+'_knee',n+'_thigh',[kx,4,z+2 if rear else z],[c([kx-2.5,1.5,z+(2 if rear else -1)],[5,4,5],2)])
   b(n+'_foot',n+'_knee',[fx,1.5,z],[c([fx-3,.125,z-4],[6,1.5,7],3),c([fx-3,.125,z-5],[2,1.5,2],2),c([fx+1,.125,z-5],[2,1.5,2],2)])
 for i in range(8):
  x=-6+(i%4)*4;z=(i//4)*5
  b('venom_gland_'+str(i),'body',[x,12,z],[c([x-1.5,12,z-1.5],[3,2,3],3)])
 b('tongue_reach','head',[0,5.5,-13])
 b('tongue_root','tongue_reach',[0,5.5,-13])
 for i in range(5):
  z=-13-i
  b('tongue_'+str(i),'tongue_root' if i==0 else 'tongue_'+str(i-1),[0,5.5,z],[c([-1,4.5,z-1],[2,2,1],1)])
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'tongue_root':track('scale',[(0,[1,1,.08]),(ticks,[1,1,.08])]),'throat_sac':track('scale',[(0,[1,1,1]),(ticks/2,[1,1.15,1.15]),(ticks,[1,1,1])])}
  if name!='idle':
   for i,(side,leg) in enumerate([('left','front'),('right','front'),('left','hind'),('right','hind')]):
    n=side+'_'+leg;ph=0 if i in [0,3] else math.pi
    ch[n+'_thigh']=wave(0,ticks,8 if name=='walk' else 14,ph)
    ch[n+'_knee']=wave(0,ticks,-4 if name=='walk' else -7,ph);ch[n+'_foot']=wave(0,ticks,-4 if name=='walk' else -7,ph)
  clip(r,name,ch,True)
 clip(r,'attack',{'tongue_root':track('scale',[(0,[1,1,.08]),(8,[1,1,.08]),(10,[1,1,16]),(14,[1,1,16]),(23,[1,1,.08]),(28,[1,1,.08])]),'mouth_jaw':track('rotation',[(0,[0,0,0]),(8,[12,0,0]),(10,[16,0,0]),(23,[0,0,0]),(28,[0,0,0])])})
 ch={'tongue_root':track('scale',[(0,[1,1,.08]),(40,[1,1,.08])])}
 for side in ['left','right']:
  ch[side+'_hind_thigh']=track('rotation',[(0,[0,0,0]),(6,[-16,0,0]),(10,[25,0,0]),(26,[8,0,0]),(40,[0,0,0])])
  ch[side+'_hind_knee']=track('rotation',[(0,[0,0,0]),(6,[12,0,0]),(10,[-20,0,0]),(26,[0,0,0]),(40,[0,0,0])])
 clip(r,'leap',ch)
 ch={'tongue_root':track('scale',[(0,[1,1,.08]),(32,[1,1,.08])]),'throat_sac':track('scale',[(0,[1,1,1]),(10,[1.3,1.3,1.3]),(12,[1,1,1]),(32,[1,1,1])])}
 ch.update({'venom_gland_'+str(i):track('scale',[(0,[1,1,1]),(10,[1.4,1.4,1.4]),(12,[1.6,1.6,1.6]),(20,[1,1,1]),(32,[1,1,1])]) for i in range(8)})
 clip(r,'burst',ch)
 clip(r,'hurt',{'tongue_root':track('scale',[(0,[1,1,.08]),(8,[1,1,.08])]),'head':track('rotation',[(0,[0,0,0]),(2,[-6,0,0]),(8,[0,0,0])])})
 clip(r,'death',{'tongue_root':track('scale',[(0,[1,1,.08]),(44,[1,1,.08])]),'body':track('scale',[(0,[1,1,1]),(30,[1,.5,1]),(44,[1,.5,1])]),'head':track('rotation',[(0,[0,0,0]),(30,[12,0,0]),(44,[12,0,0])])})

def priest(r):
 c=r.cube
 # The established hierarchy contains separate body and identity/inertia wrappers.
 original=json.loads((OUT/'source'/r.name/'original.geo.json').read_text())['minecraft:geometry'][0]['bones']
 for old in original:r.bone(old['name'],old.get('parent'),[round(v*8)/8 for v in old['pivot']])
 by={b['name']:b for b in r.bones}
 def cubes(name,items):by[name]['cubes']=items
 cubes('body_pelvis',[c([-4.5,7,-3.5],[9,4,7]),c([-5,9,-4],[10,2,8],3)])
 cubes('body_waist',[c([-3.5,10,-3],[7,3,6],2)])
 cubes('body_waist_upper',[c([-4,12,-3.5],[8,3,7])])
 cubes('body_chest',[c([-5,14,-3.5],[10,5,7]),c([-6,17,-4],[12,2,8]),c([-2,14,-4.5],[4,5,1],3)])
 cubes('chest_front',[c([-5,14,-4.5],[2,5,1],3),c([3,14,-4.5],[2,5,1],3)])
 cubes('chest_back',[c([-4,14,3.5],[8,5,1]),c([-1,15,4.5],[2,3,1],3)])
 cubes('body_neck',[c([-2,18,-2],[4,2,4],3)])
 cubes('body_head',[c([-3.5,19,-3],[7,5,6],2)])
 cubes('mask',[c([-3,19,-4],[6,4,1],3),c([-2.5,21,-4.5],[2,1.5,.5],2),c([.5,21,-4.5],[2,1.5,.5],2),c([-1,19,-4.5],[2,1.5,.5],1)])
 cubes('crown',[c([-4.5,23,-4],[9,2,8]),c([-3,25,-2.5],[6,2,5]),c([-1.5,27,-1.5],[3,2,3],3),c([-5.5,23,-2],[2,3,4]),c([3.5,23,-2],[2,3,4])])
 cubes('robe_front',[c([-5.5,3,-4.5],[11,7,1.5]),c([-2,3,-5],[4,7,.5],3)])
 cubes('robe_back',[c([-5.5,3,3.5],[11,7,1.5]),c([-4.5,2,4],[9,2,1],2)])
 for side,s in [('right',-1),('left',1)]:
  x=s*4
  cubes('body_'+side+'_upper_arm',[c([x-2,12,-2.5],[4,6,5])])
  cubes('body_'+side+'_forearm',[c([x-2,8,-2.5],[4,5,5],2)])
  cubes(side+'_hand',[c([x-1.75,6.5,-2],[3.5,2.5,4],3)])
  cubes(side+'_sleeve_inner',[c([x-3,13,-3.5],[6,5,7]),c([x-3.5,12,-4],[7,2,8],3)])
  cubes(side+'_sleeve_outer',[c([x-3.5,8,-4],[7,5,8]),c([x-4,7,-4.5],[8,2,9],3)])
  cubes(side+'_sleeve_tail',[c([x-3,5,1],[6,3,2])])
  cubes(side+'_robe_panel',[c([s*4-1,3,-3],[2,7,6])])
  lx=s*2.25
  cubes('body_'+side+'_thigh',[c([lx-1.75,4,-2],[3.5,5,4],2)])
  cubes('body_'+side+'_shin',[c([lx-1.5,1,-2],[3,4,4],2)])
  cubes('body_'+side+'_foot',[c([lx-2,.125,-3.5],[4,1.5,6],2)])
 cubes('beads',[c([-3,16,-5],[2,2,1],2),c([1,16,-5],[2,2,1],2),c([-1,14,-5],[2,2,1],3)])
 # Bring the square staff and hand ahead of the thick cuff/robe; the grip is visible.
 by['right_hand']['pivot']=[-6,7.5,-5]
 cubes('right_hand',[c([-7.5,6.5,-6.5],[3,2.5,4],3)])
 cubes('right_wrist',[c([-6.5,7,-4],[3,2,3],3)])
 for n in ['staff','right_grip','body_right_grip']:by[n]['pivot']=[-6,7.5,-5]
 cubes('staff',[c([-6.5,.125,-5.5],[1,30.875,1],2),c([-11,30,-6],[10,2,2],1),c([-7.5,31,-6.5],[3,3,3],3)])
 cubes('right_grip',[c([-7.5,7,-6.5],[3,2,3],3)])
 for i,x in enumerate([-10,-6,-2]):
  for n in ['talisman_spring_'+str(i),'talisman_'+str(i)]:by[n]['pivot']=[x,30,-6]
  by['talisman_tip_'+str(i)]['pivot']=[x,25,-6]
  cubes('talisman_'+str(i),[c([x-1,25,-6.5],[2,5,1],3),c([x-1,27,-7],[2,2,.5],1)])
  cubes('talisman_tip_'+str(i),[c([x-1,23,-6.5],[2,2,1],3)])
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'head':wave(1,ticks,1)}
  if name!='idle':
   for side,s in [('right',-1),('left',1)]:
    phase=0 if s==1 else math.pi
    ch[side+'_thigh']=wave(0,ticks,10 if name=='walk' else 18,phase)
    ch[side+'_knee']=wave(0,ticks,-4 if name=='walk' else -8,phase)
    ch[side+'_ankle']=wave(0,ticks,-6 if name=='walk' else -10,phase)
   ch['left_shoulder']=wave(0,ticks,8,math.pi)
  clip(r,name,ch,True)
 for name in ['buff','skill']:
  ticks=lengths(r)[name]
  clip(r,name,{'left_shoulder':track('rotation',[(0,[0,0,0]),(16,[-60,0,-10]),(20,[-65,0,-10]),(30,[-55,0,-10]),(ticks,[0,0,0])]),'left_elbow':track('rotation',[(0,[0,0,0]),(16,[-28,0,0]),(30,[-28,0,0]),(ticks,[0,0,0])]),'chest':track('rotation',[(0,[0,0,0]),(20,[-4,0,0]),(ticks,[0,0,0])])})
 clip(r,'attack',{'left_shoulder':track('rotation',[(0,[0,0,0]),(20,[-35,0,-18]),(24,[-70,0,-12]),(26,[-50,0,-12]),(28,[-70,0,-12]),(30,[-50,0,-12]),(32,[-70,0,-12]),(50,[0,0,0])]),'chest':track('rotation',[(0,[0,0,0]),(20,[0,-10,0]),(24,[0,8,0]),(32,[0,8,0]),(50,[0,0,0])])})
 clip(r,'hurt',{'chest':track('rotation',[(0,[0,0,0]),(2,[-7,0,0]),(10,[0,0,0])])})
 clip(r,'death',{'pelvis':track('position',[(0,[0,0,0]),(30,[0,-5,0]),(40,[0,-5,0])]),'waist_upper':track('rotation',[(0,[0,0,0]),(30,[30,0,0]),(40,[30,0,0])]),'head':track('rotation',[(0,[0,0,0]),(30,[20,0,0]),(40,[20,0,0])]),**{side+'_thigh':track('rotation',[(0,[0,0,0]),(30,[0,0,s*35]),(40,[0,0,s*35])]) for side,s in [('right',-1),('left',1)]}})

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+',choices=IDS,default=IDS);selected=parser.parse_args().ids
 hashes_path=OUT/'beasts-priest-owned-hashes.json';owned=json.loads(hashes_path.read_text()) if hashes_path.exists() else {}
 for name in selected:
  for folder,suffix,original in [('geo','.geo.json','original.geo.json'),('animations','.animation.json','original.animation.json')]:
   p=ASSETS/f'{folder}/blueprint/{name}{suffix}'
   assert p.read_bytes()==(OUT/'source'/name/original).read_bytes() or hashlib.sha256(p.read_bytes()).hexdigest()==owned.get(str(p)), 'Concurrent resource modification: '+name
 for name,(palette,portrait),builder in zip(IDS,SPECS,[centipede,serpent,toad,priest]):
  if name not in selected:continue
  rig=Rig(name,palette,portrait);builder(rig);rig.save()
  print(name,len(rig.bones),'bones',sum(len(b.get('cubes',[])) for b in rig.bones),'cuboids',flush=True)
 from contacts import settle
 settle(selected)
 for name in selected:
  a=ASSETS/f'animations/blueprint/{name}.animation.json';(OUT/'blockbench'/(name+'.animation.json')).write_bytes(a.read_bytes())
  for folder,suffix in [('geo','.geo.json'),('animations','.animation.json')]:
   p=ASSETS/f'{folder}/blueprint/{name}{suffix}';owned[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 hashes_path.write_text(json.dumps(owned,indent=2)+'\n')

if __name__=='__main__':main()
