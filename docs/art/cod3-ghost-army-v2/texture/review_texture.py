"""Actual final atlas sampled on frozen source and animation; software only."""
from pathlib import Path
import sys,itertools,json
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[3];A=R/'src/main/resources/assets/dynasty';sys.path.insert(0,str(R/'tools/art/boss-forms'));import texture_review as v
v.r.CATEGORY='scenic';N='ghost_army_soldier';tex=np.array(Image.open(D/'texture.png').convert('RGB'))
def pose(t=0,lod=''):return v.r.geometry(N,clip='animation.scenic.idle',tick=t,geo_path=A/f'geo/scenic/{N}{lod}.geo.json')
def draw(q,texture,yaw,title,size=(650,750),frame_points=None):
 light=np.array([-.75,.85,.25]);light/=np.linalg.norm(light);cache={};lit=[]
 for points,uv,bn in q:
  normal=np.cross(points[1]-points[0],points[2]-points[0]);norm=np.linalg.norm(normal);shade=round(.6+.4*abs(float(normal@light)/norm),4) if norm>1e-9 else .6
  atlas=uv.get('_tex',texture);key=(id(atlas),shade)
  if key not in cache:cache[key]=np.clip(atlas*shade,0,255).astype(np.uint8)
  lit.append((points,dict(uv,_tex=cache[key]),bn))
 return v.labelled(v.raster(lit,texture,yaw=yaw,elevation=5,size=size,mode='unlit',frame_points=frame_points),title,'软件实际UV贴图预览 · 非游戏截图 · 无发光/粒子 · 原图256px')
if __name__=='__main__':
 allpoints=np.concatenate([p for t in range(0,81,4) for p,_,_ in pose(t)]);frame=np.array(list(itertools.product(*zip(allpoints.min(0)-2,allpoints.max(0)+2))))
 for yaw,n in [(180,'front'),(135,'45'),(90,'right'),(-90,'left'),(0,'back')]:
  draw(pose(),tex,yaw,'巡猎陶兵 / '+n,frame_points=frame).save(D/f'{n}.png')
  draw(pose(),np.full_like(tex,153),yaw,'灰模 / '+n,frame_points=frame).save(D/f'gray-{n}.png')
  draw(pose(),np.zeros_like(tex),yaw,'黑剪影 / '+n,frame_points=frame).save(D/f'silhouette-{n}.png')
 for name,bns in [('head-close',{'head','neck'}),('grip-close',{'right_hand','spear','right_forearm'})]:
  q=[qq for qq in pose() if qq[2] in bns]
  if name=='grip-close':q=[qq for qq in q if 18<qq[0][:,1].mean()<27]
  draw(q,tex,135,name,(700,620)).save(D/f'{name}.png')
 for lod in ('','_medium','_far'):
  draw(pose(0,lod),tex,135,'实际贴图 LOD '+(lod or 'full'),frame_points=frame).save(D/f'lod{lod or "_full"}.png')
  frames=[draw(pose(t,lod),tex,135,f'{lod or "full"} / {t} tick',(400,440),frame) for t in range(0,80,5)]
  frames[0].save(D/f'walk{lod}.webp',save_all=True,append_images=frames[1:],duration=250,loop=0,lossless=True)
  sheet=Image.new('RGB',(1600,2080))
  for i,im in enumerate(frames):sheet.paste(im,(i%4*400,i//4*520))
  sheet.save(D/f'walk-contact{lod}.png')
 sheet=Image.new('RGB',(1950,1660),(232,233,228))
 for i,n in enumerate(['front','45','right','back','head-close','grip-close']):
  im=Image.open(D/f'{n}.png');im.thumbnail((650,830));sheet.paste(im,(i%3*650,i//3*830))
 sheet.save(D/'overview.png');print('Actual PNG reviews written; software only',flush=True)
