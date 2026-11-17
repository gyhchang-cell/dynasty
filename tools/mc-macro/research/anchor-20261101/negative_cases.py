from pathlib import Path
import subprocess,os,json,time
root=Path(__file__).resolve().parents[2];game=root/'.build/anchor-singleplayer';pid=(game/'pid').read_text().strip();env={**os.environ,'MC_TEST_PID':pid}
assert '/.build/anchor-singleplayer/saves/mcPvPmax_Anchor_Test/' in subprocess.check_output(['lsof','-F','n','-p',pid],text=True)
def probe(*a):
 r=subprocess.run([str(game/'probe'),*a],env=env,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
def trial(label,extra=None):
 r=subprocess.run(['python3',str(root/'research/anchor-20261101/trial.py'),label,'0'],env={**os.environ,**(extra or {})},capture_output=True,text=True)
 print(r.stdout,flush=True)
 if r.returncode:raise RuntimeError(r.stderr)
 return json.loads((root/'research/anchor-20261101/trials'/(label+'.json')).read_text())
probe('resume');probe('command','/gamemode creative')
r=trial('right-final-left-excluded',{'MC_ANCHOR_TRIGGER':'left'})
assert 'ANCHOR BEGIN' not in r['log'] and 'ANCHOR CLICK' not in r['log'],'left click must not trigger'
probe('command','/item replace entity @s hotbar.2 with minecraft:air')
r=trial('right-final-missing-glow')
assert 'ANCHOR REJECT' in r['log'] and 'ANCHOR CLICK' not in r['log'],'missing glowstone must not charge'
probe('command','/item replace entity @s hotbar.2 with minecraft:glowstone 64')
print('Live negative cases passed',flush=True)
