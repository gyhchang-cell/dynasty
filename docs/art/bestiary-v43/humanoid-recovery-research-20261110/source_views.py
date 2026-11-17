"""Read-only external source study; never exports Dynasty runtime assets."""
from pathlib import Path
import sys, importlib.util, math, json, hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tools/art/bestiary-v41'))
spec=importlib.util.spec_from_file_location('raster_study',ROOT/'tools/art/bestiary-v41/review.py')
pv=importlib.util.module_from_spec(spec);spec.loader.exec_module(pv)
from build_models import face_rects
OUT=ROOT/'build/bestiary-v43/human-companions-source-20261110';OUT.mkdir(parents=True,exist_ok=True)
ATLAS=ROOT/'build/bestiary-v43/references/justinwon777__HumanCompanions/forge 1.20.1/src/main/resources/assets/humancompanions/textures/entities/male/medieval-man-hugh.png'
# Native 1.20.1 wide PlayerModel mesh: origin, size, pivot, UV, deformation.
BASE={
'head':((-4,-8,-4),(8,8,8),(0,0,0),(0,0),0),
'body':((-4,0,-2),(8,12,4),(0,0,0),(16,16),0),
'right_arm':((-3,-2,-2),(4,12,4),(-5,2,0),(40,16),0),
'left_arm':((-1,-2,-2),(4,12,4),(5,2,0),(32,48),0),
'right_leg':((-2,0,-2),(4,12,4),(-1.9,12,0),(0,16),0),
'left_leg':((-2,0,-2),(4,12,4),(1.9,12,0),(16,48),0),
}
PARTS=dict(BASE)
for name,parent,uv,d in [('hat','head',(32,0),.5),('jacket','body',(16,32),.25),('right_sleeve','right_arm',(40,32),.25),('left_sleeve','left_arm',(48,48),.25),('right_pants','right_leg',(0,32),.25),('left_pants','left_leg',(0,48),.25)]:
 o,s,p,_,_=BASE[parent];PARTS[name]=(o,s,p,uv,d)
PARENT={'hat':'head','jacket':'body','right_sleeve':'right_arm','left_sleeve':'left_arm','right_pants':'right_leg','left_pants':'left_leg'}
def geometry(bow=False):
 q=[]
 # Isolated source bow pose, head yaw/pitch=0. Not full setupAnim replay.
 rots={'right_arm':(-math.pi/2,-.1,0),'left_arm':(-math.pi/2,.5,0)} if bow else {}
 for n,(o,s,p,uv,d) in PARTS.items():
  m=pv.matrix(p,rots.get(PARENT.get(n,n),(0,0,0)))
  pts=pv.V*(np.array(s)+2*d)+np.array(o)-d
  pts=pts@m[:3,:3].T+m[:3,3];pts[:,1]=24-pts[:,1]
  pts*=.9375 # CompanionRenderer.scale; model-space view, not bounding-box measurement.
  for f,ids in pv.POLYS.items():
   u,v,w,h=face_rects({'size':s,'uv':uv})[f]
   if f=='down':v+=h;h=-h
   tc=np.array([[u+w,v],[u,v],[u,v+h],[u+w,v+h]],float)
   q.append((pts[ids],tc,n))
 return q
views=[]
for state,yaw in [('neutral',0),('neutral',45),('neutral',90),('neutral',180),('bow-pose-only',45)]:
 name=f'{state}-{yaw}.png';p=OUT/name
 pv.raster(geometry(state!='neutral'),Image.open(ATLAS),yaw=yaw,size=(420,440),scale=11,mode='unlit').save(p)
 views.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'state':state,'yaw':yaw})
canvas=Image.new('RGB',(420*5,440),'#ece9df')
for i,v in enumerate(views):canvas.paste(Image.open(ROOT/v['path']).convert('RGB'),(420*i,0))
canvas.save(OUT/'overview.png')
(OUT/'views.json').write_text(json.dumps({'views':views,'limits':['Source-only offline pixel-textured model, not Minecraft screenshot.','No armor, held items, head items or elytra.','Bow panel isolates native bow branch at zero head rotation; omits locomotion, bobbing and full entity setupAnim.','No Dynasty resources or external assets copied into runtime.']},indent=2)+'\n')
print(OUT/'overview.png')
