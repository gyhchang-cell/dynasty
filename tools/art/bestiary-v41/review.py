"""Native ModelPart UV conventions, true pixel sampling, no averaged face colours.

Offline evidence only, not game captures. Bones, boxes and UVs are the same data
that build_models exports to the Java layer. Pose expressions match the native
BestiarySpiritModel. Every view uses a fixed scale and the same basic lighting.
"""
from pathlib import Path
import json, math, re, shutil, hashlib, gzip, zipfile, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from build_models import ROOT, OUT, ASSETS, face_rects

FONT='/System/Library/Fonts/STHeiti Medium.ttc'
def font(n):return ImageFont.truetype(FONT,n)

VANILLA=Path.home()/'.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar'
with zipfile.ZipFile(VANILLA) as archive:
    SCENE_ATLASES={
        '__player':Image.open(io.BytesIO(archive.read('assets/minecraft/textures/entity/player/wide/steve.png'))).convert('RGBA'),
        '__stone':Image.open(io.BytesIO(archive.read('assets/minecraft/textures/block/stone_bricks.png'))).convert('RGBA'),
    }

# Vertex and polygon ordering read from MC1.20.1 ModelPart.Cube/Polygon source.
V=np.array([(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)])
POLYS={'up':[5,4,0,1],'down':[2,3,7,6],'west':[0,4,7,3],
       'north':[1,0,3,2],'east':[5,1,2,6],'south':[4,5,6,7]}

def matrix(pos,rot):
    x,y,z=rot;cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    a=np.eye(4);a[:3,:3]=rz@ry@rx;a[:3,3]=pos;return a

def pose(name,t,state):
    out={};put=lambda n,r=None,p=None:out.update({n:dict(rotation=r or [0,0,0],position=p or [0,0,0])})
    flying=state=='fly';moving=state=='walk';swing=t*.62;amount=.8 if moving else 0
    put('head',[0,.35 if state=='alert' else math.sin(t*.035)*.13,0])
    if name=='phoenix':
        put('body',[-.1 if flying else math.sin(t*.07)*.018,0,0])
        for side,sign in [('left',1),('right',-1)]:
            n='wing_'+side
            put(n,[0,-sign*1.25 if not flying else 0,sign*(math.cos(t*.52)*.55 if flying else .12+math.sin(t*.09)*.025)])
            put(n+'_fore',[0,-sign*.18 if not flying else 0,sign*(math.cos(t*.52-.45)*.19 if flying else .05)])
            put(n+'_tip',[0,0,sign*math.sin(t*.52-.7)*(.1 if flying else .01)])
            put('leg_'+side,[-.7 if flying else math.cos(swing*.8+(math.pi if sign<0 else 0))*amount*.45,0,0])
            put('foot_'+side,[.55 if flying else 0,0,0])
        for i in range(3):
            put(f'tail{i}',[math.sin(t*.12+i*.4)*.07,0,0]);put(f'tail{i}_tip',[math.sin(t*.12+i*.4-.5)*.07,0,0])
    else:
        attack=math.sin((t%20)/20*math.pi) if state=='attack' else 0
        put('body',[0,0,0],[0,math.sin(t*.08)*.045,0])
        put('neck',[attack*.13,0,0])
        if attack:put('head',[-attack*.22,0,0])
        for i,n in enumerate(('front_left','front_right','back_left','back_right')):
            step=math.cos(swing*.8+(0 if i in (0,3) else math.pi))*amount*.52
            put('leg_'+n,[step,0,0]);put('ankle_'+n,[max(0,-step)*.45,0,0])
        for i in range(9):
            put(f'tail{i}',[math.sin(t*.08+i*.4)*.035,math.sin(t*.065+i*.36)*.045,0])
            put(f'tail{i}_tip',[0,math.sin(t*.065+i*.36-.55)*.08,0])
    return out

def geometry(data,t=0,state='idle',animate=True):
    world={};quads=[];channels=pose(data['id'],t,state) if animate else {}
    for b in data['bones']:
        ch=channels.get(b['name'],{});position=np.array(b['pivot'])+ch.get('position',[0,0,0]);rot=np.array(b['rotation'])+ch.get('rotation',[0,0,0])
        world[b['name']]=(world[b['parent']] if b['parent'] else np.eye(4))@matrix(position,rot)
        for c in b['cubes']:
            points=V*np.array(c['size'])+c['origin'];points=(world[b['name']]@np.column_stack((points,np.ones(8))).T).T[:,:3];points[:,1]=24-points[:,1]
            for f,inds in POLYS.items():
                u,v,w,h=face_rects(c)[f]
                if f=='down':v+=h;h=-h
                tc=np.array([[u+w,v],[u,v],[u,v+h],[u+w,v+h]])
                quads.append((points[inds],tc,b['name']))
    return quads

python_geometry=geometry
NATIVE_PATH=ROOT/'build/bestiary-v41/native-mesh.json.gz'
NATIVE=json.loads(gzip.decompress(NATIVE_PATH.read_bytes())) if NATIVE_PATH.exists() else {}

def geometry(data,t=0,state='idle',animate=True):
    key=state+'@'+str(t)
    if animate and key in NATIVE.get(data['id'],{}):
        raw=np.array(NATIVE[data['id']][key],dtype=float).reshape((-1,4,5))
        return [(quad[:,:3],quad[:,3:],'__native') for quad in raw]
    return python_geometry(data,t,state,animate)

def player(x=-19):
    q=[]
    for o,s,uv in [((-4,-8,-4),(8,8,8),(0,0)),((-4,0,-2),(8,12,4),(16,16)),((-8,0,-2),(4,12,4),(40,16)),((4,0,-2),(4,12,4),(40,16)),((-4,12,-2),(4,12,4),(0,16)),((0,12,-2),(4,12,4),(0,16))]:
        pts=V*s+np.array(o);pts[:,1]=24-pts[:,1];pts=pts*.9+[x,0,0]
        for face,ids in POLYS.items():
            u,v,w,h=face_rects({'size':s,'uv':uv})[face]
            if face=='down':v+=h;h=-h
            tc=np.array([[u+w,v],[u,v],[u,v+h],[u+w,v+h]])
            q.append((pts[ids],tc,'__player'))
    return q

def floor():
    q=[]
    for x in range(-48,48,16):
        for z in range(-32,48,16):
            q.append((np.array([[x,-.05,z],[x+16,-.05,z],[x+16,-.05,z+16],[x,-.05,z+16]]),np.array([[0,0],[16,0],[16,16],[0,16]]),'__stone'))
    return q

def raster(q,atlas,yaw=40,size=(900,640),mode='lit',scale=13,reference=False):
    w,h=size;a=math.radians(yaw);e=math.radians(9)
    toward=np.array([math.sin(a)*math.cos(e),math.sin(e),-math.cos(a)*math.cos(e)])
    right=np.array([math.cos(a),0,math.sin(a)]);up=np.cross(toward,right);up=-up if up[1]<0 else up
    basis=np.vstack((right,up,toward));rgb=np.zeros((h,w,3),np.uint8);rgb[:]=[232,234,226];depth=np.full((h,w),-np.inf)
    atlas=np.array(atlas.convert('RGBA'));extra={n:np.array(im) for n,im in SCENE_ATLASES.items()};light=np.array([-.4,.8,-.45]);light/=np.linalg.norm(light)
    center=np.array([0,12,5])@basis.T
    if reference:q=q+player(-24)+floor()
    for vertices,tc,bone in q:
        pixels=extra.get(bone,atlas)
        p=(vertices@basis.T-center)*[scale,-scale,1]+[w/2,h/2,0]
        normal=np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]);n=np.linalg.norm(normal)
        if n<1e-8:continue
        shade=.68+.32*abs(normal/n@light)
        for ids in ((0,1,2),(0,2,3)):
            tri=p[list(ids)];tex=tc[list(ids)]
            x0=max(0,math.floor(tri[:,0].min()));x1=min(w-1,math.ceil(tri[:,0].max()));y0=max(0,math.floor(tri[:,1].min()));y1=min(h-1,math.ceil(tri[:,1].max()))
            if x1<x0 or y1<y0:continue
            xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5);a,b,c=tri
            den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-8:continue
            u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;z=1-u-v
            zz=u*a[2]+v*b[2]+z*c[2];old=depth[y0:y1+1,x0:x1+1];mask=(u>=-1e-6)&(v>=-1e-6)&(z>=-1e-6)&(zz>old)
            # Clamp to the face interior to avoid floating-point sampling of an adjacent UV gutter.
            uvx=u*tex[0,0]+v*tex[1,0]+z*tex[2,0];uvy=u*tex[0,1]+v*tex[1,1]+z*tex[2,1]
            tx=np.clip(np.floor(np.clip(uvx,tex[:,0].min()+1e-5,tex[:,0].max()-1e-5)).astype(int),0,pixels.shape[1]-1)
            ty=np.clip(np.floor(np.clip(uvy,tex[:,1].min()+1e-5,tex[:,1].max()-1e-5)).astype(int),0,pixels.shape[0]-1)
            color=pixels[ty,tx,:3].astype(float);mask &= pixels[ty,tx,3]>127
            if bone.startswith('#'):
                color[:]=tuple(bytes.fromhex(bone[1:]));mask=(u>=-1e-6)&(v>=-1e-6)&(z>=-1e-6)&(zz>old)
            elif mode=='gray':color[:]=[165,174,175]
            elif mode=='silhouette':color[:]=[22,25,29]
            if mode not in ('unlit','silhouette'):color*=shade
            rgb[y0:y1+1,x0:x1+1][mask]=np.clip(color,0,255).astype(np.uint8)[mask];old[mask]=zz[mask]
    return Image.fromarray(rgb)

def baseline(name):
    src=(ROOT/'src/main/java/com/dynasty/client/DetailedBeastModel.java').read_text()
    kind='Fox' if name=='nine_tailed_fox' else 'Phoenix'
    chunk=src.split('private static void build'+kind+'(')[1].split('\n    }')[0]
    bones=[dict(name='root',parent=None,pivot=[0,0,0],rotation=[0,0,0],cubes=[])]
    pat=r'box\(root, "([^"]+)",\s*([\d., Ff\s-]+)\);'
    for n,args in re.findall(pat,chunk):
        vals=[float(x.strip().rstrip('Ff')) for x in args.split(',')];u,v,w,h,d,x,y,z=vals
        bones.append(dict(name=n,parent='root',pivot=[x,y,z],rotation=[0,0,0],cubes=[dict(origin=[-w/2,-h/2,-d/2],size=[w,h,d],uv=[u,v])]))
    if kind=='Fox':
        spots=[(0,96),(24,96),(48,96),(72,96),(96,96),(0,108),(24,108),(48,108),(72,108)]
        for i,(u,v) in enumerate(spots):bones.append(dict(name=f'tail{i}',parent='root',pivot=[(i-4)*1.4,10+(i%3)*1.5,8],rotation=[.35,math.radians((i-4)*9),0],cubes=[dict(origin=[-2,-2,0],size=[4,4,8],uv=[u,v])]))
    data=dict(id=name,bones=bones,texture_size=[128,128]);folder=OUT/name
    (folder/'before.model.json').write_text(json.dumps(data,indent=2)+'\n')
    shutil.copy2(ASSETS/'textures/entity'/f'{name}.png',folder/'before.texture.png')
    return data,Image.open(folder/'before.texture.png')

def card(images,labels,path,title,cols=2):
    cw,ch=images[0].size;out=Image.new('RGB',(cw*cols,65+math.ceil(len(images)/cols)*(ch+42)),(232,234,226));d=ImageDraw.Draw(out);d.text((20,14),title,font=font(24),fill='#283936')
    for i,(im,label) in enumerate(zip(images,labels)):
        x=(i%cols)*cw;y=65+(i//cols)*(ch+42);out.paste(im,(x,y));d.text((x+15,y+ch+6),label,font=font(18),fill='#283936')
    out.save(path)

def main():
    overview=[];report={}
    for name,title in [('nine_tailed_fox','基础九尾狐'),('phoenix','凤凰')]:
        folder=OUT/name;data=json.loads((folder/'model.json').read_text());atlas=Image.open(ASSETS/data['texture'].split('assets/dynasty/')[-1]);q=geometry(data)
        old,oldtex=baseline(name)
        before=raster(geometry(old,animate=False),oldtex);after=raster(q,atlas)
        card([before,after],['原模型 / 原始PNG','本轮 / 实际独立PNG'],folder/'before-after.png',title+' · 同机位、同尺度、同基础光照')
        views=[]
        for angle,label in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
            im=raster(q,atlas,angle);im.save(folder/(label+'.png'));views.append(im)
        card(views,['正面','45度','侧面','背面'],folder/'views.png',title+' · 软件逐像素UV预览')
        card([raster(q,atlas,40,mode='unlit'),raster(q,atlas,40,mode='gray'),raster(q,atlas,40,mode='silhouette'),raster(q,atlas,40,reference=True)],['原色 / 无额外光效','灰模','黑色剪影','玩家1.8m，同一比例'],folder/'checks.png',title+' · 材质、轮廓、比例')
        overview.append(raster(geometry(data,10,'fly') if name=='phoenix' else q,atlas,40,reference=True,scale=11))
        for state in (('idle','walk','attack') if name=='nine_tailed_fox' else ('idle','walk','fly')):
            frames=[]
            for t in range(0,80,2):
                im=raster(geometry(data,t,state),atlas,40,size=(720,500),scale=10);d=ImageDraw.Draw(im);d.text((15,15),title+' / '+state+f' / {t} tick · 离线预览',font=font(18),fill='#283936');frames.append(im)
            frames[0].save(folder/(state+'.gif'),save_all=True,append_images=frames[1:],duration=100,loop=0)
        pts=np.concatenate([p for p,_,_ in q]);report[name]=dict(bones=len(data['bones']),cubes=sum(len(b['cubes']) for b in data['bones']),bounds_m=((pts.max(0)-pts.min(0))/16).round(3).tolist(),lowest_y=float(pts[:,1].min()),texture_size=data['texture_size'])
    card(overview,['九尾狐 · 连续尾根 / 低伏四足','凤凰 · 肩翼连接 / 飞羽分层'],OUT/'overview.png','本轮未精修生物 · 实际UV贴图 · 软件预览，非游戏截图')
    (OUT/'asset-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
