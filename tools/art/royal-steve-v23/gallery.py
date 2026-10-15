"""Publish native evidence and editable assets; never label software renders as game captures."""
from pathlib import Path
import json,shutil,zipfile,re
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/royal-steve-v23';A=R/'src/main/resources/assets/dynasty'
N=R/'docs/art/boss-human-v12/native/royal-v23-final';B=N.parent/'royal-v23-before'
IDS=['dragon_king','dragon_emperor'];names=['东海龙王','龙帝']
assert 'PASS: 38' in (N/'PASS.txt').read_text()
for kind,source in [('native',N),('before-native',B)]:
 out=D/kind;out.mkdir(exist_ok=True)
 for f in source.iterdir():
  if f.is_file() and f.suffix in ('.png','.json','.txt'):shutil.copy2(f,out/f.name)
# All images below use the same crop at the same camera/lighting; full captures remain linked.
CROP=(560,340,2210,1480)
def screenshot(folder,index):return next(folder.glob(f'{index:02d}-*.png'))
def crop(path):return Image.open(path).convert('RGB').crop(CROP)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',30)
def panel(images,labels,path):
 out=Image.new('RGB',(sum(i.width for i in images),max(i.height for i in images)+64),'#17212a');draw=ImageDraw.Draw(out);x=0
 for im,label in zip(images,labels):out.paste(im,(x,64));draw.text((x+24,16),label,font=font,fill='#edf4f4');x+=im.width
 out.save(path)
for j,(id,name) in enumerate(zip(IDS,names)):
 for angle,offset in [('front',0),('45',2),('side',4),('back',6)]:
  panel([crop(screenshot(B,j*14+offset)),crop(screenshot(N,j*14+offset))],['修改前 · '+name,'修改后 · 同机位 / 无气场'],D/id/f'before-after-{angle}.png')
  panel([crop(screenshot(N,j*14+offset)),crop(screenshot(N,j*14+offset+1))],['关闭气场 · '+name,'开启气场 · 同机位 / 普通游戏光照'],D/id/f'aura-{angle}.png')
 frames=[crop(f).resize((1100,760),Image.Resampling.LANCZOS) for f in sorted((N/('sequence-'+id)).glob('*.png'))]
 assert len(frames)==24
 frames[0].save(D/id/'native-idle.webp',save_all=True,append_images=frames[1:],duration=200,loop=0,quality=88)
 # Software clips already cover complete idle/walk/attack/cast/hurt/death timelines.
 panel([crop(screenshot(N,j*14+i)) for i in [9,10,11]],['实机 · 蓄势 1 tick','实机 · 接触 3 tick','实机 · 回稳 5 tick'],D/id/'native-attack-phases.png')
panel([crop(screenshot(N,3)),crop(screenshot(N,17))],['东海龙王 · 潮带 / 三叉王兵','龙帝 · 帝剑 / 竖向赤金符流'],D/'overview.png')
# Executable game resources and editable sources, not a new game mod/package.
with zipfile.ZipFile(D/'royal-models.zip','w',zipfile.ZIP_DEFLATED) as z:
 for id in IDS:
  for folder,suffix in [('geo','.geo.json'),('animations','.animation.json'),('textures/entity','.png')]:
   f=A/folder/'boss_cuboid'/(id+suffix);z.write(f,'assets/dynasty/'+str(f.relative_to(A)))
  z.write(D/'blockbench'/(id+'.bbmodel'),'blockbench/'+id+'.bbmodel')
 for f in (R/'tools/art/royal-steve-v23').glob('*.py'):z.write(f,'source/'+f.name)
report={'direction':'用户已认可天将 V22：Steve 六主体块等比放大，小范围冠盔与甲片，大原创武器和细长符文；其余非人形保留专用结构。','scope':IDS,'height':'两只裸身2.7格，六主体块1.35倍，无独立放大脚掌。','unchanged':'注册ID、技能判定、碰撞、服务器逻辑、六段动画长度、已认可天将资源。','verified':['离线完整构建（跳过测试任务）','几何标准比例、逐面UV、贴图实际加载与归属哈希','每只19组实机状态，包括四视角气场开关、移动、攻击三个阶段、受伤、倒地、夜间、远处与低粒子设置','每只24帧实机气场循环、六段完整软件动画'], 'pending':['自然遭遇完整战斗与多人联机','用户对新造型的最终美术验收'],'reference':'沿用用户已认可的天将 V22 制作方法及此前已查看的灾变参考；本轮没有声称重新查看额外外部角色。','selfReview':'回看去除了龙帝胸前像字母的盘纹，改为角、首、盘身的原创像素簇；复查武器握持、落地、背面、同机位与玩家比例。'}
(D/'delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
parts=['''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>龙王与龙帝 · V23</title><style>body{margin:0;background:#101820;color:#e3eaee;font:17px/1.65 system-ui}main{max-width:1450px;margin:auto;padding:32px}h1,h2{color:#ead6a9}a{color:#94d6df}img{max-width:100%;display:block;background:#1b2530}figure{margin:16px 0}figcaption{color:#b7c4cc;font-size:15px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}.card{padding:18px;background:#19232d;border-radius:12px}summary{cursor:pointer;padding:10px;color:#c8dddb}.pixel{image-rendering:pixelated}nav{display:flex;gap:24px}section{margin:36px 0}small{color:#b1bfc7}</style><main><h1>东海龙王 / 龙帝 · 沿用认可的人形方向</h1><p>六主体块保持史蒂夫比例，整体1.35倍、裸身约2.7格。以小范围冠盔、不同的大武器、像素服制和两套气场区分身份。天将保持不变。</p><nav><a href="#dragon_king">东海龙王</a><a href="#dragon_emperor">龙帝</a><a href="#checks">验证与资源</a></nav><figure><a href="overview.png"><img src="overview.png"></a><figcaption>真实游戏截图；同距离8格、普通日间光照，玩家与石砖作参照。没有套宣传滤镜。</figcaption></figure>''']
def fig(src,label,cls=''):return f'<figure><a href="{src}"><img loading="lazy" class="{cls}" src="{src}"></a><figcaption>{label}（点击原图）</figcaption></figure>'
for j,(id,name) in enumerate(zip(IDS,names)):
 desc='小龙角、浅须髯与海玉胸饰；青碧衣料和冷银甲，长柄三叉潮汐王兵。气场横向绕身，低位水带、两侧上卷潮流与钩形细符文。' if j==0 else '低帝冕、封闭金面与暗朱服制；阔刃帝剑和左手玉玺。气场从背后向上升起，赤金光带、断续侧光与竖排分枝细符文。'
 parts.append(f'<section id="{id}"><h2>{name}</h2><p>{desc}</p>'+fig(f'{id}/native-idle.webp','实机连续待机 / 气场运动，24帧')+fig(f'{id}/before-after-front.png','同机位修改前后 · 关闭气场')+fig(f'{id}/aura-45.png','45度 · 气场关闭 / 开启'))
 parts.append('<details><summary>正面、侧面、背面与更多前后对照</summary>')
 for angle in ['front','side','back']:parts.append(fig(f'{id}/aura-{angle}.png',angle+' · 真实游戏画面'))
 for angle in ['45','side','back']:parts.append(fig(f'{id}/before-after-{angle}.png',angle+' · 前后对照'))
 parts.append('</details>'+fig(f'{id}/native-attack-phases.png','实机攻击三个阶段；服务器时间轴未改'))
 parts.append('<details><summary>原色贴图、近景、UV、完整软件动画</summary><p>以下为逐面使用真实 PNG 的软件检查图，不是游戏截图。UV检查纹理仅用于检查，不进入正式资源。</p><div class="grid">')
 for file,label in [('front-unlit.png','原色 / 正面'),('45-unlit.png','原色 / 45度'),('close-face.png','面部近景'),('close-chest.png','胸甲近景'),('close-weapon.png','武器近景'),('player-scale.png','比例检查'),('texture.png','原始256×256图集'),('texture-4x.png','整数4倍最近邻'),('uv-overlay-4x.png','UV岛叠加'),('uv-direction.png','方向检查')]:parts.append(fig(id+'/'+file,label,'pixel' if 'texture' in file else ''))
 parts.append('</div><div class="grid">')
 for clip in ['idle','walk','attack','cast','hurt','death']:parts.append(fig(id+'/'+clip+'.webp','完整软件动画 · '+clip))
 parts.append('</div></details><details><summary>原始游戏画面与状态记录</summary>')
 for f in sorted(N.glob('*-'+id+'-*.png')):
  num=f.name.split('-')[0];parts.append(f'<p><a href="native/{f.name}">{f.stem}</a> · <a href="native/{num}-state.json">加载/姿态记录</a></p>')
 parts.append(f'</details><a href="blockbench/{id}.bbmodel">可编辑 Blockbench 源文件</a></section>')
parts.append('''<section id="checks"><h2>检查与资源</h2><p>构建通过；两只共38组实机状态通过。完整软件动画与实机三个攻击阶段分别提供，不把静态截图冒充全程动作录像。自然遭遇完整战斗及多人联机仍待验证。</p><p>源文件、PNG、逐面UV与导出源同步更新；导出带归属检查，避免覆盖手动或并行修改。未复制外部资产，未修改战斗数值或碰撞。</p><p><a href="royal-models.zip">下载两套实际资源与可编辑源文件</a> · <a href="asset-validation.json">比例/UV/时间轴检查</a> · <a href="native/PASS.txt">38组实机检查</a> · <a href="native/runtime-manifest.json">实机资源哈希</a> · <a href="delivery.json">交付记录</a></p><p>另已检查人形渲染绑定：兵马俑战士、大臣、刺客、玉甲卫、冥卒、雷使、鲛人仍有后续逐只审视空间；这里只确认绑定，没有据此判定每只都需要重做，本轮先完成龙王与龙帝。</p></section></main></html>''')
(D/'index.html').write_text(''.join(parts))
for ref in re.findall(r'(?:src|href)="([^"]+)"',''.join(parts)):
 if not ref.startswith('#'):assert (D/ref).exists(),ref
print('Gallery ready; local links and 38-state evidence checked.')
