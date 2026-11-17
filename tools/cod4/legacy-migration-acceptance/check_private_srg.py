"""Read-only class-file linkage audit; never initializes Minecraft classes."""
import hashlib
import json
import re
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'docs/cod4/audit-20261022/legacy-migration-acceptance'
RECEIPT = AUDIT / 'legacy-migration-private-reobf08.json'
JAVA_HOME = Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home')
SRG = ROOT / ('tools/cod4/ecology-acceptance/.work/client-build/gradle-home/caches/'
              'forge_gradle/minecraft_user_repo/net/minecraftforge/forge/'
              '1.20.1-47.4.10/forge-1.20.1-47.4.10-srg.jar')


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, count):
        value = self.data[self.pos:self.pos + count]
        if len(value) != count:
            raise ValueError('Truncated class file')
        self.pos += count
        return value

    def u1(self):
        return self.take(1)[0]

    def u2(self):
        return struct.unpack('>H', self.take(2))[0]

    def u4(self):
        return struct.unpack('>I', self.take(4))[0]


def parse(data):
    r = Reader(data)
    assert r.u4() == 0xCAFEBABE
    minor, major = r.u2(), r.u2()
    cp = [None] * r.u2()
    i = 1
    while i < len(cp):
        tag = r.u1()
        if tag == 1:
            value = r.take(r.u2()).decode('utf-8', errors='replace')
        elif tag in (3, 4):
            value = r.take(4).hex()
        elif tag in (5, 6):
            value = r.take(8).hex()
        elif tag in (7, 8, 16, 19, 20):
            value = r.u2()
        elif tag in (9, 10, 11, 12, 17, 18):
            value = (r.u2(), r.u2())
        elif tag == 15:
            value = (r.u1(), r.u2())
        else:
            raise ValueError(f'Unknown constant tag {tag}')
        cp[i] = (tag, value)
        i += 2 if tag in (5, 6) else 1

    def utf(index):
        assert cp[index][0] == 1
        return cp[index][1]

    def cname(index):
        return utf(cp[index][1]) if index else None

    def attributes():
        return {utf(r.u2()): r.take(r.u4()) for _ in range(r.u2())}

    def members():
        result = {}
        for _ in range(r.u2()):
            access, name, desc = r.u2(), utf(r.u2()), utf(r.u2())
            result[(name, desc)] = {'access': access, 'attributes': attributes()}
        return result

    access, name, parent = r.u2(), cname(r.u2()), cname(r.u2())
    interfaces = [cname(r.u2()) for _ in range(r.u2())]
    fields, methods, attrs = members(), members(), attributes()
    assert r.pos == len(data)
    refs, classes = [], set()
    for entry in cp:
        if not entry:
            continue
        tag, value = entry
        if tag in (9, 10, 11):
            owner = cname(value[0])
            nt = cp[value[1]]
            assert nt[0] == 12
            refs.append({'kind': 'field' if tag == 9 else 'method',
                         'interface': tag == 11, 'owner': owner,
                         'name': utf(nt[1][0]), 'descriptor': utf(nt[1][1])})
        if tag == 7:
            n = utf(value)
            if n.startswith('['):
                classes.update(re.findall(r'L([^;]+);', n))
            else:
                classes.add(n)
        if tag == 1:
            # Includes descriptors, annotations and generic signatures.
            classes.update(re.findall(r'L([a-zA-Z_$][\w$/]*);', value))
    return {'name': name, 'parent': parent, 'interfaces': interfaces,
            'access': access, 'major': major, 'minor': minor,
            'fields': fields, 'methods': methods, 'attributes': attrs,
            'refs': refs, 'classes': classes}


def main():
    receipt_bytes = RECEIPT.read_bytes()
    receipt = json.loads(receipt_bytes)
    patch = ROOT / receipt['output']
    assert sha(patch.read_bytes()) == receipt['output_sha256']
    for source, expected in receipt['production_sources'].items():
        assert sha((ROOT / source).read_bytes()) == expected, source

    command = receipt['command']
    libs = [Path(command[i + 1]) for i, arg in enumerate(command) if arg == '--lib']
    # Mojmap Minecraft must not accidentally satisfy a missing SRG symbol.
    libs = [p for p in libs if '_mapped_official_' not in str(p)]
    paths = [patch, SRG, *libs, JAVA_HOME / 'jmods/java.base.jmod']
    paths = list(dict.fromkeys(paths))
    archives = [(p, zipfile.ZipFile(p)) for p in paths]
    cache, used, errors, resolutions = {}, {}, [], []

    def load(name):
        if name in cache:
            return cache[name]
        entry = name + '.class'
        for path, archive in archives:
            key = 'classes/' + entry if path.suffix == '.jmod' else entry
            try:
                payload = archive.read(key)
            except KeyError:
                continue
            data = parse(payload)
            data['archive'], data['entry'] = path, key
            cache[name] = data
            used[(str(path), key)] = sha(payload)
            return data
        cache[name] = None
        return None

    def resolve(owner, name, desc, kind, visited=None):
        visited = set() if visited is None else visited
        if owner in visited:
            return None
        visited.add(owner)
        data = load(owner)
        if data is None:
            return None
        if (name, desc) in data[kind + 's']:
            return owner
        if name == '<init>':
            return None
        for parent in ([data['parent']] if data['parent'] else []) + data['interfaces']:
            found = resolve(parent, name, desc, kind, visited)
            if found:
                return found
        return None

    names = set(receipt['classes'])
    with zipfile.ZipFile(patch) as archive:
        assert {n for n in archive.namelist() if not n.endswith('/')} == names
        for name, expected in receipt['classes'].items():
            assert sha(archive.read(name)) == expected
    for entry in sorted(names):
        name = entry.removesuffix('.class')
        data = load(name)
        assert data['major'] == 61, (name, data['major'])
        for dependency in sorted(data['classes']):
            if load(dependency) is None:
                errors.append({'class': name, 'missing_class': dependency})
        for ref in data['refs']:
            declared = resolve(ref['owner'], ref['name'], ref['descriptor'], ref['kind'])
            row = {'class': name, **ref, 'declared_in': declared}
            resolutions.append(row)
            if declared is None:
                errors.append(row)
    used_archives = sorted({path for path, _ in used})
    result = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS_STATIC_SRG_MEMBER_RESOLUTION' if not errors else 'FAIL',
        'input_receipt_sha256': sha(receipt_bytes),
        'patch_sha256': sha(patch.read_bytes()),
        'tool_sha256': sha(Path(__file__).read_bytes()),
        'production_sources': receipt['production_sources'],
        'patch_classes': receipt['classes'], 'member_reference_count': len(resolutions),
        'resolutions': resolutions, 'errors': errors,
        'used_archives': {path: sha(Path(path).read_bytes()) for path in used_archives},
        'used_class_entries': [{'archive': p, 'entry': n, 'sha256': v}
                              for (p, n), v in sorted(used.items())],
        'limitations': [
            'Static constant-pool class/member resolution only; no class initialization or game.',
            'Not actual Forge event dispatch, registration, access-control or stack verification.',
            'Does not establish real old-world remap, Clone, TCP or current-pack acceptance.',
            'Renamer propagated LivingEntity lambda warning retained; not a patch member reference.'
        ], 'game_starts': 0, 'shared_jar_written': False,
        'runtime_acceptance_credit': 0, 'checklist_deletions': 0
    }
    output = AUDIT / 'legacy-migration-srg-linkage09.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for _, archive in archives:
        archive.close()
    print(json.dumps({k: result[k] for k in ['status', 'member_reference_count', 'errors']},
                     ensure_ascii=False))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
