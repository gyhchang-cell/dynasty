# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty');D=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration';B=D/'batch-056'
b=json.loads((B/'batch-056.json').read_text());a=json.loads((B/'document-integrity.json').read_text())
(B/'semantic-duplicate-review.json').write_text(json.dumps(dict(credit=0,accepted=False,new_suggestions_pending_Kepler=2,semantic_acceptance=False,master_sha256_read_only=a['master_sha256_read_only'],master_rows_at_check=a['master_rows_at_check'],primary_mechanical_matches=a['master_primary_matches'],supporting_methods_not_credit=True,source_commit_reused_from_batch_053=True,review=[dict(family=r['family'],risk=r['semantic_duplicate_risk']) for r in b['records']],excluded=[dict(family=r['family'],reason=r['observation']) for r in b['excluded_records']]),ensure_ascii=False,indent=2)+'\n')
(B/'HANDOFF.md').write_text('''# Halley batch-056 → Kepler

2条待审建议、1条排除，全部credit0/accepted=false。沿用053官方The Betweenlands固定commit eafac1c217cdf304d477b025708e0dadf82b6953、tree 194e44209e5494bc78378963e15cbfc8ba944373和原始source/blob；没有重复下载计数。

1. 区域共享战利品：容器持久StorageID连接共同pool，恢复已分配数量、种子和保底次数。生成前先清容器LootTable，扣共享量后填槽，部分填充失败不退款；item匹配未核NBT/metadata，临时EntryKey不比较poolRoll，空栈分支重复iterator.remove。storage原始lootSeed未保存（已建pool自身seed有保存），不能称所有未来pool随机状态无损。pot/chest、种子、保底、refill/regenerate全部同链合1。
2. 真正蟹笼生产：tile捕获timer和本地fraction/时间戳连接持久区域预算、卸载票据保留量；每20tick实际消费推进后捕获实体变物品。OwnerUUID读要求STRING而writer setUniqueId、重新new TokenBucket后reader未重绑world/pos，是明确恢复边界；不声称外部原生加载顺序已动态验证。所有token类只是这个真实玩法对象的支持，不计通用限流/缓存信用。

排除：SpiritTreeKillToken只定位到真实击杀生产、列表读写，未找到玩家进度/领取等玩法消费者，0信用；不因kill/token/NBT字样纳入。

完整方法/具体观察与限制/去重风险见JSON。文档核对0哈希或AST错误；190方法、184字段仅支持规模，绝非有效实现数。主账1237行只读快照主方法机械0匹配仍需语义去重。本批未完整读巨型tower生成方法（截断），明确只选完整的小绑定/入口方法。

无编译/测试/上游执行/游戏/服务器/屏幕操作；不改主账、生产、待办或原档。十小时最低时段尚未结束，继续实际其他独立数据对象审阅。
''')
p=D/'CONTINUATION-20261028.json';c=json.loads(p.read_text());c['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();c['manual_suggestions_not_accepted_credit']['batch-056']=2
for f in B.iterdir():
 if f.is_file():c['files'][str(f.relative_to(D))]=hashlib.sha256(f.read_bytes()).hexdigest()
c['current']='056 two pending chains plus spirit token exclusion audited, ready handoff; continue actual Betweenlands durable object review; ten-hour minimum incomplete.';p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
print('056 ready credit0')
