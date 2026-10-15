"""Review assets from live resources, distinguishing software samples from native frames."""
import json,sys,math,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/steve-fighters-v25';A=R/'src/main/resources/assets/dynasty';sys.path.insert(0,str(R/'tools/art/boss-forms'))
import texture_review as v
F='/System/Library/Fonts/STHeiti Medium.ttc';font=lambda n:ImageFont.truetype(F,n)
def nonhuman():
 for id,name in [('carp_spirit','鲤鱼精'),('tree_spirit','树灵'),('clockwork_rat','机关鼠')]:
  dd=D/'nonhuman'/id;tex=np.array(Image.open(A/f'textures/entity/secondary/{id}.png'));q=v.r.geometry(id,geo_path=A/f'geo/secondary/{id}.geo.json',animation_path=A/f'animations/secondary/{id}.animation.json')
  pts=np.concatenate([x[0]for x in q]);right=np.array([math.cos(math.pi/4),0,math.sin(math.pi/4)]);refs=v.references(right*((pts@right).min()-24))
  for view,angle in [('front',0),('45',45),('side',90),('back',180)]:v.labelled(v.raster(q,tex,yaw=angle,mode='lit'),name+' / '+view+' / 软件逐面UV预览').save(dd/(view+'.png'))
  v.labelled(v.raster(q+refs,tex,mode='lit'),name+' / 玩家与原版尺寸参照（软件）').save(dd/'scale.png')
  # Geometry-only views cannot use the artwork as a substitute for structure.
  gray=np.full(tex.shape,168,dtype=np.uint8);black=np.zeros(tex.shape,dtype=np.uint8)
  for mode,t in [('gray',gray),('silhouette',black)]:v.labelled(v.raster(q,t,mode='lit'),name+' / '+mode+' 软件检查').save(dd/(mode+'.png'))
  before=v.r.geometry(id,geo_path=dd/'before.geo.json',animation_path=A/f'animations/secondary/{id}.animation.json');bt=np.array(Image.open(dd/'before.png').convert('RGB'))
  both=before+q;frame=np.concatenate([x[0]for x in both]);ims=[v.labelled(v.raster(before,bt,mode='lit',size=(800,700),frame_points=frame),name+' / 修改前'),v.labelled(v.raster(q,tex,mode='lit',size=(800,700),frame_points=frame),name+' / 修改后')]
  out=Image.new('RGB',(1600,780));out.paste(ims[0],(0,0));out.paste(ims[1],(800,0));out.save(dd/'comparison.png')
  # Complete existing motion timeline, sampled uniformly. No server/contact validation inferred.
  an=json.loads((A/f'animations/secondary/{id}.animation.json').read_text())['animations'];frames=[]
  for clip in ['idle','wander','attack','special']:
   end=an[clip]['animation_length']*20
   for n in range(12):
    qq=v.r.geometry(id,clip=clip,tick=end*n/11,geo_path=A/f'geo/secondary/{id}.geo.json',animation_path=A/f'animations/secondary/{id}.animation.json');frames.append(v.labelled(v.raster(qq,tex,mode='lit',size=(640,480)),name+' / '+clip+f' / {end*n/11:.1f} tick（软件）'))
  frames[0].save(dd/'motion.gif',save_all=True,append_images=frames[1:],duration=110,loop=0)

def native(batch):
 path=D/'native'/batch;targets=json.loads((D/'targets.json').read_text())+[{"id":id,"name":name}for id,name in [('carp_spirit','鲤鱼精'),('tree_spirit','树灵'),('clockwork_rat','机关鼠')]]
 overview=Image.new('RGB',(1700,math.ceil(len(targets)/5)*400),(235,237,229));d=ImageDraw.Draw(overview)
 for i,t in enumerate(targets):
  id,name=t['id'],t['name'];dd=D/id if i<14 else D/'nonhuman'/id;dd.mkdir(exist_ok=True)
  files=sorted(path.glob(f'*-{id}-front.png'))
  if not files:continue
  im=Image.open(files[0]);w,h=im.size
  # Same crop in every fixture: actual relative scale retained, no per-mob auto zoom.
  crop=(round(w*.29),round(h*.20),round(w*.68),round(h*.85));body=im.crop(crop);card=body.resize((340,360));overview.paste(card,((i%5)*340,(i//5)*400));d.text(((i%5)*340+12,(i//5)*400+365),name,font=font(22),fill=(35,43,42))
  for view in ['front','45','side','back','action']:
   pp=sorted(path.glob(f'*-{id}-{view}.png'))
   if pp:Image.open(pp[0]).crop(crop).save(dd/(view+'-game.png'))
  # Face and equipment crops use native pixels, no artificial image retouching.
  facebox={'carp_spirit':(.44,.53,.57,.73),'tree_spirit':(.44,.38,.57,.55),'clockwork_rat':(.44,.69,.57,.85)}.get(id,(.44,.26,.57,.47))
  im.crop(tuple(round(v*(w if j%2==0 else h))for j,v in enumerate(facebox))).save(dd/'face-game.png')
  frames=[]
  for fp in sorted((path/'frames'/id).glob('*.png')):frames.append(Image.open(fp).crop(crop).resize((680,round((crop[3]-crop[1])*680/(crop[2]-crop[0])))))
  if frames:frames[0].save(dd/'motion-game.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
 overview.save(D/'overview-game.jpg',quality=94)
 if (path/'PASS.txt').exists():
  # Raw full-resolution sequence frames remain disposable; deliver actual pixel crops/GIFs.
  import shutil
  if (path/'frames').exists():shutil.rmtree(path/'frames')

def page():
 targets=json.loads((D/'targets.json').read_text());cards=[]
 for t in targets+[{"id":id,"name":name,"nonhuman":True}for id,name in [('carp_spirit','鲤鱼精'),('tree_spirit','树灵'),('clockwork_rat','机关鼠')]]:
  id,name=t['id'],t['name'];prefix='nonhuman/'+id if t.get('nonhuman')else id
  imgs=''.join(f'<figure><img loading="lazy" src="{prefix}/{f}.png"><figcaption>{label}</figcaption></figure>'for f,label in [('front-game','正面·游戏'),('45-game','45度·游戏'),('side-game','侧面·游戏'),('back-game','背面·游戏'),('face-game','近景·游戏')])
  material_note={'carp_spirit':'参考 Cosmic Cod、Devil’s Pupfish、Mudskipper 与 Snapper 的鱼轴、独立鳍尾和口部；原创鲤鱼保留专用骨架与动作，重绘背鳞、腹色、须和尾鳍。','tree_spirit':'参考 Flutter 与 Leapleaf 的植物中心和外扩结构；保留树灵身份，用树干结眼、四处根支撑及错落枝叶建立植物结构。','clockwork_rat':'参考 Jerboa、Raccoon、Skunk、Sugar Glider 与 Squirrel 的水平身轴、耳吻与四足关系；木壳、黄铜、暗铁分区，原有尾与发条仍可动。'}.get(id,'保持标准史蒂夫六块主体和原版关节，以帽盔、眉鼻、甲袖、腰带和职业装备作小幅区别；普通战斗单位不新增领域或浮文。')
  extra=f'<p>{material_note}</p>'+ (f'<details><summary>同机位修改前后（软件）与灰模</summary><img loading="lazy" src="{prefix}/comparison.png"><div class="views"><img loading="lazy" src="{prefix}/gray.png"><img loading="lazy" src="{prefix}/silhouette.png"></div></details>'if t.get('nonhuman')else '')
  cards.append(f'<section><h2>{name} <small>dynasty:{id}</small></h2>{extra}<div class="views">{imgs}</div><details><summary>动作与实际PNG</summary><div class="views"><figure><img loading="lazy" src="{prefix}/motion-game.gif"><figcaption>静音实机时钟序列·AI关闭的美术场景</figcaption></figure><figure><img loading="lazy" src="{prefix}/texture-4x.png"><figcaption>原始PNG整数倍最近邻</figcaption></figure><figure><img loading="lazy" src="{prefix}/uv-overlay.png"><figcaption>UV岛检查图</figcaption></figure></div></details></section>')
 html='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>Dynasty：人形战斗单位与非人形小怪</title><style>body{background:#151c21;color:#e7e2d5;font:17px/1.65 system-ui;margin:32px auto;max-width:1500px}h1{font-size:28px}small{font-size:14px;color:#aab5b5}section{padding:20px 0;border-top:1px solid #3b474a}.views{display:flex;gap:12px;overflow-x:auto}figure{margin:0;min-width:260px;max-width:420px}img{width:100%;image-rendering:pixelated}a{color:#accdc2}summary{cursor:pointer}figcaption{font-size:14px}</style><h1>现有战斗单位美术改进</h1><p>14个人类持械单位：史蒂夫六块主体、小幅帽盔与装备强化。普通怪无新领域、浮文或气场。3个现有非人形单位：鱼体、根枝、木铜机关各自独立。</p><p>以下标“游戏”的画面来自静音隔离Forge场景，玩家和石砖为比例参照。动作序列使用实际使用物品与同步技能时钟，AI关闭；完整自然战斗、全部技能和多人观察仍待独立验证。</p><p><a href="nonhuman-references/index.html">100个非人形来源模型研究（灰模重建，含局限说明）</a> · <a href="native/fighters-v25-integrated/creative-inventory.json">创造栏实际顺序与刷怪蛋检查</a></p><img src="overview-game.jpg">'''+''.join(cards)+'</html>'
 (D/'index.html').write_text(html)
if __name__=='__main__':
 if len(sys.argv)>1:native(sys.argv[1]);page()
 else:nonhuman()
