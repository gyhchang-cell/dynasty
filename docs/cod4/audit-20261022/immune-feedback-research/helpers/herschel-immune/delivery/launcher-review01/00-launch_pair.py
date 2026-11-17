"""Exact read-only plan/check and explicit once-only reviewed sweep host/peer launcher.

Default is check. No approval writer, preparation, world copying, compilation,
GUI control or launcher shell. Only run mode may enter the owned-pair watchdog.
"""
from pathlib import Path
import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = Path('/Users/a15356015027/Desktop/dynasty')
BASE = ROOT / 'build/cod4-sweep-native-20261029'
TOOLS = ROOT / 'tools/cod4/sweep-native-acceptance'
DOCS = ROOT / 'docs/cod4/audit-20261022/sweep-native-acceptance'
SOURCE = ROOT / 'build/cod4-mob-network-20261023/run-12/host/saves/mob-qa-1793198631800'
MC = Path('/Users/a15356015027/Public/.minecraft')
PROFILE = MC / 'versions/Dynasty'
JAVA = Path('/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home/bin/java')
JHOME = JAVA.parent.parent
FOLDERS = ('mods', 'config', 'defaultconfigs', 'resourcepacks')
ENV_FORBIDDEN = ('JAVA_TOOL_OPTIONS', '_JAVA_OPTIONS', 'JDK_JAVA_OPTIONS', 'CLASSPATH')
BUDGETS = dict(startup_seconds=240, absolute_seconds=900, save_seconds=60,
               term_seconds=15, poll_seconds=.25)
SHARED_SHA = '0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'
READY_STATUS = 'READY_FOR_ONE_BOUNDED_SWEEP_RUN'
SELF_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
LOADED_TOOL_SHA = {}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(path):
    path = Path(path)
    require(path.is_absolute() and path.resolve(strict=True) == path,
            'Noncanonical/symlink/missing path: ' + str(path))
    return path


def sha(path):
    path = canonical(path)
    require(path.is_file(), 'Regular file required: ' + str(path))
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    return json.loads(canonical(path).read_text(), object_pairs_hook=unique_object)


def digest_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def manifest(path):
    """Absent differs from empty; reject links, special files and linked ancestors."""
    path = Path(path)
    require(not path.is_symlink(), 'Symlink directory: ' + str(path))
    if not path.exists():
        canonical(path.parent)
        return None
    canonical(path)
    require(path.is_dir(), 'Directory required: ' + str(path))
    result = {}
    for current, dirs, files in os.walk(path, followlinks=False):
        for name in dirs + files:
            p = Path(current) / name
            kind = p.lstat().st_mode
            require(not stat.S_ISLNK(kind), 'Symlink input: ' + str(p))
            require(stat.S_ISDIR(kind) or stat.S_ISREG(kind), 'Special input: ' + str(p))
            if stat.S_ISREG(kind):
                result[p.relative_to(path).as_posix()] = sha(p)
    return dict(sorted(result.items()))


def root_for(run):
    require(re.fullmatch(r'sweep[0-9]{2,25}', run) is not None, 'Short sweepNN label required')
    canonical(ROOT)
    canonical(BASE)
    root = canonical(BASE / run)
    require(root.parent == BASE, 'Not a direct owned sweep root')
    return root


def clean_environment(environ=None):
    environ = os.environ if environ is None else environ
    require(not any(key in environ for key in ENV_FORBIDDEN),
            'Forbidden inherited Java environment (even empty): ' + ','.join(ENV_FORBIDDEN))


def identity(role):
    return str(uuid.UUID(bytes=hashlib.md5(('OfflinePlayer:Cod4Mob' + role.title()).encode()).digest(), version=3))


def properties(root, role):
    return {'dynasty.sweepqa.enabled': 'true', 'dynasty.sweepqa.instance': str(root / role),
            'dynasty.sweepqa.output': str(root / (role + '-evidence')),
            'dynasty.sweepdriver.enabled': 'true', 'dynasty.sweepdriver.role': role,
            'dynasty.sweepdriver.bridge': str(root / 'bridge'),
            'ecology.nativeqa.enabled': 'false', 'ecology.nativegate.observe': 'false',
            'ecology.bounded.observe': 'false'}


def check_argv(argv, root, role):
    require(isinstance(argv, list) and argv and all(isinstance(x, str) and x and '\0' not in x for x in argv), 'Invalid argv')
    require(argv[0] == str(JAVA), 'Unexpected JVM')
    require(argv.count('cpw.mods.bootstraplauncher.BootstrapLauncher') == 1, 'Exact native main required')
    main = argv.index('cpw.mods.bootstraplauncher.BootstrapLauncher')
    props = {}
    for arg in argv[1:]:
        require(not arg.startswith(('@', '-javaagent', '-agentlib', '-agentpath', '-Xbootclasspath', '-XX:Flags', '-XX:VMOptionsFile')), 'JVM injection: ' + arg)
        if arg.startswith('-D'):
            key, sep, value = arg[2:].partition('=')
            require(sep and key not in props and arg in argv[1:main], 'Duplicate/late/property override: ' + key)
            props[key] = value
    expected = properties(root, role)
    actual = {k: v for k, v in props.items() if k.startswith(('dynasty.', 'ecology.'))}
    require(actual == expected, 'Sweep/ecology property override or extra flag')
    safe_props = {'apple.awt.UIElement', 'fml.earlyWindowControl', 'java.library.path', 'jna.tmpdir',
                  'org.lwjgl.system.SharedLibraryExtractPath', 'io.netty.native.workdir',
                  'minecraft.launcher.brand', 'minecraft.launcher.version', 'java.net.preferIPv6Addresses',
                  'ignoreList', 'mergeModules', 'libraryDirectory'}
    require(set(props) == set(expected) | safe_props, 'Unknown/missing JVM property')
    require(props['apple.awt.UIElement'] == 'true' and props['fml.earlyWindowControl'] == 'false', 'Background bootstrap required')
    native = str(PROFILE / 'natives-macos-arm64')
    for key in ('java.library.path', 'jna.tmpdir', 'org.lwjgl.system.SharedLibraryExtractPath', 'io.netty.native.workdir'):
        require(props[key] == native, 'Native directory override')
    require(props['libraryDirectory'] == str(MC / 'libraries'), 'Library root override')
    # Reject JVM options not used by the fixed installed native launch recipe.
    paired = {'-cp', '-p', '--add-modules', '--add-opens', '--add-exports'}
    standalone = {'-Xmx4G', '-XX:ActiveProcessorCount=2', '-XstartOnFirstThread'}
    i = 1
    while i < main:
        arg = argv[i]
        if arg.startswith('-D') or arg in standalone:
            i += 1
        else:
            require(arg in paired and i + 1 < main, 'Unsupported JVM argument: ' + arg)
            if arg in ('-cp', '-p', '--add-modules'):
                require(argv[:main].count(arg) == 1, 'Repeated JVM path/module option')
            i += 2
    for flag, value in {'--username': 'Cod4Mob' + role.title(), '--uuid': identity(role).replace('-', ''),
                        '--gameDir': str(root / role), '--launchTarget': 'forgeclient',
                        '--assetsDir': str(MC / 'assets')}.items():
        require(argv.count(flag) == 1 and argv.index(flag) > main and argv[argv.index(flag) + 1] == value,
                'Native role/profile binding: ' + flag)
    require(len(argv[main + 1:]) % 2 == 0, 'Malformed game arguments')
    game_flags = argv[main + 1::2]
    require(all(x.startswith('--') for x in game_flags) and len(game_flags) == len(set(game_flags)), 'Duplicate game argument')
    return props


def load_tool(name, path):
    """Only fixed reviewed Python modules; no prep imports or execution."""
    canonical(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Execute the reviewed .py bytes, never a cached .pyc or a preloaded tool.
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    require(str(path) not in LOADED_TOOL_SHA or LOADED_TOOL_SHA[str(path)] == digest, 'Tool changed within process')
    exec(payload, module.__dict__)
    LOADED_TOOL_SHA[str(path)] = digest
    return module


def installed_command(instance, output):
    # Reuse just the installed-metadata constructor. Its ecology flags are removed
    # before any use. Imported helper modules have guarded CLIs, no child launch.
    ecology = ROOT / 'tools/cod4/ecology-native-acceptance'
    names = ('prepare_inputs', 'lint_mixin_boundary', 'watchdog')
    previous = {name: sys.modules.get(name) for name in names}
    try:
        for name in names:
            sys.modules[name] = load_tool('_sweep_input_' + name, ecology / (name + '.py'))
        tool = load_tool('_sweep_metadata_input', ecology / 'launch_once.py')
        require(tool.JAVA == JAVA and tool.PROFILE == PROFILE, 'Installed constructor paths changed')
        return tool.command(instance, output)
    finally:
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def regenerate(root, role):
    original = installed_command(root / role, root / (role + '-evidence'))
    argv = [x for x in original['argv'] if not x.startswith('-Decology.')]
    for flag, value in [('--username', 'Cod4Mob' + role.title()), ('--uuid', identity(role).replace('-', ''))]:
        require(argv.count(flag) == 1, 'Duplicate original profile flag')
        argv[argv.index(flag) + 1] = value
    argv = argv[:1] + ['-D' + k + '=' + v for k, v in properties(root, role).items()] + argv[1:]
    check_argv(argv, root, role)
    return argv, original['installed_version_sha256']


def bind_files(paths):
    return {str(p): sha(p) for p in sorted(set(paths))}


def packaged(path, entries):
    import zipfile
    with zipfile.ZipFile(canonical(path)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'Duplicate Jar entries')
        for entry, expected in entries.items():
            actual = hashlib.sha256(archive.read(entry)).hexdigest()
            require(actual == expected, 'Packaged class/resource changed: ' + entry)
        require(json.loads(archive.read('pack.mcmeta'))['pack']['pack_format'] == 15, 'Missing format15 metadata')


def snapshot(run):
    """Fresh full disk observations; no cached manifest or trusted self-described paths."""
    clean_environment()
    require(canonical(Path(__file__)) == TOOLS / 'launch_pair.py' and sha(Path(__file__)) == SELF_SHA, 'Executing launcher source changed or moved')
    root = root_for(run)
    prep_path = root / 'prepared-inputs.json'
    before = sha(prep_path)
    prep = read(prep_path)
    require(prep['run'] == run and prep['status'] == 'PREPARED_ONLY_NOT_REVIEWED_OR_RUNTIME_READY' and prep['game_started'] is False, 'Not pristine preparation')
    bridge = canonical(root / 'bridge')
    require({p.name for p in bridge.iterdir()} == {'plan.json'}, 'Used/stale bridge')
    for name in ['execution-started.json', 'pair-watchdog-start.json', 'pair-watchdog-result.json',
                 'host-watchdog.log', 'peer-watchdog.log']:
        require(not (root / name).exists() and not (root / name).is_symlink(), 'Consumed/used run: ' + name)
    plan_path = bridge / 'plan.json'
    plan = read(plan_path)
    expected_plan = dict(run=run, private_root=str(root), host_instance=str(root / 'host'), peer_instance=str(root / 'peer'),
                         host_output=str(root / 'host-evidence'), peer_output=str(root / 'peer-evidence'),
                         host_uuid=identity('host'), peer_uuid=identity('peer'), saved_world='sweep-world', bootstrap_existing_world=True,
                         qa_sha256=prep['artifact_sha256']['qa'], driver_sha256=prep['artifact_sha256']['driver'],
                         production_sha256=prep['artifact_sha256']['production'])
    require(plan == expected_plan, 'Plan differs from fixed role/root/provenance contract')
    require(read(root / 'sweep-driver-private.json') == {'run': run, 'plan_sha256': sha(plan_path)}, 'Plan/rootmarker mismatch')
    require(prep['source_own_world'] == str(SOURCE), 'Unexpected source checkpoint')
    source = manifest(SOURCE)
    require(source and source == prep['source_files_sha256'], 'Source checkpoint changed')
    production = {f: manifest(ROOT / 'modpack' / f) for f in FOLDERS}
    require(production == prep['production_source_folders_sha256'], 'Original production sources changed')
    require(sha(ROOT / 'modpack/mods/dynasty-1.4.0.jar') == SHARED_SHA, 'Shared baseline changed')
    world = root / 'host/saves/sweep-world'
    require(manifest(world) == source, 'Copied world changed/incomplete')
    require({p.name for p in canonical(root / 'host/saves').iterdir()} == {'sweep-world'}, 'Extra host saves')
    for role in ('host', 'peer'):
        require('playerdata/' + identity(role) + '.dat' in source, 'Checkpoint role UUID missing')
        instance = canonical(root / role)
        expected_leaves = {f for f in FOLDERS if production[f] is not None} | {'options.txt'}
        if role == 'host':
            expected_leaves.add('saves')
        require({p.name for p in instance.iterdir()} == expected_leaves, 'Unexpected instance entry')
        out = canonical(root / (role + '-evidence'))
        require(not any(out.iterdir()), 'Used/nonempty evidence output')
    receipts = {'production': (DOCS / 'current-bundle-private-integration.json', 'private_jar_sha256', BASE / 'current-bundle/dynasty-1.4.0.jar'),
                'qa': (DOCS / 'coordinator-reobf03.json', 'jar_sha256', BASE / 'helper-build03/libs/dynasty-sweep-native-acceptance-2.0.jar'),
                'quiet': (ROOT / 'docs/cod4/audit-20261022/ecology-native-acceptance/inputs-01/helper-integration-compile20.json', 'to_helper_sha256', ROOT / 'build/cod4-ecology-native-20261028/inputs-01/host/mods/dynasty-ecology-native-acceptance-1.4.0.jar'),
                'driver': (DOCS / 'driver/coordinator-reobf01.json', 'jar_sha256', BASE / 'driver-build01/libs/dynasty-sweep-stage-driver-1.0.jar')}
    expected_receipts = {str(p.relative_to(ROOT)): sha(p) for p, _, _ in receipts.values()}
    require(prep['source_receipts_sha256'] == expected_receipts, 'Artifact provenance receipt changed')
    artifact_files = []
    for key, (receipt, field, jar) in receipts.items():
        expected = read(receipt)[field]
        require(sha(jar) == prep['artifact_sha256'][key] == expected, 'Artifact source changed: ' + key)
        artifact_files += [jar, receipt]
        for role in ('host', 'peer'):
            private = root / role / 'mods' / jar.name
            require(sha(private) == expected, 'Copied artifact changed: ' + key)
    private_files = {}
    for role in ('host', 'peer'):
        files = {}
        for folder in FOLDERS:
            files.update({folder + '/' + k: v for k, v in (manifest(root / role / folder) or {}).items()})
        files['options.txt'] = sha(root / role / 'options.txt')
        require(files == prep['input_files_sha256'][role], 'Prepared private files changed: ' + role)
        private_files[role] = files
    prep_tools = [TOOLS / 'prepare_pair.py', ROOT / 'tools/cod4/ecology-native-acceptance/launch_once.py',
                  ROOT / 'tools/cod4/ecology-native-acceptance/prepare_inputs.py']
    require(prep['preparation_sources_sha256'] == {str(p.relative_to(ROOT)): sha(p) for p in prep_tools}, 'Preparation source changed')
    tools = prep_tools + list(TOOLS.glob('*.py')) + [TOOLS / 'driver/qa.init.gradle', TOOLS / 'qa.init.gradle']
    ecology = ROOT / 'tools/cod4/ecology-native-acceptance'
    tools += [ecology / p for p in ('watchdog.py', 'lint_mixin_boundary.py')]
    for parent in [TOOLS / 'src', TOOLS / 'resources', TOOLS / 'driver/src', TOOLS / 'driver/resources', ecology / 'src', ecology / 'resources']:
        tools += [parent / p for p in (manifest(parent) or {})]
    # Frozen Java/resources and actual SRG class inventory, separately from current text.
    srg = read(DOCS / 'driver/coordinator-reobf01.json')
    frozen = {}
    for relative, expected in srg['frozen_inputs'].items():
        original = TOOLS / 'driver' / relative
        staged = BASE / 'driver-frozen01' / relative
        require(sha(original) == sha(staged) == expected, 'Driver frozen source/resource mismatch')
        frozen[str(staged)] = expected
    packaged(receipts['driver'][2], srg['archive_entries_sha256'])
    qa_compile = read(DOCS / 'offline-compile02.json')
    qa_work = ROOT / qa_compile['work']
    for relative, expected in qa_compile['sources'].items():
        original = ROOT / relative
        staged = qa_work / 'frozen' / original.relative_to(TOOLS / 'src')
        require(sha(original) == sha(staged) == expected, 'QA frozen Java mismatch')
        frozen[str(staged)] = expected
    qa = read(DOCS / 'coordinator-reobf03.json')
    packaged(receipts['qa'][2], qa['classes_sha256'])
    artifact_files += [DOCS / 'offline-compile02.json']
    production_compile = ROOT / 'docs/cod4/audit-20261022/sweep-receipt-research/offline-compile-receipt.json'
    production_source = ROOT / 'src/main/java/com/dynasty/cod3/FangtianSweep.java'
    production_frozen = ROOT / 'tools/cod4/sweep-receipt-research/.work/receipt-fix/native-compile/frozen/com/dynasty/cod3/FangtianSweep.java'
    require(sha(production_source) == sha(production_frozen) == read(production_compile)['source_sha256'], 'Production frozen source mismatch')
    frozen[str(production_frozen)] = sha(production_frozen)
    tools.append(production_source)
    artifact_files.append(production_compile)
    quiet_verification = ROOT / 'docs/cod4/audit-20261022/ecology-native-acceptance/preparation-20261028/verification.json'
    verification = read(quiet_verification)
    require(verification['jar_sha256'] == prep['artifact_sha256']['quiet'], 'Quiet helper source receipt differs')
    for relative, expected in verification['source_sha256'].items():
        if relative.endswith('.java'):
            require(sha(ROOT / relative) == expected, 'Quiet helper source changed')
    artifact_files.append(quiet_verification)
    commands = {}
    for role in ('host', 'peer'):
        commands[role], version = regenerate(root, role)
        require(commands[role] == prep['argv'][role], 'Regenerated argv differs from prepared argv')
        require(version == prep['installed_metadata_sha256'][role] == sha(PROFILE / 'Dynasty.json'), 'Installed metadata changed')
    # Bind all classpath/module-path archives plus full libraryDirectory inventory,
    # Java runtime libraries/executable/release and the extracted native directory.
    runtime_files = [JAVA, JHOME / 'release', PROFILE / 'Dynasty.json', PROFILE / 'Dynasty.jar']
    for argv in commands.values():
        for flag in ('-cp', '-p'):
            require(argv.count(flag) == 1, 'Missing/duplicate launch path')
            for value in argv[argv.index(flag) + 1].split(os.pathsep):
                p = canonical(Path(value))
                require(p.is_file() and (p.is_relative_to(MC / 'libraries') or p == PROFILE / 'Dynasty.jar'), 'Unexpected library path')
                runtime_files.append(p)
    runtime_trees = {str(p): manifest(p) for p in [JHOME / 'lib', MC / 'libraries', PROFILE / 'natives-macos-arm64']}
    require(all(runtime_trees.values()), 'Missing runtime library/native tree')
    # Include assets index bytes (not rewritten by this tool); gameplay assets are
    # still the installed fullpack and never copied or rebuilt by the launcher.
    index = commands['host'][commands['host'].index('--assetIndex') + 1]
    require(re.fullmatch(r'[a-zA-Z0-9_-]+', index) is not None, 'Invalid assets index')
    runtime_files.append(MC / 'assets/indexes' / (index + '.json'))
    require(sha(prep_path) == before, 'Prepared receipt raced during validation')
    tool_bindings = bind_files(tools)
    require(all(tool_bindings.get(p) == h for p, h in LOADED_TOOL_SHA.items()), 'Loaded Python source differs from binding')
    return {'schema': 'sweep-launch-inputs-v1', 'run': run, 'root': str(root),
            'final_bindings_sha256': bind_files([prep_path, plan_path, root / 'sweep-driver-private.json'] + artifact_files),
            'tool_sources_sha256': tool_bindings, 'frozen_inputs_sha256': frozen,
            'source_world_path': str(SOURCE), 'source_world_sha256': source,
            'copied_world_path': str(world), 'copied_world_sha256': manifest(world),
            'production_source_folders_sha256': production, 'private_files_sha256': private_files,
            'runtime_files_sha256': bind_files(runtime_files), 'runtime_trees_sha256': runtime_trees,
            'argv': commands, 'budgets_seconds': BUDGETS,
            'gameplay_acceptance': False}


def reviewed(root, observed):
    path = canonical(root / 'reviewed-launch-ready.json')
    value = read(path)
    require(value.get('status') == READY_STATUS and value.get('run') == root.name and value.get('one_attempt_only') is True,
            'Independent one-run readiness required')
    require(value.get('snapshot_sha256') == digest_json(observed), 'Final readiness input SHA differs')
    require(isinstance(value.get('reviewer'), str) and value['reviewer'].strip(), 'Independent reviewer identity required')
    report = Path(value['review_report'])
    require(not report.is_absolute() and '..' not in report.parts, 'Relative review report required')
    report = canonical(ROOT / report)
    require(report.is_relative_to(DOCS) and report != path, 'Independent report must be in sweep evidence directory')
    require(sha(report) == value['review_report_sha256'], 'Independent review report changed')
    return sha(path)


def require_awake():
    # Read-only CoreGraphics status. No wake, unlock, screen/focus or display mutation.
    cg = ctypes.CDLL('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
    cg.CGMainDisplayID.restype = ctypes.c_uint32
    for name in ('CGDisplayIsActive', 'CGDisplayIsAsleep'):
        getattr(cg, name).argtypes = [ctypes.c_uint32]
        getattr(cg, name).restype = ctypes.c_uint32
    display = cg.CGMainDisplayID()
    require(display and cg.CGDisplayIsActive(display) and not cg.CGDisplayIsAsleep(display), 'Inactive/asleep display; no wake attempted')


def concurrent_java(process_text):
    blocked = []
    for line in process_text.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) < 3:
            continue
        _, comm, args = parts
        # comm may contain spaces; a /bin/java execution token also catches that.
        is_java = Path(comm).name in ('java', 'javaw') or re.search(r'(?:^|/)bin/java(?:\s|$)', comm + ' ' + args)
        if not is_java:
            continue
        gradle = any(x in args for x in ('org.gradle.launcher.daemon.bootstrap.GradleDaemon',
                                         'org.gradle.wrapper.GradleWrapperMain', 'org.gradle.launcher.GradleMain'))
        game = any(x.lower() in args.lower() for x in ('minecraft', 'bootstraplauncher', 'forgeclient', 'forgeserver',
                                                       'gametest', 'net.fabricmc', 'net.quiltmc', '-jar '))
        if not gradle or game:
            blocked.append(parts[0])
    return blocked


def require_no_game():
    text = subprocess.check_output(['/bin/ps', '-axo', 'pid=,comm=,args='], text=True, errors='strict')
    require(not concurrent_java(text), 'Existing game/QA/unknown Java present; never attach/stop user instances')


def execute(run):
    # Crucially reject missing approval before snapshot imports, display/process IO,
    # marker creation or any possible entry to the owned process controller.
    root = root_for(run)
    canonical(root / 'reviewed-launch-ready.json')
    observed = snapshot(run)
    ready_sha = reviewed(root, observed)
    require_awake()
    require_no_game()
    # Re-observe disk inputs after platform checks; no trust in a cached plan.
    again = snapshot(run)
    require(digest_json(again) == digest_json(observed), 'Inputs raced before run')
    require(reviewed(root, again) == ready_sha, 'Readiness raced before run')
    clean_environment()
    require_awake()
    require_no_game()
    watchdog_path = TOOLS / 'pair_watchdog.py'
    watchdog = load_tool('_sweep_owned_pair', watchdog_path)
    require(LOADED_TOOL_SHA[str(watchdog_path)] == again['tool_sources_sha256'][str(watchdog_path)], 'Loaded watchdog differs from final binding')
    with (root / 'execution-started.json').open('x') as stream:
        json.dump({'readiness_sha256': ready_sha, 'snapshot_sha256': digest_json(again),
                   'one_attempt_only': True, 'existing_pid_attached': False}, stream)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    # Two foreground Popen children are created exclusively inside this controller,
    # each with its own owned process group; no shell, detach, PID discovery or retry.
    return watchdog.run_owned_pair(again['argv'], root=root, **BUDGETS)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', help='Existing canonical prepared sweepNN root')
    parser.add_argument('--mode', choices=('plan', 'check', 'run'), default='check')
    args = parser.parse_args(argv)
    if args.mode == 'run':
        print(json.dumps(execute(args.run), indent=2))
        return 0
    observed = snapshot(args.run)
    root = root_for(args.run)
    ready = root / 'reviewed-launch-ready.json'
    approved = False
    if ready.exists() or ready.is_symlink():
        reviewed(root, observed)
        approved = True
    output = {'status': 'INPUTS_CHECKED_READY_BOUND' if approved else 'INPUTS_CHECKED_NO_READY_NOT_LAUNCHABLE',
              'run': args.run, 'snapshot_sha256': digest_json(observed),
              'independent_ready_present_and_matches': approved, 'game_started': False,
              'gameplay_acceptance': False}
    if args.mode == 'plan':
        output['snapshot'] = observed
    print(json.dumps(output, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError) as error:
        print('REFUSED: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
