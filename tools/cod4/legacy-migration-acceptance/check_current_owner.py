"""Resolve the patch's Dynasty member against the current package, not a stale owner."""
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from check_private_srg import AUDIT, ROOT, parse


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source = AUDIT / 'legacy-migration-private-reobf08.json'
    reobf = json.loads(source.read_text())
    previous = AUDIT / 'legacy-migration-srg-linkage09.json'
    link = json.loads(previous.read_text())
    assert link['status'] == 'PASS_STATIC_SRG_MEMBER_RESOLUTION' and not link['errors']
    base = ROOT / 'modpack/mods/dynasty-1.4.0.jar'
    base_sha = sha(base.read_bytes())
    assert base_sha == '0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'
    with zipfile.ZipFile(base) as archive:
        owner_bytes = archive.read('com/dynasty/Dynasty.class')
    owner = parse(owner_bytes)
    patch_path = ROOT / reobf['output']
    assert sha(patch_path.read_bytes()) == reobf['output_sha256']
    references = []
    with zipfile.ZipFile(patch_path) as patch:
        for name in sorted(reobf['classes']):
            for ref in parse(patch.read(name))['refs']:
                if ref['owner'].startswith('com/dynasty/') and ref['owner'] not in {
                        'com/dynasty/LegacyItemMappings', 'com/dynasty/LegacyPlayerProgression'}:
                    assert ref['owner'] == 'com/dynasty/Dynasty', ref
                    assert ref['kind'] == 'field' and ref['name'] == 'LOGGER', ref
                    assert ref['descriptor'] == 'Lorg/slf4j/Logger;', ref
                    flags = owner['fields'][(ref['name'], ref['descriptor'])]['access']
                    assert flags & 0x0001 and flags & 0x0008, 'LOGGER must be public static'
                    references.append({'patch_class': name, **ref, 'current_owner_field_flags': flags})
    assert len(references) == 2
    assert sha(base.read_bytes()) == base_sha
    report = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS_CURRENT_OWNER_REFERENCED_MEMBER_ONLY',
        'base': str(base.relative_to(ROOT)), 'base_sha256': base_sha,
        'current_owner_sha256': sha(owner_bytes),
        'prior_compilation_owner_sha256': reobf['baseline_owner_sha256'],
        'owner_bytes_equal': sha(owner_bytes) == reobf['baseline_owner_sha256'],
        'references': references,
        'patch_sha256': reobf['output_sha256'],
        'input_receipt_sha256': {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in (source, previous)},
        'tool_sha256': sha(Path(__file__).read_bytes()),
        'earlier_preparation_guard': {
            'result': 'BLOCKED_BEFORE_OUTPUT_WRITE',
            'reason': 'Exact current Dynasty.class SHA differs from the old Mojmap compilation library.',
            'failed_candidate_created': False,
            'resolution': 'Actual current public static LOGGER descriptor matches both patch references; no old class copied.'
        },
        'limitations': ['Only referenced owner member is checked; no equivalence claim for all Dynasty behavior.',
                        'This does not prove class initialization, Forge registration or runtime success.'],
        'game_starts': 0, 'shared_jar_written': False, 'checklist_deletions': 0
    }
    output = AUDIT / 'legacy-migration-current-owner11.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'references': len(references),
                      'current_owner_sha256': report['current_owner_sha256']}))


if __name__ == '__main__':
    main()
