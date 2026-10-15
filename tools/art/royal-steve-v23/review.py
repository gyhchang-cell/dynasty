"""Actual UV/PNG software previews, explicitly not game screenshots."""
from create import *
sys.path.insert(0,str(R/'tools/art/boss-forms'))
import texture_review as v
v.r.CATEGORY='boss_cuboid';v.D=D
NAMES=['东海龙王','龙帝']
def blank(qs,col=(151,156,157)):return [(p,{'uv':[0,0],'uv_size':[1,1],'_tex':np.array([[col]],dtype=np.uint8)},n) for p,uv,n in qs]
def run():
 for id,name in zip(IDS,NAMES):
  out=D/id;tx=np.array(Image.open(out/'texture.png'));qs=v.r.geometry(id);refs=v.references(np.array([-30,0,5]));frame=np.concatenate([p for p,_,_ in qs+refs])
  def draw(qs,title,yaw=35,mode='lit',tex=tx,size=(800,680),fr=None):return v.labelled(v.raster(qs,tex,yaw,elevation=4,size=size,mode=mode,frame_points=fr),name+' / '+title)
  for yaw,label in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
   for mode in ['lit','unlit']:draw(qs,label+' / '+mode,yaw,mode).save(out/f'{label}-{mode}.png')
   draw(blank(qs),'灰模 / '+label,yaw).save(out/f'gray-{label}.png')
  draw(blank(qs,(0,0,0)),'黑色剪影',0,'unlit').save(out/'silhouette.png')
  draw(qs+refs,'1.8米玩家与石砖、木材',35,fr=frame).save(out/'player-scale.png')
  for label,bones in [('face',['head','crown','beard']),('weapon',['weapon','right_arm']),('chest',['chest','left_arm'])]:draw([q for q in qs if q[2] in bones],label+' / 原色',12,'unlit',size=(600,520)).save(out/f'close-{label}.png')
  check=v.checker(id);draw(qs,'UV方向检查',35,'unlit',tex=check).save(out/'uv-direction.png')
  for clip,a in json.loads((A/'animations/boss_cuboid'/f'{id}.animation.json').read_text())['animations'].items():
   times=np.linspace(0,a['animation_length'],24);poses=[v.r.geometry(id,clip,float(t)*20) for t in times];fp=np.concatenate([p for q in poses for p,_,_ in q])
   frames=[draw(q,f'{clip} {t*20:.1f} tick',30,'lit',size=(500,460),fr=fp) for q,t in zip(poses,times)]
   frames[0].save(out/(clip+'.webp'),save_all=True,append_images=frames[1:],duration=max(20,round(a['animation_length']*1000/23)),loop=0,lossless=True)
  print(id,'review done',flush=True)
if __name__=='__main__':run()
