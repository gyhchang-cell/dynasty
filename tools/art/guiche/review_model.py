"""Deterministic software review of the actual Gecko JSON (Pillow + NumPy).

Orthographic evidence, not an in-game screenshot. Samples pixel UVs with nearest
neighbour filtering and uses a triangle depth buffer, including folded necks.
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from build_model import REPO, GEO, ANIM, TEX, ID, SOURCE

OUT = REPO/'docs/art/guiche-v2'


def sample(track, t):
    if isinstance(track, list): return np.array(track, dtype=float)
    pairs = sorted((float(k),np.array(v,dtype=float)) for k,v in track.items())
    if t <= pairs[0][0]: return pairs[0][1]
    for (a,v),(b,w) in zip(pairs,pairs[1:]):
        if t <= b: return v+(w-v)*(t-a)/(b-a)
    return pairs[-1][1]


def transform(position=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
    x,y,z = np.radians(np.array(rotation)*[-1,-1,1])
    cx,cy,cz,sx,sy,sz = math.cos(x),math.cos(y),math.cos(z),math.sin(x),math.sin(y),math.sin(z)
    rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    m=np.eye(4);m[:3,:3]=rz@ry@rx@np.diag(scale)
    m[:3,3]=np.array(position)*[-1,1,1]
    return m


# Four corners in image-UV order; orientation follows Gecko's mirrored X axis.
FACES = {
    'north': [(1,1,0),(0,1,0),(0,0,0),(1,0,0)],
    'south': [(0,1,1),(1,1,1),(1,0,1),(0,0,1)],
    'east': [(1,1,1),(1,1,0),(1,0,0),(1,0,1)],
    'west': [(0,1,0),(0,1,1),(0,0,1),(0,0,0)],
    'up': [(0,1,1),(1,1,1),(1,1,0),(0,1,0)],
    'down': [(0,0,0),(1,0,0),(1,0,1),(0,0,1)],
}


def geometry(clip=None, tick=0, baseline=False):
    g=json.loads((SOURCE/'original.geo.json' if baseline else GEO).read_text())['minecraft:geometry'][0]
    a=json.loads((SOURCE/'original.animation.json' if baseline else ANIM).read_text())['animations']
    channels=a.get('animation.'+ID+'.'+str(clip),{}).get('bones',{})
    world={};pivots={b['name']:np.array(b['pivot']) for b in g['bones']};quads=[]
    for b in g['bones']:
        ch=channels.get(b['name'],{});pivot=pivots[b['name']]
        pos=pivot-(pivots[b['parent']] if b.get('parent') else np.zeros(3))
        rot=np.array(b.get('rotation',[0,0,0]),dtype=float)
        if 'position' in ch:pos=pos+sample(ch['position'],tick/20)
        if 'rotation' in ch:rot=rot+sample(ch['rotation'],tick/20)
        sc=sample(ch['scale'],tick/20) if 'scale' in ch else [1,1,1]
        matrix=(world[b['parent']] if b.get('parent') else np.eye(4))@transform(pos,rot,sc)
        world[b['name']]=matrix
        for c in b.get('cubes',[]):
            cp=np.array(c.get('pivot',b['pivot']))
            cm=matrix@transform(cp-pivot,c.get('rotation',[0,0,0]))
            for f,corners in FACES.items():
                p=np.array(corners)*np.array(c['size'])+np.array(c['origin'])-cp
                p=p*[-1,1,1]
                p=(cm@np.column_stack((p,np.ones(4))).T).T[:,:3]
                quads.append((p,c['uv'][f],b['name']))
    return quads


def raster(quads,yaw=0,elevation=8,size=(720,560),silhouette=False,baseline=False):
    w,h=size;yaw,elevation=map(math.radians,(yaw,elevation))
    toward=np.array([math.sin(yaw)*math.cos(elevation),math.sin(elevation),-math.cos(yaw)*math.cos(elevation)])
    right=np.array([math.cos(yaw),0,math.sin(yaw)])
    up=np.cross(toward,right);up=-up if up[1]<0 else up
    basis=np.vstack((right,up,toward));points=np.concatenate([p for p,_,_ in quads]); projected=points@basis.T
    lo,hi=projected.min(0),projected.max(0);center=(lo+hi)/2
    scale=min((w-64)/(hi[0]-lo[0]),(h-70)/(hi[1]-lo[1]))
    bg=(238,235,225) if not silhouette else (248,246,239)
    rgb=np.empty((h,w,3),dtype=np.uint8);rgb[:]=bg;depth=np.full((h,w),-np.inf)
    atlas=np.array(Image.open(REPO/'src/main/resources/assets/dynasty/textures/entity/nian_beast.png' if baseline else TEX).convert('RGB'))
    light=np.array([-.35,.8,-.5]);light/=np.linalg.norm(light)
    for vertices,uv,bone in quads:
        p=(vertices@basis.T-center)*[scale,-scale,1]+[w/2,h/2,0]
        normal=np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]);n=np.linalg.norm(normal)
        if n<1e-9:continue
        shade=.68+.32*abs(float((normal/n)@light))
        x,y=uv['uv'];du,dv=uv['uv_size'];tex=np.array([[x,y],[x+du,y],[x+du,y+dv],[x,y+dv]],dtype=float)
        for inds in [(0,1,2),(0,2,3)]:
            tri=p[list(inds)];tc=tex[list(inds)]
            x0=max(0,int(math.floor(tri[:,0].min())));x1=min(w-1,int(math.ceil(tri[:,0].max())))
            y0=max(0,int(math.floor(tri[:,1].min())));y1=min(h-1,int(math.ceil(tri[:,1].max())))
            if x1<x0 or y1<y0:continue
            xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
            a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-9:continue
            u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
            v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;z=1-u-v
            zz=u*a[2]+v*b[2]+z*c[2];old=depth[y0:y1+1,x0:x1+1]
            mask=(u>=-1e-6)&(v>=-1e-6)&(z>=-1e-6)&(zz>old)
            if not mask.any():continue
            tx=np.clip((u*tc[0,0]+v*tc[1,0]+z*tc[2,0]).astype(int),0,atlas.shape[1]-1)
            ty=np.clip((u*tc[0,1]+v*tc[1,1]+z*tc[2,1]).astype(int),0,atlas.shape[0]-1)
            color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade
            if baseline and not silhouette and any(s in bone for s in ['body','tail','wing','feather']):color=color*[1,.58,.55]
            rgb[y0:y1+1,x0:x1+1][mask]=np.clip(color,0,255).astype('uint8')[mask];old[mask]=zz[mask]
    return Image.fromarray(rgb)


def font(size):
    path=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
    return ImageFont.truetype(str(path),size) if path.exists() else ImageFont.load_default()


def sheet(images,labels,file,title,cols=3):
    cw,ch=images[0].size;rows=math.ceil(len(images)/cols)
    out=Image.new('RGB',(cw*cols,80+(ch+42)*rows+44),(238,235,225));d=ImageDraw.Draw(out)
    d.text((28,19),title,fill=(41,38,49),font=font(27))
    for i,(im,label) in enumerate(zip(images,labels)):
        x=(i%cols)*cw;y=80+(i//cols)*(ch+42);out.paste(im,(x,y));d.text((x+25,y+ch+4),label,fill=(64,54,63),font=font(19))
    d.text((28,out.height-31),'Actual exported Cuboid geometry / nearest-pixel UV / software preview, not Minecraft capture',fill=(90,82,89),font=font(16))
    out.save(OUT/file)


def main():
    neutral=geometry();views=[(0,6),(45,12),(90,6),(180,6),(0,6)]
    ims=[raster(neutral,*v,size=(640,460),silhouette=i==4) for i,v in enumerate(views)]
    ims.append(raster(geometry('death',70),45,20,size=(640,460)))
    sheet(ims,['FRONT 0','THREE-QUARTER 45','SIDE 90','BACK 180','BLACK SILHOUETTE','DEATH - LANDED / tick 70'], 'review.png','GUICHE / EIGHT MOURNING FACES + CENTRAL STUMP')
    raster(neutral,35,10,size=(1400,1020)).save(OUT/'hero.png')
    sheet([raster(geometry(baseline=True),35,10,baseline=True),raster(neutral,35,10)],['BEFORE / shared atlas','AFTER / dedicated four-colour atlas'],'before-after.png','DYNASTY / GUICHE ART REBUILD',cols=2)
    poses=[('fly',6),('peck',12),('peck',40),('bomb',20),('dive',24),('death',70)]
    sheet([raster(geometry(a,t),40,12,size=(640,460)) for a,t in poses],[f'{a.upper()} / tick {t}' for a,t in poses],'actions.png','GUICHE / EXISTING SEVEN-CLIP ANIMATION CONTRACT')
    bounds={}
    for a,t in [(None,0),('death',40),('death',60),('death',80)]:
        pts=np.concatenate([p for p,_,_ in geometry(a,t)])
        bounds[f'{a or "rest"}@{t}']={'min':pts.min(0).round(3).tolist(),'max':pts.max(0).round(3).tolist()}
    (OUT/'pose-bounds.json').write_text(json.dumps(bounds,indent=2)+'\n')
    print(json.dumps(bounds,indent=2))


if __name__=='__main__':main()
