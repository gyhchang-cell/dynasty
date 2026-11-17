"""Prepare a reviewable EA18-only research delta. Does not install or aggregate."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'tools/cod4/ecology-availability-research'
DOCS = ROOT / 'docs/cod4/audit-20261022/ecology-availability-research'
STAGE = TOOLS / '.work/terrapin-v5-draft'
STAGE.mkdir(exist_ok=True)
assert not (STAGE / 'manifest.json').exists(), 'Immutable staged delta exists; do not rerun.'
sha = lambda b: hashlib.sha256(b).hexdigest()
bindings = {
    'complete_chain_proposal': dict(path=str((DOCS / 'coordinator-terrapin-parent-payload-proposal-20261102.json').relative_to(ROOT)),
        sha256='1607ef4f719ab013a0d0bb59cb72499e55677a4d781f513e88e8429719fcbf47'),
    'complete_chain_review': dict(path=str((DOCS / 'independent-terrapin-parent-payload-review-20261103.json').relative_to(ROOT)),
        sha256='bb28c1f73828ba83fcb2c12e84c08d6b05f8c0b24a31eee316bbf0302d9f6e55'),
    'complete_chain_clarification': dict(path=str((DOCS / 'coordinator-terrapin-nbt-merge-clarification-20261102.json').relative_to(ROOT)),
        sha256='ca2fca70dcc17651265bd3415b878b9ca9fb856a041dd2539a0fc20ddf2ccaae'),
}
for b in bindings.values():
    assert sha((ROOT / b['path']).read_bytes()) == b['sha256']
proposal = json.loads((ROOT / bindings['complete_chain_proposal']['path']).read_text())
peer = json.loads((ROOT / bindings['complete_chain_review']['path']).read_text())
base = TOOLS / 'sources/AlexModGuy__AlexsMobs'
tree = json.loads((base / 'tree.json').read_text())
assert tree['sha'] == proposal['source_commit'] and tree['truncated'] is False
chain, copies = [], {}
for ref in proposal['actual_read_ranges']:
    if ref['source_kind'] != 'fixed_mod_git':
        continue
    original = ROOT / ref['path']
    raw = original.read_bytes()
    assert sha(raw) == ref['file_sha256']
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    assert blob == ref['git_blob_sha1'] == next(x['sha'] for x in tree['tree'] if x['path'] == ref['source_path'])
    target = base / ref['source_path']
    if target.exists():
        assert target.read_bytes() == raw
    else:
        copies[str(target.relative_to(ROOT))] = dict(original=ref['path'], sha256=sha(raw))
    lo, hi = ref['lines']
    excerpt = '\n'.join(raw.decode().splitlines()[lo-1:hi])
    chain.append(dict(repo='AlexModGuy/AlexsMobs', revision=proposal['source_commit'],
        path=ref['source_path'], source_local=str(target.relative_to(ROOT)), source_sha256=sha(raw),
        git_blob_sha1=blob, source_metadata=str((base/'source.json').relative_to(ROOT)),
        tree_metadata=str((base/'tree.json').relative_to(ROOT)),
        provenance='Same cached fixed Git tree and exact original bytes; no new acquisition or semantic credit.',
        line=lo, end_line=hi, excerpt=excerpt, excerpt_sha256=sha(excerpt.encode()), url=ref['url']))
assert len(chain) == 22
record = dict(chain[0], id='EA-0018', status='reviewed_proposed', proposed_credit=1,
    accepted_credit=0, supporting_ranges_credit=0, semantic_key=proposal['semantic_key'],
    author_thread_id=proposal['author_thread_id'], general_context_schema='terrapin-parent-payload-v1',
    chain=chain, native_auxiliary_artifact=proposal['native_artifact'],
    native_auxiliary_ranges=[x for x in proposal['actual_read_ranges'] if x['source_kind']=='native_forge_archive'],
    observation=peer['observed_chain'], application=proposal['application'],
    limits=peer['limitations'] + [x['correction'] for x in peer['proposal_corrections_and_conditions']],
    deduplication=peer['decision_rationale'], **bindings)
batch = dict(schema='ecology-reviewed-proposals-v5', status='ACTUAL_REVIEWED_PROPOSAL_PENDING_REAL_GENERAL_RECEIPT_ZERO_CREDIT',
    records=[record], candidate_identifier_invented=False,
    publication_scope='EA18 allocates the next actual identifier after EA17; unexecuted EA15 draft remains unaccepted.')
(STAGE / 'batch-013.json').write_text(json.dumps(batch, ensure_ascii=False, indent=2)+'\n')
(STAGE / 'source-copies.json').write_text(json.dumps(copies, ensure_ascii=False, indent=2)+'\n')

code = (TOOLS / 'receipt_validation.py').read_text()
assert sha(code.encode()) == '7e6f0121d8b572a4dafb296b224b0bff004c895a968802fbd3b49756a8b332fc'
code = code.replace("'allowed_ids': {'EA-0016', 'EA-0017'},", "'allowed_ids': {'EA-0016', 'EA-0017', 'EA-0018'},")
context = '''
def general_terrapin_context(review, record, snap, policy, identifier):
    """EA18 only: actual independent parent-payload review; all ranges support0."""
    require(identifier == 'EA-0018' and identifier in policy['allowed_ids'], 'EA18 reviewer scope mismatch')
    require(review.get('reviewer_thread_id') == policy['thread_id'] and
            record.get('author_thread_id') == policy['proposal_author_thread_id'] and
            record['author_thread_id'] != review['reviewer_thread_id'], 'EA18 actual independent authors mismatch')
    require(record.get('general_context_schema') == 'terrapin-parent-payload-v1', 'EA18 wrong context schema')
    require(all(type(record.get(k)) is int and record[k] == value for k, value in
                [('proposed_credit',1),('accepted_credit',0),('supporting_ranges_credit',0)]), 'EA18 exact proposal credits required')
    require(all(k not in obj for obj in (record,review) for k in ('candidate_id','original_candidate_id')),
            'EA18 has no candidate identifier')
    documents = {}
    for field, expected in GENERAL_EA18_BINDINGS.items():
        require(record.get(field) == review.get(field) == expected, 'EA18 exact document binding mismatch: '+field)
        path = local_path(expected['path'], DOCS)
        require(sha(snap.read(path)) == expected['sha256'], 'EA18 immutable document SHA mismatch')
        documents[field] = snap.json(path)
    proposal, peer = documents['complete_chain_proposal'], documents['complete_chain_review']
    require(peer.get('reviewer_thread_id') == policy['thread_id'] and
            peer.get('proposal') == GENERAL_EA18_BINDINGS['complete_chain_proposal'] and
            peer.get('status') == 'INDEPENDENT_COMPLETE_PARENT_PAYLOAD_REVIEW_RECOMMEND_AT_MOST_ONE_WITH_CONDITIONAL_CORRECTIONS_ZERO_APPLIED_CREDIT' and
            type(peer.get('recommended_maximum_credit')) is int and peer['recommended_maximum_credit'] == 1 and
            all(type(peer.get(k)) is int and peer[k] == 0 for k in ('accepted_credit','applied_credit','supporting_ranges_credit')),
            'EA18 eligible actual independent recommendation missing')
    require(record['repo'] == 'AlexModGuy/AlexsMobs' and record['revision'] == proposal['source_commit'] ==
            '09755dade2cfbdf14839e026d3af446f9d3ff843' and record['semantic_key'] == proposal['semantic_key'] == peer['semantic_key'] ==
            'phenotypic-parent-payload-across-pregnancy-egg-block-stack-silk-and-bucket-boundaries', 'EA18 source/semantic identity mismatch')
    require(record['observation'] == review.get('observed_chain') == peer['observed_chain'] and review.get('limits') == record['limits'] and
            record['limits'] == peer['limitations']+[x['correction'] for x in peer['proposal_corrections_and_conditions']],
            'EA18 complete corrected semantic observations/limits mismatch')
    refs, checks, formal = proposal['actual_read_ranges'], peer['range_checks'], record['chain']
    require(len(refs) == len(checks) == 51 and len(formal) == 22, 'EA18 exact51/22 range coverage missing')
    artifact = proposal['native_artifact']
    require(artifact == record.get('native_auxiliary_artifact') == peer['provenance']['native_artifact'] and
            record.get('native_auxiliary_ranges') == [r for r in refs if r['source_kind']=='native_forge_archive'],
            'EA18 native artifact/range mismatch')
    archive_path = Path(artifact['source_archive']).resolve()
    require(archive_path.is_relative_to((ROOT/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches').resolve()),
            'EA18 native archive outside original cache')
    archive_raw = snap.read(archive_path)
    require(sha(archive_raw) == artifact['sha'] == peer['provenance']['native_archive_sha256_recomputed'], 'EA18 actual archive SHA mismatch')
    native_base = local_path(artifact['private_source'], ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources')
    native_files, identities, mod_count = set(), set(), 0
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        for index,(ref,check) in enumerate(zip(refs,checks)):
            require(type(check.get('index')) is int and check['index']==index and check.get('actual_text_read') is True and
                    ref.get('actually_read') is True and all(type(x.get('support_credit')) is int and x['support_credit']==0 for x in (ref,check)),
                    'EA18 actual read/support identity mismatch')
            for field in ('path','source_path','lines','file_sha256','excerpt_sha256','source_kind'):
                require(ref[field] == check.get(field), 'EA18 complete source binding mismatch: '+field)
            source = local_path(ref['path'], ROOT/'tools/cod4')
            raw = snap.read(source); lo,hi=ref['lines']; lines=raw.decode().splitlines(keepends=True)
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(lines), 'EA18 invalid range')
            identity=(ref['path'],lo,hi)
            require(identity not in identities, 'EA18 duplicate complete range')
            identities.add(identity)
            require(sha(raw)==ref['file_sha256'] and sha(''.join(lines[lo-1:hi]).encode())==ref['excerpt_sha256'],
                    'EA18 actual complete source/excerpt mismatch')
            if ref['source_kind']=='fixed_mod_git':
                mod_count+=1
                require(ref['repo']==check.get('repo')==record['repo'] and ref['commit']==check.get('commit')==record['revision'] and
                        check.get('tree_blob_matches') is True, 'EA18 original mod identity mismatch')
                linked=[e for e in formal if (e['path'],e['line'],e['end_line'])==(ref['source_path'],lo,hi)]
                require(len(linked)==1, 'EA18 mod range not linked exactly once')
                e=linked[0]
                require(e['source_sha256']==sha(raw) and e['git_blob_sha1']==ref['git_blob_sha1']==check.get('git_blob_sha1') and
                        e['url']==ref['url']==check.get('url') and snap.read(local_path(e['source_local'],TOOLS/'sources'))==raw,
                        'EA18 formal/original source/blob/URL mismatch')
                proof=validate_source(e,snap)
                require(proof['source_metadata_sha256']==proposal['source_metadata_sha256']==check.get('source_metadata_sha256') and
                        proof['tree_metadata_sha256']==proposal['source_tree_sha256']==check.get('tree_metadata_sha256'),
                        'EA18 actual metadata/tree mismatch')
            else:
                require(ref['source_kind']=='native_forge_archive' and source==(native_base/ref['source_path']).resolve(),
                        'EA18 native source identity mismatch')
                require(ref.get('source_archive_sha256')==check.get('source_archive_sha256')==artifact['sha'] and
                        ref.get('archive_entry_exact') is True and check.get('archive_entry_exact') is True and
                        archive.read(ref['source_path'])==raw, 'EA18 actual native entry mismatch')
                native_files.add(ref['source_path'])
        extras=peer.get('additional_native_support_checks')
        require(isinstance(extras,list) and len(extras)==10, 'EA18 ten native delta supports missing')
        for index,ref in enumerate(extras):
            require(type(ref.get('index')) is int and ref['index']==index and ref.get('actual_text_read') is True and
                    type(ref.get('support_credit')) is int and ref['support_credit']==0 and
                    ref.get('source_kind')=='native_forge_archive' and ref.get('source_archive_sha256')==artifact['sha'] and
                    ref.get('archive_entry_exact') is True, 'EA18 native delta reviewer binding mismatch')
            source=local_path(ref['path'],native_base)
            require(source==(native_base/ref['source_path']).resolve(), 'EA18 native delta path mismatch')
            raw=snap.read(source); lo,hi=ref['lines']; lines=raw.decode().splitlines(keepends=True)
            require(type(lo) is int and type(hi) is int and 1<=lo<=hi<=len(lines) and archive.read(ref['source_path'])==raw and
                    sha(raw)==ref['file_sha256'] and sha(''.join(lines[lo-1:hi]).encode())==ref['excerpt_sha256'],
                    'EA18 actual native delta bytes/excerpt mismatch')
    require(mod_count==22 and len(native_files)==12, 'EA18 exact mod/native file coverage missing')
    return dict(proposal=GENERAL_EA18_BINDINGS['complete_chain_proposal'], review=GENERAL_EA18_BINDINGS['complete_chain_review'],
                clarification=GENERAL_EA18_BINDINGS['complete_chain_clarification'], range_count_support0=51,
                native_delta_ranges_support0=10, mod_ranges_support0=22, native_ranges_support0=29, native_files_support0=12,
                native_archive_sha256=artifact['sha'], original_proposal_author_thread_id=record['author_thread_id'],
                actual_reviewer_thread_id=review['reviewer_thread_id'], native_gameplay_credit=0)

'''
old_route = "complete_proof=(general_skreecher_context(d,r,snap,policy,identifier) if identifier=='EA-0016' else general_context(d,r,snap,policy,identifier)) if role=='general' else None"
new_route = "complete_proof=((general_terrapin_context(d,r,snap,policy,identifier) if identifier=='EA-0018' else general_skreecher_context(d,r,snap,policy,identifier) if identifier=='EA-0016' else general_context(d,r,snap,policy,identifier)) if role=='general' else None)"
assert code.count(old_route) == 1
code = code.replace(old_route,new_route)
assert code.count('def validate_receipt(') == 1
code = code.replace('def validate_receipt(', 'GENERAL_EA18_BINDINGS = '+repr(bindings)+'\n\n'+context+'def validate_receipt(')
(STAGE / 'receipt_validation.py').write_text(code)
summary=(TOOLS/'summarize.py').read_text()
assert sha(summary.encode()) == '36f74cf758429e4751945d1822238e5e4b89efada3922953754bea8fe20af8a6'
summary=summary.replace("'ecology-master-acceptance-v4'", "'ecology-master-acceptance-v5'")
(STAGE/'summarize.py').write_text(summary)
manifest=dict(status='STAGED_EA18_ONLY_PENDING_INDEPENDENT_DELTA_REVIEW_NO_FORMAL_RECEIPT_OR_CREDIT',
    baseline_validator_sha256=sha((TOOLS/'receipt_validation.py').read_bytes()),
    baseline_summary_sha256=sha((TOOLS/'summarize.py').read_bytes()),
    baseline_ledger_sha256=sha((DOCS/'master-acceptance-ledger.json').read_bytes()),
    files={p.name:sha(p.read_bytes()) for p in STAGE.glob('*') if p.is_file()},
    bindings=bindings, formal_batch_target=str((DOCS/'batch-013.json').relative_to(ROOT)),
    credit=0, game_starts=0, production_changes=0)
(STAGE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'stage':str(STAGE.relative_to(ROOT)),'manifest_sha256':sha((STAGE/'manifest.json').read_bytes()),
                  'formal_source_copies_pending':len(copies),'accepted_credit':0}))
