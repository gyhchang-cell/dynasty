"""EA53 only: closed typed research receipt validation, no writes or old calls.

PROPOSED CODE. Not installed, executed, or authorized by this source file.
Local roles/paths are user-authorized workflow identity, not cryptography.
The caller supplies the existing Snapshot; its old validators are never called.
"""
from pathlib import Path
import hashlib
import io
import json
import re
import zipfile

AUTHOR = '01a12516-2eaf-73e2-b615-20f8b422158c'
MAIN = '01a16364-cac0-7ca2-a042-a5312781ca34'
IDENTIFIER = 'EA-0053'
LABEL = 'general original ManedWolf author after distinct Main complete policy review'
DECISION = 'ACCEPT_ONE_RELATED_MANED_WOLF_IMPLEMENTATION_WITH_EXPLICIT_LIMITS'
POLICY = 'tools/cod4/ecology-availability-research/maned_wolf_v36_policy.json'
DOCS = 'docs/cod4/audit-20261022/ecology-availability-research/'
RECEIPT = DOCS + 'independent-reviews/general-EA0053.json'
BATCH = DOCS + 'batch-044.json'
STATIC_REVIEW = DOCS + 'coordinator-maned-wolf-v36-v2-code-static-review-20261111.json'
GRANT = DOCS + 'coordinator-maned-wolf-v36-v2-actual-author-execution-grant-20261111.json'
EXTRA = {'reviewer', 'reviewer_thread_id', 'decision', 'reviewed_batch',
         'reviewed_batch_sha256', 'actual_author_confirmation', 'execution_grant',
         'actual_attempt_marker', 'author_execution_token'}


def require(value, message):
    if not value:
        raise ValueError('ManedWolf v36: ' + message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def physical(path):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'canonical absolute path')
    require(not any(p.is_symlink() for p in [path] + list(path.parents)), 'symlink path')
    return path


def relative(root, value):
    require(isinstance(value, str) and value and not Path(value).is_absolute() and '..' not in Path(value).parts, 'relative source path')
    p = physical(root / value)
    require(p.is_relative_to(root), 'path escapes repository')
    return p


def binding(desc, snap):
    require(type(desc) is dict and set(desc) == {'path', 'sha256', 'bytes'}, 'exact descriptor')
    require(type(desc['bytes']) is int and desc['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', desc['sha256']) is not None, 'descriptor types')
    raw = snap.read(physical(desc['path']))
    require(sha(raw) == desc['sha256'] and len(raw) == desc['bytes'], 'immutable binding changed: ' + desc['path'])
    return raw


def receipt_bytes(raw, actual):
    require(type(raw) is bytes and type(actual) is bytes and raw == actual, 'caller raw differs from actual receipt file')


def inventory_match(actual, expected):
    require(type(actual) is set and type(expected) is set and actual == expected, 'competing receipt/batch/candidate inventory drift')


def check_inventories(spec, root):
    # Repeat at both boundaries; this is not an atomic process lock.
    for inv in spec['baseline_inventories']:
        actual = {str(p) for p in physical(inv['directory']).glob(inv['glob']) if p.is_file()}
        expected = set(inv['paths'])
        if inv['glob'] == 'batch-*.json':
            expected.add(str(relative(root, BATCH)))
        elif inv['directory'] == str(relative(root, DOCS+'independent-reviews')):
            expected.add(str(relative(root, RECEIPT)))
        inventory_match(actual, expected)


def typed_sources(record, spec, snap, root):
    """Recompute exactly32 authorized ranges. Never trust claimed PASS results."""
    chain = record.get('chain')
    require(isinstance(chain, list) and len(chain) == 32, 'exact source count')
    require(sha(canonical(chain)) == spec['chain_canonical_sha256'], 'closed complete chain')
    result = []
    archive_cache = {}
    for e in chain:
        raw = snap.read(relative(root, e['source_local']))
        require(sha(raw) == e['source_sha256'], 'actual source hash')
        lo, hi = e['line'], e['end_line']
        lines = raw.decode('utf-8').splitlines()
        require(type(lo) is int and type(hi) is int and 1 <= lo <= hi <= len(lines), 'range')
        excerpt = '\n'.join(lines[lo-1:hi])
        require(excerpt == e['excerpt'] and sha(excerpt.encode()) == e['excerpt_sha256'], 'excerpt')
        require(sha(b''.join(raw.splitlines(keepends=True)[lo-1:hi])) == e['raw_excerpt_sha256'], 'raw excerpt')
        require(type(e['whole_file_read']) is bool, 'whole flag type')
        if e['whole_file_read']:
            require(lo == 1 and hi == len(lines), 'claimed whole source incomplete')
        row = {k:e[k] for k in ['source_kind', 'source_local', 'source_sha256', 'line', 'end_line', 'excerpt_sha256', 'raw_excerpt_sha256']}
        if e['source_kind'] == 'repository_git':
            require(e['repo'] == spec['repository'] and e['revision'] == spec['revision'], 'exact Git identity')
            base = 'tools/cod4/ecology-availability-research/sources/' + e['repo'].replace('/', '__') + '/'
            require(e['source_local'] == base + e['path'] and e['source_metadata'] == base+'source.json' and e['tree_metadata'] == base+'tree.json', 'Git repository namespace')
            meta_raw = snap.read(relative(root,e['source_metadata']))
            tree_raw = snap.read(relative(root,e['tree_metadata']))
            meta, tree = json.loads(meta_raw), json.loads(tree_raw)
            require(sha(meta_raw) == spec['repository_metadata_sha256'] and sha(tree_raw) == spec['repository_tree_sha256'], 'fixed metadata bytes')
            revisions = [meta[k] for k in ['sha','commit'] if k in meta]
            require(meta['repo'] == e['repo'] and revisions and all(x == e['revision'] for x in revisions), 'metadata pin')
            require(tree['sha'] == e['revision'] and tree['truncated'] is False, 'tree pin/completeness')
            matches = [x for x in tree['tree'] if x['path'] == e['path']]
            blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            require(len(matches) == 1 and matches[0]['type'] == 'blob' and matches[0]['sha'] == blob == e['git_blob_sha1'] and matches[0]['size'] == len(raw), 'actual Git blob/size')
            require(e['url'] == f"https://github.com/{e['repo']}/blob/{e['revision']}/{e['path']}#L{lo}-L{hi}", 'fixed URL')
            row.update(repo=e['repo'], revision=e['revision'], git_blob_sha1=blob,
                source_metadata_sha256=sha(meta_raw), tree_metadata_sha256=sha(tree_raw))
        elif e['source_kind'] == 'artifact_native':
            require(not any(k in e for k in ['repo','revision','git_blob_sha1','source_metadata','tree_metadata','url']), 'native cannot assert Git')
            require(e['source_coordinate'] == spec['native_coordinate'] and e['source_artifact'] == spec['native_artifact'], 'typed native coordinate/archive')
            artifact = e['source_artifact']
            path = relative(root,artifact['path'])
            if str(path) not in archive_cache:
                blob = snap.read(path)
                require(sha(blob) == artifact['sha256'], 'actual archive SHA256')
                archive_cache[str(path)] = blob
            with zipfile.ZipFile(io.BytesIO(archive_cache[str(path)])) as z:
                require(z.namelist().count(e['path']) == 1 and z.read(e['path']) == raw, 'unique archive entry bytes')
            require(e['source_local'] == 'tools/cod4/ecology-availability-research/sources/native-artifact-forge-1.20.1-47.4.10/'+e['path'], 'native cache namespace')
            row.update(source_coordinate=e['source_coordinate'], source_artifact=artifact, archive_entry=e['path'])
        else:
            raise ValueError('ManedWolf v36: unrecognized source kind')
        result.append(row)
    require(sum(e['source_kind']=='repository_git' for e in result)==21 and sum(e['source_kind']=='artifact_native' for e in result)==11, 'typed21+11')
    return result


def record_shape(receipt, record, spec):
    require(sha(canonical(record)) == spec['record_canonical_sha256'], 'whole record immutable')
    require(set(receipt) == set(record) | EXTRA, 'closed receipt fields')
    for k,v in record.items():
        if k != 'accepted_credit':
            require(canonical(receipt[k]) == canonical(v), 'whole record field: '+k)
    require(record['id'] == IDENTIFIER and record['general_context_schema']=='maned-wolf-source-v36', 'exact ID/context')
    require(record['author_thread_id'] == AUTHOR and record['independent_reviewer_thread_id'] == MAIN and AUTHOR != MAIN, 'distinct actual roles')
    require(type(record['accepted_credit']) is int and record['accepted_credit']==0 and type(record['proposed_credit']) is int and record['proposed_credit']==1, 'one pending whole')
    require(receipt['reviewer']==LABEL and receipt['reviewer_thread_id']==AUTHOR and receipt['decision']==DECISION, 'actual author/decision')
    require(type(receipt['accepted_credit']) is int and receipt['accepted_credit']==1 and receipt['actual_author_confirmation'] is True, 'not automatic acceptance')
    require([len(record[k]) for k in ['observation','application','limits']]==[16,2,6], 'original judgment sizes')
    require(len(record['Main_independent_findings'])==17 and len(record['Main_additional_limits'])==12 and len(record['actual_author_finding_responses'])==17 and len(record['actual_author_limit_responses'])==12, 'Main and actual author complete limits')
    for k in ['global_novelty_credit','new_migration_credit','supporting_ranges_credit','native_gameplay_credit','runtime_material_payment_credit','native_birth_kill_pickup_credit','building_credit','art_credit']:
        require(type(record[k]) is int and record[k]==0, 'no extra credit: '+k)
    require(record['upstream_code_executed'] is False, 'no upstream execution')


def validate_receipt(path, raw, batches_by_id, snap, root):
    """No grant creation/consumption here. A new reviewed one-shot author is prerequisite."""
    root = physical(root)
    require(not getattr(snap,'overrides',None), 'synthetic snapshot cannot produce actual acceptance')
    require(physical(Path(path).absolute()) == relative(root,RECEIPT), 'exact receipt namespace')
    actual_receipt_raw = snap.read(relative(root, RECEIPT))
    receipt_bytes(raw, actual_receipt_raw)
    spec = snap.json(relative(root,POLICY))
    require(spec['schema']=='maned-wolf-closed-v36-policy-v1' and spec['id']==IDENTIFIER, 'exact policy')
    bp, record = batches_by_id[IDENTIFIER]
    require(physical(Path(bp).absolute())==relative(root,BATCH), 'exact batch path')
    batch_raw = snap.read(relative(root,BATCH))
    require(sha(batch_raw)==spec['batch_sha256'] and snap.json(relative(root,BATCH))['records']==[record], 'exact one-record batch bytes')
    receipt = json.loads(actual_receipt_raw)
    record_shape(receipt,record,spec)
    require(receipt['reviewed_batch']==BATCH and receipt['reviewed_batch_sha256']==sha(batch_raw), 'reviewed batch binding')
    # Frozen old51/raw five outputs and current510 remain actual prerequisites,
    # not revalidated old receipts. Changing any input stops the entire new delta.
    for d in spec['frozen_inputs']:
        binding(d,snap)
    baseline = {n:snap.json(physical(d['path'])) for n,d in spec['five_baseline'].items()}
    master = baseline['master-acceptance-ledger.json']
    require(master['independently_accepted']==51 and len(master['accepted'])==51 and sha(canonical(master['accepted']))==spec['old51_canonical_sha256'], 'complete old51')
    require(not any(r['id']==IDENTIFIER or r['semantic_key']==record['semantic_key'] for r in master['accepted']), 'duplicate ID/key zero')
    check_inventories(spec, root)
    bindings = {k:json.loads(binding(d,snap)) for k,d in record['immutable_bindings'].items()}
    candidate, main, author = [bindings[k] for k in ['candidate','Main_review','author_confirmation']]
    require(candidate['formal_id'] is None and candidate['accepted_credit']==candidate['applied_credit']==0, 'original candidate not rewritten')
    require(record['complete_original_judgment']==main['original_judgment_preserved']==author['original_judgment_full_unchanged'], 'whole original6field judgment')
    require(record['Main_independent_findings']==main['independent_findings'] and record['Main_additional_limits']==main['limits'], 'actual Main judgment')
    require(record['actual_author_finding_responses']==author['finding_responses'] and record['actual_author_limit_responses']==author['limit_responses'], '29 actual author responses')
    require(record['complete_EA10']==main['EA10_additional_saved_whole_projection'], 'EA10 whole preserved')
    require(record['current_program510_context']==spec['current_program510_context'], 'current510 exact context')
    checks = typed_sources(record,spec,snap,root)
    # The exact code proposal is reviewed by a distinct Main, then a NEW grant
    # binds installed bytes and a NEW marker; no old token/proof is accepted.
    sr_raw = snap.read(relative(root,STATIC_REVIEW))
    sr = json.loads(sr_raw)
    require(sr['reviewer_thread_id']==MAIN and sr['decision']=='PASS_EXACT_MANED_WOLF_V36_CODE_PROPOSAL_ONLY', 'distinct Main current exact code review')
    code_proposal = sr['code_proposal']
    require(code_proposal['path']==spec['code_proposal_path'], 'exact reviewed code proposal namespace')
    proposal = json.loads(binding(code_proposal,snap))
    grant_raw = binding(receipt['execution_grant'],snap)
    require(receipt['execution_grant']['path']==str(relative(root,GRANT)), 'new author grant namespace')
    grant = json.loads(grant_raw)
    require(grant['reviewer_thread_id']==MAIN and grant['purpose']=='EXECUTE_ACTUAL_MANED_WOLF_V36_V2_AUTHOR_ONCE_NO_AGGREGATION' and grant['actual_author_thread_id']==AUTHOR, 'new Main author authority')
    require(grant['assigned_record_id']==IDENTIFIER and grant['assigned_batch']==BATCH, 'Main explicitly assigns proposed ID/batch')
    require(grant['code_proposal']==code_proposal and grant['Main_static_review']==dict(path=str(relative(root,STATIC_REVIEW)),sha256=sha(sr_raw),bytes=len(sr_raw)), 'exact new review/grant')
    require(grant['author_execution_authorized'] is True and grant['one_execution_only'] is True and grant['no_retry_after_any_attempt'] is True and grant['external_timeout_seconds']==60, 'one attempt bounded')
    for k in ['aggregation_authorized','old_validator_execution_authorized','old_executor_replay_authorized','upstream_execution_authorized','production_authorized']:
        require(grant[k] is False, 'forbidden grant scope: '+k)
    token = receipt['author_execution_token']
    require(isinstance(token,str) and re.fullmatch(r'maned-wolf-v36-v2-[0-9a-f]{48}',token) is not None and grant['author_execution_token']==token, 'fresh namespaced token')
    installed = proposal['installed_files']
    require(grant['exact_installed_files']==[{k:e[k] for k in ['path','sha256','bytes']} for e in installed], 'exact installed tool allowlist')
    for e in installed:
        binding({k:e[k] for k in ['path','sha256','bytes']},snap)
    for e in proposal['unchanged_installed_dependencies']:
        binding(e,snap)
    install_desc = grant['Main_actual_install_review']
    require(install_desc['path']==str(relative(root,DOCS+'coordinator-maned-wolf-v36-v2-actual-install-review-20261111.json')), 'distinct actual install review namespace')
    installed_review = json.loads(binding(install_desc,snap))
    require(installed_review['reviewer_thread_id']==MAIN and installed_review['decision']=='PASS_ACTUAL_MANED_WOLF_V36_INSTALL_NORMALIZATION' and installed_review['code_proposal']==code_proposal and installed_review['exact_installed_files']==grant['exact_installed_files'] and installed_review['actual_batch_sha256']==sha(batch_raw), 'Main actual install and normalization closure')
    marker_desc = receipt['actual_attempt_marker']
    require(marker_desc['path']==spec['future_author_marker_path'] and grant['output_directory']==str(Path(marker_desc['path']).parent), 'new actual attempt namespace')
    marker = json.loads(binding(marker_desc,snap))
    require(marker['author_thread_id']==AUTHOR and marker['phase']=='MANED_WOLF_V36_V2_ACTUAL_AUTHOR_ONCE' and marker['attempt_consumed'] is True and marker['author_execution_token']==token and marker['grant_sha256']==sha(grant_raw) and marker['code_proposal']==code_proposal, 'genuine new marker bound to exact attempt')
    require(not getattr(snap,'overrides',None), 'actual snapshot not fixtures')
    require(isinstance(getattr(snap,'bytes',None),dict), 'actual Snapshot byte closure')
    for p, saved in snap.bytes.items():
        current = physical(Path(p).absolute()).read_bytes()
        require(sha(current)==sha(saved) and len(current)==len(saved), 'current input changed before validation return')
    check_inventories(spec, root)
    return dict(state='validated_acceptance',id=IDENTIFIER,role='general',reviewer=LABEL,decision=DECISION,
        semantic_key=record['semantic_key'],accepted_credit=1,receipt=RECEIPT,receipt_sha256=sha(actual_receipt_raw),
        batch=BATCH,batch_sha256=sha(batch_raw),source_checks_recomputed=checks,
        base_resource_checks_recomputed=[],supporting_ranges_credit=0,limitations=record['limits'],
        observed_chain=record['observation'],complete_chain_support_proof=dict(
            bindings=record['immutable_bindings'],complete_original_judgment=record['complete_original_judgment'],
            Main_additional_limits=record['Main_additional_limits'],actual_author_limit_responses=record['actual_author_limit_responses'],
            actual_original_author_thread=AUTHOR,independent_semantic_acceptance_thread=MAIN,
            current_program510_context=record['current_program510_context'],code_proposal=code_proposal,
            actual_author_execution_grant=receipt['execution_grant'],actual_attempt_marker=marker_desc,
            native_gameplay_credit=0,global_novelty_credit=0,new_migration_credit=0,runtime_material_payment_credit=0,
            authorization_identity_boundary='User-authorized local roles and new reviewed workflow, not cryptographic identity.'))
