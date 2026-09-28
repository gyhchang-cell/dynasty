"""Publish verified Minecraft render captures and original-art manifests, not mock gameplay."""
import html,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/art/realm-remaster-v4'
RES=ROOT/'src/main/resources/assets/dynasty'
def main():
 lang=json.loads((RES/'lang/zh_cn.json').read_text())
 out=DOC/'preview';out.mkdir(parents=True,exist_ok=True)
 def capture(name,label,group='models'):
  source=ROOT/'build/runtime-render-qa/results'/f'{name}.png'
  if not source.exists():return ''
  shutil.copy2(source,out/source.name)
  return f'<figure class="{group}"><a href="preview/{source.name}"><img loading="lazy" src="preview/{source.name}" alt="{html.escape(label)}"></a><figcaption>{html.escape(label)}</figcaption></figure>'
 buildings=''.join(capture(n,t,'building') for n,t in [('campus-observatory','九霄星坛 · 42×42 扩建 / 藏书廊与水庭'),('campus-palace-cutaway','皇宫内部 · 真实方块模型剖视'),('structure-main-hall','大殿 · 真实方块模型')])
 mobs=''.join(capture('mob-'+i,t) for i,t in [('dragon_emperor','龙帝 · 重甲与塔盾'),('nine_heaven_general','九天神将 · 翼刃与悬浮兵刃'),('dragon_king','龙王 · 分节龙尾、龙吻与角'),('undead_first_emperor','始皇亡魂 · 冕旒与悬浮面具'),('rebel_general','叛将 · 塔盾与护臂'),('eunuch_mastermind','宦官主谋 · 魂袍与面具'),('soul_soldier','魂兵 · 无足魂袍'),('thunder_envoy','雷使 · 翼刃'),('merfolk','鲛人 · 分节鱼尾')])
 weapons='';frames=''
 for row in json.loads((DOC/'weapons.json').read_text()):
  key=row['id'];source=RES/'textures/item'/f'{key}.png'
  shutil.copy2(source,out/source.name)
  label=lang.get('item.dynasty.'+key,key)
  card=f'<figure class="item"><img loading="lazy" src="preview/{source.name}" alt="{label}"><figcaption>{label}</figcaption></figure>'
  if '_pulling_' in key: frames+=card
  else: weapons+=card
 terrain=''
 for row in json.loads((DOC/'assets.json').read_text()):
  key=row['id'];shutil.copy2(RES/'textures/block'/f'{key}.png',out/f'{key}.png')
  terrain+=f'<figure><div class="tile" style="background-image:url(preview/{key}.png)"></div><figcaption>{lang["block.dynasty."+key]}</figcaption></figure>'
 tooltips=''
 for name in ('two-line-accessory','book-evolution'):
  source=ROOT/'build/book-qa/results'/f'{name}.png'
  if source.exists():
   shutil.copy2(source,out/source.name)
   tooltips+=f'<img class="wide" src="preview/{source.name}" alt="实际客户端检查">'
 body=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>王朝 · 山河与百炼</title>
<style>body{{margin:0;background:#101b1c;color:#ede8d4;font:16px/1.8 system-ui}}main{{max-width:1240px;margin:auto;padding:44px 24px}}h1{{font-size:44px;margin:0}}h2{{margin-top:56px;color:#d7c08a}}p{{max-width:900px;color:#b9c9c4}}small{{color:#b9c9c4}}a{{color:#9bdac3}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}figure{{margin:0;background:#172527;border:1px solid #344547;border-radius:10px;overflow:hidden}}img{{display:block;width:100%;object-fit:contain}}figcaption{{padding:12px 16px}}.item img{{height:220px;image-rendering:pixelated;background:#142122}}.tile{{height:200px;background-size:100px;image-rendering:pixelated}}.wide{{margin:18px 0;max-width:100%;border:1px solid #344547}}.notice{{padding:18px;border-left:3px solid #d7c08a;background:#1d2d2e}}code{{color:#a7e9cf}}</style>
<main><small>DYNASTY / REALM REMASTER 04 · 2026-09-24</small><h1>山河重构，百炼成锋</h1>
<p>建筑生成修复、四境原创地层、异形轮廓与流派兵器补全。下方角色与建筑图由 Minecraft 客户端真实模型渲染；地块是平铺贴图预览，不冒充游戏地形截图。</p>
<p class="notice">建筑和地层的生成修复只作用于新生成区块。不会删除旧存档；已存在的半栋建筑不会自动重建。地形起伏算法本轮保留，替换的是专属地表与岩层。</p>
<h2>01 / 楼梯可通，建筑完整</h2><p>修复坐标误用引起的高柱、楼梯朝向和出口栏杆。星坛从 26×26 扩为 42×42，新增藏书廊、水庭与钟亭。建筑生成更疏，皇宫、书院和关隘加入主世界适宜群系。</p><div class="grid">{buildings}</div>
<h2>02 / 不止方块人</h2><p>保留王朝题材，加入塔盾、层叠重甲、翼刃、悬浮面具、魂袍与分节水族尾巴；这是游戏内可用模型，不是概念画。常规士兵仍保留人形，年兽等现有兽型保留。</p><div class="grid">{mobs}</div>
<h2>03 / 四境原生地层</h2><p>天朝玉岩与灵玉沃土、幽冥岩与幽魂土、九霄云岩与星砂地、潮纹岩与珍珠砂。均为本轮原创纹理；实际区块生成已测试。入境标题补齐正确翻译键。</p><div class="grid">{terrain}</div>
<h2>04 / 兵器与被动分支</h2><p>新增北辰破阵枪、承影剑、风翎弓、雷符杖；每件都有配方、被动效果、流派归属和后续进化。锻造保留等级与附魔。已重制的旧精品素材不重复覆盖，饰品节点独立放在流派页上方。</p><div class="grid">{weapons}</div>
<details><summary>查看独立拉弦帧</summary><div class="grid">{frames}</div></details>
<h2>05 / 更清楚的提示</h2><p>饰品属性每行一条。名称统一为「自然指南针」「探险者指南针」；匹配检查支持 <code>zhinan</code>、<code>zhinanzhen</code>、<code>znz</code>。山河录同步展示新分支配方。</p>{tooltips}
<p><a href="assets.json">地层原创素材记录</a> · <a href="weapons.json">兵器生成提示词</a> · <a href="skins.json">角色纹理生成记录</a></p></main></html>'''
 (DOC/'gallery.html').write_text(body)
 print(DOC/'gallery.html')
if __name__=='__main__':main()
