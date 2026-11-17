"""Freeze one bounded source study; preserve historic reference counts and production."""
import datetime, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def freeze(folder,batch,key,prior_folder,observations,pages,details,pending):
    b=ROOT/'docs/art'/folder; prior=ROOT/'docs/art'/prior_folder
    ledger=json.loads((prior/'combined-semantic-ledger.json').read_text())
    assert key not in ledger['reviewed_case_keys'] and key not in ledger['reviewed_pending_whole_keys']
    review=dict(batch=batch,key=key,observations=observations,actually_viewed_pages=pages,details=details,pending=pending,new_validated_credit=0,new_learning_groups=0,whole_candidate_families=1,validated_applicable_total=None,exact_gap=None,runtime_accepted=False,not_counted=['four slots','texture files','cuboids','UV rectangles','color variants','new namespace'])
    save(b/'semantic-review.json',review)
    ledger['pending_whole_families'].append(dict(primary_whole_key=key,review=str((b/'semantic-review.json').relative_to(ROOT)),review_sha256=sha(b/'semantic-review.json'),new_validated_credit=0,new_learning_groups=0,whole_candidate_learning_families=1,pending=pending))
    ledger['reviewed_pending_whole_keys'].append(key)
    assert ledger['validated_independent_design_total'] is None and ledger['exact_remaining_gap_to_1000'] is None
    save(b/'combined-semantic-ledger.json',ledger)
    bp=ROOT/'docs/art/armor-ars-reference-20261111/source-baseline.json';baseline=json.loads(bp.read_text());changes=[p for p,h in baseline.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    save(b/'protected-assets-check.json',dict(baseline=str(bp),sha256=sha(bp),checked=len(baseline),changed=changes))
    assert not changes,changes
    progress=dict(batch=batch,status='BOUNDED_WHOLE_REFERENCE_STUDY_DONE_INDEPENDENT_ACCEPTANCE_PENDING',key=key,study=str(b/'README.md'),prior=str(prior/'progress.json'),new_validated_credit=0,validated_applicable_total=None,exact_gap=None,reference_gate_met=False,production_changes=0,game_starts=0,checklist_deletions=0,pending=pending,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save(b/'progress.json',progress)
    files={str(p.relative_to(b)):sha(p) for p in sorted(b.rglob('*')) if p.is_file() and not p.name.startswith('bounded-receipt-') and p.name!='coordinator-receipt.json'}
    data=(json.dumps(dict(batch=batch,scope='REFERENCE_RESEARCH_ONLY',inputs=files,production_changes=0,game_starts=0,checklist_deletions=0),ensure_ascii=False,indent=2)+'\n').encode();h=hashlib.sha256(data).hexdigest();rp=b/f'bounded-receipt-{h}.json';rp.write_bytes(data)
    save(b/'coordinator-receipt.json',dict(batch=batch,key=key,bounded_receipt=str(rp),bounded_receipt_sha256=h,observations=str(b/'README.md'),observations_sha256=sha(b/'README.md'),semantic_review=str(b/'semantic-review.json'),semantic_review_sha256=sha(b/'semantic-review.json'),new_validated_credit=0,validated_applicable_total=None,exact_gap=None,protected_unchanged=len(baseline),production_changes=0,pending=pending))
    p=ROOT/'docs/art/armor-continuation-20261102/progress.json';old=p.read_bytes();j=json.loads(old)
    assert j['latest_continuation']==str((prior/'progress.json').relative_to(ROOT)),j['latest_continuation']
    j.update(status=batch+'_WHOLE_REFERENCE_STUDY_DONE_GATE_PENDING',latest_continuation=str((b/'progress.json').relative_to(ROOT)),latest_combined_semantic_ledger=str((b/'combined-semantic-ledger.json').relative_to(ROOT)),latest_reference_gate_met=False,latest_minimum_open_gap_under_current_policy=None)
    assert p.read_bytes()==old
    save(p,j)
    assert all(sha(b/n)==h for n,h in files.items())
    print(json.dumps(dict(batch=batch,coordinator_receipt=str(b/'coordinator-receipt.json'),sha256=sha(b/'coordinator-receipt.json'),hashed_files=len(files),protected_unchanged=len(baseline)),ensure_ascii=False))
