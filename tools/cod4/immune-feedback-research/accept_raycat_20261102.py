"""One manual semantic decision with independent review; file hashes earn zero."""
from datetime import datetime, timezone
import hashlib
import json
from ledger import B, O, R, record, verify


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    out = O / 'coordinator-raycat-status-transfer-acceptance-20261102.json'
    assert not out.exists()
    pp = O / 'coordinator-raycat-status-transfer-proposal-20261102.json'
    rp = O / 'independent-raycat-status-transfer-review-20261102.json'
    assert sha(pp.read_bytes()) == 'aa7f89226a82e719aac62fd9638d9d05d9a9b0c2af7c84905b92c7e1e9a4bc75'
    assert sha(rp.read_bytes()) == '99a743bcad9b2084c9020b9ceb9a04529af232c9ec540c7c0d430b22664811e9'
    p, peer = [json.loads(x.read_text()) for x in [pp, rp]]
    f = O / 'reviewed.json'
    before = f.read_bytes()
    assert sha(before) == 'b56df51cacd2e625a174ce52b267741db04f97541e1ac97b8ae6a8755ab38921'
    rows = json.loads(before)
    assert len(rows) == 459
    prefix = (json.dumps(rows[:-1], ensure_ascii=False, indent=2) + '\n').encode()
    assert sha(prefix) == peer['deduplication']['ledger_sha256_at_review'] == p['ledger_sha256_before_proposal']
    assert rows[-1]['id'] == 'alexscaves-native-quorum-ritual-windup-versus-victim-owned-committed-capture-lifecycle'
    assert peer['status'] == 'ACCEPT_ONE_BOUNDED_SEMANTIC_REFERENCE_WITH_EXACT_PERIOD_CLARIFICATION'
    assert peer['maximum_recommended_credit'] == 1 and peer['ledger_credit_written_by_reviewer'] == p['accepted_credit'] == 0
    assert peer['proposal_sha256'] == sha(pp.read_bytes()) and peer['semantic_key'] == p['semantic_key']
    source = B / 'sources/AlexModGuy__AlexsCaves'
    mraw, traw = [(source / x).read_bytes() for x in ['source.json', 'tree.json']]
    assert sha(mraw) == p['source_manifest_sha256'] and sha(traw) == p['source_tree_sha256']
    meta, tree = json.loads(mraw), json.loads(traw)
    assert not tree['truncated'] and meta['commit'] == tree['sha'] == p['commit']
    manifest = {x['path']: x for x in meta['files']}
    blobs = {x['path']: x['sha'] for x in tree['tree'] if x['type'] == 'blob'}
    refs, aux = [], []
    for ref, check in zip(p['actual_source_ranges'], peer['provenance_checks'], strict=True):
        path, rel = R / ref['path'], ref['source_path']
        raw = path.read_bytes()
        lines = raw.decode().splitlines(keepends=True)
        lo, hi = ref['lines']
        assert 1 <= lo <= hi <= len(lines)
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert sha(raw) == ref['file_sha256'] == check['file_sha256']
        assert blob == ref['git_blob_sha1'] == check['git_blob_sha1'] == blobs[rel]
        assert sha(''.join(lines[lo - 1:hi]).encode()) == ref['excerpt_sha256'] == check['excerpt_sha256']
        assert check['path'] == ref['path'] and check['lines'] == ref['lines'] and check['local_file_blob_tree_excerpt_match']
        if rel in manifest:
            assert path == source / rel and sha(raw) == manifest[rel]['sha256'] and blob == manifest[rel]['git_blob_sha1']
            refs.append((rel, lo, hi))
        else:
            assert ref['supplemental_fixed_raw_source_not_original_manifest']
            assert path.is_relative_to(B / '.work/raycat-20261102')
            aux.append({**ref, 'repo': p['repo'], 'commit': p['commit'], 'research_credit': 0,
                        'role': 'supplemental fixed-tree effect/tag supporting whole chain only'})
    assert len(refs) == 15 and len(aux) == 2
    own_keys = {x['key'] for x in p['semantic_comparisons']}
    compared = []
    for c in peer['deduplication']['full_decision_comparisons']:
        old = next(x for x in rows if x['id'] == c['key'])
        assert sha(json.dumps(old, ensure_ascii=False, sort_keys=True).encode()) == c['full_record_sha256']
        assert c['decision'] == 'distinct'
        compared.append({**c, 'coordinator_substantive_decision_fields_read': c['key'] in own_keys,
                         'old_source_chain_reread_claimed': False})
    assert len(own_keys) == 5 and len(compared) == 9
    dp = O / 'semantic-dedup.json'
    dbefore = dp.read_bytes()
    dedup = json.loads(dbefore)
    precise = (
        '精确限定：live-target只指当前integerID解析，不代表最终isAlive/距离/LOS/归属/effect资格复验。'
        'heal/add/remove/add均为请求，接收方先请求获益再独立处理源方减层，不验最终结果。'
        'Irradiated调度level<=0直接false；正level令整数j=200/level，j>1才tick%j==j/2，'
        '否则每ticktrue；j为0不执行modulo0，也不是零周期。'
        'body radiation helper显式LEQUAL，eyes EQUAL；beam getNucleeperLights未显式设置LEQUAL，'
        '各pass不能泛化成共同depth或可见遮挡已验证。')
    observation = p['distinctness_argument'] + '\n' + precise
    limits = [x for x in p['limitations'] if not x.startswith(('Radiation own tick', 'Beam fullbright240'))]
    limits += peer['wording_clarifications']
    limits += ['Beam fullbright240为调用参数，不证明像素/遮挡/声音/网络/性能；sepia仍可达amount-target beam。'
               'PostEffectRegistry及底层状态、纹理PNG未展开。',
               '主协调实际读5旧决策实质字段；独立审阅另对比4旧决策，本次核其收据/哈希，'
               '不冒充主协调重读4条字段或9条旧源链。Underzealot是NPC仪式风起→牺牲者runtime转换尝试，'
               'Raycat是延迟接收方先请求获益→源方现值减层，两个完整机制不同。'
               '17范围/12文件/tag/effect/模型等支持0，整链只1，无生产/美术/native/清单验收。']
    assert f.read_bytes() == before and dp.read_bytes() == dbefore
    row = record(p['semantic_key'], p['repo'], refs, '\n'.join(peer['complete_chain_observations']),
                 observation, p['application_to_boss_immune'], '\n'.join(limits),
                 'native_delayed_cross_entity_status_transfer_attempt_with_independent_recipient_gain_and_state_cue')
    row['auxiliary_refs'] = aux
    row['independent_review'] = {'path': str(rp.relative_to(R)), 'sha256': sha(rp.read_bytes()), 'accepted_credit': 1}
    updated = json.loads(f.read_text())
    assert len(updated) == 460 and updated[-1]['id'] == p['semantic_key']
    updated[-1] = row
    f.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + '\n')
    dedup['groups'].append({'family': 'delayed-id-selected-recipient-first-status-transfer-attempt-20261102',
                            'credited_chains': [p['semantic_key']], 'rationale': observation})
    dp.write_text(json.dumps(dedup, ensure_ascii=False, indent=2) + '\n')
    verify()
    receipt = {'recorded_at': datetime.now(timezone.utc).isoformat(),
        'decision': 'ACCEPT_ONE_INDEPENDENTLY_REVIEWED_DELAYED_STATUS_TRANSFER_ATTEMPT_FAMILY',
        'new_effective_credit': 1, 'prior_total': 459, 'accepted_total': 460, 'remaining': 540,
        'key': p['semantic_key'], 'prior_ledger_sha256': sha(before), 'current_ledger_sha256': sha(f.read_bytes()),
        'review_baseline458_still_exact_prefix': True,
        'proposal': {'path': str(pp.relative_to(R)), 'sha256': sha(pp.read_bytes()), 'immutable_pending_history_retained': True},
        'independent_review': row['independent_review'], 'source_commit': meta['commit'],
        'source_manifest_sha256': sha(mraw), 'source_tree_sha256': sha(traw),
        'actual_source_bindings_revalidated': p['actual_source_ranges'], 'semantic_comparisons': compared,
        'observations': peer['complete_chain_observations'], 'clarifications': precise, 'limitations': limits,
        'formal_design_gate_satisfied': False, 'production_changes': 0, 'art_changes': 0,
        'game_starts': 0, 'checklist_deletions': 0, 'duration_hours_claimed': 0}
    with out.open('x') as stream:
        stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': str(out.relative_to(R)), 'sha256': sha(out.read_bytes()), 'accepted_total': 460, 'remaining': 540}))


if __name__ == '__main__':
    main()
