"""Resolve six integrated delta classes against their actual private bundle.

This is a new integration-context check, not a repeat gameplay test. It never
defines, initializes or executes the inspected classes.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'docs/cod4/audit-20261022'
sys.path.insert(0, str(ROOT / 'tools/cod4/legacy-migration-acceptance'))
from check_private_srg import parse, JAVA_HOME, SRG


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    receipt = AUDIT / 'combined-private-integration-20261102.json'
    out = AUDIT / 'combined-private-linkage-20261102.json'
    assert not out.exists(), 'Preserve prior evidence'
    raw = receipt.read_bytes()
    bundle = json.loads(raw)
    candidate = ROOT / bundle['output']
    assert sha(candidate.read_bytes()) == bundle['output_sha256']
    reobf_path = AUDIT / 'legacy-migration-acceptance/legacy-migration-private-reobf08.json'
    reobf = json.loads(reobf_path.read_text())
    args = reobf['command']
    libs = [Path(args[i + 1]) for i, a in enumerate(args) if a == '--lib']
    libs = [p for p in libs if '_mapped_official_' not in str(p)]
    paths = list(dict.fromkeys([candidate, SRG, *libs, JAVA_HOME / 'jmods/java.base.jmod']))
    archives = [(path, zipfile.ZipFile(path)) for path in paths]
    cache, used, resolutions, errors = {}, {}, [], []

    def load(name):
        if name in cache:
            return cache[name]
        for path, archive in archives:
            entry = ('classes/' if path.suffix == '.jmod' else '') + name + '.class'
            try:
                data = archive.read(entry)
            except KeyError:
                continue
            result = parse(data)
            result['archive'] = path
            cache[name] = result
            used[(str(path), entry)] = sha(data)
            return result
        cache[name] = None
        return None

    def resolve(owner, name, desc, kind, seen=None):
        seen = set() if seen is None else seen
        if owner in seen:
            return None
        seen.add(owner)
        cls = load(owner)
        if cls is None:
            return None
        if (name, desc) in cls[kind + 's']:
            return owner
        if name == '<init>':
            return None
        for parent in ([cls['parent']] if cls['parent'] else []) + cls['interfaces']:
            found = resolve(parent, name, desc, kind, seen)
            if found:
                return found
        return None

    delta = {**bundle['replaced_entries'], **bundle['added_entries']}
    for name, expected in delta.items():
        assert used.get((str(candidate), name)) in (None, expected)
        cls = load(name.removesuffix('.class'))
        assert cls and cls['archive'] == candidate and cls['major'] == 61
        assert used[(str(candidate), name)] == expected
        for dependency in sorted(cls['classes']):
            if load(dependency) is None:
                errors.append({'class': name, 'missing_class': dependency})
        for ref in cls['refs']:
            declared = resolve(ref['owner'], ref['name'], ref['descriptor'], ref['kind'])
            row = {'class': name, **ref, 'declared_in': declared}
            resolutions.append(row)
            if declared is None:
                errors.append(row)
    for _, archive in archives:
        archive.close()
    assert sha(candidate.read_bytes()) == bundle['output_sha256']
    assert sha((ROOT / bundle['base']).read_bytes()) == bundle['base_sha256']
    for path, expected in bundle['production_sources'].items():
        assert sha((ROOT / path).read_bytes()) == expected
    result = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS_COMBINED_STATIC_MEMBER_RESOLUTION' if not errors else 'FAIL_COMBINED_STATIC_MEMBER_RESOLUTION',
        'input_receipt_sha256': sha(raw), 'candidate': bundle['output'],
        'candidate_sha256': bundle['output_sha256'], 'delta_classes': delta,
        'member_reference_count': len(resolutions), 'resolutions': resolutions, 'errors': errors,
        'used_archives': {p: sha(Path(p).read_bytes()) for p in sorted({p for p, _ in used})},
        'used_class_entries': [{'archive': p, 'entry': n, 'sha256': v} for (p, n), v in sorted(used.items())],
        'classpath_source_receipt_sha256': sha(reobf_path.read_bytes()),
        'parser_tool_sha256': sha((ROOT / 'tools/cod4/legacy-migration-acceptance/check_private_srg.py').read_bytes()),
        'tool_sha256': sha(Path(__file__).read_bytes()),
        'game_starts': 0, 'shared_jar_written': False, 'native_acceptance_credit': 0,
        'checklist_deletions': 0, 'duration_hours_claimed': 0,
        'limitations': [
            'Constant-pool member/class linkage only; no class execution/initialization or Minecraft bootstrap.',
            'No access-control, event registration, Mixin, native gameplay or visual proof.',
            'The combined class context is new; this check does not repeat any passed old gameplay project.',
            'Old prepared QA plans/markers and all professional resources remain untouched.'
        ],
    }
    with out.open('x') as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'member_reference_count': len(resolutions),
                      'class_count': len(delta), 'errors': errors}, ensure_ascii=False))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
