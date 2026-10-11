#!/usr/bin/env python3
"""Run one exported, frozen Forge client; bound its lifetime and leave other JVMs alone."""
import argparse,json,os,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('launch',type=Path);p.add_argument('--timeout',type=int,default=360);a=p.parse_args()
c=json.loads(a.launch.read_text());out=next(Path(v.split('=',1)[1]) for v in c['jvmArgs'] if v.startswith('-Ddynasty.cod3RemainsQa.output='))
work=Path(c['directory']);work.mkdir(parents=True,exist_ok=True)
(work/'options.txt').write_text('soundCategory_master:0.0\nrenderDistance:6\nsimulationDistance:5\n')
out.mkdir(parents=True,exist_ok=True)
with (out/'client.log').open('w') as log:
 child=subprocess.Popen([c['executable'],*c['jvmArgs'],'-cp',c['classpath'],c['main'],*c['args']],cwd=work,env=dict(os.environ,**c['environment']),stdout=log,stderr=subprocess.STDOUT)
 try:
  deadline=time.monotonic()+a.timeout
  while child.poll() is None:
   if time.monotonic()>deadline:raise TimeoutError('Disposable remains client timed out')
   time.sleep(1)
  if child.returncode or not (out/'PASS.txt').exists():raise RuntimeError('Client failed; see '+str(out/'client.log'))
  print('PASS one integrated Forge client; '+str(out/'PASS.txt'))
 finally:
  if child.poll() is None:
   child.terminate()
   try:child.wait(timeout=10)
   except subprocess.TimeoutExpired:child.kill();child.wait()
