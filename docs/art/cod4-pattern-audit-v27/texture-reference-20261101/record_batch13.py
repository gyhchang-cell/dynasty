"""Manual comparison of the eighteen remaining slate/sigil source images."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-13-candidates.json').read_text())['rows']
N={
497:('EXCLUDE-slate-tier-carrier',497,0,'灰黑石片中一条左上亮脊，中央是粉白短斜簇，右侧横纹宽而暗。','同石坯等级内核只换色/短簇，和恶魔、空灵、灌注、强化板合并，不计五种身份。',[]),
498:('malum-fork-hook',49,0,'黄色三根短上柱由一条横干连接，中轴向下分叉成两足。','沿用叉钩主干族；主符黄亮和石坯灰暗面积有差异，不当真实发光验收。',['chiling_brush','leifu_staff']),
499:('malum-bent-flow',48,0,'绿色粗弧上宽下开口，左下向内转一短足，内部石面保留大孔。','与弯流/回钩组织合并；启停499/500同设计，不算两个弹跳符。',['chiling_brush']),
500:('malum-bent-flow',48,0,'同一粗弧与短足变暗绿，石坯轮廓及内孔位置均未变化。','仅状态明度不同，沿用499观察，不加数。',['chiling_brush']),
501:('EXCLUDE-slate-tier-carrier',497,0,'与空白石板同壳、同左上亮脊，中心小簇改成淡黄绿。','等级核换色不是新的主干/纹章设计，不凭 demonslate 名称计帝纹。',[]),
502:('EXCLUDE-slate-tier-carrier',497,0,'同灰石坯中央改为淡紫白斜簇，右侧仍是同宽暗横纹。','与等级石板合并；紫色不自动等于全新学院身份。',[]),
503:('malum-stacked-bars',52,0,'三条黄橙横段穿过一根竖干，上宽下短，下端分为两短足。','与已有堆横主干合并；麦穗/丰收名称不作为当前身份完成证据。',['chiling_brush']),
504:('malum-stacked-bars',52,0,'相同三横/竖干与双足变为暗赭橙，宽度节奏未改变。','启停状态与503合并，不凭亮暗拆例。',['chiling_brush']),
505:('EXCLUDE-slate-tier-carrier',497,0,'同灰石片内核为青白短斜簇，外壳裂纹位置保持。','只换等级内核颜色，仍为同石坯案例。',[]),
506:('malum-fork-hook',49,0,'橙色长中轴，上端与左右短上柱相接，下方两足不等长，亮色偏上部。','结构仍属已读叉钩；只记录重心和分叉，不按 lava 词根额外建新火符。',['leifu_staff','chiling_brush']),
507:('EXCLUDE-literal-tool-pictogram',507,0,'黄色/橙色横折头像镐头，斜杆从左上通向右下末端。','工具象形不是用于现有武器的专属方令刻纹，不直接借原版工具轮廓。',[]),
508:('EXCLUDE-literal-tool-pictogram',507,0,'同镐头和斜杆变暗橙，亮头缩为少量灰黄块。','和507同状态设计，不另算物品/符纹。',[]),
509:('EXCLUDE-slate-tier-carrier',497,0,'石坯中心短斜簇改为薄荷绿，灰白亮脊及右侧暗纹不变。','五张等级石板保守合并，不把内核材质换色拆为新纹章。',[]),
510:('bloodmagic-upper-bar-hanging-loop',510,1,'红粉上横首向左垂短竖，右下接一个大暗孔的下挂环；上首与环之间有明确窄连接。','仅为上首/下挂环构图候选，与纯闭菱或单回钩不同；全局旧参考仍待排重，不当已有刻纹完成。',['chiling_brush']),
511:('open-comb-rune',159,0,'金黄三条短横臂从右侧竖脊伸向左，左上白亮块作端点，下端有短足。','与开梳主干的转向版本合并；不能因多一亮端另计身份。',['chiling_brush']),
512:('malum-stacked-bars',52,0,'蓝紫三条横段在右侧收成回折，顶端一块白亮面，下缘两条短竖。','仍借堆横/短竖节奏；和513启停为同设计，不计两个能力符。',['chiling_brush']),
513:('malum-stacked-bars',52,0,'同横段与底部双竖变暗蓝紫，石底亮脊仍白灰，符与石底对比下降。','与512合并；对比下降作为状态读图限制记录，不改变本项目透明度。',['chiling_brush']),
514:('EXCLUDE-narrow-container-component',514,0,'灰边窄斜管内是连续红色像素，宽度约两格，没有独立纹章面。','容器组件不适合当前学院/帝王身份符纹；不为凑数扩成新设计。',[]),
}
for r in rows:
 n=int(r['reference_id'].split('-')[1]);family,rep,credit,note,limit,targets=N[n]
 r.update(status='VISUALLY_REVIEWED_LOCAL_PIXEL_ART',semantic_family=family,family_representative=f'VIS-{rep:03}',
  distinct_family_proposed_credit=credit,scope='partial_composition',observation_zh=note,limitation=limit,
  inspected_detail_view=r['review_sheet'],applicable_targets_proposal=targets,coordinator_accepted_new_visual_credit=0)
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),
 proposed_distinct_design_families=sum(r['distinct_family_proposed_credit'] for r in rows),
 coordinator_accepted_new_visual_credit=0,production_gate_met=False,
 policy='18 actually opened source PNGs. Five slate tiers merge; four active/inactive pairs merge. Common glyph organizations reuse earlier families. One hanging-loop/header candidate pending global semantic review; no target or runtime acceptance.',rows=rows)
(D/'review-batch-13.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
