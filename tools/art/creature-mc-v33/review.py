"""Actual face-UV previews, separate from native screenshots."""
from refine import *
import ast,sys,numpy as np
sys.modules['paint']=old
s=importlib.util.spec_from_file_location('prev',R/'tools/art/cod1-creatures-v32/review.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
g=v.g;title=v.title;raster=v.raster;references=v.references

def run(id,quick=False):
 d=D/id;tex=np.array(Image.open(old.path(id,'texture')).convert('RGB'));bt=np.array(Image.open(d/'before.png').convert('RGB'));anim=json.loads(old.path(id,'anim').read_text())['animations'];idle=next(a for a in anim if a.endswith('.idle'))
 q=g.geometry(id,clip=idle,tick=0);bq=g.geometry(id,clip=idle,tick=0,geo_path=d/'before.geo.json');p=np.concatenate([x for x,u,b in q+bq]);ref=references([float(p[:,0].min())-26,0,0]);frame=np.concatenate([x for x,u,b in q+bq+ref]);name=SPECS[id][0]
 def render(q,tex,yaw=45,mode='lit',size=(760,580),fr=frame):return raster(q,tex,yaw=yaw,size=size,mode=mode,frame_points=fr)
 a=title(render(bq+ref,bt),name+' / V32');b=title(render(q+ref,tex),name+' / V33 / 同相机同尺度');out=Image.new('RGB',(1520,616));out.paste(a);out.paste(b,(760,0));out.save(d/'comparison.png')
 for label,yaw in [('front',0),('45',45),('side',90),('back',180)]:title(render(q+ref,tex,yaw),name+' / '+label+' / 软件像素UV').save(d/(label+'.png'))
 for mode in ['unlit','gray','silhouette']:
  if mode=='silhouette':
   im=raster(q,np.zeros_like(tex),yaw=45,size=(760,580),mode='unlit',frame_points=frame);title(im,name+' / silhouette').save(d/'silhouette.png')
  else:title(render(q+ref,tex,mode=mode),name+' / '+mode).save(d/(mode+'.png'))
 if quick:return
 report={}
 for clip,a in anim.items():
  poses=[g.geometry(id,clip=clip,tick=float(t))for t in np.linspace(0,a.get('animation_length',1)*20,41)];points=np.concatenate([x for pose in poses for x,u,b in pose]);assert np.isfinite(points).all();report[clip]={'samples':41,'bounds':[points.min(0).tolist(),points.max(0).tolist()]}
  if clip.endswith(('.idle','.walk','.fly','.hurt','.death'))or clip==next(k for k in anim if not k.endswith(('.idle','.walk','.fly','.hurt','.death'))):
   fr=np.concatenate([points,frame]);frames=[title(render(pose+ref,tex,size=(640,480),fr=fr),name+' / '+clip.rsplit('.',1)[-1])for pose in poses[::2]];frames[0].save(d/(clip.rsplit('.',1)[-1]+'.webp'),save_all=True,append_images=frames[1:],duration=max(40,int(a.get('animation_length',1)*1000/len(frames))),loop=0,lossless=True)
 (d/'animation-check.json').write_text(json.dumps(report,indent=2));print('Reviewed',id,flush=True)
if __name__=='__main__':
 for id in [a for a in sys.argv[1:]if a!='--quick']or SPECS:run(id,'--quick'in sys.argv)
