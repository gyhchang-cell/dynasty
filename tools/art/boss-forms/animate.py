"""Species-specific mechanical and quadruped motion, matched to existing server skill clocks."""
import math,copy
DURATIONS=[{'attack':.9,'cast':1.5,'death':.95},{'attack':1.1,'cast':1.8,'death':.95},{'attack':1.2,'cast':1.5,'death':.95},{'roar':2.5,'spin':3.85,'throw':2.5,'death':3.5},{'net':2.1,'wheels':3.75,'spiders':2.8,'death':3},{'sweep':2.65,'charge':3.1,'order':3,'death':3.5},{'mirror':3.8,'fire':4.95,'split':1.55,'death':3.5},{'slam':4.85,'wheel':5.35,'throw':5.7,'death':3.5}]
PRIMARY=['coffin','canopy','war_frame','yoke','chassis','beast_body','fox_body','furnace']

def keys(axis,seq):return [(t,[v if j==axis else 0 for j in range(3)]) for t,v in seq]
def animate(g,i):
 durations={'idle':4.,'walk':[2.6,3.2,2.1,2.6,1.8,1.8,2.0,2.8][i],'hurt':.45,**DURATIONS[i]}
 for clip,t in durations.items():g.anim[clip]={'loop':clip in ['idle','walk'],'animation_length':t,'bones':{}}
 def tr(c,b,k,seq):g.track(c,b,k,seq)
 def rot(c,b,axis,seq):tr(c,b,'rotation',keys(axis,seq))
 def pos(c,b,axis,seq):tr(c,b,'position',keys(axis,seq))
 def cyc(c,b,axis,amp,period=4.,phase=0,channel='rotation'):
  seq=[]
  for j in range(9):
   t=j*period/8;v=round(math.sin(j*math.pi/4+phase)*amp,4);seq.append((round(t,5),[v if d==axis else 0 for d in range(3)]))
  tr(c,b,channel,seq)
 p=PRIMARY[i];rot('hurt',p,0,[(0,0),(.08,-5),(.22,4),(.45,0)])
 if i==0:
  cyc('idle','coffin',2,1.2);cyc('idle','dragon_skull',0,3,phase=1);cyc('idle','dragon_jaw',0,5)
  cyc('walk','coil_base',1,7,2.6);cyc('walk','coffin',2,4,2.6);cyc('walk','dragon_spine_0',1,5,2.6)
  for c in ['attack','cast']:
   t=durations[c]
   for s in [-1,1]:rot(c,'lid_'+str(s),1,[(0,0),(.2,s*20),(.4,s*50),(t,0)])
   rot(c,'dragon_skull',0,[(0,0),(.18,-15),(.36,24),(t,0)]);rot(c,'dragon_jaw',0,[(0,0),(.3,34),(.55,4),(t,0)]);rot(c,'edict_arm',2,[(0,0),(.3,26),(t,0)])
  rot('death','root',2,[(0,0),(.35,18),(.85,78)]);rot('death','dragon_spine_3',0,[(0,0),(.85,35)])
 elif i==1:
  cyc('idle','mask',2,4);cyc('idle','canopy',1,3)
  for n in g.by:
   if n.startswith('hanging_cloth_'):cyc('idle',n,0,7,phase=int(n[-1])*.8);cyc('walk',n,0,16,3.2,phase=int(n[-1])*.6)
  cyc('walk','canopy',2,5,3.2);cyc('walk','mask',1,13,3.2)
  for c in ['attack','cast']:
   t=durations[c]
   for j in range(7):rot(c,'curtain_fan_'+str(j),1,[(0,0),(t*.4,(j-3)*9),(t*.7,(j-3)*14),(t,0)])
   for s in [-1,1]:rot(c,'sleeve_'+str(s),2,[(0,0),(t*.35,s*28),(t*.7,s*40),(t,0)]);rot(c,'fingers_'+str(s),0,[(0,0),(t*.6,-40),(t,0)])
   pos(c,'mask',2,[(0,0),(t*.5,-7),(t,0)])
  for j in range(7):rot('death','curtain_fan_'+str(j),2,[(0,0),(.8,-(j-3)*16)])
  pos('death','canopy',1,[(0,0),(.9,-29)])
  for n in g.by:
   if n.startswith('hanging_cloth_'):rot('death',n,0,[(0,0),(.9,86)])
 elif i==2:
  cyc('idle','war_core',1,10);cyc('idle','breach_arm',0,2)
  cyc('walk','war_frame',2,4,2.1);cyc('walk','breach_arm',0,8,2.1)
  for j,n in enumerate(g.gait):pos('walk',n,1,[(0,0),(.525,3 if j==0 else 0),(1.05,0),(1.575,3 if j else 0),(2.1,0)])
  rot('attack','weapon_arm',0,[(0,0),(.4,-72),(.6,25),(1.2,0)]);rot('attack','war_frame',1,[(0,0),(.4,-18),(.6,23),(1.2,0)])
  rot('cast','breach_arm',0,[(0,0),(.5,-70),(1.0,-65),(1.5,0)])
  rot('death','root',2,[(0,0),(.3,-15),(.9,-64)]);rot('death','breach_arm',0,[(0,0),(.9,-20)])
 elif i==3:
  cyc('idle','bound_head',2,5);cyc('idle','giant_arm_-1',0,2,phase=1)
  cyc('walk','yoke',2,3,2.6)
  for j,n in enumerate(g.gait):cyc('walk',n,0,5,2.6,phase=j*2)
  rot('roar','bound_head',2,[(0,0),(.6,15),(1.2,48),(1.8,43),(2.5,0)]);rot('roar','giant_arm_-1',0,[(0,0),(1.2,-25),(2.5,0)])
  rot('spin','yoke',1,[(0,0),(.8,-25),(1.3,160),(1.8,340),(2.3,520),(3.85,720)])
  rot('throw','giant_arm_1',0,[(0,0),(.6,-95),(1.,25),(2.5,0)]);rot('throw','forearm_1',0,[(0,0),(.6,40),(1.,-20),(2.5,0)])
  pos('death','yoke',1,[(0,0),(.7,-7),(2.5,-16)])
  rot('death','bound_head',2,[(0,0),(2.5,56)])
  for s in [-1,1]:rot('death','giant_arm_'+str(s),2,[(0,0),(2.5,s*60)]);rot('death','forearm_'+str(s),2,[(0,0),(2.5,-s*45)]);rot('death','yoke',2,[(0,0),(2.5,16)])
 elif i==4:
  cyc('idle','pilot',1,12);cyc('idle','drive_shaft',2,8)
  rot('walk','drive_shaft',2,[(0,0),(1.8,360)])
  for n in g.by:
   if n.startswith('manipulator_'):cyc('idle',n,0,3,phase=1 if n.endswith('-1') else 0)
  for c,hit in [('net',.7),('wheels',.5),('spiders',1.)]:
   t=durations[c]
   for s in [-1,1]:
    for j in [0,1]:rot(c,'manipulator_'+str(j)+'_'+str(s),0,[(0,0),(hit*.5,-20),(hit,35),(min(t,hit+.4),15),(t,0)]);rot(c,'tool_'+str(j)+'_'+str(s),2,[(0,0),(hit,s*22),(t,0)])
   if c=='wheels':rot(c,'drive_shaft',2,[(0,0),(t,1080)])
   if c=='spiders':rot(c,'boiler',0,[(0,0),(.8,0),(1.,-55),(2.,-55),(t,0)])
  pos('death','chassis',1,[(0,0),(.6,-7),(2.7,-17)]);rot('death','chassis',2,[(0,0),(1.,8),(2.7,14)])
 elif i==5:
  cyc('idle','beast_neck',0,3);cyc('idle','beast_tail',1,8)
  cyc('walk','beast_tail',1,14,1.8)
  rot('sweep','pole_turret',1,[(0,0),(.75,-70),(1.,0),(1.15,100),(2.65,0)])
  rot('sweep','beast_neck',1,[(0,0),(.75,-12),(1.15,16),(2.65,0)])
  rot('charge','beast_neck',0,[(0,0),(.6,16),(.8,20),(1.6,20),(3.1,0)]);pos('charge','beast_body',1,[(0,0),(.7,-3),(1.6,-3),(3.1,0)])
  for j in range(4):rot('order','dorsal_scale_'+str(j),0,[(0,0),(.9,-22),(1.2,-35),(2.,-30),(3.,0)])
  rot('death','beast_body',2,[(0,0),(.7,-18),(2.8,-78)])
 elif i==6:
  cyc('idle','fox_head',1,13);cyc('idle','fox_neck',0,2)
  for j in range(3):
   cyc('idle',f'tail_{j}_root',1,5,phase=j);cyc('idle',f'tail_{j}_mid',0,4,phase=j*.6)
   cyc('walk',f'tail_{j}_root',1,9,2.,phase=j*.4)
  for c,hit in [('mirror',1.),('fire',1.),('split',.3)]:
   t=durations[c];rot(c,'fox_neck',0,[(0,0),(hit*.6,-20),(hit,-32),(t,0)])
   for j in range(3):rot(c,f'tail_{j}_root',1,[(0,0),(hit,(j-1)*22),(t*.8,(j-1)*28),(t,0)]);rot(c,f'tail_{j}_mid',0,[(0,0),(hit,-10),(t,0)])
   if c=='fire':pos(c,'front_-1',1,[(0,0),(.7,5),(1.,9),(1.6,0),(t,0)])
  rot('death','fox_body',2,[(0,0),(.7,15),(2.7,84)])
  for j in range(3):rot('death',f'tail_{j}_root',1,[(0,0),(2.7,(1-j)*40)])
 elif i==7:
  cyc('idle','inset_face',1,5);cyc('idle','hammer_piston_-1',0,2)
  cyc('walk','furnace',2,3,2.8)
  for j,n in enumerate(g.gait):pos('walk',n,1,[(0,0),(.7,3 if j==0 else 0),(1.4,0),(2.1,3 if j else 0),(2.8,0)])
  for s in [-1,1]:rot('slam','hammer_yoke_'+str(s),0,[(0,0),(.7,-35),(1.22,-75 if s<0 else -55),(1.4,0),(1.65,-10),(4.85,0)])
  pos('slam','furnace',1,[(0,0),(1.2,2),(1.4,-2),(1.65,-1),(4.85,0)])
  for s in [-1,1]:rot('wheel','hammer_yoke_'+str(s),1,[(0,0),(.8,s*65),(1.3,-s*50),(2.1,s*65),(2.9,-s*50),(3.35,s*60),(5.35,0)])
  rot('throw','hammer_yoke_1',0,[(0,0),(1.5,-70),(1.8,-30),(2.4,0),(5.7,0)]);tr('throw','hammer_1','scale',[(0,[1,1,1]),(1.79,[1,1,1]),(1.8,[0,0,0]),(4.19,[0,0,0]),(4.2,[1,1,1]),(5.7,[1,1,1])])
  pos('death','furnace',1,[(0,0),(.6,-4),(2.7,-13)]);rot('death','furnace',0,[(0,0),(2.7,18)])
  for s in [-1,1]:rot('death','hammer_yoke_'+str(s),0,[(0,0),(2.7,-35)]);rot('death','hammer_piston_'+str(s),0,[(0,0),(2.7,25)])
 # Solved, alternating foot contacts for quadrupeds and the six-legged mechanism.
 if i in [4,5,6]:
  period=durations['walk'];axis=0 if i==4 else 2;rotaxis=2 if i==4 else 0;sgn=1 if i==4 else -1
  for index,n in enumerate(g.gait):
   lower=n.replace('outrigger_','link_') if i==4 else n.replace('front_','front_paw_').replace('rear_','rear_paw_')
   b=g.by[lower];foot=b['cubes'].pop();f=[foot['origin'][j]+foot['size'][j]/2 for j in range(3)];sole=g.bone(lower+'_sole',lower,f);g.by[sole]['cubes'].append(foot)
   h=g.by[n]['pivot'];k=b['pivot'];l1=math.hypot(k[1]-h[1],k[axis]-h[axis]);l2=math.hypot(f[1]-k[1],f[axis]-k[axis]);base1=math.atan2(k[axis]-h[axis],k[1]-h[1]);base2=math.atan2(f[axis]-k[axis],f[1]-k[1]);phase=(index%2 if i==4 else (index in [0,3]))*.5
   tracks=[[],[],[]]
   for step in range(17):
    t=step*period/16;u=(step/16+phase)%1;lift=5*math.sin(u*math.pi*2) if u<.5 else 0;stroke=2.5*math.cos(u*2*math.pi);dy=f[1]+lift-h[1];other=f[axis]+stroke-h[axis];dist=min(l1+l2-.01,max(abs(l1-l2)+.01,math.hypot(dy,other)));factor=dist/max(.0001,math.hypot(dy,other));dy*=factor;other*=factor;theta=math.atan2(other,dy);off=math.acos(max(-1,min(1,(l1*l1+dist*dist-l2*l2)/(2*l1*dist))))
    choices=[theta-off,theta+off];a1=min(choices,key=lambda v:abs(math.atan2(math.sin(v-base1),math.cos(v-base1))));dy2=dy-l1*math.cos(a1);do2=other-l1*math.sin(a1);a2=math.atan2(do2,dy2)
    d1=math.atan2(math.sin(a1-base1),math.cos(a1-base1));d2=math.atan2(math.sin(a2-base2),math.cos(a2-base2));angles=[sgn*math.degrees(d1),sgn*math.degrees(d2-d1),-sgn*math.degrees(d2)]
    for j,v in enumerate(angles):tracks[j].append((round(t,5),round(v,4)))
   for bn,trk in zip([n,lower,sole],tracks):rot('walk',bn,rotaxis,trk)
 # Keep only the authored channels; no common humanoid swing is shared between species.
 prefix='' if i<3 else 'animation.'+g.id+'.'
 g.anim={prefix+k:v for k,v in g.anim.items()}
