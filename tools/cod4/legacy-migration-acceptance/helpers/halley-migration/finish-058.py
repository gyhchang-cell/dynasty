# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty');D=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration';B=D/'batch-058'
b=json.loads((B/'batch-058.json').read_text());a=json.loads((B/'document-integrity.json').read_text())
(B/'semantic-duplicate-review.json').write_text(json.dumps(dict(credit=0,accepted=False,new_suggestions_pending_Kepler=2,semantic_acceptance=False,master_sha256_read_only=a['master_sha256_read_only'],master_rows_at_check=a['master_rows_at_check'],primary_mechanical_matches=a['master_primary_matches'],source_commit_reused_from_batch_053=True,supporting_methods_not_credit=True,review=[dict(family=r['family'],risk=r['semantic_duplicate_risk']) for r in b['records']],excluded=[dict(family=r['family'],reason=r['observation']) for r in b['excluded_records']]),ensure_ascii=False,indent=2)+'\n')
(B/'HANDOFF.md').write_text('''# Halley batch-058 → Kepler

2待审＋1排除，全部credit0、accepted=false。官方Betweenlands commit eafac1c217cdf304d477b025708e0dadf82b6953、tree 194e44209e5494bc78378963e15cbfc8ba944373；源与真实blob引用053。

1. 已安装两栖甲升级的磨损托管：甲槽damage与取出的最后1件storedDamage互转，randomUID阻堆叠；shift-click失败保甲槽、清临时件标记；hadNoNBT只在本键清除且compound空时去tag。物理Items与counts/worn快照不是同一事实，读库存未自动重算counts；本项含真实效果和消耗消费者。四装备/升级种类/每key/GUI支持都合1。
2. 幼体已支付投喂/孵化进度与旧Owner名回退UUID：reader新OwnerUUID即使空也优先旧Owner，解析catch没有先clear；Facing直接数组索引、Items强转有具体错型边界。成熟时仅转owner/name/electric给新成年pet，spawn结果未确认就删除幼体。放回蛋会将owner重设为放置玩家，因此不能说原归属总保留。普通/电性/野生分支同发育链合1，常见原生owner converter本身不额外计数。

排除：InventoryItem注释里的旧ItemInventory loop不执行，不是现行格式fallback；基类支持0。完整方法/输入输出/逐项观察应用限制风险见JSON。

文档核对0源hash/AST错误。174支持方法/117字段不是实现数量；只读主账1243行快照主方法机械0匹配仍待最终语义去重。无编译、测试、上游/原生owner查询执行、游戏、GUI或屏幕操作；不改主账生产待办原档。十小时最低时段尚未到，继续Draeton嵌套载体与其他独立状态审查。
''')
p=D/'CONTINUATION-20261028.json';c=json.loads(p.read_text());c['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();c['manual_suggestions_not_accepted_credit']['batch-058']=2
for f in B.iterdir():
 if f.is_file():c['files'][str(f.relative_to(D))]=hashlib.sha256(f.read_bytes()).hexdigest()
c['current']='0582pending1excluded ready handoff; continueDraeton nested carrier.10hminimum incomplete.';p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print('058 ready credit0')
