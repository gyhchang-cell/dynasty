"""Resolve the new QA classes in the candidate/SRG context, without defining any class."""
from pathlib import Path
from contextlib import ExitStack
import datetime
import hashlib
import json
import sys
import zipfile

R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / 'tools/cod4/legacy-migration-acceptance'))
from check_private_srg import parse, SRG, JAVA_HOME

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
receipt_path = R / sys.argv[1]
receipt = json.loads(receipt_path.read_text())
assert receipt['status'] == 'PASS'
qa = R / receipt['output']
assert sha(qa) == receipt['output_sha256']
for name, expected in receipt['sources'].items():
    assert sha(R / name) == expected, name
libraries = []
for name, row in receipt['libraries'].items():
    p = Path(name)
    assert sha(p) == row['sha256'], name
    if '_mapped_official_' not in name:
        libraries.append(p)
candidate = R / 'build/cod4-combined-private-20261102/candidate01/dynasty-1.4.0.jar'
assert sha(candidate) == 'e5a78244082214ab5fd76eb35bbb42151e3ec7bd8bc13afee3bc58ea4fe3a669'
paths = list(dict.fromkeys([qa, candidate, SRG, *libraries, JAVA_HOME / 'jmods/java.base.jmod']))
cache, used, resolutions, errors = {}, {}, [], []
with ExitStack() as stack:
    archives = [(p, stack.enter_context(zipfile.ZipFile(p))) for p in paths]

    def load(name):
        if name in cache:
            return cache[name]
        for p, z in archives:
            entry = ('classes/' if p.suffix == '.jmod' else '') + name + '.class'
            try:
                raw = z.read(entry)
            except KeyError:
                continue
            result = parse(raw)
            result['archive'] = p
            cache[name] = result
            used[(str(p), entry)] = hashlib.sha256(raw).hexdigest()
            return result
        cache[name] = None
        return None

    def resolve(owner, name, descriptor, kind, seen=None):
        seen = set() if seen is None else seen
        if owner in seen:
            return None
        seen.add(owner)
        cls = load(owner)
        if cls is None:
            return None
        if (name, descriptor) in cls[kind + 's']:
            return owner
        if name == '<init>':
            return None
        for parent in ([cls['parent']] if cls['parent'] else []) + cls['interfaces']:
            found = resolve(parent, name, descriptor, kind, seen)
            if found:
                return found
        return None

    classes = {n: digest for n, digest in receipt['entries'].items() if n.endswith('.class')}
    for name, digest in classes.items():
        cls = load(name.removesuffix('.class'))
        assert cls and cls['archive'] == qa and cls['major'] == 61
        assert used[(str(qa), name)] == digest
        for dependency in sorted(cls['classes']):
            if load(dependency) is None:
                errors.append({'qa_class': name, 'missing_class': dependency})
        for ref in cls['refs']:
            declared = resolve(ref['owner'], ref['name'], ref['descriptor'], ref['kind'])
            row = {'qa_class': name, **ref, 'declared_in': declared}
            resolutions.append(row)
            if declared is None:
                errors.append(row)
assert sha(qa) == receipt['output_sha256']
result = dict(status='PASS_STATIC_QA_MEMBER_RESOLUTION' if not errors else 'FAIL_STATIC_QA_MEMBER_RESOLUTION',
              recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              reobf_receipt=str(receipt_path.relative_to(R)), reobf_receipt_sha256=sha(receipt_path),
              qa=str(qa.relative_to(R)), qa_sha256=sha(qa), candidate_sha256=sha(candidate),
              classes=classes, member_reference_count=len(resolutions), resolutions=resolutions, errors=errors,
              used_archives={p: sha(Path(p)) for p in sorted({p for p, _ in used})},
              used_entries=[{'archive': p, 'entry': n, 'sha256': digest} for (p, n), digest in sorted(used.items())],
              parser_sha256=sha(R / 'tools/cod4/legacy-migration-acceptance/check_private_srg.py'),
              limitations=['No class definition/initialization, access-control or JVM verifier claim',
                           'No subscriber discovery, C2S, Clone, world load or native acceptance',
                           'Renamer propagation warnings preserved, not silently classified as runtime-safe'],
              game_starts=0, runtime_approved=False, checklist_deletions=0)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
target = R / 'docs/cod4/audit-20261022/legacy-native-acceptance' / ('linkage-' + stamp + '.json')
with target.open('x') as f:
    json.dump(result, f, indent=2); f.write('\n')
print(json.dumps({'status': result['status'], 'receipt': str(target.relative_to(R)), 'refs': len(resolutions), 'errors': errors}))
raise SystemExit(bool(errors))
