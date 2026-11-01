"""Manual observations after opening all four batch05 sheets and older glyph sheets."""
import json
from pathlib import Path
from datetime import datetime, timezone

D = Path(__file__).resolve().parent
data = json.loads((D / 'batch-05-candidates.json').read_text())
# id: family, representative, proposed-new-family, actual observation, application limit, target ids
N = {
155: ('EXCLUDE-blank',155,0,'空白石坯只有裂缝和厚边，没有专属符号。','共享载体不作为纹样案例。',[]),
156: ('malum-bent-flow',48,0,'蓝白短竖笔上端弯向右，底端左收；载体仍为同一块裂石。','与已读折向主干族合并；周围低饱和晕色不用于硬边原稿。',['chiling_brush','leifu_staff']),
157: ('malum-fire-s',50,0,'红白弯钩由上方斜干下折，再在底部向左收口。','归已有弯曲火形族，不按红色另计；不据血符名称推断游戏机制。',['chiling_brush']),
158: ('goety-branched-cross-central-square',44,0,'四个白短尖围出方形暗心，横竖交叉但中心不填白。','归已有中心留孔十字族；不能扩大成全屏光十字。',['chiling_brush','supreme_sword']),
159: ('open-comb-rune',159,1,'紫色直竖连两道向右短横，开口保持清楚；少数白点压在横笔上。','只学开合和笔粗节奏；与 evocation 为同形，不算两个学院。',['chiling_brush','leifu_staff']),
160: ('open-comb-rune',159,0,'绿色竖干加两道短横，与上一张 E 状骨干一致。','同形换色并入 VIS-159；不能以绿/紫区分两个独立案例。',['chiling_brush','leifu_staff']),
161: ('malum-fork-hook',49,0,'橙色粗中干左右各分短支，亮点集中在枝端。','归已有分叉钩族；石坯和元素颜色不加数。',['leifu_staff']),
162: ('down-wedge-stem',162,1,'黄白倒三角宽头接一段很短竖尾，亮面上宽下尖。','只可借方向明确的头尾关系；不直接搬宗教含义或光晕。',['chiling_brush','beichen_spear']),
163: ('goety-branched-cross-central-square',44,0,'两条青白折线交成斜叉，中间暗缝让四臂可分。','与交叉分枝主干保守合并；斜转和冰色不另算一套。',['leifu_staff']),
164: ('paired-post-gap',164,1,'两侧淡紫竖笔，中间上下各一亮点，形成有间隙的双柱。','学习双柱与间断节点，不把每个亮点当独立星座。',['chiling_brush','leifu_staff']),
165: ('malum-tree-fork',60,0,'绿色直弯主干在下端向左右分短叉，白色停在根部转折。','归已读树叉族；自然名称不能充当云龙纹。',['chiling_brush']),
166: ('malum-center-post-ward',67,0,'短黄白中柱向右上分笔，下端保留暗缺口。','与已有中央守势柱组织合并；只有构图层借鉴。',['zhenyue_blade','chiling_brush']),
167: ('malum-tree-fork',60,0,'紫黑三叉顶连底部短横，中央直笔从上贯下。','与树叉/中心主干已有观察合并，不因符尾横线加案例。',['chiling_brush']),
168: ('silver-shield-blue-field',168,1,'灰盾中部白灰大面、深灰单侧厚边，蓝色沿盾外轮廓围一圈。','是界面盾牌图标，不能作为已绑定的武器护罩或穿戴甲纹；只借护形主次。',['zhenyue_blade']),
169: ('parallel-falling-marks',169,1,'紫色两道长斜亮簇伴短点，留出暗色对角间隔。','只借方向和重复节奏，排除周围晕光，不照搬原像素。',['zhuxing_bow','fengling_bow']),
170: ('parallel-falling-marks',169,0,'蓝色多道平行斜点/短线，同向落下、长短交替。','与上一张平行落点族合并；不能拿不同颜色和数量重复计。',['zhuxing_bow','fengling_bow']),
171: ('branched-lightning-fold',171,1,'粗白主折线分出两个明显支路，青蓝较暗区域围绕分叉。','只能学习主叉与支叉层级；不复制柔光，不推断连锁目标数量。',['leifu_staff']),
172: ('EXCLUDE-generic-soft-diagonal-beam',172,0,'一条斜白核心外包多层青蓝发散亮带，没有可辨身份节点。','通用能量束且软亮面积过大，不能当专属北辰枪纹样。',[]),
173: ('EXCLUDE-name-not-cloud-motif',173,0,'红底上是白色心形及上方半环，画面并不是云折。','cloud 名称不足以算流云/承影参考；排除当前云纹范围。',[]),
174: ('hollow-radial-command',174,1,'深紫外坯内有四个方孔/回折小结，中心暗，节点对称。','小型命令符的组织参考，不据名称声称已实现命令技能。',['chiling_brush','supreme_sword']),
175: ('hollow-radial-command',174,0,'蓝灰外坯包围五个黑孔，中心很暗，各孔互相保持间隔。','与上一张放射留孔组织合并；四孔/五孔不是自动独立学院案例。',['chiling_brush','supreme_sword']),
176: ('EXCLUDE-guardian-face',176,0,'青绿格状正脸配两个亮点，橙边包住整体。','像生物脸或面具，非当前守势印纹；不用 guardian 名称硬套护卫范围。',[]),
177: ('silver-shield-blue-field',168,0,'银灰盾在圆形蓝底上，主盾轮廓与 VIS-168 相近。','不同模组/外坯形状仍是相同盾形构图，合并；非真实护罩画面。',['zhenyue_blade']),
178: ('parallel-falling-marks',169,0,'几枚灰白箭头同向排在褐色杆和绿底上，尖端与杆色分离。','与同向箭雨/落点组织合并；仅借轴向，不能照搬背景。',['zhuxing_bow','fengling_bow']),
179: ('clustered-hard-star-points',179,1,'紫色底上三块白亮星簇错位分布，四向短臂及暗间距可辨。','可学星点大小主次；星簇不是三段攻击或星座机制证据。',['zhuxing_bow']),
180: ('open-tapered-vortex',180,1,'浅青漏斗上宽下窄，横向折层朝底端旋收。','只学开放的折向层级，不复制圆润锥体、软晕或龙卷技能含义。',['liuyun_sword','chengying_sword']),
181: ('open-tapered-vortex',180,0,'白青开口弧带从左下向右上回卷，中心暗空可见。','与漏斗旋收的流向族合并；弧度转向不自动多计。',['liuyun_sword','chengying_sword']),
182: ('EXCLUDE-generic-crescent',182,0,'一片厚白弯月占满绿色圆底，内部没有节点或折线组织。','太泛化且弯缘过圆，不作当前云龙/翎片身份参考。',[]),
183: ('branched-lightning-fold',171,0,'白蓝粗闪电三段折向，中部伸一短支，暗蓝底留白充足。','同一闪电主干族，不把较少分叉当另一套。',['leifu_staff']),
184: ('branched-lightning-fold',171,0,'白色长折笔穿过中间，蓝亮细支向外散。','与 VIS-171/183 合并；色差和支路数量不重复计。',['leifu_staff']),
185: ('EXCLUDE-generic-concentric-ring',185,0,'紫盘内部是两个近同心轮廓，外侧褐边。','通用圈不能算镇岳的专用方印/护卫纹；沿用旧批排除原则。',[]),
186: ('malum-bent-flow',48,0,'暗木底上两枚厚的右向折角上下分段，中间留条窄暗缝。','与折向主干族合并；阴刻载体变化只增材质观察，不增符号设计。',['chiling_brush','leifu_staff']),
187: ('malum-tree-fork',60,0,'阴刻主柱下垂，上方短叉向两侧伸，下方呈厚钩。','树叉形复用，不算新符；低对比木雕不能直接当发光法阵。',['chiling_brush']),
188: ('malum-fork-hook',49,0,'斜向粗笔在末端多次直角回钩，几个粗端沿主干分开。','合并已有分叉钩族；只学笔画开口，不搬木底噪点。',['chiling_brush']),
189: ('malum-center-post-ward',67,0,'方厚上块连中央短柱和下方横足，两侧凹口形成站稳的底部。','归中心柱守势组织；不按地元素名称新算镇岳一族。',['zhenyue_blade','chiling_brush']),
190: ('malum-closed-lozenge',59,0,'粗菱环留中央方孔，下端接一段短尾，木纹被符形打断。','闭合菱符归旧族；不能将小方孔认作完整盔甲 UV 面。',['chiling_brush','supreme_sword']),
191: ('malum-fire-s',50,0,'上下起伏的火钩构成厚折柱，腰部两侧伸出短点。','与火形折笔归同族；不因阴刻/发光两种材质重复计。',['leifu_staff']),
192: ('EXCLUDE-heart-block-silhouette',192,0,'上宽双肩与下尖底构成近心形阴刻，内部不分笔画。','与当前方符/护卫/云折主题关联弱，排除而非按 sacred 名称凑数。',[]),
193: ('EXCLUDE-skull-like-mask',193,0,'上宽下收的黑面带两处暗眼孔，底端小缺口。','面具/骷髅读形，不冒充当前命令符。',[]),
194: ('squared-corner-meander',194,1,'白色直角回折组成四角对称框，边线之间保留连续暗缝，中央大孔不填满。','只学方折线连通与留空；这是门面纹理，不能冒充完整建筑，也不复制原图。',['chiling_brush','supreme_sword','zhenyue_blade']),
195: ('squared-corner-meander',194,0,'白色 L 形和短线分散在四边，中心无完整图案。','是同门纹的 CTM 局部组件，不单算设计或完整建筑；装配规则尚未核读。',['chiling_brush','supreme_sword']),
196: ('EXCLUDE-soft-fiery-field',196,0,'橙黄底上四团软亮峰围中心，边界连续过渡、没有硬笔结构。','不符合当前硬像素材质，也不是独立符号。',[]),
197: ('EXCLUDE-dense-horizontal-noise',197,0,'细密灰褐横纹夹杂细绿亮点，远看纹样主次不清。','48px 图的高密度纹理不适合原版粗材质；不因 ironwood 名称算板甲纹样。',[]),
198: ('single-overlap-feather',198,1,'黑灰长羽沿对角轴，中心轴以几块亮灰说明，两侧外沿阶梯错开。','可学窄长轴与羽片重叠；只参照构形，不复制原版/暮色像素。',['fengling_bow']),
199: ('radial-feather-fan',199,1,'绿扇面由数条粗斜叶肋向同一底轴汇聚，少量青灰点在肋间。','与单羽不同的是多扇片汇聚组织；不将单片、颜色或各纹点分别计。',['fengling_bow','zhuxing_bow']),
}
rows = []
for r in data['rows']:
    n = int(r['reference_id'].split('-')[1])
    family, rep, credit, note, limit, targets = N[n]
    r.update(status='VISUALLY_REVIEWED_LOCAL_NOT_COORDINATOR_ACCEPTED', semantic_family=family,
             family_representative=f'VIS-{rep:03}', distinct_family_proposed_credit=credit,
             observation_zh=note, limitation=limit, scope='targeted_symbol_composition',
             applicable_targets_proposal=targets, applicability='composition-only, not actual bound texture/UV/game acceptance',
             inspected_detail_view=r['review_sheet'], counts_as_runtime_or_new_production=False,
             coordinator_accepted_new_visual_credit=0)
    rows.append(r)
out = dict(recorded_at=datetime.now(timezone.utc).isoformat(), viewed_pngs=len(rows),
           proposed_distinct_design_families=sum(r['distinct_family_proposed_credit'] for r in rows),
           coordinator_accepted_new_visual_credit=0, production_gate_met=False,
           policy='Actual 45 PNGs opened; new family proposals are pending global historic semantic dedup and target-specific review. Eight prior glyph families reused across sources/materials are not counted again. No code, game, architecture or production credit.', rows=rows)
(D / 'review-batch-05.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'}, ensure_ascii=False))
