"""Publish reproducible review artifacts; never write gameplay or another checkout."""
from refine import *
import shutil,sys,html

NOTES={
'gudu_tianzhunv':('暮色甲虫、Alex多足虫的前后分区','去掉大白色人形胸块；胸腹连成蛛壳，腿端收尖，腹纹顺腹背排列。保留原有仪式面具身份。'),
'yinyang_liandan_fangshi':('暮色Death Tome的器物主体与薄附件关系','保持真实空炉腔，简化炉肩与盖，面具用眼窝和下颌分区，铜与内铁、瓷面分开。'),
'fubo_xunhai_yecha':('Alex龙虾/螳螂虾、暮色甲虫','后甲盾与低头部相接；六足改为斜向节肢，去平底靴，口器与眼柄独立。'),
'banshan_jiazhou_shikuang':('Alex灰熊/猿类的前肢承重','棺移回背部既有上方体量；肩胸、头口露出，前拳减去底座感，棺木与尸身分清。'),
'mojia_jueying_cike':('Alex鳐形/扁体生物与Cobblemon薄翼结构','墨翼连成薄膜，躯体压低，去竹橇色底座，前缘成对眼斑与尾鳍有方向；匕首挂架保留。'),
'hanshan_tongjia_juyuan':('Alex Gorilla实际灰模与原始PNG','毛皮成为身体主体，铜仅保留护片；重画眉、鼻口、顺向毛簇，收后脚。检查并修正眼块被口鼻埋住的问题。'),
'qingdeng_panguan_guichai':('暮色Death Tome的薄书页与活化书识别','厚铁柜改为薄书封与页层，独眼为主；墨盂缩小，紫封、纸页、青灯各有明度。'),
'liefeng_jindiao_yushi':('Alex Bald Eagle实际原始PNG、暮色Raven体块','胸、背、颈连贯，减少重复翅条；淡颈深背、羽片分组，钩喙与眼清晰，爪持弓不动。'),
'zhenmu_suanni_tonghou':('Alex猫科口鼻、Cobblemon狮形鬃部的大形组织','方框鬃简化成阶梯鬃块，鼻口与眼窝形成兽脸；中空铸铜炉腹及原有球足保持。')}

def research(source):
 src=Path(source);dest=D/'references';dest.mkdir(parents=True,exist_ok=True)
 records=json.loads((src/'manifest.json').read_text());assert len(records)==1000
 ledger=json.loads((R/'docs/art/steve-fighters-v25/nonhuman-references/ledger.json').read_text())
 lookup={v['image']:v for v in ledger};jarhash=hashlib.sha256((src.parent/'cobblemon-reference.jar').read_bytes()).hexdigest()
 for i,v in enumerate(records):
  v['sheet']='sheet-%02d.png'%(i//20+1);v['positionInSheet']=i%20+1
  v['visuallyReviewed']='static gray source structure only; no runtime animation/texture claim'
  if i<100:
   original=lookup[Path(v['image']).name];v.update(source=original['source'],sha256=original['sha256'],commit=original['commit'])
  else:v.update(download='https://cdn.modrinth.com/data/MdwFAVRL/versions/GJ2a1b8O/Cobblemon-fabric-1.8.2%2B1.21.1.jar',project='https://modrinth.com/mod/cobblemon',version='1.8.2',jarSha256=jarhash)
  v.pop('image',None)
 for f in src.glob('sheet-*.png'):shutil.copy2(f,dest/f.name)
 (dest/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 rows=''.join('<details><summary>第%d–%d个</summary><a href="sheet-%02d.png"><img loading="lazy" src="sheet-%02d.png"></a><p>%s</p></details>'%(i*20+1,(i+1)*20,i+1,i+1,' · '.join(html.escape(v['name'])for v in records[i*20:(i+1)*20]))for i in range(50))
 (dest/'index.html').write_text('''<!doctype html><html lang="zh"><meta charset="utf-8"><title>1000个结构样本</title><style>body{max-width:1280px;margin:40px auto;padding:20px;background:#e4e8e0;color:#20352f;font:17px/1.7 system-ui}img{width:100%}details{padding:14px;border-bottom:1px solid #aab5ab}a{color:#326558}</style><h1>1000个生物结构样本</h1><p>83个Alex’s Mobs、14个暮色森林、3个Goety，另有900个Cobblemon不同物种文件夹的实际模型。50张联系表已逐张查看。这里是源码/geo的静态灰模总览，未还原全部动画、透明裁切、运行缩放与贴图；不是1000段实机观察。细杆、薄面和分离附件在绑定姿态下可能失真。广泛比较体块方法，不照搬宝可梦题材。</p><p>直接用于本批的是节肢、猿、猛禽、猫科与活化书相关结构。另实际查看Alex的gorilla、蓝龙虾、螳螂虾、白头鹰原始PNG，学习毛、甲壳和淡颈深背的像素组织，未复制纹理。</p><p><a href="manifest.json">逐项来源、版本、哈希和限制</a> · <a href="https://www.curseforge.com/minecraft/mc-mods/alexs-mobs/gallery">Alex作者展示</a> · <a href="https://modrinth.com/mod/cobblemon">Cobblemon官方项目</a> · <a href="../index.html">返回本批修改</a></p>'''+rows+'</html>')

def native(name):
 n=D/'native'/name;assert(n/'PASS.txt').exists()
 manifest=json.loads((n/'runtime-manifest.json').read_text())
 for rel,h in manifest['resources'].items():assert hashlib.sha256((R/'src/main/resources'/rel).read_bytes()).hexdigest()==h,rel
 for i,id in enumerate(SPECS):
  d=D/id
  for j,(view,label)in enumerate([('front','front'),('45','45'),('side','side'),('back','back'),('action','contact')]):shutil.copy2(n/f'{i*5+j:02d}-{id}-{view}.png',d/f'native-{label}.png')
  ticks=[];frames=[]
  for f in sorted((n/'frames'/id).glob('*.png')):
   im=Image.open(f).convert('RGB');im=im.resize((im.width//2,im.height//2),Image.Resampling.NEAREST);frames.append(im);ticks.append(int(f.stem))
  assert ticks[-1]==144 and len(ticks)>=25
  durations=[(b-a)*50 for a,b in zip(ticks,ticks[1:])]+[200]
  frames[0].save(d/'native-action.webp',save_all=True,append_images=frames[1:],duration=durations,loop=0,lossless=True)
  before=R/'docs/art/cod1-creatures-v32'/id/'native-45.png'
  if before.exists():
   a=Image.open(before).convert('RGB');b=Image.open(d/'native-45.png').convert('RGB');assert a.size==b.size
   out=Image.new('RGB',(a.width*2,a.height));out.paste(a);out.paste(b,(a.width,0));out.save(d/'native-comparison.png')
 for f in ['PASS.txt','progress.txt','runtime-manifest.json']:shutil.copy2(n/f,D/('native-'+f))
 report={'build':'PASS: Forge47.4.10 / GeckoLib4.8.4 / JDK17, build -x test','unitTests':'not run (-x test)','native':'45 renderer/texture views plus 9 existing synchronized skill sequences through144 ticks; fixture AI disabled, explicitly grounded. Not natural combat or multiplayer certification.','sourceRoundtrip':'9 authoritative exporters reproduce all55 scoped files byte-for-byte','geometry':'Original anatomy/connected masses changed; existing bone hierarchy, pivots, rotations and animation bytes preserved','weapons':'unchanged geometry, UV and legacy pixels; delegated to another conversation','references':'1000 static source model overview, 50 contact sheets actually viewed; related species studied for anatomy. No claim1000 textured full gameplay reviews.','limitations':'Collision, hitbox, natural AI gait/death, network and complete cod1 gameplay still require their own validation. This is art work, not completion of all cod1.','sound':'Muted disposable fixture; existing user save and sound/brightness preferences untouched','selfReviewFixes':['diagonal appendages replace boot blocks','corpse head exposed instead cabinet front','ape eyes moved in front of muzzle occluder','directional material clusters replace large flat surfaces']}
 (D/'completion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

def gallery():
 from PIL import ImageFont
 if all((D/id/'native-45.png').exists()for id in SPECS):
  sheet=Image.new('RGB',(1920,1380),'#e6e9e2');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',23)
  for i,(id,v)in enumerate(SPECS.items()):
   # Identical crop/scale for every creature; full uncropped views remain linked below.
   im=Image.open(D/id/'native-45.png').convert('RGB');w,h=im.size;im=im.crop((int(w*.12),int(h*.15),int(w*.88),int(h*.92)));im.thumbnail((640,420),Image.Resampling.NEAREST);x=i%3*640;y=i//3*460;sheet.paste(im,(x+(640-im.width)//2,y+40));draw.text((x+12,y+7),v[0],font=font,fill='#243c31')
  sheet.save(D/'native-overview.png')
 head='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Dynasty 生物结构 V33</title><style>body{margin:0;background:#e6e9e2;color:#20352e;font:17px/1.6 system-ui}header,main{max-width:1480px;margin:auto;padding:28px}h1{font-size:38px;margin:10px 0}h2{margin:0}nav{display:flex;gap:10px;flex-wrap:wrap}a{color:#326254}nav a,button{border:1px solid #9aab9b;border-radius:18px;padding:7px 14px;background:#f2f3ed;text-decoration:none;color:#274f41;cursor:pointer}section{background:#f4f4ee;border-radius:14px;padding:24px;margin:26px 0;scroll-margin-top:20px}img{display:block;width:100%;height:auto;image-rendering:pixelated}figure{margin:8px 0}figcaption{font-size:14px;color:#52655a}small{color:#647568}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.full{grid-column:1/-1}details{padding:15px 0;border-top:1px solid #c8d0c5}summary{cursor:pointer}code{font-size:13px}button[aria-pressed=true]{background:#304f40;color:white}@media(max-width:800px){.grid{grid-template-columns:1fr}} </style><header><small>DYNASTY / 生物形体与像素材质 / V33</small><h1>让结构读成生物</h1><p>修正九只现有精英的箱壳、平底足与断开的主体关系。不是新增物种；ID、技能、既有动作与武器保留。左图V32，右图V33；同机位、同尺度比较。</p><p><a href="references/index.html">1000个实际结构样本与研究边界</a> · <a href="completion.json">验证范围</a> · <a href="verification.json">UV、骨架与动画检查</a></p><nav>'''
 chunks=[head+''.join(f'<a href="#{id}">{v[0]}</a>'for id,v in SPECS.items())+'</nav></header><main>']
 if(D/'native-overview.png').exists():chunks.append('<figure><a href="native-overview.png"><img src="native-overview.png"></a><figcaption>实际游戏总览：全部相同裁切、相同比例；每只完整原图和对比在下方。</figcaption></figure>')
 for id,v in SPECS.items():
  d=D/id;ref,note=NOTES[id]
  native_ok=(d/'native-45.png').exists()
  primary='native-45.png'if native_ok else '45.png'
  comparison='native-comparison.png'if(d/'native-comparison.png').exists()else'comparison.png'
  views=['native-'+s+'.png'for s in ['front','45','side','back','contact']]if native_ok else[s+'.png'for s in ['front','45','side','back']]
  chunks.append(f'<section id="{id}"><h2>{v[0]}</h2><small>dynasty:{id}</small><p>{note}</p><p><small>实际借鉴：{ref}。不使用参考网格或像素。</small></p><figure><img loading="lazy" src="{id}/{comparison}"><figcaption>左：修改前　右：修改后 / '+('实际Forge渲染截图，同条件'if comparison.startswith('native')else'逐面UV软件预览，同条件')+'</figcaption></figure>')
  chunks.append('<div class="grid">'+''.join(f'<figure><a href="{id}/{f}"><img loading="lazy" src="{id}/{f}"></a><figcaption>{f} / '+('实机固定场景'if f.startswith('native')else'软件预览')+'</figcaption></figure>'for f in views)+'</div>')
  if native_ok:chunks.append(f'<details><summary>完整技能实机序列 / 0–144 tick</summary><img loading="lazy" src="{id}/native-action.webp"><p>现有同步技能；AI关闭的固定场景，不冒充自然战斗。截图逐4 tick采样，WebP半尺寸最近邻。</p></details>')
  clips=[p.name for p in d.glob('*.webp')if not p.name.startswith('native')]
  chunks.append('<details><summary>原色、灰度、剪影、PNG和完整软件动作</summary><div class="grid">'+''.join(f'<figure><a href="{id}/{f}"><img loading="lazy" src="{id}/{f}"></a><figcaption>{f} / 软件与源图</figcaption></figure>'for f in ['unlit.png','gray.png','silhouette.png','texture-2x.png',*clips])+'</div></details></section>')
 chunks.append('</main></html>');(D/'index.html').write_text(''.join(chunks))

if __name__=='__main__':
 if '--references'in sys.argv:research(sys.argv[sys.argv.index('--references')+1])
 if '--native'in sys.argv:native(sys.argv[sys.argv.index('--native')+1])
 gallery()
