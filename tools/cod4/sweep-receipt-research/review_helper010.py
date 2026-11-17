"""Integrity after Carson's full source reads; no script-inferred credit."""
import json,hashlib,datetime,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/sweep-receipt-research';d=json.loads((O/'helpers/apugli-rpginventory/batch-010.json').read_text());tree=json.loads((R/'tools/cod4/armor-acceptance/.work/research-sources/SlimeKnights__TinkersConstruct/tree.json').read_text());errors=[];count=0;spec=[]
H=lambda b:hashlib.sha256(b).hexdigest()
for i,e in enumerate(d['entries']):
 support=[]
 for n in e['evidence']:
  raw=(R/n['source_local']).read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  ok=H(raw)==n['source_sha256'] and H(n['excerpt'].encode())==n['snippet_sha256'] and '\n'.join(raw.decode().splitlines()[n['line']-1:n['end_line']]).strip()==n['excerpt'].strip() and any(t['path']==n['path'] and t['sha']==blob for t in tree['tree'])
  count+=1
  if not ok:errors.append([n['path'],n.get('method')])
  if n.get('method') and n['method'] not in ('CombatFishingHook','FluidEffectProjectile','Entity','Block') and not (n['path']==e['path'] and n['method']==e['method'] and n['line']==e['line']):support.append([n['source_local'],n['method'],n['line']+1])
 spec.append(dict(candidate_indices=[7529+i],observation=['主审接受挂钩准备态→用户稍后收线的真实伤害消费1；当前装备重取及迟到失效限制见batch178。','主审接受具体炮红石延后发射→飞行载荷→当前源库存写回/剩量消费1；资源结果不等于伤害成功，见batch178。'][i],supporting_methods=support))
vanilla=[]
for n in {(n['path'],n['line'],n['end_line']):n for e in d['entries'] for n in e['local_vanilla_support']}.values():
 raw=(R/n['source_local']).read_bytes();artifact=Path(n['source_artifact'])
 with zipfile.ZipFile(artifact) as z:assert z.read(n['path'])==raw
 assert H(raw)==n['source_sha256'] and H(n['excerpt'].encode())==n['snippet_sha256']
 assert '\n'.join(raw.decode().splitlines()[n['line']-1:n['end_line']]).strip()==n['excerpt'].strip()
 vanilla.append(dict(source_local=n['source_local'],source_sha256=H(raw),artifact=str(artifact),artifact_sha256=H(artifact.read_bytes()),path=n['path'],method=n['method'],line=n['line'],end_line=n['end_line'],excerpt=n['excerpt'],additional_credit=0))
assert not errors
(O/'manual-chain-spec-078.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
(O/'apugli-batch-010-main-review.json').write_text(json.dumps(dict(reviewed_at=datetime.datetime.now().astimezone().isoformat(),helper_batch='helpers/apugli-rpginventory/batch-010.json',evidence_nodes_checked=count,errors=errors,source_checks_only_credit=0,manual_accept_indices=[7529,7530],semantic_dedup='准备/收线消费和有限流体弹载荷各整链1；通用ToolAttackUtil/同步方块效果/每配方/父层方法均0',main_additional_observation='FluidEffectProjectile.onHitBlock在效果后若仍有流体且当前块已为空气直接return，不经过尾部updateCannonStack；影响context物品写回，不宣称复现。Impact取消亦未消除hitType驱动的位置分支。',full_methods_not_credit=True,local_vanilla_support=vanilla,runtime_tested=False,upstream_code_executed=False),ensure_ascii=False,indent=2)+'\n');print(count,'helper evidence nodes verified; no automatic credit;',len(vanilla),'local artifact supports')
