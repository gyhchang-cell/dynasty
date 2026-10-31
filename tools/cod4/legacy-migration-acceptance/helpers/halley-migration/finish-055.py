# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty');D=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration';B=D/'batch-055'
b=json.loads((B/'batch-055.json').read_text());a=json.loads((B/'document-integrity.json').read_text())
(B/'semantic-duplicate-review.json').write_text(json.dumps(dict(credit=0,accepted=False,new_suggestions_pending_Kepler=3,master_sha256_read_only=a['master_sha256_read_only'],master_rows_at_check=a['master_rows_at_check'],primary_mechanical_matches=a['master_primary_matches'],semantic_acceptance=False,source_commit_reused_from_batch_053=True,supporting_methods_framework_tables_pet_variants_never_credit=True,review=[dict(family=r['family'],risk=r['semantic_duplicate_risk']) for r in b['records']],excluded=[dict(family=r['family'],reason=r['observation']) for r in b['excluded_records']]),ensure_ascii=False,indent=2)+'\n')
(B/'HANDOFF.md').write_text('''# Halley batch-055 → Kepler

3条待审建议＋1显示迁移排除，全部credit0、accepted=false。同官方The Betweenlands commit eafac1c217cdf304d477b025708e0dadf82b6953、tree 194e44209e5494bc78378963e15cbfc8ba944373；原始source、Git blob等引用053，未重复下载。

1. GatheringRing按owner UUID离线托管真实宠物：死亡/卸载收回，条件取回才删queue。四宠物及Animator入口/30秒缓存都同链合1。addEntry仅接受缓存便移除实体、保存失败仍evict、tmp覆盖先删旧file再rename、未注册entity先null访问及spawn布尔忽略，不能声称无损/一次成功生成。lastUserUUID价格查询与实际playerUUID取回还不同。
2. CompostBin旧键实际类型冲突：Items INT_ARRAY写Inventory INT_ARRAY，父reader却只收compound且先清物理槽；旧新共存还会旧覆盖新。长度不符的并行数组整组置0但不重算总量。完整tick/真实投入和产物消费者已读，这是兼容缺陷反例，绝不标旧档恢复成功。
3. 旧两维portal缺目标维度：依据当前world/配置补0或BL，新INT目标字段优先；要有对端位置或TargetDimSet才由玩家tick使用。支持factory/file/region/真实portal验证消费。配置变化、空bounds、缺PortalPos为0坐标等边界明确。

排除：LocationStorage version0仅修title可见性/translate:name，10名/每键都0信用，不从portal父链再拆。

完整方法、具体触发/输入/输出/观察应用限制及重复风险见batch-055.json和reviewed-suggestions.jsonl。文档核对0哈希/AST错误；244方法/188字段仅支持规模，主账1228行只读快照机械主方法0匹配不等于接受。请跨已有宠物召回/Waystones等最终去重。

无上游执行/编译/测试/游戏/服务器/GUI/屏幕操作，无主账、生产、待办和原存档变更。十小时工作最低时段仍未宣称完成，继续同源独立持久领取/战利品状态审查。
''')
p=D/'CONTINUATION-20261028.json';c=json.loads(p.read_text());c['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();c['manual_suggestions_not_accepted_credit']['batch-055']=3
for f in B.iterdir():
 if f.is_file():c['files'][str(f.relative_to(D))]=hashlib.sha256(f.read_bytes()).hexdigest()
c['current']='055 threechain suggestions+oneUIexclusion packaged/audited,readyhandoff.053/054delivered4+4.Continue Betweenlands durable loot/claim history;10hminimumincomplete.';c['reservations']['batch-055']='SameBetweenlands fixed053commit GatheringRing escrow+Compost legacyTypeMismatch+oldPortal dimensionfallback3pending';p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
print('055 ready credit0')
