"""Native V20/V21 comparison, without recolouring or exposure changes."""
from pathlib import Path
import json, hashlib, shutil, zipfile, re
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]
D=R/'docs/art/tianjiang-runes-v21'
N=R/'docs/art/boss-human-v12/native/tianjiang-runes-v21-final'
OLD=R/'docs/art/tianjiang-runes-v20/native'
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
    for i,name in [(1,'front'),(3,'45'),(5,'side'),(7,'back')]:
        Image.open(shot(N,i)).crop(CROP).save(D/(name+'.png'))
        board([i,i],['V20 · 原版','V21 · 更长、更细、错落加密'],name+'-comparison',[OLD,N])
    board([9,10,11],['蓄势','接触','恢复'],'attack')
    board([14,15],['普通夜间 · 关闭','普通夜间 · 开启'],'night')
    board([17,18],['最少粒子','减少粒子'],'settings')
    frames=[Image.open(p).crop(CROP).convert('RGB') for p in sorted((N/'sequence').glob('*.png'))]
    assert len(frames)==24
    frames[0].save(D/'motion.webp',save_all=True,append_images=frames[1:],duration=200,loop=0,lossless=True)
    report={'nativeStates':19,'sequenceFrames':24,'runtimeJarSha256':manifest['productionJarSha256'],
        'approvedV17AssetsUnchanged':old['approvedV17AssetsUnchanged'],
        'changes':{'glyphPathVerticalStretch':[1.55,1.65,1.75,1.85],'glyphPathWidthScale':.82,'strokeHalfWidthBefore':.034,'strokeHalfWidthAfter':.018,'majorSignsBefore':12,'majorSignsAfter':18,'minorSignsBefore':24,'minorSignsAfter':48,'placement':'Deterministic irregular angle, height, depth and lean; no per-frame random flicker'},
        'unchanged':['Body model','Texture','Animation','Weapon','Combat','Other bosses','36 light shards and 84 rendered motes'],
        'pending':['User visual acceptance','Multiplayer performance','Third-party shaders']}
    (D/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    def fig(name,caption,ext='png'):return f'<figure><a href="{name}.{ext}"><img src="{name}.{ext}"></a><figcaption>{caption}</figcaption></figure>'
    page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>天将符文 V21</title><style>body{margin:0;background:#e9ece8;color:#243842;font:17px/1.8 system-ui}main{max-width:1600px;margin:auto;padding:28px}img{width:100%;height:auto}figure{margin:20px 0 30px}a{color:#176479}</style><main><h1>天将 · 细长错落符文 V21</h1><p>本轮只改符文：笔画宽度约减半，形状收窄拉长；主符印12→18枚，环绕碎符24→48枚。高度、距离、倾斜角错开，避免整齐排成一圈。保留脸部前方视线和原有晶片光屑，身体、头部、武器与动作均不改。</p>'''
    page+=fig('motion','24帧无声实机采样，4.8秒循环。','webp')
    for name,caption in [('45-comparison','左V20、右V21；同8米、同FOV70、同光照与裁切。'),('front-comparison','正面同机位对照'),('side-comparison','侧面同机位对照'),('back-comparison','背面同机位对照'),('attack','原有攻击：蓄势、接触、恢复'),('night','普通夜间，无后期提亮'),('settings','粒子数量设置的简化表现')]:page+=fig(name,caption)
    page+='''<p>构建通过（跳过通用测试）；19个受控实机状态通过。已核对运行资源与模型、贴图、动画哈希。自然战斗、多人性能和第三方光影仍待验证。仅改天将，其他Boss等待验收。</p><p><a href="validation.json">验证记录</a> · <a href="native/PASS.txt">实机记录</a> · <a href="../tianjiang-runes-v20/reference-notes.json">沿用的参考记录</a></p></main></html>'''
    (D/'index.html').write_text(page)
    for rel in re.findall(r'(?:src|href)="([^"]+)"',page):assert (D/rel).is_file(),rel
    print('V21 native gallery and locked-asset checks complete.')
if __name__=='__main__':main()
