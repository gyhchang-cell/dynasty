"""Add the two audited classes to a private copy of today's shared JAR only."""
import copy
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'docs/cod4/audit-20261022/legacy-migration-acceptance'
BASE = ROOT / 'modpack/mods/dynasty-1.4.0.jar'
EXPECTED_BASE = '0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'
OUTPUT = ROOT / 'build/cod4-legacy-fix-20261102/private-bundle10/dynasty-1.4.0.jar'
ALLOWED = {'com/dynasty/LegacyItemMappings.class', 'com/dynasty/LegacyPlayerProgression.class'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    reobf_path = AUDIT / 'legacy-migration-private-reobf08.json'
    link_path = AUDIT / 'legacy-migration-srg-linkage09.json'
    owner_path = AUDIT / 'legacy-migration-current-owner11.json'
    reobf = json.loads(reobf_path.read_text())
    link = json.loads(link_path.read_text())
    owner = json.loads(owner_path.read_text())
    assert link['status'] == 'PASS_STATIC_SRG_MEMBER_RESOLUTION' and not link['errors']
    assert link['input_receipt_sha256'] == digest(reobf_path.read_bytes())
    assert owner['status'] == 'PASS_CURRENT_OWNER_REFERENCED_MEMBER_ONLY'
    assert owner['patch_sha256'] == reobf['output_sha256']
    assert owner['input_receipt_sha256'][str(link_path.relative_to(ROOT))] == digest(link_path.read_bytes())
    assert set(reobf['classes']) == ALLOWED
    for source, expected in reobf['production_sources'].items():
        assert digest((ROOT / source).read_bytes()) == expected, source
    base_before = digest(BASE.read_bytes())
    assert base_before == EXPECTED_BASE, 'Shared JAR changed; review its current input first'
    assert owner['base_sha256'] == base_before
    patch_path = ROOT / reobf['output']
    assert digest(patch_path.read_bytes()) == reobf['output_sha256']
    assert not OUTPUT.exists(), 'Do not overwrite a prepared candidate'
    before = {}
    with zipfile.ZipFile(BASE) as base, zipfile.ZipFile(patch_path) as patch:
        infos = base.infolist()
        names = base.namelist()
        assert len(names) == len(set(names))
        assert not ALLOWED.intersection(names), 'This candidate expects two new classes'
        assert not any(n.upper().startswith('META-INF/') and n.upper().endswith(('.SF', '.RSA', '.DSA'))
                       for n in names), 'Signed JAR needs a different release workflow'
        assert digest(base.read('com/dynasty/Dynasty.class')) == owner['current_owner_sha256']
        assert {n for n in patch.namelist() if not n.endswith('/')} == ALLOWED
        payloads = {name: patch.read(name) for name in sorted(ALLOWED)}
        assert {name: digest(data) for name, data in payloads.items()} == reobf['classes']
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT.open('xb') as handle, zipfile.ZipFile(handle, 'w') as out:
            out.comment = base.comment
            for info in infos:
                data = base.read(info.filename)
                before[info.filename] = digest(data)
                out.writestr(copy.copy(info), data)
            for name, data in payloads.items():
                info = copy.copy(patch.getinfo(name))
                out.writestr(info, data)
    with zipfile.ZipFile(OUTPUT) as out:
        assert out.testzip() is None
        assert len(out.namelist()) == len(set(out.namelist()))
        assert set(out.namelist()) == set(before) | ALLOWED
        for name, expected in before.items():
            assert digest(out.read(name)) == expected, name
        for name, expected in reobf['classes'].items():
            assert digest(out.read(name)) == expected, name
    assert digest(BASE.read_bytes()) == base_before, 'Input changed during preparation'
    report = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PRIVATE_CANDIDATE_PREPARED_NOT_RUNTIME_ACCEPTED',
        'base': str(BASE.relative_to(ROOT)), 'base_sha256': base_before,
        'output': str(OUTPUT.relative_to(ROOT)), 'output_sha256': digest(OUTPUT.read_bytes()),
        'production_sources': reobf['production_sources'],
        'added_entries': reobf['classes'], 'changed_existing_entries': [],
        'unchanged_existing_entries': len(before),
        'existing_entry_payload_manifest_sha256': digest(json.dumps(before, sort_keys=True).encode()),
        'input_receipts': {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in (reobf_path, link_path, owner_path)},
        'tool_sha256': digest(Path(__file__).read_bytes()),
        'zip_crc': 'PASS', 'duplicate_entries': 0, 'shared_jar_written': False,
        'specialist_asset_payloads_unchanged': True,
        'sweep_private_candidate_not_merged': True,
        'ready_or_execution_marker_created': False, 'game_starts': 0,
        'runtime_acceptance_credit': 0, 'checklist_deletions': 0,
        'limitations': ['Only two migration classes added to a private current-base copy.',
                        'No actual MissingMappings/Clone/old-world/network validation.',
                        'Existing source-only changes and private sweep changes are not claimed integrated.',
                        'No shared JAR, original saves, exports, user client or professional assets written.']
    }
    report_path = AUDIT / 'legacy-migration-private-bundle10.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'unchanged_existing_entries', 'output_sha256']},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
