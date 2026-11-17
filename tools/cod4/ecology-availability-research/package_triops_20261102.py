"""Package already manually read EA-C004 as one complete, still unaccepted proposal.

No source execution, network, game launch, or production change. EA15/16 remain
reserved by the existing unexecuted build_tenth.py draft; neither earns credit.
"""
import hashlib
import json
from datetime import datetime, timezone
from evidence import ROOT, DOCS, TOOLS, sha, verify_records


def main():
    proposal_path = DOCS / 'coordinator-triops-whole-chain-proposal-20261102.json'
    proposal_raw = proposal_path.read_bytes()
    assert sha(proposal_raw) == 'dff883662b1f85cb1a3faf04a9eb0e78c136fb35cf6c305d47087db6d8e5847a'
    p = json.loads(proposal_raw)
    target = DOCS / 'batch-011.json'
    assert not target.exists() and p['candidate_id'] == 'EA-C004'
    previous = [r for f in DOCS.glob('batch-*.json') for r in json.loads(f.read_text())['records']]
    assert len(previous) == 14 and 'EA-0017' not in {r['id'] for r in previous}
    assert p['semantic_key'] not in {r['semantic_key'] for r in previous}
    candidates = json.loads((DOCS / 'candidates-002.json').read_text())['records']
    assert sum(r['id'] == p['candidate_id'] for r in candidates) == 1
    base = TOOLS / 'sources/AlexModGuy__AlexsMobs'
    meta_raw, tree_raw = [(base / name).read_bytes() for name in ['source.json', 'tree.json']]
    meta, tree = json.loads(meta_raw), json.loads(tree_raw)
    assert meta['repo'] == 'AlexModGuy/AlexsMobs'
    assert meta['sha'] == tree['sha'] == p['source_commit'] and not tree['truncated']
    blobs = {r['path']: r['sha'] for r in tree['tree'] if r['type'] == 'blob'}
    chain, auxiliary = [], []
    copies = []
    for r in p['actual_read_ranges']:
        raw = (ROOT / r['path']).read_bytes()
        assert sha(raw) == r['file_sha256']
        a, z = r['lines']
        lines = raw.decode().splitlines(keepends=True)
        assert sha(''.join(lines[a - 1:z]).encode()) == r['excerpt_sha256']
        if r.get('repo') != meta['repo']:
            auxiliary.append(r)
            continue
        rel = r['source_path']
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert blob == r['git_blob_sha1'] == blobs[rel] and r['commit'] == meta['sha']
        destination = base / rel
        if destination.exists():
            assert destination.read_bytes() == raw
        else:
            # The one item-registry support is the same fixed tree/blob, not a new pin.
            assert rel == 'src/main/java/com/github/alexthe666/alexsmobs/item/AMItemRegistry.java'
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open('xb') as stream:
                stream.write(raw)
            copies.append({'source': r['path'], 'destination': str(destination.relative_to(ROOT)),
                           'file_sha256': sha(raw), 'git_blob_sha1': blob, 'research_credit': 0})
        excerpt = '\n'.join(raw.decode().splitlines()[a - 1:z])
        chain.append({
            'repo': meta['repo'], 'revision': meta['sha'], 'path': rel,
            'source_local': str(destination.relative_to(ROOT)), 'source_sha256': sha(raw),
            'git_blob_sha1': blob, 'pinned_tree_match': True,
            'source_metadata': str((base / 'source.json').relative_to(ROOT)),
            'tree_metadata': str((base / 'tree.json').relative_to(ROOT)),
            'provenance': 'Original fixed local official-repository tree and bytes, not fresh network verification',
            'line': a, 'end_line': z, 'excerpt': excerpt, 'excerpt_sha256': sha(excerpt.encode()),
            'url': f'https://github.com/{meta["repo"]}/blob/{meta["sha"]}/{rel}#L{a}-L{z}',
            'role': r.get('role', 'bounded containing-method or registry/tag context; no separate credit'),
            'evidence_kind': 'complete_file' if a == 1 and z == len(lines) else 'supporting_range'
        })
    assert len(chain) == 17 and len(auxiliary) == 12 and len(copies) <= 1
    observations = p['observations'] + [
        'Native hatch override first calls destroyBlock; its boolean result is not checked. '
        'Report the destruction request/order, not guaranteed removal or committed offspring.',
        'Hatched child setPersistenceRequired(true) bypasses the shown native Forge despawn-event and '
        'ordinary distance branches through their outer guard. This is not protection against every removal path.'
    ]
    limits = p['limitations'] + [
        'Formal chain contains17 pinned mod-source ranges;12 native archive-backed ranges are support0, '
        'bound in the immutable complete proposal and independent complete-chain review. '
        'No native archive source is disguised as a Git repository or separate mechanism.',
        'EA15/16 occur only in the unexecuted existing build_tenth draft and are not proposed or accepted ledger items. '
        'EA17 is a newly allocated whole mechanism from real original EA-C004; the candidate remains unchanged and zero-credit.',
        'Terrapin draft is not credited by this decision. Any later parent-carrier/genetics proposal needs actual '
        'full-chain independent comparison against this accepted-or-proposed egg lifecycle, not species/template counting.'
    ]
    row = {
        'id': 'EA-0017', 'semantic_key': p['semantic_key'], 'status': 'reviewed_proposed',
        'proposed_credit': 1, 'accepted_credit': 0,
        **{k: v for k, v in chain[0].items() if k != 'role'},
        'chain': chain, 'observation': observations, 'application': p['application'],
        'limits': limits, 'deduplication': p['semantic_comparisons'],
        'upstream_code_executed': False, 'independent_acceptance': 'pending actual independent receipt validation',
        'author_thread_id': '01a16364-cac0-7ca2-a042-a5312781ca34',
        'original_candidate_id': p['candidate_id'],
        'complete_chain_proposal': {'path': str(proposal_path.relative_to(ROOT)), 'sha256': sha(proposal_raw)},
        'native_auxiliary_artifact': p['native_artifact'], 'native_auxiliary_ranges': auxiliary,
        'supporting_ranges_credit': 0
    }
    batch = {
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'REVIEWED_PROPOSED_NOT_INDEPENDENTLY_ACCEPTED', 'records': [row],
        'proposed_credit': 1, 'accepted_credit': 0, 'integrity': verify_records([row]),
        'reserved_existing_unexecuted_draft_ids': ['EA-0015', 'EA-0016'],
        'original_source_metadata_sha256': sha(meta_raw), 'original_tree_sha256': sha(tree_raw),
        'source_copy_support_zero_credit': copies,
        'review_routing': {'EA-0017': 'actual existing general chat, explicit reviewer authorization before counting'},
        'runtime_credit': 0, 'production_changes': 0, 'checklist_deletions': 0
    }
    assert (base / 'source.json').read_bytes() == meta_raw and (base / 'tree.json').read_bytes() == tree_raw
    with target.open('x') as stream:
        stream.write(json.dumps(batch, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'batch': str(target.relative_to(ROOT)), 'sha256': sha(target.read_bytes()),
                      'id': row['id'], 'proposed_credit': 1, 'accepted_credit': 0,
                      'mod_ranges_support0': len(chain), 'native_ranges_support0': len(auxiliary),
                      'source_copies_support0': len(copies)}))


if __name__ == '__main__':
    main()
