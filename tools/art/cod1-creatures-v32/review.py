"""Actual face-UV software previews; no game screenshot claims."""
from pathlib import Path
import ast,json,math,importlib.util,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from paint import SPECS,path,topology,R
D=R/'docs/art/cod1-creatures-v32'; B=R/'build/cod1-creatures-v32/baseline'
s=importlib.util.spec_from_file_location('geom',R/'tools/art/secondary-cuboid/review_models.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);g.CATEGORY='blueprint/elite';r=g
source=(R/'tools/art/boss-forms/texture_review.py').read_text()
for node in ast.parse(source).body:
 if isinstance(node,ast.FunctionDef) and node.name in ('raster','cuboid','references'):exec(ast.get_source_segment(source,node),globals())
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',18)
def title(im,label):
 out=Image.new('RGB',(im.width,im.height+36),'#e8e9e4');out.paste(im,(0,36));ImageDraw.Draw(out).text((12,6),label,font=font,fill='#26383a');return out
def run(id,quick=False):
 d=D/id;geo=path(id,'geo');old=D/id/'before.geo.json';tex=np.array(Image.open(path(id,'texture')).convert('RGB'));bt=np.array(Image.open(d/'before-texture.png').convert('RGB'))
 anim=json.loads(path(id,'anim').read_text())['animations'];idle=next((a for a in anim if a.endswith('.idle')),next(iter(anim)));q=g.geometry(id,clip=idle,tick=0);bq=g.geometry(id,clip=idle,tick=0,geo_path=old)
 pts=np.concatenate([v for v,u,b in q]);offset=np.array([float(pts[:,0].min())-26,0,0]);ref=references(offset);scene=q+ref;frame=np.concatenate([v for v,u,b in scene]);name=SPECS[id][0]
 def render(q,texture=tex,yaw=45,mode='lit',size=(760,580)):
  return raster(q,texture,yaw=yaw,size=size,mode=mode,frame_points=frame)
 imgs=[title(render(bq+ref,bt),name+' / 原贴图'),title(render(scene),name+' / 新贴图，同尺度')]
 comparison=Image.new('RGB',(1520,616));comparison.paste(imgs[0]);comparison.paste(imgs[1],(760,0));comparison.save(d/'comparison.png')
 if quick:return
 for label,yaw in [('front',0),('side',90),('back',180),('45',45)]:
  title(render(scene,yaw=yaw),name+' / '+label+' / 软件基础光照').save(d/(label+'.png'))
 for mode in ('unlit','gray','dim'):title(render(scene,mode=mode),name+' / '+mode+' / 软件预览').save(d/(mode+'.png'))
 overlay=Image.open(d/'texture.png').convert('RGB');draw=ImageDraw.Draw(overlay)
 for i,v in enumerate(json.loads((d/'islands.json').read_text())):
  x,y,w,h=v['rect'];draw.rectangle((x,y,x+w-1,y+h-1),outline=(220,64,160))
 overlay.resize((overlay.width*3,overlay.height*3),Image.Resampling.NEAREST).save(d/'uv-overlay.png')
 samples={};clips=[a for a in anim if a.endswith(('.idle','.walk','.death'))];attack=next((a for a in anim if not a.endswith(('.idle','.walk','.hurt','.death'))),None)
 if attack:clips.append(attack)
 for clip in anim:
  length=anim[clip].get('animation_length',1);allpts=[]
  for tick in np.linspace(0,length*20,41):
   pq=g.geometry(id,clip=clip,tick=float(tick));p=np.concatenate([v for v,u,b in pq]);assert np.isfinite(p).all();allpts.append(p)
  p=np.concatenate(allpts);samples[clip]={'samples':41,'bounds':[p.min(0).tolist(),p.max(0).tolist()]}
 for clip in clips:
  length=anim[clip].get('animation_length',1);frames=[]
  # Frame all sampled poses together so camera never zooms during an action.
  poses=[g.geometry(id,clip=clip,tick=float(t)) for t in np.linspace(0,length*20,25)];f=np.concatenate([v for pose in poses for v,u,b in pose]+[v for v,u,b in ref]);f=np.concatenate([f,frame])
  for pose in poses:frames.append(title(raster(pose+ref,tex,yaw=45,size=(640,480),mode='lit',frame_points=f),name+' / '+clip.rsplit('.',1)[-1]+' / 原时间轴'))
  frames[0].save(d/(clip.rsplit('.',1)[-1]+'.webp'),save_all=True,append_images=frames[1:],duration=max(40,round(length*1000/25)),loop=0,lossless=True)
 (d/'animation-sampling.json').write_text(json.dumps(samples,indent=2)+'\n')
 print('reviewed',id,flush=True)
if __name__=='__main__':
 for id in [x for x in sys.argv[1:] if x!='--quick'] or SPECS:run(id,'--quick'in sys.argv)
