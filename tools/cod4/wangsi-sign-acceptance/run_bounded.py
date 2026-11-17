"""Run only our isolated localhost headless fixture, with an external 240s budget."""
from pathlib import Path
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'tools/cod4/wangsi-sign-acceptance/.work'
phase = sys.argv[1]
assert phase in ('generate', 'reopen', 'natural_interactions')
OUT = ROOT / 'docs/cod4/audit-20261022' / ('interaction-natural-acceptance' if phase == 'natural_interactions' else 'wangsi-sign-native-acceptance')
OUT.mkdir(exist_ok=True)
assert not (OUT / f'{phase}.json').exists(), 'Never overwrite an earlier native receipt'
if phase == 'reopen':
    assert json.loads((OUT / 'generate.json').read_text())['status'] == 'PASS'
if phase != 'generate':
    assert (BASE / 'server/world/level.dat').is_file(), 'Existing private world required'
server = BASE / 'server'
server.mkdir(exist_ok=True)
if phase == 'generate':
    assert not (server / 'world').exists(), 'Generation requires a fresh private world'
    template = (ROOT / 'tools/cod4/ecology-acceptance/.work/cross-build/cross-dimension-run7/server.properties').read_text()
    template = template.replace('server-port=25589', 'server-port=25593')
    template = template.replace('white-list=false', 'white-list=true')
    (server / 'server.properties').write_text(template)
    (server / 'eula.txt').write_text('eula=true\n')
with socket.socket() as probe:
    probe.bind(('127.0.0.1', 25593))
env = os.environ.copy()
env['JAVA_HOME'] = '/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home'
env['GRADLE_USER_HOME'] = str(ROOT / 'tools/cod4/ecology-acceptance/.work/client-build/gradle-home')
args = ['./gradlew', '--offline', '--no-daemon', '--max-workers=1', '--project-cache-dir',
        str(BASE / 'project-cache'), '-I', 'tools/cod4/wangsi-sign-acceptance/qa.init.gradle',
        f'-PwangsiPhase={phase}', 'runServer']
start = time.monotonic()
timed_out = False
with (OUT / f'{phase}.log').open('x') as log:
    process = subprocess.Popen(args, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        code = process.wait(timeout=240)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGINT)
        try:
            code = process.wait(timeout=12)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            code = process.wait(timeout=5)
receipt = {'phase': phase, 'exit_code': code, 'external_timeout': timed_out,
           'elapsed_seconds': round(time.monotonic()-start, 2), 'budget_seconds': 240,
           'command': args, 'working_directory': str(server), 'headless_server_only': True,
           'game_clients_started': 0, 'user_original_world_touched': False,
           'native_result_exists': (OUT / f'{phase}.json').exists()}
if receipt['native_result_exists']:
    receipt['native_status'] = json.loads((OUT / f'{phase}.json').read_text()).get('status')
receipt['log_sha256'] = hashlib.sha256((OUT / f'{phase}.log').read_bytes()).hexdigest()
(OUT / f'{phase}-process.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
sys.exit(0 if code == 0 and not timed_out and receipt.get('native_status') == 'PASS' else 1)
