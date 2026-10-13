"""Software shape/color review of Java's actual triangles; never game evidence."""
import json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/art/weapon-impact-v1'


def image(frame,yaw,mode='color',size=280):
    angle=math.radians(yaw);e=math.radians(8)
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


def main():
    data=json.loads((OUT/'actual-triangles.json').read_text());folder=OUT/'software';folder.mkdir(exist_ok=True)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
    sheets=[]
    angles=[('front',0,'color'),('45',45,'color'),('side',90,'color'),('back',180,'color'),('black',45,'black'),('gray',45,'gray')]
    canvas=Image.new('RGB',(280*6,90+len(data)*310),(224,222,211));d=ImageDraw.Draw(canvas)
    d.text((20,15),'ACTUAL JAVA TRIANGLES / FIXED WORLD SCALE / SOFTWARE SHAPE+COLOR ONLY',fill=(30,31,30),font=font)
    d.text((20,40),'No GLFW, game lighting or transparent-overlap acceptance. Bottom line = one world block.',fill=(30,31,30),font=font)
    for row,(id,v) in enumerate(data.items()):
        # A middle frame shows physical expansion instead of auto-zooming tiny
        # freshly spawned geometry. Each effect stays on the same world scale.
        age=3 if id!='yitian_sword' else 4
        frame=next(f for f in v['frames'] if f['age']==age)
        for col,(label,yaw,mode) in enumerate(angles):
            im=image(frame,yaw,mode);im.save(folder/f'{id}-{label}-{age}.png')
            canvas.paste(im,(col*280,90+row*310));d.text((col*280+8,90+row*310+282),id+' '+label+' t='+str(age),fill=(30,31,30),font=font)
    canvas.save(OUT/'software-views.png')
    timeline=Image.new('RGB',(280*8,90+3*310),(224,222,211));d=ImageDraw.Draw(timeline)
    d.text((20,20),'EXACT JAVA TIMELINE FRAMES / SAME WORLD SCALE / SOFTWARE ONLY',fill=(30,31,30),font=font)
    for row,id in enumerate(['qinggang_sword','gilded_mace','yitian_sword']):
        for col,frame in enumerate(data[id]['frames']):
            im=image(frame,45);timeline.paste(im,(280*col,90+310*row));d.text((280*col+8,90+310*row+282),id+' t='+str(frame['age']),fill=(30,31,30),font=font)
    timeline.save(OUT/'software-rhythms.png')
    print('Generated actual-triangle multi-view and timeline diagnostics; native visuals pending')


if __name__=='__main__':main()
