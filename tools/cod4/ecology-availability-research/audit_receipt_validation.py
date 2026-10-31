"""Own aggregator in-memory counterexample inspection. No source/receipt mutations on disk.
Not upstream tests, compilation, gameplay validation, or research credit.
"""
import copy
import json
from pathlib import Path
from evidence import ROOT,DOCS,dump,sha
from receipt_validation import aggregate,validate_receipt,Snapshot,InvalidReceipt,resolve,require

by_id={r['id']:(p,r) for p in sorted(DOCS.glob('batch-*.json')) for r in json.loads(p.read_text())['records']}
real,report,snap=aggregate(by_id); snap.stable()
require({f'EA-{i:04d}' for i in range(1,14)} <= {r['id'] for r in real},'previous13 receipt baseline no longer accepted; inspect changed evidence/conflicts')
path=DOCS/'independent-reviews/carson-EA0010.json'
base=json.loads(path.read_text())
cases=[]
def run(name, mutate=None, overrides=None, alternate_path=None, alternate_map=None, expected='invalid'):
    d=copy.deepcopy(base)
    if mutate: mutate(d)
    raw=(json.dumps(d,ensure_ascii=False)+'\n').encode()
    try:
        result=validate_receipt(alternate_path or path,raw,alternate_map or by_id,Snapshot(overrides))
        state=result['state']; reason=result.get('reason')
    except (InvalidReceipt,ValueError,KeyError,TypeError,OSError,UnicodeError) as exc:
        state='invalid';reason=str(exc)
    require(state==expected,'counterexample failed: '+name+' -> '+state)
    cases.append({'case':name,'expected':expected,'observed':state,'pass':True,'reason':reason,'synthetic_zero_credit':True})
def put(k,v):return lambda d:d.__setitem__(k,v)
def checkput(k,v):return lambda d:d['source_checks'][0].__setitem__(k,v)
run('unknown reviewer',put('reviewer','unknown reviewer'))
run('reviewer substring is not authorization',put('reviewer','Carson independent full-chain text and semantic review plus attacker'))
run('role namespace mismatch',put('reviewer','coordinator independent complete-chain read'))
run('unauthorized filename',alternate_path=path.with_name('unlisted-EA0010.json'))
run('receipt id vs filename mismatch',put('id','EA-0011'))
run('unknown id',put('id','EA-0999'),alternate_path=path.with_name('carson-EA0999.json'))
run('candidate is not eligible',put('id','EA-C001'),alternate_path=path.with_name('carson-EAC001.json'))
run('semantic mismatch',put('semantic_key','different mechanism'))
run('batch SHA mismatch',put('reviewed_batch_sha256','0'*64))
run('reviewed_batch path mismatch',put('reviewed_batch',str((DOCS/'batch-001.json').relative_to(ROOT))))
run('reviewed_batch traversal',put('reviewed_batch','../batch-005.json'))
run('Carson reviewed_batch required',lambda d:d.pop('reviewed_batch'))
run('credit boolean is not1',put('accepted_credit',True))
run('credit2 forbidden',put('accepted_credit',2))
run('gap decision zero credit',put('decision','GAP'),expected='non_accepting')
run('reject decision zero credit',put('decision','REJECT'),expected='non_accepting')
run('candidate decision zero credit',put('decision','candidate'),expected='non_accepting')
run('other role positive decision not accepted',put('decision','ACCEPT_ONE_RELATED_IMPLEMENTATION'))
run('missing semantic observation',lambda d:d.pop('observed_complete_chain'))
run('incomplete range coverage',lambda d:d['source_checks'].pop())
run('duplicate range cannot replace another',lambda d:d['source_checks'].__setitem__(-1,copy.deepcopy(d['source_checks'][0])))
for field,value in [('path','wrong/path.java'),('source_local','wrong/source.java'),('line',1),('end_line',1),
                    ('source_sha256','0'*64),('git_blob_sha1','0'*40),('revision','0'*40),
                    ('excerpt_sha256','0'*64),('url','https://example.invalid/not-fixed')]:
    run('receipt evidence '+field+' mismatch',checkput(field,value))
run('reviewer false PASS flag',checkput('excerpt_exact',False))
run('metadata hash mismatch',put('source_metadata_sha256','0'*64))
run('tree metadata hash mismatch',put('tree_metadata_sha256','0'*64))
bp,r=by_id['EA-0010'];e=r['chain'][0]
run('actual source bytes corrupted',overrides={(ROOT/e['source_local']).resolve():b'not the cached source\n'})
tree_path=(ROOT/e['tree_metadata']).resolve();tree=json.loads(tree_path.read_text())
next(x for x in tree['tree'] if x['path']==e['path'])['sha']='0'*40
run('actual fixed tree entry corrupted',overrides={tree_path:json.dumps(tree).encode()})
meta_path=(ROOT/e['source_metadata']).resolve();meta=json.loads(meta_path.read_text())
meta['sha' if 'sha' in meta else 'commit']='0'*40
run('actual cached commit corrupted',overrides={meta_path:json.dumps(meta).encode()})
run('actual batch bytes changed',overrides={bp.resolve():bp.read_bytes()+b' '})
# Forged matching batch+receipt hash cannot hide an excerpt not equal to actual source.
fakebatch=json.loads(bp.read_text());fr=next(x for x in fakebatch['records'] if x['id']=='EA-0010')
fr['chain'][0]['excerpt']+=' forged';fr['chain'][0]['excerpt_sha256']=sha(fr['chain'][0]['excerpt'].encode())
fr['excerpt']=fr['chain'][0]['excerpt'];fr['excerpt_sha256']=fr['chain'][0]['excerpt_sha256']
fakeraw=json.dumps(fakebatch).encode();fake_map=dict(by_id);fake_map['EA-0010']=(bp,fr)
def forge(d):
    d['reviewed_batch_sha256']=sha(fakeraw)
    d['source_checks'][0]['excerpt_sha256']=fr['excerpt_sha256']
run('self-consistent forged excerpt still rejected',forge,{bp.resolve():fakeraw},alternate_map=fake_map)
# Simulate a second authorized reviewer for the SAME id, without writing a receipt.
coord=json.loads((DOCS/'independent-reviews/coordinator-EA0001.json').read_text())
second=copy.deepcopy(coord);second['reviewer']='Carson independent complete source-chain review'
second['decision']='ACCEPT_ONE_RELATED_IMPLEMENTATION_WITH_EXPLICIT_LIMITS'
second['reviewed_batch']=str(by_id['EA-0001'][0].relative_to(ROOT))
second['source_checks']=[]
for e in by_id['EA-0001'][1]['chain']:
    second['source_checks'].append({**{k:e[k] for k in ('path','source_local','source_sha256','git_blob_sha1','revision','line','end_line','excerpt_sha256','url')},
        'source_byte_SHA_match':True,'blob_header_SHA1_matches_tree_entry':True,'cached_revision_metadata_match':True,'excerpt_exact':True})
p1=DOCS/'independent-reviews/coordinator-EA0001.json';p2=DOCS/'independent-reviews/carson-EA0001.json'
inputs=[(p1,p1.read_bytes()),(p2,json.dumps(second).encode())]
a,q,_=aggregate(by_id,inputs)
require(len(a)==1 and len(a[0]['reviews'])==2 and not q['conflicts'],'cross-reviewer identical acceptance must count1')
cases.append({'case':'two reviewers same id count once','pass':True,'unique_accepted_ids':1,'review_receipts':2,'synthetic_zero_credit':True})
for decision in ('REJECT','GAP','candidate'):
    changed=copy.deepcopy(second);changed['decision']=decision
    a,q,_=aggregate(by_id,[(p1,p1.read_bytes()),(p2,json.dumps(changed).encode())])
    require(not a and len(q['conflicts'])==1,'conflicting '+decision+' must hold zero')
    cases.append({'case':'accept vs '+decision+' hold','pass':True,'unique_accepted_ids':0,'synthetic_zero_credit':True})
changed=copy.deepcopy(second);changed['source_checks'][0]['source_sha256']='0'*64
a,q,_=aggregate(by_id,[(p1,p1.read_bytes()),(p2,json.dumps(changed).encode())])
require(not a and len(q['conflicts'])==1,'invalid competing acceptance must hold zero')
cases.append({'case':'accept vs invalid evidence hold','pass':True,'unique_accepted_ids':0,'synthetic_zero_credit':True})
# Freeze and compare all real inputs; synthetic cases have never entered independent-reviews.
snap.stable()
dump('aggregation-counterexample-audit.json',{'status':'OWN_TEXT_AGGREGATOR_IN_MEMORY_INSPECTION_COMPLETE',
 'real_receipt_counts':report['counts'],'actual_accepted_ids':[x['id'] for x in real],
 'actual_receipt_hashes':[{k:x[k] for k in ('receipt','receipt_sha256')} for x in report['receipt_inputs']],
 'counterexamples':cases,'all_pass':all(x['pass'] for x in cases),'case_count':len(cases),
 'source_or_receipt_files_modified':False,'synthetic_receipts_written':False,
 'no_upstream_code_execution_compilation_game_or_runtime_tests':True,
 'scope':'Identity/schema, exact batch/source/revision/tree/blob/excerpt binding, same-id dedup and conflicts; no automatic semantic re-review or cryptographic author identity proof.'})
print('Actual:',len(real),'accepted unique IDs;',len(cases),'in-memory counterexample checks passed; real evidence unchanged')
