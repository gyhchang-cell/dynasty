"""Bounded source-study render; external assets remain in build/, never runtime."""
from pathlib import Path
import sys, importlib.util, json, math, hashlib
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tools/art/bestiary-v41'))
spec=importlib.util.spec_from_file_location('source_study_raster',ROOT/'tools/art/bestiary-v41/review.py')
pv=importlib.util.module_from_spec(spec);spec.loader.exec_module(pv)
from build_models import face_rects

CACHE=ROOT/'build/bestiary-v43/prisoner-vanilla-atlas-20261109'
BONES=json.loads((ROOT/'build/bestiary-v43/humanoid-candidates/005-Goety-2-Prisoner.model.json').read_text())
# UV origins/logical dimensions transcribed from pinned PrisonerModel.createBodyLayer.
# Deformed dimensions come from the already cached source mesh; UV stays undeformed.
UV={
 'head':[((0,0),(8,10,8),False)], 'hat':[((32,0),(8,10,8),False)],
 'hat_rim':[((30,47),(16,16,1),False)], 'nose':[((24,0),(2,4,2),False)],
 'body':[((16,20),(8,12,6),False)], 'jacket':[((0,38),(8,20,6),False)],
 'arms':[((40,38),(8,4,4),False),((44,22),(4,8,4),False),((44,22),(4,8,4),True)],
 'right_leg':[((0,22),(4,12,4),False)], 'left_leg':[((0,22),(4,12,4),False)]}

def geometry(time=None):
    # Exact published keyframes only. No interpolation or full-game replay claimed.
    states={0:(-2.5,-5,0,0,0),.8:(-15,-90,-3,0,45),
            1.3:(35,-10,0,-3,0),2.75:(-2.5,-5,0,0,0)}
    upper,arms,arm_y,arm_z,hold=states[time] if time is not None else (0,0,0,0,0)
    changes={'upper_body':([math.radians(upper),0,0],[0,0,0]),
             'arms':([math.radians(arms),0,0],[0,arm_y,arm_z]),
             'head':([math.radians(2.5 if time is not None else 0),0,0],[0,0,0]),
             'hold':([math.radians(hold),0,0],[0,0,0])}
    world={};q=[]
    for n,b in BONES.items():
        rot,pos=changes.get(n,([0,0,0],[0,0,0]))
        world[n]=(world[b['parent']] if b['parent'] else np.eye(4))@pv.matrix(np.array(b['pos'])+pos,np.array(b['rot'])+rot)
        for c,(uv,size,mirror) in zip(b['boxes'],UV.get(n,[])):
            pts=pv.V*c['size']+c['origin']
            pts=pts@world[n][:3,:3].T+world[n][:3,3];pts[:,1]=24-pts[:,1]
            rects=face_rects({'uv':uv,'size':size})
            for f,ids in pv.POLYS.items():
                u,v,w,h=rects[f]
                if f=='down':v+=h;h=-h
                tc=np.array([[u+w,v],[u,v],[u,v+h],[u+w,v+h]],float)
                if mirror:tc[:,0]=tc[:,0].min()+tc[:,0].max()-tc[:,0]
                q.append((pts[ids],tc,n))
    return q,world['hold'][:3,3].tolist()

views=[]
for skin,angle,time,label in [('villager',0,None,'front'),('villager',45,None,'45'),
                            ('villager',90,None,'side'),('villager',180,None,'back'),
                            ('wandering_trader',45,None,'trader-45'),
                            *[('villager',45,t,'mining-'+str(t)) for t in (0,.8,1.3,2.75)]]:
    q,hand=geometry(time);name='source-'+label+'.png';p=CACHE/name
    pv.raster(q,Image.open(CACHE/(skin+'.png')),yaw=angle,size=(480,540),scale=11,mode='unlit').save(p)
    views.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                      skin=skin,yaw=angle,source_time_seconds=time,hold_in_native_model_coordinates=hand,
                      textured_faces=len(q)))
q0,h0=geometry(0);qe,he=geometry(2.75)
assert np.allclose(h0,he)
assert all(np.allclose(a[0],b[0]) for a,b in zip(q0,qe))
receipt=dict(status='source-only render; manual visual inspection required',views=views,
             published_mining_loop_endpoints_equal=True,
             limits=['Not a game capture or full composite renderer.',
                     'No profession, shackles, chain, head-item or held-item layers.',
                     'Only four exact mining keyframes; no CATMULLROM interpolation or movement AI.',
                     'No new Dynasty geometry, animation, PNG or attachment object.'])
(CACHE/'source-views.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('9 source views; loop endpoints agree; no runtime assets changed')
