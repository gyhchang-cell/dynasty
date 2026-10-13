"""One quiet client with a fresh disposable world; never touches user saves."""
import json,os,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parents[3]
base=root/'build/maintenance/npc-trading-v1'
c=json.loads((base/'launch.json').read_text())
work=Path(c['directory']);work.mkdir(parents=True,exist_ok=True)
(work/'options.txt').write_text('soundCategory_master:0.0\nrenderDistance:3\nsimulationDistance:3\nlang:zh_cn\n')
out=base/'results';out.mkdir(parents=True,exist_ok=True)
with (out/'client.log').open('w') as log:
 child=subprocess.Popen([c['executable'],*c['jvmArgs'],'-cp',c['classpath'],c['main'],*c['args']],cwd=work,env=dict(os.environ,**c['environment']),stdout=log,stderr=subprocess.STDOUT)
 try:
  deadline=time.monotonic()+360
  while child.poll() is None:
   if time.monotonic()>deadline:raise TimeoutError('NPC QA timed out')
   time.sleep(1)
  if child.returncode or not (out/'PASS.txt').exists():raise RuntimeError('See '+str(out/'client.log'))
  print('PASS one muted Forge client, actual menus/slots/network and 75 textured/silhouette views')
 finally:
  if child.poll() is None:
   child.terminate()
   try:child.wait(timeout=10)
   except subprocess.TimeoutExpired:child.kill();child.wait()
