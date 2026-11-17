"""Prepare/check one isolated historical-world read. Only reviewed run starts Java."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
R = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
BUILD = R / 'build/cod4-legacy-native-20261102'
RUN = BUILD / 'read01'
HOST, OUT = RUN / 'host', RUN / 'evidence'
DOC = R / 'docs/cod4/audit-20261022/legacy-native-acceptance'
SOURCE = R / 'build/cod4-old-world-20261023/run-06-fixed/saves/legacy-copy'
ORIGINAL = R / 'run/saves/New World'
CANDIDATE = R / 'build/cod4-combined-private-20261102/candidate01/dynasty-1.4.0.jar'
CONTRACT = R / 'docs/cod4/audit-20261022/legacy-migration-acceptance/coordinator-typed-root-clone-contract02-20261101.json'
FIELDS = R / 'build/cod4-legacy-fix-20261101/field-matrix05/audited-fields.snbt'
REOBF = DOC / 'reobf-20261102T130148-997818Z.json'
LINKAGE = DOC / 'linkage-20261102T130219-030052Z.json'
QUIET_RECEIPT = R / 'docs/cod4/audit-20261022/ecology-native-acceptance/preparation-20261028/verification.json'
PAIR_PATH = R / 'tools/cod4/sweep-native-acceptance/launch_pair.py'
PAIR_SHA = '800c27cd8005faed73fb790bc49b7165f90f7906e66c309421c2e926c14ba64e'
SHARED_SHA = '0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'
UUID = '380df991-f603-344c-a090-369bad2a924a'
REVIEWER_THREAD = '01a12516-2eaf-73e2-b615-20f8b422158c'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pair_tools():
    payload = PAIR_PATH.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == PAIR_SHA, 'Unreviewed metadata/platform helper'
    spec = importlib.util.spec_from_file_location('_legacy_reviewed_platform', PAIR_PATH)
    module = importlib.util.module_from_spec(spec)
    exec(payload, module.__dict__)
    return module


def read(p):
    return json.loads(Path(p).read_text(), object_pairs_hook=pair.unique_object)


def write(p, data):
    with Path(p).open('x') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


pair = pair_tools()


def artifacts():
    reobf, linkage, quiet = read(REOBF), read(LINKAGE), read(QUIET_RECEIPT)
    assert reobf['status'] == 'PASS' and linkage['status'] == 'PASS_STATIC_QA_MEMBER_RESOLUTION'
    assert linkage['reobf_receipt_sha256'] == sha(REOBF)
    qa = R / reobf['output']
    quiet_jar = R / quiet['jar']
    assert sha(qa) == reobf['output_sha256'] == linkage['qa_sha256']
    assert sha(CANDIDATE) == linkage['candidate_sha256'] == 'e5a78244082214ab5fd76eb35bbb42151e3ec7bd8bc13afee3bc58ea4fe3a669'
    assert sha(quiet_jar) == quiet['jar_sha256'] == 'c942abde6d61c8654e53fa3aad3bf1425a37755281836d8e0d4af43899ea6711'
    for name, expected in reobf['sources'].items():
        assert sha(R / name) == expected, name
    for name, expected in quiet['source_sha256'].items():
        assert sha(R / name) == expected, name
    pair.packaged(qa, reobf['entries'])
    return [CANDIDATE, qa, quiet_jar]


def command():
    original = pair.installed_command(HOST, OUT)
    argv = [x for x in original['argv'] if not x.startswith('-Decology.')]
    properties = {'dynasty.legacyqa.enabled': 'true', 'dynasty.legacyqa.worldRead': 'true',
                  'dynasty.legacyqa.root': str(BUILD), 'dynasty.legacyqa.instance': str(HOST),
                  'dynasty.legacyqa.output': str(OUT), 'dynasty.legacyqa.contract': str(BUILD / 'contract.json'),
                  'dynasty.legacyqa.fields': str(BUILD / 'fields.snbt'),
                  'ecology.nativeqa.enabled': 'false', 'ecology.nativegate.observe': 'false',
                  'ecology.bounded.observe': 'false'}
    argv[1:1] = ['-D' + k + '=' + v for k, v in properties.items()]
    for flag, value in {'--username': 'LegacyOwnerQA', '--uuid': UUID.replace('-', '')}.items():
        assert argv.count(flag) == 1
        argv[argv.index(flag) + 1] = value
    native_keys = ('java.library.path', 'jna.tmpdir', 'org.lwjgl.system.SharedLibraryExtractPath', 'io.netty.native.workdir')
    for key in native_keys:
        indices = [i for i, x in enumerate(argv) if x.startswith('-D' + key + '=')]
        assert len(indices) == 1
        argv[indices[0]] = '-D' + key + '=' + str(HOST / 'natives')
    assert argv[0] == str(pair.JAVA) and argv.count('cpw.mods.bootstraplauncher.BootstrapLauncher') == 1
    return argv, original['installed_version_sha256']


def prepare():
    assert not RUN.exists() and not RUN.is_symlink(), 'Never overwrite or duplicate a consumed attempt'
    pair.clean_environment()
    expected = read(R / 'docs/cod4/audit-20261022/old-world-acceptance/original-file-sha256.json')
    assert pair.manifest(SOURCE) == pair.manifest(ORIGINAL) == expected
    assert sha(R / 'modpack/mods/dynasty-1.4.0.jar') == SHARED_SHA
    jars = artifacts()
    source_folders = {name: pair.manifest(R / 'modpack' / name) for name in pair.FOLDERS}
    BUILD.mkdir(exist_ok=True)
    pair.canonical(BUILD)
    RUN.mkdir()
    HOST.mkdir()
    OUT.mkdir()
    for name, manifest in source_folders.items():
        if manifest is not None:
            subprocess.run(['/bin/cp', '-cR', str(R / 'modpack' / name), str(HOST / name)], check=True)
            assert pair.manifest(HOST / name) == manifest
    world = HOST / 'saves/legacy-copy'
    world.parent.mkdir()
    subprocess.run(['/bin/cp', '-cR', str(SOURCE), str(world)], check=True)
    assert pair.manifest(world) == pair.manifest(SOURCE) == pair.manifest(ORIGINAL) == expected
    for jar in jars:
        shutil.copyfile(jar, HOST / 'mods' / jar.name)
        assert sha(HOST / 'mods' / jar.name) == sha(jar)
    for source, target in [(CONTRACT, BUILD / 'contract.json'), (FIELDS, BUILD / 'fields.snbt')]:
        with target.open('xb') as f:
            f.write(source.read_bytes())
        assert sha(source) == sha(target)
    assert sha(BUILD / 'contract.json') == '8b75878379fa8740a274b8f63021834af6bbeb2ef25a004997c34ce84dc92a01'
    assert sha(BUILD / 'fields.snbt') == '269e730f3106206e6e827f4cf87ac04f889e0ee83d6a89c6dca9b4e524043c61'
    native = pair.PROFILE / 'natives-macos-arm64'
    native_manifest = pair.manifest(native)
    subprocess.run(['/bin/cp', '-cR', str(native), str(HOST / 'natives')], check=True)
    assert pair.manifest(HOST / 'natives') == pair.manifest(native) == native_manifest
    (HOST / 'options.txt').write_text('soundCategory_master:0.0\npauseOnLostFocus:false\nlang:zh_cn\nguiScale:3\nmaxFps:30\nrenderDistance:3\nsimulationDistance:5\ntutorialStep:none\nresourcePacks:["vanilla","mod_resources","file/dynasty-quest-guides-v3.zip"]\n')
    fml = HOST / 'config/fml.toml'
    text = fml.read_text() if fml.exists() else ''
    text = re.sub(r'(?m)^earlyWindowControl\s*=.*$', 'earlyWindowControl=false', text)
    if not re.search(r'(?m)^earlyWindowControl\s*=', text):
        text += '\nearlyWindowControl=false\n'
    fml.write_text(text)
    (HOST / 'config/dynamic_fps.json').write_text('{"enabled":false}\n')
    assert {name: pair.manifest(R / 'modpack' / name) for name in pair.FOLDERS} == source_folders
    argv, version = command()
    write(RUN / 'prepared.json', dict(status='PREPARED_ONLY_NO_RUNTIME_APPROVAL', source_folders=source_folders,
          original_world=expected, source_world=expected, private_files=pair.manifest(HOST), argv=argv,
          installed_version_sha256=version, artifact_files=pair.bind_files(jars),
          game_starts=0, checklist_deletions=0, source_world_mutations=0))
    print(json.dumps({'status': 'PREPARED_ONLY_NO_RUNTIME_APPROVAL', 'world_files': len(expected),
                      'private_files': len(pair.manifest(HOST)), 'mod_jars': len(list((HOST / 'mods').glob('*.jar'))), 'game_starts': 0}))


def snapshot():
    pair.clean_environment()
    pair.canonical(RUN)
    pair.canonical(OUT)
    assert not any(OUT.iterdir()) and not (RUN / 'execution-started.json').exists()
    prepared = read(RUN / 'prepared.json')
    assert prepared['status'] == 'PREPARED_ONLY_NO_RUNTIME_APPROVAL'
    assert pair.manifest(HOST) == prepared['private_files']
    assert pair.manifest(SOURCE) == prepared['source_world'] == pair.manifest(ORIGINAL) == prepared['original_world']
    assert {name: pair.manifest(R / 'modpack' / name) for name in pair.FOLDERS} == prepared['source_folders']
    assert sha(R / 'modpack/mods/dynasty-1.4.0.jar') == SHARED_SHA
    jars = artifacts()
    assert pair.bind_files(jars) == prepared['artifact_files']
    for jar in jars:
        assert sha(HOST / 'mods' / jar.name) == sha(jar)
    assert sha(CONTRACT) == sha(BUILD / 'contract.json') and sha(FIELDS) == sha(BUILD / 'fields.snbt')
    argv, version = command()
    assert argv == prepared['argv'] and version == prepared['installed_version_sha256']
    tools = [Path(__file__), PAIR_PATH, B / 'artifact_inputs.py', B / 'reobfuscate.py', B / 'check_linkage.py']
    tools += list((B / 'src').rglob('*.java')) + list((B / 'resources').rglob('*'))
    tools += [R / 'tools/cod4/ecology-native-acceptance' / name for name in pair.REVIEWED_METADATA_SHA]
    tools += [R / name for name in read(QUIET_RECEIPT)['source_sha256']]
    tools += [R / 'src/main/java/com/dynasty' / name for name in ['LegacyPlayerProgression.java', 'LegacyItemMappings.java', 'DynastyManual.java']]
    tools = [p for p in tools if p.is_file()]
    runtime_files = [pair.JAVA, pair.JHOME / 'release', pair.PROFILE / 'Dynasty.json', pair.PROFILE / 'Dynasty.jar']
    for flag in ['-cp', '-p']:
        assert argv.count(flag) == 1
        runtime_files += [Path(p) for p in argv[argv.index(flag) + 1].split(os.pathsep)]
    index = argv[argv.index('--assetIndex') + 1]
    assert re.fullmatch(r'[a-zA-Z0-9_-]+', index)
    runtime_files.append(pair.MC / 'assets/indexes' / (index + '.json'))
    trees = {str(p): pair.manifest(p) for p in [pair.JHOME / 'lib', pair.MC / 'libraries', HOST / 'natives']}
    assert all(trees.values())
    return dict(schema='legacy-one-owned-world-read-v1', private_root=str(RUN), private_files=prepared['private_files'],
                source_world=prepared['source_world'], original_world=prepared['original_world'],
                production_folders=prepared['source_folders'], argv=argv,
                tools=pair.bind_files(tools), inputs=pair.bind_files([RUN / 'prepared.json', REOBF, LINKAGE, QUIET_RECEIPT, CONTRACT, FIELDS, *jars]),
                runtime_files=pair.bind_files(runtime_files), runtime_trees=trees,
                java_environment={name: os.environ.get(name) for name in pair.ENV_FORBIDDEN},
                budgets={'startup': 240, 'runtime': 300, 'absolute': 600, 'normal_save': 60, 'term': 15},
                native_acceptance=False)


def check_review_contract(ready, report):
    assert ready['status'] == 'READY_FOR_ONE_BOUNDED_LEGACY_WORLD_READ' and ready['one_attempt_only'] is True
    assert report['status'] == 'INDEPENDENT_READY_FOR_ONE_BOUNDED_LEGACY_WORLD_READ'
    for document in [ready, report]:
        assert document['private_root'] == str(RUN) and document['one_attempt_only'] is True
        assert document['reviewer_thread'] == REVIEWER_THREAD
        assert re.fullmatch(r'[0-9a-f]{64}', document['snapshot_sha256'])
    assert report['snapshot_sha256'] == ready['snapshot_sha256']


def reviewed_documents():
    ready_path = pair.canonical(RUN / 'reviewed-world-read-ready02.json')
    ready_payload = ready_path.read_bytes()
    ready = json.loads(ready_payload, object_pairs_hook=pair.unique_object)
    relative = Path(ready['independent_review'])
    assert not relative.is_absolute() and '..' not in relative.parts
    report_path = pair.canonical(R / relative)
    assert report_path.is_relative_to(DOC) and report_path != ready_path
    report_payload = report_path.read_bytes()
    report_sha = hashlib.sha256(report_payload).hexdigest()
    assert report_sha == ready['independent_review_sha256']
    report = json.loads(report_payload, object_pairs_hook=pair.unique_object)
    check_review_contract(ready, report)
    return ready, report, hashlib.sha256(ready_payload).hexdigest(), report_sha


def process_blockers(payload):
    # macOS process argv can contain non-UTF8 filesystem bytes. Surrogate escape
    # preserves them losslessly while keeping every ASCII Java token observable.
    assert isinstance(payload, bytes)
    return pair.concurrent_java(os.fsdecode(payload))


def require_no_game():
    payload = subprocess.check_output(['/bin/ps', '-axo', 'pid=,comm=,args='])
    assert not process_blockers(payload), 'Existing game/QA/unknown Java present; no attachment or signals'


def execute():
    # No metadata imports/platform queries/marker consumption without current independent readiness.
    documents = reviewed_documents()
    ready = documents[0]
    observed = snapshot()
    assert ready['snapshot_sha256'] == pair.digest_json(observed)
    pair.require_awake()
    require_no_game()
    assert snapshot() == observed, 'Inputs changed after platform observation'
    assert reviewed_documents() == documents, 'Readiness or independent report changed during preflight'
    marker = {'ready_sha256': documents[2], 'independent_review_sha256': documents[3],
              'snapshot_sha256': pair.digest_json(observed), 'one_attempt_only': True}
    write(RUN / 'execution-started.json', marker)
    watchdog_path = R / 'tools/cod4/ecology-native-acceptance/watchdog.py'
    watchdog = pair.load_tool('_legacy_owned_watchdog', watchdog_path, pair.REVIEWED_METADATA_SHA['watchdog.py'])
    result = watchdog.run_owned(observed['argv'], instance=HOST, evidence=OUT, startup_seconds=240,
                                runtime_seconds=300, absolute_seconds=600, save_grace_seconds=60, term_grace_seconds=15)
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'plan', 'run'])
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare()
    elif args.mode == 'plan':
        observed = snapshot()
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')
        target = RUN / ('snapshot-not-ready-' + stamp + '.json')
        write(target, observed)
        print(json.dumps({'status': 'PLANNED_NOT_RUNTIME_READY', 'snapshot': str(target.relative_to(R)),
                          'snapshot_sha256': pair.digest_json(observed), 'game_starts': 0}))
    else:
        execute()
