#!/usr/bin/env python3
"""Snapshot current inputs without touching shared builds, packs or installed instances."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = HERE / '.work'


def main():
    manifest = {}
    for relative in ('src/main/java', 'src/main/resources', 'src/generated/resources'):
        for source in sorted((ROOT / relative).rglob('*')):
            if not source.is_file():
                continue
            rel = source.relative_to(ROOT)
            content = source.read_bytes()
            manifest[str(rel)] = hashlib.sha256(content).hexdigest()
            target = WORK / 'frozen' / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    # Do not let deleted production files survive in the private snapshot.
    for target in (WORK / 'frozen/src').rglob('*'):
        if target.is_file() and str(target.relative_to(WORK / 'frozen')) not in manifest:
            target.unlink()
    recipe_root = WORK / 'frozen/src/main/resources/data/dynasty/recipes'
    recipes = []
    for path in sorted(recipe_root.rglob('*.json')):
        data = json.loads(path.read_text())
        recipes.append({'id': 'dynasty:' + str(path.relative_to(recipe_root).with_suffix('')), 'json': data})
    (WORK / 'qa-resources').mkdir(parents=True, exist_ok=True)
    (WORK / 'qa-resources/journey-recipes.json').write_text(json.dumps(recipes))
    (WORK / 'source-hashes.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Frozen {len(manifest)} files and {len(recipes)} exact recipe definitions under {WORK}')


if __name__ == '__main__':
    main()
