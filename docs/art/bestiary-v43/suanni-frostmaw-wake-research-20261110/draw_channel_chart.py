"""Plot selected relative keyframe channels, never model/world-ground positions."""
from pathlib import Path
import runpy
from PIL import Image, ImageDraw, ImageFont

B = Path(__file__).resolve().parent
R = runpy.run_path(str(B / 'read_wake_phases.py'))
text = R['SOURCE'].read_text()
names = ['ACTIVATE_ANIMATION', 'ACTIVATE_NO_CRYSTAL_ANIMATION', 'DEACTIVATE_ANIMATION']
im = Image.new('RGB', (1200, 780), '#f4f1e9')
d = ImageDraw.Draw(im)
font = ImageFont.load_default(size=15)
title = ImageFont.load_default(size=20)
d.text((24, 15), 'Frostmaw wake / sleep: selected SOURCE CHANNELS', fill='#17232b', font=title)
d.text((24, 45), 'Relative targets only. No geometry, terrain, lighting, textures or runtime proof.', fill='#6b3434', font=font)
channels = [('root:rotate',2,1.2,'#936039','root Z (rad)'),
            ('headJoint:rotate',0,1.0,'#375c93','head X (rad)'),
            ('jawJoint:rotate',0,1.6,'#9f4252','jaw X (rad)')]
for row,name in enumerate(names):
    clip = R['read_clip'](text,name)
    x0,x1,y0,y1 = 65,1160,130+row*207,285+row*207
    d.text((24,y0-38),name,fill='#17232b',font=font)
    base = y0+85
    for t in range(0,121,20):
        x=x0+(x1-x0)*t/120
        d.line([(x,y0),(x,y1)],fill='#ddd7ca')
        d.text((x-5,y1+4),str(t),fill='#676565',font=font)
    d.line([(x0,base),(x1,base)],fill='#827c70')
    for key,axis,scale,color,label in channels:
        pts=[]
        for k in range(clip['total_keyframe_ticks']*4+1):
            t=k/4
            value=R['channel_at'](clip,t,key)[axis]
            pts.append((x0+(x1-x0)*t/120,base-value*70/scale))
        d.line(pts,fill=color,width=3)
    for p in clip['phases']:
        x=x0+(x1-x0)*p['end']/120
        d.line([(x,y0),(x,y0+7)],fill='#252b2e')
for n,(_,_,_,color,label) in enumerate(channels):
    x=35+n*335
    d.line([(x,755),(x+32,755)],fill=color,width=3)
    d.text((x+40,746),label+'; separate scales',fill=color,font=font)
im.save(B/'wake-source-channels.png')
