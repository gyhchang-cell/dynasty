"""Native V21/V22 comparison, without recolouring or exposure changes."""
from pathlib import Path
import json, hashlib, shutil, zipfile, re
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]
D=R/'docs/art/tianjiang-runes-v22'
N=R/'docs/art/boss-human-v12/native/tianjiang-runes-v22-final'
OLD=R/'docs/art/tianjiang-runes-v21/native'
CROP=(560,340,2210,1480)
def shot(root,i): return next(root.glob(f'{i:02d}-nine_heaven_general-*.png'))
def board(ids,labels,name,roots=None):
    roots=roots or [N]*len(ids)
    out=Image.new('RGB',(1650*len(ids),1200),'#e9ece8');draw=ImageDraw.Draw(out)
    font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',26)
    for j,(i,label,root) in enumerate(zip(ids,labels,roots)):
        out.paste(Image.open(shot(root,i)).crop(CROP),(1650*j,55));draw.text((1650*j+16,10),label,font=font,fill='#243842')
    out.save(D/(name+'.png'))
def main():
    assert (N/'PASS.txt').exists()
    D.mkdir(parents=True,exist_ok=True)
    old=json.loads((R/'docs/art/tianjiang-runes-v20/validation.json').read_text())
    manifest=json.loads((N/'runtime-manifest.json').read_text())
    assert hashlib.sha256((R/'build/libs/dynasty-1.4.0.jar').read_bytes()).hexdigest()==manifest['productionJarSha256']
    with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as z:
        for p,h in old['approvedV17AssetsUnchanged'].items():
            assert hashlib.sha256(z.read('assets/dynasty/'+p)).hexdigest()==h
        for i in range(19):
            state=json.loads((N/f'{i:02d}-state.json').read_text())
            for p,h in state['loadedResourceSha256'].items():assert hashlib.sha256(z.read(p)).hexdigest()==h
    (D/'native').mkdir(exist_ok=True)
    for p in N.iterdir():
        if p.is_file():shutil.copy2(p,D/'native'/p.name)
    for i,name in [(1,'front'),(3,'45'),(5,'side'),(7,'back'),(16,'far')]:
        Image.open(shot(N,i)).crop(CROP).save(D/(name+'.png'))
        board([i,i],['V21 · 上一版','V22 · 细长主笔、窄分支、收尖末端'],name+'-comparison',[OLD,N])
    board([9,10,11],['蓄势','接触','恢复'],'attack')
    board([14,15],['普通夜间 · 关闭','普通夜间 · 开启'],'night')
    board([17,18],['最少粒子','减少粒子'],'settings')
    frames=[Image.open(p).crop(CROP).convert('RGB') for p in sorted((N/'sequence').glob('*.png'))]
    assert len(frames)==24
    frames[0].save(D/'motion.webp',save_all=True,append_images=frames[1:],duration=200,loop=0,lossless=True)
    report={'nativeStates':19,'sequenceFrames':24,'runtimeJarSha256':manifest['productionJarSha256'],
        'approvedV17AssetsUnchanged':old['approvedV17AssetsUnchanged'],
        'changes':{'glyphPathVerticalStretch':[2.30,2.45,2.60,2.75],'glyphPathWidthScale':.46,'strokeHalfWidthBefore':.018,'strokeHalfWidthAfter':.010,'majorSigns':18,'minorSigns':48,'openEndWidthFraction':.24,'placement':'Deterministic irregular angle, height, depth and lean; no per-frame random flicker'},
        'unchanged':['Body model','Texture','Animation','Weapon','Combat','Other bosses','36 light shards and 84 rendered motes'],
        'pending':['User visual acceptance','Multiplayer performance','Third-party shaders']}
    (D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    def fig(name,caption,ext='png'):return f'<figure><a href="{name}.{ext}"><img src="{name}.{ext}"></a><figcaption>{caption}</figcaption></figure>'
    page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>天将符文 V22</title><style>body{margin:0;background:#e9ece8;color:#243842;font:17px/1.8 system-ui}main{max-width:1600px;margin:auto;padding:28px}img{width:100%;height:auto}figure{margin:20px 0 30px}a{color:#176479}</style><main><h1>天将 · 纵向剑纹式符文 V22</h1><p>在V21上继续调整：主笔拉长约48%，横向收窄约44%，笔画再细约44%，侧面厚度减半，断笔末端收尖。保留18枚主符印与48枚碎符的错落密度，不再通过堆数量掩盖宽短问题。身体、头部、武器与动作均不改。</p>'''
    page+=fig('motion','24帧无声实机采样，4.8秒循环。','webp')
    for name,caption in [('45-comparison','左V21、右V22；同8米、同FOV70、同光照与裁切。'),('front-comparison','正面同机位对照'),('side-comparison','侧面同机位对照'),('back-comparison','背面同机位对照'),('attack','原有攻击：蓄势、接触、恢复'),('far-comparison','12米同机位对比：细笔画远处会减弱，保留整体气场轮廓。'),('night','普通夜间，无后期提亮'),('settings','粒子数量设置的简化表现')]:page+=fig(name,caption)
    page+="""<h2>实际查看的剑斗罗参考</h2><p>查看了<a href="https://www.sohu.com/a/574637922_100121502">2022年动画评论文章中的截图</a>，不是官方制作分解，也不是手游或漫画。七杀剑近景显示沿长轴延伸的纹路和收尖轮廓；“剑道尘心”静帧可见巨剑周围细长的纵向符号列，前后疏密不同。</p><p>借鉴纵向、细线、断笔与疏密关系，未复制字形或图片。静帧分辨率不足以逐字辨认符号，也没有据此推断动画速度。本版仍保留天将原有配色和原创四组符形。</p><p><a href="https://p5.itc.cn/images01/20220806/091da555b37d4cfcba06fab5318ea671.png">七杀剑近景</a> · <a href="https://p1.itc.cn/images01/20220806/32168c90f89a447189d9f9db22216e77.png">剑道尘心符号列静帧</a></p>"""
    page+='''<p>构建通过（跳过通用测试）；19个受控实机状态通过。已核对运行资源与模型、贴图、动画哈希。自然战斗、多人性能和第三方光影仍待验证。仅改天将，其他Boss等待验收。</p><p><a href="validation.json">验证记录</a> · <a href="native/PASS.txt">实机记录</a> · <a href="../tianjiang-runes-v20/reference-notes.json">沿用的参考记录</a></p></main></html>'''
    (D/'index.html').write_text(page)
    for rel in re.findall(r'(?:src|href)="([^"]+)"',page):
        if not rel.startswith('https:'):assert (D/rel).is_file(),rel
    print('V22 native gallery and locked-asset checks complete.')
if __name__=='__main__':main()
