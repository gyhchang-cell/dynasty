"""Record the actual second-pass visual comparisons; no automatic semantic credit."""
import json
from pathlib import Path
from datetime import datetime, timezone

D = Path(__file__).resolve().parent
paired = json.loads((D / 'prior-case-pairs.json').read_text())
notes = {
    'irons_spellbooks:archevoker': ('旧图标用宽金领襟包住黑衣中央，肩部灰阶块很大；现图集以细金滚边、腰扣和大片炭黑分区表达同一套装备。', '只能学习金边与底衣的面积主次，图标夸张边宽不能直接搬到穿戴 UV。'),
    'irons_spellbooks:cryomancer': ('旧图标冰白肩领围住深青躯干；现图集同样白外层与深青底衣分离。已核过的 armorBody 首块实际为深青，不能按整图白色占比猜胸面。', '同装备复查，逐面 UV 是补充证据，不另算一套；其他岛的白色不用于替代胸面。'),
    'irons_spellbooks:pyromancer': ('旧图标深红兜帽外轮廓、黑色内开口与孤立金扣；现图集黑红衣片和少量金点延续同类层级。', '版本和图标抽象程度不同，不足以认定是全新设计。不能据静态图推断发光或施法效果。'),
    'irons_spellbooks:shadowwalker': ('旧图标方肩灰黑包裹、紫色小颈饰；现图集多段暗包带、细银链和很少紫色。', '银链属于局部结构，不能变成整衣亮描边；同装备图标/图集不重复计。'),
    'irons_spellbooks:paladin': ('旧图标以宽金肩和中央 V 亮面读形；现图集另分灰链甲区域，金板与柔性连接不共用满亮材质。', '同装备增加材质阅读深度，不能作为另一套盔甲。box UV 未验证前不声称完整面对应。'),
    'enigmaticlegacy:crying': ('旧图标紫板、中央高亮紫宝石与两侧金褐连接点；现图集延续局部紫亮心和少量金边。', '同设计复查，不能将高亮点扩成全板霓虹或增加新案例。'),
    'aether:valkyrie': ('旧图标白青大板、少量金节点和底边；现图集保留白金主次，金色没有填满整个表面。', '同套上下层/经典版均合并；只借白金面积关系，不搬原纹。'),
    'aether:neptune': ('旧图标蓝色原版胸甲轮廓与少数硬折高光；现图集蓝板阶梯亮边，基本组织与本批其他着色板甲相近。', '与 gravitite/obsidian/zanite 已合并为着色板甲族，不能另计蓝色材质。'),
    'aether:gravitite': ('旧图标粉紫板面以几块大亮簇说明金属，现图集同色板与边缘亮块。', '图集细节更多不等于新装备案例；与同组织换色套仍归一个族。'),
    'create:copper_diving': ('旧参考只有铜色潜水靴，短 L 轮廓与几处硬高光；新参考是上身/头盔图集，含绿色观察窗。', '槽位不一致，只能暂核同套铜材质，不能做同胸形态、胸面纹样或 UV 的直接对照。'),
    'create:netherite_diving': ('旧参考为紫灰潜水靴，新参考为深紫上身/头盔图集，局部橙色节点。', '槽位不一致，同名套装只作复用候选，不能证明相同胸部设计或新增一套。'),
    'goety:cursed_paladin': ('旧图标蓝黑方肩、大块暗蓝平面和中央暗缝；现图集把同类板甲、链甲/布区分散到各岛。', '同套复查，不把图集多岛或长条拆为新参考；本批深色板链甲族仍保守合并。'),
}
rows = []
for r in paired['rows']:
    row = dict(r)
    if r['case'] in notes:
        row['status'] = 'VISUALLY_RECHECKED_SAME_CASE_NO_NEW_CREDIT'
        row['observation_zh'], row['application_limit_zh'] = notes[r['case']]
        row['slot_comparable'] = not r['case'].startswith('create:')
        row['novelty_decision'] = 'HOLD_SLOT_MISMATCH_FAMILY_ONLY' if not row['slot_comparable'] else 'ALREADY_STUDIED_EQUIPMENT_CASE'
    else:
        row['status'] = 'PENDING_PRIOR_PNG_NOT_COMPARED'
        row['observation_zh'] = '只展示了本批现图；未找到旧 PNG，不伪造旧新视觉对照。'
        row['novelty_decision'] = 'UNRESOLVED_NOT_AUTOMATICALLY_NEW'
    row['accepted_credit'] = 0
    rows.append(row)
out = {
    'recorded_at': datetime.now(timezone.utc).isoformat(),
    'reviewer': 'same chat/agent second pass, not independent reviewer or coordinator acceptance',
    'prior_icons_actually_reopened': 12,
    'slot_comparable_same_cases': 10,
    'family_only_slot_mismatches': 2,
    'missing_prior_png': 5,
    'new_visual_credit': 0,
    'prior_73_stage_proposals_unchanged_as_history': True,
    'important_boundary': 'No exact SHA match did NOT establish semantic novelty. Ten same-slot cases are historical reuse; two slot-mismatched pairs and five missing comparisons remain held. Do not subtract raw row counts from the already merged 73 families or add them to every target gate.',
    'rows': rows,
}
(D / 'prior-case-semantic-review.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, ensure_ascii=False))
