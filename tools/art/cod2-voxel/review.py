"""Deterministic software review of the actual Gecko JSON (Pillow + NumPy).

Orthographic evidence, not an in-game screenshot. Samples pixel UVs with nearest
neighbour filtering and uses a triangle depth buffer, including folded necks.
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
REPO=Path(__file__).resolve().parents[3]
ASSETS=REPO/"src/main/resources/assets/dynasty"
ID="jubi_shigandang"
def select(name):
    global ID,GEO,ANIM,TEX,SOURCE
    ID=name
    from resource_paths import resource_paths
    GEO,ANIM,TEX=resource_paths(ID)
    SOURCE=REPO/f"docs/art/cod2-voxel-v1/source/{ID}"
select(ID)

OUT = REPO/'docs/art/cod2-voxel-v1'


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
                inflate=c.get('inflate',0)
                p=np.array(corners)*(np.array(c['size'])+inflate*2)+np.array(c['origin'])-inflate-cp
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
    atlas=np.array(Image.open(SOURCE/'texture.png' if baseline else TEX).convert('RGB'))
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
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',action='store_true')
    parser.add_argument('--ids',nargs='+',default=['jubi_shigandang','juli_bixi_kuilei','tongbi_feitian_yecha']);args=parser.parse_args()
    views=[(0,0),(45,8),(90,0),(180,0),(0,0)]
    for name in args.ids:
        select(name);neutral=geometry('idle',0) if name=='shanjing_shanxiao' and not args.baseline else geometry(baseline=args.baseline)
        ims=[raster(neutral,*v,size=(420,360),silhouette=i==4,baseline=args.baseline) for i,v in enumerate(views)]
        sheet(ims,['FRONT','45 DEGREES','SIDE 90','BACK','BLACK SILHOUETTE'],name+('-before.png' if args.baseline else '-review.png'),name.upper(),cols=3)
        if not args.baseline:
            sheet([raster(geometry(baseline=True),35,8,baseline=True),raster(neutral,35,8)],['BEFORE / shared atlas','AFTER / 16 x 16 four-colour'],name+'-comparison.png',name.upper(),cols=2)
            actions={'jubi_shigandang':[('attack',12),('attack',16),('slam',20),('slam',30),('death',44)],'juli_bixi_kuilei':[('attack',12),('attack',18),('stomp',24),('stomp',32),('death',44)],'tongbi_feitian_yecha':[('idle',10),('attack',16),('grab',20),('grab',60),('death',44)],
                'youdeng_guimianfu':[('walk',4),('attack',12),('attack',18),('glare',24),('death',44)],
                'xueju_mangguyu':[('walk',4),('attack',12),('attack',16),('resonance',30),('death',44)],
                'shashui_funigui':[('walk',4),('attack',10),('attack',14),('pool',24),('death',44)],
                'qingtong_shuangtoushekui':[('attack',7),('attack',10),('rear_attack',10),('fire',18),('poison',18),('death',44)],
                'xunshan_mujiaquan':[('walk',4),('attack',6),('attack',8),('alarm',20),('death',44)],
                'bazu_digongzhu':[('walk',4),('attack',9),('attack',12),('drop',20),('death',44)],
                'mingsha_shixie':[('attack',8),('attack',12),('attack',20),('song',20),('death',44)],
                'baimu_mowu':[('walk',4),('attack',8),('attack',12),('gaze',26),('death',44)],
                'bishui_xuanjiao_youzi':[('walk',4),('attack',8),('attack',12),('coil',18),('death',44)],
                'chimu_zhuha':[('walk',4),('attack',8),('attack',10),('leap',10),('burst',12),('death',44)],
                'fufa_jijiu':[('walk',4),('attack',20),('attack',24),('buff',20),('death',40)],
                'juma_changqiangbing':[('walk',4),('attack',8),('attack',12),('brace',8),('death',40)],
                'kuijun_sishi':[('walk',4),('attack',8),('attack',12),('attack',17),('detonate',19),('death',40)],
                'kumu_shujing':[('camouflage',20),('wake',20),('attack',18),('roots',28),('death',44)],
                'liannu_zhenzu':[('walk',4),('attack',14),('attack',18),('attack',22),('roll',12),('death',40)],
                'ludun_jiashi':[('walk',4),('attack',12),('attack',16),('attack',24),('death',40)],
                'muxue_feilu':[('walk',4),('attack',10),('attack',14),('blood',20),('death',44)],
                'pijia_panjiang_huwei':[('walk',4),('attack',12),('attack',16),('attack',22),('counter',10),('death',44)],
                'tiesuo_chihou':[('walk',4),('attack',9),('attack',15),('grapple',12),('knee',6),('death',40)],
                'shibian_lishi':[('walk',4),('attack',14),('attack',20),('hurt',2),('death',44)],
                'yinbing_guizu':[('walk',4),('attack',10),('attack',14),('phase',3),('death',44)],
                'yinyang_zhijiao_youhun':[('walk',4),('attack',16),('hold',18),('hold',24),('hold',60),('death',44)],
                'zhenwang_zhangqiguan':[('walk',4),('attack',12),('attack',18),('hurt',2),('death',40)],
                'shanjing_shanxiao':[('walk',4),('skill',14),('skill',24),('rock',12),('rock',18),('climb',6),('death',32)],
                'zuwu_daoshou':[('walk',4),('attack',8),('attack',12),('attack',22),('death',40)],
                'fuhun_baibu_tongzi':[('walk',4),('attack',8),('attack',12),('curse',34),('curse',40),('death',36)],
                'zhiren_jianke':[('walk',4),('attack',2),('attack',6),('shed',2),('shed',6),('death',8)],
                'xianzhen_duantoujiang':[('walk',4),('roar',24),('spin',26),('spin',36),('throw',20),('death',60)],
                'qianji_bailian_yanshi':[('walk',4),('net',14),('wheels',10),('spiders',20),('death',52)],
                'yanshi_clockwork_spider':[('walk',2),('walk',4),('fuse',0),('fuse',3)]}[name]
            sheet([raster(geometry(c,t),35,10,size=(420,360)) for c,t in actions],[f'{c} / tick {t}' for c,t in actions],name+'-actions.png',name.upper()+' ACTIONS',cols=3)
    print('review complete:',OUT)

if __name__=='__main__':main()
