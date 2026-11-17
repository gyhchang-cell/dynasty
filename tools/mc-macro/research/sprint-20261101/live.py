from pathlib import Path
import subprocess,os,json,time,sys
root=Path(__file__).resolve().parents[2];game=root/'.build/anchor-singleplayer';out=root/'research/sprint-20261101';pid=(game/'pid').read_text().strip();env={**os.environ,'MC_TEST_PID':pid}
assert '/.build/anchor-singleplayer/saves/mcPvPmax_Anchor_Test/' in subprocess.check_output(['lsof','-F','n','-p',pid],text=True)
def probe(*a):
 r=subprocess.run([str(game/'probe'),*a],env=env,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
def read():
 s=json.loads((game/'state.json').read_text())
 if not (s.get('active') and time.monotonic()-s.get('received',0)<.3):raise RuntimeError('Inactive/stale game')
 return s
def walk(label):
 p=subprocess.Popen([str(game/'probe'),'walk','1.2'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 samples=[]
 while p.poll() is None:
  try:s=read();samples.append({k:s.get(k) for k in ['received','tick','forward','sprinting','sprintKeyDown','toggleSprint','position','selected']})
  except RuntimeError:pass
  time.sleep(.03)
 stdout,stderr=p.communicate()
 if p.returncode:raise RuntimeError(stdout+stderr)
 (out/(label+'.json')).write_text(json.dumps(samples,indent=2))
 moving=[s for s in samples if s['forward']]
 assert len(moving)>5,'No useful movement samples'
 print(label,{'moving_samples':len(moving),'sprinting':sum(s['sprinting'] for s in moving),'key_down':sum(s['sprintKeyDown'] for s in moving),'toggle':moving[0]['toggleSprint'],'selected':moving[0]['selected']},flush=True)
 return moving
if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'hold'
 probe('resume')
 for cmd in ['/fill -8 64 -8 8 64 40 obsidian','/fill -8 65 -8 8 68 40 air','/gamemode survival','/tp @s 0.5 65 0.5 0 0','/effect give @s minecraft:saturation 1 10 true']:
  probe('command',cmd)
 probe('key','19');time.sleep(.5)
 s=read();assert s['toggleSprint']==(mode=='toggle'),s.get('toggleSprint')
 enabled=walk(mode+'-enabled');assert all(x['sprinting'] for x in enabled[3:]),'Enabled sprint gap'
 probe('control');time.sleep(.3)
 disabled=walk(mode+'-disabled');assert not any(x['sprinting'] for x in disabled[3:]),'Control did not disable'
 probe('control');time.sleep(.3)
 restored=walk(mode+'-restored');assert all(x['sprinting'] for x in restored[3:]),'Control did not restore'
 print(mode+' full Control test passed',flush=True)
