"""No-game lifecycle checks using only fresh Python child processes."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from watchdog import run_owned

results=[]
with tempfile.TemporaryDirectory(prefix='dynasty-watchdog-smoke-') as tmp:
    root=Path(tmp)
    for name,program,forced in [
        ('normal','pass',False),
        ('blocked','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)',True),
        ('partial_readiness_then_cooperative_stop', '''import json,time
from pathlib import Path
e=Path('evidence')
p=e/'controller-start.json'
p.write_text('{')
time.sleep(.06)
p.write_text(json.dumps({'instance':str(Path.cwd())}))
while not (e/'stop-client.txt').exists():time.sleep(.01)
''',False)]:
        inst=root/name;inst.mkdir();ev=inst/'evidence';ev.mkdir()
        r=run_owned([sys.executable,'-c',program],instance=inst,evidence=ev,
            startup_seconds=.3,runtime_seconds=.2,absolute_seconds=.8,
            save_grace_seconds=.2,term_grace_seconds=.2,poll_seconds=.01)
        assert r['forced_signal_used']==forced and r['native_save_verified'] is False
        assert r['elapsed_seconds']<3
        if forced:assert r['exit_code']==-9
        else:assert r['exit_code']==0
        if name.startswith('partial_'):
            assert r['controller_ready_observed'] and r['stop_reason']=='runtime_deadline'
        results.append({'case':name,**r})
    ev=root/'invalid';ev.mkdir()
    try:run_owned([sys.executable,'-c','pass'],instance=root,evidence=ev,startup_seconds=float('nan'))
    except ValueError:results.append({'case':'invalid_budget','rejected_before_child_start':True})
    else:raise AssertionError('NaN accepted')
root=Path(__file__).resolve().parents[3]
receipt=root/'docs/cod4/audit-20261022/ecology-native-acceptance/preparation-20261028/watchdog-smoke.json'
receipt.write_text(json.dumps({'status':'PASS_PYTHON_CHILD_ONLY_NO_GAME',
    'watchdog_sha256':hashlib.sha256(Path(__file__).with_name('watchdog.py').read_bytes()).hexdigest(),
    'cases':results,'java_or_game_started':False,'worlds_accessed':False},indent=2)+'\n')
print('PASS: normal, blocked TERM/KILL, partial readiness/cooperative stop, invalid budget; no game')
