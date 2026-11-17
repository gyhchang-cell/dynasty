import math,json
from pathlib import Path

def crosses(a,b,block,pad=0):
 near,far=0.,1.
 for i in range(3):
  low=block[i]-pad;high=block[i]+1+pad;d=b[i]-a[i]
  if abs(d)<1e-9:
   if a[i]<=low or a[i]>=high:return False
   continue
  x,y=(low-a[i])/d,(high-a[i])/d;near=max(near,min(x,y));far=min(far,max(x,y))
 return near<far-1e-6 and far>1e-6 and near<1-1e-6

def protected(anchor,shield,p):
 source=[v+.5 for v in anchor]
 return all(crosses(source,[p[0]+x,p[1]+y,p[2]+z],shield,-.01) for x in [-.31,.31] for y in [.01,1.81] for z in [-.31,.31])

def visible(anchor,shield,p):
 eye=[p[0],p[1]+1.62,p[2]]
 for axis in range(3):
  for side in [0,1]:
   plane=anchor[axis]+side
   if (eye[axis]-plane)*(1 if side else -1)<=0:continue
   other=[i for i in range(3) if i!=axis]
   for u in [.5,.06,.94]:
    for v in [.5,.06,.94]:
     q=[0.,0.,0.];q[axis]=plane;q[other[0]]=anchor[other[0]]+u;q[other[1]]=anchor[other[1]]+v
     if math.dist(eye,q)<4.485 and not any(crosses(eye,q,b,.02) for b in shield):return q
 return None
result=[]
for ay in [65,66,67]:
 a=[0,ay,3];origin=[.5,65,.5];solutions=[]
 offsets=sorted([(x/20,z/20) for x in range(-17,18) for z in range(-17,18) if x*x+z*z<=17*17],key=lambda v:math.hypot(*v))
 for dx,dz in offsets:
  p=[origin[0]+dx,origin[1],origin[2]+dz]
  for y in [ay,ay-1,ay+1]:
   for x,z in [(0,2),(-1,2),(1,2),(0,1)]:
    b=[x,y,z]
    if not protected(a,b,p):continue
    ray=visible(a,[b],p)
    if ray:solutions.append({'move':math.hypot(dx,dz),'position':p,'shield':b,'ray':ray});break
   if solutions:break
  if solutions:break
 result.append({'anchor':a,'nearest_in_grid':solutions[:1]})
print(json.dumps(result,indent=2));Path(__file__).with_name('geometry-probe.json').write_text(json.dumps(result,indent=2))
