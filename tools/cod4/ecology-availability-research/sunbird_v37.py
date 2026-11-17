"""UNINSTALLED, UNEXECUTED proposed single-Sunbird author receipt validator.

No entry point, file writes, old validator calls, installation or aggregation.
The prospective ID is assigned only by a separate future exact Main grant.
Local workflow roles/paths are user-authorized identities, not cryptography.
"""
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

AUTHOR = '01a12516-2eaf-73e2-b615-20f8b422158c'
MAIN = '01a16364-cac0-7ca2-a042-a5312781ca34'
IDENTIFIER = 'EA-0054'  # proposed parameter only; this source grants nothing
DOCS = 'docs/cod4/audit-20261022/ecology-availability-research/'
BATCH = DOCS + 'batch-045.json'
RECEIPT = DOCS + 'independent-reviews/general-EA0054.json'
POLICY = 'tools/cod4/ecology-availability-research/sunbird_v37_policy.json'
LABEL = 'general original Sunbird author after distinct Main complete policy and actual ACK review'
DECISION = 'ACCEPT_ONE_RELATED_SUNBIRD_IMPLEMENTATION_WITH_EXPLICIT_LIMITS'
EXTRA = {'reviewer', 'reviewer_thread_id', 'decision', 'reviewed_batch',
         'reviewed_batch_sha256', 'actual_author_confirmation', 'execution_grant',
         'actual_attempt_marker', 'author_execution_token'}


def need(value, message):
    if not value:
        raise ValueError('Sunbird proposed v37: ' + message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def physical(value):
    p = Path(value)
    need(p.is_absolute() and '..' not in p.parts and
         not any(q.is_symlink() for q in [p] + list(p.parents)), 'physical absolute path')
    return p


def relative(root, value):
    need(type(value) is str and value and not Path(value).is_absolute()
         and '..' not in Path(value).parts, 'closed relative path')
    p = physical(root / value)
    need(p.is_relative_to(root), 'outside repository')
    return p


def bound(descriptor, snap):
    need(type(descriptor) is dict and set(descriptor) == {'path', 'sha256', 'bytes'}, 'closed descriptor')
    need(type(descriptor['bytes']) is int and descriptor['bytes'] >= 0
         and re.fullmatch('[0-9a-f]{64}', descriptor['sha256']), 'descriptor values')
    raw = snap.read(physical(descriptor['path']))
    need(len(raw) == descriptor['bytes'] and sha(raw) == descriptor['sha256'], 'changed bound input')
    return raw


def inventory_check(spec):
    for inv in spec['baseline_inventories']:
        paths = list(physical(inv['directory']).glob(inv['glob']))
        need(all(physical(str(p)).is_file() for p in paths), 'inventory file type')
        need({str(p) for p in paths} == set(inv['paths']) | set(inv['only_allowed_future_paths']),
             'competing or missing evidence')


def sources(record, spec, snap, root):
    chain = record['chain']
    need(sha(canonical(chain)) == spec['chain_canonical_sha256'], 'closed entire source chain')
    result, archives = [], {}
    for e in chain:
        raw = snap.read(relative(root, e['source_local']))
        need(sha(raw) == e['source_sha256'], 'source bytes')
        a, b = e['line'], e['end_line']
        need(type(a) is int and type(b) is int and 1 <= a <= b <= len(raw.splitlines()), 'source range')
        text = '\n'.join(raw.decode('utf-8').splitlines()[a-1:b])
        need(text == e['excerpt'] and sha(text.encode()) == e['excerpt_sha256']
             and sha(b''.join(raw.splitlines(keepends=True)[a-1:b])) == e['raw_excerpt_sha256'], 'both excerpt encodings')
        need(type(e['whole_file_read']) is bool, 'whole flag')
        if e['whole_file_read']:
            need(a == 1 and b == len(raw.splitlines()), 'whole source coverage')
        row = {k:e[k] for k in ('source_kind','source_local','source_sha256','line','end_line','excerpt_sha256','raw_excerpt_sha256')}
        if e['source_kind'] == 'repository_git':
            need(e['repo'] == spec['repository'] and e['revision'] == spec['revision'], 'fixed repository pin')
            base = 'tools/cod4/ecology-availability-research/sources/AlexModGuy__AlexsMobs/'
            need(e['source_local'] == base + e['path'] and e['source_metadata'] == base+'source.json'
                 and e['tree_metadata'] == base+'tree.json', 'fixed Git namespace')
            mr, tr = [snap.read(relative(root, e[k])) for k in ('source_metadata','tree_metadata')]
            need(sha(mr) == spec['repository_metadata_sha256'] and sha(tr) == spec['repository_tree_sha256'], 'fixed local metadata')
            meta, tree = json.loads(mr), json.loads(tr)
            pins = [meta[k] for k in ('sha','commit') if k in meta]
            need(meta['repo'] == e['repo'] and pins and all(p == e['revision'] for p in pins), 'metadata pin')
            need(tree['truncated'] is False and tree['sha'] == e['revision'], 'local complete tree snapshot')
            matches = [x for x in tree['tree'] if x['path'] == e['path']]
            blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            need(len(matches) == 1 and matches[0]['type'] == 'blob' and matches[0]['size'] == len(raw)
                 and matches[0]['sha'] == blob == e['git_blob_sha1'], 'Git blob and size')
            need(e['url'] == f"https://github.com/{e['repo']}/blob/{e['revision']}/{e['path']}#L{a}-L{b}", 'exact source URL')
            row.update(repo=e['repo'],revision=e['revision'],git_blob_sha1=blob,
                source_metadata_sha256=sha(mr),tree_metadata_sha256=sha(tr),
                commit_to_root_tree_bridge_independently_certified=False)
        else:
            need(e['source_kind'] == 'artifact_native' and not any(k in e for k in
                 ('repo','revision','git_blob_sha1','source_metadata','tree_metadata','url')), 'typed native, no fake Git')
            need(e['source_coordinate'] == spec['native_coordinate']
                 and e['source_artifact'] == spec['native_artifact'], 'native coordinate/archive')
            artifact = e['source_artifact']; ap = relative(root, artifact['path'])
            if str(ap) not in archives:
                archives[str(ap)] = snap.read(ap)
                need(sha(archives[str(ap)]) == artifact['sha256'], 'archive bytes')
            with zipfile.ZipFile(io.BytesIO(archives[str(ap)])) as z:
                need(z.namelist().count(e['path']) == 1 and z.read(e['path']) == raw, 'unique native entry')
            need(e['source_local'] == 'tools/cod4/ecology-availability-research/sources/native-artifact-forge-1.20.1-47.4.10/'+e['path'], 'native cache namespace')
            row.update(source_coordinate=e['source_coordinate'],source_artifact=artifact,archive_entry=e['path'])
        result.append(row)
    need([sum(e['source_kind'] == k for e in result) for k in ('repository_git','artifact_native')]
         == spec['typed_range_counts'], 'exact typed ranges')
    return result


def validate_receipt(path, raw, batches_by_id, snap, root):
    root = physical(root)
    need(not getattr(snap, 'overrides', None), 'fixtures cannot produce actual acceptance')
    need(physical(Path(path).absolute()) == relative(root, RECEIPT), 'exact one receipt path')
    actual = snap.read(relative(root, RECEIPT));need(type(raw) is bytes and actual == raw, 'actual on-disk receipt')
    spec = snap.json(relative(root, POLICY))
    need(spec['schema'] == 'sunbird-proposed-v37-closed-policy-v1' and spec['proposed_id'] == IDENTIFIER, 'exact proposed policy')
    bp, record = batches_by_id[IDENTIFIER]
    need(physical(Path(bp).absolute()) == relative(root, BATCH), 'single batch path')
    br = snap.read(relative(root, BATCH))
    need(sha(br) == spec['batch_sha256'] and json.loads(br)['records'] == [record]
         and sha(canonical(record)) == spec['record_canonical_sha256'], 'exact whole batch/record')
    receipt = json.loads(actual)
    need(set(receipt) == set(record) | EXTRA, 'closed receipt fields')
    for k, v in record.items():
        if k != 'accepted_credit':need(canonical(receipt[k]) == canonical(v), 'whole record field '+k)
    need(record['id'] == IDENTIFIER and record['general_context_schema'] == 'sunbird-source-v37'
         and record['formal_id'] is None and record['proposed_identifier_not_assigned'] is True, 'proposed-only record')
    need(record['author_thread_id'] == AUTHOR and record['independent_reviewer_thread_id'] == MAIN
         and AUTHOR != MAIN and type(record['proposed_credit']) is int and record['proposed_credit'] == 1
         and type(record['accepted_credit']) is int and record['accepted_credit'] == 0, 'narrow distinct author role')
    need(receipt['reviewer'] == LABEL and receipt['reviewer_thread_id'] == AUTHOR and receipt['decision'] == DECISION
         and type(receipt['accepted_credit']) is int and receipt['accepted_credit'] == 1
         and receipt['actual_author_confirmation'] is True, 'actual author acceptance required')
    need(receipt['reviewed_batch'] == BATCH and receipt['reviewed_batch_sha256'] == sha(br), 'actual batch binding')
    for descriptor in spec['frozen_live_inputs']:bound(descriptor,snap)
    inventory_check(spec)
    baseline = {k:json.loads(bound(v,snap)) for k,v in spec['five_baseline'].items()}
    master = baseline['master-acceptance-ledger.json']; rv = baseline['receipt-validation.json']
    need(master['independently_accepted'] == len(master['accepted']) == len(rv['receipt_inputs']) == 52
         and sha(canonical(master['accepted'])) == spec['old52_master_canonical_sha256']
         and sha(canonical(rv['receipt_inputs'])) == spec['old52_results_canonical_sha256'] and rv['conflicts'] == [], 'complete old52')
    need(not any(x['id'] == IDENTIFIER or x['semantic_key'] == record['semantic_key'] for x in master['accepted']), 'duplicate ID/key abort')
    original = {k:json.loads(bound(v,snap)) for k,v in record['immutable_judgment_bindings'].items()}
    c,m,a,cl = [original[k] for k in ('candidate','Main_review','author_ACK','Main_ACK_closure')]
    need(record['original_candidate_whole'] == c and record['Main_review_whole'] == m
         and record['original_author_ACK_whole'] == a and record['Main_ACK_closure_whole'] == cl
         and a['Main_whole_review_object'] == m, 'four unchanged whole original objects')
    for k in ('observation','application','limits'):need(record[k] == c[k], 'original16/2/7')
    need(record['Main_independent_findings'] == m['Main_independent_findings']
         and record['Main_limits'] == m['Main_limits'] and [len(record[k]) for k in ('observation','application','limits')] == [16,2,7], 'whole Main judgment')
    need(record['actual_author_finding_responses'] == a['Main_finding_acknowledgements']
         and record['actual_author_limit_responses'] == a['Main_limit_acknowledgements']
         and len(record['actual_author_finding_responses']) == 17 and len(record['actual_author_limit_responses']) == 12, 'actual29 ACK')
    context = json.loads(bound(record['current_program512_context'],snap))
    pm = json.loads(bound(context['actual_Main_review'],snap))
    need(pm['formal_program_count'] == context['formal_count'] == 512 and pm['formal_dedup_groups'] == context['groups'] == 240
         and context['gap'] == 488 and context['gate_met'] is False, 'current512 separate from historical contexts')
    for d in context['actual_formal_outputs']:bound(d,snap)
    checks = sources(record,spec,snap,root)
    # These files DO NOT exist in this private proposal. Only future distinct
    # Main actions and a genuine one-shot author attempt may supply them.
    static_raw = snap.read(physical(spec['future_Main_static_review_path'])); static = json.loads(static_raw)
    need(static['reviewer_thread_id'] == MAIN and static['decision'] == 'PASS_EXACT_SUNBIRD_PRIVATE_V1_UNINSTALLED_CODE_ONLY', 'distinct Main new code review')
    proposal = json.loads(bound(static['code_proposal'],snap))
    need(static['code_proposal']['path'] == spec['code_proposal_path'], 'exact fresh plan namespace')
    grant_raw = bound(receipt['execution_grant'],snap); grant = json.loads(grant_raw)
    need(receipt['execution_grant']['path'] == spec['future_Main_author_grant_path'], 'fresh grant namespace')
    need(grant['reviewer_thread_id'] == MAIN and grant['actual_author_thread_id'] == AUTHOR
         and grant['purpose'] == 'EXECUTE_SUNBIRD_PRIVATE_V1_ACTUAL_AUTHOR_ONCE_NO_AGGREGATION'
         and grant['assigned_record_id'] == IDENTIFIER and grant['assigned_batch'] == BATCH, 'Main actually assigns parameters')
    need(grant['code_proposal'] == static['code_proposal'] and grant['Main_static_review'] ==
         dict(path=spec['future_Main_static_review_path'],sha256=sha(static_raw),bytes=len(static_raw)), 'exact proposal/review grant binding')
    need(grant['author_execution_authorized'] is True and grant['one_execution_only'] is True
         and grant['no_retry_after_any_attempt'] is True and grant['external_timeout_seconds'] == 60, 'once/bounded author authority')
    for k in ('aggregation_authorized','old_validator_execution_authorized','old_executor_replay_authorized','upstream_execution_authorized','production_authorized'):
        need(grant[k] is False, 'forbidden scope '+k)
    token = receipt['author_execution_token']
    need(type(token) is str and re.fullmatch('sunbird-private-v1-author-[0-9a-f]{48}',token)
         and grant['author_execution_token'] == token, 'new token, no old replay')
    payloads = proposal['prospective_install_payloads']
    expected_installed = [dict(path=e['target'],sha256=e['private_proposed_postimage']['sha256'],bytes=e['private_proposed_postimage']['bytes']) for e in payloads]
    need(grant['exact_installed_files'] == static['exact_installed_files'] == expected_installed, 'exact reviewed installed allowlist')
    for d in expected_installed:bound(d,snap)
    install_desc = grant['Main_actual_install_review']
    need(install_desc['path'] == spec['future_Main_actual_install_review_path'], 'fresh actual install review')
    install = json.loads(bound(install_desc,snap))
    need(install['reviewer_thread_id'] == MAIN and install['decision'] == 'PASS_ACTUAL_EXACT_SUNBIRD_PRIVATE_V1_INSTALL'
         and install['code_proposal'] == static['code_proposal'] and install['exact_installed_files'] == expected_installed, 'distinct Main actual install closure')
    marker_desc = receipt['actual_attempt_marker'];need(marker_desc['path'] == spec['future_author_marker_path'], 'new marker namespace')
    marker = json.loads(bound(marker_desc,snap))
    need(grant['output_directory'] == str(Path(marker_desc['path']).parent)
         and marker['phase'] == 'SUNBIRD_PRIVATE_V1_ACTUAL_AUTHOR_ONCE' and marker['author_thread_id'] == AUTHOR
         and marker['attempt_consumed'] is True and marker['author_execution_token'] == token
         and marker['grant_sha256'] == sha(grant_raw) and marker['code_proposal'] == static['code_proposal'], 'genuine new attempt marker')
    need(not getattr(snap,'overrides',None) and type(getattr(snap,'bytes',None)) is dict, 'actual snapshot closure')
    for p,saved in snap.bytes.items():need(physical(Path(p).absolute()).read_bytes() == saved, 'input drift before return')
    inventory_check(spec)
    return dict(state='validated_acceptance',id=IDENTIFIER,role='general',reviewer=LABEL,decision=DECISION,
        semantic_key=record['semantic_key'],accepted_credit=1,receipt=RECEIPT,receipt_sha256=sha(actual),batch=BATCH,batch_sha256=sha(br),
        source_checks_recomputed=checks,base_resource_checks_recomputed=[],supporting_ranges_credit=0,
        observed_chain=record['observation'],limitations=record['limits'],complete_chain_support_proof=dict(
            whole_original_candidate=c,whole_Main_review=m,whole_actual_author_ACK=a,whole_Main_ACK_closure=cl,
            current_program512_context=context,actual_execution_grant=receipt['execution_grant'],actual_attempt_marker=marker_desc,
            original_author_confirmation_not_independent_self_review=True,source_range_credit=0,native_gameplay_credit=0,
            global_novelty_credit=0,new_migration_credit=0,runtime_material_payment_credit=0,production_authorized=False))
