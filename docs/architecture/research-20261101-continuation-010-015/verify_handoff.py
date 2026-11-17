#!/usr/bin/env python3
"""Read-only check of completed research receipts, then record this handoff."""
import ast
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
EXPECTED=[(10,5,20,4,4,1),(11,4,16,3,4,0),(12,4,16,6,3,1),
 (13,3,12,2,1,2),(14,4,16,4,0,4),(15,3,12,4,1,2)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def check_receipt(folder):
 receipt=read(folder/'RECEIPT.json')
 for e in receipt['files']:
  p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],str(p)
 return dict(folder=str(folder),receipt_sha256=sha(folder/'RECEIPT.json'),files_verified=len(receipt['files']))
def main():
 batches=[];receipts=[]
 for batch,templates,images,relooks,proposals,holds in EXPECTED:
  folder=BASE/f'research-20261101-dungeons-{batch:03d}';v=read(folder/'verification.json');r=read(folder/'manual-review.json')
  receipts.append(check_receipt(folder))
  assert v['status'].startswith('PASS') and v['templates_studied']==templates and v['new_images_actually_viewed_and_verified']==images
  assert v['historical_images_reviewed_again']==relooks and v['proposals']==proposals and not v['formal_credit_added']
  assert len(r['entries'])==templates and sum(x['credit_proposal'] for x in r['entries'])==proposals and templates-proposals==holds
  assert all(len(x['images_actually_viewed'])==4 and len(x['observations'])==7 and not x['formal_credit_added'] for x in r['entries'])
  assert not any(v.get(k,0) for k in ['java_run','game_run','network_requests','production_changes','checklist_deletions'])
  batches.append(dict(batch=batch,templates=templates,new_images=images,historical_relooks=relooks,proposals=proposals,holds=holds,formal_credit=0))
 urban=BASE/'research-20261101-scoped-urban-lodging-ledger';receipts.append(check_receipt(urban));u=read(urban/'urban-lodging-scope-register.json')
 assert u['accepted_references']==2 and u['remaining']==998 and not u['construction_allowed']
 assert sha(urban/'urban-lodging-scope-register.json')=='38a1bcaf7c032e024a18dcf5f66c00467b34771e1974299e4dad4da98b64a330'
 assert sha(BASE/'continuation-20261022/references/full-buildings.json')=='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
 assert sha(BASE/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json')=='2426e889e05abf75b9afe50ae0ab50a1a40420e53ae94332c425a43e3606f267'
 totals={k:sum(b[k] for b in batches) for k in ['templates','new_images','historical_relooks','proposals','holds','formal_credit']}
 assert totals==dict(templates=23,new_images=92,historical_relooks=23,proposals=13,holds=10,formal_credit=0)
 report=dict(status='PASS_010_TO_015_RESEARCH_RECEIPTS_AND_TWO_OLD_004_LAYOUT_ACCEPTANCES',batches=batches,totals=totals,
  receipts=receipts,old004_accepted_in_isolated_urban_scope=2,urban_remaining=998,new_asset_tasks_completed=0,
  java_run=False,game_run=False,network_requests=0,checklist_deletions=0,
  limits='Study/view counts and pending proposals are not accepted reference counts. Scope counts cannot be pooled; no relevant scope at1000.')
 (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 ast.parse(Path(__file__).read_text(),filename=str(__file__))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 (OUT/'RECEIPT.json').write_text(json.dumps(dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]),ensure_ascii=False,indent=2)+'\n')
 check_receipt(OUT)
 print(json.dumps(dict(status=report['status'],totals=totals,receipts_checked=len(receipts),urban_accepted=2,urban_remaining=998),ensure_ascii=False))
if __name__=='__main__':main()
