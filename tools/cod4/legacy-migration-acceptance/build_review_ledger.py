"""Validate explicitly authored review notes against pinned AST contexts. No auto-accept."""
from pathlib import Path
import json,hashlib,collections
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
index={x['candidate_id']:x for x in map(json.loads,(O/'candidates.jsonl').read_text().splitlines())}
notes=[x for p in sorted((O/'reviews').glob('*.json')) for x in json.loads(p.read_text())]
rows=[];seen=set();families=set();structs={}
for n in notes:
    assert n['candidate_id'] not in seen;seen.add(n['candidate_id'])
    c=index[n['candidate_id']]
    assert hashlib.sha256((R/c['private_file']).read_bytes()).hexdigest()==c['file_sha256'],c['private_file']
    assert n['status'] in ('accepted','rejected','duplicate','pending')
    if n['status']=='accepted':
        for k in ('family','trigger','input','output','preservation','application_limit'):assert n.get(k),n
        assert n['family'] not in families,('semantic family repeated',n['family'])
        previous=structs.get(c['structural_fingerprint'])
        if previous:
            resolution=n.get('structural_collision_review',{})
            assert resolution.get('compared_candidate')==previous,('AST family repeated',c['candidate_id'])
            assert resolution.get('distinct_gameplay_owner_reason') and resolution.get('reviewed_consumers'),resolution
        families.add(n['family']);structs.setdefault(c['structural_fingerprint'],c['candidate_id'])
    evidence=[]
    for i in [n['candidate_id']]+n.get('supporting_candidates',[]):
        q=index[i];assert hashlib.sha256((R/q['private_file']).read_bytes()).hexdigest()==q['file_sha256']
        assert hashlib.sha256(q['context'].encode()).hexdigest()==q['method_sha256'],('method context hash changed',i)
        evidence.append({k:q[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')})
    rows.append({**n,'credit':int(n['status']=='accepted'),'evidence':evidence})
(O/'reviewed.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
counts=collections.Counter(x['status'] for x in rows)
summary={'target':1000,'accepted_unique_implementations':len(families),'gap':max(0,1000-len(families)),'review_decisions':dict(counts),'candidate_methods':len(index),'unreviewed_candidates':len(index)-len(seen),'production_change_gate_met':len(families)>=1000,'candidate_count_is_not_review_count':True,'counting':'explicit semantic family + AST collision check; identical reader requires explicit reviewed distinct gameplay-owner/consumer justification; same-chain supports and key-only clones give no extra credit','ledger_sha256':hashlib.sha256((O/'reviewed.jsonl').read_bytes()).hexdigest()}
(O/'research-progress.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
