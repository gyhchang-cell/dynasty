from pathlib import Path
import subprocess,os,time,json,sys
root=Path(__file__).resolve().parents[2];game=root/'.build/anchor-singleplayer';out=root/'research/combat-20261102';pid=(game/'pid').read_text().strip()
def probe(*args):
 assert '/.build/anchor-singleplayer/saves/mcPvPmax_Anchor_Test/' in subprocess.check_output(['lsof','-F','n','-p',pid],text=True)
 r=subprocess.run([str(game/'probe'),*args],env={**os.environ,'MC_TEST_PID':pid},capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 return r.stdout
def fresh():
 for _ in range(50):
  s=json.loads((game/'state.json').read_text())
  if s.get('singleplayer') and s.get('active') and time.monotonic()-s.get('received',0)<.25:return s
  time.sleep(.05)
 raise RuntimeError('Inactive game, not a valid trial')
def command(c):probe('command',c)
def run(label,hold='3'):
 b=fresh();log=game/'app.log';offset=log.stat().st_size;samples=[]
 assert b['selected']==0 and b['combat']['delayTicks']>10
 p=subprocess.Popen([str(game/'probe'),'left',hold],env={**os.environ,'MC_TEST_PID':pid},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 while p.poll() is None:
  s=json.loads((game/'state.json').read_text());samples.append({k:v for k,v in s.items() if k not in ['cells','token','slots']});time.sleep(.025)
 stdout,stderr=p.communicate();assert p.returncode==0,stdout+stderr
 a=fresh();text=log.read_bytes()[offset:].decode();record={'case':label,'before':b,'after':a,'samples':samples,'log':text}
 (out/(label+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2));print(label,'\n'+'\n'.join(x for x in text.splitlines() if 'SWORD' in x))
if __name__=='__main__':
 if sys.argv[1]=='setup':
  for c in ['/gamemode survival','/difficulty normal','/fill -8 64 -8 8 64 40 obsidian','/fill -8 65 -8 8 69 40 air','/kill @e[tag=mcpvp_combat]','/time set midnight','/item replace entity @s hotbar.0 with minecraft:diamond_sword','/tp @s 0.5 65 0.5 0 0','/summon minecraft:zombie 0.5 65 3.0 {NoAI:1b,Silent:1b,PersistenceRequired:1b,Tags:["mcpvp_combat"],attributes:[{id:"minecraft:max_health",base:1000.0},{id:"minecraft:knockback_resistance",base:1.0}],Health:1000.0f}']:
   command(c)
  probe('key','18');print(json.dumps(fresh()['combat']))
 elif sys.argv[1]=='run':run(sys.argv[2],sys.argv[3] if len(sys.argv)>3 else '3')
