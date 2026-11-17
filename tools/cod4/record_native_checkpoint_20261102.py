"""Record actual migration source/QA work and preserve all unaccepted TODO scope."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

R = Path(__file__).resolve().parents[2]
A = R / 'docs/cod4/audit-20261022'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    out = A / 'coordinator-native-qa-offline-checkpoint-20261102.json'
    assert not out.exists()
    core = [A / 'active-workstreams.json', A / 'continuation-20261028/session.json']
    before = {p: p.read_bytes() for p in core}
    active, session = [json.loads(before[p]) for p in core]
    pending = A / 'pending-tasks.json'
    pending_sha = sha(pending)
    assert read(pending)['count'] == 51
    names = [
        'todo-evidence-review-20261101/legacy-migration-current-source-independent-review-20261102.json',
        'todo-evidence-review-20261101/typed-root-review-count-clarification-20261102.json',
        'todo-evidence-review-20261101/legacy-native-qa-independent-review-20261102.json',
        'legacy-native-acceptance/offline-compile-20261102T122610-913659Z.json',
        'legacy-native-acceptance/comparison-checks-20261102T122757-214883Z.json',
        'legacy-native-acceptance/native-input-20261102T122852-069354Z.json',
        'legacy-native-acceptance/reobf-20261102T123247-236656Z.json',
        'legacy-native-acceptance/linkage-20261102T123414-477715Z.json',
    ]
    receipts = [{'path': n, 'sha256': sha(A / n)} for n in names]
    source_review, clarification, qa_review, compiled, checks, native, reobf, linkage = [read(A / n) for n in names]
    assert not source_review['blocking_findings'] and not qa_review['blocking_findings']
    assert clarification['actual_native_archive_bound_entries'] == 7
    for row in source_review['source_evidence']:
        assert sha(R / row['path']) == row['sha256']
        lines = (R / row['path']).read_text().splitlines()
        for span in row['actual_read_ranges']:
            excerpt = '\n'.join(lines[span['start'] - 1:span['end']])
            assert hashlib.sha256(excerpt.encode()).hexdigest() == span['sha256']
    for row in qa_review['source_evidence']:
        assert sha(R / row['path']) == row['sha256']
    for n, expected in compiled['sources'].items():
        assert sha(R / n) == expected
    assert checks['status'] == compiled['status'] == reobf['status'] == 'PASS'
    assert checks['compile_receipt_sha256'] == sha(A / names[3])
    assert len(checks['runtime_library_files']) == 786
    assert sha(R / reobf['output']) == reobf['output_sha256'] == linkage['qa_sha256']
    assert linkage['member_reference_count'] == 196 and not linkage['errors']
    assert native['status'] == 'PASS_READ_ONLY_NATIVE_NBT_INPUT' and native['original_files_verified'] == 32
    old = read(A / 'old-world-acceptance/post-fix-fresh-copy-input.json')
    for root in [Path(old['source']), Path(old['copy'])]:
        actual = {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file()}
        assert actual == old['source_files_sha256']
    raw = native['native_input']
    assert len(raw['disk_player']['forge_data']) == 4
    assert raw['both_inventory_tags_equal'] and raw['both_forge_data_equal']
    assert raw['disk_player']['inventory'][4]['full_stack_snbt'] == '{Count:1b,Slot:4b,id:"dynasty:quest_ledger"}'
    snapshot = dict(active['latest_research_snapshot'])
    assert snapshot['migration_accepted'] == 1000 and snapshot['immunity_accepted'] == 458 and snapshot['ecology_accepted'] == 14
    assignment = read(A / 'all-cod-direct-dispatch-20261101.json')
    for row in assignment['files']:
        assert sha(Path(row['path'])) == row['sha256']
    assert sha(R / 'modpack/mods/dynasty-1.4.0.jar') == '0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'
    assert not Path('/Users/a15356015027/.codex/automations/dynasty/automation.toml').exists()
    now = datetime.now(timezone.utc).isoformat()
    work = ('Accepted current independent bounded migration-source review and QA-observer review; corrected both QA P2 findings. '
            'Built fresh QA-only SRG jar and resolved196 member references in the current candidate/SRG context. '
            '34 QA-only comparison checks pass with786 actual library bytes and Java binaries bound. '
            'Native NBT reader inspected original prepared copy without world/player construction: four actual typed root facts, '
            'quest_ledger Slot4/Count1b, historical healing registry entry but no inventory stack; both original and prepared copy32files unchanged. '
            'No native world/Clone/C2S/save-reopen acceptance or TODO deletion.')
    report = dict(recorded_at=now, work=work, receipts=receipts, research_snapshot=snapshot,
                  candidate=qa_review['candidate']['path'], candidate_sha256=qa_review['candidate']['actual_sha256'],
                  private_qa=reobf['output'], private_qa_sha256=reobf['output_sha256'],
                  independent_production_source_review_complete=True, independent_qa_observer_source_review_complete=True,
                  new_packaging_capture_linkage_tools_independent_review='requested_in_existing_general_chat',
                  actual_old_progress_fields=raw['disk_player']['forge_data'], original_world_files_unchanged=32,
                  original_inventory_healing_coverage=False, original_inventory_custom_tag_or_forgecaps_for_quest_ledger=False,
                  modeled107_field_fixture_not_historical_coverage=True, renamer_warning_count=len(reobf['warnings']),
                  historical_failures_retained=['precompile manifest schema guard before Java', 'authlib10 comparison failure',
                                                'prior reobf status guard before Java', 'empty ZIP directory postcondition guard'],
                  no_automation=True, runtime_approved=False, new_ready_or_execution_marker=False,
                  source_changes='new private QA tools only', production_mutations=0, game_starts=0,
                  native_acceptance=False, checklist_deletions=0, cod4_remaining=51, all_complete=False,
                  duration_hours_claimed=0, ten_actual_active_hours_complete=False, tool_sha256=sha(Path(__file__)))
    with out.open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2); f.write('\n')
    segment = dict(recorded_at=now, work=work, receipt=out.name, receipt_sha256=sha(out),
                   research_credit_added=0, game_starts=0, checklist_deletions=0, duration_hours_claimed=0)
    next_scope = ('Collect independent new packaging-tool review, then bind current private old-world/TCP inputs and genuine native C2S/End/remap readback. '
                  'No old marker consumption or blind launch; continue original specialists by title and substantive local research.')
    for data in [active, session]:
        data['latest_coordinator_checkpoint'] = report
        data['next_coordinator_scope'] = next_scope
        data['latest_migration_native_qa_20261102'] = {'receipt': out.name, 'sha256': sha(out),
                                                     'source_and_observer_independent_review_complete': True,
                                                     'native_acceptance': False, 'runtime_approved': False}
        data.setdefault('work_segments', []).append(segment)
    for stream in active['workstreams']:
        if stream['owner'] == 'Kepler':
            stream['historical_status_before_current_checkpoint'] = stream['status']
            stream['status'] = '1000/1000; current root copier/item alias source and QA observer independently reviewed, private combined candidate and QA-only SRG ready for further input/preflight work; actual native acceptance pending'
        elif stream['owner'] == 'Russell':
            stream['historical_status_before_current_checkpoint'] = stream['status']
            stream['status'] = '458/1000 actual accepted; gap542; no immune production repair before gate'
        elif stream['owner'] == '做建模的':
            stream['scope'] = 'Bodies, bones, animation and attachment interfaces only; own newer human priority first. Held/accessory objects belong to texture chat.'
        elif stream['owner'] == '做贴图的':
            stream['scope'] = 'Armor priority, texture/UV and held/accessory objects under latest own human requirements; no body/AI/building misc work.'
            stream['status'] = 'Active original-chat armor design reference continuation after56 worn-UV static review; historical196 pool is not a current applicable gate; preserve approved112icons'
    session['coordinator_immediate_scope'] = next_scope
    assert sha(pending) == pending_sha
    for p in core:
        assert p.read_bytes() == before[p]
    for p, data in zip(core, [active, session]):
        temp = p.with_name(p.name + '.native-checkpoint.tmp')
        with temp.open('x') as f:
            json.dump(data, f, ensure_ascii=False, indent=2); f.write('\n')
        os.replace(temp, p)
    print(json.dumps({'checkpoint': out.name, 'sha256': sha(out), 'qa_member_refs': 196,
                      'native_acceptance': False, 'cod4_remaining': 51, 'game_starts': 0}))


if __name__ == '__main__':
    main()
