"""Integrity of already manually read helper009; no inferred acceptance."""
import json,hashlib,datetime,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/sweep-receipt-research';d=json.loads((O/'helpers/apugli-rpginventory/batch-009.json').read_text());idx=json.loads((O/'helpers/apugli-rpginventory/source-index-009.json').read_text());tree=json.loads((R/'tools/cod4/armor-acceptance/.work/research-sources/SlimeKnights__TinkersConstruct/tree.json').read_text());errors=[];count=0;spec=[]
H=lambda b:hashlib.sha256(b).hexdigest()
for i,e in enumerate(d['entries']):
 support=[]
 for n in e['evidence']:
  raw=(R/n['source_local']).read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  ok=H(raw)==n['source_sha256'] and H(n['excerpt'].encode())==n['snippet_sha256'] and '\n'.join(raw.decode().splitlines()[n['line']-1:n['end_line']]).strip()==n['excerpt'].strip() and any(t['path']==n['path'] and t['sha']==blob for t in tree['tree'])
  count+=1
  if not ok: errors.append([n['path'],n.get('method')])
  # constructors and configuration declarations were read, but are not method snapshots.
  if n.get('method') and n['method'] != Path(n['path']).stem and not (n['path']==e['path'] and n['method']==e['method'] and n['line']==e['line']):support.append([n['source_local'],n['method'],n['line']+1])
 support.append([e['source_local'],'getDefaultHooks'])
 spec.append(dict(candidate_indices=[7527+i],observation=['Carson主审接受前次受伤形成未来momentum窗口1，SlotInCharge支持0，具体边界见batch174。','Carson主审接受当刻伤害转换非累加再生时钟载荷1，真实治疗不等于预算，具体边界见batch174。'][i],supporting_methods=support))
# Local vanilla is support only; bind source bytes to actual versioned artifact, never Git-pretend.
vanilla=[]
for n in { (n['path'],n['line'],n['end_line']):n for e in d['entries'] for n in e['local_vanilla_support']}.values():
 raw=(R/n['source_local']).read_bytes();artifact=Path(n['source_artifact'])
 with zipfile.ZipFile(artifact) as z:assert z.read(n['path'])==raw
 assert H(raw)==n['source_sha256'] and H(n['excerpt'].encode())==n['snippet_sha256']
 end=n['end_line'];note=None
 if n['method']=='playerTouch' and n['path'].endswith('ThrownTrident.java'):
  end=170;note='helper ends at169 blank before closing brace; main reviewer read actual complete165..170. Preserved helper unchanged.'
 vanilla.append(dict(source_local=n['source_local'],source_sha256=H(raw),artifact=str(artifact),artifact_sha256=H(artifact.read_bytes()),path=n['path'],method=n['method'],line=n['line'],end_line=end,excerpt='\n'.join(raw.decode().splitlines()[n['line']-1:end]),correction=note,additional_credit=0))
assert not errors
(O/'manual-chain-spec-072.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
(O/'apugli-batch-009-main-review.json').write_text(json.dumps(dict(reviewed_at=datetime.datetime.now().astimezone().isoformat(),helper_batch='helpers/apugli-rpginventory/batch-009.json',evidence_nodes_checked=count,errors=errors,source_checks_only_credit=0,manual_accept_indices=[7527,7528],manual_auxiliary_indices=[],full_methods_not_credit=True,config_declarations_not_full_provider=True,local_vanilla_support=vanilla,runtime_tested=False,upstream_code_executed=False),ensure_ascii=False,indent=2)+'\n');print(count,'helper evidence nodes checked, no automatic credit; corrected parent snapshot recorded separately')
