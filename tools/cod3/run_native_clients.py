"""Launch two frozen Forge clients on loopback; only uses disposable build/cod3-client worlds."""
import argparse,json,os,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('launch',type=Path);p.add_argument('run');a=p.parse_args()
if not a.run or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-' for c in a.run):p.error('Safe unique run id required')
repo=Path(__file__).resolve().parents[2];out=repo/'build/cod3-client'/a.run;out.mkdir(parents=True,exist_ok=False)
config=json.loads(a.launch.read_text());children=[];logs=[]
try:
 for role in ['host','peer']:
  work=out/role;work.mkdir();(work/'options.txt').write_text('soundCategory_master:0.0\n')
  jvm=[v for v in config['jvmArgs'] if not v.startswith('-Ddynasty.cod3ClientQa.')]
  jvm+=['-Ddynasty.cod3ClientQa.role='+role,'-Ddynasty.cod3ClientQa.output='+str(out/'results')]
  game=list(config['args']);game[game.index('--username')+1]='Cod3'+role.title()
  log=(out/(role+'.log')).open('w');logs.append(log)
  children.append(subprocess.Popen([config['executable'],*jvm,'-cp',config['classpath'],config['main'],*game],cwd=work,env=dict(os.environ,**config['environment']),stdout=log,stderr=subprocess.STDOUT))
 deadline=time.monotonic()+750
 while any(c.poll() is None for c in children):
  for role,c in zip(['host','peer'],children):
   fail=out/'results'/role/'FAIL.txt'
   if fail.exists():raise RuntimeError(fail.read_text())
   if c.poll() is not None and (c.returncode!=0 or not (out/'results'/role/'PASS.txt').exists()):raise RuntimeError(role+' exited without PASS; inspect '+str(out/(role+'.log')))
  if time.monotonic()>deadline:raise RuntimeError('Native client timeout')
  time.sleep(1)
 for role in ['host','peer']:print((out/'results'/role/'PASS.txt').read_text(),flush=True)
finally:
 for c in reversed(children):
  if c.poll() is None:
   c.terminate()
   try:c.wait(timeout=10)
   except subprocess.TimeoutExpired:c.kill();c.wait()
 for log in logs:log.close()
