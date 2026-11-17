#!/usr/bin/env python3
"""Read-only cached provenance/range/decision consistency checks; not semantic acceptance."""
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
R = next(p for p in H.parents if (p/'src/main/java/com/dynasty').is_dir())
sha = lambda b: hashlib.sha256(b).hexdigest()

def verify(number, expected_maximum):
    path=H/f'immune-reference-batch-{number:03}.json'
    raw=path.read_bytes(); doc=json.loads(raw)
    assert doc['research_credit']==0 and doc['maximum_proposed_credit']==expected_maximum
    assert not doc['production_changes'] and not doc['runtime_executed']
    repositories={}
    for prov in doc['provenances']:
        mr=(R/prov['manifest_path']).read_bytes()
        assert sha(mr)==prov['manifest_sha256']
        m=next(x for x in json.loads(mr) if x['repo']==prov['repo'])
        assert m['commit']==prov['commit']
        assert m.get('branch')==prov['branch'] and m.get('tag')==prov['tag']
        cr=(R/prov['commit_metadata_path']).read_bytes()
        tr=(R/prov['tree_metadata_path']).read_bytes()
        assert sha(cr)==m['commit_metadata_sha256']
        assert sha(tr)==m['tree_metadata_sha256']
        c=json.loads(cr); t=json.loads(tr)
        assert c['sha']==m['commit']
        assert c['tree']['sha']==t['sha']==m['git_tree']==prov['git_tree']
        assert not t.get('truncated')
        repositories[m['repo']]={'manifest':m,'files':{e['source']:e for e in m['files']},
            'blobs':{e['path']:e['sha'] for e in t['tree'] if e['type']=='blob'}}
    ranges=[]; covered={}; full_files=set()
    for ref in doc['source_refs']:
        rep=repositories[ref['repo']]; entry=rep['files'][ref['path']]
        assert ref['commit']==rep['manifest']['commit']
        source=(R/ref['path']).resolve()
        assert source.is_relative_to(R)
        sr=source.read_bytes()
        assert sha(sr)==ref['file_sha256']==entry['sourceSha256']
        blob=hashlib.sha1(b'blob '+str(len(sr)).encode()+b'\0'+sr).hexdigest()
        assert blob==ref['git_blob_sha1']==entry['source_blob']==rep['blobs'][entry['path']]
        assert ref['upstream_path']==entry['path']
        lines=sr.decode().splitlines(); start,end=ref['lines']
        assert 1<=start<=end<=len(lines)
        current=set(range(start,end+1)); previous=covered.setdefault(ref['path'],set())
        assert not previous.intersection(current), 'Do not double-count overlapping cited ranges'
        previous.update(current)
        if len(previous)==len(lines):full_files.add(ref['path'])
        ranges.append({'path':ref['path'],'lines':ref['lines'],
            'range_text_sha256':sha('\n'.join(lines[start-1:end]).encode())})
    snapshot=doc['dedup_snapshot']; lr=(R/snapshot['path']).read_bytes()
    ledger=json.loads(lr); by={x['id']:x for x in ledger}
    for cmp in snapshot['comparisons']:
        expected={k:v for k,v in by[cmp['accepted_id']].items() if k not in ['source_refs','auxiliary_refs']}
        assert cmp['full_semantic_decision_read']==expected and cmp['distinction']
    assert number == 35 and len(snapshot['comparisons']) == 6
    migration_count=0
    if 'migration_overlap_screen' in doc:
        screen=doc['migration_overlap_screen']
        migration={x['candidate_id']:x for x in [json.loads(l) for l in (R/screen['path']).read_text().splitlines() if l.strip()]}
        for cmp in screen['comparisons']:
            old=migration[cmp['accepted_id']]
            assert all(old[k]==v for k,v in cmp['complete_semantic_decision_read'].items())
            assert old['status']=='accepted' and old['credit']==1
            migration_count+=1
    if 'availability' in doc:
        av=doc['availability']
        assert sha((R/av['path']).read_bytes())==av['sha256']
    base=doc['baseline']
    assert sha((R/base['accepted034_receipt_path']).read_bytes())==base['accepted034_receipt_sha256']
    reuse=doc['prior_read_reuse']
    prior_raw=(R/reuse['path']).read_bytes()
    assert sha(prior_raw)==reuse['sha256']
    prior=json.loads(prior_raw)
    old={(x['path'],tuple(x['lines'])):x for x in prior['source_refs']}
    reused=[x for x in doc['source_refs'] if x['reading_context'].startswith('unchanged034_')]
    assert len(reused)==reuse['reused_ranges']
    for item in reused:
        origin=old[(item['path'],tuple(item['lines']))]
        assert item['file_sha256']==origin['file_sha256'] and item['git_blob_sha1']==origin['git_blob_sha1']
    new=[x for x in doc['source_refs'] if x not in reused]
    assert len(new)==reuse['new_ranges']
    assert sum(x['lines'][1]-x['lines'][0]+1 for x in new)==reuse['new_cited_lines']
    return {'status':'PASS','new_ranges':len(new),'reused_ranges':len(reused),'new_cited_lines':reuse['new_cited_lines'],'proposal_path':str(path.relative_to(R)),'proposal_sha256':sha(raw),
        'source_ranges_verified':len(ranges),'unique_source_files_verified':len(covered),
        'full_files_cited':len(full_files),'unique_cited_source_lines':sum(map(len,covered.values())),
        'ranges':ranges,'complete_semantic_decisions_verified':len(snapshot['comparisons']),
        'migration_semantic_decisions_verified':migration_count,'ledger_rows_observed':len(ledger),
        'ledger_changed_since_snapshot':sha(lr)!=snapshot['sha256'],
        'maximum_pending_credit':expected_maximum,'research_credit_awarded':0,
        'network_requests':0,'game_or_upstream_execution':False,
        'limits':['Only cached commit/tree/blob/range and recorded semantic-decision consistency checked. Not actual upstream availability, semantic acceptance, gameplay or independent review.',
            '035 reuses unchanged034 registration/helper support; no Core binary build750, native spawn acceptance, AI, unload, tracking or payment settlement claim.033 remains0.']}

if __name__=='__main__':
    print(json.dumps(verify(35,1),ensure_ascii=False,indent=2))
