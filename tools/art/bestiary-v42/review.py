"""Render native-baked ModelPart vertices with real nearest-sampled PNGs.

Every before/after shares camera, world scale and basic lighting. This is an
offline native-mesh review, never labelled an in-game capture.
"""
from pathlib import Path
import sys, importlib.util, json, gzip, hashlib, zipfile, subprocess, math
import numpy as np
from PIL import Image, ImageDraw
from build_models import ROOT,OUT,ASSETS,IDS,TITLES,SCALES,faces

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
old_build=load('v41_build',ROOT/'tools/art/bestiary-v41/build_models.py')
sys.modules['build_models']=old_build
r=load('v41_review',ROOT/'tools/art/bestiary-v41/review.py')

def capture():
    build=ROOT/'build/bestiary-v42';classes=build/'classes';classes.mkdir(exist_ok=True)
    cp=str(ROOT/'build/classes/java/main')+':'+(ROOT/'build/bestiary-v41/classpath.txt').read_text().strip()
    java='/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/'
    with (build/'native-compile.log').open('w') as log:
        subprocess.run([java+'javac','-cp',cp,'-d',str(classes),str(ROOT/'tools/art/bestiary-v42/NativeMeshCheck.java')],check=True,stdout=log,stderr=subprocess.STDOUT)
    with (build/'native-bake.log').open('w') as log:
        subprocess.run([java+'java','-Djava.awt.headless=true','-cp',str(classes)+':'+cp,'com.dynasty.client.NativeMeshCheck',str(build/'native-mesh.json.gz')],check=True,stdout=log,stderr=subprocess.STDOUT)
    return json.loads(gzip.decompress((build/'native-mesh.json.gz').read_bytes()))

def quads(raw):
    raw=np.array(raw,dtype=float).reshape((-1,4,5))
    return [(q[:,:3],q[:,3:],'__native') for q in raw]

def label(im,text):
    # Keep captions outside the model image; long Chinese labels must not cover a helmet.
    canvas=Image.new('RGB',(im.width,im.height+44),'#e8eae2');canvas.paste(im,(0,44))
    ImageDraw.Draw(canvas).text((16,10),text,font=r.font(20),fill='#283936');return canvas

def close(q,atlas,axis='head',mode='lit'):
    # Show the actual complete geometry, framing the head/chest rather than inventing a new face.
    im=r.raster(q,atlas,10,size=(900,900),scale=18,mode=mode)
    box=(260,30,650,335) if axis=='head' else (260,270,650,575)
    return im.crop(box).resize((780,610),Image.Resampling.NEAREST)

def main():
    native=capture();overview=[];report={}
    for id,title,scale in zip(IDS,TITLES,SCALES):
        folder=OUT/id;data=json.loads((folder/'model.json').read_text())
        atlas=Image.open(folder/'texture.png').convert('RGBA');oldtex=Image.open(folder/'before.texture.png')
        q=quads(native[id]['idle@0']);old=quads(native[id]['before'])
        r.card([r.raster(old,oldtex),r.raster(q,atlas)],['旧版实际模型 / PNG','本轮实际模型 / 独立PNG'],folder/'before-after.png',title+' · 同机位 / 同尺度 / 基础光照')
        images=[]
        for angle,name in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
            im=r.raster(q,atlas,angle);im.save(folder/(name+'.png'));images.append(im)
        r.card(images,['正面','45度','侧面','背面'],folder/'views.png',title+' · 原始PNG逐面贴图',2)
        r.card([r.raster(q,atlas,40,mode='unlit'),r.raster(q,atlas,40,mode='gray'),r.raster(q,atlas,40,mode='silhouette'),r.raster(q,atlas,40,reference=True)],['原色，无额外光效','灰模','黑色剪影','玩家与石砖，同一世界比例'],folder/'checks.png',title+' · 材质 / 轮廓 / 比例')
        for part in ['head','chest']:label(close(q,atlas,part),title+' · '+('头部' if part=='head' else '胸部')).save(folder/('close-'+part+'.png'))
        overview.append(r.raster(q,atlas,35,size=(720,620),scale=12,reference=True))
        for state in (['idle','walk'] if id=='minister' else ['idle','walk','attack']):
            frames=[]
            for t in range(0,80,2):
                im=r.raster(quads(native[id][state+'@'+str(t)]),atlas,35,size=(620,520),scale=11)
                frames.append(label(im,title+f' / {state} / {t} tick · 离线'))
            frames[0].save(folder/(state+'.gif'),save_all=True,append_images=frames[1:],duration=100,loop=0)
        if id!='minister':
            r.card([r.raster(quads(native[id]['attack@'+str(t)]),atlas,35,size=(480,440),scale=10) for t in (0,4,8,12,18)],['挥击进度0%','挥击进度20%','挥击进度40%','挥击进度60%','挥击进度90%'],folder/'attack-stages.png',title+' · 原版挥击进度驱动（离线扫描不宣称伤害接触帧）',3)
        # Direction-labelled checker is diagnostic only, never written to runtime assets.
        checker=Image.new('RGBA',(128,128));d=ImageDraw.Draw(checker)
        occupied=np.zeros((128,128),dtype=np.uint8);count=0
        for i,b in enumerate(data['bones']):
            for c in b['cubes']:
                for f,(u,v,w,h) in faces(c).items():
                    u,v,w,h=map(int,(u,v,w,h));assert u>=0 and v>=0 and u+w<=128 and v+h<=128
                    assert not occupied[v:v+h,u:u+w].any(),(id,b['name'],f,'overlap')
                    occupied[v:v+h,u:u+w]=1
                    assert np.array(atlas)[v:v+h,u:u+w,3].min()==255
                    d.rectangle((u,v,u+w-1,v+h-1),fill=['#bc7757','#69969c','#a29755'][i%3]);d.line((u,v,u+w-1,v),fill='#ffffdf');d.point((u,v+h-1),fill='#ff5151')
                    count+=1
        r.raster(q,checker,35,mode='unlit').save(folder/'uv-direction.png')
        poses={k:v for k,v in native[id].items() if k!='before'}
        bounds=[]
        for key,raw in poses.items():
            arr=np.array(raw);assert np.isfinite(arr).all()
            assert arr[:,3:].min()>=0 and arr[:,3:].max()<=128
            assert len(arr)==count*4,(id,key,len(arr),count)
            bounds.append(float(arr[:,1].min()))
        canonical=[]
        if id!='soul_soldier':
            for name,size in [('head',[8,8,8]),('body',[8,12,4]),('right_arm',[4,12,4]),('left_arm',[4,12,4]),('right_leg',[4,12,4]),('left_leg',[4,12,4])]:
                b=next(b for b in data['bones'] if b['name']==name);assert b['cubes'][0]['size']==size;canonical.append(name)
        pts=np.concatenate([p for p,_,_ in q]);report[id]=dict(native_poses=len(poses),faces=count,bones=len(data['bones']),cubes=count//6,canonical_steve_blocks=canonical,texture=[128,128],uv_nonoverlap=True,opaque_all_faces=True,bounds_m=((pts.max(0)-pts.min(0))/16).round(3).tolist(),lowest_y_range=[min(bounds),max(bounds)],sha256=hashlib.sha256((folder/'texture.png').read_bytes()).hexdigest())
    r.card(overview,['玉甲卫 · 半覆面 / 玉色札甲','冥卒 · 空壳 / 悬布 / 骨面','雷使 · 头巾 / 露面 / 铜箍','鲛人 · 鳃鳍 / 鱼肤 / 地面步态','兵马俑 · 陶土面 / 发髻 / 模制札甲','大臣（友方）· 官帽 / 老年面部 / 叠襟'],OUT/'overview.png','五只小怪与一位友方NPC · 实际PNG / 原生模型离线预览',2)
    (OUT/'validation.json').write_text(json.dumps(dict(assets=report,checks=['Java编译','真实原生LayerDefinition烘焙','680组真实动作顶点；友方大臣不伪造攻击','每面UV边界/独立分配/不透明','五只人形六主体块Steve尺寸','追加两只前已查看100个独立怪物的模型与原始贴图'],pending=['实机自然遭遇与战斗','多人同步与20只同屏负载']),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
