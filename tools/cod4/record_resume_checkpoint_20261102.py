"""Recover completed immutable deliveries into coordinator state; never clear TODOs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'docs/cod4/audit-20261022'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def exclusive(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    target = AUDIT / 'coordinator-recovered-deliveries-20261102.json'
    assert not target.exists()
    now = datetime.now(timezone.utc).isoformat()
    active_path = AUDIT / 'active-workstreams.json'
    session_path = AUDIT / 'continuation-20261028/session.json'
    core_before = {p: p.read_bytes() for p in [active_path, session_path]}
    active, session = [json.loads(core_before[p]) for p in [active_path, session_path]]
    pending_path = AUDIT / 'pending-tasks.json'
    pending_raw = pending_path.read_bytes()
    pending = json.loads(pending_raw)
    assert pending['count'] == len(pending['tasks']) == 51 and not pending['all_complete']
    receipt_names = [
        'combined-private-integration-20261102.json', 'combined-private-linkage-20261102.json',
        'armor-acquisition-integration-20261102.json',
        'coordinator-armor-itemtask-native-review-20261102.json',
        'immune-feedback-research/coordinator-boundroid-preflight-routing-review-20261102.json',
        'immune-feedback-research/coordinator-gammaroach-status-qualified-counter-review-20261102.json',
    ]
    receipts = [{'path': n, 'sha256': sha((AUDIT / n).read_bytes())} for n in receipt_names]
    combined = read(AUDIT / receipt_names[0])
    assert sha((ROOT / combined['output']).read_bytes()) == combined['output_sha256']
    assert sha((ROOT / combined['base']).read_bytes()) == combined['base_sha256']
    assert combined['base_sha256'] == '0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'
    for path, expected in combined['production_sources'].items():
        assert sha((ROOT / path).read_bytes()) == expected, path
    linkage = read(AUDIT / receipt_names[1])
    assert linkage['candidate_sha256'] == combined['output_sha256']
    assert linkage['member_reference_count'] == 223 and not linkage['errors']
    uv = ROOT / 'docs/art/armor-worn-uv-20261102'
    baseline_path = uv / 'source-baseline.json'
    baseline = read(baseline_path)
    changed = [path for path, expected in baseline.items() if sha((ROOT / path).read_bytes()) != expected]
    assert len(baseline) == 289 and not changed
    index = read(uv / 'evidence-index.json')
    for name, expected in index['files'].items():
        assert sha((uv / name).read_bytes()) == expected, name
    uv_report = {
        'recorded_at': now, 'status': 'OWNER_STATIC_DELIVERY_INTEGRITY_PASS_ART_AND_RUNTIME_PENDING',
        'owner_source_paths_bound': len(baseline), 'owner_evidence_files_bound': len(index['files']),
        'source_baseline_sha256': sha(baseline_path.read_bytes()),
        'owner_evidence_index_sha256': sha((uv / 'evidence-index.json').read_bytes()),
        'source_changes': changed,
        'coordinator_read_full_receipts': ['README.md', 'progress.json', 'manual-review.json',
                                        'findings.json', 'reference-variant-review.json', 'verification.json'],
        'previous_turn_images_actually_viewed': ['approved-icon-worn-match-01.png',
                                                'seams-01.png', 'vanilla-controls-review.png'],
        'image_observations': [
            'Approved-icon comparison shows broad material identity differences for cinnabar and hongmeng and cloth-layout differences for brocade; it is a source preview, not posed wearing.',
            'Seam evidence shows both RGB-only boundaries and transparent-versus-opaque boundaries; values alone do not establish a visual defect.',
            'Native iron/leather controls retain open face and narrow layer2 waist; this does not authorize altering intentional full-face helmets.',
        ],
        'owner_report': read(uv / 'progress.json'),
        'independent_full_uv_algorithm_replay_claimed': False,
        'all_owner_pages_independently_viewed': False,
        'new_reference_credit': 0, 'new_artwork': 0, 'game_acceptance': False,
        'checklist_deletions': 0,
    }
    uv_target = AUDIT / 'coordinator-armor-uv-delivery-review-20261102.json'
    exclusive(uv_target, uv_report)
    receipts.append({'path': uv_target.name, 'sha256': sha(uv_target.read_bytes())})
    progress = read(AUDIT / 'immune-feedback-research/progress.json')
    eco_path = AUDIT / 'ecology-availability-research/master-acceptance-ledger.json'
    ecology = read(eco_path)
    migration = read(AUDIT / 'legacy-migration-acceptance/research-progress.json')
    snapshot = {'recorded_at': now, 'migration_accepted': migration['accepted_unique_implementations'],
                'migration_gap': migration['gap'], 'migration_ledger_sha256': migration['ledger_sha256'],
                'immunity_accepted': progress['reviewed_effective_semantic_dedup'],
                'immunity_gap': progress['remaining'],
                'immunity_ledger_sha256': sha((AUDIT / 'immune-feedback-research/reviewed.json').read_bytes()),
                'ecology_accepted': ecology['independently_accepted'], 'ecology_gap': ecology['shortfall'],
                'ecology_ledger_sha256': sha(eco_path.read_bytes()), 'cod4_remaining': 51,
                'other_art_building_nbt_gates_not_inferred': True}
    assert snapshot['immunity_accepted'] == 458
    assignment = read(AUDIT / 'all-cod-direct-dispatch-20261101.json')
    prompt_hashes = {}
    for row in assignment['files']:
        path = Path(row['path'])
        prompt_hashes[str(path)] = sha(path.read_bytes())
        assert prompt_hashes[str(path)] == row['sha256'], path
    assert not Path('/Users/a15356015027/.codex/automations/dynasty/automation.toml').exists()
    work = ('Recovered interrupted-turn deliveries: combined six-class private SRG candidate and223 static member resolutions; '
            '112 armor recipe/154 task structural integration and native FTB consume/inventory/NBT boundaries; '
            'two genuinely distinct immunity mechanisms already accepted, now458/1000; '
            'owner56UV delivery integrity checked289 source paths/60 evidence files. '
            'No product acceptance or TODO deletion inferred from recovery or hashes.')
    report = {'recorded_at': now, 'work': work, 'receipts': receipts, 'research_snapshot': snapshot,
              'candidate': combined['output'], 'candidate_sha256': combined['output_sha256'],
              'unchanged_resource_entries': combined['unchanged_resource_entries'],
              'all_cod_prompt_sha256_unchanged': prompt_hashes,
              'pending_sha256_unchanged': sha(pending_raw),
              'restart_instruction': 'AGENTS.md', 'restart_instruction_sha256': sha((ROOT / 'AGENTS.md').read_bytes()),
              'no_automation': True, 'background_restart_guaranteed': False,
              'specialists_currently_active': {'texture_turn': '01a19c21-9eec-7852-a719-dfa8ba486cd7',
                                              'model_turn': '01a19c22-c239-7fe1-80da-81897d7629df'},
              'native_acceptance': False, 'production_mutations': 0, 'new_artwork': 0,
              'game_starts': 0, 'checklist_deletions': 0, 'all_complete': False,
              'duration_hours_claimed': 0, 'ten_actual_active_hours_complete': False,
              'tool_sha256': sha(Path(__file__).read_bytes())}
    exclusive(target, report)
    priority = dict(active['latest_armor_texture_priority_20261102'])
    priority.update({'recorded_at': now, 'current_owner_state': 'active_reference_continuation_after56UV_delivery',
                     'latest_turn': '01a19c21-9eec-7852-a719-dfa8ba486cd7',
                     'wait_cursor': '46f27f18-0198-495c-8a89-41ea4b65aa71:1',
                     'owner_progress': 'docs/art/armor-worn-uv-20261102/progress.json',
                     'owner_progress_sha256_at_checkpoint': sha((uv / 'progress.json').read_bytes()),
                     'coordinator_uv_delivery_receipt': uv_target.name,
                     'current_scope': 'Continue independent relevant armor designs after completed56 staticUV review; retain112icons; no new art below applicable gate',
                     'reference_gate': '253 reopenedPNG/75namefamilies/23 conservativegroups are subset evidence, not1000 independent designs',
                     'owner_latest_observation': '5 orphan sleeve-cap source families,5 whole-torso old worn families,3 priority material mismatches; actual wearing/art findings remain open.'})
    segment = {'recorded_at': now, 'work': work, 'receipt': target.name, 'receipt_sha256': sha(target.read_bytes()),
               'new_credit_earned_by_recovery': 0, 'prior_uncheckpointed_immunity_credit_recovered': 2,
               'production_source_changes': 0, 'game_starts': 0, 'checklist_deletions': 0, 'duration_hours_claimed': 0}
    next_scope = ('Continue native migration source/QA contract review and actual local immune/ecology research; '
                  'collect current texture/model deliveries by existing cursor. No blind runtime, sharedJar overwrite or gate reduction.')
    for data in [active, session]:
        data['latest_coordinator_checkpoint'] = report
        data['latest_research_snapshot'] = snapshot
        data['latest_armor_texture_priority_20261102'] = priority
        data['next_coordinator_scope'] = next_scope
        data.setdefault('work_segments', []).append(segment)
        data['restart_continuation_20261102'] = {'source': 'latest human: 中断重启就继续做直到完成并删除所有任务',
                                               'instructions': 'AGENTS.md', 'no_scheduled_tasks': True,
                                               'resume_from_saved_evidence': True, 'all_complete': False}
    session['coordinator_immediate_scope'] = next_scope
    session['actual_active_work_hours_not_yet_complete'] = True
    active['all_complete'] = False
    assert pending_path.read_bytes() == pending_raw
    for path in core_before:
        assert path.read_bytes() == core_before[path], path
    for path, data in [(active_path, active), (session_path, session)]:
        temporary = path.with_name(path.name + '.resume-write.tmp')
        with temporary.open('x') as stream:
            stream.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        os.replace(temporary, path)
    print(json.dumps({'checkpoint': target.name, 'sha256': sha(target.read_bytes()),
                      'uv_source_paths': len(baseline), 'immunity': snapshot['immunity_accepted'],
                      'pending_cod4': 51, 'game_starts': 0, 'deleted_tasks': 0}))


if __name__ == '__main__':
    main()
