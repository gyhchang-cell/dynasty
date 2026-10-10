"""Cuboid vertices in Gecko model space; export-time math, no gameplay state."""
import math
from itertools import product

def sample(track,t):
 if isinstance(track,list):return track
 pairs=sorted((float(k),v) for k,v in track.items())
 if t<=pairs[0][0]:return pairs[0][1]
 for (a,v),(b,w) in zip(pairs,pairs[1:]):
  if t<=b:return [v[i]+(w[i]-v[i])*(t-a)/(b-a) for i in range(3)]
 return pairs[-1][1]

def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def transform(p=(0,0,0),r=(0,0,0),s=(1,1,1)):
 x,y,z=map(math.radians,[-r[0],-r[1],r[2]])
 cx,cy,cz=math.cos(x),math.cos(y),math.cos(z);sx,sy,sz=math.sin(x),math.sin(y),math.sin(z)
 rx=[[1,0,0,0],[0,cx,-sx,0],[0,sx,cx,0],[0,0,0,1]]
 ry=[[cy,0,sy,0],[0,1,0,0],[-sy,0,cy,0],[0,0,0,1]]
 rz=[[cz,-sz,0,0],[sz,cz,0,0],[0,0,1,0],[0,0,0,1]]
 m=mul(mul(rz,ry),rx)
 for i in range(3):
  for j in range(3):m[i][j]*=s[j]
  m[i][3]=p[i]*(-1 if i==0 else 1)
 return m

def vertices(bones,channels,t):
 pivots={b['name']:b['pivot'] for b in bones};world={};out=[]
 for b in bones:
  pivot=b['pivot'];parent=b.get('parent');ch=channels.get(b['name'],{})
  p=[pivot[i]-(pivots[parent][i] if parent else 0) for i in range(3)]
  r=b.get('rotation',[0,0,0]).copy()
  for field,dest in [('position',p),('rotation',r)]:
   if field in ch:
    for i,v in enumerate(sample(ch[field],t)):dest[i]+=v
  matrix=mul(world[parent],transform(p,r,sample(ch['scale'],t) if 'scale' in ch else [1,1,1])) if parent else transform(p,r)
  world[b['name']]=matrix
  for cube in b.get('cubes',[]):
   cp=cube.get('pivot',pivot);cm=mul(matrix,transform([cp[i]-pivot[i] for i in range(3)],cube.get('rotation',[0,0,0])))
   for corner in product((0,1),repeat=3):
    v=[(cube['origin'][i]+cube['size'][i]*corner[i]-cp[i])*(-1 if i==0 else 1) for i in range(3)]+[1]
    out.append([sum(cm[i][j]*v[j] for j in range(4)) for i in range(3)])
 return out

def ground_death(rig):
 """Species fall and folded regalia, with the lowest Cuboid on the floor."""
 length=.7;dragon=rig.id=='dragon_emperor';king=rig.id=='dragon_king'
 ch={}
 def bend(b,end):
  ch[b]={'rotation':{'0':[0,0,0],'0.175':[v*.18 for v in end],'0.49':[v*.86 for v in end],'0.7':end}}
 bend('body',[0,0,80 if dragon else 86 if king else 90])
 bend('chest',[-5 if dragon else 6,0,0]);bend('jaw',[25 if dragon or king else 8,0,0])
 if dragon:
  bend('neck_0',[8,0,0]);bend('neck_3',[5,0,0])
  for side,sign in [('left',1),('right',-1)]:
   for end in ['front','hind']:
    bend(end+'_'+side+'_leg',[12,0,sign*18]);bend(end+'_'+side+'_leg_shin',[22,0,0])
 elif not king:
  bend('left_arm',[15,0,15]);bend('right_arm',[20,0,-10])
 else:
  bend('left_arm',[10,0,15]);bend('right_arm',[15,0,-10]);bend('tail_0',[0,8,0])
 if rig.id=='nine_heaven_general':
  bend('storm_ring_outer',[0,90,0]);bend('storm_ring_inner',[0,90,0])
  for side,sign in [('left',1),('right',-1)]:
   name='thunder_drum_'+side;bend(name,[0,90,0])
   ch[name]['position']={'0':[0,0,0],'0.7':[-sign*4,0,0]}
   for i in range(3):
    name='thunder_blade_'+side+'_'+str(i);bend(name,[0,90,0])
    # Six levitating blades settle beside the corpse rather than keeping
    # the dead torso suspended on their former wide fan arrangement.
    ch[name]['position']={'0':[0,0,0],'0.7':[-sign*(15+i*4-6),0,0]}
 # Dense authored position keys compensate the actual lowest animated cube.
 # They move the whole rig once, preserving child and weapon relationships.
 pos={}
 for i in range(113):
  t=length*i/112;low=min(v[1] for v in vertices(rig.bones,ch,t))
  pos[format(t,'.6g')]=[0,round(-low+(.03 if i else 0),6),0]
 ch['body']['position']=pos
 return {'loop':False,'animation_length':length,'bones':ch}
