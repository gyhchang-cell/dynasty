from pathlib import Path
import subprocess,os,time,json,sys
root=Path(__file__).resolve().parents[2];game=root/'.build/combat-lan';out=root/'research/combat-20261102';pid=(game/'client-a/pid').read_text().strip();helper=root/'.build/anchor-singleplayer/probe'
def fresh():
 for _ in range(50):
  try:s=json.loads((game/'state.json').read_text())
  except (OSError,ValueError):time.sleep(.05);continue
  if s.get('active') and not s.get('singleplayer') and time.monotonic()-s.get('received',0)<.25:return s
  time.sleep(.05)
 raise RuntimeError('No fresh local multiplayer gameplay state')
def run(label,action='left',*args):
 connections=subprocess.check_output(['lsof','-nP','-a','-p',pid,'-iTCP'],text=True);assert '127.0.0.1:25585' in connections
 b=fresh();assert b['selected']==0 and b.get('combat'), 'Sword not held'
 log=game/'app.log';offset=log.stat().st_size;samples=[]
 p=subprocess.Popen([str(helper),action,*args],env={**os.environ,'MC_TEST_PID':pid},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 while p.poll() is None:
  s=json.loads((game/'state.json').read_text());samples.append({k:v for k,v in s.items() if k not in ['cells','slots','keys','token']});time.sleep(.02)
 stdout,stderr=p.communicate();assert p.returncode==0,stdout+stderr
 a=fresh();text=log.read_bytes()[offset:].decode();(out/('duel-'+label+'.json')).write_text(json.dumps({'case':label,'before':b,'after':a,'samples':samples,'log':text,'input_trace':stdout},ensure_ascii=False,indent=2))
 print('\n'.join(l for l in text.splitlines() if 'SWORD' in l or 'SPRINT' in l));print('attacks',text.count('SWORD ATTACK'),'released',not a['leftDown'])
if __name__=='__main__':run(*sys.argv[1:])
