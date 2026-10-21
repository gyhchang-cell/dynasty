"""Actual native pixel crops and matched-camera before/after, with live PNG/UV evidence."""
from pathlib import Path
import json,sys,hashlib,shutil,importlib.util,math
from PIL import Image,ImageDraw,ImageFont
import numpy as np
R=Path(__file__).resolve().parents[3];A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/fighter-identity-v26';V=R/'docs/art/steve-fighters-v25';N=V/'native/fighters-v25-identity-v26';B=V/'native/fighters-v25-integrated'
sys.path.insert(0,str(R/'tools/art/steve-fighters-v25'));import identity
FONT='/System/Library/Fonts/STHeiti Medium.ttc';font=lambda s:ImageFont.truetype(FONT,s)
TARGETS=json.loads((V/'targets.json').read_text())+[{'id':'tree_spirit','name':'树灵'}]
def software_tree():
 sys.path.insert(0,str(R/'tools/art/boss-forms'));import texture_review as v
 tex=np.array(Image.open(A/'textures/entity/secondary/tree_spirit.png'));geo=A/'geo/secondary/tree_spirit.geo.json';an=A/'animations/secondary/tree_spirit.animation.json';q=v.r.geometry('tree_spirit',geo_path=geo,animation_path=an);dd=D/'tree_spirit';dd.mkdir(exist_ok=True)
 for name,angle in [('front',0),('45',45),('side',90),('back',180)]:v.labelled(v.raster(q,tex,yaw=angle,mode='lit'),'树灵 / '+name+' 软件实际UV预览').save(dd/f'{name}-software.png')
 Image.open(A/'textures/entity/secondary/tree_spirit.png').resize((1024,512),Image.Resampling.NEAREST).save(dd/'texture-4x.png')
 def sourcebefore():return D/'before/src/main/resources/assets/dynasty/geo/secondary/tree_spirit.geo.json'
 qb=v.r.geometry('tree_spirit',geo_path=sourcebefore(),animation_path=an);bt=np.array(Image.open(D/'before/src/main/resources/assets/dynasty/textures/entity/secondary/tree_spirit.png'));frame=np.concatenate([x[0]for x in q+qb]);ims=[v.labelled(v.raster(qq,tt,mode='lit',size=(800,750),frame_points=frame),label)for qq,tt,label in [(qb,bt,'修改前·软件'),(q,tex,'修改后·软件')]];out=Image.new('RGB',(1600,830));out.paste(ims[0],(0,0));out.paste(ims[1],(800,0));out.save(dd/'comparison-software.png')

def native():
 assert (N/'PASS.txt').exists(),'Only complete passing native batches are publishable'
 overview=Image.new('RGB',(1700,1200),(232,234,224));od=ImageDraw.Draw(overview);heads=Image.new('RGB',(1400,math.ceil(len(TARGETS)/7)*250),(232,234,224));hd=ImageDraw.Draw(heads)
 for i,t in enumerate(TARGETS):
  id=t['id'];dd=D/id;dd.mkdir(exist_ok=True);first=Image.open(next(N.glob(f'*-{id}-front.png')));w,h=first.size;crop=(round(w*.22),round(h*.05),round(w*.76),round(h*.88))
  for view in ['front','45','side','back','action']:
   matches=list(N.glob(f'*-{id}-{view}.png'))
   if not matches and view=='action':matches=[min((N/'frames'/id).glob('*.png'),key=lambda p:abs(int(p.stem)-16))]
   pp=matches[0];im=Image.open(pp);im.crop(crop).save(dd/(view+'.png'))
  card=Image.new('RGB',(340,360),(232,234,224));ci=first.crop(crop);ci.thumbnail((340,360));card.paste(ci,((340-ci.width)//2,360-ci.height));card.save(dd/'card.png');overview.paste(Image.open(dd/'card.png'),(i%5*340,i//5*400));od.text((i%5*340+6,i//5*400+364),t['name'],font=font(22),fill=(28,39,39))
  box=(.44,.38,.57,.55)if id=='tree_spirit'else(.44,.26,.57,.47);face=first.crop(tuple(round(v*(w if j%2==0 else h))for j,v in enumerate(box)));face.save(dd/'head.png');face.thumbnail((190,205));heads.paste(face,(i%7*200,i//7*250));hd.text((i%7*200+5,i//7*250+210),t['name'],font=font(19),fill=(28,39,39))
  old=Image.open(next(B.glob(f'*-{id}-front.png'))).crop(crop);new=first.crop(crop);comparison=Image.new('RGB',(old.width*2,old.height+35),(232,234,224));comparison.paste(old,(0,0));comparison.paste(new,(old.width,0));cd=ImageDraw.Draw(comparison);cd.text((10,old.height+2),'修改前',font=font(23),fill=(25,34,34));cd.text((old.width+10,old.height+2),'修改后',font=font(23),fill=(25,34,34));comparison.save(dd/'before-after.png')
  frames=[];durations=[];fps=sorted((N/'frames'/id).glob('*.png'))
  for j,p in enumerate(fps):
   im=Image.open(p).crop(crop);im.thumbnail((680,850));frames.append(im);tick=int(p.stem.rsplit('-',1)[-1])if '-'in p.stem else j*2;durations.append(100)
  if frames:frames[0].save(dd/'motion.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0)
  tp=A/f'textures/entity/steve_fighters/{id}.png'if id!='tree_spirit'else A/'textures/entity/secondary/tree_spirit.png';im=Image.open(tp);im.save(dd/'texture.png');over=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST);draw=ImageDraw.Draw(over)
  if id!='tree_spirit':
   q=json.loads((A/f'models/entity/steve_fighters/{id}.json').read_text());islands=[f for p in q['parts']for f in p['faces'].values()]
  else:
   q=json.loads((A/'geo/secondary/tree_spirit.geo.json').read_text())['minecraft:geometry'][0];islands=[f for b in q['bones']for c in b.get('cubes',[])for f in c['uv'].values()]
  for uv in islands:
   x,y=uv['uv'];ww,hh=uv['uv_size'];assert x>=0 and y>=0 and x+ww<=im.width and y+hh<=im.height;draw.rectangle((x*4,y*4,(x+ww)*4-1,(y+hh)*4-1),outline=(217,103,157))
  over.save(dd/'uv.png');im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(dd/'texture-4x.png')
 overview.save(D/'overview.jpg',quality=95);heads.crop((0,0,1400,500)).save(D/'heads-game.jpg',quality=95)
 proof=D/'native';proof.mkdir(exist_ok=True)
 for n in ['PASS.txt','runtime-manifest.json','creative-inventory.json']:shutil.copy2(N/n,proof/n)

def page():
 cards=[]
 for t in TARGETS:
  id=t['id'];note=identity.DESCRIPTIONS.get(id,'树干贯通、分叉承接偏冠、底部四向树根。树冠总高度约2.6格；树皮纵向组织，叶丛采用连接色簇；保持已有骨架、动作与碰撞。')
  imgs=''.join(f'<figure><img loading="lazy" src="{id}/{f}.png"><figcaption>{label}</figcaption></figure>'for f,label in [('front','实机正面'),('45','实机45度'),('side','实机侧面'),('back','实机背面'),('head','实机头部近景'),('before-after','同机位前后')])
  cards.append(f'<section><h2>{t["name"]} <small>dynasty:{id}</small></h2><p>{note}</p><div class="row">{imgs}</div><details><summary>动作、原始PNG和UV检查</summary><div class="row"><figure><img loading="lazy" src="{id}/motion.gif"><figcaption>实机同步动作时钟·AI关闭</figcaption></figure><figure><a href="{id}/texture.png"><img loading="lazy" src="{id}/texture-4x.png"></a><figcaption>实际PNG最近邻4倍，点击原图</figcaption></figure><figure><img loading="lazy" src="{id}/uv.png"><figcaption>UV岛检查</figcaption></figure></div></details></section>')
 html='''<!doctype html><meta charset="utf-8"><title>人形身份区分与树灵修正</title><style>body{font:17px/1.65 system-ui;background:#172125;color:#e8e3d4;max-width:1450px;margin:30px auto;padding:0 22px}h1{font-size:28px}h2{font-size:23px}small,figcaption{font-size:14px;color:#b7c5be}section{border-top:1px solid #54605c;padding:16px 0}.row{display:flex;gap:14px;overflow:auto}figure{margin:0;min-width:280px;max-width:500px}img{max-width:100%;image-rendering:pixelated}a{color:#a6cdc1}summary{cursor:pointer}</style><h1>14种独立面部与甲衣；树灵树形修正</h1><p>保留史蒂夫六块身体与原有战斗身份。用露面/护鼻/闭面/蒙面、发须与眼部组织，以及交领、皮背心、斜带、札甲和叠甲建立差异。无新增领域、浮文或气场。鱼与机关鼠不改。</p><p>图片为同一静音隔离Forge场景的真实PNG与模型绑定；动作采用现有服务器同步时钟，AI关闭。完整自然战斗、所有技能与多人未据此宣称验证。所有人物和树灵沿用原碰撞与技能。</p><p>暮色参考实际查看：<a href="https://github.com/TeamTwilight/twilightforest/blob/e5d776e3b18258548f7fd618adf65315fbc8d053/src/main/resources/assets/twilightforest/textures/entity/squirrel2.png">松鼠背腹分色与32px图集</a>、<a href="https://github.com/TeamTwilight/twilightforest/blob/e5d776e3b18258548f7fd618adf65315fbc8d053/src/main/resources/assets/twilightforest/textures/entity/firebeetle.png">喷火甲虫的壳腹主次</a>、<a href="https://github.com/TeamTwilight/twilightforest/blob/e5d776e3b18258548f7fd618adf65315fbc8d053/src/main/resources/assets/twilightforest/textures/entity/swarmspider.png">群聚蜘蛛的暗体与局部识别点</a>。同时复看松鼠和喷火甲虫源码体块。仅借鉴少量形体与材质分区明确身份的方法，不复制资产；未声称暮色有对应树灵。</p><p><a href="validation.json">资源检查</a> · <a href="native/PASS.txt">实机记录</a></p><img src="overview.jpg"><h2>实际头部与遮面方式</h2><img src="heads-game.jpg">'''+''.join(cards)+'</html>'
 (D/'index.html').write_text(html)
if __name__=='__main__':
 D.mkdir(exist_ok=True)
 if len(sys.argv)>1:native();page()
 else:software_tree()
