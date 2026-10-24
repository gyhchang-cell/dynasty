"""Synchronize README checkpoints only from the verified published research."""
from pathlib import Path
import json,re
b=Path(__file__).resolve().parent;s=json.loads((b/'evidence/armor-references.json').read_text())['summary'];p=b/'README.md';t=p.read_text()
state='专属研究已补足（事后补读）' if s['gate_met'] else '专属研究持续进行'
t=re.sub(r'\*\*专属研究[^\n]*?\*\*',f"**{state}，当前核验检查点：{s['accepted_implementation_sites']}/1000，仍缺{s['shortfall']}。**",t,count=1)
c=s['review_decisions'];t=re.sub(r'原593个候选[^\n]*',f"原593个候选（其中原先340处未审）已经全部逐段结案，接受301处、排除292处。之后扩大到事件、能力、属性和冷却辅助方法，补取完整固定版本Java源码。最新扫描涉及{s['source_files_scanned']}个Java物理文件路径（跨缓存可重复）；{s['candidate_methods']}个归一化候选不是有效参考数。目前逐段接受{c['accepted']}处、排除{c['excluded']}处、尚未计入{c.get('not_accepted_unreviewed',0)}处。未声称穷尽所有外部源码。",t,count=1)
t=t.replace('已读冷却NBT、登录状态恢复没有旧ID映射，不计该迁移门槛。','已读冷却NBT、登录状态恢复没有旧ID映射，不计该迁移门槛；候选2728已实际读到Accessories旧字段改名，作为独立队列交叉线索保留，但没有registry旧物品ID映射，也未纳入独立迁移门槛。')
p.write_text(t)
