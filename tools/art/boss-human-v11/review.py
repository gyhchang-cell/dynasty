"""Original atlas per-face previews, consistent scale and honest software labels."""
from create import *
import texture_review as v
v.r.CATEGORY='boss_cuboid';v.D=D
def quads(id,clip=None,tick=0,before=False):
 kw={'geo_path':D/'before'/f'{id}.geo.json','animation_path':D/'before'/f'{id}.animation.json'} if before else {}
 q=v.r.geometry(id,clip or 'idle',tick,**kw)
 scale=1
 return [(p*scale,uv,n) for p,uv,n in q]
def run(full=True):
 for id in IDS:
  path=D/id;tex=np.array(Image.open(path/'texture.png').convert('RGB'));q=quads(id);bq=quads(id,before=True);bt=np.array(Image.open(D/'before'/f'{id}.png').convert('RGB'))
  pts=np.concatenate([p for p,_,_ in q]);bp=np.concatenate([p for p,_,_ in bq]);frame=np.concatenate([pts,bp]);offset=np.array([-70,0,-25]);ref=v.references(offset);scene=q+ref
  for angle,name in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
   for mode in ['unlit','lit']:v.labelled(v.raster(q,tex,angle,mode=mode),NAMES[id]+' / '+name+' / '+mode).save(path/f'{name}-{mode}.png')
   if angle in [0,45,90]:
    out=Image.new('RGB',(1700,720))
    for j,(qs,tx,title) in enumerate([(bq,bt,'V10 现有模型'),(q,tex,'V11 Boss增强')]):out.paste(v.labelled(v.raster(qs,tx,angle,size=(850,640),frame_points=frame),NAMES[id]+' / '+title+' / 同机位同尺度'),(j*850,0))
    out.save(path/f'compare-{name}.png')
  for mode,col in [('gray-model',(143,148,150)),('silhouette',(0,0,0))]:
   blank=np.full_like(tex,col);v.labelled(v.raster(scene,blank,45,mode='lit' if mode=='gray-model' else 'unlit'),NAMES[id]+' / '+mode+' / 1.8m玩家').save(path/f'{mode}.png')
  check=v.checker(id);v.labelled(v.raster(q,check,45),NAMES[id]+' / UV编号与方向').save(path/'uv-direction.png')
  v.labelled(v.raster(scene,tex,25,mode='lit'),NAMES[id]+' / 1.8m玩家与1m石砖参照').save(path/'scene.png')
  if not full:continue
  for mode in ['gray','dim']:v.labelled(v.raster(q,tex,mode=mode),NAMES[id]+' / '+mode).save(path/f'{mode}.png')
  for distance in [8,16]:v.labelled(v.raster(scene,tex,mode='lit',distance=distance),NAMES[id]+f' / 正常视高 / {distance}m').save(path/f'distance-{distance}m.png')
  for part,names in [('face',['head','hair','crown','beard','tassel_-6','tassel_6']),('torso',['chest','waist','pelvis']),('hand',['right_forearm','right_hand','weapon'])]:
   subset=[a for a in q if a[2] in names]
   if subset:v.labelled(v.raster(subset,tex,20,size=(720,540)),NAMES[id]+' / '+part+' / 原色').save(path/f'close-{part}.png')
  animations=json.loads((A/f'animations/boss_cuboid/{id}.animation.json').read_text())['animations']
  for clip,a in animations.items():
   actionref=v.references(np.array([-25,0,0]))[12:];times=np.linspace(0,a['animation_length']*20,24);poses=[quads(id,clip,float(t)) for t in times];fp=np.concatenate([p for qs in poses for p,_,_ in qs]+[p for p,_,_ in actionref]);frames=[]
   for t,pq in zip(times,poses):frames.append(v.labelled(v.raster(pq+actionref,tex,30,size=(560,420),mode='lit',frame_points=fp),NAMES[id]+f' / {clip} / {t:.2f} tick'))
   frames[0].save(path/f'{clip}.webp',save_all=True,append_images=frames[1:],duration=max(15,round(a['animation_length']*1000/23)),loop=0,lossless=True)
   sheet=Image.new('RGB',(1680,1000))
   for j,i in enumerate([0,5,9,13,18,23]):sheet.paste(frames[i],(j%3*560,j//3*500))
   sheet.save(path/f'{clip}-phases.png')
  print('review',id,flush=True)
 overview=Image.new('RGB',(1500,780))
 for j,id in enumerate(IDS):
  tex=np.array(Image.open(D/id/'texture.png'));q=quads(id)+v.references(np.array([-25,0,0]))[12:]
  overview.paste(v.labelled(v.raster(q,tex,25,size=(500,700),frame_points=np.array([[-37,0,-10],[37,55,26]]),mode='lit'),NAMES[id]+' / 共用世界尺度'),(j*500,0))
 overview.save(D/'overview.png')
if __name__=='__main__':run('--quick' not in sys.argv)
