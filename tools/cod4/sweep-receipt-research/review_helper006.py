"""Save manually concluded chain reviews; byte checks confer zero credit."""
import json,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/sweep-receipt-research';d=json.loads((O/'helpers/apugli-rpginventory/batch-006.json').read_text());errors=[];checks=0
for e in d['entries']:
 for n in e['evidence']:
  raw=(R/n['source_local']).read_bytes();root=R/n['source_root'];tree=json.loads((R/'tools/cod4/armor-acceptance/.work/research-sources/SlimeKnights__TinkersConstruct/tree.json').read_text());blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  ok=hashlib.sha256(raw).hexdigest()==n['source_sha256'] and hashlib.sha256(n['excerpt'].encode()).hexdigest()==n['snippet_sha256'] and '\n'.join(raw.decode().splitlines()[n['line']-1:n['end_line']]).strip()==n['excerpt'].strip() and any(t['path']==n['path'] and t['sha']==blob for t in tree['tree'])
  checks+=1
  if not ok:errors.append([n['path'],n['method']])
assert not errors
spec=[]
for i,j in [(7520,0),(7521,1),(7522,2),(7523,4),(4283,3)]:
 e=d['entries'][j];support=[]
 for n in e['evidence'][1:]:
  if n['method'] not in ['TinkerTools','BounceInfo']:support.append([n['source_local'],n['method'],n['line']+2])
 spec.append({'candidate_indices':[i],'observation':'Carson主审全文阅读helper006具体生产/消费方法；支持方法只补调用链，不自动信用。反射窗口条待生产链补足暂0，其余见batch171人工裁定。','supporting_methods':support})
(O/'manual-chain-spec-066.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
(O/'apugli-batch-006-main-review.json').write_text(json.dumps({'reviewed_at':datetime.datetime.now().astimezone().isoformat(),'helper_batch':'helpers/apugli-rpginventory/batch-006.json','evidence_nodes_checked':checks,'errors':errors,'source_checks_only_credit':0,'manual_accept_indices':[7520,7521,7522,7523],'manual_pending_index':4283,'pending_reason':'碰撞端完整166行已读，反射active_modifier启动和反射时长生产缺完整具体盾使用链；留待补证，不凭碰撞handler直接入账。','semantic_dedup':'Bleeding相位与迟读target.lastHurtMob；Sling先移除slot记录再当前装备放出；looting hurt内动态UUID槽；SlimeBounce实体age+1交接。各一整链，共用performAttack/两侧/头腿/反射的退款穿透分支均0额外。','upstream_code_executed':False,'runtime_tested':False},ensure_ascii=False,indent=2)+'\n');print(checks,'evidence nodes checked; no automatic credit')
