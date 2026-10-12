"""Quick Steve construction demonstration + original smaller humanoid boss candidate.
Vanilla skin is read locally for review only and is NEVER placed in mod assets.
"""
from pathlib import Path
import sys,importlib.util,json,zipfile,io,copy
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/boss-steve-v14';D.mkdir(parents=True,exist_ok=True)
s=importlib.util.spec_from_file_location('grey_rig',R/'tools/art/boss-structure-v13/create.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
sys.path.insert(0,str(R/'tools/art/boss-forms'));import texture_review as v
def base(id,boss=False):
 g=m.Rig(id);g.bone('body','root',[0,12,0]);g.bone('chest','body',[0,15,0],[5,-5,0] if boss else None)
 g.box('chest',[0,18,0],[9,12,6] if boss else [8,12,4]);g.by['chest']['cubes'][-1]['uv']=[16,16]
 g.bone('head','chest',[0,24,0]);g.box('head',[0,28,0],[8,8,8]);g.by['head']['cubes'][-1]['uv']=[0,0]
 for side,x,uv,luv in [('right',-6,[40,16],[0,16]),('left',6,[32,48],[16,48])]:
  n=g.bone(side+'_arm','chest',[x,22,0],[-12 if side=='left' else 6,0,-5 if side=='left' else 7] if boss else None)
  if boss:
   g.box(n,[x,20,0],[5,8,6]);f=g.bone(side+'_forearm',n,[x,16,0],[-28 if side=='right' else -12,0,0]);g.box(f,[x,13,-1],[6,7,6])
   h=g.bone(side+'_hand',f,[x,10,-1]);g.box(h,[x,9,-1],[4.5,3,5]);g.bone(side+'_grip',h,[x,9,-2])
  else:g.box(n,[x,18,0],[4,12,4]);g.by[n]['cubes'][-1]['uv']=uv
  leg=g.bone(side+'_leg','body',[-2 if side=='right' else 2,12,0]);g.box(leg,[-2 if side=='right' else 2,6,0],[4.5,12,5] if boss else [4,12,4]);g.by[leg]['cubes'][-1]['uv']=luv
 return g
def general():
 g=base('nine_heaven_general',True)
 # Modest increases over Steve, rather than a hulking 3.7m torso.
 g.box('chest',[0,19,-3.5],[9,10,2]);g.box('chest',[0,12,0],[10,3,7])
 for side,x in [('right',-6),('left',6)]:
  g.box(side+'_arm',[x,23,0],[7.5,3.5,8],[0,0,12 if x<0 else -12])
  g.box(side+'_leg',[-3 if x<0 else 3,8,-3],[4,8,1.5])
 g.bone('helmet','head',[0,30,0]);g.box('helmet',[0,31,0],[9,3,9]);g.box('helmet',[0,33,1],[3,5,6])
 for x in [-4,4]:g.box('helmet',[x,27,1],[2,7,6])
 g.bone('mantle','chest',[0,23,4]);g.box('mantle',[0,15,4.5],[12,19,2],[-8,0,0])
 g.bone('weapon','right_grip',[-6,9,-2]);g.beam('weapon',[-6,4,-2],[-6,29,-2],1.5,1.5)
 # Broad cutting plane and stepped point make the main weapon legible at a distance.
 g.box('weapon',[-7.5,34,-2],[6,11,2]);g.box('weapon',[-9,40,-2],[3,3,2],[0,0,-20]);g.box('weapon',[-8,42,-2],[2,3,2],[0,0,-20]);g.box('weapon',[-10,29.5,-2],[3,5,2],[0,0,-25]);g.box('weapon',[-6,27,-2],[8,2,4])
 for b in g.bones:
  for c in b['cubes']:
   c.pop('_segment',None);c['uv']={f:{'uv':[2,2],'uv_size':[4,4]} for f in v.r.FACES}
 # Body ~2.6m including helmet; weapon remains its own clear silhouette.
 factor=1.19
 for b in g.bones:
  b['pivot']=[x*factor for x in b['pivot']]
  for c in b['cubes']:
   for k in ['origin','size','pivot']:
    if k in c:c[k]=[x*factor for x in c[k]]
 return g
def save(g,tex):
 p=D/g.id;p.mkdir(exist_ok=True)
 geo={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+g.id,'texture_width':tex.width,'texture_height':tex.height,'visible_bounds_width':8,'visible_bounds_height':6,'visible_bounds_offset':[0,1.5,0]},'bones':g.bones}]}
 (p/(g.id+'.geo.json')).write_text(json.dumps(geo,indent=2)+'\n')
 (p/(g.id+'.animation.json')).write_text(json.dumps({'format_version':'1.8.0','animations':{}})+'\n')
 if g.id!='steve_reference':tex.save(p/'gray.png')
 return v.r.geometry(g.id,geo_path=p/(g.id+'.geo.json'),animation_path=p/(g.id+'.animation.json'))
def run():
 jar=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar')
 with zipfile.ZipFile(jar) as z:skin=Image.open(io.BytesIO(z.read('assets/minecraft/textures/entity/player/wide/steve.png'))).convert('RGB')
 steve=base('steve_reference');q=save(steve,skin);q=[(p*.9375,uv,n) for p,uv,n in q]
 hero=general();grey=Image.new('RGB',(16,16),(160,164,166));hq=save(hero,grey)
 old=D.parent/'boss-structure-v13/candidates/nine_heaven_general';oq=v.r.geometry('nine_heaven_general',geo_path=old/'nine_heaven_general.geo.json',animation_path=old/'nine_heaven_general.animation.json')
 # Uniform camera and world units across all panels.
 frame=np.concatenate([p for qs in [q,hq,oq] for p,_,_ in qs]);uniform=lambda qs:[(p,{'uv':[2,2],'uv_size':[4,4]},n) for p,uv,n in qs]
 def render(qs,tex,title,yaw=25,black=False):
  im=v.raster(qs,np.zeros((16,16,3),dtype=np.uint8) if black else np.array(tex),yaw,elevation=3,size=(650,680),mode='unlit' if black else 'lit',frame_points=frame)
  return v.labelled(im,title,'实际模型离线预览 · 同单位/同机位 · 非游戏截图')
 board=Image.new('RGB',(1950,1520),(232,233,228))
 panels=[(q,skin,'Steve原型 / 经典6体块'),(uniform(oq),grey,'上一版天将 / 本体偏大'),(hq,grey,'Steve基础调整 / 紧凑本体＋明确大兵器')]
 for j,(qs,tx,title) in enumerate(panels):
  top=render(qs,tx,title);bottom=render(uniform(qs),grey,title+' / 正面结构',yaw=0)
  board.paste(top,(j*650,0));board.paste(bottom,(j*650,760))
  top.save(D/['steve.png','previous.png','sample.png'][j])
 board.save(D/'comparison.png')
 side=Image.new('RGB',(1950,760),(232,233,228))
 for j,yaw in enumerate([45,90,180]):side.paste(render(hq,grey,'天将快速样例 / '+str(yaw)+'°',yaw),(j*650,0))
 side.save(D/'sample-angles.png')
 scene=[(p+[-25,0,0],dict(uv,_tex=np.array(skin)),n) for p,uv,n in q]+hq
 v.labelled(v.raster(scene,np.array(grey),25,size=(1000,760),frame_points=np.concatenate([p for p,_,_ in scene])),'Steve与天将样例 / 同场景比例','离线灰模 · Steve视觉约1.88m；天将主体约2.6m · 非游戏截图').save(D/'player-scale.png')
 core=[x for x in hq if x[2] not in ['weapon','helmet','mantle']]
 render(core,grey,'去掉兵器、头盔、披挂的Steve派生主体').save(D/'body-only.png')
 (D/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Steve基础与小Boss快速对照</title><style>body{max-width:1500px;margin:auto;padding:20px;background:#eceee9;font:18px/1.6 system-ui}img{width:100%}a{color:#176079}</style><h1>Steve建模是什么？先看这个快速对照</h1><p>左：原版经典宽臂Steve，头8×8×8、躯干8×12×4、手臂4×12×4、腿4×12×4，共6个主块。皮肤从本机1.20.1客户端读取，只作研究渲染，不放进Dynasty资源。玩家碰撞身高1.8m，图中视觉模型约1.88m。</p><p>中：上一版天将灰模。右：基于Steve关节关系制作的紧凑天将样例；主体约2.6m，肩胸稍厚、肘部弯曲、重心前压，主兵器的切削面加宽。不是最终纹理或已接入游戏的成品。</p><a href="comparison.png"><img src="comparison.png"></a><a href="player-scale.png"><img src="player-scale.png"></a><a href="sample-angles.png"><img src="sample-angles.png"></a><p><a href="body-only.png">去配件主体检查</a> · <a href="nine_heaven_general/nine_heaven_general.geo.json">实际候选模型</a></p><p>本轮实际查看：灾变Scylla与Maledictus的本机隔离实机截图；铁魔法作者展示的Dead King；暮色幽灵骑士官方模型源码（HumanoidModel骨架）。暮色画廊本页主要是场景，未把它当Boss模型图片研究。</p><p><a href="https://www.curseforge.com/minecraft/mc-mods/lendercataclysm/gallery">灾变作者画廊</a> · <a href="https://media.forgecdn.net/attachments/653/896/2023-04-28_17.png">铁魔法死王作者展示</a> · <a href="https://github.com/TeamTwilight/twilightforest/blob/latest/src/main/java/twilightforest/client/model/entity/KnightPhantomModel.java">暮色幽灵骑士模型源码（技术结构参考）</a></p>''')
 print('Saved Steve demonstration and smaller Steve-derived boss candidate. No production files changed.')
if __name__=='__main__':run()
