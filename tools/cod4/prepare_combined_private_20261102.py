"""Combine two exact, previously built SRG deltas against the current shared base.

This produces a private review candidate only. It deliberately does not update
prepared QA instances, their frozen inputs, plans, readiness or execution marks.
"""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'docs/cod4/audit-20261022'
OUT = ROOT / 'build/cod4-combined-private-20261102/candidate01/dynasty-1.4.0.jar'
REPORT = AUDIT / 'combined-private-integration-20261102.json'
BASE = ROOT / 'modpack/mods/dynasty-1.4.0.jar'
BASE_SHA = '0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_receipt(rel):
    path = AUDIT / rel
    raw = path.read_bytes()
    return json.loads(raw), {str(path.relative_to(ROOT)): sha(raw)}


def payloads(path, expected):
    assert sha(path.read_bytes()) == expected, path
    with zipfile.ZipFile(path) as jar:
        assert len(jar.namelist()) == len(set(jar.namelist())), 'Duplicate ZIP entries'
        assert jar.testzip() is None, 'CRC mismatch'
        return {n: jar.read(n) for n in jar.namelist()}


def main():
    assert not OUT.exists() and not REPORT.exists(), 'Preserve existing candidate and receipt'
    sweep, bindings = read_receipt('sweep-native-acceptance/current-bundle-private-integration.json')
    migration, more = read_receipt('legacy-migration-acceptance/legacy-migration-private-bundle10.json')
    bindings.update(more)
    independent, more = read_receipt('sweep-receipt-research/helpers/jason-sweep/sweep-production-fix-review.json')
    bindings.update(more)
    assert independent['status'] == 'NO_NEW_DETERMINISTIC_STATIC_BLOCKER_NATIVE_ACCEPTANCE_PENDING'
    assert not independent['blocking_findings']
    assert sweep['base_sha256'] == migration['base_sha256'] == BASE_SHA
    sweep_names = {
        'com/dynasty/cod3/FangtianSweep.class',
        'com/dynasty/cod3/FangtianSweep$Start.class',
        'com/dynasty/cod3/FangtianSweep$Contact.class',
        'com/dynasty/cod3/FangtianSweep$Receipt.class',
    }
    added = {'com/dynasty/LegacyItemMappings.class', 'com/dynasty/LegacyPlayerProgression.class'}
    assert set(sweep['changed_entries']) == sweep_names
    assert set(migration['added_entries']) == added and not migration['changed_existing_entries']
    source_hashes = dict(migration['production_sources'])
    source_hashes[independent['production']['path']] = independent['production']['sha256']
    for path, expected in source_hashes.items():
        assert sha((ROOT / path).read_bytes()) == expected, path
    base = payloads(BASE, BASE_SHA)
    old_sweep = payloads(ROOT / sweep['private_jar'], sweep['private_jar_sha256'])
    old_migration = payloads(ROOT / migration['output'], migration['output_sha256'])
    assert len(base) == 6789
    assert set(old_sweep) == set(base)
    assert {n for n in base if old_sweep[n] != base[n]} == sweep_names
    assert set(old_migration) == set(base) | added and not added.intersection(base)
    assert all(old_migration[n] == raw for n, raw in base.items())
    assert {n: sha(old_migration[n]) for n in added} == migration['added_entries']
    delta = {n: old_sweep[n] for n in sweep_names}
    delta.update({n: old_migration[n] for n in added})
    assert len(delta) == 6
    assert not any(n.upper().startswith('META-INF/') and n.upper().endswith(('.SF', '.RSA', '.DSA')) for n in base)
    # Existing resource entries, manifests, professional assets and unrelated
    # classes all come from the CURRENT base, never from either older full JAR.
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BASE) as original, zipfile.ZipFile(ROOT / migration['output']) as migration_jar:
        with OUT.open('xb') as file, zipfile.ZipFile(file, 'w') as jar:
            jar.comment = original.comment
            for info in original.infolist():
                jar.writestr(copy.copy(info), delta.get(info.filename, base[info.filename]))
            for name in sorted(added):
                jar.writestr(copy.copy(migration_jar.getinfo(name)), delta[name])
    with zipfile.ZipFile(OUT) as jar:
        assert jar.testzip() is None
        assert len(jar.namelist()) == len(set(jar.namelist()))
        assert set(jar.namelist()) == set(base) | added
        changed = {n for n in base if jar.read(n) != base[n]}
        assert changed == sweep_names
        for name, raw in base.items():
            if name not in sweep_names:
                assert jar.read(name) == raw, name
        for name, raw in delta.items():
            assert jar.read(name) == raw
        # Explicit professional-data protection separate from class delta checks.
        resources = {n: sha(raw) for n, raw in base.items() if not n.endswith('.class')}
        assert all(sha(jar.read(n)) == expected for n, expected in resources.items())
    assert sha(BASE.read_bytes()) == BASE_SHA, 'Shared base changed during preparation'
    assert all(sha((ROOT / n).read_bytes()) == expected for n, expected in source_hashes.items())
    result = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PRIVATE_SIX_CLASS_SRG_INTEGRATION_PAYLOAD_PASS_NATIVE_ACCEPTANCE_PENDING',
        'base': str(BASE.relative_to(ROOT)), 'base_sha256': BASE_SHA,
        'output': str(OUT.relative_to(ROOT)), 'output_sha256': sha(OUT.read_bytes()),
        'input_receipts': bindings, 'production_sources': source_hashes,
        'replaced_entries': {n: sha(delta[n]) for n in sorted(sweep_names)},
        'added_entries': {n: sha(delta[n]) for n in sorted(added)},
        'unchanged_existing_entries': len(base) - len(sweep_names),
        'existing_entry_count': len(base), 'output_entry_count': len(base) + len(added),
        'unchanged_resource_entries': len(resources),
        'resource_payload_manifest_sha256': sha(json.dumps(resources, sort_keys=True).encode()),
        'zip_crc': 'PASS', 'duplicate_entries': 0,
        'tool_sha256': sha(Path(__file__).read_bytes()),
        'shared_jar_written': False, 'professional_asset_payloads_unchanged': True,
        'qa_instances_or_old_plans_updated': False, 'ready_or_execution_marker_created': False,
        'production_source_mutations': 0, 'game_starts': 0, 'native_acceptance_credit': 0,
        'research_credit': 0, 'checklist_deletions': 0, 'duration_hours_claimed': 0,
        'limitations': [
            'Integration of the exact four sweep and two migration classes only, not all working-tree source fixes.',
            'No new game runtime, event dispatch, old-world or multiplayer/visual acceptance.',
            'Current independent review of migration production source remains pending.',
            'This candidate is not bound to the old sweep01 plan/ready; those inputs and markers remain untouched.',
            'No shared install, save access, export, push or specialist-art publication.'
        ],
    }
    with REPORT.open('x') as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'output_sha256', 'unchanged_existing_entries',
                                          'unchanged_resource_entries', 'output_entry_count']}))


if __name__ == '__main__':
    main()
