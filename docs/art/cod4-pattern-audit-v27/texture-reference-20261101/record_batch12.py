"""Manual observations after opening all three pinned addon-focus sheets."""
from pathlib import Path
from datetime import datetime, timezone
import json
D = Path(__file__).resolve().parent
rows = json.loads((D/'batch-12-candidates.json').read_text())['rows']
# Conservative reuse: an addon namespace or different spell name is not novelty.
N = {
469:('open-tapered-vortex',180,'紫色宽折带从上部绕向中央暗孔，下端收窄；外侧棕灰框不参与内符。','与已读收束旋涡合并，只借主块和负空间，不复制发光紫边。',['liuyun_sword','chengying_sword']),
470:('EXCLUDE-common-focus-carrier',470,'深紫环沿八个方向凸出短方块，中央十字状大暗孔，没有独立主干。','共同焦点外壳与角点不构成专属身份，不能把八个凸块计八例。',[]),
471:('EXCLUDE-common-focus-carrier',470,'深紫盘内有偏向左上的浅紫粗环，右下留黑孔，局部亮块仅三阶。','一般环孔与覆亮位置不能单独成为新符族，也不作为完整护卫装饰。',[]),
472:('EXCLUDE-fragmented-crystal-pictogram',472,'绿色背景上多块白粉紫斜片交叠，暗碎片之间有很多单像素分隔。','晶簇象形而非当前律令纹样；不把碎高光的密度当精致标准。',[]),
473:('EXCLUDE-ambiguous-split-disc',473,'灰白圆面被纵向大黑裂隙分开，右侧灰块更宽，上下都有短阶梯边。','当前只能确认明暗分裂，不能凭 ashen_breath 名字认定为云、风或影身份。',[]),
474:('EXCLUDE-literal-weapon-pictogram',474,'棕色直长杆竖贯中心，右侧青色弯板、左下深蓝段，外场红绿。','这是杆/刃器物组合，不是兵器表面的纹章设计；避免直接挪用图标。',[]),
475:('EXCLUDE-character-face-pictogram',475,'灰黑罩壳中横置两根青眼线，下方两条浅色竖条像牙或面罩边。','头脸造型不借名作帝王护卫甲参考。',[]),
476:('EXCLUDE-character-face-pictogram',475,'棕黑脸块仅露出两点青眼和中央暗口，亮点高度一致。','与上一头脸归同类排除；换头盔轮廓不能充符纹数量。',[]),
477:('EXCLUDE-ambiguous-inset-plate',477,'金棕框内为左右不同明度的蓝灰板，中央斜折暗缝连接上下。','仅看到通用嵌板，不把 tomb 名称或斜暗缝当独立帝纹。',[]),
478:('EXCLUDE-character-face-pictogram',475,'蓝黑上盖有一条灰横棱，下方红橙方形口或核心，四角用暗红收边。','读形为面罩/核心象形，非本项目稳定刻纹；不误作实际激光反馈。',[]),
479:('EXCLUDE-ambiguous-inset-plate',477,'棕金盘内部为浅色不规则折面和细窄暗缝，中央一小块黄亮面。','结构偏面板/石块，不能因沙漠名称追加山岳护卫符。',[]),
480:('EXCLUDE-character-face-pictogram',475,'骨白长中轴将棕灰脸分开，下方小口，两侧各一点暗橙眼。','面部语义清楚，与当前方令纹样无关。',[]),
481:('open-comb-rune',159,'大白色底部横块托起三根向上分叉柱，柱间留灰色深槽。','与已有开梳主干合并，只借底部承托和三柱间距，不能认作当前冲量技能。',['chiling_brush']),
482:('malum-fork-hook',49,'橙金盘中一根亮黄横首，下接向两侧分开的短折干，中间深孔宽。','保守归入已有叉钩主干；外围火焰轮廓不另计符族。',['leifu_staff','chiling_brush']),
483:('EXCLUDE-generic-bright-core',483,'黑红圆壳中心套橙、黄、浅黄三层方核，四侧有短橙块。','嵌套发亮方核过通用，没有专属主干；不能将亮度层级计新设计。',[]),
484:('EXCLUDE-character-face-pictogram',475,'深紫双角/长头罩下有左右浅灰脸侧，中部几乎全黑。','是实体头部象形，不将名字当符文语义。',[]),
485:('EXCLUDE-character-face-pictogram',475,'浅青宽帽沿上方有白灰与淡紫块，下方露出两点紫眼及横向下颌。','帽罩与脸的轮廓不能充作当前人物甲UV或符纹完整案例。',[]),
486:('parallel-falling-marks',169,'白色宽箭头朝上，金色直杆延至下缘，深蓝两侧留出大空场。','仅借箭头/轴/空场分工，与已读箭向族合并，不复制长矛物品图。',['zhuxing_bow']),
487:('EXCLUDE-character-face-pictogram',475,'锈棕面罩上深蓝双眼，左右有亮绿短块，下端为绿褐嘴部。','同类面部象形，外圈换色也不增加符纹案例。',[]),
488:('open-tapered-vortex',180,'浅黄风带上部宽，沿斜阶梯向右下收成窄尖，棕底仍连续。','与已有收束旋涡合并；不按 sandstorm 名称增加风翎身份。',['liuyun_sword']),
489:('EXCLUDE-ambiguous-layered-disc',489,'蓝色圆面横向浅深带交叠，上下边为青灰短阶梯，没有清楚的独立蛇形。','只凭 storm_serpent 名字不能当游龙或蛇类纹样；当前身份不足，保留排除。',[]),
490:('EXCLUDE-character-face-pictogram',475,'紫黑罩壳内左右浅紫折角对称，中央深长鼻/缝，下方短浅横线。','图像更接近面罩象形，不把对称亮角硬解释成律令叉符。',[]),
491:('goety-paired-inward-curls',336,'四条浅青横臂朝内折，左右各围出上下暗孔，中心保持深色贯通。','与前批双侧内卷组织合并；只研究横臂粗度和内孔，不新增另一云族。',['liuyun_sword','chengying_sword']),
492:('EXCLUDE-character-face-pictogram',475,'青黑脸侧两点浅青亮眼，顶部黄粉弧帽，下缘浅灰短横块。','仍为头部象形，不将金粉配色算帝王装饰或盔甲完整UV。',[]),
493:('EXCLUDE-character-face-pictogram',475,'浅青灰长面罩在金边内，额头纵向浅条，下方左右深色牙形。','能辨头盔但不能据 thunder 名称算雷符，限当前目标排除。',[]),
494:('malum-closed-lozenge',59,'紫色粗框围中央竖向方孔，外侧粉红小段沿上下转角排列。','闭合内孔组织已有；粉紫高亮边只作有限强调色反例，不另算新符。',['chiling_brush','supreme_sword']),
495:('open-tapered-vortex',180,'上部紫色宽折段向下收束，中央一条浅紫横亮段偏左，下尾尖窄。','与已读旋涡族合并；不按 void 改色扩成新学院。',['liuyun_sword','chengying_sword']),
496:('EXCLUDE-literal-weapon-pictogram',474,'青色场中一根较深青长杆上端开成宽叉，外侧浅青包边。','是武器象形，不能将 water 名称充风、水符纹设计。',[]),
}
for r in rows:
    n=int(r['reference_id'].split('-')[1]); family,rep,note,limit,targets=N[n]
    r.update(status='VISUALLY_REVIEWED_LOCAL_PIXEL_ART',semantic_family=family,
        family_representative=f'VIS-{rep:03}',distinct_family_proposed_credit=0,
        scope='partial_composition',observation_zh=note,limitation=limit,
        inspected_detail_view=r['review_sheet'],applicable_targets_proposal=targets,
        coordinator_accepted_new_visual_credit=0)
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),
    proposed_distinct_design_families=0,coordinator_accepted_new_visual_credit=0,production_gate_met=False,
    policy='All28 source PNGs opened. Common carriers, face/weapon pictograms and ambiguous names excluded for current identity goals; relevant glyph organizations merge with earlier families. Zero new proposals, not28 cases.',rows=rows)
(D/'review-batch-12.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
