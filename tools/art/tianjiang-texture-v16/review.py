"""Same geometry/UV/pose/camera before-after reviews of real PNG samples."""
from export import *
import numpy as np,shutil
sys.path.insert(0,str(R/'tools/art/boss-forms'))
import texture_review as v
v.r.CATEGORY='boss_cuboid'
def run():
 before=np.array(Image.open(D/'before.png'));after=np.array(Image.open(D/'after.png'))
 q=v.r.geometry(ID,'idle',0);frame=np.concatenate([p for p,_,_ in q])
 def draw(qs,tex,title,yaw=0,mode='unlit',size=(920,850),fr=None):
  return v.labelled(v.raster(qs,tex,yaw,elevation=4,size=size,mode=mode,frame_points=fr),title)
 def pair(name,qs,title,yaw=0,mode='unlit'):
  fr=np.concatenate([p for p,_,_ in qs]);board=Image.new('RGB',(1840,930))
  for i,(tex,label) in enumerate([(before,'修改前'),(after,'修改后')]):board.paste(draw(qs,tex,label+' / '+title,yaw,mode,fr=fr),(i*920,0))
  board.save(D/(name+'.png'))
 texboard=Image.new('RGB',(1080,590),(232,233,228))
 for i,name in enumerate(['before','after']):
  ImageDraw=__import__('PIL.ImageDraw',fromlist=['ImageDraw']);d=ImageDraw.Draw(texboard)
  d.text((i*540+14,10),'修改前 / 128×128' if i==0 else '修改后 / 相同128×128与UV',font=v.font(20),fill=(37,42,43))
  texboard.paste(Image.open(D/(name+'-4x.png')),(i*540+14,50))
 texboard.save(D/'texture-comparison.png')
 pair('front-comparison',q,'正面 / PNG原色 / 相同形体')
 pair('45-comparison',q,'45° / 基础漫反射 / 相同形体',45,'lit')
 for yaw,name in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
  for mode in ['unlit','lit']:draw(q,after,name+' / '+mode,yaw,mode,fr=frame).save(D/f'{name}-{mode}.png')
 for name,bones,yaw in [('head',['head','crest'],10),('chest',['chest'],10),('weapon',['weapon','right_arm'],20),('shoulder',['left_arm'],15)]:
  qs=[z for z in q if z[2] in bones];pair(name+'-comparison',qs,name+' / 原色细节',yaw)
  draw(qs,after,name+' / 实际PNG原色',yaw).save(D/(name+'-close.png'))
 for mode in ['gray','dim']:draw(q,after,mode+' / 材质主次',45,mode,fr=frame).save(D/(mode+'.png'))
 scene=q+v.references(np.array([-30,0,5]));sf=np.concatenate([p for p,_,_ in scene])
 draw(scene,after,'玩家、石砖与木材参照',35,'lit',fr=sf).save(D/'player-scale.png')
 for distance in [8,16]:
  v.labelled(v.raster(scene,after,25,distance=distance,mode='lit',size=(1100,850)),f'正常视高 / {distance}m / 软件透视').save(D/f'distance-{distance}.png')
 uv=D/'uv';uv.mkdir(exist_ok=True)
 for f in ['texture.png','islands.json']:shutil.copy2(D/f,uv/f)
 v.D=D;check=v.checker('uv')
 for yaw,name in [(45,'uv-direction'),(90,'uv-side')]:draw(q,check,'仅预览：UV方向与编号',yaw,fr=frame).save(D/(name+'.png'))
 for clip in ['idle','walk','attack','cast','hurt','death']:
  a=json.loads(TARGETS[1].read_text())['animations'][clip];times=np.linspace(0,a['animation_length']*20,24)
  poses=[v.r.geometry(ID,clip,float(t)) for t in times];fr=np.concatenate([p for qs in poses for p,_,_ in qs]);frames=[]
  for t,qs in zip(times,poses):frames.append(draw(qs,after,f'{clip} / {t:.2f} tick',30,'lit',(560,500),fr))
  frames[0].save(D/f'{clip}.webp',save_all=True,append_images=frames[1:],duration=max(15,round(a['animation_length']*1000/23)),loop=0,lossless=True)
 print('Same-camera PNG comparisons, front/45/head/chest/weapon, UV direction and unchanged clips rendered.')
if __name__=='__main__':run()
