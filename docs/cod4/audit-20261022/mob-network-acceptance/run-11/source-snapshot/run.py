"""Private two-client LAN/TCP runner; only terminates its own process groups."""
from pathlib import Path
import subprocess,sys,time,os,signal,json,re,shutil,hashlib
R=Path(__file__).resolve().parents[3];run=sys.argv[1];out=R/'docs/cod4/audit-20261022/mob-network-acceptance'/run
assert re.fullmatch(r'run-\d+',run)
suite=sys.argv[2] if len(sys.argv)>2 else 'states'
assert not out.exists(),'Never overwrite existing evidence'
import ctypes
cg=ctypes.CDLL('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics');cg.CGMainDisplayID.restype=ctypes.c_uint32
d=cg.CGMainDisplayID();assert d and cg.CGDisplayIsActive(d) and not cg.CGDisplayIsAsleep(d),'Do not wake display for QA'
lines=subprocess.check_output(['ps','-axo','pid,command'],text=True).splitlines()
busy=[v.split()[0] for v in lines if len(v.split())>1 and v.split()[1].endswith('/bin/java') and any(s in v for s in ['-Ddynasty.packqa.output=','-Ddynasty.armorqa.output=','-Ddynasty.networkqa.output='])]
assert not busy,'Other private QA running: '+','.join(busy)
out.mkdir(parents=True)
toolroot=R/'tools/cod4/mob-network-acceptance'
for name in ['src','resources']:shutil.copytree(toolroot/name,out/'source-snapshot'/name)
for name in ['launch.py','run.py','qa.init.gradle','fullpack-audit.py']:shutil.copy2(toolroot/name,out/'source-snapshot'/name)
(out/'source-hashes.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in toolroot.rglob('*') if p.is_file() and '.work' not in p.parts and '__pycache__' not in p.parts},indent=2))
children=[]
try:
 for role in ['host','peer']:
  children.append(subprocess.Popen([sys.executable,str(R/'tools/cod4/mob-network-acceptance/launch.py'),run,role,suite],cwd=R,start_new_session=True))
  if role=='host':
   startup=time.monotonic()+240
   while not (out/'port.txt').exists():
    if children[0].poll() is not None:raise RuntimeError('Host exited; peer not launched')
    log=out/'host-client.log'
    if log.exists() and '[Render thread/FATAL]' in log.read_text(errors='replace'):raise RuntimeError('Host fatal startup; peer not launched')
    if time.monotonic()>startup:raise TimeoutError('Host startup exceeded240s; peer not launched')
    time.sleep(2)
   print('Private host LAN ready; launch peer once',flush=True)
 deadline=time.monotonic()+1440;last=None
 while time.monotonic()<deadline:
  failures=list(out.glob('*FAIL*')) if out.exists() else []
  if failures:raise RuntimeError([(p.name,p.read_text()[:1500]) for p in failures])
  results=sorted(out.glob('result-*.json'))
  if results and results[-1].name!=last:
   last=results[-1].name;v=json.loads(results[-1].read_text());print(len(results),v['name'],v['checks'],flush=True)
  if all(p.poll() is not None for p in children):break
  if any((out/(r+'-exit-code.txt')).exists() and (out/(r+'-exit-code.txt')).read_text().strip()!='0' for r in ['host','peer']):raise RuntimeError('Private client nonzero exit; no automatic restart')
  time.sleep(3)
 else:raise TimeoutError('24min bound exceeded')
 assert all((out/(r+'-COMPLETE')).exists() for r in ['host','peer'])
 print('Both real clients completed; inspect product assertions separately',flush=True)
finally:
 if list(out.glob('*FAIL*')):
  for p in children:
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:pass
 for p in children:
  if p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
 for p in children:
  try:p.wait(timeout=15)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL)
