"""Actual per-face PNG review, same native scale; software evidence explicitly labelled."""
from refine import *
import texture_review as v
v.r.CATEGORY='boss_cuboid';v.D=D
NAMES={'nine_heaven_general':'九霄天将 · 雷鼓刑钟','dragon_king':'东海龙王','dragon_emperor':'龙帝'}
def quads(id,clip=None,tick=0,before=False):
 kw={'geo_path':D/'before'/f'{id}.geo.json','animation_path':D/'before'/f'{id}.animation.json'} if before else {}
 q=v.r.geometry(id,clip,tick,**kw)
 scale=1.4 if id=='dragon_emperor' else 1.35 if id=='dragon_king' and not before else 1
 q=[(p*scale,uv,bn) for p,uv,bn in q]
 return q

def run(full=True):
 for id in IDS:
  path=D/id;tex=np.array(Image.open(path/'texture.png').convert('RGB'));q=quads(id);bq=quads(id,before=True);bt=np.array(Image.open(D/'before'/f'{id}.png').convert('RGB'))
  pts=np.concatenate([p for p,_,_ in q]);bp=np.concatenate([p for p,_,_ in bq]);frame=np.concatenate([pts,bp]);right=np.array([2**-.5,0,2**-.5]);ref=v.references(right*(min(pts@right)-48));scene=q+ref;sp=np.concatenate([p for p,_,_ in scene])
  for angle,name in [(0,'front'),(45,'45'),(90,'right'),(-90,'left'),(180,'back')]:
   for mode in ['unlit','lit']:
    v.labelled(v.raster(q,tex,angle,mode=mode),NAMES[id]+' / '+name+' / '+mode).save(path/f'{name}-{mode}.png')
   if angle in [0,45,90]:
    before=v.labelled(v.raster(bq,bt,angle,size=(850,640),frame_points=frame),NAMES[id]+' / 修改前 · 相同取景与实际缩放')
    after=v.labelled(v.raster(q,tex,angle,size=(850,640),frame_points=frame),NAMES[id]+' / 修改后 · 真实 PNG')
    out=Image.new('RGB',(1700,720));out.paste(before,(0,0));out.paste(after,(850,0));out.save(path/f'compare-{name}.png')
  for mode,col in [('gray-model',(143,148,150)),('silhouette',(0,0,0))]:
   blank=np.empty_like(tex);blank[:]=col
   v.labelled(v.raster(scene,blank,45,size=(1100,800),mode='lit' if mode=='gray-model' else 'unlit',frame_points=sp),NAMES[id]+' / '+mode+' / 同场景1.8m玩家').save(path/f'{mode}.png')
  check=v.checker(id)
  for angle,name in [(45,'uv-direction'),(90,'uv-side')]:v.labelled(v.raster(q,check,angle),NAMES[id]+' / 编号、U/V方向检查').save(path/f'{name}.png')
  v.labelled(v.raster(scene,tex,45,size=(1100,800),mode='lit'),NAMES[id]+' / 玩家、石砖、木材比例').save(path/'scene.png')
  if not full:continue
  for mode in ['gray','dim']:v.labelled(v.raster(q,tex,mode=mode),NAMES[id]+' / '+mode).save(path/f'{mode}.png')
  for distance in [10,18,28]:v.labelled(v.raster(scene,tex,mode='lit',size=(1100,760),distance=distance),NAMES[id]+f' / 正常视高 / {distance}m').save(path/f'distance-{distance}m.png')
  # Fixed framing for each COMPLETE animation, not one 0-tick pose.
  animations=json.loads((A/f'animations/boss_cuboid/{id}.animation.json').read_text())['animations']
  for clip,a in animations.items():
   times=np.linspace(0,a['animation_length']*20,32);poses=[quads(id,clip,float(t)) for t in times];fp=np.concatenate([p for qs in poses for p,_,_ in qs]+[p for p,_,_ in ref]);frames=[]
   for i,(t,pq) in enumerate(zip(times,poses)):
    im=v.labelled(v.raster(pq+ref,tex,35,size=(640,480),mode='lit',frame_points=fp),NAMES[id]+f' / {clip} / {t:.2f} tick');frames.append(im)
   frames[0].save(path/f'{clip}.webp',save_all=True,append_images=frames[1:],duration=max(15,round(a['animation_length']*1000/31)),loop=0,lossless=True)
   sheet=Image.new('RGB',(640*3,560*2))
   for j,i in enumerate([0,6,12,18,25,31]):sheet.paste(frames[i],(j%3*640,j//3*560))
   sheet.save(path/f'{clip}-phases.png')
  print('review',id,flush=True)
if __name__=='__main__':run('--quick' not in sys.argv)
