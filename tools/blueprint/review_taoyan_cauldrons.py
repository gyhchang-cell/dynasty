#!/usr/bin/env python3
"""Review actual two-form living vessel, never launches Java or Minecraft."""
from pathlib import Path
import ast,json,math,importlib.util
from functools import lru_cache
from types import SimpleNamespace
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'docs/blueprint-cod1/evidence/taoyan-cauldron-v1';D.mkdir(parents=True,exist_ok=True)
ID='taoyan_zhishi';ident=ID
# Reuse the same documented fixed world camera, plain references and raster functions.
p=R/'tools/blueprint/review_bronze_suanni.py';ns={'__file__':str(p)};exec(p.read_text().split('report={}')[0],ns)
r=ns['r'];r.CATEGORY='blueprint/boss';r.json=SimpleNamespace(loads=lru_cache(maxsize=8)(json.loads));references=ns['references'];labelled=ns['labelled'];font=ns['font'];sheet_source=ast.parse(p.read_text())
for n in sheet_source.body:
 if isinstance(n,ast.FunctionDef) and n.name=='sheet':exec(ast.get_source_segment(p.read_text(),n),globals())
source=(R/'tools/art/boss-forms/texture_review.py').read_text()
for n in ast.parse(source).body:
 if isinstance(n,ast.FunctionDef) and n.name=='raster':
  code=ast.get_source_segment(source,n).replace('center=(lo+hi)/2','center=np.array([0,26,0])@basis.T').replace('else:scale=min((w-80)/(hi[0]-lo[0]),(h-60)/(hi[1]-lo[1]))','else:scale=5.5');exec(code,globals())
def render(clip='idle',tick=0,yaw=45,mode='lit'):
 q=r.geometry(ident,clip=f'animation.{ID}.{clip}',tick=tick);tex=np.array(Image.open(A/f'textures/entity/blueprint/boss/{ident}.png').convert('RGB'))
 if mode in ('shape_gray','silhouette'):
  flat=np.full((2,2,3),176 if mode=='shape_gray' else 0,dtype=np.uint8);q=[(v,{'uv':[0,0],'uv_size':[2,2],'_tex':flat},b) for v,u,b in q]
 return raster(q+references(yaw),tex,yaw=yaw,elevation=8,size=(1400,700),mode='unlit' if mode=='silhouette' else 'lit')
report={}
for stage in (1,2):
 ident=ID if stage==1 else ID+'_phase2';g=json.loads((A/f'geo/blueprint/boss/{ident}.geo.json').read_text())['minecraft:geometry'][0];anim=json.loads((A/f'animations/blueprint/boss/{ident}.animation.json').read_text())['animations'];rows={}
 for clip,data in anim.items():
  name=clip.rsplit('.',1)[1];samples=[]
  for t in np.linspace(0,data['animation_length']*20,81):
   q=r.geometry(ident,clip=clip,tick=float(t));pts=np.concatenate([v for v,u,b in q]);footnames=[b['name'] for b in g['bones'] if b['name'].endswith('_foot')];feet=[min(float(v[:,1].min()) for v,u,b in q if b==n) for n in footnames];mins={b:min(float(v[:,1].min()) for v,u,bone in q if bone==b) for b in {x[2] for x in q}};samples.append({'minimumY':float(pts[:,1].min()),'maximumY':float(pts[:,1].max()),'maxRadius':float(np.linalg.norm(pts[:,[0,2]],axis=1).max()),'groundedFeet':sum(abs(y)<.2 for y in feet),'lowestBone':min(mins,key=mins.get)})
  rows[name]={'minimumY':min(x['minimumY'] for x in samples),'maximumY':max(x['maximumY'] for x in samples),'maximumRadius':max(x['maxRadius'] for x in samples),'minGroundedFeet':min(x['groundedFeet'] for x in samples),'lowestBone':min(samples,key=lambda x:x['minimumY'])['lowestBone']};print(ident,name,rows[name],flush=True)
 report[ident]={'bones':len(g['bones']),'cuboids':sum(len(b.get('cubes',[])) for b in g['bones']),'clips':rows}
 ims=[render(yaw=y,mode=m) for y,m in [(0,'lit'),(180,'lit'),(90,'lit'),(-90,'lit'),(45,'lit'),(45,'shape_gray'),(45,'silhouette')]];sheet(ims,['正面','背面','右侧','左侧','45度','灰模','剪影'],ident+' / 固定5.5px每模型单位 / 原创1.8m人和1m石块参照 / 软件预览',ident+'-views.png',cols=3)
 ims=[];names=[]
 for clip,t in [('intro',140),('ram',20),('whip',18),('whip',32),('oil',24),('bells',24),('transition',24),('slam',32),('drink',24),('death',100),('death',160)]:ims.append(render(clip,t));names.append(f'{clip} {t}t')
 sheet(ims,names,ident+' / 实际攻击与阶段源姿态 / 软件预览',ident+'-poses.png',cols=3)
(D/'software-sampling.json').write_text(json.dumps({'source':'actual exported geometry/animations; software only, native not run','samplesPerClip':81,'forms':report},ensure_ascii=False,indent=2)+'\n')
