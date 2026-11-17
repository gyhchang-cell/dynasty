# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty');D=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration';B=D/'batch-054'
b=json.loads((B/'batch-054.json').read_text());a=json.loads((B/'document-integrity.json').read_text())
(B/'semantic-duplicate-review.json').write_text(json.dumps(dict(credit=0,accepted=False,new_suggestions_pending_Kepler=4,master_sha256_read_only=a['master_sha256_read_only'],master_rows_at_check=a['master_rows_at_check'],primary_mechanical_matches=a['master_primary_matches'],semantic_acceptance=False,source_commit_reused_from_batch_053=True,supporting_same_chain_nodes_never_credit=True,review=[dict(family=r['family'],risk=r['semantic_duplicate_risk']) for r in b['records']],excluded=[dict(family=r['family'],reason=r['observation']) for r in b['excluded_records']]),ensure_ascii=False,indent=2)+'\n')
(B/'HANDOFF.md').write_text('''# Halley batch-054 → Kepler

4条待审建议，全部credit0、accepted=false；1条排除。沿用053同一真实官方commit eafac1c217cdf304d477b025708e0dadf82b6953 / tree 194e44209e5494bc78378963e15cbfc8ba944373，源码、commit/tree/blob元数据只引用053，不重复下载，不计来源/方法数。MC1.12.2/mod3.9.6。

- 装备真实栈＋购买护符槽数＋圆宝石镜像合为1：keepInventory条件复制；读回直接数组不重放onEquip，宝石另行持久化支持同装备状态。负槽只查上界、隐藏槽、死亡canDrop=false仍最终clear等边界已记录。不把镜像或每类别拆信用。
- 饮食厌恶记忆1：恒true跨Clone，仅HatredMap白名单，lastSickness反馈缓存不保存。真实食用消费者有惩罚，这是上游设计观察，禁止引入本项目新死亡惩罚。
- 玩家携带乘客1：断线取消dismount保护保存，实体完整NBT读入queue、login后实例化；未清queue/确认startRiding，writer未写未实例化queue，不能声称幂等无损。默认只非死亡Clone。
- 付供品坐标祝福1：三坐标类型齐全才恢复、同维度濒死取消死亡后消费。不是死亡后永久Clone；未核旧塑像仍存在。经验损失/半血等均为上游观察，绝不实施于本项目。

排除0：PlayerPersisted中的respawn_in_bl是临时路由，不能因所在根被原生保留而扩大永久进度白名单。

完整方法与字段、source/excerpt/normalized SHA256、line范围、Git blob见batch-054.json/reviewed-suggestions.jsonl。文档核对0错误；183完整方法/86字段/2静态块仅支持规模。主账1221行只读快照、机械primary匹配0，并非语义接受。需特别复核与Curios/Accessories、Diet/SoL、Anthropophagy及实体重建家族的重复风险。

研究静态且仅写Halley工具/文档；无游戏/GUI/屏幕/测试/编译/上游执行，无主账/生产/待办/原存档变更。继续同源GatheringRing实际离线宠物持久化链审查，十小时最低时段未宣称完成。
''')
p=D/'CONTINUATION-20261028.json';c=json.loads(p.read_text());c['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();c['manual_suggestions_not_accepted_credit']['batch-054']=4
for f in B.iterdir():
 if f.is_file():c['files'][str(f.relative_to(D))]=hashlib.sha256(f.read_bytes()).hexdigest()
c['current']='054 4 chain suggestions+1exclusion audited,readyhandoff;053delivered4.Continue fixed Betweenlands GatheringRing actual offline entity persistence chain;10hminimumincomplete.';c['reservations']['batch-054']='Betweenlands same053fixedcommit concrete equipment/food/passengers/blessing4pending;supportmirrorcombined0extra';p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
print('054 handoff ready credit0')
