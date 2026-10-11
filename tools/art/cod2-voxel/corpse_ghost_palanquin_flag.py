"""Original coarse corpse, spirit procession and standard bearer; art only."""
import hashlib,json,math
from build_models import Rig,track,OUT,ASSETS
from mechanicals import clip,lengths,wave
from armies_tree import skeleton,steps,fist,human_end,pin_all
from shield_skull_guard_scout import human,locomotion

IDS=['shibian_lishi','yinbing_guizu','yinyang_zhijiao_youhun','zhenwang_zhangqiguan']
SPECS=[
 (['#ffffff','#6b7763','#293a31','#b09b61'],['..111..','..323..','.11111.','1121211','1133311','.11.11.','.22.22.']),
 (['#ffffff','#6f9899','#243d45','#b0b496'],['..333..','..121..','.11111.','1131133','..111.3','..112.3','...22.3']),
 (['#ffffff','#b7ac8b','#293b39','#8a3c3b'],['..333..','.31113.','.12221.','3111113','1121211','.2...2.','22...22']),
 (['#ffffff','#576e67','#263333','#b39863'],['..121.3','..323.3','.111133','1131133','.111133','.12.1.3','.22.2.3']),
]

def ordered(r):
 pending=list(r.bones);result=[];known=set()
 while pending:
  ready=[b for b in pending if not b.get('parent') or b['parent'] in known]
  assert ready,'Cyclic/missing parent'
  for b in ready:result.append(b);known.add(b['name']);pending.remove(b)
 r.bones=result

def corpse(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 put('pelvis',[c([-6,10,-4],[12,5,8],2),c([-6.5,12,-4.5],[13,2,9],3)])
 put('waist',[c([-4.5,13,-4],[9,4,8],2)])
 put('waist_upper',[c([-6,16,-4.5],[12,4,9])])
 put('chest',[c([-9,19,-5],[18,9,10]),c([-8,27,-4.5],[16,2,9],2)])
 put('chest_front',[c([-8,21,-6],[16,6,1.5],2),c([-7,23,-6.5],[5,3,1],3),c([2,23,-6.5],[5,3,1],3)])
 put('chest_back',[c([-8,20,5],[16,8,1.5],2),c([-2,21,6],[4,6,1.5],3)])
 put('belly',[c([-6,14,-6.5],[12,8,11]),c([-5,15,-7],[10,4,1],2)])
 put('trapezius',[c([-7,26,1],[14,5,6]),c([-5,30,2],[10,2,4],2)])
 by['neck']['pivot']=[0,28.25,-2];by['head']['pivot']=[0,31.75,-2]
 put('neck',[c([-2.5,27,-4.5],[5,3,5],2)])
 put('head',[c([-4.5,29,-6],[9,6,8]),c([-3.5,35,-5],[7,1.5,6],2),c([-4,31,-7],[3,2,1.5],2),c([1,31,-7],[3,2,1.5],2),c([-1,29.5,-7],[2,3,1.5],3),c([-4.5,32,-2],[2,4,4],3)])
 r.bone('corpse_jaw','head',[0,29,-2],[c([-4,27.5,-6.5],[8,2,2],2),c([-4,27.5,-4.5],[2,2,5]),c([2,27.5,-4.5],[2,2,5]),c([-3,29,-6.75],[2,2,1],3),c([1,29,-6.75],[2,2,1],3)])
 put('vein_chest',[c([-1,19,-7.5],[2,6,1],3),c([-4,22,-7.5],[8,2,1],3)])
 for side,s in [('right',-1),('left',1)]:
  a=[s*11,28,0];e=[s*11,17,-.5];w=[s*11,5.75,-1.5]
  for n in ['shoulder','upper_arm']:by[side+'_'+n]['pivot']=a.copy()
  for n in ['elbow','forearm']:by[side+'_'+n]['pivot']=e.copy()
  for n in ['wrist','hand']:by[side+'_'+n]['pivot']=w.copy()
  put(side+'_upper_arm',steps(c,a,e,6));put(side+'_elbow',[c([s*11-3.5,15,-4],[7,4,7],2)])
  put(side+'_forearm',steps(c,e,w,5.5));put(side+'_wrist',[c([s*11-3.5,5,-5],[7,3,7],2)])
  put(side+'_hand',[c([s*11-4,3.75,-5],[8,3,7])])
  put('vein_'+side+'_arm',[c([s*11-1,20,-4],[2,6,1],3),c([s*11-2.5,22,-4],[5,2,1],3)])
  r.bone(side+'_broken_lock','{}_shoulder'.format(side),a,[c([s*11-4,26,-4.5],[8,3,9],2),c([s*11-3.5,28.5,-4],[7,2,8],3)])
  for i in range(5):
   x=s*11+(i-2)*1.5
   for j,y in enumerate([3.75,2.5,1.25]):
    n=f'{side}_finger_{i}_{j}';by[n]['pivot']=[x,y,-2]
    if i in [0,2,4]:put(n,[c([x-1,y-1.25,-3.25 if j<2 else -4],[2,1.5,2.5 if j<2 else 3.25],3 if j==2 else 1)])
  x=s*4
  for n in ['thigh','knee','shin','ankle','foot']:by[side+'_'+n]['pivot'][0]=x
  put(side+'_thigh',[c([x-2.5,6.375,-3],[5,6,6]),c([x-3,9,-3.5],[6,3,7],2)])
  put(side+'_knee',[c([x-2.5,5.5,-3.5],[5,2.5,7],3)])
  put(side+'_shin',[c([x-2,1.5,-2.5],[4,5,5],2)])
  put(side+'_ankle',[c([x-2.5,1,-3],[5,2,6],1)])
  put(side+'_foot',[c([x-3,.125,-4.5],[6,2,8],2),c([x-3,1,-4.5],[6,1.5,2],3)])
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'chest':wave(0,ticks,1.5),'corpse_jaw':wave(0,ticks,3)}
  if name!='idle':
   amp=12 if name=='walk' else 27
   for side,s in [('right',-1),('left',1)]:
    ph=0 if s==1 else math.pi
    ch[side+'_thigh']=wave(0,ticks,amp,ph);ch[side+'_knee']=wave(0,ticks,-amp*.3,ph);ch[side+'_ankle']=wave(0,ticks,-amp*.7,ph)
    ch[side+'_shoulder']=wave(0,ticks,-amp*.4,ph);ch[side+'_elbow']=wave(0,ticks,3,ph)
  clip(r,name,ch,True)
 ch={'waist_upper':track('rotation',[(0,[0,0,0]),(14,[-12,0,0]),(20,[25,0,0]),(28,[25,0,0]),(46,[0,0,0])]),'corpse_jaw':track('rotation',[(0,[0,0,0]),(14,[24,0,0]),(20,[40,0,0]),(46,[0,0,0])])}
 for side,s in [('right',-1),('left',1)]:
  ch[side+'_shoulder']=track('rotation',[(0,[0,0,0]),(14,[-150,0,s*12]),(19,[-150,0,s*12]),(20,[-20,0,s*8]),(28,[-15,0,s*8]),(46,[0,0,0])])
  ch[side+'_elbow']=track('rotation',[(0,[0,0,0]),(14,[-20,0,0]),(20,[15,0,0]),(46,[0,0,0])])
 clip(r,'attack',ch);human_end(r)
 r.animations['animation.'+r.name+'.death']['bones']['corpse_jaw']=track('rotation',[(0,[0,0,0]),(28,[35,0,0]),(44,[35,0,0])])

def ghost(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 r.bone('ghost_pelvis','root',[0,11,0],[c([-4,9,-3],[8,4,6],2),c([-4.5,11,-3.5],[9,2,7],3)])
 r.bone('ghost_waist','ghost_pelvis',[0,13,0],[c([-3,12,-2.5],[6,3,5],2)])
 by['chest']['parent']='ghost_waist'
 put('chest',[c([-5,14,-3],[10,8,6]),c([-5.5,20,-3.5],[11,2,7],3)])
 put('breastplate',[c([-5,15,-4.5],[10,6,1.5],2),c([-3,16,-5],[6,4,1],3)])
 put('helmet',[c([-4,22,-3.5],[8,5,7],2),c([-4.5,26,-4],[9,2,8],3),c([-3.5,28,-3],[7,1.5,6],3),c([-1,29,-2],[2,1.5,4],1),c([-4.5,22,-3],[1.5,4,6]),c([3,22,-3],[1.5,4,6])])
 put('ghost_eyes',[c([-3.5,23.5,-4.25],[7,3,1],2)])
 for side,s in [('right',-1),('left',1)]:
  put(side+'_ghost_flame',[c([s*2-1,24,-5],[2,2,1.5],1),c([s*2-1,26,-4.75],[2,1.5,1],1)])
  a=by[side+'_shoulder']['pivot'];e=by[side+'_elbow']['pivot'];w=by[side+'_hand']['pivot']
  put(side+'_upper_arm',steps(c,a,e,3));put(side+'_elbow',[c([e[0]-1.75,e[1]-1.5,e[2]-1.75],[3.5,3,3.5],2)])
  put(side+'_forearm',steps(c,e,w,3,2));put(side+'_wrist',[c([w[0]-1.75,w[1]-1.5,-1.75],[3.5,3,3.5])])
  r.bone(side+'_ghost_pauldron',side+'_shoulder',a,[c([s*5-2.5,20,-3.5],[5,3,7],2),c([s*5-2,23,-2.5],[4,1.5,5],3)])
  if side=='right':fist(r,by,side,w,[68,0,0])
  else:put(side+'_hand',[c([w[0]-1.5,w[1]-1.5,-2],[3,3,4]),c([w[0]-1.5,w[1]-3,-2],[3,2,1.5],3)])
 put('smoke_tail_0',[c([-4,5.5,-2.5],[8,7,5],2),c([-3.5,5,1.5],[7,4,5],1)])
 put('smoke_tail_1',[c([-3,2.5,2],[6,5,6],1),c([-2.5,1.5,6],[5,3,4],2)])
 put('smoke_tail_2',[c([-2,.125,7],[4,3,5],2),c([-1.5,.5,11],[3,2,3],1)])
 x,y,z=by['ghost_ge']['pivot']
 put('ghost_ge',[c([x-.625,y-8,z-.625],[1.25,27,1.25],2),c([x-1.5,y+15,z-1.25],[3,4,2.5],3),c([x-1.25,y+17,z-1.25],[2.5,7,2.5],3),c([x-6,y+15,z-1.25],[5,3,2.5],3),c([x-6,y+12,z-1.25],[2,3,2.5],1)])
 ordered(r)
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'chest':wave(0,ticks,1),'helmet':wave(1,ticks,1)}
  for i in range(3):ch['smoke_tail_'+str(i)]=wave(1,ticks,3 if name=='idle' else 6,i*.7)
  clip(r,name,ch,True)
 clip(r,'attack',{'right_shoulder':track('rotation',[(0,[0,0,0]),(10,[-15,0,-5]),(14,[22,0,0]),(20,[18,0,0]),(34,[0,0,0])]),'right_elbow':track('rotation',[(0,[0,0,0]),(10,[15,0,0]),(14,[0,0,0]),(34,[0,0,0])]),'chest':track('position',[(0,[0,0,0]),(10,[0,0,1]),(14,[0,0,-3]),(20,[0,0,-2]),(34,[0,0,0])])})
 clip(r,'phase',{'chest':track('rotation',[(0,[0,0,0]),(3,[0,0,12]),(6,[0,0,-10]),(16,[0,0,0])]),'smoke_tail_0':track('rotation',[(0,[0,0,0]),(3,[0,-18,0]),(6,[0,15,0]),(16,[0,0,0])])})
 clip(r,'hurt',{'chest':track('rotation',[(0,[0,0,0]),(2,[-10,0,0]),(10,[0,0,0])])})
 clip(r,'death',{'ghost_pelvis':{**track('rotation',[(0,[0,0,0]),(28,[35,0,0]),(44,[35,0,0])]),**track('position',[(0,[0,0,0]),(28,[0,-5,0]),(44,[0,-5,0])])},'helmet':track('rotation',[(0,[0,0,0]),(28,[20,0,0]),(44,[20,0,0])]),'ghost_eyes':track('scale',[(0,[1,1,1]),(18,[1,1,1]),(44,[.05,.05,.05])])})

def palanquin(r):
 by=skeleton(r);c=r.cube
 def put(n,v):by[n]['cubes']=v
 put('cabin',[c([-10,10,-10],[20,2,20],2),c([-10,12,8.5],[20,14,1.5],1),*[c([x,12,z],[3,15,3],3) for x in [-10,7] for z in [-10,7]],c([-11,10,-24],[2,3,48],2),c([9,10,-24],[2,3,48],2)])
 put('roof',[c([-12,26,-12],[24,3,24],3),c([-10,29,-10],[20,2,20],1),c([-8,31,-8],[16,2,16],3),c([-1,33,-6],[2,2,12],2)])
 put('banner',[c([-1,32,1],[2,8,2],2),c([1,35,1],[6,5,1.5],3),c([2,36,.5],[2,3,1],1)])
 for i,y in enumerate([25,20,15]):
  put('curtain_'+str(i),[c([-6,y-5,-10.75],[12,5,1.5],1),c([-6,y-5,-11.25],[2,5,1],3),c([4,y-5,-11.25],[2,5,1],3)])
 for side,s in [('right',-1),('left',1)]:
  a=by[side+'_ghost_arm']['pivot'];h=by[side+'_ghost_hand']['pivot']
  put(side+'_ghost_arm',steps(c,a,h,3,2));put(side+'_ghost_hand',[c([s*4-2,15,-15],[4,4,5],2),c([s*4-3.5,13.5,-16],[2,3,3],1),c([s*4+1.5,13.5,-16],[2,3,3],1)])
 for i in range(4):
  x,_,z=by['bearer_'+str(i)]['pivot'];base='bearer_'+str(i)
  # Old bearer is a local anchor. New layered volumes replace the tiny human box.
  r.bone(base+'_pelvis',base,[x,7,z],[c([x-2,5,z-2],[4,3,4],2)])
  r.bone(base+'_waist',base+'_pelvis',[x,9,z],[c([x-1.5,8,z-1.5],[3,2,3],2)])
  r.bone(base+'_chest',base+'_waist',[x,12,z],[c([x-2,10,z-2],[4,5,4],1),c([x-2.5,13,z-2.5],[5,2,5],3)])
  r.bone(base+'_smoke',base+'_pelvis',[x,5,z],[c([x-1.5,2,z-1.5],[3,4,3],2),c([x-1,.125,z],[2,2,3],2)])
  by['bearer_head_'+str(i)]['parent']=base+'_chest'
  put('bearer_head_'+str(i),[c([x-2.5,15,z-2.5],[5,4,5],2),c([x-3,18,z-3],[6,1.5,6],3),c([x-1.5,15.5,z-3],[3,2,1],1)])
  for side,s in [('right',-1),('left',1)]:
   n=base+'_'+side;by[n]['parent']=base+'_chest'
   put(n,[c([x+s*2-1,11,z-2],[2,4,4],1),c([x+s*2-1,10,z-2],[2,2,4],2)])
 ordered(r)
 for name in ['idle','walk','run']:
  ticks=lengths(r)[name];ch={'banner':wave(0,ticks,2)}
  for i in range(3):ch['curtain_'+str(i)]=wave(0,ticks,1 if name=='idle' else 4,i*.6)
  for i in range(4):
   ch['bearer_'+str(i)]=wave(0,ticks,1 if name=='idle' else 5,(i%2)*math.pi)
   ch['bearer_'+str(i)+'_smoke']=wave(0,ticks,2 if name=='idle' else 6,(i%2)*math.pi)
  clip(r,name,ch,True)
 clip(r,'attack',{'cabin':track('rotation',[(0,[0,0,0]),(10,[-6,0,0]),(16,[10,0,0]),(25,[5,0,0]),(44,[0,0,0])]),'curtain_0':track('rotation',[(0,[0,0,0]),(10,[15,0,0]),(16,[35,0,0]),(25,[15,0,0]),(44,[0,0,0])])})
 ch={}
 for i in range(3):ch['curtain_'+str(i)]=track('rotation',[(0,[0,0,0]),(18,[20 if i==0 else 5,0,0]),(24,[35 if i==0 else 8,0,0]),(64,[35 if i==0 else 8,0,0]),(84,[0,0,0])])
 for side,s in [('right',-1),('left',1)]:
  ch[side+'_ghost_arm']=track('rotation',[(0,[0,0,0]),(18,[0,s*15,s*10]),(24,[-8,s*-15,s*-8]),(64,[-8,s*-15,s*-8]),(84,[0,0,0])])
  ch[side+'_ghost_hand']=track('rotation',[(0,[0,0,0]),(18,[0,0,s*25]),(24,[20,0,s*-12]),(64,[20,0,s*-12]),(84,[0,0,0])])
 clip(r,'hold',ch)
 clip(r,'hurt',{'cabin':track('rotation',[(0,[0,0,0]),(2,[-7,0,0]),(10,[0,0,0])])})
 clip(r,'death',{'cabin':track('rotation',[(0,[0,0,0]),(28,[0,0,10]),(44,[0,0,10])]),'roof':track('rotation',[(0,[0,0,0]),(28,[15,0,-18]),(44,[15,0,-18])]),**{'bearer_'+str(i):track('rotation',[(0,[0,0,0]),(28,[25,0,0]),(44,[25,0,0])]) for i in range(4)}})

def flag(r):
 by=human(r,'guard');c=r.cube
 def put(n,v):by[n]['cubes']=v
 hip=by['pelvis']['pivot'][1];hy=by['head']['pivot'][1];top=by['chest']['pivot'][1]
 put('chest',[c([-5.5,hip+5,-4],[11,top-hip-4,8]),c([-6,top-2,-4.5],[12,2,9],2)])
 put('chest_front',[c([-5.5,hip+5,-5.5],[11,top-hip-5,1.5]),c([-1.5,hip+5,-6],[3,top-hip-5,1],3)])
 put('chest_back',[c([-5.5,hip+5,4],[11,top-hip-5,1.5],2)])
 put('shadow_hood',[c([-4.5,hy+1.5,-4.5],[9,2,9],2),c([-3.5,hy+3,-3.5],[7,1.5,7],2),c([-1,hy+4,-3],[2,2,6],3),c([-4.5,hy-2,-2.5],[1.5,5,6],2),c([3,hy-2,-2.5],[1.5,5,6],2),c([-4.5,hy+2,1],[2,4,2],3),c([2.5,hy+2,1],[2,4,2],3)])
 put('belt',[c([-5.5,hip,-4.5],[11,2,9],2),c([-1.5,hip,-5.5],[3,2,1.5],3)])
 for side,s in [('right',-1),('left',1)]:
  put(side+'_skirt',[c([s*3-3,hip-7,-4.5],[6,7,1.5],2),c([s*3-3,hip-7,-5],[6,2,2],3)])
  r.bone(side+'_flag_pauldron',side+'_shoulder',by[side+'_shoulder']['pivot'],[c([s*6-3,top-3,-4],[6,3,8]),c([s*6-2.5,top,-3],[5,2,6],3)])
 x,y,z=by['flagstaff']['pivot']
 put('flagstaff',[c([x-.625,1,z-.625],[1.25,31.5,1.25],2),c([x-1,1,z-1],[2,3,2],3)])
 put('flag_upper',[c([x-.625,32.5,z-.625],[1.25,17,1.25],2),c([x-1.5,49,z-1.5],[3,3,3],3)])
 for i in range(4):
  y=49-i*4
  put('flag_cloth_'+str(i),[c([x+.625,y-4,z-.5],[13.375 if i<3 else 11.375,4,1],1),c([x+.625,y-4,z-1],[2,4,1],3),c([x+12,y-4,z-1],[2,4,1],3)] if i<3 else [c([x+.625,y-4,z-.5],[11.375,4,1],1),c([x+.625,y-4,z-1],[2,4,1],3)])
  if i in [1,2]:by['flag_cloth_'+str(i)]['cubes'] += [c([x+5,y-4,z-1],[2,4,1],3),c([x+3,y-2,z-1],[6,2,1],3)]
 # Existing ghost overlay used to duplicate the entire body. Keep non-coplanar
 # broad soul buckles at established locators, with the original death fade.
 put('ghost_chest_front',[c([-2,hip+6,-6.75],[4,3,1],3)])
 put('ghost_shadow_hood',[c([-3,hy-1.5,-5.5],[2,2,1],3),c([1,hy-1.5,-5.5],[2,2,1],3)])
 for side,s in [('right',-1),('left',1)]:put('ghost_'+side+'_skirt',[c([s*3-1,hip-5,-5.75],[2,3,1],3)])
 ordered(r);locomotion(r,'shield')
 for animation in r.animations.values():
  ticks=animation['animation_length']*20
  for i in range(4):animation['bones']['flag_cloth_'+str(i)]=wave(1,ticks,1,i*.5)
 clip(r,'attack',{'waist_upper':track('rotation',[(0,[0,0,0]),(12,[-6,0,0]),(18,[14,0,0]),(26,[10,0,0]),(40,[0,0,0])]),'flagstaff':track('position',[(0,[0,0,0]),(12,[0,3,0]),(18,[0,-1,0]),(26,[0,-1,0]),(40,[0,0,0])]),'right_grip':track('position',[(0,[0,0,0]),(12,[0,3,0]),(18,[0,-1,0]),(26,[0,-1,0]),(40,[0,0,0])])})
 # Shift the actual hand together with the pole instead of sliding it through a palm.
 ch=r.animations['animation.'+r.name+'.attack']['bones'];movement=ch.pop('flagstaff');ch.pop('right_grip');ch['right_wrist']=movement
 human_end(r)
 death=r.animations['animation.'+r.name+'.death']['bones']
 for n in by:
  if n.startswith('ghost_'):death[n]=track('scale',[(0,[1,1,1]),(8,[1,1,1]),(22,[.001,.001,.001]),(40,[.001,.001,.001])])
 pin_all(r,'flagstaff')

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--ids',nargs='+',choices=IDS,default=IDS);selected=p.parse_args().ids
 owned_path=OUT/'corpse-ghost-palanquin-flag-owned-hashes.json';owned=json.loads(owned_path.read_text()) if owned_path.exists() else {}
 for name in selected:
  for folder,suffix,original in [('geo','.geo.json','original.geo.json'),('animations','.animation.json','original.animation.json')]:
   current=ASSETS/f'{folder}/blueprint/{name}{suffix}'
   assert current.read_bytes()==(OUT/'source'/name/original).read_bytes() or hashlib.sha256(current.read_bytes()).hexdigest()==owned.get(str(current)),'Concurrent modification: '+name
 for name,spec,builder in zip(IDS,SPECS,[corpse,ghost,palanquin,flag]):
  if name not in selected:continue
  rig=Rig(name,*spec);builder(rig);ordered(rig);rig.save();print(name,len(rig.bones),'bones',sum(len(b.get('cubes',[])) for b in rig.bones),'cuboids',flush=True)
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
  for folder,suffix in [('geo','.geo.json'),('animations','.animation.json')]:
   current=ASSETS/f'{folder}/blueprint/{name}{suffix}';owned[str(current)]=hashlib.sha256(current.read_bytes()).hexdigest()
 owned_path.write_text(json.dumps(owned,indent=2)+'\n')
if __name__=='__main__':main()
