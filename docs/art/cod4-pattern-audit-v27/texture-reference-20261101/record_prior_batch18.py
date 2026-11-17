"""One visually reopened historical bow is reuse, despite the pack-folder change."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
x=json.loads((D/'prior-batch18-pairs.json').read_text())
r=x['rows'][0]
r.update(status='VISUALLY_COMPARED_SOURCE_AND_PRIOR_PNG_NOT_INDEPENDENT_ACCEPTANCE',slot_comparable=True,
 novelty_decision='ALREADY_STUDIED_EQUIPMENT_CASE',accepted_credit=0,
 observation_zh='旧第92号与当前VIS-692均为暗紫棕弓身、灰握点、金黄横扣和米白阶梯弦，源PNG逐字节相同；不同整合包文件夹不生成新装备。已实际打开双图对照页。',
 comparison_limit='只排同源图标重复；未验游戏握持、状态谓词、整体UV或当前王朝目标身份。')
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),prior_icons_actually_reopened=1,same_equipment_reuse_rows=1,
 new_credit=0,reviewer='same agent visual source comparison, not independent acceptance',rows=x['rows'])
(D/'prior-batch18-semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Historical bow reuse confirmed; accepted new credit0.')
