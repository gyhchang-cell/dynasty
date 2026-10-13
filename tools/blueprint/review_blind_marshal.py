#!/usr/bin/env python3
"""Actual dual-form source poses, fixed5.5px/unit; never a game/client proof."""
from pathlib import Path
import json,numpy as np
from functools import lru_cache
from types import SimpleNamespace
R=Path(__file__).resolve().parents[2]
p=R/'tools/blueprint/review_taoyan_cauldrons.py'
exec(p.read_text().split('\nreport={}\n',1)[0])
ID='gongsun_wuwang';D=R/'docs/blueprint-cod1/evidence/blind-marshal-v1';D.mkdir(parents=True,exist_ok=True)
r.json=SimpleNamespace(loads=lru_cache(maxsize=8)(json.loads))
def render(clip='idle',tick=0,yaw=45,mode='lit'):
 q=r.geometry(ident,clip=f'animation.{ID}.{clip}',tick=tick);tex=np.array(Image.open(A/f'textures/entity/blueprint/boss/{ident}.png').convert('RGB'))
 if mode in ('shape_gray','silhouette'):
  flat=np.full((2,2,3),176 if mode=='shape_gray' else 0,dtype=np.uint8);q=[(v,{'uv':[0,0],'uv_size':[2,2],'_tex':flat},b) for v,u,b in q]
 return raster(q+references(yaw),tex,yaw=yaw,elevation=8,size=(1500,1000),mode='unlit' if mode=='silhouette' else 'lit')
report={}
for ident in (ID,ID+'_foot'):
 anim=json.loads((A/f'animations/blueprint/boss/{ident}.animation.json').read_text())['animations'];rows={}
 for clip,data in anim.items():
  samples=[]
  for t in np.linspace(0,data['animation_length']*20,81):
   q=r.geometry(ident,clip=clip,tick=float(t));pts=np.concatenate([v for v,u,b in q]);mins={b:min(float(v[:,1].min()) for v,u,bone in q if bone==b) for b in {x[2] for x in q}}
   samples.append({'minimumY':float(pts[:,1].min()),'maximumY':float(pts[:,1].max()),'maximumRadius':float(np.linalg.norm(pts[:,[0,2]],axis=1).max()),'lowestBone':min(mins,key=mins.get)})
  name=clip.rsplit('.',1)[1];rows[name]={'minimumY':min(x['minimumY'] for x in samples),'maximumY':max(x['maximumY'] for x in samples),'maximumRadius':max(x['maximumRadius'] for x in samples),'lowestBone':min(samples,key=lambda x:x['minimumY'])['lowestBone']};print(ident,name,rows[name],flush=True)
 report[ident]=rows
 sheet([render(yaw=y,mode=m) for y,m in ((0,'lit'),(180,'lit'),(90,'lit'),(-90,'lit'),(45,'lit'),(45,'shape_gray'),(45,'silhouette'))],['正面','背面','右侧','左侧','45度','灰模','剪影'],ident+' / 固定5.5px每单位 / 原创1.8m人物、1m石块 / 软件预览',ident+'-views.png',cols=3)
 sheet([render(c,t) for c,t in [('intro',100),('trample',30),('slash',16),('listen',30),('arrows',24),('morph',0),('morph',30),('morph',60),('onslaught',48),('storm',24),('death',40),('death',200)]],[f'{c} {t}t' for c,t in [('intro',100),('trample',30),('slash',16),('listen',30),('arrows',24),('morph',0),('morph',30),('morph',60),('onslaught',48),('storm',24),('death',40),('death',200)]],ident+' / 全技能与变形源姿态 / 软件预览',ident+'-poses.png',cols=3)
(D/'software-sampling.json').write_text(json.dumps({'source':'actual exported software poses; native not run','samplesPerClip':81,'forms':report},indent=2)+'\n')
