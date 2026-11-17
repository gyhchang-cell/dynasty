"""Read native FTB consumer bytecode without defining Minecraft classes."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/cod4/audit-20261022/armor-itemtask-native-20261102'
JAVAP = Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javap')
INPUTS = {
    'ftb-quests-forge-2001.4.22.jar': [
        'quest/task/ItemTask', 'quest/Chapter', 'quest/BaseQuestFile',
        'util/FTBQuestsInventoryListener', 'integration/item_filtering/ItemMatchingSystem',
    ],
    'ftb-library-forge-2001.2.13.jar': ['config/Tristate'],
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    bindings = []
    for jar, classes in INPUTS.items():
        path = ROOT / 'modpack/mods' / jar
        payload = path.read_bytes()
        prefix = 'dev/ftb/mods/' + ('ftbquests/' if 'quests-' in jar else 'ftblibrary/')
        with zipfile.ZipFile(path) as archive:
            for suffix in classes:
                entry = prefix + suffix + '.class'
                raw = archive.read(entry)
                proc = subprocess.run(
                    [str(JAVAP), '-p', '-c', '-classpath', str(path),
                     entry[:-6].replace('/', '.')],
                    check=True, capture_output=True, text=True, timeout=25,
                )
                assert not proc.stderr.strip(), proc.stderr
                target = OUT / (suffix.replace('/', '_') + '.javap.txt')
                data = proc.stdout.encode()
                if target.exists():
                    assert target.read_bytes() == data, target
                else:
                    target.write_bytes(data)
                bindings.append({'jar': str(path.relative_to(ROOT)), 'jar_sha256': sha(payload),
                                 'entry': entry, 'class_sha256': sha(raw),
                                 'javap': str(target.relative_to(ROOT)),
                                 'javap_sha256': sha(data), 'lines': len(proc.stdout.splitlines())})
        assert sha(path.read_bytes()) == sha(payload)
    record = {'status': 'BYTECODE_CAPTURE_ONLY_SEMANTIC_REVIEW_PENDING',
              'bindings': bindings, 'javap': str(JAVAP),
              'javap_sha256': sha(JAVAP.read_bytes()),
              'tool_sha256': sha(Path(__file__).read_bytes()),
              'minecraft_class_execution': False, 'game_starts': 0,
              'reference_credit': 0, 'production_mutations': 0,
              'prior_capture_failure': 'Initial capture stopped at absent QuestFile.class after two unchanged captures; actual BaseQuestFile substituted after archive inventory.'}
    (OUT / 'capture.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'captures': len(bindings),
                      'lines': sum(x['lines'] for x in bindings)}))


if __name__ == '__main__':
    main()
