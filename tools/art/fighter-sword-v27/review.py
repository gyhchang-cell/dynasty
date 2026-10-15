"""Matched-camera native grip comparisons, using the real exported model resources."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,shutil,hashlib
R=Path(__file__).resolve().parents[3];D=R/'docs/art/fighter-sword-v27';N=R/'docs/art/steve-fighters-v25/native/fighters-v25-sword-v27';B=R/'docs/art/steve-fighters-v25/native/fighters-v25-identity-v26'
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',22)
def crop(p):
 im=Image.open(p).convert('RGB');w,h=im.size;return im.crop((round(w*.25),round(h*.22),round(w*.7),round(h*.88)))
def file(folder,id,view):return next(folder.glob(f'*-{id}-{view}.png'))
def main():
 assert (N/'PASS.txt').exists()
 ids=[Path(p).stem for p in json.loads((D/'changed.json').read_text())];names={q['id']:q['name']for q in json.loads((R/'docs/art/steve-fighters-v25/targets.json').read_text())};sections=[]
 for id in ids:
  dd=D/id;dd.mkdir(exist_ok=True)
  for view in ['front','45','side','back']:crop(file(N,id,view)).save(dd/(view+'.png'))
  old=crop(file(B,id,'45'));new=crop(file(N,id,'45'));out=Image.new('RGB',(old.width*2,old.height+38),'#e8eae0');out.paste(old,(0,0));out.paste(new,(old.width,0));d=ImageDraw.Draw(out);d.text((12,old.height+3),'之前：刀刃沿手臂竖直',font=font,fill='black');d.text((old.width+12,old.height+3),'现在：掌中握柄、刀尖向前',font=font,fill='black');out.save(dd/'comparison.jpg',quality=94)
  frames=[]
  for p in sorted((N/'frames'/id).glob('*.png')):
   im=crop(p);im.thumbnail((500,700));frames.append(im)
  frames[0].save(dd/'motion.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
  sections.append(f'<section><h2>{names[id]}</h2><img src="{id}/comparison.jpg"><div><img loading="lazy" src="{id}/side.png"><img loading="lazy" src="{id}/motion.gif"></div></section>')
 Image.open(file(N,'imperial_soldier','45')).convert('RGB').resize((1400,900)).save(D/'vanilla-reference.jpg',quality=94)
 for name in ['PASS.txt','runtime-manifest.json']:shutil.copy2(N/name,D/name)
 (D/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>刀剑握持修正</title><style>body{max-width:1250px;margin:30px auto;padding:0 20px;background:#1b252a;color:#ece8df;font:18px/1.6 system-ui}img{max-width:100%}section{border-top:1px solid #7b817d;margin-top:25px}section>div{display:flex}section>div img{width:50%;object-fit:contain}a{color:#bad7d4}</style><h1>9种人物的刀剑握持修正</h1><p>模型内置刀剑原来沿局部-Y轴竖立。现在以手掌为支点前转65°，握点向掌内收2.2模型单位；柄、护手和刀刃作为整件随手臂运动。保留原刀形、身体、贴图、尺寸、碰撞和攻击时序。背包真实物品继续走原版物品层，不额外旋转第二次。</p><p>下图中间是原版尸壳持原版铁剑（原版抬臂姿势），右侧是修正后的帝国士兵；用来核对原版物品显示链路，手臂姿势不同，不冒充同姿势玩家。下方前后对比使用同机位、同尺度与同光照，聚焦被改人物，参照物不作前后比较。</p><img src="vanilla-reference.jpg"><p>画面来自隔离、静音的Forge实机；AI关闭并触发已有动作时钟。自然战斗与多人未验证，动作GIF是客户端采样回放。<a href="PASS.txt">实机检查记录</a></p>'''+''.join(sections))
 print('Exported',len(ids),'matched-camera grip comparisons')
if __name__=='__main__':main()
