#!/usr/bin/env python3
"""Isolated native connected-route run with input receipts recorded BEFORE execution."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = HERE / '.work/routes'
QA = HERE / 'java/JourneyRouteGameTests.java'
INIT = HERE / 'routes.init.gradle'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def freeze():
    manifest = {}
    for relative in ('src/main/java', 'src/main/resources'):
        for source in sorted((ROOT / relative).rglob('*')):
            if not source.is_file():
                continue
            relative_path = source.relative_to(ROOT)
            data = source.read_bytes()
            manifest[str(relative_path)] = hashlib.sha256(data).hexdigest()
            target = WORK / 'frozen' / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    for path in (WORK / 'frozen').rglob('*'):
        if path.is_file() and str(path.relative_to(WORK / 'frozen')) not in manifest:
            path.unlink()
    dump(WORK / 'source-hashes.json', manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--freeze', action='store_true', help='Refresh only this tool private snapshot; no other run may be active')
    args = parser.parse_args()
    assert args.run.replace('-', '').replace('_', '').isalnum(), 'Use a simple unique run name'
    run = WORK / args.run
    assert not run.exists(), 'Never reuse a native test world or replace a run receipt'
    run.mkdir(parents=True)
    manifest = freeze() if args.freeze else json.loads((WORK / 'source-hashes.json').read_text())
    assert all(sha(WORK / 'frozen' / path) == digest for path, digest in manifest.items())
    shutil.copytree(ROOT / 'modpack/config/ftbquests/quests', run / 'config/ftbquests/quests')
    quest_hashes = {str(p.relative_to(run)): sha(p) for p in sorted((run / 'config').rglob('*')) if p.is_file()}
    dump(run / 'quest-hashes.json', quest_hashes)
    plan = json.loads((HERE / 'routes/plan.json').read_text())
    for path, digest in plan['input_sha256'].items():
        checked = run / path.removeprefix('modpack/') if path.startswith('modpack/') else WORK / 'frozen' / path
        assert sha(checked) == digest, 'Graph/recipe input changed; rebuild route_plan and refresh private freeze: ' + path
    qa_resources = WORK / 'qa-resources'
    qa_resources.mkdir(parents=True, exist_ok=True)
    for name in ('quest-graph', 'recipes'):
        shutil.copy2(HERE / ('routes/' + name + '.json'), qa_resources / ('route-' + name + '.json'))
    equipment = json.loads((HERE / 'old-equipment-utility.json').read_text())
    dump(qa_resources / 'route-equipment.json', {'items': [i['item'] for i in equipment['items']]})
    shutil.copytree(qa_resources, run / 'qa-inputs')
    shutil.copy2(QA, run / 'JourneyRouteGameTests.java')
    supply_qa = HERE / 'java/JourneySupplyGameTests.java'
    shutil.copy2(supply_qa, run / supply_qa.name)
    shutil.copy2(INIT, run / 'routes.init.gradle')
    dump(run / 'source-hashes.json', manifest)
    command = ['./gradlew', '--offline', '--no-daemon', '--max-workers=2',
        '--project-cache-dir', str((WORK / 'project-cache').relative_to(ROOT)),
        '-I', str(INIT.relative_to(ROOT)), '-PjourneyRun=' + args.run,
        'runGameTestServer']
    receipt = {'run': args.run, 'started_at': datetime.datetime.now().astimezone().isoformat(),
        'command': command, 'qa_sha256': sha(QA), 'supply_qa_sha256': sha(supply_qa), 'init_sha256': sha(INIT),
        'build_gradle_sha256': sha(ROOT / 'build.gradle'), 'source_manifest_sha256': sha(run / 'source-hashes.json'),
        'selected_cases': 'ALL', 'source_file_count': len(manifest), 'quest_manifest_sha256': sha(run / 'quest-hashes.json'), 'qa_inputs': {p.name: sha(p) for p in sorted(qa_resources.glob('*.json'))}}
    dump(run / 'run-receipt.json', receipt)
    env = dict(os.environ)
    env.setdefault('JAVA_HOME', '/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home')
    with (WORK / (args.run + '.log')).open('w') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    receipt.update(finished_at=datetime.datetime.now().astimezone().isoformat(), exit_code=result.returncode,
        qa_unchanged_during_run=sha(QA) == receipt['qa_sha256'],
        supply_qa_unchanged_during_run=sha(supply_qa) == receipt['supply_qa_sha256'],
        init_unchanged_during_run=sha(INIT) == receipt['init_sha256'],
        log_sha256=sha(WORK / (args.run + '.log')))
    dump(run / 'run-receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
