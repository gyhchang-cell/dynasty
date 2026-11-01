"""Fixed source geometry + PNG + numeric shoot channel inspection; not Gecko runtime."""
from pathlib import Path
import json,math,hashlib,ast,collections
import numpy as np
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent;A=B/'sources/Virus5600__Defensive-Measures-Mod/src/main/resources/assets/dm';font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
g=json.loads((A/'geo/ballista.geo.json').read_text())['minecraft:geometry'][0];anim=json.loads((A/'animations/ballista.animation.json').read_text())['animations']['animation.ballista.shoot'];tex=np.array(Image.open(A/'textures/entity/ballista/ballista.png').convert('RGBA'));texcache={'actual':tex}
# Reuse only the reviewed generic raster function, not the source module's top-level side effects.
tree=ast.parse((B.parent/'batch-22/inspect-assets.py').read_text());f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='render');exec(compile(ast.Module(body=[f],type_ignores=[]),'<reviewed-nearest-raster>','exec'))
def channel(v,t,default):
 if v is None:return np.array(default,float)
 if isinstance(v,list):return np.array(v,float)
 keys=sorted((float(k),val) for k,val in v.items());lo=keys[0];hi=keys[-1]
 if t<=lo[0]:return np.array(lo[1],float)
 if t>=hi[0]:return np.array(hi[1],float)
 for a,b in zip(keys,keys[1:]):
  if a[0]<=t<=b[0]:return np.array(a[1],float)+(np.array(b[1],float)-a[1])*(t-a[0])/(b[0]-a[0])
def matrix(pivot,rot,pos,scale):
 rx,ry,rz=np.radians(rot);cx,sx=np.cos(rx),np.sin(rx);cy,sy=np.cos(ry),np.sin(ry);cz,sz=np.cos(rz),np.sin(rz)
 Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);Rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]]);r=Rz@Ry@Rx@np.diag(scale);m=np.eye(4);m[:3,:3]=r;m[:3,3]=pivot+pos-r@pivot;return m
bones={b['name']:b for b in g['bones']}
def mesh(t):
 mats={};fs=[]
 def bm(n):
  if n in mats:return mats[n]
  b=bones[n];an=anim['bones'].get(n,{}) if t is not None else {};pivot=np.array(b['pivot'],float);r=np.array(b.get('rotation',[0,0,0]),float)+channel(an.get('rotation'),t,[0,0,0]);m=matrix(pivot,r,channel(an.get('position'),t,[0,0,0]),channel(an.get('scale'),t,[1,1,1]));mats[n]=bm(b['parent'])@m if 'parent' in b else m;return mats[n]
 for b in g['bones']:
  for c in b.get('cubes',[]):
   x0,y0,z0=c['origin'];w,h,d=c['size'];x1,y1,z1=np.array(c['origin'])+np.array(c['size']);u,v=c['uv'];uvs={'west':[u,v+d,u+d,v+d+h],'north':[u+d,v+d,u+d+w,v+d+h],'east':[u+d+w,v+d,u+2*d+w,v+d+h],'south':[u+2*d+w,v+d,u+2*d+2*w,v+d+h],'up':[u+d,v,u+d+w,v+d],'down':[u+d+w,v+d,u+d+2*w,v]};q={'north':[(x1,y1,z0),(x1,y0,z0),(x0,y0,z0),(x0,y1,z0)],'south':[(x0,y1,z1),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1)],'east':[(x1,y1,z1),(x1,y0,z1),(x1,y0,z0),(x1,y1,z0)],'west':[(x0,y1,z0),(x0,y0,z0),(x0,y0,z1),(x0,y1,z1)],'up':[(x0,y1,z0),(x0,y1,z1),(x1,y1,z1),(x1,y1,z0)],'down':[(x0,y0,z1),(x0,y0,z0),(x1,y0,z0),(x1,y0,z1)]}
   for side,p in q.items():
    p=np.array(p,float);p=(np.c_[p,np.ones(4)]@bm(b['name']).T)[:,:3]
    if np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))<1e-10:continue
    u0,v0,u1,v1=uvs[side]
    if c.get('mirror',b.get('mirror',False)):u0,u1=u1,u0
    uv=np.array([[u0,v0],[u0,v1],[u1,v1],[u1,v0]],float)/128
    fs.append(dict(points=p,uv=uv,texture='actual',bone=b['name']))
 return fs
states=[None,0,.04,.28,.6,.92,1.2];meshes={str(t):mesh(t) for t in states};allp=np.concatenate([f['points'] for fs in meshes.values() for f in fs]);sheet=Image.new('RGB',(1040,920),'#f2f1e8');d=ImageDraw.Draw(sheet)
for i,(yaw,lit) in enumerate([(0,False),(45,False),(90,False),(45,True)]):
 x=i%2*520;y=i//2*460;sheet.paste(render(meshes['None'],yaw,lit),(x,y+30));d.text((x+10,y+6),f'bind / {yaw}deg / '+('basic diffuse' if lit else 'raw PNG'),font=font,fill='#27303a')
sheet.save(B/'ballista-bind-software.png')
frames=[];contact=Image.new('RGB',(1040,1380),'#f2f1e8');d=ImageDraw.Draw(contact)
for i,t in enumerate(states[1:]):
 im=render(meshes[str(t)],45,True);x=i%2*520;y=i//2*460;contact.paste(im,(x,y+30));d.text((x+10,y+6),f'shoot t={t}s / numeric channels only',font=font,fill='#27303a');frames.append(im)
contact.save(B/'shoot-numeric-frames.png')
# Visible UV allocation only, no source rewrite.
im=Image.fromarray(tex).resize((768,768),Image.Resampling.NEAREST);d=ImageDraw.Draw(im)
for f in meshes['None']:
 pts=[(u*768,v*768) for u,v in f['uv']];d.line(pts+[pts[0]],fill=(255,80,90,255),width=1)
im.save(B/'uv-ballista.png')
stats=dict(bones=len(bones),cubes=sum(len(b.get('cubes',[])) for b in g['bones']),bind_faces=len(meshes['None']),declared_texture=[128,128],actual_texture=list(Image.open(A/'textures/entity/ballista/ballista.png').size),renderer_scale=.8125,stages=states,shoot_length_seconds=anim['animation_length'],limits=['source hierarchy with approximate standard box-UV, numeric linear channels only','no Java/Gecko animation blending,query,controller or spawn execution','bind vs numeric shoot/near-degenerate frames software only; not game screenshot','same family0 extra units; original PNG unedited'])
(B/'geometry-inspection.json').write_text(json.dumps(stats,indent=2)+'\n');print(stats)
