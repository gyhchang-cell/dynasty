"""Read static armor declarations without loading or executing any mod code."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile

D = Path(__file__).resolve().parent
JAVAP = Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javap')


def save(n, v):
    (D / n).write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')


def main():
    assert not (D / 'binding-class-provenance.json').exists()
    p = json.loads((D / 'provenance.json').read_text())
    classes, mappings = [], []
    for archive in p['archives']:
        jar = archive['path']
        with zipfile.ZipFile(jar) as z:
            paths = z.namelist()
            targets = {}
            for case in p['cases']:
                if case['icons'][0]['jar'] != jar:
                    continue
                key = case['case_key'].split(':')[1].replace('_', '').lower()
                bases = [e for e in paths if '/item/' in e and e.endswith('Item.class') and '$' not in e
                         and Path(e).stem.removesuffix('Item').lower() == key]
                assert len(bases) == 1, (key, bases)
                base = bases[0]
                sub = [base.removesuffix('.class') + '$' + part + '.class' for part in ['Helmet', 'Chestplate', 'Leggings', 'Boots']]
                assert all(e in paths for e in sub)
                targets[base] = False
                for e in sub:
                    targets[e] = False
                mappings.append({'case_key': case['case_key'], 'base': base, 'parts': sub, 'jar': jar})
            registries = [e for e in paths if '/init/' in e and e.endswith('ModItems.class')]
            assert len(registries) == 1, registries
            targets[registries[0]] = True
            for entry, verbose in targets.items():
                b = z.read(entry); h = hashlib.sha256(b).hexdigest(); ns = next(c['case_key'].split(':')[0] for c in p['cases'] if c['icons'][0]['jar'] == jar)
                local = Path('binding-classes') / ns / f'{h[:12]}-{Path(entry).name}'
                (D / local).parent.mkdir(parents=True, exist_ok=True)
                (D / local).write_bytes(b)
                listing = Path('binding-disassembly') / ns / (Path(entry).stem + ('-verbose' if verbose else '') + '.txt')
                (D / listing).parent.mkdir(parents=True, exist_ok=True)
                command = [str(JAVAP), '-p', '-c', *(['-v'] if verbose else []), str(D / local)]
                result = subprocess.run(command, check=True, capture_output=True)
                (D / listing).write_bytes(result.stdout)
                classes.append({'jar': jar, 'entry': entry, 'sha256': h, 'local': str(local), 'disassembly': str(listing),
                                'disassembly_sha256': hashlib.sha256(result.stdout).hexdigest(), 'verbose': verbose,
                                'scope': 'Static resource and slot declarations only; mod code not executed.'})
    save('binding-class-provenance.json', {'javap': str(JAVAP), 'javap_sha256': hashlib.sha256(JAVAP.read_bytes()).hexdigest(),
                                          'classes': classes, 'case_class_mappings': mappings, 'game_starts': 0})
    print(json.dumps({'static_classes_copied': len(classes), 'sets': len(mappings), 'registry_classes': 3}))


if __name__ == '__main__':
    main()
