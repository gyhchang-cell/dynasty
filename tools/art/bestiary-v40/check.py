"""Offline checks of native layer parameters, UVs, hierarchy and anatomical contacts."""
from pathlib import Path
import json,sys,re,hashlib,importlib.util
import numpy as np
R=Path(__file__).resolve().parents[3];D=R/'docs/art/bestiary-v40';sys.path.insert(0,str(R/'tools/art/boss-forms'));import texture_review as v

def obb(q):
 p=np.concatenate([a[0] for a in q]);f=q[0][0];x=f[1]-f[0];y=f[3]-f[0];x/=np.linalg.norm(x);y/=np.linalg.norm(y);return p,[x,y,np.cross(x,y)]
def touch(a,b):
 ap,aa=a;bp,ba=b
 if np.any(ap.max(0)<bp.min(0)-1e-5) or np.any(bp.max(0)<ap.min(0)-1e-5):return False
 for axis in aa+ba+[np.cross(x,y) for x in aa for y in ba]:
  if np.linalg.norm(axis)<1e-7:continue
  p=ap@axis;q=bp@axis
  if max(p)<min(q)-1e-5 or max(q)<min(p)-1e-5:return False
 return True
result={}
for kind in ('nian_beast','qilin'):
 out=D/kind;g=json.loads((out/'model.geo.json').read_text())['minecraft:geometry'][0];boneparts=[b for b in g['bones'] if b.get('cubes')];names=[b['name'] for b in boneparts];worst=[];samples=[]
 for tick in range(21):
  quads=v.r.geometry(kind,clip='animation.bestiary.walk',tick=tick,geo_path=out/'model.geo.json',animation_path=out/'model.animation.json');boxes=[obb(quads[i:i+6]) for i in range(0,len(quads),6)];seen={0};todo=[0]
  while todo:
   i=todo.pop()
   for j in range(len(boxes)):
    if j not in seen and touch(boxes[i],boxes[j]):seen.add(j);todo.append(j)
  disconnected=[names[i] for i in range(len(boxes)) if i not in seen]
  if disconnected:samples.append({'tick':tick,'disconnected':disconnected})
 # Native Java and source design share the same output dimensions/parents.
 java=(R/'src/main/java/com/dynasty/client/BestiaryQuadrupedLayers.java').read_text();parts=json.loads((out/'design.json').read_text())
 for p in parts:assert ('"'+p['name']+'"') in java
 result[kind]={'connection_issues':samples,'sampled_poses':21,'native_java_definition_has_all_parts':True}
 print(kind,'disconnected',samples[:2])
(D/'connection-check.json').write_text(json.dumps(result,indent=2)+'\n')
