"""Matched-scale proportion and silhouette review, using actual geometry and PNG."""
from proportions import *
import sys

def review():
 out=D/ID;out.mkdir(exist_ok=True);tex=np.array(Image.open(A/'textures/entity/boss_forms'/(ID+'.png')))
 oldq=v.r.geometry(ID,clip='idle',tick=0,geo_path=B/(ID+'.geo.json'),animation_path=B/(ID+'.animation.json'));newq=v.r.geometry(ID,clip='idle',tick=0)
 refs=v.references(np.array([-80,0,0]));frame=np.concatenate([x[0] for q in [oldq,newq,refs] for x in q])
 for yaw,name in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
  angle=np.radians(yaw);refs=v.references(np.array([-80*np.cos(angle),0,-80*np.sin(angle)]));frame=np.concatenate([x[0] for q in [oldq,newq,refs] for x in q])
  ims=[]
  for q,label in [(oldq,'调整前 v7'),(newq,'调整后 v8')]:
   im=v.labelled(v.raster(q+refs,tex,size=(1000,700),yaw=yaw,mode='lit',frame_points=frame),f'{label} / {name} / 同相机同尺度 · 玩家1.8m');ims.append(im)
  im=Image.new('RGB',(2000,780));im.paste(ims[0],(0,0));im.paste(ims[1],(1000,0));im.save(D/('comparison-'+name+'.png'))
  for mode in ['unlit','lit','gray']:
   v.labelled(v.raster(newq,tex,yaw=yaw,size=(1000,740),frame_points=frame,mode=mode),'兵煞残甲 / '+name+' / '+mode).save(out/(name+'-'+mode+'.png'))
 # Identical crop of the existing support parts; full geometry still renders for correct occlusion.
 feetframe=np.concatenate([x[0] for q in [oldq,newq] for x in q if x[2].startswith('support_')])
 for yaw,label in [(0,'front'),(45,'45'),(90,'side')]:
  sheet=Image.new('RGB',(1600,680))
  for k,(q,version) in enumerate([(oldq,'v7'),(newq,'v8')]):
   im=v.labelled(v.raster(q,tex,yaw=yaw,size=(800,600),frame_points=feetframe,mode='lit'),f'腿脚连接 / {version} / {label} / 同尺度')
   sheet.paste(im,(800*k,0))
  sheet.save(D/f'feet-comparison-{label}.png')
 for q,label in [(oldq,'before'),(newq,'after')]:
  black=np.zeros_like(tex);v.labelled(v.raster(q,black,yaw=45,size=(1000,740),frame_points=frame,mode='unlit'),'纯黑剪影 / '+label).save(out/(label+'-silhouette.png'))
 refs=v.references(np.array([-60,0,-50]))
 for distance in [10,18,28]:v.labelled(v.raster(newq+refs,tex,mode='lit',distance=distance,size=(1200,800)),f'玩家视高 / {distance}m / 1.8m比例参照').save(out/f'distance-{distance}m.png')
 v.D=D;check=v.checker(ID)
 for yaw,label in [(45,'uv-direction'),(90,'uv-side')]:v.labelled(v.raster(newq,check,yaw=yaw,frame_points=frame),label+' / 检查纹理仅用于预览').save(out/(label+'.png'))
 if '--quick' not in sys.argv:
  from material_review import clips
  import material_review as mr
  mr.p.D=D;mr.v.D=D;clips(ID)
  for clip in ['walk','attack']:
   seconds=json.loads((B/(ID+'.animation.json')).read_text())['animations'][clip]['animation_length'];times=np.linspace(0,seconds*20,40)
   pairs=[(v.r.geometry(ID,clip=clip,tick=float(t),geo_path=B/(ID+'.geo.json'),animation_path=B/(ID+'.animation.json')),v.r.geometry(ID,clip=clip,tick=float(t))) for t in times]
   frame=np.concatenate([x[0] for pair in pairs for q in pair for x in q]);frames=[]
   for t,pair in zip(times,pairs):
    sheet=Image.new('RGB',(1440,620))
    for k,q in enumerate(pair):sheet.paste(v.labelled(v.raster(q,tex,size=(720,540),frame_points=frame,mode='lit'),f'{clip} / {t:.1f}tick / v{7+k} · 同机位'),(k*720,0))
    frames.append(sheet)
   frames[0].save(D/f'comparison-{clip}-full.webp',save_all=True,append_images=frames[1:],duration=round(seconds*1000/40),loop=0,lossless=True)
   print('Matched full motion',clip,flush=True)
 print('Proportion review ready',flush=True)
if __name__=='__main__':review()
