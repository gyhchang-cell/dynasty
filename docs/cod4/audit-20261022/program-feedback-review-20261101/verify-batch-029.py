#!/usr/bin/env python3
"""Verify immutable evidence against existing local Git; never award credit."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'src/main/java/com/dynasty').is_dir())
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def main():
    proposal = HERE / 'immune-reference-batch-029.json'
    raw = proposal.read_bytes()
    doc = json.loads(raw)
    assert doc['research_credit'] == 0 and doc['maximum_proposed_credit'] == 0
    assert not doc['production_changes'] and not doc['runtime_executed']
    prov = doc['provenance']
    manifest_raw = (ROOT / prov['manifest_path']).read_bytes()
    assert sha(manifest_raw) == prov['manifest_sha256']
    manifest = next(x for x in json.loads(manifest_raw) if x['repo'] == doc['repo'])
    assert manifest['commit'] == doc['commit'] and manifest['branch'] == doc['branch']
    files = {x['source']:x for x in manifest['files']}
    git = ['git', '--git-dir=' + str(ROOT / prov['bare_git_path'])]
    tree = subprocess.check_output(git + ['rev-parse', doc['commit'] + '^{tree}'], text=True).strip()
    assert tree == prov['git_tree'] == manifest['git_tree']
    ranges, unique_paths = [], set()
    for ref in doc['source_refs']:
        path = (ROOT / ref['path']).resolve()
        assert path.is_relative_to(ROOT)
        entry = files[ref['path']]
        source = path.read_bytes()
        assert sha(source) == ref['file_sha256'] == entry['sourceSha256']
        blob = hashlib.sha1(b'blob ' + str(len(source)).encode() + b'\0' + source).hexdigest()
        assert blob == ref['git_blob_sha1'] == entry['source_blob']
        assert ref['upstream_path'] == entry['path']
        assert source == subprocess.check_output(git + ['cat-file','blob',doc['commit']+':'+entry['path']])
        lines = source.decode().splitlines()
        start,end=ref['lines']
        assert 1 <= start <= end <= len(lines)
        assert ref['path'] not in unique_paths
        unique_paths.add(ref['path'])
        ranges.append({'path':ref['path'],'lines':ref['lines'],'range_text_sha256':sha('\n'.join(lines[start-1:end]).encode())})
    assert len(ranges) == 14
    assert sum(x['upstream_path'].endswith('.java') for x in doc['source_refs']) == 12
    snap = doc['dedup_snapshot']
    ledger_raw = (ROOT / snap['path']).read_bytes()
    ledger = json.loads(ledger_raw)
    by_id = {x['id']:x for x in ledger}
    for c in snap['comparisons']:
        expected = {k:v for k,v in by_id[c['accepted_id']].items() if k not in ['source_refs','auxiliary_refs']}
        assert c['full_semantic_decision_read'] == expected
        assert c['distinction']
    assert len(snap['comparisons']) == 6
    migration = doc['migration_overlap_screen']
    migration_raw = (ROOT / migration['path']).read_bytes()
    mrows = [json.loads(line) for line in migration_raw.decode().splitlines() if line.strip()]
    m_by_id = {x['candidate_id']:x for x in mrows}
    for c in migration['comparisons']:
        row = m_by_id[c['accepted_id']]
        assert all(row[k] == v for k,v in c['complete_semantic_decision_read'].items())
        assert row['status'] == 'accepted' and row['credit'] == 1
    result = {
        'status':'PASS', 'proposal_path':str(proposal.relative_to(ROOT)), 'proposal_sha256':sha(raw),
        'source_ranges_verified':len(ranges), 'unique_source_files_verified_against_existing_local_git':len(unique_paths),
        'java_files_with_cited_ranges_verified':12, 'unique_cited_source_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in ranges),
        'ranges':ranges, 'complete_semantic_comparisons_verified':len(snap['comparisons']),
        'migration_comparisons_verified':len(migration['comparisons']),
        'ledger_rows_observed':len(ledger), 'ledger_changed_since_snapshot':sha(ledger_raw)!=snap['sha256'],
        'migration_changed_since_snapshot':sha(migration_raw)!=migration['sha256'],
        'maximum_pending_credit':0, 'research_credit_awarded':0,
        'network_requests':0, 'game_or_upstream_execution':False,
        'limits':['Only source provenance/range/full-decision consistency verified.',
                  'Not a gameplay test, source semantic acceptance or independent review.',
                  'Absent local packet sender, empty handler and incomplete concrete/native lifecycle; no credit.'],
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
