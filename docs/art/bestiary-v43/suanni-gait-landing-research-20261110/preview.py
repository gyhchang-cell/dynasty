from pathlib import Path
import importlib.util,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path('/Users/a15356015027/Desktop/dynasty');O=R/'docs/art/bestiary-v43/suanni-gait-landing-research-20261110'
spec=importlib.util.spec_from_file_location('suanni_contact_preview',R/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/elite'
id='zhenmu_suanni_tonghou';poses=[('walk',27.9),('stomp',9.9),('death',24),('death',57)]
qs=[r.geometry(id,clip='animation.'+id+'.'+clip,tick=t)for clip,t in poses]
# Side view at zero elevation gives a legible local Y=0 line; same bounds/scale all panels.
lo=np.array([-44,-3,-60]);hi=np.array([44,42,60]);w,h=720,560;scale=min((w-64)/(hi[0]-lo[0]),(h-70)/(hi[1]-lo[1]));center=(lo+hi)/2
y=int(h/2+center[1]*scale)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
out=Image.new('RGB',(w*2,(h+42)*2+50),(238,235,225));d=ImageDraw.Draw(out)
for i,(q,(clip,t))in enumerate(zip(qs,poses)):
 r.TEX=R/f'src/main/resources/assets/dynasty/textures/entity/blueprint/elite/{id}{"_dead" if clip=="death" and t>=16 else ""}.png'
 im=r.raster(q,yaw=90,elevation=0,size=(w,h),frame_bounds=(lo,hi));di=ImageDraw.Draw(im);di.line((15,y,w-15,y),fill=(130,65,53),width=2);di.text((16,y-24),'local Y=0',font=font,fill=(130,65,53))
 x=i%2*w;yy=i//2*(h+42)+50;out.paste(im,(x,yy));d.text((x+18,yy+h+8),f'{clip} / {t} ticks / identical side camera and scale',font=font,fill=(35,38,43))
d.text((20,15),'Actual current PNG + final geometry; offline linear transforms only; not Minecraft capture',font=font,fill=(35,38,43))
out.save(O/'contact-poses.png');print(O/'contact-poses.png')
