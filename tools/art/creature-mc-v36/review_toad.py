import sys,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools/art/cod2-voxel'))
import review as r
from build_models import Rig
r.select('chimu_zhuha');D=R/'docs/art/creature-mc-v36/chimu_zhuha';D.mkdir(parents=True,exist_ok=True)
g=json.loads(r.GEO.read_text());old=json.loads((D/'before.geo.json').read_text())
assert r.ANIM.read_bytes()==(D/'before.animation.json').read_bytes()
assert [{k:v for k,v in b.items() if k!='cubes'} for b in g['minecraft:geometry'][0]['bones']]==[{k:v for k,v in b.items() if k!='cubes'} for b in old['minecraft:geometry'][0]['bones']]
actual=r.GEO;actualtex=r.TEX
views=[]
for angle in [0,45,90,180]:
 r.GEO=D/'before.geo.json';q1=r.geometry('idle',0)
 r.GEO=actual;q2=r.geometry('idle',0)
 points=np.concatenate([p for p,u,b in q1+q2]);lo,hi=points.min(0),points.max(0)
 import itertools
 anchors=[(np.tile(np.array([hi[i] if bit else lo[i] for i,bit in enumerate(bits)]),(4,1)),{},'frame') for bits in itertools.product([0,1],repeat=3)]
 r.TEX=D/'before.png';before=r.raster(q1+anchors,angle,8,size=(640,480))
 r.TEX=actualtex;after=r.raster(q2+anchors,angle,8,size=(640,480))
 after.save(D/f'{angle}.png');pair=Image.new('RGB',(1280,510),(238,235,225));pair.paste(before,(0,30));pair.paste(after,(640,30));d=ImageDraw.Draw(pair);d.text((15,10),'BEFORE / 2x2 shared colour',(40,40,40));d.text((655,10),'AFTER / authored skin UV - software preview',(40,40,40));pair.save(D/f'compare-{angle}.png')
a=json.loads(r.ANIM.read_text())['animations'];bounds={}
for clip,data in a.items():
 name=clip.split('.')[-1];ticks=data['animation_length']*20
 for t in np.linspace(0,ticks,41):
  q=r.geometry(name,float(t));assert all(np.isfinite(p).all() for p,u,b in q)
 frames=[r.raster(r.geometry(name,float(t)),45,8,size=(480,360)) for t in np.linspace(0,ticks,25)]
 frames[0].save(D/(name+'.webp'),save_all=True,append_images=frames[1:],duration=max(40,int(ticks*50/24)),loop=0)
 bounds[name]='41 finite geometry samples; 25-frame software playback'
im=Image.open(r.TEX);im.save(D/'texture.png');im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(D/'texture-4x.png')
mask=Image.new('1',im.size);md=ImageDraw.Draw(mask)
for b in g['minecraft:geometry'][0]['bones']:
 for c in b.get('cubes',[]):
  for uv in c['uv'].values():
   x,y=uv['uv'];w,h=uv['uv_size'];assert x>=0 and y>=0 and x+w<=im.width and y+h<=im.height
   assert not mask.crop((x,y,x+w,y+h)).getbbox();md.rectangle((x,y,x+w-1,y+h-1),fill=1)
# Source export uses the very same face UVs and dimensions.
rig=object.__new__(Rig);rig.name='chimu_zhuha';rig.bones=g['minecraft:geometry'][0]['bones'];rig.image=im;rig.bbmodel(r.TEX)
(D/'verification.json').write_text(json.dumps({'rigAndAnimationPreserved':True,'UVBoundsAndNoOverlap':True,'clips':bounds,'nativeGame':'pending'},indent=2))
(D/'index.html').write_text('<meta charset="utf-8"><title>赤目朱蛤 — 修改对照</title><style>body{background:#eeebe1;color:#242424;font:18px sans-serif;margin:32px}img{max-width:100%;image-rendering:pixelated}section{margin:30px 0}</style><h1>赤目朱蛤：头身、前后肢与皮肤</h1><p>软件逐面PNG预览，不是游戏截图。旧版左，新版右；相同视角、共同包围范围与相同像素比例。</p>'+''.join(f'<section><h2>{a}°</h2><img src="compare-{a}.png"></section>' for a in [0,45,90,180])+''.join(f'<section><h2>{n} — 完整时间轴</h2><img src="{n}.webp"></section>' for n in bounds)+'<h2>实际像素图集</h2><img src="texture-4x.png"><p>参考：Alex’s Mobs 雨蛙的短颈连续身体与背腹色区。没有复制原纹理。1000项模型+贴图研究仍未完成。</p>')
print('PASS',len(bounds),'clips; UV; rig; animation bytes; Blockbench export')
