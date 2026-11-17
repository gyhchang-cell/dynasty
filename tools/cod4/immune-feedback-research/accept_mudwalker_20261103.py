"""One independent bounded terrain-policy decision; no native execution."""
from datetime import datetime, timezone
import hashlib
import json
from accept_weedwood_20261103 import sha, encode, git
from ledger import O, R, verify


def main():
    proposal = R / 'docs/cod4/audit-20261022/program-feedback-review-20261101/immune-reference-batch-023.json'
    review_path = O / 'coordinator-mudwalker-footing-review-20261103.json'
    acceptance_path = O / 'coordinator-mudwalker-footing-acceptance-20261103.json'
    assert not review_path.exists() and not acceptance_path.exists()
    raw = proposal.read_bytes()
    assert sha(raw) == 'ad1d4b3e5ef92d624e7fbd8500fa7e0f156f482f08a8c45929e31ea6a4e87674'
    p = json.loads(raw)
    assert p['status'] == 'pending_independent_semantic_review'
    assert type(p['research_credit']) is int and p['research_credit'] == 0
    assert type(p['maximum_proposed_credit']) is int and p['maximum_proposed_credit'] == 1
    lp, dp = O / 'reviewed.json', O / 'semantic-dedup.json'
    before, dbefore = lp.read_bytes(), dp.read_bytes()
    assert sha(before) == '0c952a23e8975927f7bfa7d715be876eb548e0f01f003288c9bd969acca3d905'
    rows, dedup = json.loads(before), json.loads(dbefore)
    assert len(rows) == 463
    key = p['semantic_family']
    assert key not in {r['semantic_dedup_key'] for r in rows}
    prov = p['provenance']
    mr = (R / prov['manifest_path']).read_bytes()
    assert sha(mr) == prov['manifest_sha256']
    m = next(x for x in json.loads(mr) if x['repo'] == p['repo'])
    repo, commit = R / prov['bare_git_path'], p['commit']
    assert git(repo, 'rev-parse', commit + '^{commit}').decode().strip() == commit == m['commit']
    assert git(repo, 'rev-parse', commit + '^{tree}').decode().strip() == m['git_tree'] == prov['git_tree']
    mf = {x['path']: x for x in m['files']}
    previous = json.loads((R / 'docs/cod4/audit-20261022/program-feedback-review-20261101/immune-reference-batch-022.json').read_text())
    checks, refs = [], []
    for i, r in enumerate(p['source_refs']):
        data = (R / r['path']).read_bytes()
        rel, (lo, hi) = r['upstream_path'], r['lines']
        entry = mf[rel]
        assert R / r['path'] == R / entry['source']
        assert sha(data) == r['file_sha256'] == entry['sourceSha256']
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == r['git_blob_sha1'] == entry['source_blob']
        assert git(repo, 'show', commit + ':' + rel) == data
        lines = data.splitlines(keepends=True)
        assert 1 <= lo <= hi <= len(lines)
        reuse = i in [23,24,25,26,27,28,29,30,32,33]
        if reuse:
            assert any(x['path'] == r['path'] and x['file_sha256'] == r['file_sha256'] and x['lines'][0] <= lo <= hi <= x['lines'][1] for x in previous['source_refs'])
        checks.append({**r, 'excerpt_sha256': sha(b''.join(lines[lo-1:hi])),
                       'actual_new_range_read': not reuse, 'reused_same_turn_022_actual_read': reuse,
                       'source_identity_verified': True, 'support_credit': 0})
        refs.append({'path':r['path'], 'source_path':rel, 'lines':[lo,hi], 'file_sha256':sha(data),
                     'url':f'https://github.com/{p["repo"]}/blob/{commit}/{rel}#L{lo}-L{hi}'})
    assert len(checks) == 34 and sum(x['actual_new_range_read'] for x in checks) == 24
    by = {r['id']:r for r in rows}
    comparisons = []
    for c in p['dedup_snapshot']['comparisons']:
        row = by[c['accepted_id']]
        assert all(row.get(f) == c['full_semantic_decision_read'].get(f) for f in ['id','category','semantic_dedup_key','full_chain_observation','concrete_observation','limitations'])
        comparisons.append({'id':row['id'], 'full_record_sha256':sha(json.dumps(row,ensure_ascii=False,sort_keys=True).encode()),
                            'substantive_decision_fields_actually_read':True, 'old_source_chain_reread':False,
                            'distinction':c['distinction']})
    assert len(comparisons) == 5
    clarifications = [
        'Accepted unit is mod-owned environmental footing/contact qualification and its capability producer/lifetime, not a certified successful drink/consumption/payment chain. Actual ItemFood1.12 finish-to-onFoodEaten native implementation was not found in this bounded local cache. A similarly named MineColonies ItemFood is not substituted. Mod override and complete own parent are read; native callback dispatch remains an explicit external boundary.',
        'For living actors mud checks heavyweight before later species, boots, active capability and creative-flight exemptions. Ordinary EntityItem is not living, so does not satisfy that first predicate and reaches its later item exemption. Sludge has a different source policy and never checks heavyweight here.',
        'Mud protected floor contributes full1.0 collision only when intersecting; ineligible client fallback may contribute0.875 while server contributes none in this override. No native movement solver or desynchronization reproduction; getCollisionBoundingBox separately returns0.875.',
        'Protected contact skips this call new drag/web/onGround/IN_WALL requests, without reversing existing web/motion or rejecting every later damage/control source. Sludge skip only affects its on-ground web call, not all terrain.',
        'Nonrenewal is brew caller policy, not universal setter policy: public setActive(duration>0) replaces raw absolute deadline. Existing active lease prevents this brew renewal even when heavyweight currently vetoes mud protection. Deadline expiry derives state but does not clear raw field or dirty it.',
        'Elixir qualification uses ResourceLocation object identity==, not value equals. Same-potion registry assignment is source context, not a guarantee all runtime references preserve identity. MudWalk does not cure the heavyweight effect.',
        'Raw long deadline copied through nondeath capability Clone has no world-clock rebase. Long subtraction castsint before clamp; server/client clocks, extreme values and capability injection order untested. Dirty-only tracker ready after21 ordinary updates from0 is not exact20tick periodic delivery or per-contact ACK.',
        'Coordinator read24 new cited ranges including complete terrain/capability/brew/enum/boots/shared capability-handler classes. Ten registration/transport ranges reuse identical same-turn022 actual readings. Five full prior substantive decision fields compared; old source chains not reread. Shared timer/serialization/metadata/boots/support variants confer0 extra.'
    ]
    observations = [x['stage']+': '+x['observation'] for x in p['full_chain']] + clarifications
    limits = p['critical_boundaries'] + clarifications
    now = datetime.now(timezone.utc).isoformat()
    review = {'recorded_utc':now,'reviewer_thread_id':'01a16364-cac0-7ca2-a042-a5312781ca34',
              'proposal_author_thread_id':'01a16392-312e-72f2-a4dd-56e184f9cb02',
              'proposal_path':str(proposal.relative_to(R)),'proposal_sha256':sha(raw),
              'decision':'ACCEPT_ONE_BOUNDED_MOD_OWNED_ENVIRONMENTAL_FOOTING_CONTACT_POLICY',
              'recommended_credit':1,'review_alone_ledger_credit':0,'semantic_key':key,
              'actual_source_checks':checks,'semantic_comparisons':comparisons,'complete_chain_observations':observations,
              'limitations':limits,'production_changes':0,'game_starts':0,'checklist_deletions':0,'active_hours_claimed':0}
    rr=encode(review)
    row={'id':key,'status':'reviewed_effective','repo':p['repo'],'commit':commit,
         'category':'native_environmental_footing_and_contact_policy_with_nonrenewing_brew_lease_and_source_specific_veto_precedence',
         'semantic_dedup_key':key,'count_unit':'one complete mod-owned policy lifecycle; shared native callback and timer/transport/variant support0',
         'source_refs':refs,'full_chain_observation':'\n'.join(observations),
         'concrete_observation':'One source-side environmental control policy: nonrenewing brew-granted lease changes mud floor and suppresses new contact penalties, but heavyweight veto precedes all mud exemptions and does not apply to sludge. Distinct from unconditional cobweb refusal, collision-derived phasing, struggle attenuation or latent exposure masking. No successful drink/payment or whole-engine movement proof.',
         'application_to_boss_immune':p['application'],'limitations':'\n'.join(limits),'research_credit':1,'reviewed_utc':now,
         'independent_review':{'path':str(review_path.relative_to(R)),'sha256':sha(rr),'accepted_credit':1}}
    rows.append(row)
    dedup['groups'].append({'family':'source-specific-environmental-footing-contact-lease-20261103','credited_chains':[key],'rationale':row['concrete_observation']})
    assert lp.read_bytes()==before and dp.read_bytes()==dbefore
    with review_path.open('xb') as f:f.write(rr)
    lp.write_bytes(encode(rows));dp.write_bytes(encode(dedup));verify()
    assert json.loads(lp.read_bytes())[:-1]==json.loads(before)
    result={'recorded_utc':now,'decision':review['decision'],'new_effective_credit':1,'prior_total':463,'accepted_total':464,
            'remaining':536,'prior_ledger_sha256':sha(before),'current_ledger_sha256':sha(lp.read_bytes()),
            'old463_records_identical':True,'review':row['independent_review'],'proposal_sha256':sha(raw),
            'native_itemfood_finish_dispatch_certified':False,'formal_design_gate_satisfied':False,
            'production_changes':0,'game_starts':0,'checklist_deletions':0,'active_hours_claimed':0}
    with acceptance_path.open('xb') as f:f.write(encode(result))
    print(json.dumps({'acceptance':str(acceptance_path.relative_to(R)),'sha256':sha(acceptance_path.read_bytes()),'accepted_total':464,'remaining':536,'ledger_sha256':sha(lp.read_bytes())}))


if __name__=='__main__':
    main()
