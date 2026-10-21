"""Small review page for the existing creature batch, not a new asset system."""
from paint import *
import html
D=R/'docs/art/cod1-creatures-v32'
notes={
'gudu_tianzhunv':'参考Naga分区的连续性：腹背纹样连续，紫黑甲壳、墨发、骨白半身与毒囊分开；对额前共面头皮做同色衔接。',
'yinyang_liandan_fangshi':'参考Ignis的冷暗连接与暖金属主面：铜炉和铁接头分开，瓷面、青火和暖火各有归属；保留真实炉腔和三足。',
'fubo_xunhai_yecha':'参考Naga头部/躯体分区：琥珀瞳、暗眼窝、浅腹与青壳相衬，分层壳缝沿尾向组织。',
'banshan_jiazhou_shikuang':'参考Goety亡灵的浅布/暗内层关系：棺壳暖木、冷铁门、灰绿残躯、裹尸布与血门分区；不覆盖真实空腔。',
'mojia_jueying_cike':'参考Goety低饱和衣料的内外层次：墨翼折帛、竹滑橇、冷铁滑轨与墨核分开，折纹沿构件而非随机斑点。',
'hanshan_tongjia_juyuan':'参考Hydra的暗主体与口眼识别：暗毛、猿面与古铜重甲分开；拳臂铜套按同一组体块组织明暗。',
'qingdeng_panguan_guichai':'参考Goety亡灵的浅色识别中心：独眼、青灯、纸页、墨迹、紫封铁册拉开，实际笔和笔尖保留。',
'liefeng_jindiao_yushi':'参考Hydra头口与身体的明度区别：淡颈羽突出鹰眼钩喙，褐金覆羽与飞羽分区，羽纹沿主翼展开方向组织。',
'zhenmu_suanni_tonghou':'参考Ignis的金属/内核分区和Hydra口眼主次：古铜狮壳、铁风箱与炉芯分开，修正眼窝/瞳/齿的索引。'}
css='''body{margin:0;background:#e9e8e1;color:#263337;font:16px/1.7 -apple-system,sans-serif}main{max-width:1450px;margin:auto;padding:32px}h1{font-size:32px}p{max-width:1100px}nav{display:flex;flex-wrap:wrap;gap:10px;position:sticky;top:0;background:#e9e8e1ed;padding:12px;z-index:2}a{color:#315c66}nav a{padding:7px 13px;border:1px solid #bbc9c7;border-radius:20px;text-decoration:none}article{border-top:1px solid #b9c4be;padding:25px 0}img{width:100%;display:block;image-rendering:pixelated;background:#d5dcda;border-radius:6px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}figure{margin:0}figcaption{padding:6px}details{margin:12px 0}summary{cursor:pointer}code{font-size:13px}small{color:#58696c}@media(max-width:800px){.grid{grid-template-columns:1fr}}'''
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>cod1 非人形生物 · V32</title><style>'+css+'</style><main><h1>cod1 · 九只非人形／混合体精英资源收尾</h1><p>保留已认可的模型、比例、骨架与动作时序，补齐逐面UV和原创像素材质。身体之外的武器几何及其旧UV像素保留。下方明确区分实际Minecraft画面与软件检查。</p><p><a href="verification.json">资源核对</a> · <a href="completion.json">构建与原生验收</a> · <a href="../steve-fighters-v25/nonhuman-references/index.html">既有100只非人形结构参考档案</a> · <a href="../human-armor-v31/index.html">上一批已完成的人形护卫/祭酒</a></p><nav>']
parts += ['<a href="#'+id+'">'+v[0]+'</a>'for id,v in SPECS.items()];parts+=['</nav>']
def fig(src,label):return '<figure><a href="'+src+'"><img loading="lazy" src="'+src+'" alt="'+html.escape(label)+'"></a><figcaption>'+label+'</figcaption></figure>'
for id,spec in SPECS.items():
 d=D/id;parts+=['<article id="'+id+'"><h2>'+spec[0]+'</h2><code>dynasty:'+id+'</code><p>'+notes[id]+'</p>']
 if (d/'native-45.png').exists():
  parts+=['<h3>原生Minecraft · 普通日光 · 静音独立场景</h3><p>玩家同框；原渲染器、原技能时钟，AI关闭并显式设置静态场景接地状态。只证明美术加载与受控动作，不代表自然战斗通过。</p><div class="grid">']
  for f,l in [('native-45.png','45度 / 游戏原图'),('native-front.png','正面 / 游戏原图'),('native-side.png','侧面 / 游戏原图'),('native-back.png','背面 / 游戏原图'),('native-action.webp','既有技能全段 / 原生连续采样，半尺寸最近邻'),('native-contact.png','既有技能阶段 / 游戏原图')]:
   if(d/f).exists():parts.append(fig(id+'/'+f,l))
  parts.append('</div>')
 parts+=['<details><summary>同条件前后、原色、灰度与UV检查</summary>',fig(id+'/comparison.png','左：旧PNG/UV；右：新PNG/UV。相同模型、相机和基础光照，软件预览。'),'<div class="grid">']
 for f,l in [('unlit.png','真实PNG原色 / 无额外光效'),('gray.png','灰度层级'),('front.png','软件正面 / 玩家、石砖、木材'),('side.png','软件侧面 / 同比例'),('back.png','软件背面'),('uv-direction.png','临时编号/方向纹理 · 仅预览')]:
  if(d/f).exists():parts.append(fig(id+'/'+f,l))
 parts+=['</div><p><a href="'+id+'/texture.png">原始PNG</a> · <a href="'+id+'/texture-2x.png">2倍最近邻</a> · <a href="'+id+'/uv-overlay.png">UV岛叠图</a> · <a href="'+id+'/animation-sampling.json">所有动作逐帧范围检查</a></p></details><details><summary>离线动作回放（原时间轴）</summary><div class="grid">']
 for f in sorted(d.glob('*.webp')):
  if not f.name.startswith('native-'):parts.append(fig(id+'/'+f.name,f.stem+' / 软件回放'))
 parts+=['</div></details></article>']
parts+=['''<article><h2>实际查看的材质参考</h2><p>本次查看了暮色Naga、Hydra，灾变Ignis的原始图集，以及本机愚者安装的Goety 2.5.36.1中的Necromancer和Apostle图集。只研究颜色组织与材质主次，未复制像素。整合包光影、宣传光照不计入PNG参考。</p><ul><li><a href="https://github.com/TeamTwilight/twilightforest/tree/e5d776e3b18258548f7fd618adf65315fbc8d053/src/main/resources/assets/twilightforest/textures/entity">暮色森林原始资源 · 固定版本</a>：头口、背腹和身体方向。</li><li><a href="https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/resources/assets/cataclysm/textures/entity/ignis/ignis_idle_0.png">Ignis原始图集</a>：大金属面、暗连接、少量亮部。</li><li><a href="https://github.com/Polarice3/Goety-2/tree/1.20/src/main/resources/assets/goety/textures/entity">Goety原始资源</a>：浅色识别中心、暗衣料及内部层次。</li></ul><p>本页没有宣布cod1整体DONE。自然入口、全部技能实战、死亡流程实机、双人联机和未实装Boss仍保留验收；模型形态未被改成人。</p></article></main></html>''']
(D/'index.html').write_text(''.join(parts));print(D/'index.html')
