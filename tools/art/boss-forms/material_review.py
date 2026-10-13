"""Actual PNG detail comparisons and complete, fixed-camera clip playback."""
import json,sys
import numpy as np
from PIL import Image,ImageDraw
from materials import p
v=p.v;v.D=p.D

def details(id):
 out=p.D/id;tex=np.array(Image.open(out/'texture.png'));old=np.array(Image.open(p.D/'before'/(id+'.png')))
 pre='' if id=='rebel_general' else 'animation.'+id+'.';q=v.r.geometry(id,clip=pre+'idle',tick=0)
 def bone(n):return [x for x in q if x[2]==n]
 if id=='rebel_general':regions={'face':bone('broken_helm'),'weapon':bone('war_glaive'),'armor':bone('breach_arm')[:18]}
 else:regions={'face':bone('bound_head')[-24:],'weapon':bone('blade_mount'),'yoke':bone('yoke')[:18]}
 for name,parts in regions.items():
  frame=np.concatenate([x[0] for x in parts])
  for mode in ['unlit','lit','gray']:
   for angle,label in [(0,'front'),(35,'45')]:
    ims=[v.labelled(v.raster(q,t,size=(720,560),yaw=angle,frame_points=frame,mode=mode),f'{name} / {version} / {mode} · 相同原动作') for version,t in [('BEFORE',old),('AFTER',tex)]]
    sheet=Image.new('RGB',(1440,640));sheet.paste(ims[0],(0,0));sheet.paste(ims[1],(720,0));sheet.save(out/f'detail-{name}-{label}-{mode}.png')
 # Texture raw size and enlarged version stay available as files, not downscaled collage only.
 v.labelled(v.raster(q,tex,mode='dim'),id+' / dim · 软件弱光').save(out/'dim.png')

def clips(id):
 out=p.D/id;tex=np.array(Image.open(out/'texture.png'));pre='' if id=='rebel_general' else 'animation.'+id+'.'
 anim=json.loads((p.A/'animations/boss_forms'/(id+'.animation.json')).read_text())['animations'];review={}
 old=json.loads((p.D/'before'/(id+'.animation.json')).read_text())['animations']
 for name,a in anim.items():
  short=name.split('.')[-1];times=np.linspace(0,a['animation_length']*20,40)
  poses=[v.r.geometry(id,clip=name,tick=float(t)) for t in times]
  frame=np.concatenate([x[0] for q in poses for x in q]);frames=[]
  for i,(t,q) in enumerate(zip(times,poses)):
   im=v.labelled(v.raster(q,tex,size=(720,540),frame_points=frame,mode='lit'),id+f' / {short} {t:.1f}t');frames.append(im)
  frames[0].save(out/(short+'-full.webp'),save_all=True,append_images=frames[1:],duration=round(a['animation_length']*1000/40),loop=0,lossless=True)
  # Every generated frame is visible in a filmstrip, for review of complete motion.
  sheet=Image.new('RGB',(1800,2480),(232,233,228))
  for i,im in enumerate(frames):sheet.paste(im.resize((360,310),Image.Resampling.NEAREST),(i%5*360,i//5*310))
  sheet.save(out/(short+'-filmstrip.png'))
  # Five explicit phases (including the existing server contact) with fixed scale.
  contact={'attack':12,'roar':24,'spin':26,'throw':20}.get(short,a['animation_length']*10)
  sample=[0,contact*.6,contact*.85,contact,a['animation_length']*18]
  sheet=Image.new('RGB',(1800,420),(232,233,228))
  for i,t in enumerate(sample):
   im=v.labelled(v.raster(v.r.geometry(id,clip=name,tick=t),tex,size=(360,340),frame_points=frame,mode='lit'),f'{short} / {t:.1f}t');sheet.paste(im,(i*360,0))
  sheet.save(out/(short+'-phases.png'))
  review[short]={'frames':40,'durationSeconds':a['animation_length'],'animationChanged':a!=old[name],'filmstrip':short+'-filmstrip.png'}
  print('Complete clip',id,short,flush=True)
 (out/'motion-review.json').write_text(json.dumps(review,indent=2)+'\n')
if __name__=='__main__':
 for id in [a for a in sys.argv[1:] if a in p.TARGETS] or p.TARGETS:
  details(id)
  if '--details-only' not in sys.argv:clips(id)
