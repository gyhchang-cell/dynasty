"""Process-list decoding regression; synthetic bytes only, no ps/display/Java."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys
sys.dont_write_bytecode = True
B = Path(__file__).resolve().parents[1]
R = B.parents[2]
spec = importlib.util.spec_from_file_location('_legacy_process_bytes_checks', B / 'world_read_plan.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
cases = [
    ('non_utf8_non_java', b'21 /Applications/Other\xff Other\xff\n', []),
    ('java_with_non_utf8_argument', b'22 /Library/jdk/bin/java /Library/jdk/bin/java net.minecraft.Main --name \xff\n', ['22']),
    ('unknown_java_is_blocked', b'23 /Library/jdk/bin/java /Library/jdk/bin/java Example\xfe\n', ['23']),
    ('gradle_only_allowed', b'24 /Library/jdk/bin/java /Library/jdk/bin/java org.gradle.launcher.daemon.bootstrap.GradleDaemon \xff\n', []),
    ('gradle_plus_game_blocked', b'25 /Library/jdk/bin/java /Library/jdk/bin/java org.gradle.launcher.daemon.bootstrap.GradleDaemon forgeclient \xff\n', ['25']),
]
rows = []
for label, payload, expected in cases:
    assert os.fsencode(os.fsdecode(payload)) == payload, label
    assert tool.process_blockers(payload) == expected, label
    rows.append({'case': label, 'blocked_pids': expected, 'lossless_roundtrip': True})
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = dict(status='PASS_LOSSLESS_NON_UTF8_PROCESS_FIXTURES', cases=rows, checks=len(rows),
              sources={str(p.relative_to(R)): sha(p) for p in [Path(__file__), B / 'world_read_plan.py', tool.PAIR_PATH]},
              game_starts=0, process_or_display_queries=0, signals_sent=0, runtime_approved=False)
target = R / 'docs/cod4/audit-20261022/legacy-native-acceptance' / ('process-byte-checks-' + stamp + '.json')
with target.open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(json.dumps({'status': result['status'], 'checks': len(rows), 'receipt': str(target.relative_to(R)), 'game_starts': 0}))
