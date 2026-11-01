"""Conservative manual composition review of forty-one actual focus icons."""
from pathlib import Path
import json
from datetime import datetime, timezone
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-10-candidates.json').read_text())['rows']
# family, representative, proposal only, concrete observation, scope limit, target proposal
N={
322:('parallel-falling-marks',169,0,'斜向灰白小箭叠在深绿焦点中，箭杆/箭尖仍可分。','只借多标记方向分工；与已读落箭族合并，不照搬箭物品像素。',['zhuxing_bow']),
323:('EXCLUDE-generic-focus-disc',323,0,'紫色同心粗环围小孔，棕框承载轮廓。','通用圈孔没有足够学院身份；共同焦点外壳不计新设计。',[]),
324:('EXCLUDE-character-face-pictogram',324,0,'黑盔绿脸，正中红色额点；五官用短横分区。','这是脸谱图标，不是当前帝王护卫纹章；不因名字 blackguard 就充作护卫甲。',[]),
325:('paired-post-gap',164,0,'三根浅黄竖柱压在金底上，中间留暗缝。','与柱/间隙组织保守合并；不能把三柱数当三种纹样。',['chiling_brush']),
326:('EXCLUDE-bright-impact-cluster',326,0,'橙红盘内三团黄白亮点与暗连线。','整体读成爆炸团，不适合当前稳定的刻纹；不借全图高饱和亮点。',[]),
327:('silver-shield-blue-field',168,0,'灰白盾占中心，蓝青外场分段围盾，盾内保持大白面。','与先前银盾蓝场合并；不能直接复制原版盾形去冒充新帝纹。',['zhenyue_blade']),
328:('EXCLUDE-focus-state-ring',328,0,'青黑粗环中心全黑，亮点只在两处转角。','和启用/类型及军团状态成同一焦点状态对照；空壳不计身份案例。',[]),
329:('EXCLUDE-focus-state-ring',328,0,'同壳启用后中心出现绿横块和两点洋红，轮廓不变。','状态内符不能拆成一整套新设计；未查看动画/程序，不声称状态时序。',[]),
330:('EXCLUDE-focus-state-ring',328,0,'同一青环内换成下伸青块和洋红横叉。','只记录同款可变内符，不因颜色和开关另计。',[]),
331:('EXCLUDE-motion-body-pictogram',331,0,'金底上的白灰折形有一长下肢和横伸部，读成运动人物。','动作小人不是当前方令/云折纹样，不按 charge 名称认定冲量反馈已完成。',[]),
332:('quadrant-linked-square-crosses',3,0,'紫黑底上四端小方孔经灰蓝折线相连。','与已有四结方阵组织合并；只借节点连通与留孔，不复制内符。',['chiling_brush','supreme_sword']),
333:('open-tapered-vortex',180,0,'青白旋风从宽横帽沿收成下方小钩，暗侧宽度有变化。','与既有收束旋涡族合并；图标不是游戏内云龙或残影证据。',['liuyun_sword','chengying_sword']),
334:('branched-lightning-fold',171,0,'橙金背景中一根白色折闪，上下粗段错位，节点留硬边。','雷折组织已有；橙底不能使同构雷折变新学院。',['leifu_staff']),
335:('malum-tree-fork',60,0,'棕绿底中央黄绿粗主干向四周分叉，分叉端短。','保守归到树叉主干；不可据图标名称宣称已绑敌。',['chiling_brush']),
336:('goety-paired-inward-curls',336,1,'青白上帽下接两条向内卷的侧臂，中央直柱粗，左右卷端留深孔。','可借双侧卷折和中轴留白，不把飞行功能移给云剑。',['liuyun_sword','chengying_sword']),
337:('EXCLUDE-simple-inset-plate',337,0,'黑灰外圈中是绿色嵌套直角长板，中亮边暗。','只是一块通用嵌板，缺少当前专属身份；不是完整穿戴材质案例。',[]),
338:('malum-fork-hook',49,0,'青底灰白折线一端为箭尖，另一端回钩，留一个小方孔。','钩/叉主干已有，方向头只作局部观察，不新增一把武器设计。',['chiling_brush']),
339:('EXCLUDE-generic-focus-disc',323,0,'黄绿边框内是粉紫盘与少量同心折块。','颜色和圆盘套层不足以成为独特徽纹。',[]),
340:('branched-lightning-fold',171,0,'深蓝底中白亮主闪左右折转，顶部和末端为青色小节点。','与旧雷折族合并；研究主闪与暗底面积，不使用全图发光。',['leifu_staff']),
341:('quadrant-linked-square-crosses',3,0,'暗青盘里深孔围中心相接，四角与中柱作短连接。','与 command 四结组织合并，不能因 order 名字另计。',['chiling_brush','supreme_sword']),
342:('goety-broad-cleft-crescent',342,1,'青绿盘中一片宽白弯刃从上到下收细，暗凹面留下宽缺口。','只借大色块和负空间收束；不承诺剑新增风刃技能。',['liuyun_sword','chengying_sword']),
343:('goety-opposed-turn-arrows',343,1,'黑底上灰白两根折返箭沿上下边相对转向，中间完全空出。','双箭端的转向有构图价值；无当前具体武器身份对应，不向门槛分摊。',[]),
344:('EXCLUDE-bright-impact-cluster',326,0,'蓝底中多条青白亮块交叠，中心读形密集。','细碎高亮较多，不适合当前刻纹的粗主干；不按 shocking 名称增加雷符案例。',[]),
345:('EXCLUDE-portal-pictogram',345,0,'深蓝盘内灰边长框围黑白纵向孔，像一扇开口门。','门/声波图标不等于现有兵器身份，保留观察但不计。',[]),
346:('EXCLUDE-character-face-pictogram',324,0,'浅青圆面上有两暗眼和小口，亮点面积较大。','这是一张脸样图，不按 soul_armor 误充穿戴甲图集。',[]),
347:('clustered-hard-star-points',179,0,'紫底三颗白色硬星各留暗分隔，主亮星尺度不完全一致。','与既有星点簇合并；多星不是多案例，也不证明追踪箭。',['zhuxing_bow']),
348:('EXCLUDE-literal-weapon-pictogram',348,0,'青色盘中斜放灰白剑，有短棕握柄和直护手。','完整剑物品图标不能自动充当原创剑身铭纹；避免直接改原版剑像素。',[]),
349:('EXCLUDE-ambiguous-multiring-glyph',349,0,'青色短横臂与紫色双环交错，中央为大暗孔。','原图可见但当前语义联系薄弱；不将一般环结硬套成控制符。',[]),
350:('branched-lightning-fold',171,0,'蓝场上两道近白折闪共用中间轴段，末端分开。','仍归雷折族，双道分叉不拆成两个技能或两种设计。',['leifu_staff']),
351:('EXCLUDE-bright-impact-cluster',326,0,'多条黄青亮线围成不均匀旋团，内部有暗小孔。','密集亮团不适合方令留白；当前不借光团遮盖粗像素结构。',[]),
352:('EXCLUDE-literal-weapon-pictogram',348,0,'蓝场中白灰三叉斜伸，灰柄贯穿，端部可辨。','三叉物品轮廓与弓/符身份不同，不凭 storm 词根计入风翎。',[]),
353:('EXCLUDE-focus-state-ring',328,0,'黑紫粗环中留全黑孔，和青环同类外壳结构。','与 troop active 合并状态；和 call 环壳也不靠换色新增。',[]),
354:('EXCLUDE-focus-state-ring',328,0,'紫环启用后内有蓝块、洋红横点，轮廓仍同焦点。','状态反馈只记录，不当独立艺术案例。',[]),
355:('open-comb-rune',159,0,'青底三根竖线向上伸，两侧白而中间暗绿，底部相连。','与既有开梳/竖柱族合并；上下方向不增加新符。',['chiling_brush']),
356:('EXCLUDE-literal-weapon-pictogram',348,0,'棕底灰色长剑压在盾形上，横护手清楚。','盾剑组合是物品象形，不是当前帝王铭文，不能把 vanguard 名字算帝甲案例。',[]),
357:('goety-staggered-lateral-wind-strokes',357,1,'深青盘中三条白青横风段上下错开，右端一条弯折下收，大片暗隙保留。','可借分段、错位与粗细收尾；只关联云折组织，不证明残影机制。',['liuyun_sword','chengying_sword']),
358:('open-tapered-vortex',180,0,'灰底白线沿方折内卷，中央小孔与外线分离。','与旋涡族合并，直角化只作边界校准，不另起假设计。',['liuyun_sword']),
359:('malum-bent-flow',48,0,'蓝盘内暗紫粗钩弯成问号，外弧浅，尾部收细。','与已读弯流/钩形保守合并；低对比暗符也不能生硬搬入小剑面。',['liuyun_sword','chengying_sword']),
360:('goety-opposed-wave-lobes',360,1,'深蓝场上下两片白青浪瓣相向围出中间宽黑沟，浪头大小有区别。','可借对向色块及中心留空，不复制海浪像素，不认作已经完成游龙。',['liuyun_sword','chengying_sword']),
361:('branched-lightning-fold',171,0,'蓝白两条斜亮段围暗心交错，端点青白相接。','与已有折闪/分叉亮段合并，蓝色的 surging 不必算新的风符。',['leifu_staff']),
362:('branched-lightning-fold',171,0,'近黑蓝盘顶部短暗横块，底部白色小折闪，明暗面积悬殊。','主干仍是雷折；不因 monsoon 名称误算云纹或雨序已接入。',['leifu_staff']),
}
for r in rows:
    n=int(r['reference_id'].split('-')[1]);family,rep,credit,note,limit,targets=N[n]
    r.update(status='VISUALLY_REVIEWED_LOCAL_PIXEL_ART',semantic_family=family,
        family_representative=f'VIS-{rep:03}',distinct_family_proposed_credit=credit,
        scope='partial_composition',observation_zh=note,limitation=limit,
        inspected_detail_view=r['review_sheet'],applicable_targets_proposal=targets,
        coordinator_accepted_new_visual_credit=0)
out={'recorded_at':datetime.now(timezone.utc).isoformat(),'viewed_pngs':len(rows),
    'proposed_distinct_design_families':sum(r['distinct_family_proposed_credit'] for r in rows),
    'coordinator_accepted_new_visual_credit':0,'production_gate_met':False,
    'policy':'Actual local focus-icon study. Shared focus shell, status pairs and earlier composition families merge. Names are not visual evidence, and icons are not complete UV or target designs.', 'rows':rows}
(D/'review-batch-10.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
