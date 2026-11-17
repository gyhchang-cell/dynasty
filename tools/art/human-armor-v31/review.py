from pathlib import Path
import json,shutil
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];W=Path('/Users/a15356015027/.codex/worktrees/boss-eight-art/dynasty');D=R/'docs/art/human-armor-v31'
N=W/'docs/art/steve-fighters-v25/native/fighters-v25-armor-v31';B=W/'docs/art/steve-fighters-v25/native/fighters-v25-humans-v30-final3';id='pijia_panjiang_huwei'
assert (N/'PASS.txt').exists()
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',24)
def crop(p):
 im=Image.open(p).convert('RGB');w,h=im.size;return im.crop((int(w*.14),int(h*.20),int(w*.71),int(h*.90)))
for v in ['front','45','side','back']:
 before=crop(next(B.glob(f'*-{id}-{v}.png')));after=crop(next(N.glob(f'*-{id}-{v}.png')))
 after.save(D/f'{v}.jpg',quality=95)
 out=Image.new('RGB',(before.width+after.width,after.height+42),'#e4e2d9');out.paste(before);out.paste(after,(before.width,0));draw=ImageDraw.Draw(out);draw.text((12,after.height+5),'之前',font=font,fill='black');draw.text((before.width+12,after.height+5),'身体装备精修 · 武器未改',font=font,fill='black');out.save(D/f'comparison-{v}.jpg',quality=95)
paths=sorted((N/'frames'/id).glob('*.png'));frames=[crop(p)for p in paths];ticks=[int(p.stem)for p in paths]
for im in frames:im.thumbnail((850,650))
frames[0].save(D/'motion.webp',save_all=True,append_images=frames[1:],duration=[max(50,(b-a)*50)for a,b in zip(ticks,ticks[1:])]+[150],loop=0,quality=90)
for filename in ['texture.png','texture-4x.png']:shutil.copy2(R/f'docs/art/steve-fighters-v25/{id}/{filename}',D/filename)
shutil.copy2(N/'PASS.txt',D/'native-PASS.txt');v=json.loads((D/'verification.json').read_text());v['native']='PASS four views + original skill20 sampled across windup, contacts and recovery, AI disabled';v['build']='PASS isolated build -x test';v['pending']=['Natural combat, multiplayer and whole cod1 entity acceptance remain pending.'];(D/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
(D/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>披甲叛将护卫 · 人物装备精修</title><style>body{margin:32px auto;padding:0 20px;max-width:1400px;background:#152027;color:#e9e5d9;font:18px/1.7 system-ui}img{max-width:100%;margin-bottom:24px}a{color:#b8d8cd}h2{margin-top:44px}</style><h1>披甲叛将护卫 · 身体与装备</h1><p>保留史蒂夫六主体、当前体型与武器。补齐 cod1 的兽吞肩甲和铜质护心镜，叠札胸甲与暗朱后衣拉开材质。无领域、无新粒子，不修改技能和伤害。</p><p>以下为实际Forge客户端同机位对照，玩家同框。武器几何与逐面像素均未修改；新增装备导致部分UV岛移位。</p>'''+''.join(f'<h2>{label}</h2><img src="comparison-{view}.jpg">' for view,label in [('front','正面'),('45','45度'),('side','侧面'),('back','背面')])+'''<h2>原技能时钟动作采样</h2><p>关闭AI的同步动作检查，包含蓄势、攻击和恢复，不代替自然战斗或多人验证。</p><img src="motion.webp"><h2>真实像素图集</h2><a href="texture.png">原始256×256 PNG</a><p><img src="texture-4x.png" style="image-rendering:pixelated"></p><a href="verification.json">未改武器/主体的检查记录</a> · <a href="native-PASS.txt">客户端检查</a><p>cod1整项仍为PARTIAL：本轮没有删去整只护卫的功能和验收要求。</p>''')
print(D/'index.html')
