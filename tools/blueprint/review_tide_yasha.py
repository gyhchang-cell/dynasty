#!/usr/bin/env python3
"""Fixed world-scale software review of actual exports; this never runs Minecraft.

Uses the repository's Gecko coordinate transforms and nearest-pixel raster functions.
Hidden dive phase 9..29 is controlled by the renderer; these views inspect its source
compression and emergence at 0/8/30/34/71. A 1.8m neutral figure and 1m stone are
original size references. They are neither an imported player mesh nor native proof.
"""
from pathlib import Path
import ast, json, math, importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[2]
A=R/'src/main/resources/assets/dynasty'
D=R/'docs/blueprint-cod1/evidence/tide-yasha-v1'
D.mkdir(parents=True,exist_ok=True)
ID='fubo_xunhai_yecha'
s=importlib.util.spec_from_file_location('ding_geometry',R/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);r.CATEGORY='blueprint/elite'
source=(R/'tools/art/boss-forms/texture_review.py').read_text()
for n in ast.parse(source).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('cuboid','raster'):
  code=ast.get_source_segment(source,n)
  if n.name=='raster':
   code=code.replace('center=(lo+hi)/2','center=np.array([0,18,0])@basis.T')
   code=code.replace('else:scale=min((w-80)/(hi[0]-lo[0]),(h-60)/(hi[1]-lo[1]))','else:scale=5.5')
  exec(code,globals())
tex=np.array(Image.open(A/f'textures/entity/blueprint/elite/{ID}.png').convert('RGB'))
anim=json.loads((A/f'animations/blueprint/elite/{ID}.animation.json').read_text())['animations']
def font(n):
 for p in ('/System/Library/Fonts/STHeiti Medium.ttc','/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'):
  if Path(p).exists(): return ImageFont.truetype(p,n)
 return ImageFont.load_default()
def model(clip=None,tick=0):
 q=r.geometry(ID,clip=f'animation.{ID}.{clip}' if clip else None,tick=tick)
 return [p for p in q if (not p[2].startswith('reef_') and p[2]!='planted_trident' or clip=='death') and (p[2]!='trident' or clip!='death')]
def references(yaw):
 right=np.array([math.cos(math.radians(yaw)),0,math.sin(math.radians(yaw))]);away=np.array([-math.sin(math.radians(yaw)),0,math.cos(math.radians(yaw))])
 q=[];p=right*-66+away*5
 for o,size,col in [([-4,21.6,-4],[8,7.2,8],(174,139,112)),([-4,10.8,-2],[8,10.8,4],(49,122,134)),([-7,10.8,-2],[3,10.8,4],(49,122,134)),([4,10.8,-2],[3,10.8,4],(49,122,134)),([-4,0,-2],[4,10.8,4],(56,66,93)),([0,0,-2],[4,10.8,4],(56,66,93))]:q+=cuboid(np.array(o)+p,size,np.full((2,2,3),col,dtype=np.uint8))
 stone=Image.new('RGB',(16,16),(127,130,123));d=ImageDraw.Draw(stone)
 for y in (0,8):
  d.line((0,y,15,y),fill=(78,83,79));x=(y//8)*8;d.line((x,y,x,y+7),fill=(78,83,79))
 q+=cuboid(right*68+away*4-np.array([8,0,8]),[16,16,16],np.array(stone))
 floor=Image.new('RGB',(16,16),(197,201,190));d=ImageDraw.Draw(floor);d.line((0,0,15,0),fill=(163,168,159));d.line((0,0,0,15),fill=(163,168,159))
 # Ground is a tiled 1m reference grid, not part of the entity mesh.
 for x in range(-96,97,16):
  for z in range(-96,97,16):q+=cuboid(np.array([x,-1,z]),[16,1,16],np.array(floor))
 return q

def render(clip=None,tick=0,yaw=45,mode='lit'):
 q=model(clip,tick)
 if mode in ('shape_gray','silhouette'):
  flat=np.full((2,2,3),176 if mode=='shape_gray' else 0,dtype=np.uint8)
  q=[(v,{'uv':[0,0],'uv_size':[2,2],'_tex':flat},b) for v,u,b in q]
 return raster(q+references(yaw),tex,yaw=yaw,elevation=8,size=(880,480),mode='unlit' if mode=='silhouette' else 'lit')
def labelled(im,title):
 out=Image.new('RGB',(im.width,im.height+80),(232,233,228));out.paste(im,(0,44));d=ImageDraw.Draw(out);d.text((15,8),title,fill=(37,42,43),font=font(20));d.text((15,out.height-26),'软件预览 / 实际16×16逐面UV / 1.8m玩家尺寸、1m方块自绘参照 / 非游戏截图',fill=(68,73,73),font=font(13));return out

def sheet(ims,names,title,file,cols=3):
 w,h=ims[0].size;out=Image.new('RGB',(w*cols,60+(h+35)*math.ceil(len(ims)/cols)),(232,233,228));d=ImageDraw.Draw(out);d.text((20,15),title,fill=(37,42,43),font=font(24))
 for i,(im,label) in enumerate(zip(ims,names)):
  x=i%cols*w;y=60+i//cols*(h+35);out.paste(im,(x,y));d.text((x+15,y+h+4),label,fill=(37,42,43),font=font(18))
 out.save(D/file)

report={}
for clip,data in anim.items():
 name=clip.rsplit('.',1)[1];rows=[]
 for tick in np.linspace(0,data['animation_length']*20,81):
  q=model(name,float(tick));pts=np.concatenate([p[0] for p in q]);assert np.isfinite(pts).all()
  feet=[float(np.concatenate([p[0] for p in q if p[2]==f'{side}_leg{i}_foot'])[:,1].min()) for i in range(3) for side in ('left','right')]
  mins={b:float(np.concatenate([p[0] for p in q if p[2]==b])[:,1].min()) for b in {p[2] for p in q}}
  rows.append({'tick':round(float(tick),3),'bounds':[pts.min(0).round(3).tolist(),pts.max(0).round(3).tolist()],'feetY':feet,'lowestBone':min(mins,key=mins.get),'lowestY':min(mins.values())})
 report[name]={'minimumY':min(x['lowestY'] for x in rows),'maximumY':max(x['bounds'][1][1] for x in rows),'maximumXZ':max(max(abs(x['bounds'][i][j]) for i in (0,1) for j in (0,2)) for x in rows),'minGroundedFeet':min(sum(abs(v)<.2 for v in x['feetY']) for x in rows),'samples':rows}
 print(name,{k:v for k,v in report[name].items() if k!='samples'},'lowest',min(rows,key=lambda x:x['lowestY'])['lowestBone'],flush=True)
(D/'software-sampling.json').write_text(json.dumps({'source':'actual exported Gecko JSON, software transforms only; not native PASS','samplesPerClip':81,'modelUnitsPerMetre':16,'clips':report},indent=2)+'\n')
angles=[0,180,90,-90,45,45];modes=['lit']*5+['shape_gray'];labels=['正面','背面','右侧','左侧','45度','灰模 / 45度']
ims=[render(yaw=y,mode=m) for y,m in zip(angles,modes)]
sheet(ims,labels,'伏波巡海夜叉 / 低伏甲壳、六足叉钳 / 同尺度、同相机 / 软件预览','same-scale-six-views.png')
labelled(render(mode='silhouette'),'黑剪影 / 低伏甲壳、六足承重、尾针与连接叉钳').save(D/'silhouette.png')
for name,ticks in {'idle':[0,20,40],'walk':[0,6,12,18,24],'wave':[0,6,12,18,28],'dive':[0,8,30,34,71],'combo':[0,10,19,31,39,43,54],'hurt':[0,2,8],'death':[0,8,24,32,54,70,76]}.items():
 ims=[render(name,t) for t in ticks]
 sheet(ims,[f'{name} / {t} tick' for t in ticks],f'{name} / 既有时间轴 / 软件预览',f'{name}-poses.png',cols=len(ticks))
for n in ast.parse(source).body:
 if isinstance(n,ast.FunctionDef) and n.name=='raster':
  detail=ast.get_source_segment(source,n).replace('def raster(', 'def raster_detail(')
  detail=detail.replace('center=(lo+hi)/2','center=np.array([0,14,-4])@basis.T')
  detail=detail.replace('else:scale=min((w-80)/(hi[0]-lo[0]),(h-60)/(hi[1]-lo[1]))','else:scale=10')
  exec(detail,globals())
labelled(raster_detail(model()+references(15),tex,yaw=15,elevation=10,size=(880,480),mode='lit'),
         '主体、连接叉钳与三叉头细节 / 10px每模型单位 / 此图仅供细节检查').save(D/'body-detail.png')
q=[r.geometry('yasha_tidal_vortex',clip='animation.yasha_tidal_vortex.spin',tick=t) for t in (0,6,13,20)]
sheet([raster(v+references(45),tex,yaw=45,elevation=8,size=(880,480),mode='lit') for v in q],
      [f'三米水柱 / {t} tick' for t in (0,6,13,20)],'实际水柱资源 / 同尺度玩家、地面 / 软件预览', 'vortex-poses.png',cols=4)
print('Saved actual yasha resource previews:',D,flush=True)
