from pathlib import Path
import sys,json,itertools,math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools/art/boss-forms'));import texture_review as v
D=R/'docs/art/cod3-ghost-army-v2';A=R/'src/main/resources/assets/dynasty';N='ghost_army_soldier';v.r.CATEGORY='scenic'
def pose(t=0,lod=''):return v.r.geometry(N,clip='animation.scenic.idle',tick=t,geo_path=A/f'geo/scenic/{N}{lod}.geo.json')
def review():
 tex=np.array(Image.open(D/'temporary-material-atlas.png'));gray=np.full_like(tex,153);black=np.zeros_like(tex)
 allpoints=np.concatenate([p for t in range(0,81,2) for p,_,_ in pose(t)]);lo=allpoints.min(0)-2;hi=allpoints.max(0)+2;frame=np.array(list(itertools.product(*zip(lo,hi))))
 foot='软件灰模/临时材质分区 · 非最终贴图 · 非游戏截图 · scale=1 / 1格=16单位'
 def draw(q,texture,yaw,title,size=(800,850),frame_points=frame):
  # Distinct side/front illumination exposes volume; no AO, tint or emission.
  light=np.array([-.75,.85,.25]);light/=np.linalg.norm(light);cache={};lit=[]
  for points,uv,bn in q:
   normal=np.cross(points[1]-points[0],points[2]-points[0]);norm=np.linalg.norm(normal)
   shade=round(.6+.4*abs(float(normal@light)/norm),4) if norm>1e-9 else .6
   atlas=uv.get('_tex',texture);key=(id(atlas),shade)
   if key not in cache:cache[key]=np.clip(atlas*shade,0,255).astype(np.uint8)
   lit.append((points,dict(uv,_tex=cache[key]),bn))
  return v.labelled(v.raster(lit,texture,yaw=yaw,elevation=5,size=size,mode='unlit',frame_points=frame_points),title,foot)
 for yaw,n in [(180,'front'),(135,'45'),(90,'right'),(-90,'left'),(0,'back')]:
  q=pose();draw(q,gray,yaw,'巡猎兵俑 / 灰模 '+n).save(D/f'gray-{n}.png');draw(q,black,yaw,'巡猎兵俑 / 剪影 '+n).save(D/f'silhouette-{n}.png');draw(q,tex,yaw,'巡猎兵俑 / 临时材质 '+n).save(D/f'{n}.png')
 refs=v.references(np.array([42,0,-18]));refs=[(p+(np.array([0,0,18]) if i>=12 else 0),uv,b) for i,(p,uv,b) in enumerate(refs)];draw(pose()+refs,tex,180,'同地面：兵俑约2.6m / 玩家1.8m / 方块1m',(1300,900),np.concatenate([p for p,_,_ in pose()+refs])).save(D/'world-scale.png')
 for lod in ('','_medium','_far'):draw(pose(0,lod),gray,135,'巡猎兵俑 / '+(lod or 'full')).save(D/f'lod{lod or "_full"}.png')
 for name,bns in [('head-close',{'head','neck'}),('grip-close',{'right_hand','spear','right_forearm'})]:
  q=[qq for qq in pose() if qq[2] in bns]
  if name=='grip-close':q=[qq for qq in q if qq[0][:,1].mean()>18 and qq[0][:,1].mean()<27]
  draw(q,tex,135,name,(900,700),np.concatenate([qq[0] for qq in q])).save(D/f'{name}.png')
 checker=np.array(Image.open(D/'uv-direction-check.png'));draw(pose(),checker,135,'方向/编号检查（非成品）').save(D/'uv-on-model.png')
 for lod in ('','_medium','_far'):
  frames=[draw(pose(t,lod),gray,135,f'{lod or "full"} / {t} tick',(520,560)) for t in range(0,80,2)]
  frames[0].save(D/f'walk{lod}.webp',save_all=True,append_images=frames[1:],duration=100,loop=0,lossless=True)
 cycle=Image.new('RGB',(2000,1600),(232,233,228))
 for i,t in enumerate(range(0,80,5)):
  im=draw(pose(t),gray,135,f'{t} tick',(500,320));cycle.paste(im,(i%4*500,i//4*400))
 cycle.save(D/'full-cycle-check.png')
 # Marching speed proof in world space; same phase and geometry, translated only for review.
 ground=[]
 for tick in range(0,81,2):
  q=pose(tick);moved=[(p+np.array([0,0,tick*.16]),uv,b) for p,uv,b in q];ground.append(moved)
 frame2=np.concatenate([p for q in ground for p,_,_ in q]);frames=[draw(q,gray,90,f'世界匀速0.2m/s / {i*2} tick',(680,600),frame2) for i,q in enumerate(ground[:-1])]
 frames[0].save(D/'world-travel.webp',save_all=True,append_images=frames[1:],duration=100,loop=0,lossless=True)
 sheet=Image.new('RGB',(1600,1860))
 for i,n in enumerate(['gray-front','gray-45','gray-right','gray-back']):sheet.paste(Image.open(D/f'{n}.png').resize((800,930)),(i%2*800,i//2*930))
 sheet.save(D/'overview.png');print('Software review exported',flush=True)
if __name__=='__main__':review()
