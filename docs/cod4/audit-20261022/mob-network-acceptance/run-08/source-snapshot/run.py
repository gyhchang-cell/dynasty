"""Private two-client LAN/TCP runner; only terminates its own process groups."""
from pathlib import Path
import subprocess,sys,time,os,signal,json,re,shutil,hashlib
R=Path(__file__).resolve().parents[3];run=sys.argv[1];out=R/'docs/cod4/audit-20261022/mob-network-acceptance'/run
assert re.fullmatch(r'run-\d+',run)
suite=sys.argv[2] if len(sys.argv)>2 else 'states'
out.mkdir(parents=True,exist_ok=True)
toolroot=R/'tools/cod4/mob-network-acceptance'
for name in ['src','resources']:shutil.copytree(toolroot/name,out/'source-snapshot'/name)
for name in ['launch.py','run.py','qa.init.gradle']:shutil.copy2(toolroot/name,out/'source-snapshot'/name)
(out/'source-hashes.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in toolroot.rglob('*') if p.is_file()},indent=2))
children=[]
try:
 for role in ['host','peer']:
  children.append(subprocess.Popen([sys.executable,str(R/'tools/cod4/mob-network-acceptance/launch.py'),run,role,suite],cwd=R,start_new_session=True))
 deadline=time.monotonic()+3600;last=None
 while time.monotonic()<deadline:
  failures=list(out.glob('*FAIL*')) if out.exists() else []
  if failures:raise RuntimeError([(p.name,p.read_text()[:1500]) for p in failures])
  results=sorted(out.glob('result-*.json'))
  if results and results[-1].name!=last:
   last=results[-1].name;v=json.loads(results[-1].read_text());print(len(results),v['name'],v['checks'],flush=True)
  if all(p.poll() is not None for p in children):break
  time.sleep(3)
 else:raise TimeoutError('3600s timeout')
 assert all((out/(r+'-COMPLETE')).exists() for r in ['host','peer'])
 print('Both real clients completed; inspect product assertions separately',flush=True)
finally:
 for p in children:
  if p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
 for p in children:
  try:p.wait(timeout=15)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL)
