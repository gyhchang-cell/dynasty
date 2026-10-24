"""Human-reviewed notes for the 100 distinct model + original-atlas study cards.

These are static source/atlas observations, never claims of running 100 mods.
One relevant humanoid/semi-humanoid library is reused, not 600 unique references.
"""
from pathlib import Path
import json,html,hashlib
from build_models import ROOT,OUT
notes='''黑铁甲与绿皮分开，头盔开口保持脸部窗口|宽腹短肢与长耳一读成兔，腹面留出整块浅色|轮廓极简，蓝纹依附大块衣面而非几何碎块|巨斧、前躯和小头形成主次；骨色与旧铁不等亮|外露脑色与暗绿身体分区，少量长条连接强调异常|躯干前伏与长臂相接，暗皮用局部暖色分组|六块体型也可成立，眼部单点比全身纹理更醒目|厚肩垂臂与小头形成力量，棕皮与浅齿分离
黑紫集中眼与胸，长臂使视线沿身体向下|口鼻前凸接入大头，不用几个小方盒代替脸|窄颈与长臂、肩块相接，白壳和木质分开|厚前躯压低，珊瑚附着纹理与甲壳颜色不同|鱼嘴前伸、背鳍和腿臂连成海族轮廓，腹胸用横向分区|头颈和弯背同轴，破布与腐皮分开|红色只在开口和肢端，暗体保持整面|小个体大眼比大量纹路有效，头肩连接紧凑
帽檐主导上沿，皮肤、红布和金属彼此分开|口鼻与长尾提供生物方向，红胸只占局部|大眼、前嘴和耳侧共同表达小怪，不做满面纹饰|细长海族轮廓，亮纹围绕脸胸而非到处金边|脊鳍接上背肩，深色鳞肤与浅腹口区区分|头前伸、低肩与长肢成捕食姿态，骨色中留少量肉色|朴素体块依靠褐色布与浅面区分身体上下|石甲主面完整，缝与暗关节把肢段连接读清
宽前臂压在身体前，皮革衣与灰皮、铁件分开|大肩与垂臂整体连贯，毛色成组而非均匀噪点|帽与面部相邻但分色，小红帽足够表达职业|深海躯体上窄亮纹建立头胸中心，非满身发光|帽、袖和衣摆组成大轮廓，装饰集中颈与腰|大暗体保持完整，红口提供唯一强识别点|三头改变上缘，眼口在深红体上仍可读；不照搬多头|角、头颈与前肢相接，暗色身体留有限浅角
冰蓝衣层与灰脸分开，领口包住头肩过渡|大耳、弯背和细臂连续，少数浅掌与眼点突出|方头接厚躯，绿肤中口鼻和眼是重点而非甲边|帽冠与长身区别职业，暗蓝主体上只少量彩饰|中央机器身与两臂有清楚层级，明亮色只放核心|倾头、长垂臂与下摆使幽灵成立，浅布末端积暗|细长肢体与背部连接成异形轮廓，金红集中部位|低头大前臂连贯，腐色表面上红色集中裂口
鱼尾式裙摆与手杖对应海中亡灵，胸腹有长条浅区|矮躯与宽头一体，幽蓝图集为额外观感，不能当通用金属|头部角冠、垂肢和裙体保持同向，亮点避开普通外壳|大兜帽收住头，黑布与肤色小窗口形成主次|弯曲腿臂接入厚胸，小头避免与武器争抢|腹部正面条状红区与暗侧面区分，肢体不画同等亮度|宽领接头，胸前饰物与袖口在大暗红布面上点缀|头缩在上躯中，巨臂与甲面连成整体而非额外挂肩
红眼嵌入暗身，肩胸的强体量比细纹更重要|大头短躯、短臂短足能读作完整小生物|肩胸护框与内部核心分色，身体空隙不由黑色假画|浅石外壳与紫色内区区分层次，关节不纯黑|红金甲的大面与暗内层交替，装饰跟随甲片位置|长垂臂和瘦躯连贯，红色集中于面胸与少数关节|蓝白材质用较大冰色面，不能照抄为白毛或骨|双臂弯曲形成持械姿态，骨、布与金甲各占一层
多头主轮廓与细腰形成异化，暗红大面不必全铺符|角饰和长脸形成身份，绿暗表面以眼点收束|长披布接肩颈，蓝色衣面留干净大区|骨架间有真空隙，米白骨条和深缝保持方向|斜背接臂，蓝色外皮与棕色腹面连贯|护甲大面、布和腰带分开；金边只强调边缘局部|巨胸、炉口与臂体各有体量，亮橙集中动力位置|条状绿色纹理围绕胸腹组织，暗侧面不跟着全部提亮
植物大背与粗臂连接，枝叶明暗有生长方向|头周围小块服务核心，金红纹理依附主面|帽、领和袖有层次，但身体基础保持简单|悬浮头与躯壳之间确有间隙；蓝纹围绕核心组织|帽檐和长袍连成一体，骨白胸骨与紫布分开|小头重胸与粗足形成承重，石面可以安静|头盔、肩袖和腰带分组，斜向装饰不等于每面描边|头部外环与身体框架有留空，浅纹不能盖住内外关系
长帽与前胸饰带成纵向，红布与灰面分离|朴素方体以眼嘴明确正面，黄绿皮色不靠盔甲装饰|背部大块压住肢根，内层暗色和外壳区分|白色主体上暗红脸是主视觉，大面积浅色并非不能有威胁|胸肩主块明显，浅石接暗缝，红核只占少数位置|赤色魂体围绕胸腹组织明暗，浮空头与框体有空间关系|四肢与炉胸有粗细层级，灰壳与红橙内芯分区|宽帽与黑甲体一体，红色头胸纹与暗裙分开
小兜帽包住头，肤色面窗不与黑袍混为一片|厚头颈连接长腹，黄沙与棕裂缝按部位分组|盾与躯体不等量描亮，浅头和黑衣对比清楚|细肢与宽肩交替，黄体暗肢不应同样花|盔顶与肩甲外扩很少，衣甲和灰脸仍可区分|头冠、前臂和胸连接形成纵向，红色中眼区另分层|紫袍、胸扣与灰脸三层关系足够表达施法身份|头、躯和臂紧密连接，暗绿仅用眼部亮点收束
浅色核心与金框集中于正面，灰机械壳保留大面|背部成组薄片改变侧轮廓，蓝色胸区有明确中心|高领连接头部，黑袍、金饰和红内衬是三种材质|头侧棱与弯臂保持身体方向，白体绿线仅集中少数区域|骨白脸胸、棕布与兵器分材质，不用全白包边|树干沿身长组织纹理，绿冠与木躯分开|长臂接肩，黑体也用灰色大斑分形，不填全黑|多臂围绕同一胸体连接，紫色主体保持统一
长叶臂与覆帽有植物方向，根、叶、花仅局部色变|外胸甲接肩，明绿胸与黄褐四肢分区|宽帽下头与身之间有层级，暗衣中白纹集中肩胸|分段胸腹与头颈连贯，亮橙躯体上暗足作为支撑'''.replace('\n','|').split('|')

def main():
 source=ROOT/'build/bestiary-v42/similar-mobs/ledger.json';r=json.loads(source.read_text());assert len(notes)==len(r['items'])==100
 assert hashlib.sha256('\n'.join(v['identity'] for v in r['items']).encode()).hexdigest()=='1e6562c1d1ad61cce357516e47efe70b0fcfefc923aff880bb451d94eac574e0', 'Reference selection changed; inspect again before applying notes'
 for row,note in zip(r['items'],notes):
  row.update(viewed=True,observation=note.strip(),inspection='Actually viewed source bind-pose reconstruction and original atlas on sheets 01..13; 2026-10-22',limitations='Static constructor reconstruction can differ from inherited/runtime pose; original atlas is viewed separately, not claimed to be an author-native game render.')
 r.update(status='100_DISTINCT_MOB_IDENTITIES_AND_CONSTRUCTOR_SHAPES_VIEWED',counting='Distinct entity identities and constructor geometry. Exact shape duplicates Dramix and Reyvor excluded. No skin variants counted separately; no claim of 100 modpacks or running 100 mods.',scope='Reusable comparison library for humanoid / semi-humanoid, undead, armored and construct body connections. Not 600 separate references, not a general reference set for birds or quadrupeds.',production_assets_copied=False)
 r['applied_to_next_assets']={
  'terracotta_warrior':dict(reference_pool=list(range(1,101)),closest=[1,7,11,24,27,48,51,62,77,85,93],application='Keep exact six Steve blocks. Topknot, small lamellar shoulder caps, clay face planes, overlapping chest rows; matte clay not shiny bronze. Dark joints support existing punch gait; no invented weapon.'),
  'minister':dict(reference_pool=list(range(1,101)),closest=[3,17,27,29,33,44,47,59,67,73,87,91],application='Use Steve proportions, modest hat and cuffs. Clean long robe panels, cloth direction, aged distinct face. Heavy monsters are negative proportion comparisons, never transferred to a civilian.'),
 }
 (OUT/'reference-study.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 parts=['<!doctype html><meta charset="utf-8"><title>100个实际怪物 · 结构与原始图集研究</title><style>body{background:#e9ebe4;color:#253b37;font:17px/1.6 sans-serif;max-width:1450px;margin:auto;padding:25px}img{width:100%}article{margin:26px 0}a{color:#296c73}</style><h1>100个实际怪物：模型与原始贴图</h1><p>8个模组的100个独立生物身份与构造。排除同构换色；左图是源码静态重建，右图是作者原始图集，不能当作游戏实拍或完整动画。只学习，不复制资产。此同类参考库复用于本批后续人形/半人形，不声称每只又新增100个独立参考。</p>']
 for start in range(0,100,8):
  parts.append(f'<article><img loading="lazy" src="../../../build/bestiary-v42/similar-mobs/sheet-{start//8+1:02}.png">')
  for row in r['items'][start:start+8]:parts.append(f'<p>{row["number"]:03} {html.escape(row["identity"])} — {html.escape(row["observation"])} · <a href="{row["model_source"]}">模型</a> / <a href="{row["texture_source"]}">原始PNG</a> / <a href="{row["renderer_source"]}">绑定</a></p>')
  parts.append('</article>')
 (OUT/'reference-study.html').write_text(''.join(parts));print('100 model/atlas cards actually viewed; deduplicated evidence + individual observations saved before next modeling')
if __name__=='__main__':main()
