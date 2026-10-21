#!/usr/bin/env python3
"""Bounded one-client verification; terminate only this test's child process."""
import json,os,subprocess,sys,time
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text())
out=next(Path(v.split('=',1)[1]) for v in c['jvmArgs'] if v.startswith('-Ddynasty.auroraQa.output='))
if (out/'PASS.txt').exists() or (out/'FAIL.txt').exists():
    raise SystemExit('Use a fresh -PskyRun output directory; never accept a previous run\'s PASS file.')
work=Path(c['directory']);work.mkdir(parents=True,exist_ok=True)
(work/'options.txt').write_text('soundCategory_master:0.0\nrenderDistance:4\nsimulationDistance:4\n')
out.mkdir(parents=True,exist_ok=True)
with (out/'client.log').open('w') as log:
    child=subprocess.Popen([c['executable'],*c['jvmArgs'],'-cp',c['classpath'],c['main'],*c['args']],cwd=work,env=dict(os.environ,**c['environment']),stdout=log,stderr=subprocess.STDOUT)
    (out/'owned-pid.txt').write_text(str(child.pid)+'\n')
    try:
        deadline=time.monotonic()+(600 if len(sys.argv)>2 and sys.argv[2]=="extended" else 420)
        while child.poll() is None:
            if time.monotonic()>deadline:raise TimeoutError('Disposable aurora client timed out')
            if "Can't find a primary monitor" in (out/'client.log').read_text(errors='replace'):
                raise RuntimeError('No primary monitor available; preserve the sleeping display and leave native verification pending')
            time.sleep(1)
        if child.returncode or not (out/'PASS.txt').exists() or (out/'FAIL.txt').exists():raise RuntimeError('Client failed; see '+str(out/'client.log'))
        print('PASS one silent integrated client: '+str(out/'PASS.txt'))
    finally:
        if child.poll() is None:
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait()
