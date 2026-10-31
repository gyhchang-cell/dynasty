# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
D=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
B=D/'batch-053';data=json.loads((B/'batch-053.json').read_text());audit=json.loads((B/'document-integrity.json').read_text())
review={'credit':0,'accepted':False,'new_suggestions_pending_Kepler':4,'master_rows_read_only':audit['master_rows_at_check'],'master_sha256':audit['master_sha256_read_only'],'primary_mechanical_matches':audit['master_primary_matches'],'same_repo_master_rows_at_read':0,'not_a_semantic_acceptance':True,'families':[{'family':r['family'],'distinction':r['observation'],'risk':r['semantic_duplicate_risk']} for r in data['records']],'excluded':[{'family':r['family'],'reason':r['observation']} for r in data['excluded_records']],'support_policy':'Tile registry/table rows, MissingMappings, NBT writers/readers, framework callbacks and consumers support their parent family only; no per-key/color/item/method/download credit.'}
(B/'semantic-duplicate-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
(B/'HANDOFF.md').write_text('''# Halley batch-053 → Kepler

4条实际完整链研究建议，1条排除；全部credit0、accepted=false，待主责跨账语义去重。只读主账快照1214行（不是接受数），该快照无The Betweenlands来源行，机械主方法匹配0不代表新信用已认证。

官方来源Angry-Pixel/The-Betweenlands，branch `1.12-fixes`；commit `eafac1c217cdf304d477b025708e0dadf82b6953`，Git tree `194e44209e5494bc78378963e15cbfc8ba944373`。ModInfo声明MC1.12.2/mod3.9.6。真实Git commit/tree/blob和原始文件SHA256见tools/batch-053，未运行上游。完整方法行范围、全文、摘录及归一化哈希见batch-053.json和reviewed-suggestions.jsonl。

- 旧gecko/firefly → CRITTER：注册别名与物品NBT转换合一族。new ItemStack+新compound重建Entity.id，原Count/tag等没有显式迁移，作为防丢失反例。释放读取端已追到真实Entity反序列化，spawn布尔结果未检查。两旧ID不能拆计。
- 旧方块实体ID：冻结历史表，原地只改id保留其余compound；追到真实新TE注册及purifier库存/水/加工消费者。33个映射项、机器reader、框架不另计。
- 手册发现知识：实际物品持久集合、多手册union和服务端付材料发现写回。不是玩家Clone能力。未知类型null未过滤、列表长度完成判定和共享列表存在风险。
- 世界随机元素分配：读回已有分配后仅补当前新注册物品；坏类型丢整个item条目可能导致重新随机。真实世界cap与物品数量/Infuser入槽消费者已补证。

排除：checkForLegacyPouch只补type颜色默认值，未恢复库存/任务/Clone进度。

文档完整性核对：选中证据0解析/哈希错误。230完整方法、420字段及3静态初始化只是支持证据规模，2117静态文件不是信用；4个非UTF8上游文件原始字节保留、从AST索引排除，详见unparsed-source-inventory-not-credit.json，未改编码或计为已读。没有声称全仓已研究。

另：batch-051/piggy-recolor-support-0.json已补钱罐整份NBT深拷贝及物理库存支持；新增建议0，所有颜色与通用容器生命周期不拆计。

只写Halley工具/文档目录；未改主账、生产、待办或原存档，未编译/测试、启动游戏、服务器、GUI或操作屏幕。十小时实际工作最低时段尚未完成声明，继续同固定来源的独立Clone/持久对象审查。
''')
p=D/'CONTINUATION-20261028.json';c=json.loads(p.read_text());c['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();c['manual_suggestions_not_accepted_credit']['batch-053']=4
for f in B.iterdir():
 if f.is_file():c['files'][str(f.relative_to(D))]=hashlib.sha256(f.read_bytes()).hexdigest()
c['current']='053 4 hand-reviewed chain suggestions +1color exclusion packaged/audited, handoff ready. Continue Betweenlands fixed commit independent Clone/persistent objects; 2117files/18558AST are not credit. Ten-hour minimum not complete.'
c['reservations']['batch-053']='Angry-Pixel/The-Betweenlands eafac1c217cdf304d477b025708e0dadf82b6953 exclusive; acquired complete,4suggestions pendingKepler; further concrete player Clone/persistent semantics reserved.'
p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
print('053 concrete handoff ready;credit0')
