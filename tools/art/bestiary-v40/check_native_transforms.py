import json,math,sys
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools/art/boss-forms'));import texture_review as v
report={}
for kind in ('nian_beast','qilin'):
 D=R/'docs/art/bestiary-v40'/kind;parts=json.loads((D/'design.json').read_text());by={p['name']:p for p in parts};maxerr=0
 for tick in range(21):
  # Interchange clip is piecewise linear; independently reproduce the same
  # sampled native joint angles (actual runtime uses smooth cosine).
  a=json.loads((D/'model.animation.json').read_text())['animations']['animation.bestiary.walk']['bones'];world={};q=v.r.geometry(kind,clip='animation.bestiary.walk',tick=tick,geo_path=D/'model.geo.json',animation_path=D/'model.animation.json')
  for i,p in enumerate(parts):
   pp=by[p['parent']]['pivot'] if p['parent']!='root' else [0,24,0];pos=np.array(p['pivot'])-pp;pos=pos*[1,-1,1]
   if p['parent']=='root':pos=np.array([p['pivot'][0],24-p['pivot'][1],p['pivot'][2]])
   rot=np.radians(np.array(p['rotation'])+(v.r.sample(a[p['name']]['rotation'],tick/20) if p['name'] in a else 0));x,y,z=rot;cx,cy,cz=np.cos(rot);sx,sy,sz=np.sin(rot)
   rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
   mat=np.eye(4);mat[:3,:3]=rz@ry@rx;mat[:3,3]=pos;world[p['name']]=(world[p['parent']] if p['parent']!='root' else np.eye(4))@mat
   center=np.array(p['origin'])+np.array(p['size'])/2-np.array(p['pivot']);center[1]*=-1
   native=(world[p['name']]@np.r_[center,1])[:3]*[-1,-1,1]+[0,24,0];preview=np.concatenate([qq[0] for qq in q[i*6:i*6+6]]).mean(0);maxerr=max(maxerr,float(np.max(np.abs(native-preview))))
 assert maxerr<1e-8,maxerr
 report[kind]={'native_vs_interchange_max_center_error':maxerr,'poses':21,'scope':'independent native hierarchical transform math; not engine bake or runtime acceptance'}
print(report)
(R/'docs/art/bestiary-v40/native-transform-check.json').write_text(json.dumps(report,indent=2)+'\n')
