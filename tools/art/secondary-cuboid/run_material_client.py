"""Run only our one isolated muted/hidden client; leave user processes untouched."""
import json
import argparse
import datetime
import os
import subprocess
import time
from pathlib import Path

root=Path(__file__).resolve().parents[3]
base=root/'build/maintenance/secondary-materials-v2'
c=json.loads((base/'launch.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--run',default=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
args=parser.parse_args()
assert args.run and all(x.isalnum() or x in '-_' for x in args.run)
assert Path(c['directory']).resolve()==(base/'client').resolve()
work=base/'client'/args.run;work.mkdir(parents=True,exist_ok=False)
agent=base/'quiet-window-agent.jar'
assert agent.exists(), 'Prepare QuietWindowAgent before any graphical launch'
(work/'options.txt').write_text('soundCategory_master:0.0\nrenderDistance:3\nsimulationDistance:3\nlang:zh_cn\n')
out=base/'results'/args.run;out.mkdir(parents=True,exist_ok=False)
assert not (out/'PASS.txt').exists() and not (out/'FAIL.txt').exists(), 'Keep previous run evidence'
with (out/'client.log').open('w') as log:
    child=subprocess.Popen([c['executable'],'-javaagent:'+str(agent.resolve()),*c['jvmArgs'],'-Ddynasty.secondaryMaterialQa.output='+str(out.resolve()),'-cp',c['classpath'],c['main'],*c['args']],cwd=work,env=dict(os.environ,**c['environment']),stdout=log,stderr=subprocess.STDOUT)
    try:
        deadline=time.monotonic()+360
        while child.poll() is None:
            if time.monotonic()>deadline: raise TimeoutError('Material QA timed out')
            time.sleep(1)
        if child.returncode or not (out/'PASS.txt').exists():raise RuntimeError('See '+str(out/'client.log'))
        print((out/'PASS.txt').read_text().splitlines()[-1])
    except BaseException as failure:
        if not (out/'FAIL.txt').exists():(out/'FAIL.txt').write_text(str(failure)+'\n')
        raise
    finally:
        if child.poll() is None:
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait()
