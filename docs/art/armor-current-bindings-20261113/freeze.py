"""Freeze this specialist evidence and compare-and-swap only its continuation pointer."""
from pathlib import Path
import json, hashlib, os
D=Path(__file__).resolve().parent; R=D.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def encoded(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
def digest(p):return sha(p.read_bytes())
assert not (D/'coordinator-delivery.json').exists()
pointer=R/'docs/art/armor-continuation-20261102/progress.json'
old=pointer.read_bytes(); state=json.loads(old)
assert state['latest_continuation']=='docs/art/armor-valonite-whole-20261112/progress.json'
for record in ['source-inputs.json','historical-inputs.json']:
 for p,h in json.loads((D/record).read_text()).items():assert digest(R/p)==h,p
for p,h in json.loads((D/'protected-before-after.json').read_text())['before'].items():assert digest(R/p)==h,p
manifest={str(p.relative_to(D)):digest(p) for p in sorted(D.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
receipt=encoded({'batch':'D73','files':manifest,'production_changes':0,'runtime_acceptance':False,'new_reference_credit':0,'gate_met':False})
h=sha(receipt);rp=D/f'bounded-receipt-{h}.json';rp.write_bytes(receipt)
delivery={'batch':'D73','receipt':{'path':str(rp),'sha256':h},'verification':{'path':str(D/'verification.json'),'sha256':digest(D/'verification.json')},
 'target_status':{'path':str(D/'unclosed-targets.json'),'sha256':digest(D/'unclosed-targets.json')},
 'new_credit':0,'gate_met':False,'production_changes':0,'headline':'28 current bindings, 16 exact selected originals, 14 early worn atlases; head UV naming corrected',
 'pending':['Independent review of neutral-pose head face interpretation','28 worn texture/seam/live acceptance; 16 icon-to-worn coherence','Applicable 1000 whole designs gate remains unclosed; no early artwork production']}
dp=D/'coordinator-delivery.json';dp.write_bytes(encoded(delivery))
state.update(status='D73_CURRENT_PROJECT_BINDINGS_AUDITED_RUNTIME_PENDING',latest_continuation=str((D/'progress.json').relative_to(R)),
 latest_current_binding_delivery={'path':str(dp),'sha256':digest(dp)},
 latest_exact_priority_target_status=delivery['target_status'],
 latest_combined_semantic_ledger=str((D/'combined-semantic-ledger.json').relative_to(R)),
 latest_reference_gate_met=False)
assert pointer.read_bytes()==old,'Concurrent specialist pointer update; keep evidence, do not replace'
tmp=pointer.with_name('progress.D73.tmp');tmp.write_bytes(encoded(state));os.replace(tmp,pointer)
check=json.loads(rp.read_text())
assert all(digest(D/p)==v for p,v in check['files'].items())
print(json.dumps({'frozen_files':len(manifest),'receipt_sha256':h,'delivery_sha256':digest(dp),'specialist_pointer_updated':True}))
