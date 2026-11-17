"""Integrity of already manually read helper008; no inferred acceptance."""
import json,hashlib,datetime,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/sweep-receipt-research';d=json.loads((O/'helpers/apugli-rpginventory/batch-008.json').read_text());idx=json.loads((O/'helpers/apugli-rpginventory/source-index-008.json').read_text());tree=json.loads((R/'tools/cod4/armor-acceptance/.work/research-sources/SlimeKnights__TinkersConstruct/tree.json').read_text());errors=[];count=0;spec=[]
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
 if i==2:support.append([e['source_root']+'/src/main/java/slimeknights/tconstruct/library/utils/TeleportHelper.java','randomNearbyTeleport',27])
 spec.append(dict(candidate_indices=[7524+i],observation=['Carson全文人工主审接受原槽归还1，具体限制见batch173。','Carson全文人工主审接受首次返程锚点跨刷新1，具体限制见batch173。','Carson全文人工主审同步闪避辅助0，相关性不满足本次延后回执门槛。'][i],supporting_methods=support))
# Local vanilla is support only; bind source bytes to actual versioned artifact, never Git-pretend.
vanilla=[]
for n in d['entries'][0]['local_vanilla_support']:
 raw=(R/n['source_local']).read_bytes();artifact=Path(n['source_artifact'])
 with zipfile.ZipFile(artifact) as z:assert z.read(n['path'])==raw
 assert H(raw)==n['source_sha256'] and H(n['excerpt'].encode())==n['snippet_sha256']
 end=n['end_line'];note=None
 if n['method']=='playerTouch' and n['path'].endswith('ThrownTrident.java'):
  end=170;note='helper ends at169 blank before closing brace; main reviewer read actual complete165..170. Preserved helper unchanged.'
 vanilla.append(dict(source_local=n['source_local'],source_sha256=H(raw),artifact=str(artifact),artifact_sha256=H(artifact.read_bytes()),path=n['path'],method=n['method'],line=n['line'],end_line=end,excerpt='\n'.join(raw.decode().splitlines()[n['line']-1:end]),correction=note,additional_credit=0))
assert not errors
(O/'manual-chain-spec-070.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
(O/'apugli-batch-008-main-review.json').write_text(json.dumps(dict(reviewed_at=datetime.datetime.now().astimezone().isoformat(),helper_batch='helpers/apugli-rpginventory/batch-008.json',evidence_nodes_checked=count,errors=errors,source_checks_only_credit=0,manual_accept_indices=[7524,7525],manual_auxiliary_indices=[7526],full_methods_not_credit=True,config_declarations_not_full_provider=True,local_vanilla_support=vanilla,runtime_tested=False,upstream_code_executed=False),ensure_ascii=False,indent=2)+'\n');print(count,'helper evidence nodes checked, no automatic credit; corrected parent snapshot recorded separately')
