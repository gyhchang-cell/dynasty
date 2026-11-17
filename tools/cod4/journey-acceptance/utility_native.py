#!/usr/bin/env python3
"""Isolated native utility run with input receipts recorded BEFORE execution."""
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
WORK = HERE / '.work/utility'
QA = HERE / 'java/JourneyUtilityGameTests.java'
INIT = HERE / 'utility.init.gradle'


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
    parser.add_argument('--cases', default='')
    parser.add_argument('--freeze', action='store_true', help='Refresh only this tool private snapshot; no other run may be active')
    args = parser.parse_args()
    assert args.run.replace('-', '').replace('_', '').isalnum(), 'Use a simple unique run name'
    run = WORK / args.run
    assert not run.exists(), 'Never reuse a native test world or replace a run receipt'
    run.mkdir(parents=True)
    manifest = freeze() if args.freeze else json.loads((WORK / 'source-hashes.json').read_text())
    assert all(sha(WORK / 'frozen' / path) == digest for path, digest in manifest.items())
    shutil.copy2(QA, run / 'JourneyUtilityGameTests.java')
    shutil.copy2(INIT, run / 'utility.init.gradle')
    dump(run / 'source-hashes.json', manifest)
    command = ['./gradlew', '--offline', '--no-daemon', '--max-workers=2',
        '--project-cache-dir', str((WORK / 'project-cache').relative_to(ROOT)),
        '-I', str(INIT.relative_to(ROOT)), '-PjourneyRun=' + args.run,
        '-PutilityCases=' + args.cases, 'runGameTestServer']
    receipt = {'run': args.run, 'started_at': datetime.datetime.now().astimezone().isoformat(),
        'command': command, 'qa_sha256': sha(QA), 'init_sha256': sha(INIT),
        'build_gradle_sha256': sha(ROOT / 'build.gradle'), 'source_manifest_sha256': sha(run / 'source-hashes.json'),
        'selected_cases': args.cases or 'ALL', 'source_file_count': len(manifest)}
    dump(run / 'run-receipt.json', receipt)
    env = dict(os.environ)
    env.setdefault('JAVA_HOME', '/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home')
    with (WORK / (args.run + '.log')).open('w') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    receipt.update(finished_at=datetime.datetime.now().astimezone().isoformat(), exit_code=result.returncode,
        qa_unchanged_during_run=sha(QA) == receipt['qa_sha256'],
        init_unchanged_during_run=sha(INIT) == receipt['init_sha256'],
        log_sha256=sha(WORK / (args.run + '.log')))
    dump(run / 'run-receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
