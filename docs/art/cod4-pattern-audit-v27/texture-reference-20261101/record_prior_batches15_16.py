"""Manual source identity review after animated-strip layout was corrected."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
x=json.loads((D/'prior-batches15-16-pairs.json').read_text())
notes={
547:'旧紫晶胸甲图标的白紫上沿、青黑底部与当前同名套图集材料分区一致；胸甲与穿戴展开按同装备复用，不算新甲。',
549:'旧钨胸甲是深灰大板、浅绿横嵌件与暗边，当前同源图集继续同结构；疣化红版本也保守并入，不重复加例。',
553:'旧刷怪笼甲图标实际是深蓝/灰蓝宽甲片、深色中央留孔，当前同源穿戴图集对应同材料；不是凭 spawner 名字认作笼子。',
555:'旧两栖靴PNG为16x192十二帧，已读mcmeta并逐帧核看：绿鞋身、灰白端盖，只在局部闪亮点变化。当前同源穿戴图集沿用绿硬件/灰白分材，按已有装备复用；十二帧不拆计。',
579:'旧9.5.13根靴图标有棕色带面、绿色根结；当前9.5.16穿戴图集中同根/棕带结构。版本不同保留来源，但按同名同设计装备复用，不推断UV数值相同。',
}
for r in x['rows']:
 n=int(r['current_reference'].split('-')[1])
 r.update(status='VISUALLY_COMPARED_SOURCE_AND_PRIOR_ICON_NOT_INDEPENDENT_ACCEPTANCE',accepted_credit=0,
  observation_zh=notes[n],slot_comparable=True,novelty_decision='ALREADY_STUDIED_EQUIPMENT_CASE',
  comparison_limit='物品/穿戴材质同设计排重；不声明完整UV绑定、动画运行时或三维穿戴通过。')
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),new_credit=0,prior_icons_actually_reopened=5,
 same_equipment_reuse_rows=5,animated_source_pngs=1,animation_tiles_not_equipment_cases=12,
 rejected_near_name_lookup=x['rejected_near_name_lookup'],
 reviewer='same agent visual review, not independent/coordinator acceptance',rows=x['rows'])
(D/'prior-batches15-16-semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
