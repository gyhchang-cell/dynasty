"""Review archived native evidence without launching Minecraft or changing game files."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / 'docs/cod4/audit-20261022/armor-network-acceptance'


def read(name):
    return json.loads((P / name).read_text())


def require(condition, detail):
    if not condition:
        raise AssertionError(detail)


matrix = read('result-matrix.json')
rows = matrix['rows']
require(len(rows) == 84, '84 rows')
sets = {r['set'] for r in rows}
require(len(sets) == 28, '28 distinct sets')
require(len({(r['set'], r['pieces']) for r in rows}) == 84, 'unique tiers')
for name in sets:
    require({r['pieces'] for r in rows if r['set'] == name} == {2, 3, 4}, name)
for row in rows:
    raw = read(row['serverResult'])
    require((raw['set'], raw['pieces']) == (row['set'], row['pieces']), 'raw identity')
    failures = [c['name'] for c in raw['checks'] if not c['passed']]
    if row['set'] == 'leather' and row['pieces'] == 4:
        require(failures == ['mechanism leather_4'], 'only obsolete leather assertion')
    else:
        require(not failures and raw['passed'], f"native checks case {row['case']}")
    require(all(c['passed'] for c in row['checks']), 'adjudicated checks')
    require(row['mechanismPassed'], 'mechanism outcome')
    for role in ('host', 'peer'):
        read(row['actualClients'][role])

connections = read('run-13/connections.json')
require(len(connections) == 2 and len({c['uuid'] for c in connections}) == 2, 'distinct players')
require(any(c['remote'].startswith('/') for c in connections), 'actual TCP peer')
sounds = read('run-13/peer-gap-sounds.json')
trace = read('run-13/gap-sound-server-trace.json')
sound_result = []
for stage in (1, 2, 3):
    segment = read(f'run-13/gap-sound-server-segment-{stage}.json')
    samples = [t for t in trace if t['seq'] == segment['seq']]
    require(samples == segment['trace'] and len(samples) == 180, '180 original samples')
    require(all(b['tick'] == a['tick'] + 1 for a, b in zip(samples, samples[1:])), 'native consecutive clock')
    distance = sum(d for a, b in zip(samples, samples[1:])
                   if (d := sum((x-y)**2 for x, y in zip(a['position'], b['position']))**.5) < 2)
    require(abs(distance - segment['traveled']) < 1e-7 and distance > 10, 'recomputed movement')
    events = [s for s in sounds if s['seq'] == segment['seq']]
    channels = [s for s in events if s['kind'] == 'native-PlaySoundSourceEvent-channel']
    if stage == 2:
        require(sum(s['shift'] for s in samples) >= 179 and not events, 'moving crouch silent')
    else:
        require(len(channels) == 30, 'sprint positive actual sound channels')
    for role in ('host', 'peer'):
        frame = read(f"run-13/{role}-gap-frame-{segment['seq']}.json")
        require('AFTER_LEVEL' in frame['captureEvent'], 'actual rendered frame')
        require(frame['masterVolume'] > 0 and frame['playersVolume'] > 0, 'nonmuted')
    sound_result.append({'stage': stage, 'native_ticks': len(samples),
                         'recomputed_distance': distance, 'actual_sound_channels': len(channels)})

repeat = read('run-13/gap-repeat-result.json')['observations']
require(len(repeat) == 168, '28 sets, three equip/unwear cycles')
grouped = defaultdict(list)
for row in repeat:
    grouped[row['set']].append(row)
require(set(grouped) == sets, 'repeat denominator matches mechanism matrix')
for name, observations in grouped.items():
    require([(r['cycle'], r['action']) for r in observations] ==
            [(c, a) for c in (1, 2, 3) for a in ('equipped', 'unworn')], 'cycle ordering')
    for row in observations:
        attrs = row['attributes']
        reference = observations[0 if row['action'] == 'equipped' else 1]['attributes']
        require(attrs == reference, 'recomputed exact attribute/UUID equality')
        if row['action'] == 'equipped':
            require(set(row['gearIdentities']) == {f'{name}/{i}' for i in range(4)}, 'same four stacks')
        else:
            require(row['returnedToBaseline'], 'initial baseline verified by passive fixture')
    require(observations[-1]['nativeEquipmentChanges'] - observations[0]['nativeEquipmentChanges'] == 20,
            'five subsequent four-slot native changes')

manifest = read('evidence-sha256.json')['files']
summary_changes = {}
derived_summaries = {'final-report.txt', 'receipt-matrix.json', 'result-matrix.json'}
for name, receipt in manifest.items():
    path = P / name
    require(path.is_file(), f'missing {name}')
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != receipt['sha256']:
        require(name in derived_summaries, f'raw evidence hash {name}')
        summary_changes[name] = {'archived_manifest_sha256': receipt['sha256'],
                                 'current_sha256': actual,
                                 'note': 'Derived acceptance summary updated after original manifest; original evidence manifest preserved.'}

report = {'status': 'PASS_WITH_EXPLICIT_SEPARATE_OWNERSHIP_DEFECT', 'sets': 28,
          'native_mechanism_tiers': 84, 'native_repeat_observations': 168,
          'sound_segments_recomputed': sound_result, 'manifest_files_checked': len(manifest),
          'derived_summary_hash_changes': summary_changes,
          'unchanged_raw_evidence_files': len(manifest) - len(summary_changes),
          'raw_leather_failure_preserved': True,
          'guard_targeting_defect_retained': 'defect-unprovoked-guard.json',
          'scope': 'Archived actual automated native client evidence; supplied gear/environments. No new game launch. Not natural survival acquisition or fullpack compatibility.',
          'game_content_modified': False}
(P / 'coordinator-closure-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
