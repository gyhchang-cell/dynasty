from pathlib import Path
import subprocess,json,os,sys,time,shutil
root=Path(__file__).resolve().parents[2];out=root/'research/anchor-20261101/trials';out.mkdir(exist_ok=True)
game=root/'.build/anchor-singleplayer';pid=(game/'pid').read_text().strip();env={**os.environ,'MC_TEST_PID':pid}
opened=subprocess.check_output(['lsof','-F','n','-p',pid],text=True)
assert '/.build/anchor-singleplayer/saves/mcPvPmax_Anchor_Test/' in opened,'Dedicated test save required'
label=sys.argv[1];yaw=float(sys.argv[2]) if len(sys.argv)>2 else 0;hold=float(sys.argv[3]) if len(sys.argv)>3 else .06
probe=str(game/'probe')
def run(*a):
 r=subprocess.run([probe,*a],env=env,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
run('resume')
for cmd in ['/fill -7 64 -7 7 64 7 obsidian','/fill -7 65 -7 7 68 7 air',f'/tp @s 0.5 65 0.5 {yaw} 28.37']:
 run('command',cmd)
run('key','19')
def read_fresh():
 for _ in range(40):
  s=json.loads((game/'state.json').read_text())
  if s.get('active') and s.get('singleplayer') and 0<=time.monotonic()-s.get('received',0)<.25:return s
  time.sleep(.1)
 raise RuntimeError('No fresh active singleplayer state')
time.sleep(.3)
before=read_fresh()
assert abs((before['yaw']-yaw+180)%360-180)<.3 and abs(before['pitch']-28.37)<.3, 'Test setup angle not applied'
assert all(abs(a-b)<.05 for a,b in zip(before['position'],[.5,65,.5])) and before['selected']==1,'Test setup position/slot not applied'
log=game/'app.log';offset=log.stat().st_size
run(os.environ.get('MC_ANCHOR_TRIGGER','trigger'),str(hold))
after=read_fresh();lines=log.read_bytes()[offset:].decode('utf8')
record={'label':label,'yaw':yaw,'hold':hold,'before':before,'after':after,'log':lines}
(out/(label+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2))
shutil.copy2(game/'raw.png',out/(label+'.png'))
print(json.dumps({'label':label,'log':[x for x in lines.splitlines() if 'ANCHOR' in x],'health_before':before.get('health'),'health_after':after.get('health'),'selected':after.get('selected'),'angle':[after.get('yaw'),after.get('pitch')]},ensure_ascii=False),flush=True)
