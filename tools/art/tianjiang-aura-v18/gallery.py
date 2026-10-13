"""Actual native on/off comparisons and silent 4.8-second render capture."""
from export import *
import shutil,zipfile
from PIL import ImageDraw,ImageFont
N=R/'docs/art/boss-human-v12/native/tianjiang-aura-v18-final'
def run():
 assert (N/'PASS.txt').exists()
 native=D/'native';native.mkdir(exist_ok=True)
 for p in N.iterdir():
  if p.is_file():shutil.copy2(p,native/p.name)
 baseline=json.loads((D/'baseline-hashes.json').read_text())
 for n,h in baseline.items():
  if '/assets/' in n:assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
 expected=json.loads((N/'runtime-manifest.json').read_text())['resources'];states=[]
 for i in range(14):
  s=json.loads((N/f'{i:02d}-state.json').read_text())
  for key,h in s['loadedResourceSha256'].items():
   assert expected[key]==h==hashlib.sha256((R/'src/main/resources'/key).read_bytes()).hexdigest()
  if s['stage'].endswith('-off') or s['stage']=='death':assert s['materialGlowAlpha']==0
  states.append({k:s[k] for k in ['stage','clip','age','materialGlowAlpha','replicatedSwing','auraParticleEmissionRequests']})
 assert max(s['materialGlowAlpha'] for s in states if s['stage'].startswith('attack'))>max(s['materialGlowAlpha'] for s in states if s['stage'].endswith('-on'))
 with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as z:
  key=str(OUT.relative_to(R/'src/main/resources'));assert OUT.read_bytes()==z.read(key)==(R/'build/resources/main'/key).read_bytes()
 font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',25)
 crop=(700,530,2050,1450)
 for num,view in [(0,'front'),(2,'45'),(4,'side'),(6,'back')]:
  board=Image.new('RGB',(2700,1000),(232,235,230));d=ImageDraw.Draw(board)
  for j,fx in enumerate(['off','on']):
   im=Image.open(N/f'{num+j:02d}-{ID}-{view}-{fx}.png').crop(crop)
   im.save(D/f'{view}-{fx}.png');board.paste(im,(1350*j,50))
   d.text((1350*j+16,10),view+' / '+('关闭新增气场' if j==0 else '开启新增气场')+' / 实机普通日光',font=font,fill=(30,40,48))
  d.text((16,970),'相同8米机位、FOV70、相同裁切；头部与模型完全相同。原待机微动与真实粒子位置保留。',font=font,fill=(30,40,48));board.save(D/f'{view}-comparison.png')
 frames=[]
 for p in sorted((N/'sequence').glob('*.png')):
  frames.append(Image.open(p).crop(crop).convert('RGB'))
 assert len(frames)==24
 frames[0].save(D/'aura-motion.webp',save_all=True,append_images=frames[1:],duration=200,loop=0,lossless=True)
 strip=Image.new('RGB',(1800,620),(232,235,230))
 for j,i in enumerate([0,5,10,15,20,23]):
  frame=frames[i].resize((600,409),Image.Resampling.NEAREST)
  # A small time sampler accompanies, never substitutes for, the full animation.
  frame.thumbnail((300,570),Image.Resampling.NEAREST);strip.paste(frame,(j*300,60))
 strip.crop((0,0,1800,290)).save(D/'motion-samples.png')
 report={'acceptedGeometryBaseTextureAndAnimationUnchanged':True,'emissiveMaskActivePixels':json.loads((D/'mask-validation.json').read_text())['activePixelsByBone'],
  'actualLoadedAssetsMatchSourceAndJar':True,'nativeStages':states,'nativeMotionFrames':24,'motionDurationSeconds':4.8,
  'renderer':'Actual Forge1.20.1 client / ordinary daylight / no external shaders / no bloom / no audio',
  'tested':'14 controlled visual states including effect-off/on, walk, swing tell/contact/recovery, hurt/death; real loaded mask hashes checked',
  'notTested':'Natural encounter, multiplayer load/performance, or every spell. Enhancement follows current swing; no invented spell telegraph.'}
 (D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 refs={'observedStills':[
  {'character':'千仞雪 / 斗罗大陆1','source':'https://www.sohu.com/a/652090875_120704778','image':'https://p3.itc.cn/images01/20230310/29e2709292e1402d9045e052fa26fcc4.jpeg','status':'第三方文章转刊、带片名和下集预告的动画静帧，已实际查看；非官方原视频逐帧研究','observation':'后方展开框住人物，面部清晰，武器及手部成为聚光区域','application':'天将肩后令环与光片；只借鉴位置主次，不复制翅膀、图案、服装或角色身份'},
  {'character':'霍雨浩相关融合技 / 斗罗大陆2','source':'https://www.sohu.com/a/713181398_120768750','image':'https://p3.itc.cn/images01/20230819/d965517b16164f04acbd11985db79e44.jpeg','status':'第三方转刊动画静帧，已实际查看；完整动态时序未观看','observation':'冷暖能量在掌部汇聚，面部与衣服仍然可读','application':'胸口原雷纹与大戟玉点、短刃段的少量光像素；挥击使用现有动作状态增强'},
 ],'unavailable':'新浪官方宣传图的图片服务器返回403，未将其计入看过的参考。未播放带声音的视频。','externalAssetsInProduction':False}
 (D/'reference-notes.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n')
 def f(name,label,ext='png'):return f'<figure><a href="{name}.{ext}"><img loading="lazy" src="{name}.{ext}"></a><figcaption>{label}</figcaption></figure>'
 page=f'''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>九霄天将 · 雷霆令环与身上光效 V18</title>
<style>body{{margin:0;background:#e9ece8;color:#23343b;font:17px/1.75 system-ui}}main{{max-width:1600px;margin:auto;padding:28px}}h1{{font-size:30px}}h2{{font-size:24px;margin-top:35px}}img{{max-width:100%;height:auto}}figure{{margin:0 0 26px}}figcaption{{padding:8px 0}}a{{color:#195b70}}p{{max-width:1200px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px}}</style><main>
<h1>九霄天将：雷霆统帅气场</h1>
<p>保留已经认可的V17头盔、面甲和全身模型。这轮增加的是独立客户端光效：肩后古金断环、六枚青白令符光片、缓升光屑，以及胸口雷纹与大戟局部的呼吸亮点。整个头部不新增发光像素。</p>
<h2>实际游戏动态 · 无声音</h2>{f('aura-motion','24张连续实机采样，间隔4tick，约4.8秒；普通日光，无外部光影或后期辉光。','webp')}
<h2>关闭 / 开启对照</h2>{f('front-comparison','正面8米玩家视角，同机位同裁切；武器、面部和服装保持清楚。')}{f('45-comparison','45度：令环和光片位于肩后，身体雷纹的局部发光跟随实际骨骼。')}
<div class="grid">{f('side-comparison','侧面：气场与人物的前后位置')}{f('back-comparison','背面：令符、断环与青白气流')}</div>
<h2>身上哪些地方在变化</h2><p>新增128×128透明光效遮罩只有30个有效像素：胸口原有雷纹15个，戟上玉点与短刃段15个。静止时缓慢呼吸，挥击时随原有同步挥手进度增强，死亡时关闭。没有染亮整套护甲，也没有修改基础PNG或添加身体零件。</p>
<p>待机普通设置每4tick发出3枚小光屑；攻击时最多5枚（仍受全局每4tick共16枚预算约束）。减少粒子设置降为1枚，最少粒子不发射附加粒子。令符属于客户端渲染光片，没有服务器实体、碰撞、音效、屏幕震动或新增伤害判定。</p>
<p><a href="emissive-mask.png">原始透明遮罩</a> · <a href="emissive-mask-4x.png">最近邻四倍</a> · <a href="native/10-{ID}-attack-contact.png">实际挥击接触帧</a> · <a href="native/13-{ID}-death.png">死亡关闭效果</a> · <a href="validation.json">实际加载与状态检查</a></p>
<h2>参考与自检</h2><p>实际看过的参考是转刊动画静帧：<a href="https://www.sohu.com/a/652090875_120704778">斗罗大陆1千仞雪的背后展开与武器聚光</a>、<a href="https://www.sohu.com/a/713181398_120768750">斗罗大陆2霍雨浩相关画面的掌部能量汇聚</a>。学习位置和主次，转换成原创Minecraft棱角光片；没有复制人物翅膀、魂环纹样或特效素材。没有声称看完动画中全部正反派或完整动态时序。<a href="reference-notes.json">实际参考范围</a>。</p>
<p>第一轮白天预览偏细线，第二轮加入有体量但稀疏的令符光片。构建通过；14个受控实机状态通过，新增遮罩的实际加载哈希与源资源、JAR一致。已确认关闭效果和死亡时发光归零，攻击时增强。自然遭遇与多人性能尚未验证。测试全程静音、独立临时世界，未动用户存档。</p>
<p><a href="../tianjiang-helmet-v17/index.html">此前认可的V17头部与模型</a> · 当前原始模型、基础贴图、骨架、动画文件均与V17逐字节一致。</p></main></html>'''
 (D/'index.html').write_text(page);print('Native on/off, motion and unchanged-model verification ready.')
if __name__=='__main__':run()
