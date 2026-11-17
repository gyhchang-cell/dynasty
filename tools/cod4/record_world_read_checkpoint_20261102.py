"""Append actual offline/preflight results; never infer game acceptance from readiness."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os

R = Path(__file__).resolve().parents[2]
A = R / 'docs/cod4/audit-20261022'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())


def main():
    out = A / 'coordinator-world-read-preflight-checkpoint-20261102.json'
    assert not out.exists()
    core = [A / 'active-workstreams.json', A / 'continuation-20261028/session.json']
    before = {p: p.read_bytes() for p in core}
    active, session = [json.loads(before[p]) for p in core]
    pending = A / 'pending-tasks.json'
    pending_sha = sha(pending)
    assert read(pending)['count'] == 51
    names = [
        'todo-evidence-review-20261101/legacy-native-artifact-input-independent-review-20261102.json',
        'legacy-native-acceptance/offline-compile-20261102T130116-978713Z.json',
        'legacy-native-acceptance/reobf-20261102T130148-997818Z.json',
        'legacy-native-acceptance/linkage-20261102T130219-030052Z.json',
        'legacy-native-acceptance/independent-world-read-readiness-20261102.json',
        'legacy-native-acceptance/independent-world-read-readiness02-20261102.json',
        'legacy-native-acceptance/preflight-nonutf8-failure-20261102.json',
        'legacy-native-acceptance/preflight-existing-java-block-20261102.json',
        'legacy-native-acceptance/process-byte-checks-20261102T131631-278114Z.json',
        'legacy-native-acceptance/analysis-checks-20261102T132716-002535Z.json',
        'legacy-native-acceptance/independent-analysis-source-review-20261102.json',
        'legacy-native-acceptance/independent-analysis-delta-review02-20261102.json',
    ]
    receipts = [{'path': n, 'sha256': sha(A / n)} for n in names]
    pack, compiled, reobf, linkage, ready1, ready2, fail1, block, bytechecks, analysis, review, delta = [read(A / n) for n in names]
    assert sha(R / reobf['output']) == reobf['output_sha256'] == linkage['qa_sha256']
    assert reobf['output_sha256'] == '0ccb1128245384ce939b5702cb948ee9215b26ddfa4fd8a90df56eea70af27ac'
    assert linkage['member_reference_count'] == 317 and not linkage['errors']
    for n, expected in reobf['sources'].items():
        assert sha(R / n) == expected
    for n, expected in analysis['sources'].items():
        assert sha(R / n) == expected
    assert analysis['status'] == 'PASS' and 'PASS 24 ' in analysis['output']
    assert not delta['new_blocking_findings'] and delta['analysis_receipt_sha256'] == sha(A / names[9])
    for n, row in delta['reviewed_sources'].items():
        assert sha(R / n) == row['sha256']
    assert block['status'] == 'PREFLIGHT_BLOCKED_EXISTING_GAME_OR_UNKNOWN_JAVA_NO_LAUNCH'
    assert block['game_starts'] == block['signals_sent'] == 0 and not block['marker_consumed']
    run = R / 'build/cod4-legacy-native-20261102/read01'
    assert not (run / 'execution-started.json').exists()
    assert not list((run / 'evidence').iterdir())
    candidate = R / 'build/cod4-combined-private-20261102/candidate01/dynasty-1.4.0.jar'
    assert sha(candidate) == 'e5a78244082214ab5fd76eb35bbb42151e3ec7bd8bc13afee3bc58ea4fe3a669'
    assert sha(R / 'modpack/mods/dynasty-1.4.0.jar') == '0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'
    old = read(A / 'old-world-acceptance/post-fix-fresh-copy-input.json')
    for root in [Path(old['source']), Path(old['copy']), run / 'host/saves/legacy-copy']:
        assert {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file()} == old['source_files_sha256']
    assignment = read(A / 'all-cod-direct-dispatch-20261101.json')
    for row in assignment['files']:
        assert sha(Path(row['path'])) == row['sha256']
    assert not Path('/Users/a15356015027/.codex/automations/dynasty/automation.toml').exists()
    art = [R / 'docs/art/armor-tailoring-reference-20261102/progress.json',
           R / 'docs/art/armor-tailoring-reference-20261102/verification.json',
           R / 'docs/art/armor-tailoring-reference-20261102/application-methods.json',
           R / 'docs/art/bestiary-v43/body-joints-20261102/receipt.json']
    texture = read(art[0])
    assert not texture['reference_gate_met']
    now = datetime.now(timezone.utc).isoformat()
    work = ('Built observer for existing private old-world copy; compiled and SRG-linked317 members with unchanged two-class core. '
            'Fixed independent-report semantic binding and lossless process byte decoding; both received bounded independent review. '
            'Actual first preflight stopped at non-UTF8 decoding, second stopped on five existing game/QA/unknown-Java blockers, '
            'both before execution marker or child. No further automatic retry. '
            'Added headless descriptive historical NBT comparator;24 synthetic assertions pass, exact-byte/manual/full-stack fixes independently closed. '
            'Read specialist tailoring methods and actual Underzealot carrier/ritual/render source chain; no new semantic credit or art production inferred.')
    report = dict(recorded_at=now, work=work, receipts=receipts,
                  private_root=str(run.relative_to(R)), private_qa=reobf['output'], private_qa_sha256=reobf['output_sha256'],
                  candidate_sha256=sha(candidate), static_member_references=317,
                  old_core34_checks_reused_by_exact_bytes=True, new_world_reader_not_covered_by_core34=True,
                  analysis_checks=24, analysis_checks_synthetic_only=True,
                  analysis_delta_independent_review='bounded_delta_complete_no_new_blocking_finding',
                  independent_ready02_snapshot=ready2['snapshot_sha256'], readiness_is_not_runtime_acceptance=True,
                  latest_preflight_status=block['status'], blockers_observed=len(block['diagnostic_current_blockers']),
                  execution_marker_consumed=False, original_and_prepared_and_private_world_files_unchanged=32,
                  prior_nonutf8_preflight_failure_retained=True, new_process_or_display_poll=False,
                  research_snapshot=active['latest_research_snapshot'], new_research_credit=0,
                  texture_observation={k: texture[k] for k in ['combined_name_families','combined_conservative_learning_groups',
                                       'minimum_open_gap_under_current_one_per_group_policy','validated_independent_design_total','reference_gate_met']},
                  specialist_receipts=[{'path': str(p.relative_to(R)), 'sha256': sha(p)} for p in art],
                  specialist_quota_status={'texture': 'actual429; no restoration loop', 'model': 'actual98percent_lock_and429; no restoration loop',
                                           'building_and_bug': 'prior quota restrictions retained'},
                  specialist_semantic_and_native_acceptance_not_inferred=True,
                  new_game_starts=0, signals_sent=0, existing_process_attached=False, production_mutations=0,
                  native_acceptance=False, checklist_deletions=0, cod4_remaining=51, all_complete=False,
                  no_automation=True, duration_hours_claimed=0, ten_actual_active_hours_complete=False,
                  tool_sha256=sha(Path(__file__)))
    with out.open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2); f.write('\n')
    next_scope = ('Continue actual offline immunity source-chain reading; comparator delta independently closed. '
                  'Existing game/QA/unknown Java blocked native read01 before marker; no blind retry, polling loop or existing-process control. '
                  'Native old-world load/save-reopen, Clone/C2S/End and actual duel acceptance remain. '
                  'Keep title specialties, protect approved art/sharedJar and exact pending scope; no scheduled task.')
    for data in [active, session]:
        data['latest_coordinator_checkpoint'] = report
        data['latest_migration_native_qa_20261102'] = dict(receipt=out.name, sha256=sha(out),
                source_and_observer_independent_review_complete=True, new_world_reader_independent_review_complete=True,
                native_acceptance=False, latest_preflight_status=block['status'], execution_marker_consumed=False)
        data['next_coordinator_scope'] = next_scope
        data.setdefault('work_segments', []).append(dict(recorded_at=now, work=work, receipt=out.name,
                receipt_sha256=sha(out), new_research_credit=0, game_starts=0, checklist_deletions=0, duration_hours_claimed=0))
    active['latest_runtime_preflight'] = dict(receipt=names[7], sha256=sha(A / names[7]),
                status=block['status'], game_starts=0, execution_marker_consumed=False, no_automatic_retry=True)
    session['coordinator_immediate_scope'] = next_scope
    assert sha(pending) == pending_sha
    for p in core:
        assert p.read_bytes() == before[p]
    for p, data in zip(core, [active, session]):
        temp = p.with_name(p.name + '.world-read-checkpoint.tmp')
        with temp.open('x') as f:
            json.dump(data, f, ensure_ascii=False, indent=2); f.write('\n')
        os.replace(temp, p)
    print(json.dumps(dict(checkpoint=out.name, sha256=sha(out), game_starts=0, cod4_remaining=51)))


if __name__ == '__main__':
    main()
