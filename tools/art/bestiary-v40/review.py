from pathlib import Path
import sys,json,re,itertools,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/bestiary-v40';sys.path.insert(0,str(R/'tools/art/boss-forms'));import texture_review as v
report={}
old=(D/'before/DetailedBeastModel.java').read_text();body=old.split('private static void buildQilin')[1].split('private static void buildFox')[0]
# Reconstruct actual previous native box UVs for an honest same-camera comparison.
oldbones=[{'name':'root','pivot':[0,0,0]}]
for n,u,vv,w,h,d,x,y,z in re.findall(r'box\(root, "(.*?)", (\d+), (\d+), (\d+), (\d+), (\d+), ([\d.-]+)F, ([\d.-]+)F, ([\d.-]+)F\)',body):
 u,vv,w,h,d=map(int,(u,vv,w,h,d));x,y,z=map(float,(x,y,z));oldbones.append({'name':n,'parent':'root','pivot':[x,24-y,z],'cubes':[{'origin':[x-w/2,24-y-h/2,z-d/2],'size':[w,h,d],'uv':v.r.face_uv({'uv':[u,vv],'size':[w,h,d]})}]})
for kind in ('nian_beast','qilin'):
 out=D/kind;gp=out/'model.geo.json';ap=out/'model.animation.json';tex=np.array(Image.open(out/'texture.png'))
 oldgeo={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.before','texture_width':128,'texture_height':128},'bones':oldbones}]};(out/'before.geo.json').write_text(json.dumps(oldgeo,indent=2))
 def pose(t=0,clip=None):return v.r.geometry(kind,clip=clip,tick=t,geo_path=gp,animation_path=ap)
 q=pose();before=v.r.geometry(kind,geo_path=out/'before.geo.json',animation_path=ap);ot=np.array(Image.open(R/f'src/main/resources/assets/dynasty/textures/entity/{kind}.png').convert('RGB'))
 pts=np.concatenate([x[0] for x in q+before]);frame=np.array(list(itertools.product(*zip(pts.min(0)-2,pts.max(0)+2))))
 foot='真实PNG逐面采样 · 软件预览 · 非游戏截图 · 原生加载待验证'
 for yaw,n in [(0,'front'),(45,'45'),(90,'right'),(-90,'left'),(180,'back')]:
  im=v.labelled(v.raster(q,tex,yaw=yaw,elevation=6,size=(900,650),mode='lit',frame_points=frame),kind+' / '+n,foot);im.save(out/(n+'.png'))
  prior=v.raster(before,ot,yaw=yaw,elevation=6,size=(900,650),mode='lit',frame_points=frame);pair=Image.new('RGB',(1800,730));pair.paste(v.labelled(prior,'修改前：原生定义静态重建',foot),(0,0));pair.paste(im,(900,0));pair.save(out/('compare-'+n+'.png'))
 for mode,name,t in [('unlit','unlit',tex),('lit','gray',np.full_like(tex,153)),('unlit','silhouette',np.zeros_like(tex))]:v.labelled(v.raster(q,t,yaw=45,elevation=6,size=(900,650),mode=mode,frame_points=frame),name,foot).save(out/(name+'.png'))
 head=[qq for qq in q if qq[2] in ('head','snout','jaw','cheek_left','cheek_right','horn_left','horn_right','antler_left','antler_right','ear_left','ear_right')]
 v.labelled(v.raster(head,tex,yaw=45,elevation=6,size=(900,650)),kind+' / head',foot).save(out/'head.png')
 frames=[v.labelled(v.raster(pose(t,'animation.bestiary.walk'),tex,yaw=45,elevation=6,size=(640,480),frame_points=frame),'步态 '+str(t)+' tick',foot) for t in range(21)]
 frames[0].save(out/'walk.webp',save_all=True,append_images=frames[1:],duration=50,loop=0,lossless=True)
 refs=v.references(np.array([24,0,3]));v.labelled(v.raster(q+refs,tex,yaw=45,elevation=6,size=(1100,750)),'同尺度玩家、石砖与木材',foot).save(out/'scale.png')
 uv=Image.fromarray(tex.copy());dr=ImageDraw.Draw(uv);occupied=np.zeros(tex.shape[:2],bool)
 for r in json.loads((out/'uv.json').read_text()):
  x,y,w,h=r['rect'];assert x>=0 and y>=0 and x+w<=256 and y+h<=256;assert not occupied[y:y+h,x:x+w].any();occupied[y:y+h,x:x+w]=True;dr.rectangle((x,y,x+w-1,y+h-1),outline=(218,65,141))
 uv.resize((768,768),Image.Resampling.NEAREST).save(out/'uv.png')
 bones=json.loads(gp.read_text())['minecraft:geometry'][0]['bones'];names={b['name'] for b in bones};assert all(b.get('parent','root') in names for b in bones)
 envelope=[]
 for t in np.linspace(0,20,81):
  pts=np.concatenate([qq[0] for qq in pose(float(t),'animation.bestiary.walk')]);assert np.isfinite(pts).all();envelope.append([pts.min(0).tolist(),pts.max(0).tolist()])
 bb=json.loads((out/(kind+'.bbmodel')).read_text());import base64
 assert base64.b64decode(bb['textures'][0]['source'].split(',',1)[1])==(out/'texture.png').read_bytes()
 report[kind]={'bones':len(bones),'cubes':len(bones)-1,'uv_nonoverlapping':True,'pixels_per_unit':1,'walk_samples':81,'native':'PENDING; Java not launched','png_sha256':hashlib.sha256((out/'texture.png').read_bytes()).hexdigest(),'bounds_at_rest':[np.concatenate([qq[0] for qq in q]).min(0).tolist(),np.concatenate([qq[0] for qq in q]).max(0).tolist()]}
 html='<meta charset="utf-8"><style>body{background:#20282b;color:#eee;font:18px sans-serif;max-width:1500px;margin:30px auto}img{max-width:100%}a{color:#add8cf}</style><h1>'+kind+'</h1><p>本轮原创四足模型及像素图集。软件检查；原生Java模型绑定已写入，未启动游戏或声称实机通过。</p>'
 for n in ('compare-front','compare-45','compare-right','compare-back','head','scale','gray','silhouette','unlit','uv'):html+=f'<h2>{n}</h2><img src="{n}.png">'
 html+='<h2>四足步态（软件）</h2><img src="walk.webp"><h2>原始PNG</h2><img src="texture-3x.png">';(out/'index.html').write_text(html)
 print(kind,report[kind],flush=True)
(D/'validation.json').write_text(json.dumps(report,indent=2))
(D/'index.html').write_text('<meta charset="utf-8"><style>body{background:#20282b;color:#eee;font:20px sans-serif;margin:35px}img{max-width:100%}a{color:#add8cf}</style><h1>补齐两只共用形体的神兽</h1><p>年兽：厚前躯、低头、獠牙与鬃毛。麒麟：拱颈、角枝、分蹄与方向鳞纹。</p>'+''.join(f'<h2><a href="{k}/index.html">{k} 完整对照与动作</a></h2><img src="{k}/45.png">' for k in report)+'<p>延用已有1000样本库，本轮实际复看虎、羚羊、鹿和野猪结构，以及虎/鹿原始PNG，不声称本轮新增看完1000只。</p>')
