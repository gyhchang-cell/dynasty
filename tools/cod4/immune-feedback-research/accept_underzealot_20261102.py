"""Integrate one manually read and independently reviewed mechanism, never file credit."""
from datetime import datetime, timezone
import hashlib
import json

from ledger import B, O, R, record, verify


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(row):
    return sha(json.dumps(row, ensure_ascii=False, sort_keys=True).encode())


def main():
    target = O / 'coordinator-underzealot-ritual-lifecycle-acceptance-20261102.json'
    assert not target.exists()
    proposal_path = O / 'coordinator-underzealot-ritual-lifecycle-proposal-20261102.json'
    review_path = O / 'independent-underzealot-ritual-lifecycle-review-20261102.json'
    assert sha(proposal_path.read_bytes()) == 'e89a2da3caabbc22a7ef13ed00eaee6936650f9c99bd4c7cfb77c899ba03413a'
    assert sha(review_path.read_bytes()) == 'ea3207e4bfff87a11807df34184f215ef5dcdc39570fd6fbbdb7d6fb410d6e9d'
    proposal = json.loads(proposal_path.read_text())
    review = json.loads(review_path.read_text())
    ledger_path = O / 'reviewed.json'
    before = ledger_path.read_bytes()
    assert sha(before) == proposal['ledger_sha256_before_proposal'] == '94a347cfa2ba86a8e19b8e851120f0c2d5553bb371d43fb77f5747ea74b7da6b'
    rows = json.loads(before)
    assert len(rows) == 458
    key = proposal['semantic_key']
    assert review['semantic_key'] == key
    assert review['status'] == 'ACCEPT_ONE_BOUNDED_SEMANTIC_REFERENCE_WITH_EXPLICIT_LIMITS'
    assert review['maximum_recommended_credit'] == 1
    assert review['ledger_credit_written_by_reviewer'] == proposal['accepted_credit'] == 0
    assert review['proposal_sha256'] == sha(proposal_path.read_bytes())
    source = B / 'sources/AlexModGuy__AlexsCaves'
    meta_raw = (source / 'source.json').read_bytes()
    tree_raw = (source / 'tree.json').read_bytes()
    assert sha(meta_raw) == proposal['source_manifest_sha256']
    assert sha(tree_raw) == proposal['source_tree_sha256']
    meta, tree = json.loads(meta_raw), json.loads(tree_raw)
    assert meta['commit'] == tree['sha'] == proposal['commit'] == '4718f4287c65b810aecb211789b45f54d405a94d'
    assert not tree['truncated']
    manifest = {x['path']: x for x in meta['files']}
    blobs = {x['path']: x['sha'] for x in tree['tree'] if x['type'] == 'blob'}
    refs, auxiliary, checked = [], [], []
    for ref, independent in zip(proposal['actual_source_ranges'], review['provenance_checks'], strict=True):
        path, rel = R / ref['path'], ref['source_path']
        raw = path.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        lo, hi = ref['lines']
        lines = raw.decode().splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines)
        assert sha(raw) == ref['file_sha256'] == independent['file_sha256']
        assert blob == blobs[rel] == ref['git_blob_sha1'] == independent['git_blob_sha1']
        assert sha(''.join(lines[lo - 1:hi]).encode()) == ref['excerpt_sha256'] == independent['excerpt_sha256']
        assert independent['path'] == ref['path'] and independent['lines'] == ref['lines']
        assert independent['all_local_checks_passed']
        if rel in manifest:
            assert path == source / rel
            assert sha(raw) == manifest[rel]['sha256'] and blob == manifest[rel]['git_blob_sha1']
            refs.append((rel, lo, hi))
        else:
            assert ref['supplemental_fixed_raw_source_not_original_manifest']
            assert path.is_relative_to(B / '.work/underzealot-20261102')
            auxiliary.append({**ref, 'repo': proposal['repo'], 'commit': proposal['commit'],
                              'research_credit': 0, 'role': 'supplemental fixed-tree sound consumer, support only'})
        checked.append({**ref, 'revalidated_after_independent_review': True})
    assert len(refs) == 21 and len(auxiliary) == 1
    comparison_checks = []
    own_keys = {x['key'] for x in proposal['semantic_comparisons']}
    for comparison in review['deduplication']['comparison_records']:
        prior = next(x for x in rows if x['semantic_dedup_key'] == comparison['key'])
        assert canonical(prior) == comparison['full_record_sha256']
        assert comparison['decision'] == 'distinct'
        comparison_checks.append({**comparison,
            'coordinator_substantive_decision_fields_read': comparison['key'] in own_keys,
            'old_source_chain_reread_claimed': False})
    assert len(own_keys) == 9 and len(comparison_checks) == 14
    dedup_path = O / 'semantic-dedup.json'
    dedup_before = dedup_path.read_bytes()
    dedup = json.loads(dedup_before)
    assert not any(x['semantic_dedup_key'] == key for x in rows)
    chain = '\n'.join(proposal['full_chain_observation'])
    correction = (
        '独立复核后的限定：multi-actor仅指NPC pack而非真人双人；quorum只遍历链中PRAYING标志，'
        '不在该计数方法检查存活/实际站位，离开环位分支仅清worship而未清PRAYING，可能有陈旧标志。'
        '因此不是持续有效的几何/活体quorum。dismount/unseat指脱离乘骑，不能翻译成chunk unload。'
        'committed只指已武装未来runtime尝试，不是不可逆、持久、成功或恰一次转化。'
        'Gloomoth脱骑后仍倒计时，Vesper脱骑暂停但不清标志，之后任意乘骑可恢复。')
    observation = proposal['distinctness_argument'] + '\n' + correction
    limits = '\n'.join(proposal['limitations'] + review['required_wording_limits'])
    limits += ('\n主协调实际读取原9旧决策的完整实质字段；独立审阅另对比5旧决策，'
               '主协调只核其当前收据结论及哈希，不冒充亲自重读这5条字段或14条旧源链。'
               '22范围/14文件/两个牺牲目标/状态/声音/模型均支持0，只整链1。'
               '本接受未运行游戏/Java/编译、未改生产/专业资产/清单，未证明native或10小时。')
    assert ledger_path.read_bytes() == before and dedup_path.read_bytes() == dedup_before
    row = record(key, proposal['repo'], refs, chain, observation,
                 proposal['application_to_boss_immune'], limits,
                 'native_npc_control_admission_windup_commit_interrupt_and_feedback_lifecycle')
    row['auxiliary_refs'] = auxiliary
    row['independent_review'] = {'path': str(review_path.relative_to(R)),
                                  'sha256': sha(review_path.read_bytes()), 'accepted_credit': 1}
    updated = json.loads(ledger_path.read_text())
    assert updated[-1]['id'] == key and len(updated) == 459
    updated[-1] = row
    ledger_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + '\n')
    dedup['groups'].append({'family': 'npc-prayer-flag-quorum-to-victim-owned-runtime-attempt-20261102',
        'credited_chains': [key], 'rationale': observation})
    dedup_path.write_text(json.dumps(dedup, ensure_ascii=False, indent=2) + '\n')
    verify()
    receipt = {'recorded_at': datetime.now(timezone.utc).isoformat(),
        'decision': 'ACCEPT_ONE_INDEPENDENTLY_REVIEWED_NPC_RITUAL_CONTROL_AND_FEEDBACK_LIFECYCLE',
        'new_effective_credit': 1, 'prior_total': 458, 'accepted_total': 459, 'remaining': 541,
        'key': key, 'prior_ledger_sha256': sha(before), 'current_ledger_sha256': sha(ledger_path.read_bytes()),
        'proposal': {'path': str(proposal_path.relative_to(R)), 'sha256': sha(proposal_path.read_bytes()), 'immutable_pending_history_retained': True},
        'independent_review': row['independent_review'], 'source_commit': meta['commit'],
        'source_manifest_sha256': sha(meta_raw), 'source_tree_sha256': sha(tree_raw),
        'actual_source_bindings': checked, 'semantic_comparisons': comparison_checks,
        'observation': observation, 'limitations': limits,
        'formal_design_gate_satisfied': False, 'production_changes': 0, 'art_changes': 0,
        'game_starts': 0, 'checklist_deletions': 0, 'duration_hours_claimed': 0}
    with target.open('x') as stream:
        stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': str(target.relative_to(R)), 'sha256': sha(target.read_bytes()),
                      'accepted_total': 459, 'remaining': 541}))


if __name__ == '__main__':
    main()
