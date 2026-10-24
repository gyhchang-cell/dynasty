"""Wait for other COD4 GPU QA, then run our two isolated clients; kill only our process groups on failure."""
from pathlib import Path
import json,os,signal,subprocess,sys,time,hashlib
R=Path(__file__).resolve().parents[3]
run=sys.argv[1] if len(sys.argv)>1 else 'run-01'
suite=sys.argv[2] if len(sys.argv)>2 else 'armor'
out=R/'docs/cod4/audit-20261022/armor-network-acceptance'/run
while True:
 lines=subprocess.check_output(['ps','-axo','pid,command'],text=True).splitlines()
 busy=[line.split()[0] for line in lines if '/bin/java ' in line and any(s in line for s in ['-Ddynasty.packqa.output='])]
 if not busy:break
 print('Waiting for other COD4 QA clients:',','.join(busy),flush=True);time.sleep(20)
children=[]
try:
 for role in ['host','peer']:
  children.append(subprocess.Popen([sys.executable,str(R/'tools/cod4/armor-network-acceptance/launch.py'),run,role,suite],cwd=R,start_new_session=True))
 deadline=time.monotonic()+2400;last=-1
 while time.monotonic()<deadline:
  failures=list(out.glob('*FAIL*')) if out.exists() else []
  if failures:raise RuntimeError('QA failed: '+str([(p.name,p.read_text()[:1000]) for p in failures]))
  stages=len(list(out.glob('case-result-*.json'))) if out.exists() else 0
  if stages!=last:print('Server stages completed/prepared:',stages,flush=True);last=stages
  if all(p.poll() is not None for p in children):break
  time.sleep(3)
 else:raise TimeoutError('Two-client QA did not terminate within 40 minutes')
 if not all((out/(role+'-COMPLETE')).exists() or (out/(role+'-PASS')).exists() for role in ['host','peer']):raise RuntimeError('Missing both actual client completion markers')
 print('Both real clients completed; inspect individual case assertions; PASS='+str((out/'server-PASS').exists()),flush=True)
finally:
 for p in children:
  if p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM)
 for p in children:
  try:p.wait(timeout=20)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL)
