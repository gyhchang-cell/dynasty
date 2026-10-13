"""Actual coarse production planes: opaque software diagnostics only, never native GL evidence."""
import json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/art/fangtian-sweep-v1'
def image(frame,yaw,mode='color',size=280,elevation=8):
    angle=math.radians(yaw);e=math.radians(elevation)
    toward=np.array([math.sin(angle)*math.cos(e),math.sin(e),-math.cos(angle)*math.cos(e)])
    right=np.array([math.cos(angle),0,math.sin(angle)]);up=np.cross(toward,right)
    if up[1]<0:up=-up
    basis=np.vstack((right,up,toward));background=np.array([224,222,211])
    rgb=np.empty((size,size,3),dtype=np.uint8);rgb[:]=background;depth=np.full((size,size),-np.inf)
    # Fixed world scale in every frame: 3.4 blocks across, same origin.
    scale=(size-24)/3.4
    for t in frame['triangles']:
        world=np.array([t['a'],t['b'],t['c']]);p=world@basis.T;p=p*[scale,-scale,1]+[size/2,size/2,0]
        x0=max(0,math.floor(p[:,0].min()));x1=min(size-1,math.ceil(p[:,0].max()))
        y0=max(0,math.floor(p[:,1].min()));y1=min(size-1,math.ceil(p[:,1].max()))
        if x1<x0 or y1<y0:continue
        xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
        a,b,c=p;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:continue
        u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w=1-u-v
        z=u*a[2]+v*b[2]+w*c[2];old=depth[y0:y1+1,x0:x1+1];mask=(u>=0)&(v>=0)&(w>=0)&(z>old)
        color=t['color'];color=np.array([(color>>16)&255,(color>>8)&255,color&255])
        if mode=='black':color=np.array([0,0,0])
        elif mode=='gray':color=np.array([95,98,97])
        # Deliberately opaque diagnostic, not a claim about real transparent
        # overlap blending. Geometry and discrete vertex RGB come from Java.
        rgb[y0:y1+1,x0:x1+1][mask]=color;old[mask]=z[mask]
    im=Image.fromarray(rgb);d=ImageDraw.Draw(im)
    d.line((12,size-17,12+scale,size-17),fill=(70,72,68),width=2)
    return im


data=json.loads((OUT/'actual-triangles.json').read_text());data.pop('measurements')
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
angles=[('front',0,'color',8),('45',45,'color',8),('right',90,'color',8),('left',-90,'color',8),('back',180,'color',8),('black',45,'black',8),('gray',45,'gray',8),('top',0,'color',75)]
sheet=Image.new('RGB',(280*8,90+310*2),(224,222,211));d=ImageDraw.Draw(sheet)
d.text((20,15),'FANGTIAN / ACTUAL12-FACET360 + TAPERED CROSSED CRESCENT / SOFTWARE ONLY',fill=(30,31,30),font=font)
d.text((20,40),'Same3.4-block viewport. Captured native yaw + explicit contact anchor. Recovery only, no delayed damage.',fill=(30,31,30),font=font)
for row,(name,v) in enumerate(data.items()):
 frame=next(f for f in v['frames'] if f['age']==1)
 for col,(label,yaw,mode,elev) in enumerate(angles):
  sheet.paste(image(frame,yaw,mode,elevation=elev),(col*280,90+row*310));d.text((col*280+8,90+row*310+282),name+' '+label,fill=(30,31,30),font=font)
sheet.save(OUT/'software-views.png')
sheet=Image.new('RGB',(280*7,90+310*2),(224,222,211));d=ImageDraw.Draw(sheet)
d.text((20,15),'FULL360 CONTACT AT t=0; ROTATING VISUAL RECOVERY / ORIGINAL DAMAGE IS INSTANT / SOFTWARE ONLY',fill=(30,31,30),font=font)
for row,(name,v) in enumerate(data.items()):
 for col,frame in enumerate(v['frames']):
  sheet.paste(image(frame,0,elevation=75),(col*280,90+row*310));d.text((col*280+8,90+row*310+282),name+' t='+str(frame['age']),fill=(30,31,30),font=font)
sheet.save(OUT/'software-timeline.png')
print('Generated actual Java two-yaw eight-view and native-instant/recovery diagnostics; not game screenshots')
