from pathlib import Path
import json,hashlib,datetime
B=Path(__file__).resolve().parent;root=Path.cwd()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert not list(B.glob('bounded-receipt-*.json')),'Already frozen'
for label,count in [('protected',289),('priority',70)]:
 before=json.loads((B/f'{label}-before.json').read_text());assert len(before)==count
 after={p:sha(root/p) for p in before};assert before==after,f'{label} changed'
 dump(B/f'{label}-after.json',after)
prov=json.loads((B/'provenance.json').read_text());tree=json.loads((B/'root-tree-api.json').read_text());lookup={a['path']:a for a in tree['tree']};commit=json.loads((B/'commit-api.json').read_text())
assert commit['sha']==prov['commit'] and commit['tree']['sha']==tree['sha']==prov['root_tree']
for f in prov['files']:
 b=(B/'source'/f['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==f['sha256'];assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==f['blob_sha1']==lookup[f['path']]['sha']
prior=root/'docs/art/armor-arctic-whole-20261114/combined-semantic-ledger.json';old=json.loads(prior.read_text());new=json.loads((B/'combined-semantic-ledger.json').read_text());delta=[k for k in new if old[k]!=new[k]]
assert set(delta)=={'current_batch_prior','reviewed_pending_whole_keys','pending_whole_families'}
assert new['reviewed_pending_whole_keys'][:-1]==old['reviewed_pending_whole_keys'];assert new['pending_whole_families'][:-1]==old['pending_whole_families']
assert not new['gate_met'];assert new['validated_independent_design_total'] is None
verification={'status':'PASS_BOUNDED_SOURCE_RESEARCH_ONLY','pinned_files':len(prov['files']),'protection_289':'unchanged','priority_70':'unchanged','ledger_delta_keys':delta,'new_candidate_whole_designs':1,'new_validated_credit':0,'production_files_changed':0,'game_or_build_launched':False,'task_deleted':False,'not_verified':['Independent semantic/applicability acceptance','Exact MC1.20.6 final UV/inherited mesh/runtime','Actual game visuals and native acquisition']}
dump(B/'verification.json',verification);dump(B/'progress.json',{'batch':'D87','status':'NEW_BEE_ARMOR_DESIGN_STUDIED_PENDING_ACCEPTANCE','updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requirements_saved':True,'gate_met':False,'new_validated_credit':0,'production_files_changed':0})
files={str(p.relative_to(B)):sha(p) for p in sorted(B.rglob('*')) if p.is_file()}
receipt={'batch':'D87','scope':'One new complete four-slot bee armor source study; independent acceptance pending','files':files,'verification':verification};raw=(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode();rsha=hashlib.sha256(raw).hexdigest();rp=B/f'bounded-receipt-{rsha}.json';rp.write_bytes(raw)
delivery={'batch':'D87','status':'LOCAL_RESEARCH_SAVED_NO_PRODUCTION','receipt':str(rp),'receipt_sha256':rsha,'semantic_review':str(B/'semantic-review.json'),'combined_ledger':str(B/'combined-semantic-ledger.json'),'new_candidate_whole_designs':1,'new_validated_credit':0,'global_total':None,'gap':None,'gate_met':False,'protected':289,'priority':70,'native_images_viewed':8,'production_files_changed':0,'note':'New unstudied namespace/design candidate; not another historical family consumer followup. No permission to redraw approved targets.'}
dump(B/'coordinator-delivery.json',delivery)
p=root/'docs/art/armor-continuation-20261102/progress.json';raw=p.read_bytes();state=json.loads(raw);assert state['status']=='D86_ARCTIC_DYE_CONSUMER_AND_FACE_UV_SAVED',state['status'];state['status']='D87_NEW_BEE_ARMOR_SOURCE_DESIGN_SAVED';state['latest_bumblebee_delivery']={'path':str(B/'coordinator-delivery.json'),'sha256':sha(B/'coordinator-delivery.json')};assert p.read_bytes()==raw;dump(p,state)
print(json.dumps({'files':len(files),'receipt':str(rp),'delivery_sha256':sha(B/'coordinator-delivery.json')},ensure_ascii=False))
