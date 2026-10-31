"""Source checks after manual full-chain reads, never auto-credit."""
import json,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/sweep-receipt-research'
d=json.loads((O/'helpers/apugli-rpginventory/batch-011.json').read_text());tree=json.loads((R/'tools/cod4/armor-acceptance/.work/research-sources/SlimeKnights__TinkersConstruct/tree.json').read_text())
H=lambda b:hashlib.sha256(b).hexdigest()
errors=[];support=[];seen=set()
for e in d['entries']:
 for n in e['evidence']:
  raw=(R/n['source_local']).read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  if not (H(raw)==n['source_sha256'] and H(n['excerpt'].encode())==n['snippet_sha256'] and '\n'.join(raw.decode().splitlines()[n['line']-1:n['end_line']]).strip()==n['excerpt'].strip() and any(t['path']==n['path'] and t['sha']==blob for t in tree['tree'])):errors.append([n['path'],n.get('method')])
  if n.get('method') and not(n['path']==e['path'] and n['method']==e['method']): support.append([n['source_local'],n['method'],n['line']+1])
assert not errors
note='主审全文确认tick12扫描hurt布尔→local melted→同heat phase0实际取燃料、phase3扣减余额。源当前bounds/活体/免疫/creative/抗火过滤，supplier只在首合格实体算一次；伤害true后tank.fill返回0也melted=true，不能代表产物接纳或正HP差。实体可每20tick再受击，无逐目标UUID/序列/TTL。消费fuel probe到实际drain有差异且不足仅日志仍补fuel，不是原子事务。Smeltery与Foundry共用模块合为1；此条相关性是具体游戏伤害事实汇总与分相资源结算，伤害布尔本身同步，绝非跨tick成功队列。与已审炮弹载荷/物品熔炼/一般缓存不相同；41方法及4声明不当45实现，3组排除不加信用。'
(O/'manual-chain-spec-080.json').write_text(json.dumps([dict(candidate_indices=[7531],observation=note,supporting_methods=support)],ensure_ascii=False,indent=2)+'\n')
(O/'apugli-batch-011-main-review.json').write_text(json.dumps(dict(reviewed_at=datetime.datetime.now().astimezone().isoformat(),helper_batch='helpers/apugli-rpginventory/batch-011.json',source_nodes_checked=sum(len(e['evidence']) for e in d['entries']),errors=errors,source_checks_only_credit=0,manual_accept_indices=[7531],observation=note,runtime_tested=False),ensure_ascii=False,indent=2)+'\n')
print(note)
