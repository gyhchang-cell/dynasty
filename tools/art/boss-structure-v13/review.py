"""Depth-buffer rendering of the actual candidate JSON. All panels are software views."""
from create import *
import sys,importlib.util
import numpy as np
from PIL import ImageDraw,ImageFont
sys.path.insert(0,str(R/'tools/art/boss-forms'))
import texture_review as v
v.r.CATEGORY='boss_cuboid'
FONT='/System/Library/Fonts/STHeiti Medium.ttc'
def font(n):return ImageFont.truetype(FONT,n)
MODEL_FRAME=np.array([[x,y,z] for x in [-55,55] for y in [0,75] for z in [-38,42]])
SCENE_FRAME=np.array([[x,y,z] for x in [-66,55] for y in [0,75] for z in [-38,42]])
GRAY=np.full((16,16,3),155,dtype=np.uint8)
PROPS={'weapon','seal','crown','command_mantle','royal_fins','imperial_arch'}
def quads(id,clip=None,tick=0):
 p=D/'candidates'/id
 return v.r.geometry(id,clip,tick,geo_path=p/(id+'.geo.json'),animation_path=p/(id+'.animation.json'))
def refs():
 ref=v.references(np.array([-50,0,-14]));return ref[:6]+ref[12:]
def panel(q,yaw,title,black=False,scene=False,size=(900,760)):
 ref=refs()
 tx=np.zeros_like(GRAY) if black else GRAY
 # Review geometry with a uniform material, irrespective of original atlas dimensions.
 greyq=[(p,{'uv':[2,2],'uv_size':[4,4]},n) for p,uv,n in q]
 im=v.raster(greyq+(ref if scene else []),tx,yaw,elevation=4,size=size,mode='unlit' if black else 'lit',frame_points=SCENE_FRAME if scene else MODEL_FRAME)
 return v.labelled(im,title,'离线灰模 · 1单位=1/16m · 同尺度 · 无粒子/发光 · 非游戏截图')
def run():
 global MODEL_FRAME,SCENE_FRAME
 # Shared framing from actual vertices, not a hypothetical oversized bounding box.
 MODEL_FRAME=np.concatenate([p for id in IDS for p,_,_ in quads(id)])
 SCENE_FRAME=np.concatenate([MODEL_FRAME]+[p for p,_,_ in refs()])
 board=Image.new('RGB',(2700,1740),(232,233,228));d=ImageDraw.Draw(board)
 d.text((28,15),'V13 主体结构候选 / 上排45°灰模与玩家，下排正面黑色剪影',font=font(30),fill=(35,40,42))
 before=D/'before';before.mkdir(exist_ok=True)
 source=Path('/Users/a15356015027/Desktop/dynasty/src/main/resources/assets/dynasty')
 for j,(id,name) in enumerate(zip(IDS,NAMES)):
  out=D/id;out.mkdir(exist_ok=True);q=quads(id);core=[x for x in q if x[2] not in PROPS]
  for yaw,angle in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
   panel(q,yaw,name+' / '+angle+' / 灰模').save(out/(angle+'.png'))
   panel(q,yaw,name+' / '+angle+' / 黑色剪影',black=True).save(out/(angle+'-silhouette.png'))
  panel(q,45,name+' / 1.8m玩家、1m石砖 / 共同世界尺度',scene=True).save(out/'player-scale.png')
  panel(core,45,name+' / 隐藏武器、冠与独立背饰 / 主体检查').save(out/'body-only.png')
  panel(core,0,name+' / 主体黑色剪影',black=True).save(out/'body-only-silhouette.png')
  for ext,rel in [('geo.json','geo'),('animation.json','animations')]:
   p=before/(id+'.'+ext)
   if not p.exists():p.write_bytes((source/rel/'boss_cuboid'/(id+'.'+ext)).read_bytes())
  bq=v.r.geometry(id,'idle',0,geo_path=before/(id+'.geo.json'),animation_path=before/(id+'.animation.json'))
  for angle,yaw in [('front',0),('45',45),('side',90)]:
   compare=Image.new('RGB',(1800,840),(232,233,228))
   compare.paste(panel(bq,yaw,name+' / 当前仓库资源灰模'),(0,0));compare.paste(panel(q,yaw,name+' / V13结构候选'),(900,0))
   compare.save(out/('compare-'+angle+'.png'))
  board.paste(Image.open(out/'player-scale.png'),(900*j,70));board.paste(Image.open(out/'front-silhouette.png'),(900*j,910))
  for clip in ([] if '--quick' in sys.argv else ['idle','guard']):
   frames=[];length=2 if clip=='idle' else 1
   for t in np.linspace(0,length*20,21):frames.append(panel(quads(id,clip,float(t)),45,name+f' / 结构运动样片 {clip} / {t:.1f} tick',size=(650,550)))
   frames[0].save(out/(clip+'.webp'),save_all=True,append_images=frames[1:],duration=round(length*1000/20),loop=0,lossless=True)
   sheet=Image.new('RGB',(1950,1260),(232,233,228))
   for k,i in enumerate([0,4,8,12,16,20]):sheet.paste(frames[i],(k%3*650,k//3*630))
   sheet.save(out/(clip+'-phases.png'))
  points=np.concatenate([p for p,_,_ in q]);feet=np.concatenate([p for p,_,n in q if n.endswith('_foot')])
  report={'height_m':round(float(points[:,1].max()-points[:,1].min())/16,3),'width_m_with_weapon':round(float(np.ptp(points[:,0]))/16,3),'depth_m':round(float(np.ptp(points[:,2]))/16,3),'foot_bottom_m':round(float(feet[:,1].min())/16,6),'foot_top_m':round(float(feet[:,1].max())/16,3)}
  (out/'bounds.json').write_text(json.dumps(report,indent=2)+'\n')
  print(id,report,flush=True)
 board.save(D/'overview.png')
 stripped=Image.new('RGB',(2700,1680),(232,233,228))
 for j,id in enumerate(IDS):
  stripped.paste(Image.open(D/id/'body-only.png'),(900*j,0))
  stripped.paste(Image.open(D/id/'body-only-silhouette.png'),(900*j,840))
 stripped.save(D/'body-only-overview.png')
if __name__=='__main__':run()
