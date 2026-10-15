"""Same-camera original-pixel reviews; no glow, particles or colour multiplier."""
from export import *
sys.path.insert(0,str(R/'tools/art/boss-forms'))
import texture_review as v
v.r.CATEGORY='boss_cuboid'
def run():
 textures=[np.array(Image.open(D/(n+'.png'))) for n in ['before','after']]
 paths=[D/'before'/TARGETS[0].name,TARGETS[0]]
 poses=[v.r.geometry(ID,'idle',0,geo_path=p,animation_path=TARGETS[1]) for p in paths]
 def draw(q,t,yaw=0,mode='unlit',fr=None,size=(840,780),title=''):
  return v.labelled(v.raster(q,t,yaw,elevation=4,size=size,mode=mode,frame_points=fr),title)
 for name,bones,yaw,mode in [('front',None,0,'unlit'),('45',None,45,'lit'),('head',['head','crest'],10,'unlit'),('head45',['head','crest'],45,'lit'),('helmet-side',['head','crest'],90,'lit'),('head-front',['head','crest'],0,'unlit'),('head-gray',['head','crest'],45,'gray')]:
  qs=[[x for x in q if bones is None or x[2] in bones] for q in poses];fr=np.concatenate([p for q in qs for p,_,_ in q]);board=Image.new('RGB',(1680,860))
  for i,(q,t) in enumerate(zip(qs,textures)):
   im=draw(q,t,yaw,mode,fr,title=('修改前' if i==0 else '修改后')+' / '+name)
   board.paste(im,(i*840,0))
   if i==1:im.save(D/(name+'-close.png'))
  board.save(D/(name+'-comparison.png'))
 q=poses[1];t=textures[1];scene=q+v.references(np.array([-30,0,5]));fr=np.concatenate([p for p,_,_ in scene])
 draw(scene,t,25,'lit',fr,title='原玩家比例 / 仅头盔浅层起伏').save(D/'player-scale.png')
 for yaw,name in [(90,'side'),(180,'back')]:draw(q,t,yaw,'lit',np.concatenate([p for p,_,_ in q]),title=name).save(D/(name+'.png'))
 board=Image.new('RGB',(1080,590),(232,233,228));d=ImageDraw.Draw(board)
 for i,n in enumerate(['before','after']):
  board.paste(Image.open(D/(n+'-4x.png')),(i*540+14,50));d.text((i*540+14,10),n+' / 128×128 · nearest ×4',font=v.font(20),fill=(32,38,45))
 board.save(D/'texture-comparison.png')
 for clip,a in json.loads(TARGETS[1].read_text())['animations'].items():
  ts=np.linspace(0,a['animation_length']*20,24);qs=[v.r.geometry(ID,clip,float(t)) for t in ts];fr=np.concatenate([p for q in qs for p,_,_ in q]);frames=[]
  for tick,q in zip(ts,qs):frames.append(draw(q,t,30,'lit',fr,(560,500),f'{clip} / {tick:.2f} tick / 原时间轴'))
  frames[0].save(D/(clip+'.webp'),save_all=True,append_images=frames[1:],duration=max(15,round(a['animation_length']*1000/23)),loop=0,lossless=True)
 print('Before/after, head/front/45/side, exact PNG, gray relief and all six clips rendered.')
if __name__=='__main__':run()
