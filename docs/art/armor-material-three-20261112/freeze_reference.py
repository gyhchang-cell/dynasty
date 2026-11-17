"""Freeze only local evidence data. No upstream code or historical executor is run."""
from pathlib import Path
import json,hashlib,datetime,sys
ROOT=Path.cwd()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def freeze(folder,batch,key,prior,expected_pointer,details):
 b=ROOT/'docs/art'/folder;lp=ROOT/prior;ledger=json.loads(lp.read_text());assert key not in ledger['reviewed_case_keys']+ledger['reviewed_pending_whole_keys']
 review={'batch':batch,'key':key,'observations':str(b/'README.md'),'sha256':sha(b/'README.md'),'details':details,'source_view_and_read':True,'new_validated_independent_credit':0,'pending_complete_source_family':1,'global_applicable_total':None,'exact_gap':None,'gate_met':False,'runtime_accepted':False,'pending':['Main independent applicability and whole-family semantic dedup','exact runtime source/dependency identity and wearing five views/seams','1000 applicable references gate']};save(b/'semantic-review.json',review)
 ledger['pending_whole_families'].append({'primary_whole_key':key,'review':str(b/'semantic-review.json'),'sha256':sha(b/'semantic-review.json'),'new_validated_credit':0,'pending':review['pending']});ledger['reviewed_pending_whole_keys'].append(key);ledger['current_batch_prior']={'path':str(lp),'sha256':sha(lp)};ledger['current_batch_additional_D54_carry_credit']=0
 assert ledger['validated_independent_design_total'] is None and not ledger['gate_met'];save(b/'combined-semantic-ledger.json',ledger)
 p=ROOT/'docs/art/armor-ars-reference-20261111/source-baseline.json';baseline=json.loads(p.read_text());diff=[s for s,h in baseline.items()if not(ROOT/s).is_file()or sha(ROOT/s)!=h];assert not diff;save(b/'protected-assets-check.json',{'baseline':str(p),'sha256':sha(p),'checked':len(baseline),'changed':diff,'not_Main_pixel_review':True})
 save(b/'progress.json',{'batch':batch,'status':'BOUNDED_SOURCE_STUDY_DONE_MAIN_REVIEW_PENDING','key':key,'new_independent_credit':0,'gate_met':False,'production_changes':0,'game_starts':0,'checklist_deletions':0,'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 files={str(p.relative_to(b)):sha(p)for p in sorted(b.rglob('*'))if p.is_file()and p.name!='coordinator-receipt.json'and not p.name.startswith('bounded-receipt-')};data=(json.dumps({'batch':batch,'inputs':files,'external_code_executed':False,'production_changes':0},ensure_ascii=False,indent=2)+'\n').encode();h=hashlib.sha256(data).hexdigest();rp=b/f'bounded-receipt-{h}.json';rp.write_bytes(data)
 receipt={'batch':batch,'key':key,'bounded_receipt':str(rp),'sha256':h,'observations':str(b/'README.md'),'observations_sha256':sha(b/'README.md'),'semantic_review':str(b/'semantic-review.json'),'semantic_review_sha256':sha(b/'semantic-review.json'),'protected_unchanged':len(baseline),'new_validated_credit':0,'validated_applicable_total':None,'exact_gap':None,'gate_met':False,'production_changes':0};save(b/'coordinator-receipt.json',receipt)
 pointer=ROOT/'docs/art/armor-continuation-20261102/progress.json';raw=pointer.read_bytes();d=json.loads(raw);assert d['latest_continuation']==expected_pointer,d['latest_continuation'];d.update(latest_continuation=str((b/'progress.json').relative_to(ROOT)),latest_combined_semantic_ledger=str((b/'combined-semantic-ledger.json').relative_to(ROOT)),latest_reference_gate_met=False,status=batch+'_REFERENCE_DONE_GATE_PENDING');assert pointer.read_bytes()==raw;save(pointer,d)
 assert all(sha(b/p)==h for p,h in files.items());print(json.dumps({'receipt':str(b/'coordinator-receipt.json'),'sha256':sha(b/'coordinator-receipt.json'),'frozen_files':len(files),'protected_unchanged':len(baseline)}))
if __name__=='__main__':
 spec=json.loads(Path(sys.argv[1]).read_text());freeze(**spec)
