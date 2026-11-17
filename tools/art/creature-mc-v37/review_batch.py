from pathlib import Path
import sys,json,math,itertools
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/creature-mc-v37';sys.path.insert(0,str(R/'tools/art/cod2-voxel'))
from creature_surfaces import IDS
from build_models import Rig
import review as r
report={};overview=Image.new('RGB',(1440,1620),(238,235,225));od=ImageDraw.Draw(overview)
for index,name in enumerate(sys.argv[1:] or IDS):
 r.select(name);g,a,t=r.GEO,r.ANIM,r.TEX;d=D/name
 old=json.loads((d/'before.geo.json').read_text());geo=json.loads(g.read_text());assert a.read_bytes()==(d/'before.animation.json').read_bytes()
 assert [{k:v for k,v in b.items() if k!='cubes'} for b in geo['minecraft:geometry'][0]['bones']]==[{k:v for k,v in b.items() if k!='cubes'} for b in old['minecraft:geometry'][0]['bones']]
 r.GEO=d/'before.geo.json';q1=r.geometry('idle',0);r.GEO=g;q2=r.geometry('idle',0)
 pts=np.concatenate([p for p,u,b in q1+q2]);lo,hi=pts.min(0),pts.max(0)
 anchors=[(np.tile([hi[i] if bit else lo[i] for i,bit in enumerate(bits)],(4,1)),{},'frame') for bits in itertools.product([0,1],repeat=3)]
 for angle in [0,45,90,180]:
  r.TEX=d/'before.png';before=r.raster(q1+anchors,angle,8,size=(640,480));r.TEX=t;after=r.raster(q2+anchors,angle,8,size=(640,480));after.save(d/f'{angle}.png')
  pair=Image.new('RGB',(1280,510),(238,235,225));pair.paste(before,(0,30));pair.paste(after,(640,30));dr=ImageDraw.Draw(pair);dr.text((15,8),'BEFORE',fill='black');dr.text((655,8),'AFTER - real PNG / same framing / software preview',fill='black');pair.save(d/f'compare-{angle}.png')
  if angle==45:
   overview.paste(after.resize((480,360)),((index%3)*480,(index//3)*540+30));od.text(((index%3)*480+8,(index//3)*540+8),name,fill='black')
 im=Image.open(t).convert('RGB');im.save(d/'texture.png');im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(d/'texture-3x.png')
 used=set();uv=im.copy();ud=ImageDraw.Draw(uv)
 for b in geo['minecraft:geometry'][0]['bones']:
  for c in b.get('cubes',[]):
   for f in c['uv'].values():
    x,y=f['uv'];w,h=f['uv_size'];assert x>=0 and y>=0 and x+w<=im.width and y+h<=im.height
    for Y in range(y,y+h):
     for X in range(x,x+w):assert (X,Y) not in used;used.add((X,Y))
    ud.rectangle((x,y,x+w-1,y+h-1),outline=(220,70,160))
 uv.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(d/'uv.png')
 clips=json.loads(a.read_text())['animations'];ranges={}
 for clip,data in clips.items():
  short=clip.split('.')[-1];ticks=data['animation_length']*20;allpoints=[]
  for tick in np.linspace(0,ticks,41):
   points=np.concatenate([p for p,u,b in r.geometry(short,float(tick))]);assert np.isfinite(points).all();allpoints.append(points)
  points=np.concatenate(allpoints);ranges[short]={'min':points.min(0).tolist(),'max':points.max(0).tolist()}
  frames=[r.raster(r.geometry(short,float(tick))+anchors,45,8,size=(420,340)) for tick in np.linspace(0,ticks,17)]
  frames[0].save(d/(short+'.webp'),save_all=True,append_images=frames[1:],duration=max(40,int(ticks*50/16)),loop=0)
 rig=object.__new__(Rig);rig.name=name;rig.bones=geo['minecraft:geometry'][0]['bones'];rig.image=im;rig.bbmodel(t)
 report[name]={'sameRigMetadata':True,'sameAnimationBytes':True,'UVBoundsUnique':True,'clips':ranges,'native':'pending'}
 (d/'index.html').write_text('<meta charset="utf-8"><style>body{background:#eeebe1;color:#292820;font:18px sans-serif;margin:28px}img{max-width:100%;image-rendering:pixelated}section{margin:28px 0}</style><h1>'+name+'</h1><p>左：修改前；右：修改后。相同机位、共同取景范围。真实PNG逐面软件预览，非游戏截图。</p>'+''.join(f'<section><h2>{angle}°</h2><img src="compare-{angle}.png"></section>' for angle in [0,45,90,180])+''.join(f'<section><h2>{short}</h2><img src="{short}.webp"></section>' for short in ranges)+'<h2>PNG / UV</h2><img src="texture-3x.png"><img src="uv.png">')
 print(name,'PASS',len(clips),'clips',flush=True)
overview.save(D/'overview.png');(D/'verification.json').write_text(json.dumps(report,indent=2))
(D/'index.html').write_text('<meta charset="utf-8"><style>body{background:#eeebe1;font:20px sans-serif;margin:30px}img{max-width:100%}li{margin:16px}</style><h1>八只生物：形体与像素材质修正</h1><p>软件预览；刚上传的九只精英保持不动。</p><img src="overview.png"><ul>'+''.join(f'<li><a href="{n}/index.html">{n} — 四向前后对照 / 完整动作 / PNG与UV</a></li>' for n in IDS)+'</ul>')
