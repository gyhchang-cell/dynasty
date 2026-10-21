#!/usr/bin/env python3
"""81 real animated poses: oriented-box separating-axis checks for the entire connected rig."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/art/boss-forms'))
import texture_review as v
v.r.CATEGORY='scenic'

def obb(quads):
    pts=np.concatenate([x[0] for x in quads]);q=quads[0][0]
    a=q[1]-q[0];b=q[3]-q[0];axes=np.array([a/np.linalg.norm(a),b/np.linalg.norm(b),np.cross(a,b)/np.linalg.norm(np.cross(a,b))])
    return pts,axes

def touches(a,b):
    ap,aa=a;bp,ba=b
    if np.any(ap.max(0)<bp.min(0)-1e-6) or np.any(bp.max(0)<ap.min(0)-1e-6):return False
    axes=list(aa)+list(ba)+[np.cross(x,y) for x in aa for y in ba]
    for axis in axes:
        if np.linalg.norm(axis)<1e-8:continue
        axis=axis/np.linalg.norm(axis);p=ap@axis;q=bp@axis
        if max(p)<min(q)-1e-6 or max(q)<min(p)-1e-6:return False
    return True

results=[]
for lod in ('','_medium','_far'):
    path=ROOT/f'src/main/resources/assets/dynasty/geo/scenic/azure_dragon{lod}.geo.json'
    for tick in range(81):
        quads=v.r.geometry('azure_dragon',clip='animation.scenic.idle',tick=tick,geo_path=path)
        assert len(quads)%6==0
        boxes=[obb(quads[i:i+6]) for i in range(0,len(quads),6)]
        seen={0};pending=[0]
        while pending:
            i=pending.pop()
            for j in range(len(boxes)):
                if j not in seen and touches(boxes[i],boxes[j]):seen.add(j);pending.append(j)
        if len(seen)!=len(boxes):
            missing=[(i,quads[i*6][2]) for i in range(len(boxes)) if i not in seen]
            raise AssertionError((lod,tick,missing))
    results.append({'lod':lod or 'full','poses':81,'connected_cubes':len(boxes),'floating':0})
p=ROOT/'docs/art/cod3-azure-dragon-v2/connection-validation.json';p.write_text(json.dumps(results,indent=2)+'\n');print('PASS',results)
