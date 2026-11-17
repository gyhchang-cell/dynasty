"""Publish evidence without claiming static source inspection is gameplay review."""
from refine import *
import shutil,html,sys
from PIL import ImageFont
NOTES={
'gudu_tianzhunv':'完整胸腹与细足分级；去掉生物腿上的重复箍纹，腹纹跨相邻体块连续。保留天蛛女面具身份。',
'yinyang_liandan_fangshi':'炉体和底托连成一体，减少层层方盖；面具贴近炉口，铜器下缘的氧化集中于接合处。',
'fubo_xunhai_yecha':'背壳由平板改为有厚度的中央甲壳和收窄尾缘；眼柄从甲壳前缘长出，腹口不再挂着大白板。',
'banshan_jiazhou_shikuang':'胸肩与前臂衔接收紧，拳和腕逐级收细；束尸布减薄，残躯和棺木保持区别。',
'mojia_jueying_cike':'墨翼从矩形叠板改为向外收尖、轻微折起的连续膜翼；眼点置于头背，保留匕首挂点。',
'hanshan_tongjia_juyuan':'肩根进入胸腔、肘腕收细；背甲减薄，取消手腕厚铜箍；黑毛与银背分区连续，不再与尸狂同色。',
'qingdeng_panguan_guichai':'书页靠近书脊、封面减薄，独眼收回书身；墨迹沿页栏排列，不把每页画成柜门。',
'liefeng_jindiao_yushi':'颈根连入胸背、翼根内厚外薄；胸腹淡羽与背部深羽分区，飞羽沿翼展方向排列。持弓和技能时间轴保留。',
'zhenmu_suanni_tonghou':'补足前躯和后胯连接，缩小过大的侧窗并保留炉腔；铜壳、暗铁内层和下缘铜锈分区，保留原铜球足。'}
REFS={
'gudu_tianzhunv':'Alex TarantulaHawk；暮色 HelmetCrab（胸腹、节肢连接）',
'yinyang_liandan_fangshi':'暮色 DeathTome（器物活化的主体与附属关系）',
'fubo_xunhai_yecha':'Alex Lobster、Triops；暮色 HelmetCrab（壳下肢根、眼柄、轴向尾部）',
'banshan_jiazhou_shikuang':'Alex Gorilla、Tiger（肩胯承接与前后肢重量差）',
'mojia_jueying_cike':'Alex Spectre、Triops（薄躯干、外收膜面和前后方向）',
'hanshan_tongjia_juyuan':'Alex Gorilla 源码结构及作者游戏展示（连贯胸背与毛色分区）',
'qingdeng_panguan_guichai':'暮色 DeathTome（薄页片和共同书脊）',
'liefeng_jindiao_yushi':'Alex BaldEagle；暮色 Raven（头颈和薄翼）',
'zhenmu_suanni_tonghou':'Alex Tiger、SnowLeopard（肩、胸、后胯连接）'}
def research():
 ledger=json.loads((D/'reference-ledger.json').read_text());dest=D/'references';dest.mkdir(exist_ok=True);parts=[]
 for i,(k,v) in enumerate((kv for kv in ledger.items()if kv[1].get('accepted')),1):
  src=Path(v['image']);src=src if src.is_absolute() else D/src;out=dest/src.name
  if src.resolve()!=out.resolve():shutil.copy2(src,out)
  v['image']='references/'+src.name
  parts.append(f'<article><h3>{i}. {html.escape(k)}</h3><img loading="lazy" src="{html.escape(src.name)}"><p>{html.escape(v.get("observation",""))}</p><a href="{html.escape(v["source"])}">固定版本源码</a></article>')
 assert len(parts)==1000
 (D/'reference-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
 intro='<h1>1000个非人形结构参考 / 27个模组源码库</h1><p>逐项静态源码重建图：45度与侧面。排除同几何重复、普通人形和不完整组合体；没有宝可梦。不同卡片独立取景，不用于比较实机体型。透明面片未还原贴图轮廓，动画和动态装配不在这1000项检查范围内。</p><p>这是1000个模型结构参考，不是1000次实机测试；尚未完成100个主流整合包的收录核对。并非所有参考都值得照做，笔记中保留了反例。</p><p>外部源模型与像素未导入Dynasty运行资源。</p><a href="../index.html">返回修改结果</a>'
 (dest/'index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{font:16px/1.6 system-ui;max-width:1300px;margin:30px auto;background:#e8ebe5}main{display:grid;grid-template-columns:1fr 1fr;gap:20px}article{background:white;padding:14px}img{max-width:100%}</style>'+intro+'<main>'+''.join(parts)+'</main>')
def publish(run):
 n=D/'native'/run;assert(n/'PASS.txt').exists();manifest=json.loads((n/'runtime-manifest.json').read_text())
 for rel,h in manifest['resources'].items():assert hashlib.sha256((R/'src/main/resources'/rel).read_bytes()).hexdigest()==h,rel
 font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',23);sheet=Image.new('RGB',(1920,1380),'#e6e9e2');dr=ImageDraw.Draw(sheet)
 evidence={}
 for i,(id,spec)in enumerate(SPECS.items()):
  d=D/id
  for j,view in enumerate(['front','45','side','back','action']):shutil.copy2(n/f'{i*5+j:02d}-{id}-{view}.png',d/f'native-{view}.png')
  a=Image.open(R/'docs/art/creature-mc-v34'/id/'native-45.png').convert('RGB');b=Image.open(d/'native-45.png').convert('RGB');assert a.size==b.size
  pair=Image.new('RGB',(a.width*2,a.height));pair.paste(a);pair.paste(b,(a.width,0));pair.save(d/'native-comparison.png')
  frames=[];ticks=[]
  for f in sorted((n/'frames'/id).glob('*.png')):
   im=Image.open(f).convert('RGB');frames.append(im.resize((im.width//2,im.height//2),Image.Resampling.NEAREST));ticks.append(int(f.stem))
  assert ticks[0]==0 and ticks[-1]==144 and len(ticks)>=18
  frames[0].save(d/'native-action.webp',save_all=True,append_images=frames[1:],duration=[(b-a)*50 for a,b in zip(ticks,ticks[1:])]+[200],loop=0,lossless=True)
  evidence[id]={'sampledTicks':ticks,'geometryAndPNGMatchLaunchManifest':True}
  x=i%3*640;y=i//3*460;bw,bh=b.size;thumb=b.crop((int(bw*.12),int(bh*.15),int(bw*.88),int(bh*.92)));thumb.thumbnail((640,420),Image.Resampling.NEAREST);sheet.paste(thumb,(x+(640-thumb.width)//2,y+40));dr.text((x+12,y+6),spec[0],font=font,fill='#243d33')
  overlay=Image.open(d/'texture.png').convert('RGB');draw=ImageDraw.Draw(overlay)
  for v in json.loads((d/'islands.json').read_text()):
   x0,y0,w,h=v['rect'];draw.rectangle((x0,y0,x0+w-1,y0+h-1),outline=(220,65,150))
  overlay.resize((overlay.width*3,overlay.height*3),Image.Resampling.NEAREST).save(d/'uv-overlay.png')
 sheet.save(D/'native-overview.png');(D/'runtime-manifest.json').write_text(json.dumps(manifest,indent=2));(D/'native-checks.json').write_text(json.dumps({'fixture':run,'result':(n/'PASS.txt').read_text(),'scope':'Actual Forge renderer and existing synchronized skill. AI disabled, grounded. Natural AI/death/multiplayer not certified.','entities':evidence},indent=2))
 chunks=['<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Dynasty V35 · 生物连接与像素分区</title><style>body{margin:25px auto;max-width:1600px;padding:20px;background:#e6e9e2;color:#243d33;font:17px/1.6 system-ui}img{max-width:100%;image-rendering:pixelated}section{padding:24px;background:#f6f5ed;margin:28px 0;border-radius:14px}a{color:#296754}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}nav{display:flex;gap:16px;flex-wrap:wrap}figure{margin:0}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>V35 · 当前9只生物的连接与表面修正</h1><p>主要修正平板背壳、叠箱式肩肘、空架腹部、厚翼根与互相割裂的材质。保留注册身份、武器、骨架层级、技能时间轴与碰撞。</p><p><a href="references/index.html">1000个结构参考、笔记与研究限制</a> · <a href="verification.json">资源检查</a> · <a href="native-checks.json">实机检查范围</a></p><p>以下为真实Forge截图：相同测试场景、机位、玩家比例及光照。对照左V34右V35。没有把软件预览冒充实机。</p><p>这页交付的是当前9只精英；不能据此宣称仓库所有怪物已经全部改完。此前已认可最终Boss及其他对话正在修改的资源未覆盖。</p><nav>'+''.join(f'<a href="#{id}">{s[0]}</a>'for id,s in SPECS.items())+'</nav><img src="native-overview.png">']
 for id,spec in SPECS.items():
  chunks.append(f'<section id="{id}"><h2>{spec[0]}</h2><p>{NOTES[id]}</p><p>采用的参考方法：{REFS[id]}。原创模型修改，没有复制参考资产。</p><a href="{id}/native-comparison.png"><img loading="lazy" src="{id}/native-comparison.png"></a><p>左修改前 / 右修改后；点击查看原始尺寸。</p><div class="grid">')
  for view in ['front','45','side','back','action']:chunks.append(f'<figure><a href="{id}/native-{view}.png"><img loading="lazy" src="{id}/native-{view}.png"></a><figcaption>{view} / Forge</figcaption></figure>')
  chunks.append(f'</div><details><summary>代表技能完整时间范围 0–144 tick</summary><img loading="lazy" src="{id}/native-action.webp"><p>受控同步技能序列，非自然战斗验收。</p></details><details><summary>原色、灰模、剪影与UV（软件）</summary><div class="grid">')
  for f in ['unlit.png','clay.png','silhouette.png','texture.png','texture-2x.png','uv-overlay.png']:chunks.append(f'<figure><a href="{id}/{f}"><img loading="lazy" src="{id}/{f}"></a><figcaption>{f}</figcaption></figure>')
  chunks.append('</div></details></section>')
 (D/'index.html').write_text(''.join(chunks)+'</html>')
if __name__=='__main__':
 if '--research'in sys.argv:research()
 else:publish(sys.argv[1])
