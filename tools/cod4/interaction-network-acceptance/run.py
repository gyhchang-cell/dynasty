"""Wait for other COD4 GPU QA, then run our two isolated clients; kill only our process groups on failure."""
from pathlib import Path
import json,os,signal,subprocess,sys,time,hashlib
R=Path(__file__).resolve().parents[3]
run=sys.argv[1] if len(sys.argv)>1 else 'run-01'
suite=sys.argv[2] if len(sys.argv)>2 else 'interaction'
out=R/'docs/cod4/audit-20261022/interaction-network-acceptance'/run
lines=subprocess.check_output(['ps','-axo','pid,command'],text=True).splitlines()
busy=[line.split()[0] for line in lines if len(line.split())>1 and line.split()[1].endswith('/bin/java') and any(s in line for s in ['-Ddynasty.packqa.output=','-Ddynasty.armorqa.output='])]
if busy:raise SystemExit('QA deferred: another private client group is active; no new clients started: '+','.join(busy))
import ctypes
c=ctypes.CDLL('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics');c.CGMainDisplayID.restype=ctypes.c_uint32
d=c.CGMainDisplayID();assert d and c.CGDisplayIsActive(d) and not c.CGDisplayIsAsleep(d),'Do not wake the display for QA'
assert not out.exists(),'Never overwrite a previous run'
children=[]
try:
 for role in ['host','peer']:
  children.append(subprocess.Popen([sys.executable,str(R/'tools/cod4/interaction-network-acceptance/launch.py'),run,role,suite],cwd=R,start_new_session=True))
  if role=='host':
   start_deadline=time.monotonic()+150
   while not (out/'port.txt').exists():
    if children[0].poll() is not None:raise RuntimeError('Host startup failed; peer was not started')
    host_log=out/'host-client.log'
    if host_log.exists() and ('[Render thread/FATAL]' in host_log.read_text(errors='replace')):raise RuntimeError('Fatal host startup; peer was not started')
    if time.monotonic()>start_deadline:raise TimeoutError('Bounded host startup failed; peer was not started')
    time.sleep(2)
   print('Host opened private LAN; now start peer once',flush=True)
 deadline=time.monotonic()+1440;last=-1
 while time.monotonic()<deadline:
  failures=(list(out.glob('*FAIL*'))+list(out.glob('fatal.txt'))) if out.exists() else []
  if failures:raise RuntimeError('QA failed: '+str([(p.name,p.read_text()[:1000]) for p in failures]))
  stages=len(list(out.glob('case-result-*.json'))) if out.exists() else 0
  if stages!=last:print('Server stages completed/prepared:',stages,flush=True);last=stages
  if all(p.poll() is not None for p in children):break
  if out.exists() and any((out/(r+'-exit-code.txt')).exists() and (out/(r+'-exit-code.txt')).read_text().strip()!='0' for r in ['host','peer']):raise RuntimeError('A private client exited unsuccessfully; do not wait/restart blindly')
  time.sleep(3)
 else:raise TimeoutError('Two-client QA did not terminate within 24 minutes')
 if not all((out/(role+'-COMPLETE')).exists() or (out/(role+'-PASS')).exists() for role in ['host','peer']):raise RuntimeError('Missing both actual client completion markers')
 print('Both real clients completed; inspect individual case assertions; PASS='+str((out/'server-PASS').exists()),flush=True)
finally:
 # A recorded QA assertion already asks both clients to stop. Allow their native
 # private-world save to finish before falling back to our process-group timeout.
 if (out/'fatal.txt').exists():
  for p in children:
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:pass
 for p in children:
  if p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM)
 for p in children:
  try:p.wait(timeout=20)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL)
