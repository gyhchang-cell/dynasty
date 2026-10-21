"""Publish actual before/after views; candidate research is never counted as inspected models."""
from refine import *
import shutil,html,sys
from PIL import ImageFont
NOTES={
'gudu_tianzhunv':('Alex TarantulaHawk、暮色 HelmetCrab','胸腹取消叠盖；八足根部进入胸壳，近端、膝段、末端逐级收细，保留仪式面具。'),
'yinyang_liandan_fangshi':('暮色 DeathTome 的器物活化主次；非照搬其身体','炉肩内收、底托合并，三足从炉体向外承接，再收为细踝；保留空炉腔和面具，不改成动物。'),
'fubo_xunhai_yecha':('Alex Lobster / Triops、暮色 HelmetCrab / PinchBeetle','多层平台合成一个背盾；腹部内嵌，六足从壳下接出并收细，脚端去底座。'),
'banshan_jiazhou_shikuang':('Alex Gorilla / Tiger 的胸肩、髋部与四肢连接','棺保留；胸肩前压，前臂从肩内接出、逐段收细，后腿由髋部斜向支撑；修复头块遮眼。'),
'mojia_jueying_cike':('Alex Triops 的薄躯体和前后方向；非鳐鱼源码研究','主体收为薄长躯，膜翼从侧面接出并向外倾，取消厚叠板；匕首和挂架不改。'),
'hanshan_tongjia_juyuan':('Alex Gorilla 源码与作者实际游戏展示','多块方胸并成前压胸背；肩根嵌入胸体，肘腕收细，短后腿连接髋部；限制铜片，毛面不再棋盘化。'),
'qingdeng_panguan_guichai':('暮色 DeathTome 的薄封面、书页和共同翻转轴','书封、页块统一轴线展开，去厚底框；脊骨收窄，书页不再像两块并排柜门。'),
'liefeng_jindiao_yushi':('Alex BaldEagle 源码、暮色 Raven','胸背合并并倾斜，颈嵌入前胸，头喙收紧；翅膀改薄翼与有限初级羽，尾羽变薄，保留持弓。'),
'zhenmu_suanni_tonghou':('Alex Tiger / SnowLeopard 的头肩与前后腿承接','炉腹保持真实开口，背梁改斜拱、侧面取消重复横框；颈胸连贯、前后肢粗细有别，保留原铜球足。')}

def references():
 dst=D/'references';dst.mkdir(parents=True,exist_ok=True)
 src=R/'docs/art/steve-fighters-v25/nonhuman-references';records=json.loads((src/'ledger.json').read_text());names={'Gorilla','BaldEagle','Lobster','MantisShrimp','Triops','TarantulaHawk','DeathTome','HelmetCrab','PinchBeetle','Raven','SnowLeopard','Tiger'}
 chosen=[v for v in records if v['identity']in names]
 for v in chosen:
  shutil.copy2(src/v['image'],dst/v['image']);v['reviewScope']='Actual source-derived bind-pose reconstruction viewed. No claim of full gameplay review.'
 (dst/'reviewed.json').write_text(json.dumps(chosen,ensure_ascii=False,indent=2)+'\n')
 # These images have been viewed this turn. Kept as documentary thumbnails, never runtime textures.
 for f in ['relevant-references.png','author-displays.png']:
  srcf=Path('/Users/a15356015027/Desktop/dynasty/build/creature-mc-v34')/f
  if srcf.exists():shutil.copy2(srcf,dst/f)
 rows=''.join(f'<p><a href="{v["source"]}">{v["mod"]}: {v["identity"]}</a> — 源码绑定姿态，不能替代完整动画研究。</p>' for v in chosen)
 (dst/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>V34实际参考记录</title><style>body{max-width:1200px;margin:35px auto;font:17px/1.7 system-ui;background:#e8ece4}img{max-width:100%}</style><h1>本次实际查看的参考</h1><p>12个暮色森林/Alex模型结构重建，核对Gorilla、BaldEagle、Lobster、HelmetCrab、DeathTome源码，另查看Alex作者Gorilla/Lobster/Tiger游戏展示。作者截图可能有光影，只用于构造与部位关系；未作为无光照PNG效果。</p><img src="relevant-references.png"><img src="author-displays.png">'+rows+'<p><a href="https://www.curseforge.com/minecraft/mc-mods/alexs-mobs/gallery">Alex作者展示来源</a> · <a href="reviewed.json">逐项来源与版本</a></p><p>用户要求的100个主流整合包/1000个不同非人形生物尚未完成逐项图像研究。候选包检索不等于参考过其中的生物；不将宝可梦、同一生物多包收录或未查看资产补入计数。</p><a href="../index.html">返回模型</a>')

def native(base,focused):
 n=D/'native'/base;fixed=D/'native'/focused
 assert(n/'PASS.txt').exists() and(fixed/'PASS.txt').exists()
 manifest=json.loads((fixed/'runtime-manifest.json').read_text());base_manifest=json.loads((n/'runtime-manifest.json').read_text())
 for rel,h in manifest['resources'].items():
  assert hashlib.sha256((R/'src/main/resources'/rel).read_bytes()).hexdigest()==h,rel
  if 'banshan_jiazhou_shikuang'not in rel:assert base_manifest['resources'][rel]==h
 for i,id in enumerate(SPECS):
  src=fixed if id=='banshan_jiazhou_shikuang'else n;d=D/id
  for j,(view,label)in enumerate([('front','front'),('45','45'),('side','side'),('back','back'),('action','contact')]):shutil.copy2(src/f'{i*5+j:02d}-{id}-{view}.png',d/f'native-{label}.png')
  frames=[];ticks=[]
  for f in sorted((src/'frames'/id).glob('*.png')):
   im=Image.open(f).convert('RGB');im=im.resize((im.width//2,im.height//2),Image.Resampling.NEAREST);frames.append(im);ticks.append(int(f.stem))
  assert ticks[-1]==144 and len(ticks)>=25
  frames[0].save(d/'native-action.webp',save_all=True,append_images=frames[1:],duration=[(b-a)*50 for a,b in zip(ticks,ticks[1:])]+[200],loop=0,lossless=True)
  a=Image.open(R/'docs/art/creature-mc-v33'/id/'native-45.png').convert('RGB');b=Image.open(d/'native-45.png').convert('RGB');assert a.size==b.size
  out=Image.new('RGB',(a.width*2,a.height));out.paste(a);out.paste(b,(a.width,0));out.save(d/'native-comparison.png')
 (D/'runtime-manifest.json').write_text(json.dumps(manifest,indent=2))
 (D/'native-checks.json').write_text(json.dumps({'base':{'fixture':base,'result':(n/'PASS.txt').read_text().splitlines()[-1]},'eyeOcclusionCorrection':{'fixture':focused,'result':(fixed/'PASS.txt').read_text().splitlines()[-1]},'scope':'AI disabled, grounded, existing synchronized skills. Natural AI combat, multiplayer and natural death transitions are not certified.'},ensure_ascii=False,indent=2))

def gallery():
 font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',23);sheet=Image.new('RGB',(1920,1380),'#e6e9e2');draw=ImageDraw.Draw(sheet)
 for i,(id,v)in enumerate(SPECS.items()):
  d=D/id;im=Image.open(d/'native-45.png').convert('RGB');w,h=im.size;im=im.crop((int(w*.12),int(h*.15),int(w*.88),int(h*.92)));im.thumbnail((640,420),Image.Resampling.NEAREST);x=i%3*640;y=i//3*460;sheet.paste(im,(x+(640-im.width)//2,y+40));draw.text((x+12,y+7),v[0],font=font,fill='#243c31')
 sheet.save(D/'native-overview.png')
 head='<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Dynasty V34 · 主体与关节</title><style>body{margin:30px auto;max-width:1500px;padding:20px;background:#e6e9e2;color:#243d33;font:17px/1.6 system-ui}img{max-width:100%;image-rendering:pixelated}section{padding:25px;background:#f6f5ed;margin:30px 0;border-radius:16px}a{color:#296754}.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}nav{display:flex;gap:15px;flex-wrap:wrap}figure{margin:0}small,figcaption{color:#52685b}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>V34 · 主体、头部与四肢连接</h1><p>本轮处理叠箱胸背、外接头块、粗细相同的肢段与厚板翼。保留九只身份、武器、骨架和原有动作时间轴。</p><p><a href="references/index.html">实际参考与尚未完成的研究范围</a> · <a href="verification.json">骨架/武器/UV检查</a> · <a href="native-checks.json">实机检查范围</a></p><p>左V33、右V34，同机位同尺度。以下实机为静音独立测试场景，不是用户存档；技能为AI关闭的同步动作检查，不能替代自然战斗和多人测试。</p><nav>'
 chunks=[head+''.join(f'<a href="#{id}">{v[0]}</a>'for id,v in SPECS.items())+'</nav><img src="native-overview.png">']
 for id,v in SPECS.items():
  ref,note=NOTES[id];d=D/id
  chunks.append(f'<section id="{id}"><h2>{v[0]}</h2><small>dynasty:{id}</small><p>{note}</p><p>参考：{ref}。未复制外部网格、PNG或动作。</p><a href="{id}/native-comparison.png"><img loading="lazy" src="{id}/native-comparison.png"></a><p>左修改前，右修改后 / 实机同条件</p><div class="grid">')
  for view in ['front','45','side','back','contact']:
   chunks.append(f'<figure><a href="{id}/native-{view}.png"><img loading="lazy" src="{id}/native-{view}.png"></a><figcaption>{view} / 原始Forge截图</figcaption></figure>')
  chunks.append(f'</div><details><summary>完整代表技能 0–144 tick</summary><img loading="lazy" src="{id}/native-action.webp"></details><details><summary>软件原色、灰度、剪影与贴图</summary><div class="grid">')
  for name in ['clay.png','unlit.png','gray.png','silhouette.png','texture-2x.png','uv-overlay.png']:
   chunks.append(f'<figure><img loading="lazy" src="{id}/{name}"><figcaption>{name} / 软件与源图，不是游戏截图</figcaption></figure>')
  chunks.append('</div></details></section>')
 chunks.append('</html>');(D/'index.html').write_text(''.join(chunks))
if __name__=='__main__':
 references()
 if len(sys.argv)>2:native(sys.argv[1],sys.argv[2]);gallery()
