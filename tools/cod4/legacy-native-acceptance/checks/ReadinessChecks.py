"""Regression for stale/unrelated independent report acceptance. No Java or game."""
from pathlib import Path
import copy
import datetime
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
B = Path(__file__).resolve().parents[1]
R = B.parents[2]
spec = importlib.util.spec_from_file_location('_legacy_readiness_checks', B / 'world_read_plan.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
ready = dict(status='READY_FOR_ONE_BOUNDED_LEGACY_WORLD_READ', one_attempt_only=True,
             private_root=str(tool.RUN), reviewer_thread=tool.REVIEWER_THREAD, snapshot_sha256='a' * 64)
report = dict(ready, status='INDEPENDENT_READY_FOR_ONE_BOUNDED_LEGACY_WORLD_READ')
tool.check_review_contract(ready, report)
rows = [{'case': 'matching_exact_one_read_contract', 'accepted': True}]
cases = [('old_static_review', 'report', 'status', 'INDEPENDENT_SOURCE_REVIEW_COMPLETE'),
         ('different_snapshot', 'report', 'snapshot_sha256', 'b' * 64),
         ('different_attempt', 'report', 'private_root', str(tool.BUILD / 'read02')),
         ('ready_different_attempt', 'ready', 'private_root', str(tool.BUILD / 'read02')),
         ('wrong_reviewer', 'report', 'reviewer_thread', 'another-thread'),
         ('ready_wrong_reviewer', 'ready', 'reviewer_thread', 'another-thread'),
         ('repeatable_report', 'report', 'one_attempt_only', False),
         ('malformed_digest', 'report', 'snapshot_sha256', 'not-a-sha')]
for label, target, key, value in cases:
    a, b = copy.deepcopy(ready), copy.deepcopy(report)
    (a if target == 'ready' else b)[key] = value
    try:
        tool.check_review_contract(a, b)
    except (AssertionError, KeyError):
        rows.append({'case': label, 'rejected': True})
    else:
        raise AssertionError('Unsafe readiness accepted: ' + label)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = dict(status='PASS_STALE_OR_UNRELATED_READINESS_REJECTED', cases=rows, checks=len(rows),
              sources={str(p.relative_to(R)): sha(p) for p in [Path(__file__), B / 'world_read_plan.py']},
              scope='Pure readiness-contract fixtures only; disk/document race binding independently source-reviewed',
              game_starts=0, process_or_display_queries=0, runtime_approved=False, checklist_deletions=0)
target = R / 'docs/cod4/audit-20261022/legacy-native-acceptance' / ('readiness-checks-' + stamp + '.json')
with target.open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(json.dumps({'status': result['status'], 'checks': len(rows), 'receipt': str(target.relative_to(R)), 'game_starts': 0}))
