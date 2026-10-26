"""Static evidence integrity only: not a semantic reviewer and not game acceptance."""
from ledger import O,B,R,verify
import json,hashlib,datetime
verify();rows=json.loads((O/'reviewed.json').read_text());pending=json.loads((O/'candidates.json').read_text());checked=0
for row in rows+pending:
 for ref in row['source_refs']+row.get('auxiliary_refs',[]):
  path=(R/ref['path']).resolve();assert path.is_relative_to(B/'sources')
  data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==ref['file_sha256']
  a,b=ref['lines'];assert 1<=a<=b<=len(data.decode().splitlines()),(ref['source_path'],a,b)
  checked+=1
assert all(x['research_credit']==0 for x in pending)
request=R/'docs/cod4/request.txt';lines=request.read_text().splitlines()
req=[{'line':i,'text':s} for i,s in enumerate(lines,1) if s.startswith('| Boss Immune |') or s.startswith('| 阴气 |') or s.startswith('| 阳气 |') or s.startswith('- 反馈由服务端决定')]
report={'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'effective':len(rows),'required':1000,'shortfall':1000-len(rows),'zero_credit_curated':len(pending),'source_references_hash_and_range_checked':checked,'semantic_dedup_automatically_proven':False,'formal_design_gate_satisfied':len(rows)>=1000,'request_source':str(request.relative_to(R)),'request_sha256':hashlib.sha256(request.read_bytes()).hexdigest(),'request_lines':req,'scope':{'allowed_writes':['docs/cod4/audit-20261022/immune-feedback-research','tools/cod4/immune-feedback-research'],'production_code_modified_by_this_research':False,'assets_modified_by_this_research':False,'todo_modified_by_this_research':False,'game_started_by_this_research':False},'verification_limits':'Hash/range validation only. No compilation, native event reproduction, TCP, images, sound, or pixel acceptance. No 1000 implementation completion claim.'}
(O/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
