#!/usr/bin/env python3
"""Read-only source provenance and evidence consistency, not semantic approval."""
import hashlib
import json
from pathlib import Path

H=Path(__file__).resolve().parent
R=Path('/Users/a15356015027/Desktop/dynasty')
sha=lambda b:hashlib.sha256(b).hexdigest()

def verify():
    p=H/'immune-reference-batch-039.json';raw=p.read_bytes();d=json.loads(raw)
    assert d['research_credit']==0 and d['maximum_proposed_credit']==1
    assert not d['production_changes'] and not d['runtime_executed']
    assert len(d['provenances'])==1
    v=d['provenances'][0];mr=(R/v['manifest_path']).read_bytes()
    assert sha(mr)==v['manifest_sha256']
    m=next(x for x in json.loads(mr) if x['repo']==v['repo'])
    assert m['commit']==v['commit'] and m['branch']==v['branch'] and m.get('tag')==v['tag']
    cr=(R/v['commit_metadata_path']).read_bytes();tr=(R/v['tree_metadata_path']).read_bytes()
    assert sha(cr)==m['commit_metadata_sha256'] and sha(tr)==m['tree_metadata_sha256']
    c=json.loads(cr);t=json.loads(tr)
    assert c['sha']==m['commit']
    assert c['tree']['sha']==t['sha']==v['git_tree']==m['git_tree'] and not t.get('truncated')
    blobs={x['path']:x['sha'] for x in t['tree'] if x['type']=='blob'}
    entries={x['path']:x for x in m['files']}
    seen=set(); total=0
    for x in d['source_refs']:
        e=entries[x['upstream_path']]
        assert x['path']==e['source'] and x['repo']==m['repo'] and x['commit']==m['commit']
        src=(R/x['path']).resolve();assert src.is_relative_to(R)
        sr=src.read_bytes();assert sha(sr)==x['file_sha256']==e['sourceSha256']
        blob=hashlib.sha1(b'blob '+str(len(sr)).encode()+b'\0'+sr).hexdigest()
        assert blob==x['git_blob_sha1']==e['source_blob']==blobs[x['upstream_path']]
        lines=sr.decode().splitlines();assert x['lines']==[1,len(lines)]
        assert sha('\n'.join(lines).encode())==x['range_text_sha256']
        assert x['path'] not in seen;seen.add(x['path']);total+=len(lines)
    assert len(seen)==d['full_files_actually_read']==15 and total==d['cited_lines']
    s=d['dedup_snapshot'];lr=(R/s['path']).read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
    assert len(s['comparisons'])==9
    for x in s['comparisons']:
        expected={k:v for k,v in by[x['accepted_id']].items() if k not in ['source_refs','auxiliary_refs']}
        assert x['full_semantic_decision_read']==expected and x['distinction']
    q=d['migration_overlap_screen'];mlraw=(R/q['path']).read_bytes()
    mi={x['candidate_id']:x for x in [json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]}
    assert len(q['comparisons'])==1
    for x in q['comparisons']:
        old=mi[x['accepted_id']]
        assert all(old[k]==v for k,v in x['complete_semantic_decision_read'].items())
        assert old['status']=='accepted' and old['credit']==1 and x['distinction']
    for k in ['accepted037_receipt','prior038']:
        ref=d['baseline'][k];assert sha((R/ref['path']).read_bytes())==ref['sha256']
    assert json.loads((R/d['baseline']['prior038']['path']).read_text())['research_credit']==0
    return {'status':'PASS','proposal_path':str(p.relative_to(R)),'proposal_sha256':sha(raw),
        'source_ranges_verified':len(seen),'full_files_verified':len(seen),'unique_cited_lines':total,
        'whole_semantic_comparisons_verified':9,'whole_migration_owner_comparisons_verified':1,
        'formal_count_observed':len(rows),'ledger_changed_since_snapshot':sha(lr)!=s['sha256'],
        'migration_ledger_changed_since_snapshot':sha(mlraw)!=q['sha256'],
        'research_credit_awarded':0,'maximum_pending_credit':1,'network_requests':0,
        'upstream_or_game_executed':False,'production_or_master_edits':False,
        'limitations':['Static source/range/decision consistency only; this is not independent semantic acceptance.',
            'Fixed Champions1.18.x source; no native runtime, network ordering, pixel or sound verification.',
            'Shielding full-policy proposal max1; persistence/helpers/packets/parameters have0 separate credit.']}

if __name__=='__main__':
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
